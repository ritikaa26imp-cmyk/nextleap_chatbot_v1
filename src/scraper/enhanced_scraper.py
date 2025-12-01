"""
Enhanced scraper that combines static HTML and Selenium-based scraping
with data validation and consistency checks
"""
from typing import Dict, Optional
from src.scraper.scraper import NextleapScraper
from src.scraper.selenium_scraper import SeleniumScraper, SELENIUM_AVAILABLE
import json


class EnhancedScraper(NextleapScraper):
    """Enhanced scraper with JavaScript rendering and validation"""
    
    def __init__(self, base_url: str = "https://nextleap.app", use_selenium: bool = True):
        super().__init__(base_url)
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        
    def scrape_course_page_enhanced(self, url: str) -> Dict:
        """
        Scrape course page with enhanced JavaScript rendering
        
        Args:
            url: Course page URL
            
        Returns:
            Dictionary with scraped course data
        """
        # First, try static HTML scraping
        soup = self.fetch_page(url)
        if not soup:
            return {}
        
        json_ld = self.extract_json_ld(soup)
        
        # Extract data using base scraper
        course_data = {
            "source_url": url,
            "cohort": self.extract_cohort_name(soup, url, json_ld),
            "batch": self.extract_batch_info(soup, url, json_ld),
            "curriculum": self.extract_curriculum(soup, url, json_ld),
            "mentors_instructors": self.extract_mentors_instructors(soup, url, json_ld),
            "placements": self.extract_placements(soup, url, json_ld),
            "reviews": self.extract_reviews(soup, url, json_ld),
        }
        
        # If Selenium is available and we're missing critical data, try Selenium
        if self.use_selenium:
            missing_critical = (
                not course_data["batch"].get("batch_start_date") or
                not course_data["batch"].get("cost")
            )
            
            if missing_critical:
                print(f"Missing critical data for {url}, trying Selenium...")
                try:
                    with SeleniumScraper(headless=True) as selenium_scraper:
                        if selenium_scraper:
                            selenium_soup = selenium_scraper.scrape_page(url, wait_time=5)
                            if selenium_soup:
                                dynamic_data = selenium_scraper.extract_dynamic_content(selenium_soup)
                                
                                # Update batch info with dynamic data
                                if dynamic_data.get('batch_start_date') and not course_data["batch"].get("batch_start_date"):
                                    course_data["batch"]["batch_start_date"] = dynamic_data['batch_start_date']
                                    print(f"  ✓ Extracted start date: {dynamic_data['batch_start_date']}")
                                
                                if dynamic_data.get('cost') and not course_data["batch"].get("cost"):
                                    course_data["batch"]["cost"] = dynamic_data['cost']
                                    print(f"  ✓ Extracted cost: {dynamic_data['cost']}")
                except Exception as e:
                    print(f"  ⚠ Selenium scraping failed: {e}")
        
        return course_data
    
    def validate_and_fix_data(self, course_data: Dict) -> Dict:
        """
        Validate scraped data and fix inconsistencies
        
        Args:
            course_data: Scraped course data
            
        Returns:
            Validated and fixed course data
        """
        url = course_data.get("source_url", "")
        
        # Validate batch information
        batch = course_data.get("batch", {})
        
        # Check if batch_start_date is None but should exist
        if not batch.get("batch_start_date"):
            # Try to extract from other sources or mark for manual review
            print(f"  ⚠ Warning: No start date found for {url}")
        
        # Validate cost
        if not batch.get("cost"):
            print(f"  ⚠ Warning: No cost found for {url}")
        else:
            # Ensure cost is in correct format
            cost = batch["cost"]
            if isinstance(cost, str):
                # Remove currency symbols and ensure proper formatting
                cost_clean = cost.replace('₹', '').replace('Rs', '').replace(',', '').strip()
                try:
                    cost_int = int(float(cost_clean))
                    batch["cost"] = f"{cost_int:,}"
                except ValueError:
                    print(f"  ⚠ Warning: Invalid cost format: {cost}")
        
        return course_data


