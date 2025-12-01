"""
Data validator for scraped Nextleap data
Ensures data quality and URL validation
"""
from typing import Dict, List, Optional
from urllib.parse import urlparse
import re


class DataValidator:
    """Validates scraped data"""
    
    def __init__(self):
        self.valid_domains = ['nextleap.app', 'www.nextleap.app']
    
    def validate_url(self, url: str) -> bool:
        """
        Validate that URL is a valid Nextleap URL
        """
        if not url or not isinstance(url, str):
            return False
        
        try:
            parsed = urlparse(url)
            
            # Check domain
            if parsed.netloc not in self.valid_domains:
                return False
            
            # Check scheme
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Check if URL is not empty
            if not parsed.path or parsed.path == '/':
                return False
            
            return True
        except Exception:
            return False
    
    def validate_course_data(self, data: Dict) -> Dict:
        """
        Validate and clean course data
        Returns validated data with validation status
        """
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "data": data.copy()
        }
        
        # Validate source URL
        source_url = data.get("source_url")
        if not source_url or not self.validate_url(source_url):
            validation_result["is_valid"] = False
            validation_result["errors"].append("Invalid or missing source_url")
            return validation_result
        else:
            validation_result["data"]["source_url"] = source_url
        
        # Validate cohort data - must have a valid course name
        cohort = data.get("cohort", {})
        cohort_name = cohort.get("cohort_name", "").strip()
        
        # Check for invalid course names (generic taglines, etc.)
        invalid_patterns = [
            "learning is now",
            "invite-only",
            "nextleap is",
            "accelerate your career",
            "^[-\\s]+$"  # Only dashes or spaces
        ]
        
        is_invalid_name = False
        if not cohort_name:
            validation_result["is_valid"] = False
            validation_result["errors"].append("Missing cohort name")
            is_invalid_name = True
        else:
            cohort_lower = cohort_name.lower()
            for pattern in invalid_patterns:
                if re.search(pattern, cohort_lower, re.IGNORECASE):
                    validation_result["is_valid"] = False
                    validation_result["errors"].append(f"Invalid cohort name: '{cohort_name}' (appears to be a generic tagline)")
                    is_invalid_name = True
                    break
        
        # Validate curriculum - must have curriculum content
        curriculum = data.get("curriculum", {})
        curriculum_items = curriculum.get("curriculum", [])
        if not curriculum_items or len(curriculum_items) == 0:
            validation_result["is_valid"] = False
            validation_result["errors"].append("Missing curriculum content")
        
        # Validate instructors/mentors - should have at least one
        mentors_data = data.get("mentors_instructors", {})
        instructors = mentors_data.get("instructors", [])
        mentors = mentors_data.get("mentors", [])
        if (not instructors or len(instructors) == 0) and (not mentors or len(mentors) == 0):
            validation_result["warnings"].append("Missing instructors/mentors information")
        
        # If course name is invalid or no curriculum, mark as invalid
        if is_invalid_name or not curriculum_items or len(curriculum_items) == 0:
            validation_result["is_valid"] = False
        
        # Validate batch data
        batch = data.get("batch", {})
        if not batch.get("batch_start_date"):
            validation_result["warnings"].append("Missing batch start date")
        if not batch.get("cost"):
            validation_result["warnings"].append("Missing cost information")
        
        # Ensure all nested dicts have source_url
        for key in ["cohort", "batch", "curriculum", "mentors_instructors", "placements", "reviews"]:
            if key in validation_result["data"]:
                if isinstance(validation_result["data"][key], dict):
                    validation_result["data"][key]["source_url"] = source_url
        
        return validation_result
    
    def clean_text(self, text: Optional[str]) -> Optional[str]:
        """
        Clean and normalize text content
        """
        if not text:
            return None
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Remove empty strings
        if not text:
            return None
        
        return text
    
    def validate_all_courses(self, courses_data: List[Dict]) -> List[Dict]:
        """
        Validate all course data
        Returns only valid courses with source URLs
        """
        validated_courses = []
        
        for course_data in courses_data:
            validation = self.validate_course_data(course_data)
            
            if validation["is_valid"]:
                # Clean text fields
                self._clean_course_data(validation["data"])
                validated_courses.append(validation["data"])
            else:
                print(f"Skipping invalid course data: {validation['errors']}")
        
        return validated_courses
    
    def _clean_course_data(self, data: Dict):
        """
        Clean all text fields in course data
        """
        # Clean cohort
        if "cohort" in data:
            cohort = data["cohort"]
            cohort["cohort_name"] = self.clean_text(cohort.get("cohort_name"))
            cohort["cohort_description"] = self.clean_text(cohort.get("cohort_description"))
        
        # Clean batch
        if "batch" in data:
            batch = data["batch"]
            batch["batch_start_date"] = self.clean_text(batch.get("batch_start_date"))
            batch["cost"] = self.clean_text(batch.get("cost"))
            batch["course_type"] = self.clean_text(batch.get("course_type"))
        
        # Clean curriculum
        if "curriculum" in data:
            curriculum = data["curriculum"]
            if isinstance(curriculum.get("curriculum"), list):
                curriculum["curriculum"] = [
                    self.clean_text(item) for item in curriculum["curriculum"]
                    if self.clean_text(item)
                ]
            curriculum["curriculum_text"] = self.clean_text(curriculum.get("curriculum_text"))
        
        # Clean mentors
        if "mentors_instructors" in data:
            mentors = data["mentors_instructors"]
            if isinstance(mentors.get("mentors"), list):
                mentors["mentors"] = [
                    self.clean_text(item) for item in mentors["mentors"]
                    if self.clean_text(item)
                ]
            mentors["mentors_text"] = self.clean_text(mentors.get("mentors_text"))
        
        # Clean placements
        if "placements" in data:
            placements = data["placements"]
            placements["placement_text"] = self.clean_text(placements.get("placement_text"))
        
        # Clean reviews
        if "reviews" in data:
            reviews = data["reviews"]
            if isinstance(reviews.get("reviews"), list):
                reviews["reviews"] = [
                    self.clean_text(item) for item in reviews["reviews"]
                    if self.clean_text(item)
                ]
            reviews["reviews_text"] = self.clean_text(reviews.get("reviews_text"))

