import psycopg2
import logging
import pandas as pd
from pathlib import Path
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
                    
                    -- Restaurant Fields
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
        try:
            # Convert column names to lowercase and replace spaces with underscores
            df.columns = [col.lower().replace(' ', '_') for col in df.columns]
            
            # Define all columns for insertion
            columns = [
                # Restaurant Fields
                'restaurant_name', 'restaurant_description', 'address', 
                'phone', 'website', 'google_maps_link', 'embedded_links', 
                'venue_id',
                
                # Google Fields
                'star_rating', 'number_of_reviews', 'restaurant_category',
                'latitude', 'longitude', 'accessibility', 'service_options',
                'highlights', 'popular_for', 'offerings', 'dining_options',
                'amenities', 'atmosphere', 'crowd', 'planning', 'payments',
                'parking', 'pets', 'children', 'from_the_business',
                
                # Additional processed fields
                'cleaned_address', 'city', 'state', 'zip'
            ]
            
            # Ensure all columns exist in DataFrame, fill with None if missing
            for col in columns:
                if col not in df.columns:
                    df[col] = None
            
            # Convert DataFrame to list of tuples for insertion
            values = [tuple(x) for x in df[columns].values]
            
            # Use execute_values for better performance
            from psycopg2.extras import execute_values
            execute_values(
                self.cursor,
                f"""
                INSERT INTO restaurants (
                    {', '.join(columns)}
                )
                VALUES %s
                ON CONFLICT ON CONSTRAINT restaurants_unique_name_address DO NOTHING
                """,
                values
            )
            
            self.conn.commit()
            logger.info(f"Successfully inserted {len(df)} records")
        except Exception as e:
            logger.error(f"Error inserting data: {e}")
            self.conn.rollback()
            raise

    def close(self):
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
