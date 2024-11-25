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
from src.utils.webdriver_manager import WebDriverManager
from scripts.enhance_send2db import main as enhance_and_send_to_db

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

        logger.info("Enhancing with Google Maps data and loading to database...")
        enhance_and_send_to_db()
        
    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
        raise
    finally:
        WebDriverManager.cleanup()
        if platform.system() != 'Windows':
            signal.alarm(0)

if __name__ == "__main__":
    main()
