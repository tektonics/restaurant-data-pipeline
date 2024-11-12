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
from ..config.config import EATER_CONFIG, CHROME_OPTIONS, RAW_RESTAURANTS_CSV
from contextlib import contextmanager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get user agents from config
user_agents = EATER_CONFIG['user_agents']

@contextmanager
def create_driver():
    """Create and return a configured Chrome WebDriver instance"""
    driver = None
    try:
        # Initialize Chrome options
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Comment out headless mode for debugging
        chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
        chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
        chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
        chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        
        # Create and return the driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(60)  # Increased timeout to 60 seconds
        yield driver
        
    except Exception as e:
        logger.error(f"Error creating WebDriver: {str(e)}")
        raise
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
            time.sleep(3)  # Allow time for cleanup

def scrape_eater_page(url, output_csv):
    logger.info(f"Attempting to load page: {url}")
    
    with create_driver() as driver:
        try:
            # Load the page with explicit wait
            driver.get(url)
            time.sleep(10)  # Wait for 10 seconds after loading the page
            
            # Wait for main content to load with increased timeout
            wait = WebDriverWait(driver, 30)  # Increased from 20 to 30 seconds
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'c-mapstack__card')))
            
            # Parse the page source with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Find all restaurant entries on the page
            restaurant_entries = soup.find_all('section', class_='c-mapstack__card')
            
            # Initialize data list
            data = []
            
            for entry in restaurant_entries:
                # Extract restaurant name
                name = entry.find('h1').text.strip() if entry.find('h1') else "Name Not Found"
                
                # Extract restaurant description
                description_container = entry.find('div', class_='c-entry-content venu-card')
                if description_container:
                    description_paragraphs = description_container.find_all('p')
                    description = ''.join([p.text.strip() for p in description_paragraphs])
                else:
                    description = "Description Not Found"
                
                # Extract restaurant info (address, phone, website, Google Maps link)
                info_section = entry.find('div', class_='c-mapstack__info')
                
                # Initialize with default values
                address = "Address Not Found"
                phone = "Phone Not Found"
                website = "Website Not Found"
                google_maps_link = "Google Maps Link Not Found"
                instagram_name = "Instagram Name Not Found"
                instagram_url = "Instagram URL Not Found"

                if info_section:
                    # Extract Google Maps link and address
                    address_div = info_section.find('div', class_='c-mapstack__address')
                    if address_div:
                        google_maps_link = address_div.find('a')['href']
                        address = address_div.text.strip()

                    # Extract other info
                    info_items = info_section.find_all('div', class_='info')
                    for item in info_items:
                        icon = item.find('div', class_='info-icon').find('svg').find('use')['xlink:href']
                        if '#icon-phone' in icon:
                            phone = item.find('div', class_='c-mapstack__phone-url').find('a').text.strip()
                        elif '#icon-world' in icon:
                            website = item.find('a')['href']

                # Extract Instagram information
                video_section = entry.find('div', class_='c-mapstack__video')
                if video_section:
                    iframe = video_section.find('iframe', id=lambda x: x and x.startswith('instagram-embed-'))
                    if iframe:
                        iframe_id = iframe['id']
                        try:
                            # Switch to the iframe
                            driver.switch_to.frame(iframe_id)
                            
                            # Wait for the ViewProfileButton to be present
                            wait = WebDriverWait(driver, 10)
                            view_profile_button = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'ViewProfileButton')))
                            
                            # Extract Instagram information
                            instagram_url = view_profile_button.get_attribute('href')
                            instagram_name = instagram_url.split('instagram.com/')[-1].split('?')[0]
                            
                            # Switch back to the main content
                            driver.switch_to.default_content()
                        except Exception as e:
                            print(f"Error extracting Instagram info: {e}")
                            driver.switch_to.default_content()
                
                # Condition to check if name and address are found before appending to data
                if name != "Name Not Found" and address != "Address Not Found":
                    new_entry = {
                        'Restaurant Name': name,
                        'Restaurant Description': description,
                        'Address': address,
                        'Phone': phone,
                        'Website': website,
                        'Google Maps Link': google_maps_link,
                        'Instagram Name': instagram_name,
                        'Instagram URL': instagram_url
                    }
                    
                    # Check for duplicate entry
                    if not is_duplicate_entry(output_csv, new_entry):
                        data.append(new_entry)
            
            # Write or append data to the output CSV
            fieldnames = ['Restaurant Name', 'Restaurant Description', 'Address', 'Phone', 'Website', 'Google Maps Link', 'Instagram Name', 'Instagram URL']
            with open(output_csv, 'a', newline='', encoding='utf-8') as file:  
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                if file.tell() == 0:  # Check if file is empty (first write)
                    writer.writeheader()
                writer.writerows(data)
            
            return  # Success - exit the retry loop
            
        except WebDriverException as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {str(e)}")
            raise

