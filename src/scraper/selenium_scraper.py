"""
Selenium-based scraper for JavaScript-rendered content
Falls back to requests-based scraper if Selenium is not available
"""
from typing import Dict, Optional
import re
import time
from bs4 import BeautifulSoup

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


class SeleniumScraper:
    """Selenium-based scraper for JavaScript-rendered content"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        
    def __enter__(self):
        if SELENIUM_AVAILABLE:
            try:
                chrome_options = Options()
                if self.headless:
                    chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--window-size=1920,1080')
                chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
                
                self.driver = webdriver.Chrome(options=chrome_options)
                return self
            except Exception as e:
                print(f"Warning: Could not initialize Selenium: {e}")
                print("Falling back to static HTML scraping")
                return None
        return None
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
    
    def scrape_page(self, url: str, wait_time: int = 5) -> Optional[BeautifulSoup]:
        """
        Scrape a page with JavaScript rendering
        
        Args:
            url: URL to scrape
            wait_time: Time to wait for page to load (seconds)
            
        Returns:
            BeautifulSoup object or None if failed
        """
        if not self.driver:
            return None
            
        try:
            self.driver.get(url)
            # Wait for page to load
            time.sleep(wait_time)
            
            # Try to wait for specific elements that indicate page is loaded
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except TimeoutException:
                pass
            
            # Get page source after JavaScript execution
            page_source = self.driver.page_source
            return BeautifulSoup(page_source, 'lxml')
            
        except Exception as e:
            print(f"Error scraping {url} with Selenium: {e}")
            return None
    
    def extract_dynamic_content(self, soup: BeautifulSoup) -> Dict:
        """
        Extract content that's typically loaded via JavaScript
        
        Returns:
            Dictionary with extracted dynamic content
        """
        if not soup:
            return {}
        
        data = {}
        page_text = soup.get_text()
        
        # Extract dates - more comprehensive patterns
        date_patterns = [
            r'(?:starts?|batch starts?|next batch|begins?|commences?|starting)\s+(?:on|from)?\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:,\s+\d{4})?',
            r'(?:starts?|batch starts?|next batch|begins?|commences?|starting)\s+(?:on|from)?\s*(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:,\s+\d{4})?',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:,\s+\d{4})?(?:\s+(?:starts?|batch|starting))',
            r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:,\s+\d{4})?(?:\s+(?:starts?|batch|starting))',
        ]
        
        for pattern in date_patterns:
            matches = re.finditer(pattern, page_text, re.IGNORECASE)
            for match in matches:
                date_str = match.group(0)
                # Clean up the date string
                date_str = re.sub(r'(?:starts?|batch starts?|next batch|begins?|commences?|from|on|starting)\s*', '', date_str, flags=re.I)
                date_str = date_str.strip()
                # Extract just the date part (e.g., "Jan 3")
                date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}', date_str, re.I)
                if date_match:
                    data['batch_start_date'] = date_match.group(0)
                    break
            if data.get('batch_start_date'):
                break
        
        # Extract prices from visible text (more accurate than JSON-LD)
        price_context_patterns = [
            r'(?:course fee|cost|price|fee|enrollment)[:\s]*[₹Rs\.\s]*(\d{1,3}(?:,\d{3})*)',
            r'[₹Rs\.\s]*(\d{1,3}(?:,\d{3})*)\s*(?:course fee|cost|price|fee|enrollment)',
        ]
        
        for pattern in price_context_patterns:
            matches = re.finditer(pattern, page_text, re.IGNORECASE)
            for match in matches:
                price_str = match.group(1).replace(',', '')
                try:
                    price = float(price_str)
                    if 20000 <= price <= 60000:  # Reasonable range
                        data['cost'] = f"{int(price):,}"
                        break
                except ValueError:
                    continue
            if data.get('cost'):
                break
        
        return data

