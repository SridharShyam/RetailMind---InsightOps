"""
Data service for loading and caching retail data
"""
import pandas as pd
from typing import Optional
from functools import lru_cache
import sys
import os

# Add models directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.load_data import load_retail_data
from app.config import get_settings


class DataService:
    """Service for managing retail data"""
    
    def __init__(self):
        self._data: Optional[pd.DataFrame] = None
        self.settings = get_settings()
        self._initialize_db()
        
    def _initialize_db(self):
        """Initialize database with CSV data if needed"""
        try:
            from app.models import database
            
            # Initialize DB schema
            database.init_db()
            
            # Check if we need to load initial data
            conn = database.get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT count(*) FROM products')
            count = cursor.fetchone()[0]
            conn.close()
            
            if count == 0:
                print(f"📊 Initializing database from {self.settings.DATA_PATH}")
                try:
                    df = load_retail_data(self.settings.DATA_PATH)
                    database.import_initial_data(df)
                    print("✅ Database initialized successfully")
                except Exception as e:
                    print(f"⚠️  Could not load initial data: {e}")
                    # Try generating demo data if file load fails
                    df = load_retail_data()
                    database.import_initial_data(df)
                    print("✅ Database initialized with demo data")
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")

    def load_data(self) -> pd.DataFrame:
        """Load retail data (with caching)"""
        if self._data is None:
            try:
                from app.models import database
                # Load directly from DB
                self._data = database.get_all_data_as_df()
                
                if self._data.empty:
                    print("⚠️  DB return empty dataframe, falling back to CSV load")
                    self._data = load_retail_data(self.settings.DATA_PATH)
                
                print(f"✅ Loaded {len(self._data)} records from Database")
            except Exception as e:
                print(f"⚠️  Could not load data from DB: {e}, falling back onto CSV")
                self._data = load_retail_data(self.settings.DATA_PATH)
        
        return self._data
    
    def get_product_data(self, product_name: str) -> pd.DataFrame:
        """Get data for a specific product"""
        df = self.load_data()
        
        # Case-insensitive product name matching
        product_data = df[df['product'].str.lower() == product_name.lower()].copy()
        
        if product_data.empty:
            raise ValueError(f"Product '{product_name}' not found in data")
        
        return product_data.sort_values('date')
    
    def get_all_products(self) -> list:
        """Get list of all unique products"""
        df = self.load_data()
        return sorted(df['product'].unique().tolist())
    
    def get_products_by_risk(self, risk_level: str) -> list:
        """Get products filtered by risk level"""
        # This would need risk calculation - simplified version
        return self.get_all_products()[:5]  # Placeholder
    
    def reload_data(self):
        """Force reload data from source"""
        self._data = None
        return self.load_data()
        
    def process_transaction(self, product_name: str, quantity: int, transaction_type: str = 'SALE') -> dict:
        """Process a transaction (sale/restock) and update DB"""
        from app.models import database
        
        result = database.log_transaction(product_name, quantity, transaction_type)
        if 'error' not in result:
            # Invalidate cache to force reload on next read
            self._data = None
        return result


# Singleton instance
@lru_cache()
def get_data_service() -> DataService:
    """Get cached DataService instance"""
    return DataService()