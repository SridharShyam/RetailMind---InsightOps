import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_retail_data(filepath='c:/Users/shyam/OneDrive/MyPersonalDocs/RetailMind/RM/data/synthetic_retail_inventory_with_products_10k.csv'):
    """
    Load and prepare retail data with mock data generation if file doesn't exist.
    Prices are in Rupees.
    """
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        # Generate demo data if CSV doesn't exist
        print("No CSV found, generating demo data...")
        df = generate_demo_data()
    
    # Standardize column names to lowercase immediately to avoid duplicates later
    df.columns = [c.lower() for c in df.columns]
    
    # Remove duplicate columns if any exist
    df = df.loc[:, ~df.columns.duplicated()]

    # Reset index to ensure clean alignment
    df = df.reset_index(drop=True)
    
    # Rename commonly used columns to standard internal names
    rename_map = {
        'product_name': 'product',
        'product name': 'product',
        'inventory_level': 'inventory',
        'units_sold': 'sales',
        'date': 'date' # Just to be sure
    }
    # Only rename if target doesn't exist or we want to normalize
    df = df.rename(columns=rename_map)

    # Ensure date is datetime
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    else:
        # Fallback if no date column, create one
        df['date'] = datetime.now()
        
    # Calculate daily metrics
    if 'sales' in df.columns and 'inventory' in df.columns:
        # Safely calculate velocity (handle division by zero)
        df['sales_velocity'] = df['sales'] / df['inventory'].replace(0, 1)
        # Rolling average for sales
        df['days_of_stock'] = df['inventory'] / (df['sales'].rolling(window=7, min_periods=1).mean().replace(0, 1))
    else:
         # Should not happen with valid data, but fill to avoid errors
         df['sales'] = df.get('sales', 0)
         df['inventory'] = df.get('inventory', 0)
         df['sales_velocity'] = 0
         df['days_of_stock'] = 0
         
    # --- ADDED: Expiry Date Simulation ---
    # Assign shelf life based on Category if available, otherwise default
    if 'category' in df.columns:
        def get_shelf_life(category):
            cat = str(category).upper()
            if 'FOOD' in cat or 'GROCERIES' in cat or 'BAKERY' in cat:
                return np.random.randint(1, 14) # 1-14 days
            elif 'DAIRY' in cat:
                return np.random.randint(3, 21)
            else:
                return np.random.randint(60, 365) # Non-perishables long shelf life
        
        # We apply this to generate an expiry date RELATIVE TO THE RECORD DATE
        df['shelf_life_days'] = df['category'].apply(get_shelf_life)
        
        # We'll make some products VERY close to expiry to test the alerts (e.g. 5% of food items)
        random_critical = np.random.random(len(df)) < 0.05
        
        # Add values directly to avoid any index alignment issues
        expiry_deltas = pd.to_timedelta(df['shelf_life_days'], unit='D')
        df['expiry_date'] = df['date'] + expiry_deltas
        
        # Force some to be expiring soon (tomorrow or 3 days)
        mask_critical = (df['category'].str.contains('FOOD|GROCERIES', case=False, na=False)) & (random_critical)
        
        # Safe assignment using loc
        if mask_critical.any():
            critical_offsets = pd.to_timedelta(np.random.randint(1, 4, size=mask_critical.sum()), unit='D')
            df.loc[mask_critical, 'expiry_date'] = df.loc[mask_critical, 'date'] + critical_offsets
        
    else:
        # Fallback if no category
        df['expiry_date'] = df['date'] + pd.to_timedelta(365, unit='D')

    return df

def generate_demo_data():
    """Generate realistic demo data for hackathon (INDIAN CONTEXT)"""
    products = [
        'Coffee Beans (1kg)', 'Tea Leaves (500g)', 'Organic Honey', 'Artisan Bread',
        'Fresh Milk (1L)', 'Eggs (Dozen)', 'Avocados', 'Bananas (Dozen)',
        'Olive Oil (1L)', 'Pasta', 'Tomato Sauce', 'Canned Tuna'
    ]
    
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    
    data = []
    for date in dates:
        for product in products:
            # Base values with some randomness
            base_sales = {
                'Coffee Beans (1kg)': 25, 'Tea Leaves (500g)': 15, 'Organic Honey': 8,
                'Artisan Bread': 40, 'Fresh Milk (1L)': 60, 'Eggs (Dozen)': 50,
                'Avocados': 15, 'Bananas (Dozen)': 40, 'Olive Oil (1L)': 10,
                'Pasta': 30, 'Tomato Sauce': 20, 'Canned Tuna': 15
            }
            
            sales_mult = base_sales.get(product, 20)
            
            # Add seasonality and trends
            sales = sales_mult * (0.8 + 0.4 * np.random.random())
            
            # Weekend effect
            if date.weekday() >= 5:  # Saturday/Sunday
                sales *= 1.4
            
            # Inventory with some variation
            inventory = sales * (7 + 3 * np.random.random())
            
            # Price with some logic (IN RUPEES)
            base_price = {
                'Coffee Beans (1kg)': 850.00, 
                'Tea Leaves (500g)': 450.00, 
                'Organic Honey': 350.00,
                'Artisan Bread': 60.00, 
                'Fresh Milk (1L)': 65.00, 
                'Eggs (Dozen)': 90.00,
                'Avocados': 120.00, # Per piece often high in India for imported
                'Bananas (Dozen)': 60.00, 
                'Olive Oil (1L)': 1200.00,
                'Pasta': 150.00, 
                'Tomato Sauce': 120.00, 
                'Canned Tuna': 250.00
            }
            
            price_val = base_price.get(product, 200) # Default fallback
            price = price_val * (0.95 + 0.1 * np.random.random())
            
            # Weather and event flags (simplified)
            weather_score = np.random.randint(3, 10)  # 3-10 scale
            
            # Category inference for demo data
            category = 'GROCERIES'
            
            data.append({
                'Date': date,
                'Product_Name': product,
                'Category': category,
                'Units_Sold': max(1, int(sales)),
                'Inventory_Level': max(int(sales), int(inventory)),
                'Price': round(price, 0), # No cents in Indian retail usually
                'Weather_Condition': 'Sunny' if weather_score > 5 else 'Rainy',
                'Seasonality': 'Spring'
            })
    
    df = pd.DataFrame(data)
    # The load_retail_data function handles casing and expiry
    return df