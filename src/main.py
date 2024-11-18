import platform
from src.scrapers import scrape_eater_archives, process_csv
from src.data_processing import clean_and_split_address, remove_duplicates
from src.database import init_database, RestaurantDB
from src.config.config import RAW_RESTAURANTS_CSV, CLEANED_RESTAURANTS_CSV, ENHANCED_RESTAURANTS_CSV, CHROME_OPTIONS
import pandas as pd
import logging
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor
from itertools import islice
from src.scrapers.FetchGoogleData import fetch_google_maps_data
import os
from pathlib import Path
from urllib.parse import quote
import csv
import math
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TimeoutError(Exception):
    pass

def timeout_handler():
    raise TimeoutError("Process timed out")

def run_with_timeout(timeout_duration):
    timer = threading.Timer(timeout_duration, timeout_handler)
    timer.start()
    return timer

def process_batch(batch_df, chunk_id, output_file, fieldnames):
    """Process a batch of restaurants with its own WebDriver instance"""
    driver = None
    try:
        chrome_options = Options()
        for option in CHROME_OPTIONS:
            chrome_options.add_argument(option)
            
        try:
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            logger.warning(f"System ChromeDriver failed, trying alternative path: {e}")
            try:
                service = Service('/usr/bin/chromedriver')
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                logger.error(f"All ChromeDriver attempts failed: {e}")
                raise
        
        total_in_batch = len(batch_df)
        
        for i, (idx, row) in enumerate(batch_df.iterrows(), 1):
            try:
                logger.info(f"Batch {chunk_id}: Processing {i}/{total_in_batch}")
                
                google_maps_url = row.get('Google Maps Link')
                if not google_maps_url or google_maps_url == 'Google Maps Link Not Found':
                    search_query = f"{row['Restaurant Name']} {row['Address']} {row['City']} {row['State']}"
                    google_maps_url = f"https://www.google.com/maps/search/{quote(search_query)}"
                
                google_data = fetch_google_maps_data(google_maps_url, driver)
                processed_row = {**row.to_dict(), **google_data}
                
                with open(output_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writerow(processed_row)
                    
                logger.info(f"Successfully processed and saved: {row['Restaurant Name']}")
                
            except Exception as e:
                logger.error(f"Error processing row {i} in batch {chunk_id}: {str(e)}")
                with open(output_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writerow(row.to_dict())
                continue
                
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                logger.error(f"Error closing driver: {str(e)}")

def is_row_processed(output_file, restaurant_name, address):
    """Check if a row has already been processed"""
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

def process_with_parallel(df, output_file, fieldnames):
    """Enhanced parallel processing with better error handling and progress tracking"""
    total_rows = len(df)
    num_workers = 4
    chunk_size = math.ceil(total_rows / num_workers)
    chunks = [df[i:i + chunk_size] for i in range(0, total_rows, chunk_size)]
    
    logger.info(f"Processing {total_rows} restaurants with {num_workers} workers")
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [
            executor.submit(process_batch, chunk, i, output_file, fieldnames)
            for i, chunk in enumerate(chunks)
        ]
        
        for future in futures:
            future.result()

def main():
    try:
        # WebDriver setup check
        try:
            service = Service()
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            driver = webdriver.Chrome(service=service, options=options)
            driver.quit()
            logger.info("WebDriver setup successful")
        except Exception as e:
            logger.error(f"WebDriver setup failed: {e}")
            raise

        # Set up timeout
        if platform.system() != 'Windows':
            import signal
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(1800)
        else:
            timer = run_with_timeout(1800)
        
        # Define fieldnames for CSV
        fieldnames = [
            'Restaurant Name', 'Restaurant Description', 'Address', 'Phone', 'Website',
            'Google Maps Link', 'Cleaned Address', 'City', 'State', 'Zip', 
            'Star Rating', 'Number of Reviews', 'Restaurant Category', 'Price Range',
            'Latitude', 'Longitude', 'Accessibility', 'Service options', 'Highlights',
            'Popular for', 'Offerings', 'Dining options', 'Amenities', 'Atmosphere',
            'Planning', 'Payments', 'Parking', 'Doesnt Offer'
        ]

        # Create necessary directories and initialize files
        for filepath in [RAW_RESTAURANTS_CSV, CLEANED_RESTAURANTS_CSV, ENHANCED_RESTAURANTS_CSV]:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Initialize enhanced CSV if it doesn't exist
        if not os.path.exists(ENHANCED_RESTAURANTS_CSV):
            with open(ENHANCED_RESTAURANTS_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

        logger.info("Initializing Eater.com scraper...")
        scrape_eater_archives()

        logger.info("Cleaning restaurant data...")
        df = pd.read_csv(RAW_RESTAURANTS_CSV)
        df[["Cleaned Address", "City", "State", "Zip"]] = df['Address'].apply(
            lambda x: pd.Series(clean_and_split_address(x))
        )
        df = remove_duplicates(df)
        df.to_csv(CLEANED_RESTAURANTS_CSV, index=False)

        logger.info("Enhancing with Google Maps data...")
        process_with_parallel(df, ENHANCED_RESTAURANTS_CSV, fieldnames)

        logger.info("Initializing database...")
        init_database()
        
        db = RestaurantDB()
        db.connect()
        
        logger.info("Populating database...")
        if os.path.exists(ENHANCED_RESTAURANTS_CSV):
            enhanced_df = pd.read_csv(ENHANCED_RESTAURANTS_CSV)
            db.insert_restaurant_data(enhanced_df)
            logger.info("Process completed successfully!")
        else:
            logger.warning("Enhanced restaurants CSV not found. Database population skipped.")
        
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        raise
    finally:
        if platform.system() != 'Windows':
            signal.alarm(0)

if __name__ == "__main__":
    main()
