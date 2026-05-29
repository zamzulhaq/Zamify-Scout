from playwright.sync_api import Page
from urllib.parse import urljoin
from utils.logger import logger

class CategoryScraper:
    """
    Extracts category links from a webpage using Playwright.
    """
    def __init__(self, page: Page):
        self.page = page

    def extract_categories(self, base_url: str) -> list:
        """
        Locates navigation or category links in the DOM.
        """
        categories = []
        
        # Look for all anchor tags
        locators = self.page.locator("a")
        count = locators.count()
        
        for i in range(count):
            try:
                elem = locators.nth(i)
                href = elem.get_attribute("href")
                text = elem.inner_text().strip()
                
                if href and text and ('category' in href.lower() or 'shop' in href.lower()):
                    full_url = urljoin(base_url, href)
                    categories.append({
                        "name": text,
                        "url": full_url
                    })
            except Exception as e:
                logger.debug(f"Failed to parse category link: {str(e)}")
                continue
                
        # Remove duplicates
        unique_categories = {item['url']: item for item in categories}.values()
        return list(unique_categories)
