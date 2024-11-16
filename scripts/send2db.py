import pandas as pd
import logging
from pathlib import Path
from src.database import RestaurantDB, init_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_csv_to_database():
    try:
        csv_path = Path("data/processed/all_enhanced.csv")
        
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found at {csv_path}")

        init_database()
        
        logger.info("Reading CSV file...")
        df = pd.read_csv(csv_path)
        logger.info(f"Found {len(df)} records in CSV")

        db = RestaurantDB()
        try:
            db.connect()
            logger.info("Connected to database")
            
            # Insert data
            logger.info("Inserting data into database...")
            db.insert_restaurant_data(df)
            logger.info("Data insertion complete")
            
        finally:
            db.close()
            logger.info("Database connection closed")

    except Exception as e:
        logger.error(f"Error during data loading: {e}")
        raise

if __name__ == "__main__":
    load_csv_to_database()
