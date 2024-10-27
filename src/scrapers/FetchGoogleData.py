import csv
import time
import random
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

def clean_text(text):
    return re.sub(r'^[^\w\s]+|\s+', ' ', text).strip()

def fetch_google_maps_data(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(url)
        time.sleep(random.uniform(5, 8))
        
        try:
            about_tab = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@role='tab' and contains(., 'About')]"))
            )
            about_tab.click()
            time.sleep(3)
        except (TimeoutException, NoSuchElementException):
            print(f"About tab not found or not clickable for URL: {url}")
        
        # Extract star rating
        try:
            star_rating = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.ceNzKf"))
            ).get_attribute('aria-label').split()[0]
        except:
            star_rating = 'Not available'

        # Extract number of reviews
        try:
            reviews = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span[aria-label*='reviews']"))
            ).text.strip('()')
        except:
            reviews = 'Not available'

        # Extract restaurant category
        try:
            category = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[jsaction='pane.rating.category']"))
            ).text
        except:
            category = 'Not available'

        # Extract latitude and longitude from URL
        lat_long_match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
        latitude = lat_long_match.group(1) if lat_long_match else 'Not available'
        longitude = lat_long_match.group(2) if lat_long_match else 'Not available'

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Extract information from each section
        sections = soup.find_all('div', class_='iP2t7d')
        data = {
            'Star Rating': star_rating,
            'Number of Reviews': reviews,
            'Restaurant Category': category,
            'Latitude': latitude,
            'Longitude': longitude
        }
        
        for section in sections:
            title = section.find('h2', class_='iL3Qke')
            if title:
                title = title.text.strip()
                items = [clean_text(item.text.strip()) for item in section.find_all('div', class_='iNvpkb')]
                data[title] = ', '.join(items) if items else 'Not available'
        
        return data
    
    except Exception as e:
        print(f"Error processing URL {url}: {str(e)}")
        return {}
    
    finally:
        driver.quit()

def process_csv(input_file, output_file):
    with open(input_file, 'r', newline='', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + [
            'Star Rating', 'Number of Reviews', 'Restaurant Category',
            'Latitude', 'Longitude', 'Accessibility', 'Service options',
            'Highlights', 'Popular for', 'Offerings', 'Dining options',
            'Amenities', 'Atmosphere', 'Crowd', 'Planning', 'Payments', 'Parking'
        ]
        
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            print(f"Processing: {row['Restaurant Name']}")
            google_maps_url = row['Google Maps Link']
            
            if google_maps_url and google_maps_url != "Google Maps Link Not Found":
                additional_data = fetch_google_maps_data(google_maps_url)
                row.update(additional_data)
            
            writer.writerow(row)
            time.sleep(random.uniform(2, 4))

if __name__ == "__main__":
    input_csv = "S:/restaurant_data_project/data/raw/cleaned_restaurants.csv"
    output_csv = "S:/restaurant_data_project/data/processed/cleaned_restaurants_enhanced.csv"
    process_csv(input_csv, output_csv)