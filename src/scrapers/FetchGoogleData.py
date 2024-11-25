import csv
import time
import random
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from bs4 import BeautifulSoup
from ..config.config import (
    CLEANED_RESTAURANTS_CSV, 
    ENHANCED_RESTAURANTS_CSV, 
    CHROME_OPTIONS, 
    TIMEOUT_CONFIG,
    EXPECTED_GOOGLE_FIELDS
)
import logging
from src.utils.helpers import ensure_directories_exist
from pathlib import Path
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote
import pandas as pd
import os
from src.utils.webdriver_manager import WebDriverManager
from src.utils.csv_handler import ensure_csv_exists, write_row

logging.basicConfig(level=logging.INFO)
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
    data = {field: 'Not available' for field in EXPECTED_GOOGLE_FIELDS}

    try:
        driver.get(url)
        time.sleep(1)

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
                    time.sleep(1)
            except:
                pass

        try:
            info_container = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.m6QErb[role="region"]'))
            )
            time.sleep(5)
            
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
                    
        except TimeoutException:
            logger.warning("Info container not found within timeout")
            return data
        except Exception as e:
            logger.error(f"Error extracting information sections: {str(e)}")
            return data

        if coords := re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', driver.current_url):
            data['Latitude'], data['Longitude'] = coords.groups()

        return data

    except Exception as e:
        logger.error(f"Error fetching Google Maps data: {str(e)}")
        return data

def extract_attributes(section):
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
    driver = None
    try:
        driver = WebDriverManager.create_driver()
        df = pd.read_csv(input_file)
        
        ensure_csv_exists(output_file, list(df.columns) + list(EXPECTED_GOOGLE_FIELDS))
        
        for index, row in df.iterrows():
            try:
                logger.info(f"Processing row {index + 1}/{len(df)}")
                google_maps_url = row.get('Google Maps Link')
                
                if not google_maps_url or google_maps_url == 'Google Maps Link Not Found':
                    search_query = f"{row['Restaurant Name']} {row['Address']} {row['City']} {row['State']}"
                    google_maps_url = f"https://www.google.com/maps/search/{quote(search_query)}"
                
                google_data = fetch_google_maps_data(google_maps_url, driver)
                processed_row = {**row.to_dict(), **google_data}
                
                write_row(output_file, processed_row, list(df.columns) + list(EXPECTED_GOOGLE_FIELDS))
                
            except Exception as e:
                logger.error(f"Error processing row {index}: {str(e)}")
                write_row(output_file, row.to_dict(), list(df.columns) + list(EXPECTED_GOOGLE_FIELDS))
                continue
                
    finally:
        if driver:
            driver.quit()

def process_google_data(input_file=CLEANED_RESTAURANTS_CSV, output_file=ENHANCED_RESTAURANTS_CSV):
    process_csv(input_file, output_file)

if __name__ == "__main__":
    process_google_data()
