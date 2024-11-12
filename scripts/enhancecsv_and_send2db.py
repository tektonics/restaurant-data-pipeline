import logging
from pathlib import Path
from src.scrapers.FetchGoogleData import process_google_data
from src.database.db_operations import RestaurantDB
import pandas as pd

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        # Define paths
        input_csv = Path("data/raw/cleaned_restaurants.csv")
        enhanced_csv = Path("data/processed/cleaned_restaurants_enhanced.csv")
        
        # Ensure output directory exists
        enhanced_csv.parent.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Fetch Google Data
        logger.info("Starting Google Maps data collection...")
        process_google_data(
            input_file=str(input_csv),
            output_file=str(enhanced_csv)
        )
        logger.info("Google Maps data collection complete")
        
        # Step 2: Load into database
        logger.info("Loading data into database...")
        db = RestaurantDB()
        try:
            db.connect()
            df = pd.read_csv(enhanced_csv)
            db.insert_restaurant_data(df)
            logger.info("Data successfully loaded into database")
        finally:
            db.close()
            
        logger.info("Process completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        raise

if __name__ == "__main__":
    main()
