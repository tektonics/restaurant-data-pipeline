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
from config.config import CLEANED_RESTAURANTS_CSV, ENHANCED_RESTAURANTS_CSV, CHROME_OPTIONS, TIMEOUT_CONFIG
import logging
from src.utils.helpers import ensure_directories_exist
from pathlib import Path
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return ''
    return re.sub(r'\s+', ' ', text).strip()

def safe_find_element(driver, by, selector, timeout=10):
    """Safely find an element with explicit wait and error handling"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        return element
    except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
        return None

def get_element_text(driver, selectors, default='Not available'):
    """Try multiple selectors to get element text"""
    for by, selector in selectors:
        element = safe_find_element(driver, by, selector)
        if element:
            try:
                return clean_text(element.text)
            except:
                continue
    return default

def fetch_google_maps_data(url, driver=None):
    """Fetch data from Google Maps using current selectors"""
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
        time.sleep(2)

        # Basic information
        try:
            # Get rating and review count together
            rating_element = safe_find_element(driver, By.CSS_SELECTOR, 'div.F7nice')
            if rating_element:
                rating_text = rating_element.text
                # Extract rating
                rating_match = re.search(r'(\d+\.\d+)', rating_text)
                if rating_match:
                    data['Star Rating'] = rating_match.group(1)
                # Extract review count
                reviews_match = re.search(r'\(([0-9,]+)\)', rating_text)
                if reviews_match:
                    data['Number of Reviews'] = reviews_match.group(1).replace(',', '')

            # Get category
            try:
                category = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "button.DkEaL[jsaction*='category']"))
                ).text
                data['Restaurant Category'] = category
            except:
                data['Restaurant Category'] = 'Not available'

            # Get price range
            price_range = safe_find_element(driver, By.CSS_SELECTOR, 'span[aria-label*="Price"]')
            if price_range:
                data['Price Range'] = price_range.text.strip()
        except Exception as e:
            logger.error(f"Error extracting basic info: {str(e)}")

        # Try to click "About" tab if it exists
        try:
            about_tab = safe_find_element(driver, By.CSS_SELECTOR, 'button[aria-label*="About"]')
            if about_tab:
                about_tab.click()
                time.sleep(2)  # Increased wait time for content to load
        except:
            logger.warning("About tab not found or not clickable")

        # Track all unavailable options
        unavailable_items = []

        # Extract all information sections
        try:
            # Main container for all sections
            info_container = safe_find_element(driver, By.CSS_SELECTOR, 'div.m6QErb[role="region"]')
            if info_container:
                # Get all sections
                info_sections = info_container.find_elements(By.CSS_SELECTOR, 'div.iP2t7d')
                
                for section in info_sections:
                    try:
                        # Get section title
                        title_element = section.find_element(By.CSS_SELECTOR, 'h2.iL3Qke')
                        section_title = title_element.text.strip()
                        
                        # Initialize lists for this section
                        available_options = []
                        section_unavailable = []
                        
                        # Get all options in the section
                        options = section.find_elements(By.CSS_SELECTOR, 'div.iNvpkb')
                        
                        for option in options:
                            # Get the span with aria-label for the text
                            option_span = option.find_element(By.CSS_SELECTOR, 'span[aria-label]')
                            option_text = option_span.get_attribute('aria-label')
                            
                            # Check if option is unavailable (has XJynsc class or OazX1c class)
                            not_available = any([
                                'XJynsc' in option.get_attribute('class'),
                                option.find_elements(By.CSS_SELECTOR, 'span.OazX1c'),
                                option_text.startswith("No "),
                                option_text.startswith("Doesn't "),
                                "not available" in option_text.lower()
                            ])
                            
                            if not_available:
                                # Clean up the text for unavailable items
                                if option_text.startswith("No "):
                                    option_text = option_text[3:]
                                elif option_text.startswith("Doesn't "):
                                    option_text = option_text[8:]
                                section_unavailable.append(option_text)
                            else:
                                # Clean up the text for available items
                                if option_text.startswith("Has "):
                                    option_text = option_text[4:]
                                elif option_text.startswith("Serves "):
                                    option_text = option_text[7:]
                                available_options.append(option_text)
                        
                        # Update data dictionary based on section title
                        if section_title in data:
                            if available_options:
                                data[section_title] = ', '.join(available_options)
                        
                        # Add unavailable options to the list
                        if section_unavailable:
                            unavailable_items.extend(section_unavailable)
                            
                    except Exception as e:
                        logger.error(f"Error processing section: {str(e)}")
                        continue

                # Combine all unavailable items into the Doesnt Offer field
                if unavailable_items:
                    data['Doesnt Offer'] = ', '.join(unavailable_items)
                    
        except Exception as e:
            logger.error(f"Error extracting information sections: {str(e)}")

        # Extract coordinates from URL
        try:
            coords = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', driver.current_url)
            if coords:
                data['Latitude'] = coords.group(1)
                data['Longitude'] = coords.group(2)
        except Exception as e:
            logger.error(f"Error extracting coordinates: {str(e)}")

        return data

    except Exception as e:
        logger.error(f"Error fetching Google Maps data: {str(e)}")
        return data

def process_csv(input_file, output_file):
    """Process CSV file and fetch Google Maps data"""
    fieldnames = [
        'Restaurant Name', 'Restaurant Description', 'Address', 'Phone', 'Website',
        'Google Maps Link', 'Instagram Name', 'Instagram URL', 'Cleaned Address',
        'City', 'State', 'Zip', 'Star Rating', 'Number of Reviews',
        'Restaurant Category', 'Price Range', 
        'Latitude', 'Longitude', 'Accessibility',
        'Service options', 'Highlights', 'Popular for', 'Offerings',
        'Dining options', 'Amenities', 'Atmosphere', 'Planning',
        'Payments', 'Parking', 'Doesnt Offer'  # Added Doesnt Offer
    ]

    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', newline='', encoding='utf-8') as outfile:
            
            reader = csv.DictReader(infile)
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            total_rows = sum(1 for row in csv.DictReader(open(input_file, 'r', encoding='utf-8')))
            infile.seek(0)
            next(reader)  # Skip header
            
            driver = None
            for i, row in enumerate(reader, 1):
                try:
                    if driver is None:
                        service = Service(ChromeDriverManager().install())
                        chrome_options = Options()
                        for option in CHROME_OPTIONS:
                            chrome_options.add_argument(option)
                        driver = webdriver.Chrome(service=service, options=chrome_options)
                        driver.implicitly_wait(TIMEOUT_CONFIG['element_wait'])
                        driver.set_page_load_timeout(TIMEOUT_CONFIG['page_load'])
                    
                    logger.info(f"Processing row {i} of {total_rows}: {row.get('Restaurant Name', 'Unknown')}")
                    
                    # Use existing Google Maps Link or create search URL
                    google_maps_url = row.get('Google Maps Link', '').strip()
                    if not google_maps_url:
                        search_query = f"{row['Restaurant Name']} {row.get('Address', '')} restaurant"
                        google_maps_url = f"https://www.google.com/maps/search/{quote(search_query)}"
                    
                    google_data = fetch_google_maps_data(google_maps_url, driver=driver)
                    row.update(google_data)
                    writer.writerow(row)
                    
                    # Log the collected data
                    logger.info(f"\nData collected for {row['Restaurant Name']}:")
                    logger.info("-" * 50)
                    logger.info(f"Star Rating: {google_data['Star Rating']}")
                    logger.info(f"Reviews: {google_data['Number of Reviews']}")
                    logger.info(f"Category: {google_data['Restaurant Category']}")
                    logger.info(f"Coordinates: {google_data['Latitude']}, {google_data['Longitude']}")
                    
                    # Log additional information if available
                    additional_info = {k: v for k, v in google_data.items() 
                                    if v != 'Not available' and k not in 
                                    ['Star Rating', 'Number of Reviews', 'Restaurant Category', 'Latitude', 'Longitude']}
                    if additional_info:
                        logger.info("\nAdditional Information:")
                        for key, value in additional_info.items():
                            logger.info(f"{key}: {value}")
                    logger.info("-" * 50 + "\n")
                    
                    # Random delay between requests
                    time.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    logger.error(f"Error processing row {i}: {str(e)}")
                    if driver:
                        try:
                            driver.quit()
                        except:
                            pass
                        driver = None
                    continue
            
    except Exception as e:
        logger.error(f"Error processing CSV: {str(e)}")
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def process_google_data(input_file=CLEANED_RESTAURANTS_CSV, output_file=ENHANCED_RESTAURANTS_CSV):
    """Main function to process Google Maps data"""
    process_csv(input_file, output_file)

if __name__ == "__main__":
    process_google_data()
