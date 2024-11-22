import logging
from pathlib import Path
import pandas as pd
import math
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor
from src.scrapers.FetchGoogleData import fetch_google_maps_data
from src.database.db_operations import RestaurantDB
from src.config.config import CHROME_OPTIONS, CSV_FIELDNAMES, PARALLEL_PROCESSING_CONFIG
from urllib.parse import quote
import csv
import os
import time
from scripts.send2db import load_csv_to_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_enhanced_csv():
    enhanced_csv = Path("data/processed/cleaned_restaurants_enhanced.csv")
    if enhanced_csv.exists():
        logger.info("Enhanced CSV already exists. Loading to database...")
    

def create_driver():
    options = Options()
    for option in CHROME_OPTIONS:
        options.add_argument(option)
    
    for attempt in range(3):
        try:
            driver = webdriver.Chrome(options=options)
            logger.info("ChromeDriver initialized successfully")
            return driver
        except Exception as e1:
            try:
                service = Service('/usr/bin/chromedriver')
                driver = webdriver.Chrome(service=service, options=options)
                logger.info("ChromeDriver initialized with explicit path")
                return driver
            except Exception as e2:
                try:
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=options)
                    logger.info("ChromeDriver initialized with ChromeDriverManager")
                    return driver
                except Exception as e3:
                    if attempt == 2:
                        raise Exception(f"Failed to initialize ChromeDriver: {e1}\n{e2}\n{e3}")
                    time.sleep(2 ** attempt)
                    continue
    return None

def process_chunk(chunk_df, chunk_id, output_file, fieldnames):
    driver = None
    try:
        for attempt in range(3):
            try:
                driver = create_driver()
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
                
                with open(output_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writerow(processed_row)
                    
                logger.info(f"Successfully processed and saved: {row['Restaurant Name']}")
                
            except Exception as e:
                logger.error(f"Error processing row {idx} in chunk {chunk_id}: {str(e)}")
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
        enhanced_csv = Path("data/processed/cleaned_restaurants_enhanced.csv")
        if enhanced_csv.exists():
            logger.info("Enhanced CSV already exists. Loading to database...")
            if load_csv_to_database():
                logger.info("Database loading completed successfully")
                return
            else:
                logger.error("Database loading failed")
                return
        logger.info("Enhanced CSV not found. Exiting without processing.")
        return            
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        raise

if __name__ == "__main__":
    main()
