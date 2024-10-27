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

# List of user-agent headers to rotate
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0"
]

def scrape_eater_page(url, output_csv):
    try:
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")
        
        # Initialize the WebDriver
        driver = webdriver.Chrome(options=chrome_options)
        
        # Load the page
        driver.get(url)
        
        # Wait for the page to load
        time.sleep(random.uniform(5, 10))
        
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
        
        # Close the WebDriver
        driver.quit()
        
        # Write or append data to the output CSV
        fieldnames = ['Restaurant Name', 'Restaurant Description', 'Address', 'Phone', 'Website', 'Google Maps Link', 'Instagram Name', 'Instagram URL']
        with open(output_csv, 'a', newline='', encoding='utf-8') as file:  
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if file.tell() == 0:  # Check if file is empty (first write)
                writer.writeheader()
            writer.writerows(data)
        
    except Exception as e:
        print(f"Error: {e}")
        if 'driver' in locals():
            driver.quit()

def is_duplicate_entry(csv_file, new_entry):
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Restaurant Name'] == new_entry['Restaurant Name'] and row['Address'] == new_entry['Address']:
                    return True
    except FileNotFoundError:
        pass  # File does not exist yet, so no duplicates
    return False

def scrape_eater_archives():
    output_csv = "S:/restaurant_data_project/data/raw/raw_restaurants.csv"
    base_url = "https://www.eater.com/maps/archives"
    pages_to_scrape = 75
    
    for page in range(1, pages_to_scrape + 1):
        try:
            url = base_url if page == 1 else f"{base_url}?page={page}"
            # Rotate user-agent headers
            user_agent = random.choice(user_agents)
            headers = {"User-Agent": user_agent}

            # Send HTTP request with rotated user-agent
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Rate limiting: Wait for 2-5 seconds before parsing the response
            time.sleep(random.uniform(2, 5))
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract article links from the archive page
            article_links = []
            for entry in soup.find_all('div', class_='c-compact-river__entry'):
                link = entry.find('a')['href']
                # Ensure link is absolute (starts with http)
                if not link.startswith('http'):
                    link = 'https://www.eater.com' + link
                article_links.append(link)
            
            # Iterate through each article link and scrape
            for article_link in article_links:
                print(f"Scraping: {article_link} (Page {page}/{pages_to_scrape})")
                scrape_eater_page(article_link, output_csv)
                # Additional rate limiting between article scrapes (5-10 seconds)
                time.sleep(random.uniform(5, 10))
        
        except requests.RequestException as e:
            # Monitor for errors and print the error message
            print(f"Request Error (Archives Page {page}): {e}")
            if hasattr(e, 'response') and e.response.status_code == 403:
                print("Forbidden: Possible policy change or issue with the script. Review the site's robots.txt and adjust the script accordingly.")

if __name__ == "__main__":
    scrape_eater_archives()