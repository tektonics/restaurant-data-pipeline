import psycopg2
import logging
import pandas as pd
from pathlib import Path
from psycopg2.extras import execute_values
from ..config.database_config import DATABASE
from ..config.config import EXPECTED_RESTAURANT_FIELDS, EXPECTED_GOOGLE_FIELDS

logger = logging.getLogger(__name__)

class RestaurantDB:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=DATABASE['host'],
                port=DATABASE['port'],
                database=DATABASE['database'],
                user=DATABASE['user'],
                password=DATABASE['password']
            )
            self.cursor = self.conn.cursor()
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise

    def create_tables(self):
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS restaurants (
                    id SERIAL PRIMARY KEY,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Core Fields
                    restaurant_name TEXT NOT NULL,
                    restaurant_description TEXT,
                    address TEXT,
                    cleaned_address TEXT NOT NULL,
                    city TEXT,
                    state TEXT,
                    zip TEXT,
                    phone TEXT,
                    website TEXT,
                    google_maps_link TEXT,
                    embedded_links TEXT,
                    venue_id TEXT,
                    
                    -- Google Fields
                    star_rating TEXT,
                    number_of_reviews TEXT,
                    restaurant_category TEXT,
                    price_range TEXT,
                    latitude TEXT,
                    longitude TEXT,
                    accessibility TEXT,
                    service_options TEXT,
                    highlights TEXT,
                    popular_for TEXT,
                    offerings TEXT,
                    dining_options TEXT,
                    amenities TEXT,
                    atmosphere TEXT,
                    crowd TEXT,
                    planning TEXT,
                    payments TEXT,
                    parking TEXT,
                    pets TEXT,
                    children TEXT,
                    from_the_business TEXT,
                    doesnt_offer TEXT,
                    
                    CONSTRAINT restaurants_unique_name_address UNIQUE(restaurant_name, cleaned_address)
                )
            ''')
            
            # Create indexes
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_restaurant_name ON restaurants(restaurant_name)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_location ON restaurants(city, state, zip)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_rating ON restaurants(star_rating)')
            
            self.conn.commit()
            logger.info("Tables and indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            self.conn.rollback()
            raise

    def insert_restaurant_data(self, df):
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]
        
        df = df.astype(object).where(pd.notnull(df), None)
        records = df.to_records(index=False)
        data = [tuple(None if isinstance(x, float) and pd.isna(x) else 
                      x.item() if hasattr(x, 'item') else x 
                      for x in record) 
                for record in records]

        update_cols = [col for col in df.columns if col != 'id']
        update_stmt = ", ".join([
            f"{col} = EXCLUDED.{col}" 
            for col in update_cols
        ])

        insert_query = f"""
            INSERT INTO restaurants ({', '.join(df.columns)})
            VALUES %s
            ON CONFLICT (restaurant_name, cleaned_address) DO UPDATE SET
            {update_stmt}
        """

        try:
            with self.conn.cursor() as cur:
                execute_values(cur, insert_query, data)
            self.conn.commit()
            print(f"Successfully upserted {len(data)} records")
        except Exception as e:
            self.conn.rollback()
            print(f"Error inserting data: {str(e)}")
            raise

    def close(self):
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
