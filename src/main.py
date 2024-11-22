import platform
from src.scrapers import scrape_eater_archives, process_csv
from src.data_processing import clean_and_split_address, remove_duplicates
from src.database import init_database, RestaurantDB
from src.config.config import (
    RAW_RESTAURANTS_CSV, 
    CLEANED_RESTAURANTS_CSV, 
    ENHANCED_RESTAURANTS_CSV, 
    CHROME_OPTIONS,
    CSV_FIELDNAMES,
    PARALLEL_PROCESSING_CONFIG,
    WEBDRIVER_CONFIG,
    TIMEOUT_CONFIG,
    MAX_RETRIES,
    RETRY_DELAY,
    RATE_LIMITS,
    DEFAULT_VALUES
)
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
from scripts.send2db import load_csv_to_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TimeoutError(Exception):
    pass

def timeout_handler():
    raise TimeoutError("Process timed out")

def run_with_timeout(timeout_duration=PARALLEL_PROCESSING_CONFIG['timeout_seconds']):
    timer = threading.Timer(timeout_duration, timeout_handler)
    timer.start()
    return timer

def process_batch(batch_df, chunk_id, output_file, fieldnames):
    driver = None
    try:
        chrome_options = Options()
        for option in WEBDRIVER_CONFIG['options']:
            chrome_options.add_argument(option)
            
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(WEBDRIVER_CONFIG['implicit_wait'])
            driver.set_page_load_timeout(WEBDRIVER_CONFIG['page_load_timeout'])
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
    total_rows = len(df)
    num_workers = PARALLEL_PROCESSING_CONFIG['num_workers']
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

        try:
            service = Service()
            options = webdriver.ChromeOptions()
            for option in WEBDRIVER_CONFIG['options']:
                options.add_argument(option)
            driver = webdriver.Chrome(service=service, options=options)
            driver.quit()
            logger.info("WebDriver setup successful")
        except Exception as e:
            logger.error(f"WebDriver setup failed: {e}")
            raise

        if platform.system() != 'Windows':
            import signal
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(PARALLEL_PROCESSING_CONFIG['timeout_seconds'])
        else:
            timer = run_with_timeout()
        
        if not os.path.exists(ENHANCED_RESTAURANTS_CSV):
            with open(ENHANCED_RESTAURANTS_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
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
        process_with_parallel(df, ENHANCED_RESTAURANTS_CSV, CSV_FIELDNAMES)

        logger.info("Initializing database...")
        init_database()
        
        logger.info("Loading data to database...")
        if os.path.exists(ENHANCED_RESTAURANTS_CSV):
            if load_csv_to_database():
                logger.info("Database loading completed successfully")
            else:
                logger.warning("Database loading failed")
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
