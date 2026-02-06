
import sqlite3
import os
import pandas as pd
from datetime import datetime

DB_NAME = 'retailmind.db'
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', DB_NAME)

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Products Master Table
    c.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        category TEXT,
        price REAL,
        current_inventory INTEGER DEFAULT 0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Inventory Batches (For Expiry/FIFO) 
    # This tracks distinct batches of stock.
    c.execute('''
    CREATE TABLE IF NOT EXISTS inventory_batches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        quantity INTEGER,
        expiry_date DATE,
        entry_date DATE,
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')
    
    # Ledger / Transactions History
    c.execute('''
    CREATE TABLE IF NOT EXISTS inventory_ledger (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        transaction_type TEXT, -- SALE, RESTOCK, ADJUSTMENT, EXPIRED
        quantity INTEGER, -- Positive for add, Negative for remove
        transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    ''')

    # Historical Daily Stats (For Forecasting)
    # Stores the EOD snapshot for every day
    c.execute('''
    CREATE TABLE IF NOT EXISTS daily_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        date DATE,
        sales INTEGER DEFAULT 0,
        inventory_snapshot INTEGER,
        price_snapshot REAL,
        FOREIGN KEY (product_id) REFERENCES products (id),
        UNIQUE(product_id, date)
    )
    ''')
    
    conn.commit()
    conn.close()

def import_initial_data(df):
    """
    Import initial dataframe into SQLite. 
    Only runs if DB is empty to avoid overwriting persistent state.
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check if we have data
    c.execute('SELECT count(*) FROM products')
    if c.fetchone()[0] > 0:
        conn.close()
        # print("Database already initialized. Skipping import.")
        return

    print("Initializing Database from DataFrame...")
    
    # 1. Products (Unique list)
    products_df = df[['product', 'category']].drop_duplicates(subset=['product'])
    
    product_map = {} # name -> id
    
    for _, row in products_df.iterrows():
        # Get latest price/inventory for master table
        latest = df[df['product'] == row['product']].iloc[-1]
        
        c.execute('''
            INSERT INTO products (name, category, price, current_inventory)
            VALUES (?, ?, ?, ?)
        ''', (row['product'], row.get('category', 'General'), float(latest['price']), int(latest['inventory'])))
        
        p_id = c.lastrowid
        product_map[row['product']] = p_id
        
        # Initial Batch (Latest Inventory)
        expiry = latest.get('expiry_date')
        if pd.isna(expiry): expiry = None
        else: expiry = str(expiry).split(' ')[0] # Format YYYY-MM-DD
                
        c.execute('''
            INSERT INTO inventory_batches (product_id, quantity, expiry_date, entry_date)
            VALUES (?, ?, ?, ?)
        ''', (p_id, int(latest['inventory']), expiry, datetime.now().strftime('%Y-%m-%d')))

    # 2. Daily Stats (History)
    # Bulk insert is faster
    stats_data = []
    for _, row in df.iterrows():
        p_id = product_map.get(row['product'])
        if p_id:
            d_str = row['date']
            if isinstance(d_str, datetime) or isinstance(d_str, pd.Timestamp):
                d_str = d_str.strftime('%Y-%m-%d')
            
            stats_data.append((
                p_id, 
                d_str, 
                int(row.get('sales', 0)), 
                int(row.get('inventory', 0)), 
                float(row.get('price', 0))
            ))
            
    c.executemany('''
        INSERT OR IGNORE INTO daily_stats (product_id, date, sales, inventory_snapshot, price_snapshot)
        VALUES (?, ?, ?, ?, ?)
    ''', stats_data)
        
    conn.commit()
    conn.close()
    print("Database import complete.")

def get_all_data_as_df():
    """
    Load data from DB and reconstruct the DataFrame expected by Analyzer.
    """
    conn = get_db_connection()
    
    query = '''
    SELECT 
        p.name as product,
        p.category,
        s.sales,
        s.inventory_snapshot as inventory,
        s.price_snapshot as price,
        s.date,
        b.expiry_date -- Simply taking one batch expiry for now (Simplification)
    FROM daily_stats s
    JOIN products p ON s.product_id = p.id
    LEFT JOIN (
        -- Get the earliest expiry date for each product to be safe
        SELECT product_id, MIN(expiry_date) as expiry_date 
        FROM inventory_batches 
        GROUP BY product_id
    ) b ON p.id = b.product_id
    ORDER BY s.date ASC
    '''
    
    try:
        df = pd.read_sql_query(query, conn)
        df['date'] = pd.to_datetime(df['date'])
        
        # Recalculate derived metrics that load_data.py used to do
        if not df.empty:
             df['sales_velocity'] = df['sales'] / df['inventory'].replace(0, 1)
             # df['days_of_stock'] need rolling calc, better handled in Analyzer or here?
             # Let's let load_data or analyzer handle the rolling calcs on the DF.
        
        return df
    except Exception as e:
        print(f"Error loading from DB: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def log_transaction(product_name, quantity, t_type='SALE'):
    """
    Log a transaction and update inventory safely.
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        # Get Product ID
        c.execute('SELECT id, current_inventory FROM products WHERE name = ?', (product_name,))
        row = c.fetchone()
        if not row:
            return {'error': 'Product not found'}
            
        p_id, current_inv = row['id'], row['current_inventory']
        
        # Calculate new inventory
        change = -quantity if t_type == 'SALE' else quantity
        new_inv = max(0, current_inv + change)
        
        # Update Product Master
        c.execute('UPDATE products SET current_inventory = ? WHERE id = ?', (new_inv, p_id))
        
        # Log Transaction
        c.execute('''
            INSERT INTO inventory_ledger (product_id, transaction_type, quantity, notes)
            VALUES (?, ?, ?, ?)
        ''', (p_id, t_type, change, f"Manual {t_type}"))
        
        # Update Daily Stats for Today (Or Insert)
        today = datetime.now().strftime('%Y-%m-%d')
        c.execute('''
            INSERT INTO daily_stats (product_id, date, sales, inventory_snapshot, price_snapshot)
            VALUES (?, ?, ?, ?, (SELECT price FROM products WHERE id=?))
            ON CONFLICT(product_id, date) DO UPDATE SET
            sales = sales + ?,
            inventory_snapshot = ?
        ''', (p_id, today, quantity if t_type=='SALE' else 0, new_inv, p_id, quantity if t_type=='SALE' else 0, new_inv))
        
        # FIFO Batch Update (Crucial for Expiry)
        if t_type == 'SALE':
            remaining_to_deduct = quantity
            # Get batches ordered by expiry (First Expiring First Out)
            batches = c.execute('''
                SELECT id, quantity FROM inventory_batches 
                WHERE product_id = ? AND quantity > 0 
                ORDER BY expiry_date ASC
            ''', (p_id,)).fetchall()
            
            for b in batches:
                if remaining_to_deduct <= 0: break
                
                deduct = min(b['quantity'], remaining_to_deduct)
                c.execute('UPDATE inventory_batches SET quantity = quantity - ? WHERE id = ?', (deduct, b['id']))
                remaining_to_deduct -= deduct
                
        conn.commit()
        return {'status': 'success', 'new_inventory': new_inv}
        
    except Exception as e:
        conn.rollback()
        return {'error': str(e)}
    finally:
        conn.close()

def merge_csv_data(df):
    """
    Merge uploaded CSV data into persistent DB.
    Handles Products, Daily Stats, and creates new batches.
    """
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        # 0. Normalize Columns
        # Lowercase and strip whitespace
        df.columns = df.columns.str.lower().str.strip()
        
        # Column Aliases Mapping
        # Map user provided columns to our internal schema
        column_map = {
            'item': 'product',
            'name': 'product',
            'product name': 'product',
            'product_name': 'product',
            'qty': 'inventory',
            'stock': 'inventory',
            'current inventory': 'inventory',
            'inventory_level': 'inventory',
            'cost': 'price',
            'unit price': 'price',
            'selling price': 'price',
            'cat': 'category',
            'expiration': 'expiry_date',
            'expiry': 'expiry_date',
            'units_sold': 'sales',
            'sold': 'sales'
        }
        df = df.rename(columns=column_map)
        
        # 1. Validation
        required = ['product', 'price', 'inventory']
        missing = [col for col in required if col not in df.columns]
        if missing:
            return {'error': f"CSV is missing required columns: {', '.join(missing)}. Found: {list(df.columns)}"}
        
        # Fill optional columns if missing
        if 'category' not in df.columns:
            df['category'] = 'General'
        if 'expiry_date' not in df.columns:
            df['expiry_date'] = None
            
        # Clean data types
        df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0.0)
        df['inventory'] = pd.to_numeric(df['inventory'], errors='coerce').fillna(0).astype(int)
        
        # 2. Process Data
        # Drop duplicates keeping last
        processed_df = df[['product', 'category', 'price', 'inventory', 'expiry_date']].drop_duplicates(subset=['product'], keep='last')
        
        for _, row in processed_df.iterrows():
            # Check if exists
            c.execute('SELECT id, current_inventory FROM products WHERE name = ?', (row['product'],))
            existing = c.fetchone()
            
            p_id = None
            if existing:
                p_id = existing['id']
                # If inventory changed from DB state, log it as adjustment
                diff = int(row['inventory']) - existing['current_inventory']
                if diff != 0:
                     c.execute('''
                        INSERT INTO inventory_ledger (product_id, transaction_type, quantity, notes)
                        VALUES (?, 'CSV_ADJUSTMENT', ?, 'Bulk upload adjustment')
                     ''', (p_id, diff))
                
                c.execute('''
                    UPDATE products SET price=?, category=?, current_inventory=?
                    WHERE id=?
                ''', (row['price'], row.get('category', 'General'), int(row['inventory']), p_id))
            else:
                c.execute('''
                    INSERT INTO products (name, category, price, current_inventory)
                    VALUES (?, ?, ?, ?)
                ''', (row['product'], row.get('category', 'General'), row['price'], int(row['inventory'])))
                p_id = c.lastrowid
                
            # Update/Reset Batches
            expiry = row['expiry_date']
            if pd.isna(expiry) or str(expiry).strip() == '': 
                expiry = None
            else: 
                try:
                    expiry = str(expiry).split(' ')[0]
                except:
                    expiry = None
            
            c.execute('DELETE FROM inventory_batches WHERE product_id = ?', (p_id,))
            c.execute('''
                INSERT INTO inventory_batches (product_id, quantity, expiry_date, entry_date)
                VALUES (?, ?, ?, ?)
            ''', (p_id, int(row['inventory']), expiry, datetime.now().strftime('%Y-%m-%d')))

        # 2. Daily Stats (History) - Only if 'date' and 'sales' columns exist
        # If user uploads simple inventory file, we might not have history.
        
        if 'date' in df.columns and 'sales' in df.columns:
            c.execute('SELECT name, id FROM products')
            product_map = {r['name']: r['id'] for r in c.fetchall()}
            
            stats_data = []
            for _, row in df.iterrows():
                p_id = product_map.get(row['product'])
                if p_id:
                    d_str = row['date']
                    if isinstance(d_str, datetime) or isinstance(d_str, pd.Timestamp):
                        d_str = d_str.strftime('%Y-%m-%d')
                    
                    stats_data.append((
                        p_id, 
                        d_str, 
                        int(row.get('sales', 0)), 
                        int(row.get('inventory', 0)), 
                        float(row.get('price', 0))
                    ))
            
            c.executemany('''
                INSERT OR REPLACE INTO daily_stats (product_id, date, sales, inventory_snapshot, price_snapshot)
                VALUES (?, ?, ?, ?, ?)
            ''', stats_data)
        
        conn.commit()
        return {'status': 'success', 'products_updated': len(processed_df)}
        
    except Exception as e:
        conn.rollback()
        return {'error': str(e)}
    finally:
        conn.close()

def reset_db():
    """
    Clear all data from tables but keep schema.
    Used for resetting to clean demo state.
    """
    conn = get_db_connection()
    c = conn.cursor()
    try:
        # Delete content from all tables
        c.execute('DELETE FROM daily_stats')
        c.execute('DELETE FROM inventory_ledger')
        c.execute('DELETE FROM inventory_batches')
        c.execute('DELETE FROM products')
        # Reset sequences if desired (optional)
        c.execute("DELETE FROM sqlite_sequence WHERE name IN ('products', 'daily_stats', 'inventory_ledger', 'inventory_batches')")
        conn.commit()
        print("Database cleared.")
        return True
    except Exception as e:
        print(f"Error resetting DB: {e}")
        return False
    finally:
        conn.close()
