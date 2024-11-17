import logging
from concurrent.futures import ThreadPoolExecutor
from itertools import islice
from src.scrapers.FetchGoogleData import fetch_google_maps_data
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import pandas as pd
import csv
from urllib.parse import quote

logger = logging.getLogger(__name__)

def process_with_parallel(df, output_file, fieldnames):
    """Enhanced parallel processing with better error handling and progress tracking"""
    chunk_size = 100  # Adjust the chunk size as needed
    chunks = [df[i:i + chunk_size] for i in range(0, len(df), chunk_size)]
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(process_chunk, chunk, idx, output_file, fieldnames)
            for idx, chunk in enumerate(chunks)
        ]
        
        for future in futures:
            try:
                future.result()
            except Exception as e:
                logger.error(f"Error in parallel processing: {str(e)}")

def process_chunk(chunk_df, chunk_id, output_file, fieldnames):
    """Process a chunk of restaurants with its own WebDriver instance"""
    driver = None
    try:
        chrome_options = Options()
        CHROME_OPTIONS = ['--headless', '--disable-gpu', '--no-sandbox']  # Add your desired Chrome options here
        for option in CHROME_OPTIONS:
            chrome_options.add_argument(option)
            
        try:
            # First try using system ChromeDriver
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            logger.warning(f"System ChromeDriver failed, trying alternative path: {e}")
            try:
                # Try explicit path to ChromeDriver
                service = Service('/usr/bin/chromedriver')
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                logger.error(f"All ChromeDriver attempts failed: {e}")
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