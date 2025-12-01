"""
Web scraper for Nextleap course pages
Extracts: cohorts, batches, curriculum, mentors, instructors, placements, reviews
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
import re
import json
from datetime import datetime
import time


class NextleapScraper:
    """Scraper for Nextleap course pages"""
    
    def __init__(self, base_url: str = "https://nextleap.app"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.valid_urls = set()
        
    def validate_url(self, url: str) -> bool:
        """
        Validate if URL is a valid Nextleap URL
        """
        try:
            parsed = urlparse(url)
            # Check if URL belongs to nextleap.app domain
            if parsed.netloc not in ['nextleap.app', 'www.nextleap.app']:
                return False
            
            # Check if URL is accessible
            response = self.session.head(url, timeout=10, allow_redirects=True)
            if response.status_code == 200:
                self.valid_urls.add(url)
                return True
            return False
        except Exception as e:
            print(f"Error validating URL {url}: {e}")
            return False
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetch and parse a webpage
        """
        if not self.validate_url(url):
            print(f"Invalid URL: {url}")
            return None
            
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'lxml')
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_json_ld(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extract JSON-LD structured data from page
        """
        json_ld_data = []
        scripts = soup.find_all('script', type='application/ld+json')
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, list):
                    json_ld_data.extend(data)
                else:
                    json_ld_data.append(data)
            except (json.JSONDecodeError, AttributeError):
                continue
        
        return json_ld_data
    
    def extract_cohort_name(self, soup: BeautifulSoup, url: str, json_ld: List[Dict] = None) -> Dict:
        """
        Extract cohort/course name
        """
        data = {
            "cohort_name": None,
            "cohort_description": None,
            "source_url": url
        }
        
        # First try JSON-LD structured data
        if json_ld:
            for item in json_ld:
                if item.get('@type') == 'Course':
                    if 'name' in item:
                        data["cohort_name"] = item['name']
                    if 'description' in item:
                        data["cohort_description"] = item['description']
                    break
        
        # Fallback to HTML parsing
        if not data["cohort_name"]:
            # Try title tag
            title_tag = soup.find('title')
            if title_tag:
                title_text = title_tag.get_text(strip=True)
                # Clean up title (remove "NextLeap" and "with Placement Support" etc)
                title_text = re.sub(r'\s*NextLeap\s*', '', title_text, flags=re.I)
                title_text = re.sub(r'\s*with Placement Support\s*', '', title_text, flags=re.I)
                title_text = title_text.strip()
                if title_text:
                    data["cohort_name"] = title_text
            
            # Try h1 or h2 in main content
            if not data["cohort_name"]:
                for tag in ['h1', 'h2']:
                    element = soup.find(tag)
                    if element:
                        text = element.get_text(strip=True)
                        if text and len(text) > 5 and 'NextLeap' not in text:
                            data["cohort_name"] = text
                            break
        
        # Extract description from HTML if not found in JSON-LD
        if not data["cohort_description"]:
            # Look for meta description
            meta_desc = soup.find('meta', property='og:description')
            if meta_desc and meta_desc.get('content'):
                data["cohort_description"] = meta_desc['content']
            else:
                # Look for first meaningful paragraph
                paragraphs = soup.find_all('p')
                for p in paragraphs[:5]:
                    text = p.get_text(strip=True)
                    if text and len(text) > 50 and 'NextLeap' in text:
                        data["cohort_description"] = text
                        break
        
        return data
    
    def extract_batch_info(self, soup: BeautifulSoup, url: str, json_ld: List[Dict] = None) -> Dict:
        """
        Extract batch information: start date, cost, course type (live/self-paced)
        """
        data = {
            "batch_start_date": None,
            "cost": None,
            "course_type": None,  # live, self-paced, etc.
            "source_url": url
        }
        
        # Extract cost from page text first (more accurate, may be updated dynamically)
        # Look for prices in visible text before checking JSON-LD
        page_text = soup.get_text()
        
        # Look for prices in context of course fee, cost, price keywords
        # Prioritize patterns that are more specific to course pricing
        price_context_patterns = [
            # Most specific: course fee, enrollment fee, etc.
            r'(?:course fee|enrollment fee|program fee|course cost|course price)[:\s]*[₹Rs\.\s]*(\d{1,3}(?:,\d{3})*)',
            # Specific cost/price mentions
            r'(?:cost|price|fee)[:\s]*[₹Rs\.\s]*(\d{1,3}(?:,\d{3})*)',
            # Price before keywords
            r'[₹Rs\.\s]*(\d{1,3}(?:,\d{3})*)\s*(?:course fee|enrollment fee|program fee|cost|price|fee)',
        ]
        
        # Collect all potential prices with their context
        candidate_prices = []
        
        for pattern in price_context_patterns:
            matches = re.finditer(pattern, page_text, re.IGNORECASE)
            for match in matches:
                price_str = match.group(1).replace(',', '')
                try:
                    price = float(price_str)
                    if 20000 <= price <= 60000:  # Reasonable range for course fees
                        # Get context around the match
                        start = max(0, match.start() - 50)
                        end = min(len(page_text), match.end() + 50)
                        context = page_text[start:end].lower()
                        
                        # Score based on context relevance
                        score = 0
                        if 'course' in context or 'program' in context or 'enrollment' in context:
                            score += 3
                        if 'fee' in context or 'cost' in context or 'price' in context:
                            score += 2
                        # Penalize if it's clearly about something else
                        if any(word in context for word in ['discount', 'offer', 'save', 'was', 'original']):
                            score -= 2
                        
                        candidate_prices.append({
                            'price': price,
                            'formatted': f"{int(price):,}",
                            'score': score,
                            'context': context
                        })
                except ValueError:
                    continue
        
        # Sort by score (highest first) and take the best match
        if candidate_prices:
            candidate_prices.sort(key=lambda x: x['score'], reverse=True)
            data["cost"] = candidate_prices[0]['formatted']
            print(f"  Extracted cost: ₹{data['cost']} (score: {candidate_prices[0]['score']})")
        
        # Extract from JSON-LD if not found in text (fallback, but JSON-LD may be outdated)
        if not data["cost"] and json_ld:
            for item in json_ld:
                # Extract cost from offers
                if item.get('@type') in ['Course', 'Product']:
                    offers = item.get('offers', {})
                    if isinstance(offers, dict) and 'price' in offers:
                        price = str(offers['price'])
                        # Format price with commas if needed
                        try:
                            price_int = int(price)
                            data["cost"] = f"{price_int:,}"
                        except ValueError:
                            data["cost"] = price
                
                # Extract course type from course instance
                if item.get('@type') == 'Course':
                    course_instance = item.get('hasCourseInstance', {})
                    if isinstance(course_instance, dict):
                        course_mode = course_instance.get('courseMode', '').lower()
                        if 'online' in course_mode or 'live' in course_mode:
                            data["course_type"] = "live"
        
        # Extract start date - look for patterns like "Jan 3", "January 3", "Jan 3, 2026"
        # Also look for "starts from", "next batch starts"
        date_patterns = [
            r'(?:starts?|batch starts?|next batch|begins?|commences?)\s+(?:from|on)?\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}(?:,\s+\d{4})?',
            r'(?:starts?|batch starts?|next batch|begins?|commences?)\s+(?:from|on)?\s*(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:,\s+\d{4})?',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}(?:,\s+\d{4})?(?:\s+(?:starts?|batch))',
        ]
        
        for pattern in date_patterns:
            matches = re.finditer(pattern, page_text, re.IGNORECASE)
            for match in matches:
                date_str = match.group(0)
                # Clean up the date string
                date_str = re.sub(r'(?:starts?|batch starts?|next batch|begins?|commences?|from|on)\s*', '', date_str, flags=re.I)
                date_str = date_str.strip()
                if date_str:
                    data["batch_start_date"] = date_str
                    break
            if data["batch_start_date"]:
                break
        
        # Extract cost from HTML if not found yet (fallback to general price search)
        if not data["cost"]:
            cost_patterns = [
                r'[₹Rs\.\s]*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'(\d{1,3}(?:,\d{3})*)\s*(?:INR|Rs|₹)'
            ]
            
            for pattern in cost_patterns:
                matches = re.findall(pattern, page_text)
                if matches:
                    # Filter reasonable price ranges (typically 20k-60k for courses)
                    for match in matches:
                        if isinstance(match, tuple):
                            price_str = match[0].replace(',', '')
                        else:
                            price_str = match.replace(',', '')
                        
                        try:
                            price = float(price_str)
                            if 20000 <= price <= 60000:  # Reasonable range
                                data["cost"] = f"{int(price):,}"
                                break
                        except ValueError:
                            continue
                    if data["cost"]:
                        break
        
        # Extract course type from HTML if not found
        if not data["course_type"]:
            course_type_keywords = {
                'live': ['live', 'live course', 'live classes', 'live sessions', 'live online'],
                'self-paced': ['self-paced', 'self paced', 'learn at your own pace'],
                'recorded': ['recorded', 'recorded sessions', 'pre-recorded']
            }
            
            page_lower = page_text.lower()
            for course_type, keywords in course_type_keywords.items():
                if any(keyword in page_lower for keyword in keywords):
                    data["course_type"] = course_type
                    break
        
        return data
    
    def extract_payment_options(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        Extract payment options including EMI plans
        
        Args:
            soup: BeautifulSoup object
            url: Source URL
            
        Returns:
            Dictionary with payment/EMI information
        """
        data = {
            "emi_options": [],
            "payment_options": [],
            "source_url": url
        }
        
        page_text = soup.get_text()
        
        # Extract EMI information - multiple patterns
        emi_patterns = [
            r'EMI\s+(?:of|starting\s+from|from)?\s*[₹Rs\.\s]*(\d{1,3}(?:,\d{3})*)\s*(?:per\s+month|/month|monthly)',
            r'[₹Rs\.\s]*(\d{1,3}(?:,\d{3})*)\s*(?:per\s+month|/month|monthly)\s*EMI',
            r'EMI\s+[₹Rs\.\s]*(\d{1,3}(?:,\d{3})*)\s*(?:for|over)\s*(\d+)\s*(?:months?|installments?)',
            r'(\d+)\s*(?:months?|installments?)\s*EMI\s+[₹Rs\.\s]*(\d{1,3}(?:,\d{3})*)',
            r'EMI\s+[₹Rs\.\s]*(\d{1,3}(?:,\d{3})*)\s*(?:×|x)\s*(\d+)',
        ]
        
        for pattern in emi_patterns:
            matches = re.finditer(pattern, page_text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                if len(groups) == 1:
                    # Simple EMI amount
                    amount = groups[0].replace(',', '')
                    try:
                        amount_int = int(float(amount))
                        emi_text = f"₹{amount_int:,}/month"
                        if emi_text not in data["emi_options"]:
                            data["emi_options"].append(emi_text)
                    except ValueError:
                        continue
                elif len(groups) == 2:
                    # EMI with duration
                    # Determine which is amount and which is duration
                    if groups[0].isdigit() and len(groups[0]) <= 2:
                        # First is duration
                        duration = groups[0]
                        amount = groups[1].replace(',', '')
                    else:
                        # First is amount
                        amount = groups[0].replace(',', '')
                        duration = groups[1]
                    
                    try:
                        amount_int = int(float(amount))
                        duration_int = int(duration)
                        emi_text = f"₹{amount_int:,}/month for {duration_int} months"
                        if emi_text not in data["emi_options"]:
                            data["emi_options"].append(emi_text)
                    except ValueError:
                        continue
        
        # Also look for EMI in structured data (JSON-LD, data attributes, etc.)
        # Check for EMI in any data attributes or structured content
        emi_elements = soup.find_all(string=re.compile(r'EMI', re.I))
        for elem in emi_elements:
            if elem.parent:
                parent_text = elem.parent.get_text()
                # Extract EMI amount from parent context
                emi_match = re.search(r'[₹Rs\.\s]*(\d{1,3}(?:,\d{3})*)\s*(?:per\s+month|/month|monthly)', parent_text, re.I)
                if emi_match:
                    amount = emi_match.group(1).replace(',', '')
                    try:
                        amount_int = int(float(amount))
                        emi_text = f"₹{amount_int:,}/month"
                        if emi_text not in data["emi_options"]:
                            data["emi_options"].append(emi_text)
                    except ValueError:
                        continue
        
        return data
    
    def extract_curriculum(self, soup: BeautifulSoup, url: str, json_ld: List[Dict] = None) -> Dict:
        """
        Extract curriculum information
        """
        data = {
            "curriculum": [],
            "curriculum_text": None,
            "source_url": url
        }
        
        # Extract from JSON-LD first (most reliable)
        if json_ld:
            for item in json_ld:
                if item.get('@type') == 'Course':
                    syllabus = item.get('syllabusSections', [])
                    if syllabus:
                        curriculum_items = []
                        for section in syllabus:
                            if isinstance(section, dict):
                                name = section.get('name', '')
                                desc = section.get('description', '')
                                if name:
                                    if desc:
                                        curriculum_items.append(f"{name}: {desc}")
                                    else:
                                        curriculum_items.append(name)
                        if curriculum_items:
                            data["curriculum"] = curriculum_items
                            data["curriculum_text"] = '\n'.join(curriculum_items)
        
        # Fallback to HTML parsing if JSON-LD didn't provide curriculum
        if not data["curriculum"]:
            # Look for curriculum sections
            curriculum_keywords = ['curriculum', 'syllabus', 'course content', 'what you will learn', 'modules']
            
            # Find sections that might contain curriculum
            for keyword in curriculum_keywords:
                # Look for headings containing these keywords
                headings = soup.find_all(['h1', 'h2', 'h3', 'h4'], string=re.compile(keyword, re.I))
                
                for heading in headings:
                    # Get content after this heading
                    curriculum_section = []
                    current = heading.next_sibling
                    
                    while current:
                        if hasattr(current, 'name'):
                            if current.name in ['h1', 'h2', 'h3', 'h4']:
                                break
                            if current.name in ['ul', 'ol']:
                                items = current.find_all('li')
                                for item in items:
                                    text = item.get_text(strip=True)
                                    if text:
                                        curriculum_section.append(text)
                            elif current.name == 'p':
                                text = current.get_text(strip=True)
                                if text:
                                    curriculum_section.append(text)
                        elif isinstance(current, str) and current.strip():
                            curriculum_section.append(current.strip())
                        
                        current = current.next_sibling
                    
                    if curriculum_section:
                        data["curriculum"] = curriculum_section
                        data["curriculum_text"] = '\n'.join(curriculum_section)
                        break
                
                if data["curriculum"]:
                    break
            
            # If no structured curriculum found, look for lists
            if not data["curriculum"]:
                lists = soup.find_all(['ul', 'ol'])
                for list_elem in lists:
                    items = list_elem.find_all('li')
                    if len(items) >= 3:  # Likely a curriculum list
                        curriculum_items = [item.get_text(strip=True) for item in items if item.get_text(strip=True)]
                        if curriculum_items:
                            data["curriculum"] = curriculum_items
                            data["curriculum_text"] = '\n'.join(curriculum_items)
                            break
        
        return data
    
    def extract_mentors_instructors(self, soup: BeautifulSoup, url: str, json_ld: List[Dict] = None) -> Dict:
        """
        Extract mentors and instructors information
        """
        data = {
            "mentors": [],
            "instructors": [],
            "mentors_text": None,
            "source_url": url
        }
        
        # Extract from JSON-LD first
        if json_ld:
            for item in json_ld:
                if item.get('@type') == 'Course':
                    course_instance = item.get('hasCourseInstance', {})
                    if isinstance(course_instance, dict):
                        instructors = course_instance.get('instructor', [])
                        if isinstance(instructors, list):
                            for instructor in instructors:
                                if isinstance(instructor, dict) and 'name' in instructor:
                                    data["instructors"].append(instructor['name'])
                        elif isinstance(instructors, dict) and 'name' in instructors:
                            data["instructors"].append(instructors['name'])
        
        # Fallback to HTML parsing
        if not data["instructors"]:
            # Look for mentor/instructor sections
            keywords = ['mentor', 'instructor', 'teacher', 'faculty', 'expert']
            
            page_text = soup.get_text()
            mentor_sections = []
            
            for keyword in keywords:
                # Find headings with these keywords
                headings = soup.find_all(['h1', 'h2', 'h3', 'h4'], string=re.compile(keyword, re.I))
                
                for heading in headings:
                    section_text = []
                    current = heading.next_sibling
                    
                    while current:
                        if hasattr(current, 'name'):
                            if current.name in ['h1', 'h2', 'h3', 'h4']:
                                break
                            if current.name in ['p', 'div', 'span']:
                                text = current.get_text(strip=True)
                                if text:
                                    section_text.append(text)
                        current = current.next_sibling
                    
                    if section_text:
                        mentor_sections.extend(section_text)
            
            # Also look for names (capitalized words that might be names)
            if mentor_sections:
                data["mentors_text"] = ' '.join(mentor_sections)
                # Try to extract individual names (heuristic)
                sentences = ' '.join(mentor_sections).split('.')
                for sentence in sentences:
                    words = sentence.split()
                    # Look for patterns that might be names
                    if len(words) >= 2 and words[0][0].isupper():
                        potential_name = ' '.join(words[:2])
                        if len(potential_name) > 3:
                            data["mentors"].append(potential_name)
        
        # Combine mentors and instructors
        if data["instructors"]:
            data["mentors"] = list(set(data["mentors"] + data["instructors"]))
            data["mentors_text"] = ', '.join(data["instructors"])
        
        return data
    
    def extract_placements(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        Extract placement information
        """
        data = {
            "placement_info": None,
            "placement_text": None,
            "source_url": url
        }
        
        # Look for placement-related keywords
        keywords = ['placement', 'job', 'career', 'hiring', 'companies', 'recruitment']
        
        placement_sections = []
        
        for keyword in keywords:
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'], string=re.compile(keyword, re.I))
            
            for heading in headings:
                section_text = []
                current = heading.next_sibling
                
                while current:
                    if hasattr(current, 'name'):
                        if current.name in ['h1', 'h2', 'h3', 'h4']:
                            break
                        if current.name in ['p', 'div', 'ul', 'ol']:
                            text = current.get_text(strip=True)
                            if text and len(text) > 20:  # Meaningful content
                                section_text.append(text)
                    current = current.next_sibling
                
                if section_text:
                    placement_sections.extend(section_text)
        
        if placement_sections:
            data["placement_text"] = '\n'.join(placement_sections)
            data["placement_info"] = placement_sections
        
        return data
    
    def extract_reviews(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        Extract reviews/testimonials
        """
        data = {
            "reviews": [],
            "reviews_text": None,
            "source_url": url
        }
        
        # Look for review-related keywords
        keywords = ['review', 'testimonial', 'feedback', 'student', 'alumni']
        
        review_sections = []
        
        for keyword in keywords:
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4'], string=re.compile(keyword, re.I))
            
            for heading in headings:
                section_text = []
                current = heading.next_sibling
                
                while current:
                    if hasattr(current, 'name'):
                        if current.name in ['h1', 'h2', 'h3', 'h4']:
                            break
                        if current.name in ['p', 'div', 'blockquote']:
                            text = current.get_text(strip=True)
                            if text and len(text) > 30:  # Meaningful review
                                section_text.append(text)
                    current = current.next_sibling
                
                if section_text:
                    review_sections.extend(section_text)
        
        # Also look for blockquotes which often contain testimonials
        blockquotes = soup.find_all('blockquote')
        for quote in blockquotes:
            text = quote.get_text(strip=True)
            if text and len(text) > 30:
                review_sections.append(text)
        
        if review_sections:
            data["reviews"] = review_sections
            data["reviews_text"] = '\n'.join(review_sections)
        
        return data
    
    def scrape_course_page(self, url: str) -> Optional[Dict]:
        """
        Scrape all data from a course page
        """
        print(f"\nScraping: {url}")
        
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        # Extract JSON-LD structured data first
        json_ld = self.extract_json_ld(soup)
        
        # Extract all data (pass json_ld to methods that can use it)
        course_data = {
            "scraped_at": datetime.now().isoformat(),
            "source_url": url,
            "cohort": self.extract_cohort_name(soup, url, json_ld),
            "batch": self.extract_batch_info(soup, url, json_ld),
            "payment_options": self.extract_payment_options(soup, url),
            "curriculum": self.extract_curriculum(soup, url, json_ld),
            "mentors_instructors": self.extract_mentors_instructors(soup, url, json_ld),
            "placements": self.extract_placements(soup, url),
            "reviews": self.extract_reviews(soup, url)
        }
        
        return course_data
    
    def discover_course_urls(self) -> List[str]:
        """
        Discover all course URLs from the website
        """
        discovered_urls = []
        
        # Try to find course links from homepage or courses page
        possible_pages = [
            f"{self.base_url}/",
            f"{self.base_url}/courses",
            f"{self.base_url}/course"
        ]
        
        for page_url in possible_pages:
            soup = self.fetch_page(page_url)
            if soup:
                # Find all links that might be course pages
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link.get('href', '')
                    full_url = urljoin(self.base_url, href)
                    
                    # Check if it's a course URL
                    if '/course/' in full_url and self.validate_url(full_url):
                        if full_url not in discovered_urls:
                            discovered_urls.append(full_url)
        
        return discovered_urls
    
    def scrape_all_courses(self, course_urls: List[str]) -> List[Dict]:
        """
        Scrape all provided course URLs
        """
        all_data = []
        
        for url in course_urls:
            data = self.scrape_course_page(url)
            if data:
                all_data.append(data)
            time.sleep(1)  # Be respectful with requests
        
        return all_data

