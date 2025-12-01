"""
List of Nextleap course pages to scrape
"""
from typing import List

# Base URL
BASE_URL = "https://nextleap.app"

# Known course URLs - we'll discover more dynamically
# Note: product-designer-course is not a valid course page (redirects to generic page)
KNOWN_COURSES = [
    "/course/data-analyst-course",
    "/course/product-management-course",
    # product-designer-course removed - invalid URL with no course content
    # Add more as discovered
]

def get_all_course_urls() -> List[str]:
    """
    Returns list of all course URLs to scrape.
    This will be expanded to discover courses dynamically.
    """
    return [f"{BASE_URL}{path}" for path in KNOWN_COURSES]

