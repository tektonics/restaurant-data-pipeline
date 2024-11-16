from pathlib import Path
from ..config.database_config import DATABASE, RESTAURANT_SCHEMA
import sqlite3
import pandas as pd
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RestaurantDB:
    def __init__(self, db_path: str = None):
        """Initialize database connection"""
        self.db_path = Path(db_path) if db_path else DATABASE['path']
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

    def insert_restaurant_data(self, df: pd.DataFrame):
        """Insert data from DataFrame into database"""
        try:
            field_mapping = {
                'restaurant_name': 'Restaurant Name',
                'restaurant_description': 'Restaurant Description',
                'address': 'Address',
                'phone': 'Phone',
                'website': 'Website',
                'google_maps_link': 'Google Maps Link',
                'cleaned_address': 'Cleaned Address',
                'city': 'City',
                'state': 'State',
                'zip': 'Zip',
                'star_rating': 'Star Rating',
                'number_of_reviews': 'Number of Reviews',
                'restaurant_category': 'Restaurant Category',
                'price_range': 'Price Range',
                'latitude': 'Latitude',
                'longitude': 'Longitude',
                'accessibility': 'Accessibility',
                'service_options': 'Service options',
                'highlights': 'Highlights',
                'popular_for': 'Popular for',
                'offerings': 'Offerings',
                'dining_options': 'Dining options',
                'amenities': 'Amenities',
                'atmosphere': 'Atmosphere',
                'planning': 'Planning',
                'payments': 'Payments',
                'parking': 'Parking',
                'doesnt_offer': 'Doesnt Offer'
            }

            for _, row in df.iterrows():
                core_data = {}
                for db_field, csv_field in field_mapping.items():
                    if csv_field in row and pd.notna(row[csv_field]):
                        core_data[db_field] = row[csv_field]

                if core_data:
                    columns = ', '.join(core_data.keys())
                    placeholders = ', '.join(['?' for _ in core_data])
                    
                    query = f'''
                        INSERT INTO restaurants ({columns})
                        VALUES ({placeholders})
                    '''
                    
                    self.cursor.execute(query, list(core_data.values()))

                self.conn.commit()
            logger.info(f"Inserted {len(df)} restaurants into database")
        except sqlite3.Error as e:
            logger.error(f"Error inserting data: {e}")
            self.conn.rollback()
            raise

    def get_restaurant_by_name(self, name: str) -> Dict[str, Any]:
        """Retrieve restaurant data by name"""
        try:
            self.cursor.execute('''
                SELECT * FROM restaurants WHERE restaurant_name = ?
            ''', (name,))
            restaurant = self.cursor.fetchone()
            
            if not restaurant:
                return None

            columns = [desc[0] for desc in self.cursor.description]
            result = dict(zip(columns, restaurant))

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
            core_fields = {k: v for k, v in data.items() if k in RESTAURANT_SCHEMA['core_fields']}
            if core_fields:
                set_clause = ', '.join([f"{k} = ?" for k in core_fields.keys()])
                query = f"UPDATE restaurants SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
                self.cursor.execute(query, list(core_fields.values()) + [restaurant_id])

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
    db = RestaurantDB()
    try:
        db.connect()
        
        df = pd.read_csv(Path(__file__).parent.parent.parent / "data/processed/cleaned_restaurants_enhanced.csv")
        db.insert_restaurant_data(df)
        
    finally:
        db.close()
