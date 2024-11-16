"""Database setup and initialization"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from ..config.database_config import DATABASE, RESTAURANT_SCHEMA

logging.basicConfig(
    filename=DATABASE['log_path'],
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def backup_database():
    """Create a backup of the database"""
    if DATABASE['path'].exists():
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = DATABASE['backup_path'] / f'restaurants_backup_{timestamp}.db'
        
        try:
            with sqlite3.connect(DATABASE['path']) as source:
                backup = sqlite3.connect(backup_file)
                source.backup(backup)
                backup.close()
            logger.info(f"Database backed up to {backup_file}")
        except sqlite3.Error as e:
            logger.error(f"Backup failed: {e}")
            raise

def init_database():
    """Initialize the database with tables"""
    try:
        conn = sqlite3.connect(DATABASE['path'])
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS restaurants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                restaurant_name TEXT NOT NULL,
                restaurant_description TEXT,
                address TEXT,
                phone TEXT,
                website TEXT,
                google_maps_link TEXT,
                instagram_name TEXT,
                instagram_url TEXT,
                cleaned_address TEXT,
                city TEXT,
                state TEXT,
                zip TEXT,
                star_rating REAL,
                number_of_reviews INTEGER,
                restaurant_category TEXT,
                price_range TEXT,
                latitude REAL,
                longitude REAL,
                accessibility TEXT,
                service_options TEXT,
                highlights TEXT,
                popular_for TEXT,
                offerings TEXT,
                dining_options TEXT,
                amenities TEXT,
                atmosphere TEXT,
                planning TEXT,
                payments TEXT,
                parking TEXT,
                doesnt_offer TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_restaurant_name ON restaurants(restaurant_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_location ON restaurants(city, state, zip)')

        conn.commit()
        logger.info("Database initialized successfully")
        
    except sqlite3.Error as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    try:
        if DATABASE['path'].exists():
            backup_database()
        
        init_database()
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        raise
