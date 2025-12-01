"""
Test script to inspect the actual HTML structure of Nextleap pages
"""
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scraper.scraper import NextleapScraper

def test_single_page():
    """Test scraping a single page to see structure"""
    scraper = NextleapScraper()
    
    test_url = "https://nextleap.app/course/data-analyst-course"
    print(f"Testing URL: {test_url}")
    
    soup = scraper.fetch_page(test_url)
    if soup:
        # Save HTML for inspection
        html_file = Path(__file__).parent.parent / "data" / "raw" / "test_page.html"
        html_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print(f"HTML saved to: {html_file}")
        
        # Try to extract data
        data = scraper.scrape_course_page(test_url)
        if data:
            # Save extracted data
            data_file = Path(__file__).parent.parent / "data" / "raw" / "test_extraction.json"
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Extracted data saved to: {data_file}")
            
            # Print summary
            print("\n" + "="*50)
            print("EXTRACTED DATA SUMMARY")
            print("="*50)
            print(f"Cohort Name: {data.get('cohort', {}).get('cohort_name', 'N/A')}")
            print(f"Batch Start: {data.get('batch', {}).get('batch_start_date', 'N/A')}")
            print(f"Cost: {data.get('batch', {}).get('cost', 'N/A')}")
            print(f"Course Type: {data.get('batch', {}).get('course_type', 'N/A')}")
            print(f"Curriculum Items: {len(data.get('curriculum', {}).get('curriculum', []))}")
        else:
            print("Failed to extract data")
    else:
        print("Failed to fetch page")

if __name__ == "__main__":
    test_single_page()

