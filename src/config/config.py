import os
from pathlib import Path
import logging

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Directory paths using Path for cross-platform compatibility
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# File paths
# File paths
RAW_RESTAURANTS_CSV = RAW_DATA_DIR / "raw_restaurants.csv"
CLEANED_RESTAURANTS_CSV = RAW_DATA_DIR / "cleaned_restaurants.csv"
ENHANCED_RESTAURANTS_CSV = PROCESSED_DATA_DIR / "cleaned_restaurants_enhanced.csv"

# Required fields (used for validation)
REQUIRED_RESTAURANT_FIELDS = [
    'Restaurant Name',
    'Address',
]

# Expected fields (for documentation purposes)
EXPECTED_RESTAURANT_FIELDS = [
    'Restaurant Name',
    'Restaurant Description',
    'Address',
    'Phone',
    'Website',
    'Google Maps Link',
    'Instagram Name',
    'Instagram URL'
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
    'From the business'  # Add this field
]

# Scraping configuration
EATER_CONFIG = {
    'base_url': "https://www.eater.com/maps/archives",
    'pages_to_scrape': 1,
    'user_agents': [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:46.0) Gecko/20100101 Firefox/46.0"
    ],
    'delay': {
        'page_load': (5, 10),  # (min, max) seconds
        'between_articles': (5, 10),
        'between_pages': (2, 5)
    }
}

# Selenium/Chrome configuration
CHROME_OPTIONS = [
    "--headless=new",  # Updated headless mode syntax
    "--disable-gpu",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-logging",
    "--log-level=3",
    "--disable-extensions",
    "--disable-notifications",
    "--disable-infobars",
    "--window-size=1920,1080",
    "--ignore-certificate-errors",
    "--disable-software-rasterizer",
    "--disable-web-security",
    "--allow-running-insecure-content",
    "--disable-features=MediaFoundationVideoCapture",
    "--disable-features=VizDisplayCompositor",
    "--disable-features=UseOzonePlatform",
    "--disable-features=Vulkan",
    "--disable-features=WebRTC",
    "--disable-features=AudioServiceOutOfProcess",
    "--disable-setuid-sandbox",
    "--disable-accelerated-video-decode",
    "--disable-accelerated-video-encode",
    "--disable-gpu-memory-buffer-video-frames",
    "--disable-gpu-compositing",
    "--disable-gpu-rasterization",
    "--disable-gpu-sandbox",
    "--disable-webgl",
    "--disable-webgl2",
    "--enable-unsafe-swiftshader",  # Add this to address the WebGL warning
    "--disable-features=MediaFoundationVideoCapture,VizDisplayCompositor,UseOzonePlatform,Vulkan,WebRTC,AudioServiceOutOfProcess",
    "--silent",
]

# Add timeout settings
TIMEOUT_CONFIG = {
    'page_load': 30,  # seconds
    'script': 30,
    'element_wait': 20
}

# Default values for missing data
DEFAULT_VALUES = {
    'name': "Name Not Found",
    'description': "Description Not Found",
    'address': "Address Not Found",
    'phone': "Phone Not Found",
    'website': "Website Not Found",
    'google_maps': "Google Maps Link Not Found",
    'instagram_name': "Instagram Name Not Found",
    'instagram_url': "Instagram URL Not Found"
}

# Rate limiting settings
RATE_LIMITS = {
    'min_delay': 2,
    'max_delay': 10,
    'error_delay': 30  # Delay after encountering an error
}

# Error handling settings
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# State name to abbreviation mapping
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

# Add these configurations
WEBDRIVER_CONFIG = {
    'driver_path': None,  # Will use the system PATH
    'implicit_wait': 10,
    'page_load_timeout': 30,
    'options': CHROME_OPTIONS
}

# Also add this logging configuration
logging.getLogger('selenium').setLevel(logging.ERROR)
