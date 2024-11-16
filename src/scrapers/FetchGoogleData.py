import csv
import time
import random
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from bs4 import BeautifulSoup
from ..config.config import CLEANED_RESTAURANTS_CSV, ENHANCED_RESTAURANTS_CSV, CHROME_OPTIONS, TIMEOUT_CONFIG
import logging
from src.utils.helpers import ensure_directories_exist
from pathlib import Path
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clean_text(text):
    if not text:
        return ''
    return ' '.join(text.split())

def safe_find_element(driver, by, selector, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        return element
    except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
        return None

def get_element_text(driver, selectors, default='Not available'):
    for by, selector in selectors:
        element = safe_find_element(driver, by, selector)
        if element:
            try:
                return clean_text(element.text)
            except:
                continue
    return default

def fetch_google_maps_data(url, driver=None):
    data = {
        'Star Rating': 'Not available',
        'Number of Reviews': 'Not available',
        'Restaurant Category': 'Not available',
        'Price Range': 'Not available',
        'Latitude': 'Not available',
        'Longitude': 'Not available',
        'Accessibility': 'Not available',
        'Service options': 'Not available',
        'Highlights': 'Not available',
        'Popular for': 'Not available',
        'Offerings': 'Not available',
        'Dining options': 'Not available',
        'Amenities': 'Not available',
        'Atmosphere': 'Not available',
        'Planning': 'Not available',
        'Payments': 'Not available',
        'Parking': 'Not available',
        'Doesnt Offer': 'Not available'
    }

    try:
        driver.get(url)
        time.sleep(0.5)

        try:
            elements = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((
                    By.CSS_SELECTOR, 
                    'div.F7nice, button.DkEaL[jsaction*="category"], span[aria-label*="Price"]'
                ))
            )
            
            for element in elements:
                class_name = element.get_attribute('class')
                if 'F7nice' in class_name:
                    rating_text = element.text
                    if rating_match := re.search(r'(\d+\.\d+)', rating_text):
                        data['Star Rating'] = rating_match.group(1)
                    if reviews_match := re.search(r'\(([0-9,]+)\)', rating_text):
                        data['Number of Reviews'] = reviews_match.group(1).replace(',', '')
                elif 'DkEaL' in class_name:
                    data['Restaurant Category'] = element.text
                else:
                    aria_label = element.get_attribute('aria-label')
                    if aria_label and 'Price' in aria_label:
                        data['Price Range'] = element.text.strip()

        except Exception as e:
            logger.error(f"Error extracting basic info: {str(e)}")

        if 'Not available' in data.values():
            try:
                about_tab = safe_find_element(driver, By.CSS_SELECTOR, 'button[aria-label*="About"]', timeout=2)
                if about_tab:
                    about_tab.click()
                    time.sleep(0.3)
            except:
                pass

        try:
            info_container = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.m6QErb[role="region"]'))
            )
            
            if info_container:
                info_sections = info_container.find_elements(
                    By.CSS_SELECTOR, 
                    'div.iP2t7d, div.LBgpqf'
                )
                
                unavailable_items = []
                for section in info_sections:
                    try:
                        title_element = section.find_element(By.CSS_SELECTOR, 'h2.iL3Qke')
                        section_title = title_element.text.strip()
                        
                        available_options, section_unavailable = extract_attributes(section)
                        
                        if section_title in data and available_options:
                            data[section_title] = ', '.join(available_options)
                        
                        if section_unavailable:
                            unavailable_items.extend(section_unavailable)
                            
                    except Exception as e:
                        logger.error(f"Error processing section: {str(e)}")
                        continue

                if unavailable_items:
                    data['Doesnt Offer'] = ', '.join(unavailable_items)
                    
        except Exception as e:
            logger.error(f"Error extracting information sections: {str(e)}")

        if coords := re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', driver.current_url):
            data['Latitude'], data['Longitude'] = coords.groups()

        return data

    except Exception as e:
        logger.error(f"Error fetching Google Maps data: {str(e)}")
        return data

