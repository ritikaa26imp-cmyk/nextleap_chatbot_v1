"""
Data validator to ensure consistency between scraped data and website
"""
from typing import Dict, List
import json
from datetime import datetime


class DataValidator:
    """Validate and ensure data consistency"""
    
    def __init__(self):
        self.validation_errors = []
        self.validation_warnings = []
    
    def validate_course_data(self, course_data: Dict) -> tuple[bool, List[str]]:
        """
        Validate a single course data entry
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        url = course_data.get("source_url", "unknown")
        
        # Check required fields
        if not course_data.get("cohort", {}).get("cohort_name"):
            issues.append(f"Missing cohort name for {url}")
        
        # Validate batch information
        batch = course_data.get("batch", {})
        if not batch.get("cost"):
            issues.append(f"Missing cost for {url}")
        if not batch.get("course_type"):
            issues.append(f"Missing course type for {url}")
        
        # Check for null values that should have data
        if batch.get("batch_start_date") is None:
            issues.append(f"Warning: No start date for {url} (may be dynamically loaded)")
        
        # Validate curriculum
        curriculum = course_data.get("curriculum", {})
        if not curriculum.get("curriculum") or len(curriculum.get("curriculum", [])) == 0:
            issues.append(f"Missing curriculum for {url}")
        
        return len(issues) == 0, issues
    
    def validate_all_courses(self, courses: List[Dict]) -> Dict:
        """
        Validate all courses and return validation report
        
        Returns:
            Dictionary with validation results
        """
        results = {
            "total_courses": len(courses),
            "valid_courses": 0,
            "invalid_courses": 0,
            "issues": []
        }
        
        for course in courses:
            is_valid, issues = self.validate_course_data(course)
            if is_valid:
                results["valid_courses"] += 1
            else:
                results["invalid_courses"] += 1
                results["issues"].extend(issues)
        
        return results
    
    def check_data_consistency(self, courses: List[Dict]) -> List[str]:
        """
        Check for consistency issues across all courses
        
        Returns:
            List of consistency issues
        """
        issues = []
        
        # Check for duplicate URLs
        urls = [c.get("source_url") for c in courses]
        if len(urls) != len(set(urls)):
            issues.append("Duplicate URLs found in course data")
        
        # Check for courses with same name but different data
        cohort_names = {}
        for course in courses:
            name = course.get("cohort", {}).get("cohort_name")
            url = course.get("source_url")
            if name in cohort_names:
                if cohort_names[name] != url:
                    issues.append(f"Duplicate cohort name '{name}' with different URLs")
            else:
                cohort_names[name] = url
        
        return issues


