"""
Enhanced data scraping script with validation and consistency checks
"""
import sys
from pathlib import Path
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scraper.pages import get_all_course_urls
from src.scraper.enhanced_scraper import EnhancedScraper
from src.processor.data_validator import DataValidator


def main():
    """Main scraping function with enhanced validation"""
    print("="*70)
    print("ENHANCED DATA SCRAPING WITH VALIDATION")
    print("="*70)
    print()
    
    # Initialize scraper
    scraper = EnhancedScraper(use_selenium=True)
    
    # Get all course URLs
    urls = get_all_course_urls()
    print(f"Found {len(urls)} course URLs to scrape")
    print()
    
    # Scrape all courses
    all_courses = []
    for url in urls:
        print(f"Scraping: {url}")
        course_data = scraper.scrape_course_page_enhanced(url)
        
        if course_data:
            # Validate and fix data
            course_data = scraper.validate_and_fix_data(course_data)
            
            # Add timestamp
            course_data["scraped_at"] = datetime.now().isoformat()
            
            all_courses.append(course_data)
            
            # Print summary
            cohort_name = course_data.get("cohort", {}).get("cohort_name", "Unknown")
            batch_date = course_data.get("batch", {}).get("batch_start_date", "None")
            cost = course_data.get("batch", {}).get("cost", "None")
            print(f"  ✓ {cohort_name}")
            print(f"    Start Date: {batch_date}")
            print(f"    Cost: ₹{cost}")
        else:
            print(f"  ❌ Failed to scrape {url}")
        print()
    
    # Save raw data
    raw_data_path = Path(__file__).parent.parent / "data" / "raw" / "raw_data_enhanced.json"
    raw_data_path.parent.mkdir(parents=True, exist_ok=True)
    with open(raw_data_path, 'w', encoding='utf-8') as f:
        json.dump(all_courses, f, indent=2, ensure_ascii=False)
    print(f"Saved raw data to: {raw_data_path}")
    
    # Process and validate all courses
    validator = DataValidator()
    validation_results = validator.validate_all_courses(all_courses)
    consistency_issues = validator.check_data_consistency(all_courses)
    
    print()
    print("="*70)
    print("VALIDATION RESULTS")
    print("="*70)
    print(f"Total courses: {validation_results['total_courses']}")
    print(f"Valid courses: {validation_results['valid_courses']}")
    print(f"Invalid courses: {validation_results['invalid_courses']}")
    if validation_results['issues']:
        print(f"\nIssues found:")
        for issue in validation_results['issues']:
            print(f"  - {issue}")
    if consistency_issues:
        print(f"\nConsistency issues:")
        for issue in consistency_issues:
            print(f"  - {issue}")
    print("="*70)
    
    # Save processed data
    processed_data_path = Path(__file__).parent.parent / "data" / "processed" / "nextleap_courses.json"
    processed_data_path.parent.mkdir(parents=True, exist_ok=True)
    with open(processed_data_path, 'w', encoding='utf-8') as f:
        json.dump(all_courses, f, indent=2, ensure_ascii=False)
    print(f"\nSaved processed data to: {processed_data_path}")
    print("\n✅ Enhanced scraping complete!")


if __name__ == "__main__":
    main()

