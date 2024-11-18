import logging
import requests
from bs4 import BeautifulSoup
import time
import random
import csv
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from ..config.config import EATER_CONFIG, CHROME_OPTIONS, RAW_RESTAURANTS_CSV, CLEANED_RESTAURANTS_CSV
from contextlib import contextmanager
import pandas as pd
from threading import Timer
from ..data_processing.cleanAddrRestaurants import fill_missing_city, clean_and_split_address
from ..utils.cleaning_monitor import log_cleaning_progress
from src.utils.webdriver_manager import create_driver

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

user_agents = EATER_CONFIG['user_agents']

POST_PROCESS_INTERVAL = 300
last_post_process_time = 0

@contextmanager
def get_scraping_driver():
    """Get a configured WebDriver instance for scraping"""
    driver = None
    try:
        driver = create_driver([f"user-agent={random.choice(user_agents)}"])
        yield driver
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
            time.sleep(3)

def scrape_eater_page(url, output_csv):
    logger.info(f"Attempting to load page: {url}")
    
    with get_scraping_driver() as driver:
        try:
            driver.get(url)
            time.sleep(3)
            
            wait = WebDriverWait(driver, 15)  
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'c-mapstack__card')))
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            restaurant_entries = soup.find_all('section', class_='c-mapstack__card')
            
            data = []
            
            for entry in restaurant_entries:
                name = entry.find('h1').text.strip() if entry.find('h1') else "Name Not Found"
                
                description_container = entry.find('div', class_='c-entry-content venu-card')
                if description_container:
                    description_paragraphs = description_container.find_all('p')
                    description = ''.join([p.text.strip() for p in description_paragraphs])
                else:
                    description = "Description Not Found"
                
                info_section = entry.find('div', class_='c-mapstack__info')
                
                address = "Address Not Found"
                phone = "Phone Not Found"
                website = "Website Not Found"
                google_maps_link = "Google Maps Link Not Found"

                if info_section:
                    address_div = info_section.find('div', class_='c-mapstack__address')
                    if address_div:
                        google_maps_link = address_div.find('a')['href']
                        address = address_div.text.strip()

                    info_items = info_section.find_all('div', class_='info')
                    for item in info_items:
                        icon = item.find('div', class_='info-icon').find('svg').find('use')['xlink:href']
                        if '#icon-phone' in icon:
                            phone = item.find('div', class_='c-mapstack__phone-url').find('a').text.strip()
                        elif '#icon-world' in icon:
                            website = item.find('a')['href']

                if name != "Name Not Found" and address != "Address Not Found":
                    new_entry = {
                        'Restaurant Name': name,
                        'Restaurant Description': description,
                        'Address': address,
                        'Phone': phone,
                        'Website': website,
                        'Google Maps Link': google_maps_link
                    }
                    
                    if not is_duplicate_entry(output_csv, new_entry):
                        write_to_raw_csv(new_entry, output_csv)
                        
                        clean_and_write_entry(new_entry, CLEANED_RESTAURANTS_CSV)
            
            return  
            
        except WebDriverException as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {str(e)}")
            raise

def write_to_raw_csv(entry, output_csv):
    """Write a single entry to the raw CSV file"""
    fieldnames = ['Restaurant Name', 'Restaurant Description', 'Address', 'Phone', 
                 'Website', 'Google Maps Link']
    
    with open(output_csv, 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if file.tell() == 0:  
            writer.writeheader()
        writer.writerow(entry)

def post_process_cleaned_data():
    """Post-process the cleaned CSV to fill missing cities"""
    try:
        
        df = pd.read_csv(CLEANED_RESTAURANTS_CSV)
        
        df = fill_missing_city(df)
        
        df.to_csv(CLEANED_RESTAURANTS_CSV, index=False)
        logger.info("Post-processing completed successfully")
        
    except Exception as e:
        logger.error(f"Error during post-processing: {e}")

def should_run_post_processing():
    global last_post_process_time
    current_time = time.time()
    
    if current_time - last_post_process_time >= POST_PROCESS_INTERVAL:
        last_post_process_time = current_time
        return True
    return False

def clean_and_write_entry(entry, cleaned_csv):
    cleaned_components = clean_and_split_address(entry['Address'])
    
    cleaned_entry = {
        **entry, 
        'Cleaned Address': cleaned_components['Address'],
        'City': cleaned_components['City'],
        'State': cleaned_components['State'],
        'Zip': cleaned_components['Zip']
    }
    
    if not cleaned_entry['Zip']:
        return
    
    fieldnames = ['Restaurant Name', 'Restaurant Description', 'Address', 'Phone', 
                 'Website', 'Google Maps Link', 'Cleaned Address', 'City', 'State', 'Zip']
    
    with open(cleaned_csv, 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if file.tell() == 0:  
            writer.writeheader()
        writer.writerow(cleaned_entry)
    
    if should_run_post_processing():
        post_process_cleaned_data()

def is_duplicate_entry(csv_file, new_entry):
    """Check if a restaurant entry already exists in the CSV file"""
    try:
        
        if not os.path.exists(csv_file):
            return False
            
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            existing_entries = [(row['Restaurant Name'], row['Address']) for row in reader]
            
            new_key = (new_entry['Restaurant Name'], new_entry['Address'])
            return new_key in existing_entries
            
    except Exception as e:
        logger.error(f"Error checking for duplicates: {str(e)}")
        return False  
    
    return False

def scrape_eater_archives():
    """Main scraping function"""
    global last_post_process_time
    last_post_process_time = time.time()
    
    output_csv = RAW_RESTAURANTS_CSV
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    os.makedirs(os.path.dirname(CLEANED_RESTAURANTS_CSV), exist_ok=True)
    base_url = EATER_CONFIG['base_url']
    start_page = EATER_CONFIG['page_range']['start']
    end_page = EATER_CONFIG['page_range']['end']
    
    try:
        for page in range(start_page, end_page + 1):
            logger.info(f"Processing archive page {page} (range: {start_page}-{end_page})")
            
            page_url = f"{base_url}?page={page}" if page > 1 else base_url
            
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries:
                try:
                    response = requests.get(
                        page_url, 
                        headers={"User-Agent": random.choice(user_agents)},
                        timeout=30
                    )
                    response.raise_for_status()
                    break
                except (requests.Timeout, requests.RequestException) as e:
                    retry_count += 1
                    logger.warning(f"Attempt {retry_count} failed: {e}")
                    if retry_count == max_retries:
                        raise
                    time.sleep(5)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Get all article links
            entries = soup.find_all('div', class_='c-compact-river__entry')
            if not entries:
                logger.warning(f"No entries found on page {page}. Stopping pagination.")
                break
                
            for idx, entry in enumerate(entries, 1):
                if link := entry.find('a'):
                    article_url = link['href']
                    if not article_url.startswith('http'):
                        article_url = 'https://www.eater.com' + article_url
                        
                    logger.info(f"Processing article {idx}/{len(entries)} on page {page}")
                    scrape_eater_page(article_url, output_csv)
                    time.sleep(2)
            
    except requests.Timeout:
        logger.error("Timeout accessing archive page")
    except requests.RequestException as e:
        logger.error(f"Request error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        post_process_cleaned_data()

if __name__ == "__main__":
    scrape_eater_archives()
