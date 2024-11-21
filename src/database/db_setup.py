"""Database setup and initialization"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from ..config.database_config import DATABASE, RESTAURANT_SCHEMA
from ..config.config import CSV_FIELDNAMES

logging.basicConfig(
    filename=DATABASE['log_path'],
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def backup_database():
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
    try:
        conn = sqlite3.connect(DATABASE['path'])
        cursor = conn.cursor()

        column_definitions = []
        for field in CSV_FIELDNAMES:
            field_name = field.lower().replace(' ', '_')
            column_definitions.append(f"{field_name} TEXT")

        base_columns = """
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        """
        
        all_columns = f"{base_columns}, {', '.join(column_definitions)}"

        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS restaurants (
                {all_columns}
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
