import platform
from src.scrapers import scrape_eater_archives, process_csv
from src.data_processing import clean_and_split_address, remove_duplicates
from src.database import init_database, RestaurantDB
from src.config.config import RAW_RESTAURANTS_CSV, CLEANED_RESTAURANTS_CSV, ENHANCED_RESTAURANTS_CSV
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

def process_batch(batch_df):
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        for _, row in batch_df.iterrows():
            try:
                google_data = fetch_google_maps_data(row['Google Maps Link'], driver)
                for key, value in google_data.items():
                    row[key] = value
            except Exception as e:
                logger.error(f"Error processing row: {e}")
    finally:
        if driver:
            driver.quit()

def process_with_parallel(df):
    # Split dataframe into batches
    batch_size = 100
    num_workers = 3  # Adjust based on your CPU and memory
    
    batches = [df[i:i + batch_size] for i in range(0, len(df), batch_size)]
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        executor.map(process_batch, batches)

def main():
    try:
        # Add WebDriver check
        try:
            # Test WebDriver setup
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service)
            driver.quit()
            logger.info("WebDriver setup successful")
        except Exception as e:
            logger.error(f"WebDriver setup failed: {e}")
            raise

        # Add timeout for the entire process (30 minutes)
        if platform.system() != 'Windows':
            import signal
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(1800)
        else:
            timer = run_with_timeout(1800)
        
        # Step 1: Scrape data from Eater.com
        logger.info("Starting Eater.com scraping...")
        logger.info("Initializing Eater.com scraper...")

        scrape_eater_archives()

        # Step 2: Clean and process the data
        logger.info("Cleaning restaurant data...")
        df = pd.read_csv(RAW_RESTAURANTS_CSV)
        df[["Cleaned Address", "City", "State", "Zip"]] = df['Address'].apply(
            lambda x: pd.Series(clean_and_split_address(x))
        )
        df = remove_duplicates(df)
        df.to_csv(CLEANED_RESTAURANTS_CSV, index=False)

        # Step 3: Enhance with Google Maps data
        logger.info("Enhancing with Google Maps data...")
        df = pd.read_csv(CLEANED_RESTAURANTS_CSV)
        process_with_parallel(df)

        # Step 4: Initialize and populate database
        logger.info("Initializing database...")
        init_database()
        
        db = RestaurantDB()
        db.connect()
        
        logger.info("Populating database...")
        enhanced_df = pd.read_csv(ENHANCED_RESTAURANTS_CSV)
        db.insert_restaurant_data(enhanced_df)
        
        logger.info("Process completed successfully!")
        
    except TimeoutError:
        logger.error("Process timed out after 30 minutes")
        raise
    except Exception as e:
        logger.error(f"Error in main process: {e}")
        raise
    finally:
        # Clean up timeout handlers
        if platform.system() != 'Windows':
            import signal
            signal.alarm(0)
        elif timer:
            timer.cancel()

if __name__ == "__main__":
    main()
