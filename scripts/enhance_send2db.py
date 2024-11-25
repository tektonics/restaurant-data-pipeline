import logging
from pathlib import Path
import pandas as pd
import math
from src.utils.webdriver_manager import WebDriverManager
from concurrent.futures import ThreadPoolExecutor
from src.scrapers.FetchGoogleData import fetch_google_maps_data
from src.database.db_operations import RestaurantDB
from src.config.config import (
    CHROME_OPTIONS, CSV_FIELDNAMES, 
    PARALLEL_PROCESSING_CONFIG, CLEANED_RESTAURANTS_CSV, 
    MISSING_RESTAURANTS_CSV, ENHANCED_RESTAURANTS_CSV
)
from urllib.parse import quote
import csv
import os
import time
from scripts.send2db import load_csv_to_database
from src.utils.parallel_processor import process_with_parallel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_chunk(chunk_df, chunk_id, fieldnames):
    driver = None
    try:
        for attempt in range(3):
            try:
                driver = WebDriverManager.create_driver()
                if driver:
                    break
                time.sleep(2 ** attempt)
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed to create driver: {e}")
                if attempt == 2:
                    raise
        
        total_in_chunk = len(chunk_df)
        
        for idx, row in chunk_df.iterrows():
            try:
                logger.info(f"Chunk {chunk_id}: Processing {idx - chunk_df.index[0] + 1}/{total_in_chunk}")
                
                google_maps_url = row.get('Google Maps Link')
                if not google_maps_url or google_maps_url == 'Google Maps Link Not Found':
                    search_query = f"{row['Restaurant Name']} {row['Address']} {row['City']} {row['State']}"
                    google_maps_url = f"https://www.google.com/maps/search/{quote(search_query)}"
                
                google_data = fetch_google_maps_data(google_maps_url, driver)
                processed_row = {**row.to_dict(), **google_data}
                
                with open(ENHANCED_RESTAURANTS_CSV, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    if f.tell() == 0:
                        writer.writeheader()
                    writer.writerow(processed_row)
                    
                logger.info(f"Successfully processed and saved: {row['Restaurant Name']}")
                
            except Exception as e:
                logger.error(f"Error processing row {idx} in chunk {chunk_id}: {str(e)}")
                continue
                
    finally:
        if driver:
            driver.quit()

def is_row_processed(output_file, restaurant_name, address):
    if not Path(output_file).exists():
        return False
    
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if (row['Restaurant Name'] == restaurant_name and 
                    row['Address'] == address):
                    return True
    except Exception:
        return False
    return False

def write_row_to_csv(row_data, output_file, fieldnames):
    with open(output_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(row_data)

def verify_chromedriver(path):
    if not os.path.isfile(path):
        return False
    if not os.access(path, os.X_OK):
        try:
            os.chmod(path, 0o755)
            return True
        except Exception:
            return False
    return True

def main():
    try:
        if not Path(CLEANED_RESTAURANTS_CSV).exists():
            logger.warning(f"Cleaned restaurants CSV file not found at: {CLEANED_RESTAURANTS_CSV}")
            return
        
        if not Path(ENHANCED_RESTAURANTS_CSV).exists():
            with open(ENHANCED_RESTAURANTS_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
                writer.writeheader()
        
        df = pd.read_csv(CLEANED_RESTAURANTS_CSV)
        process_with_parallel(df, ENHANCED_RESTAURANTS_CSV, CSV_FIELDNAMES)
        
        logger.info("Enhancement process completed")
        
        if load_csv_to_database():
            logger.info("Database loading completed successfully")
        else:
            logger.error("Database loading failed")
            
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        raise
    finally:
        WebDriverManager.cleanup()

if __name__ == "__main__":
    main()
