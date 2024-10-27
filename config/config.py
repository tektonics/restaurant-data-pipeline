import os

# Base project directory
PROJECT_DIR = "S:/restaurant_data_project"

# Directory paths
DATA_DIR = os.path.join(PROJECT_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")

# File paths
RAW_RESTAURANTS_CSV = os.path.join(RAW_DATA_DIR, "raw_restaurants.csv")
CLEANED_RESTAURANTS_CSV = os.path.join(RAW_DATA_DIR, "cleaned_restaurants.csv")
ENHANCED_RESTAURANTS_CSV = os.path.join(PROCESSED_DATA_DIR, "cleaned_restaurants_enhanced.csv")

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
    'Parking'
]

# Scraping configuration
EATER_CONFIG = {
    'base_url': "https://www.eater.com/maps/archives",
    'pages_to_scrape': 75,
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
    "--headless",
    "--disable-gpu",
    "--no-sandbox",
    "--disable-dev-shm-usage"
]

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