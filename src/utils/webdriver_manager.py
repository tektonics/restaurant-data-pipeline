from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from ..config.config import CHROME_OPTIONS
import logging
import os
from pathlib import Path
import stat

logger = logging.getLogger(__name__)

class WebDriverManager:
    _driver_path = None
    _instances = []
    _active = True

    @classmethod
    def create_driver(cls):
        if not cls._active:
            raise RuntimeError("WebDriverManager is not active")
            
        try:
            options = webdriver.ChromeOptions()
            for option in CHROME_OPTIONS:
                options.add_argument(option)
            
            driver_path = ChromeDriverManager().install()
            
            if 'chromedriver-linux64' in driver_path:
                driver_path = str(Path(driver_path).parent / 'chromedriver')
            
            os.chmod(driver_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
            
            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=options)
            cls._instances.append(driver)
            return driver
            
        except Exception as e:
            logger.error(f"Failed to create WebDriver: {str(e)}")
            raise

    @classmethod
    def cleanup(cls):
        cls._active = False
        for driver in cls._instances[:]:  # Create a copy of the list to iterate
            try:
                driver.quit()
                cls._instances.remove(driver)
            except Exception as e:
                logger.warning(f"Error while cleaning up driver: {e}")
        logger.info(f"WebDriver cleanup completed. Cleaned up {len(cls._instances)} instances")

