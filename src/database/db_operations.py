import sqlite3
import pandas as pd
from pathlib import Path
import logging
from typing import List, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RestaurantDB:
    def __init__(self, db_path: str = "S:/restaurant_data_project/data/database/restaurants.db"):
        """Initialize database connection"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.cursor = None

    def connect(self):
        """Create a database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def create_tables(self):
        """Create tables if they don't exist"""
        try:
            # Main restaurants table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS restaurants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    restaurant_name TEXT NOT NULL,
                    restaurant_description TEXT,
                    cleaned_address TEXT,
                    city TEXT,
                    state TEXT,
                    zip TEXT,
                    phone TEXT,
                    website TEXT,
                    google_maps_link TEXT,
                    instagram_name TEXT,
                    instagram_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Restaurant details table (for flexible additional data)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS restaurant_details (
                    restaurant_id INTEGER,
                    detail_key TEXT,
                    detail_value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id),
                    PRIMARY KEY (restaurant_id, detail_key)
                )
            ''')

            self.conn.commit()
            logger.info("Tables created successfully")
        except sqlite3.Error as e:
            logger.error(f"Error creating tables: {e}")
            raise

    def insert_restaurant_data(self, df: pd.DataFrame):
        """Insert data from DataFrame into the database"""
        try:
            # Get the core columns that match the restaurants table
            core_columns = [
                'Restaurant Name', 'Restaurant Description', 'Cleaned Address',
                'City', 'State', 'Zip', 'Phone', 'Website', 'Google Maps Link',
                'Instagram Name', 'Instagram URL'
            ]

            # Insert core data
            for _, row in df.iterrows():
                self.cursor.execute('''
                    INSERT INTO restaurants (
                        restaurant_name, restaurant_description, cleaned_address,
                        city, state, zip, phone, website, google_maps_link,
                        instagram_name, instagram_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', [row.get(col, None) for col in core_columns])
                
                restaurant_id = self.cursor.lastrowid

                # Insert additional columns as key-value pairs
                for col in df.columns:
                    if col not in core_columns and pd.notna(row[col]):
                        self.cursor.execute('''
                            INSERT INTO restaurant_details (
                                restaurant_id, detail_key, detail_value
                            ) VALUES (?, ?, ?)
                        ''', (restaurant_id, col, str(row[col])))

            self.conn.commit()
            logger.info(f"Inserted {len(df)} restaurants into database")
        except sqlite3.Error as e:
            logger.error(f"Error inserting data: {e}")
            self.conn.rollback()
            raise

    def get_restaurant_by_name(self, name: str) -> Dict[str, Any]:
        """Retrieve restaurant data by name"""
        try:
            # Get core restaurant data
            self.cursor.execute('''
                SELECT * FROM restaurants WHERE restaurant_name = ?
            ''', (name,))
            restaurant = self.cursor.fetchone()
            
            if not restaurant:
                return None

            # Convert to dictionary
            columns = [desc[0] for desc in self.cursor.description]
            result = dict(zip(columns, restaurant))

            # Get additional details
            self.cursor.execute('''
                SELECT detail_key, detail_value 
                FROM restaurant_details 
                WHERE restaurant_id = ?
            ''', (result['id'],))
            
            details = self.cursor.fetchall()
            for key, value in details:
                result[key] = value

            return result
        except sqlite3.Error as e:
            logger.error(f"Error retrieving restaurant: {e}")
            raise

    def update_restaurant(self, restaurant_id: int, data: Dict[str, Any]):
        """Update restaurant data"""
        try:
            # Update core fields
            core_fields = {k: v for k, v in data.items() if k in [
                'restaurant_name', 'restaurant_description', 'cleaned_address',
                'city', 'state', 'zip', 'phone', 'website', 'google_maps_link',
                'instagram_name', 'instagram_url'
            ]}

            if core_fields:
                set_clause = ', '.join([f"{k} = ?" for k in core_fields.keys()])
                query = f"UPDATE restaurants SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
                self.cursor.execute(query, list(core_fields.values()) + [restaurant_id])

            # Update or insert additional details
            detail_fields = {k: v for k, v in data.items() if k not in core_fields}
            for key, value in detail_fields.items():
                self.cursor.execute('''
                    INSERT OR REPLACE INTO restaurant_details (restaurant_id, detail_key, detail_value)
                    VALUES (?, ?, ?)
                ''', (restaurant_id, key, str(value)))

            self.conn.commit()
            logger.info(f"Updated restaurant ID {restaurant_id}")
        except sqlite3.Error as e:
            logger.error(f"Error updating restaurant: {e}")
            self.conn.rollback()
            raise

if __name__ == "__main__":
    # Example usage
    db = RestaurantDB()
    try:
        db.connect()
        db.create_tables()
        
        # Load and insert data
        df = pd.read_csv("S:/restaurant_data_project/data/processed/cleaned_restaurants_enhanced.csv")
        db.insert_restaurant_data(df)
        
    finally:
        db.close()