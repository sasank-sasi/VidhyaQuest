from playwright.sync_api import sync_playwright
import json
import logging
import os
import time
from bs4 import BeautifulSoup

class PageScraper:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        os.makedirs("debug", exist_ok=True)
        
    def get_course_urls(self):
        with open('courses.json', 'r') as f:
            courses = json.load(f)
            return courses if courses else []
    
    def extract_details_from_page(self, page):
        content = page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract details
        title = soup.find('h1', class_='section__heading')
        description = soup.find('div', class_='fr-view').find('p')
        instructor = soup.find('h4', class_='section__subheading')
        
        stats = {}
        stats_items = soup.find_all('li', class_='text-icon__list-item')
        
        for item in stats_items:
            icon = item.find('i')
            value = item.find('h4')
            
            if icon and value:
                if 'fa-clock-o' in icon.get('class', []):
                    stats['duration'] = value.text.strip()
                elif 'fa-star' in icon.get('class', []):
                    stats['rating'] = value.text.strip()
                elif 'fa-signal' in icon.get('class', []):
                    stats['level'] = value.text.strip()
        
        return {
            'title': title.text.strip() if title else None,
            'description': description.text.strip() if description else None,
            'instructor': instructor.text.strip() if instructor else None,
            'stats': stats
        }

    def scrape_all_courses(self):
        courses = self.get_course_urls()
        all_course_details = []
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
            )
            page = context.new_page()
            
            for index, course in enumerate(courses):
                try:
                    self.logger.info(f"Processing course {index + 1} of {len(courses)}: {course['url']}")
                    page.goto(course['url'], wait_until='domcontentloaded', timeout=60000)
                    page.wait_for_load_state('networkidle', timeout=60000)
                    page.wait_for_selector('main.course', timeout=60000)
                    time.sleep(3)
                    
                    # Extract details directly from page
                    course_details = self.extract_details_from_page(page)
                    all_course_details.append(course_details)
                    
                except Exception as e:
                    self.logger.error(f"Error processing course: {str(e)}")
                    continue
            
            context.close()
            browser.close()
        
        # Save all course details
        with open("course_details.json", "w", encoding="utf-8") as f:
            json.dump(all_course_details, f, indent=2)
        self.logger.info(f"Saved details for {len(all_course_details)} courses")

def main():
    scraper = PageScraper()
    scraper.scrape_all_courses()

if __name__ == "__main__":
    main()