def extract_attributes(section):
    """Extract attributes from a section, handling both available and unavailable items"""
    available_options = []
    unavailable_options = []
    
    options = section.find_elements(By.CSS_SELECTOR, 'div.iNvpkb, div.Rz1y8b')
    for option in options:
        try:
            spans = option.find_elements(By.CSS_SELECTOR, 'span[aria-label]')
            if not spans:
                continue
                
            option_text = spans[0].get_attribute('aria-label')
            
            not_available = (
                'XJynsc' in option.get_attribute('class') or
                bool(option.find_elements(By.CSS_SELECTOR, 'span.OazX1c')) or
                'wmQCje' in option.get_attribute('class') or
                option_text.startswith(("No ", "Doesn't ")) or
                "not available" in option_text.lower()
            )
            
            option_text = clean_text(option_text)
            for prefix in ("Has ", "Serves ", "No ", "Doesn't "):
                if option_text.startswith(prefix):
                    option_text = option_text[len(prefix):]
                    break
                
            (unavailable_options if not_available else available_options).append(option_text)
                
        except Exception as e:
            logger.debug(f"Error processing option: {str(e)}")
            continue
            
    return available_options, unavailable_options

def process_csv(input_file, output_file):
    """Process CSV file and fetch Google Maps data"""
    fieldnames = [
        'Restaurant Name', 'Restaurant Description', 'Address', 'Phone', 'Website',
        'Google Maps Link', 'Cleaned Address',
        'City', 'State', 'Zip', 'Star Rating', 'Number of Reviews',
        'Restaurant Category', 'Price Range', 
        'Latitude', 'Longitude', 'Accessibility',
        'Service options', 'Highlights', 'Popular for', 'Offerings',
        'Dining options', 'Amenities', 'Atmosphere', 'Planning',
        'Payments', 'Parking', 'Doesnt Offer'
    ]

    if not Path(input_file).exists():
        logger.error(f"Input file does not exist: {input_file}")
        return
        
    with open(input_file, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()
        if not first_line:
            logger.error("Input file is empty")
            return
            
        # Verify headers
        expected_headers = {'Restaurant Name', 'Address', 'City', 'State'}
        actual_headers = set(first_line.split(','))
        missing_headers = expected_headers - actual_headers
        if missing_headers:
            logger.error(f"Missing required headers: {missing_headers}")
            return

    try:
        service = Service(ChromeDriverManager().install())
        chrome_options = Options()
        for option in CHROME_OPTIONS:
            chrome_options.add_argument(option)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(5)  # Reduced from TIMEOUT_CONFIG['element_wait']
        driver.set_page_load_timeout(15)  # Reduced from TIMEOUT_CONFIG['page_load']

        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')  # Disable images
        chrome_options.add_argument('--disable-extensions')
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        if not Path(output_file).exists():
            with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()

        with open(input_file, 'r', encoding='utf-8') as f:
            total_rows = sum(1 for _ in csv.DictReader(f))

        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            for i, row in enumerate(reader, 1):
                try:
                    logger.info(f"Processing row {i} of {total_rows}: {row.get('Restaurant Name', 'Unknown')}")
                    
                    google_maps_url = row.get('Google Maps Link')
                    if not google_maps_url or google_maps_url.strip() == '':
                        search_components = []
                        if row.get('Restaurant Name'):
                            search_components.append(row['Restaurant Name'])
                        if row.get('Address'):
                            search_components.append(row['Address'])
                        if row.get('City'):
                            search_components.append(row['City'])
                        if row.get('State'):
                            search_components.append(row['State'])
                            
                        search_query = ' '.join(search_components) + ' restaurant'
                        google_maps_url = f"https://www.google.com/maps/search/{quote(search_query)}"
                        logger.info(f"Generated search URL for: {search_query}")
                    
                    google_data = fetch_google_maps_data(google_maps_url, driver=driver)
                    row.update(google_data)
                    
                    with open(output_file, 'a', newline='', encoding='utf-8') as outfile:
                        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                        writer.writerow(row)
                    
                    logger.info(f"Successfully processed: {row['Restaurant Name']}")
                    
                    time.sleep(random.uniform(0.5, 1))
                    
                except Exception as e:
                    logger.error(f"Error processing row {i}: {str(e)}")
                    logger.error(f"Row data: {row}") 
                    try:
                        driver.get('about:blank')
                    except:
                        if driver:
                            driver.quit()
                            driver = webdriver.Chrome(service=service, options=chrome_options)
                            driver.implicitly_wait(5)
                            driver.set_page_load_timeout(15)
                    continue
            
    except Exception as e:
        logger.error(f"Error processing CSV: {str(e)}")
    finally:
        if driver:
            driver.quit()

def process_google_data(input_file=CLEANED_RESTAURANTS_CSV, output_file=ENHANCED_RESTAURANTS_CSV):
    process_csv(input_file, output_file)

if __name__ == "__main__":
    process_google_data()