def is_duplicate_entry(csv_file, new_entry):
    """Check if a restaurant entry already exists in the CSV file"""
    try:
        # If file doesn't exist, it's not a duplicate
        if not os.path.exists(csv_file):
            return False
            
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            existing_entries = [(row['Restaurant Name'], row['Address']) for row in reader]
            
            # Check if the new entry's name and address combination already exists
            new_key = (new_entry['Restaurant Name'], new_entry['Address'])
            return new_key in existing_entries
            
    except Exception as e:
        logger.error(f"Error checking for duplicates: {str(e)}")
        return False  # If there's an error, assume it's not a duplicate
    
    return False

def scrape_eater_archives():
    output_csv = RAW_RESTAURANTS_CSV
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    base_url = EATER_CONFIG['base_url']
    
    try:
        # Only process the first page
        url = base_url
        logger.info("Processing first archive page only")

        response = requests.get(
            url, 
            headers={"User-Agent": random.choice(user_agents)},
            timeout=30
        )
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get only the first article link
        entry = soup.find('div', class_='c-compact-river__entry')
        if entry and entry.find('a'):
            article_url = entry.find('a')['href']
            if not article_url.startswith('http'):
                article_url = 'https://www.eater.com' + article_url
                
            logger.info("Processing single test article")
            scrape_eater_page(article_url, output_csv)
            
    except Exception as e:
        logger.error(f"Error processing test article: {str(e)}")
        raise

"""
TESTING vs PRODUCTION Configuration:

To switch between testing (single article) and production (full scrape), 
uncomment one version of scrape_eater_archives() and comment out the other.
"""
"""
#Testing - Single Article
def scrape_eater_archives():
    output_csv = RAW_RESTAURANTS_CSV
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    base_url = EATER_CONFIG['base_url']
    
    try:
        # Only process the first page
        url = base_url
        logger.info("Processing first archive page only")

        response = requests.get(
            url, 
            headers={"User-Agent": random.choice(user_agents)},
            timeout=30
        )
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get only the first article link
        entry = soup.find('div', class_='c-compact-river__entry')
        if entry and entry.find('a'):
            article_url = entry.find('a')['href']
            if not article_url.startswith('http'):
                article_url = 'https://www.eater.com' + article_url
                
            logger.info("Processing single test article")
            scrape_eater_page(article_url, output_csv)
            
    except Exception as e:
        logger.error(f"Error processing test article: {str(e)}")
        raise
"""

#To switch back to PRODUCTION version, replace the above function with this:

def scrape_eater_archives():
    output_csv = RAW_RESTAURANTS_CSV
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    base_url = EATER_CONFIG['base_url']
    pages_to_scrape = EATER_CONFIG['pages_to_scrape']
    
    for page in range(1, pages_to_scrape + 1):
        try:
            url = base_url if page == 1 else f"{base_url}?page={page}"
            logger.info(f"Processing archive page {page}/{pages_to_scrape}")

            # Add retry mechanism for requests
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries:
                try:
                    response = requests.get(
                        url, 
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
            article_links = []
            
            # Extract and process links
            for entry in soup.find_all('div', class_='c-compact-river__entry'):
                link = entry.find('a')
                if link and 'href' in link.attrs:
                    article_url = link['href']
                    if not article_url.startswith('http'):
                        article_url = 'https://www.eater.com' + article_url
                    article_links.append(article_url)
            
            logger.info(f"Found {len(article_links)} articles on page {page}")
            
            # Process each article
            for i, article_link in enumerate(article_links, 1):
                logger.info(f"Processing article {i}/{len(article_links)} on page {page}")
                scrape_eater_page(article_link, output_csv)
                time.sleep(random.uniform(
                    EATER_CONFIG['delay']['between_articles'][0],
                    EATER_CONFIG['delay']['between_articles'][1]
                ))
                
        except requests.Timeout:
            logger.error(f"Timeout accessing archive page {page}")
            continue
        except requests.RequestException as e:
            logger.error(f"Request error on page {page}: {str(e)}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error on page {page}: {str(e)}")
            continue


if __name__ == "__main__":
    scrape_eater_archives()
