from playwright.sync_api import sync_playwright
import json
from typing import List, Dict
import logging
import time

class AnalyticsVidhyaScraper:
    def __init__(self):
        self.base_url = "https://courses.analyticsvidhya.com/collections"  # Updated base URL
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def extract_courses_from_page(self, page) -> List[Dict]:
        courses = []
        course_elements = page.query_selector_all('a[href*="/courses/"]')
        self.logger.info(f"Found {len(course_elements)} courses on current page")
        
        for element in course_elements:
            try:
                course = {
                    'title': (element.query_selector('h3').text_content().strip() if element.query_selector('h3') else None),
                    'url': 'https://courses.analyticsvidhya.com' + element.get_attribute('href'),
                    'image': element.query_selector('img').get_attribute('src') if element.query_selector('img') else None
                }
                
                if course['title']:
                    courses.append(course)
                    self.logger.info(f"Extracted: {course['title']}")
                    
            except Exception as e:
                self.logger.error(f"Error extracting course: {str(e)}")
                continue
        return courses

    def scrape_courses(self) -> List[Dict]:
        all_courses = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
            )
            page = context.new_page()
            
            try:
                page_num = 1
                while True:
                    # Updated URL format for collections pagination
                    url = f"{self.base_url}?page={page_num}" if page_num > 1 else self.base_url
                    self.logger.info(f"Navigating to page {page_num}: {url}")
                    
                    page.goto(url, wait_until='domcontentloaded')
                    page.wait_for_load_state('networkidle')
                    time.sleep(3)
                    
                    # Wait for course cards to appear
                    page.wait_for_selector('a[href*="/courses/"]', timeout=60000)
                    
                    # Extract courses from current page
                    current_page_courses = self.extract_courses_from_page(page)
                    all_courses.extend(current_page_courses)
                    
                    # Updated next page button selector
                    next_button = page.query_selector('a[href*="?page="]')
                    if not next_button:
                        self.logger.info("No more pages to scrape")
                        break
                        
                    next_button.click()
                    page.wait_for_load_state('networkidle')
                    page_num += 1
                    time.sleep(2)  # Wait between pages
                    
                    # Debug info
                    self.logger.info(f"Moving to page {page_num}")

            except Exception as e:
                self.logger.error(f"Error during scraping: {str(e)}")
                page.screenshot(path=f"error_page_{page_num}.png")
                with open(f"page_content_{page_num}.html", "w", encoding="utf-8") as f:
                    f.write(page.content())
            finally:
                context.close()
                browser.close()
                
        return all_courses

    def save_to_json(self, courses: List[Dict], filename: str = "courses.json"):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(courses, f, indent=2, ensure_ascii=False)
        self.logger.info(f"Saved {len(courses)} courses to {filename}")

def main():
    scraper = AnalyticsVidhyaScraper()
    courses = scraper.scrape_courses()
    scraper.save_to_json(courses)

if __name__ == "__main__":
    main()