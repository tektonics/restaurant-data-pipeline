import psycopg2
import logging
from pathlib import Path
from datetime import datetime
from ..config.database_config import DATABASE, RESTAURANT_SCHEMA
from ..config.config import CSV_FIELDNAMES
import os

logging.basicConfig(
    filename=DATABASE['log_path'],
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def backup_database():
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = DATABASE['backup_path'] / f'restaurants_backup_{timestamp}.sql'
        
        # Using pg_dump for backup
        os.system(f"pg_dump -h {DATABASE['host']} -p {DATABASE['port']} "
                 f"-U {DATABASE['user']} {DATABASE['database']} > {backup_file}")
        
        logger.info(f"Database backed up to {backup_file}")
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        raise

def init_database():
    try:
        conn = psycopg2.connect(
            host=DATABASE['host'],
            port=DATABASE['port'],
            database=DATABASE['database'],
            user=DATABASE['user'],
            password=DATABASE['password']
        )
        cursor = conn.cursor()

        column_definitions = []
        for field in CSV_FIELDNAMES:
            field_name = field.lower().replace(' ', '_')
            column_definitions.append(f"{field_name} TEXT")

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS restaurants (
                id SERIAL PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                restaurant_name TEXT NOT NULL,
                cleaned_address TEXT NOT NULL,
                city TEXT,
                state TEXT,
                zip TEXT,
                UNIQUE(restaurant_name, cleaned_address)
            )
        ''')

        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_restaurant_name ON restaurants(restaurant_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_location ON restaurants(city, state, zip)')

        conn.commit()
        logger.info("Database initialized successfully")
        
    except psycopg2.Error as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    try:
        if DATABASE['path'].exists():
            backup_database()
        
        init_database()
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        raise
