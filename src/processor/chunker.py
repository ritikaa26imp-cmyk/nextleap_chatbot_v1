"""
Text chunker for Nextleap course data
Splits course data into searchable chunks with metadata
"""
from typing import List, Dict
import json


class CourseChunker:
    """Chunks course data for vector database storage"""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        """
        Initialize chunker
        
        Args:
            chunk_size: Target size for chunks (in characters)
            overlap: Overlap between chunks (in characters)
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_course_data(self, course_data: Dict) -> List[Dict]:
        """
        Chunk a single course's data into searchable pieces
        
        Args:
            course_data: Single course data dictionary
            
        Returns:
            List of chunks with metadata
        """
        chunks = []
        source_url = course_data.get("source_url", "")
        cohort_name = course_data.get("cohort", {}).get("cohort_name", "Unknown")
        
        # Chunk 1: Cohort Information
        cohort = course_data.get("cohort", {})
        cohort_text = f"Cohort: {cohort.get('cohort_name', '')}\n"
        cohort_text += f"Description: {cohort.get('cohort_description', '')}"
        
        if cohort_text.strip():
            chunks.append({
                "content": cohort_text.strip(),
                "metadata": {
                    "type": "cohort",
                    "cohort_name": cohort_name,
                    "source_url": source_url,
                    "field": "cohort_info"
                }
            })
        
        # Chunk 2: Batch Information
        batch = course_data.get("batch", {})
        batch_text = f"Batch Information for {cohort_name}:\n"
        if batch.get("batch_start_date"):
            batch_text += f"Start Date: {batch.get('batch_start_date')}\n"
        if batch.get("cost"):
            batch_text += f"Cost: {batch.get('cost')}\n"
        if batch.get("course_type"):
            batch_text += f"Course Type: {batch.get('course_type')}"
        
        if batch_text.strip() and len(batch_text.strip()) > len(f"Batch Information for {cohort_name}:\n"):
            chunks.append({
                "content": batch_text.strip(),
                "metadata": {
                    "type": "batch",
                    "cohort_name": cohort_name,
                    "source_url": source_url,
                    "field": "batch_info",
                    "cost": batch.get("cost"),
                    "batch_start_date": batch.get("batch_start_date"),
                    "course_type": batch.get("course_type")
                }
            })
        
        # Chunk for Payment Options (after batch chunk)
        payment_options = course_data.get("payment_options", {})
        if payment_options.get("emi_options"):
            payment_text = f"Payment Options for {cohort_name}:\n"
            payment_text += "EMI Options:\n"
            for emi in payment_options["emi_options"]:
                payment_text += f"- {emi}\n"
            
            if payment_text.strip():
                chunks.append({
                    "content": payment_text.strip(),
                    "metadata": {
                        "type": "payment",
                        "cohort_name": cohort_name,
                        "source_url": source_url,
                        "field": "payment_options",
                        "emi_options": payment_options.get("emi_options", [])
                    }
                })
        
        # Chunk 3: Curriculum (split into multiple chunks if needed)
        curriculum = course_data.get("curriculum", {})
        curriculum_items = curriculum.get("curriculum", [])
        
        if curriculum_items:
            # Create one chunk per curriculum item for better searchability
            for idx, item in enumerate(curriculum_items):
                chunks.append({
                    "content": f"Curriculum for {cohort_name}: {item}",
                    "metadata": {
                        "type": "curriculum",
                        "cohort_name": cohort_name,
                        "source_url": source_url,
                        "field": "curriculum",
                        "item_index": idx
                    }
                })
        
        # Chunk 4: Mentors/Instructors
        mentors = course_data.get("mentors_instructors", {})
        instructors_list = mentors.get("instructors", [])
        mentors_list = mentors.get("mentors", [])
        
        if instructors_list or mentors_list:
            mentors_text = f"Instructors and Mentors for {cohort_name}:\n"
            if instructors_list:
                mentors_text += f"Instructors: {', '.join(instructors_list)}\n"
            if mentors_list:
                mentors_text += f"Mentors: {', '.join(mentors_list)}"
            
            chunks.append({
                "content": mentors_text.strip(),
                "metadata": {
                    "type": "mentors_instructors",
                    "cohort_name": cohort_name,
                    "source_url": source_url,
                    "field": "mentors_instructors",
                    "instructors": instructors_list,
                    "mentors": mentors_list
                }
            })
        
        # Chunk 5: Placements
        placements = course_data.get("placements", {})
        placement_text = placements.get("placement_text")
        
        if placement_text:
            chunks.append({
                "content": f"Placement Information for {cohort_name}: {placement_text}",
                "metadata": {
                    "type": "placements",
                    "cohort_name": cohort_name,
                    "source_url": source_url,
                    "field": "placements"
                }
            })
        
        # Chunk 6: Reviews
        reviews = course_data.get("reviews", {})
        reviews_list = reviews.get("reviews", [])
        
        if reviews_list:
            reviews_text = "\n".join(reviews_list[:3])  # Limit to first 3 reviews
            chunks.append({
                "content": f"Reviews for {cohort_name}: {reviews_text}",
                "metadata": {
                    "type": "reviews",
                    "cohort_name": cohort_name,
                    "source_url": source_url,
                    "field": "reviews"
                }
            })
        
        return chunks
    
    def chunk_all_courses(self, courses_data: List[Dict]) -> List[Dict]:
        """
        Chunk all courses data
        
        Args:
            courses_data: List of course data dictionaries
            
        Returns:
            List of all chunks with metadata
        """
        all_chunks = []
        
        for course in courses_data:
            chunks = self.chunk_course_data(course)
            all_chunks.extend(chunks)
        
        return all_chunks

