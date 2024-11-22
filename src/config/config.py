import os
from pathlib import Path
import logging

PROJECT_ROOT = Path(__file__).parent.parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

RAW_RESTAURANTS_CSV = RAW_DATA_DIR / "raw_restaurants.csv"
CLEANED_RESTAURANTS_CSV = RAW_DATA_DIR / "cleaned_restaurants.csv"
ENHANCED_RESTAURANTS_CSV = PROCESSED_DATA_DIR / "cleaned_restaurants_enhanced.csv"

REQUIRED_RESTAURANT_FIELDS = [
    'Restaurant Name',
    'Address',
]

EXPECTED_RESTAURANT_FIELDS = [
    'Restaurant Name',
    'Restaurant Description',
    'Address',
    'Phone',
    'Website',
    'Google Maps Link',
    'Embedded Links',
    'Venue ID'
]

EXPECTED_GOOGLE_FIELDS = [
    'Star Rating',
    'Number of Reviews',
    'Restaurant Category',
    'Latitude',
    'Longitude',
    'Accessibility',
    'Service options',
    'Highlights',
    'Popular for',
    'Offerings',
    'Dining options',
    'Amenities',
    'Atmosphere',
    'Crowd',
    'Planning',
    'Payments',
    'Parking',
    'Pets',
    'Children',
    'From the business'  
]

EATER_CONFIG = {
    'base_url': "https://www.eater.com/maps/archives",
    'page_range': {
        'start': 1,
        'end': 1
    },
    'user_agents': [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0"
    ],
    'delay': {
        'page_load': (5, 10),
        'between_articles': (5, 10),
        'between_pages': (2, 5)
    }
}

CHROME_OPTIONS = [
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--ignore-certificate-errors-spki-list",
    "--ignore-ssl-errors",
    "--log-level=3",
    "--disable-extensions",
    "--disable-notifications",
    "--disable-infobars",
    "--window-size=1920,1080",
    "--disable-accelerated-video-decode",
    "--disable-accelerated-video-encode",
    "--blink-settings=imagesEnabled=false",  
    "--disable-javascript",  
    "--disk-cache-size=1",  
    "--enable-unsafe-swiftshader"  
]

TIMEOUT_CONFIG = {
    'page_load': 15,  
    'script': 15,     
    'element_wait': 10 
}

DEFAULT_VALUES = {
    'name': "Name Not Found",
    'description': "Description Not Found",
    'address': "Address Not Found",
    'phone': "Phone Not Found",
    'website': "Website Not Found",
    'google_maps': "Google Maps Link Not Found",
    'venue_id': "Venue ID Not Found"
}

RATE_LIMITS = {
    'min_delay': 1,    
    'max_delay': 5,    
    'error_delay': 15  
}

MAX_RETRIES = 3
RETRY_DELAY = 5   

state_abbreviations = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
    'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
    'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
    'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
    'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
    'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
    'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
    'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT',
    'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
    'Wisconsin': 'WI', 'Wyoming': 'WY', 'District of Columbia': 'DC'
}

WEBDRIVER_CONFIG = {
    'driver_path': None,
    'implicit_wait': 10,
    'page_load_timeout': 30,
    'options': CHROME_OPTIONS
}

logging.getLogger('selenium').setLevel(logging.ERROR)

CSV_FIELDNAMES = [
    'Restaurant Name', 'Restaurant Description', 'Address', 'Phone', 'Website',
    'Google Maps Link', 'Cleaned Address', 'City', 'State', 'Zip', 'Embedded Links', 
    'Venue ID','Star Rating', 'Number of Reviews', 'Restaurant Category', 'Price Range',
    'Latitude', 'Longitude', 'Accessibility', 'Service options', 'Highlights',
    'Popular for', 'Offerings', 'Dining options', 'Amenities', 'Atmosphere',
    'Planning', 'Payments', 'Parking', 'Doesnt Offer'
]

PARALLEL_PROCESSING_CONFIG = {
    'num_workers': 4,
    'timeout_seconds': 1800,
    'chunk_size': 100
}

