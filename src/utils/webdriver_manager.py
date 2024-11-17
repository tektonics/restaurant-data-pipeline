from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import logging
from ..config.config import CHROME_OPTIONS, WEBDRIVER_CONFIG

logger = logging.getLogger(__name__)

def create_driver(custom_options=None):
    """Create and configure a Chrome WebDriver instance"""
    driver = None
    try:
        chrome_options = Options()
        
        # Add default options
        for option in CHROME_OPTIONS:
            chrome_options.add_argument(option)
            
        # Add any custom options
        if custom_options:
            for option in custom_options:
                chrome_options.add_argument(option)
                
        try:
            # First try system ChromeDriver
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            logger.warning(f"System ChromeDriver failed, trying ChromeDriverManager: {e}")
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                logger.error(f"All ChromeDriver attempts failed: {e}")
                raise
                
        # Configure timeouts
        driver.implicitly_wait(WEBDRIVER_CONFIG['implicit_wait'])
        driver.set_page_load_timeout(WEBDRIVER_CONFIG['page_load_timeout'])
        
        return driver
        
    except Exception as e:
        if driver:
            try:
                driver.quit()
            except:
                pass
        raise
