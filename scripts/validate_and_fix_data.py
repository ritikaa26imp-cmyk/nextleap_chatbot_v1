"""
Script to validate and fix data inconsistencies
Ensures all data matches what's on the website
"""
import json
import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path
from typing import Dict, List

# Manual overrides for data that can't be scraped reliably
# These should be verified against the actual website
DATA_OVERRIDES = {
    "https://nextleap.app/course/data-analyst-course": {
        "cost": "32,999",
        "batch_start_date": "Jan 3"
    },
    "https://nextleap.app/course/product-management-course": {
        "cost": "49,999",
        "batch_start_date": "Jan 3"
    },
    "https://nextleap.app/course/ui-ux-design-course": {
        "cost": "49,999"
    },
    "https://nextleap.app/course/business-analyst-course": {
        "cost": "49,999"
    }
}


def scrape_price_from_website(url: str) -> str:
    """
    Scrape the actual price from the website
    Returns the price as string or None if not found
    """
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        soup = BeautifulSoup(response.text, 'lxml')
        page_text = soup.get_text()
        
        # Look for course-specific pricing patterns
        price_patterns = [
            r'(?:course fee|enrollment fee|program fee|course cost)[:\s]*[₹Rs\.\s]*(\d{1,3}(?:,\d{3})*)',
            r'[₹Rs\.\s]*(\d{1,3}(?:,\d{3})*)\s*(?:course fee|enrollment fee|program fee)',
        ]
        
        candidate_prices = []
        for pattern in price_patterns:
            matches = re.finditer(pattern, page_text, re.IGNORECASE)
            for match in matches:
                price_str = match.group(1).replace(',', '')
                try:
                    price = float(price_str)
                    if 20000 <= price <= 60000:
                        start = max(0, match.start() - 100)
                        end = min(len(page_text), match.end() + 100)
                        context = page_text[start:end].lower()
                        
                        # Score based on relevance
                        score = 0
                        if 'course' in context or 'program' in context:
                            score += 3
                        if 'fee' in context or 'cost' in context:
                            score += 2
                        if any(word in context for word in ['discount', 'was', 'original', 'save']):
                            score -= 2
                        
                        candidate_prices.append({
                            'price': price,
                            'formatted': f"{int(price):,}",
                            'score': score
                        })
                except ValueError:
                    continue
        
        if candidate_prices:
            candidate_prices.sort(key=lambda x: x['score'], reverse=True)
            return candidate_prices[0]['formatted']
        
        return None
    except Exception as e:
        print(f"  Error scraping {url}: {e}")
        return None


def validate_and_fix_data():
    """
    Validate all course data and fix inconsistencies
    """
    data_file = Path("data/processed/nextleap_courses.json")
    
    if not data_file.exists():
        print("Error: Processed data file not found!")
        return
    
    print("Loading course data...")
    with open(data_file, 'r') as f:
        courses = json.load(f)
    
    print(f"Found {len(courses)} courses")
    print("="*60)
    
    fixes_applied = []
    
    for course in courses:
        url = course.get("source_url", "")
        cohort_name = course.get("cohort", {}).get("cohort_name", "Unknown")
        
        print(f"\nValidating: {cohort_name}")
        print(f"  URL: {url}")
        
        batch = course.get("batch", {})
        current_cost = batch.get("cost")
        
        # Check if we have an override
        if url in DATA_OVERRIDES:
            override = DATA_OVERRIDES[url]
            expected_cost = override.get("cost")
            expected_date = override.get("batch_start_date")
            
            # Fix cost if different
            if expected_cost and current_cost != expected_cost:
                print(f"  ⚠️  Cost mismatch: Found {current_cost}, Expected {expected_cost}")
                batch["cost"] = expected_cost
                fixes_applied.append(f"{cohort_name}: Cost updated to {expected_cost}")
                print(f"  ✅ Cost fixed: {expected_cost}")
            
            # Fix date if different
            if expected_date:
                current_date = batch.get("batch_start_date")
                if current_date != expected_date:
                    print(f"  ⚠️  Date mismatch: Found {current_date}, Expected {expected_date}")
                    batch["batch_start_date"] = expected_date
                    fixes_applied.append(f"{cohort_name}: Date updated to {expected_date}")
                    print(f"  ✅ Date fixed: {expected_date}")
        else:
            # Try to scrape from website
            print(f"  Scraping price from website...")
            scraped_price = scrape_price_from_website(url)
            if scraped_price and scraped_price != current_cost:
                print(f"  ⚠️  Cost mismatch: Stored {current_cost}, Website shows {scraped_price}")
                batch["cost"] = scraped_price
                fixes_applied.append(f"{cohort_name}: Cost updated to {scraped_price}")
                print(f"  ✅ Cost fixed: {scraped_price}")
    
    # Save fixed data
    if fixes_applied:
        print("\n" + "="*60)
        print("Saving fixed data...")
        with open(data_file, 'w') as f:
            json.dump(courses, f, indent=2)
        
        print(f"\n✅ Applied {len(fixes_applied)} fixes:")
        for fix in fixes_applied:
            print(f"  - {fix}")
    else:
        print("\n✅ No fixes needed - all data is consistent!")
    
    print("\n" + "="*60)
    print("Data validation complete!")
    return fixes_applied


if __name__ == "__main__":
    validate_and_fix_data()


