"""
Script to scrape data from Nextleap course pages
"""
import sys
import os
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scraper.scraper import NextleapScraper
from src.scraper.pages import get_all_course_urls
from src.processor.validator import DataValidator


def main():
    """Main scraping function"""
    
    # Initialize scraper
    scraper = NextleapScraper()
    validator = DataValidator()
    
    # Get course URLs
    print("Discovering course URLs...")
    discovered_urls = scraper.discover_course_urls()
    
    # Add known URLs
    known_urls = get_all_course_urls()
    all_urls = list(set(discovered_urls + known_urls))
    
    print(f"Found {len(all_urls)} course URLs:")
    for url in all_urls:
        print(f"  - {url}")
    
    if not all_urls:
        print("No course URLs found. Using known URLs only.")
        all_urls = known_urls
    
    # Scrape all courses
    print(f"\nScraping {len(all_urls)} course pages...")
    courses_data = scraper.scrape_all_courses(all_urls)
    
    # Validate data
    print("\nValidating scraped data...")
    validated_courses = validator.validate_all_courses(courses_data)
    
    print(f"\nSuccessfully scraped and validated {len(validated_courses)} courses")
    
    # Save raw data
    raw_dir = Path(__file__).parent.parent / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    raw_file = raw_dir / f"raw_data_{Path(__file__).stem}.json"
    with open(raw_file, 'w', encoding='utf-8') as f:
        json.dump(courses_data, f, indent=2, ensure_ascii=False)
    print(f"Raw data saved to: {raw_file}")
    
    # Save validated data
    processed_dir = Path(__file__).parent.parent / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    processed_file = processed_dir / "nextleap_courses.json"
    with open(processed_file, 'w', encoding='utf-8') as f:
        json.dump(validated_courses, f, indent=2, ensure_ascii=False)
    print(f"Validated data saved to: {processed_file}")
    
    # Print summary
    print("\n" + "="*50)
    print("SCRAPING SUMMARY")
    print("="*50)
    for course in validated_courses:
        cohort_name = course.get("cohort", {}).get("cohort_name", "Unknown")
        source_url = course.get("source_url", "N/A")
        batch_date = course.get("batch", {}).get("batch_start_date", "N/A")
        cost = course.get("batch", {}).get("cost", "N/A")
        
        print(f"\nCohort: {cohort_name}")
        print(f"  URL: {source_url}")
        print(f"  Batch Start: {batch_date}")
        print(f"  Cost: {cost}")
    
    # Validate all URLs are valid
    print("\n" + "="*50)
    print("URL VALIDATION CHECK")
    print("="*50)
    all_urls_valid = True
    for course in validated_courses:
        url = course.get("source_url")
        if not validator.validate_url(url):
            print(f"❌ Invalid URL: {url}")
            all_urls_valid = False
        else:
            print(f"✅ Valid URL: {url}")
    
    if all_urls_valid:
        print("\n✅ All URLs are valid!")
    else:
        print("\n❌ Some URLs are invalid!")
    
    return validated_courses


if __name__ == "__main__":
    main()

