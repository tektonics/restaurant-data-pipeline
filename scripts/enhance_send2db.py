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
from src.config.config import CHROME_OPTIONS
from urllib.parse import quote
import csv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_chunk(chunk_df, chunk_id, output_file, fieldnames):
    """Process a chunk of restaurants with its own WebDriver instance"""
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        chrome_options = Options()
        for option in CHROME_OPTIONS:
            chrome_options.add_argument(option)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        total_in_chunk = len(chunk_df)
        
        for idx, row in chunk_df.iterrows():
            try:
                logger.info(f"Chunk {chunk_id}: Processing {idx - chunk_df.index[0] + 1}/{total_in_chunk}")
                
                # Generate Google Maps URL if missing
                google_maps_url = row.get('Google Maps Link')
                if not google_maps_url or google_maps_url == 'Google Maps Link Not Found':
                    search_query = f"{row['Restaurant Name']} {row['Address']} {row['City']} {row['State']}"
                    google_maps_url = f"https://www.google.com/maps/search/{quote(search_query)}"
                
                google_data = fetch_google_maps_data(google_maps_url, driver)
                processed_row = {**row.to_dict(), **google_data}
                
                # Write row immediately with file locking
                with open(output_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writerow(processed_row)
                    
                logger.info(f"Successfully processed and saved: {row['Restaurant Name']}")
                
            except Exception as e:
                logger.error(f"Error processing row {idx} in chunk {chunk_id}: {str(e)}")
                # Write original row on error
                with open(output_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writerow(row.to_dict())
                continue
                
    finally:
        if driver:
            driver.quit()

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

def write_row_to_csv(row_data, output_file, fieldnames):
    """Write a single row to CSV with proper locking"""
    with open(output_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writerow(row_data)

def main():
    try:
        # Reference the fieldnames from FetchGoogleData.py
        fieldnames = [
            'Restaurant Name', 'Restaurant Description', 'Address', 'Phone', 'Website',
            'Google Maps Link', 'Cleaned Address',
            'City', 'State', 'Zip', 'Star Rating', 'Number of Reviews',
            'Restaurant Category', 'Price Range', 'Latitude', 'Longitude', 'Accessibility',
            'Service options', 'Highlights', 'Popular for', 'Offerings',
            'Dining options', 'Amenities', 'Atmosphere', 'Planning',
            'Payments', 'Parking', 'Doesnt Offer'
        ]
        
        input_csv = Path("data/raw/missing_restaurants.csv")
        enhanced_csv = Path("data/processed/cleaned_restaurants_enhanced.csv")
        enhanced_csv.parent.mkdir(parents=True, exist_ok=True)
        
        # Create output file with headers if it doesn't exist
        if not enhanced_csv.exists():
            with open(enhanced_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
        
        df = pd.read_csv(input_csv)
        total_rows = len(df)
        
        num_workers = 4
        chunk_size = math.ceil(total_rows / num_workers)
        chunks = [df[i:i + chunk_size] for i in range(0, total_rows, chunk_size)]
        
        logger.info(f"Processing {total_rows} restaurants with {num_workers} workers")
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [
                executor.submit(process_chunk, chunk, i, enhanced_csv, fieldnames)
                for i, chunk in enumerate(chunks)
            ]
            
            for future in futures:
                future.result()  # Wait for completion and propagate exceptions
        
        logger.info("All chunks processed. Loading data into database...")
        
        # Load into database
        db = RestaurantDB()
        try:
            db.connect()
            final_df = pd.read_csv(enhanced_csv)
            db.insert_restaurant_data(final_df)
            logger.info("Data successfully loaded into database")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        raise

if __name__ == "__main__":
    main()
