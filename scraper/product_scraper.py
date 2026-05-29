from playwright.sync_api import Page
from utils.logger import logger
import time

class ProductScraper:
    """
    Extracts product cards from the DOM using Playwright.
    """
    def __init__(self, page: Page):
        self.page = page

    def extract_products(self, category_name: str, limit: int = 10) -> list:
        """
        Finds product elements and extracts data.
        """
        products = []
        
        # Scroll slightly to trigger lazy-loaded images
        self.page.mouse.wheel(0, 500)
        time.sleep(1)
        
        # Target common product card classes
        selectors = 'li.product, div.product, .product-card, article.product, .item'
        product_cards = self.page.locator(selectors)
        count = product_cards.count()
        
        logger.info(f"Found {count} potential product cards")
        
        for i in range(min(count, limit)):
            try:
                card = product_cards.nth(i)
                
                # Title
                title_loc = card.locator('.woocommerce-loop-product__title, h2, h3, .product-title').first
                title = title_loc.inner_text().strip() if title_loc.count() > 0 else ""
                
                if not title:
                    continue
                    
                # Price
                price_loc = card.locator('.price, .product-price, span.amount').first
                price = price_loc.inner_text().strip() if price_loc.count() > 0 else "N/A"
                
                # Link
                link_loc = card.locator('a').first
                link = link_loc.get_attribute('href') if link_loc.count() > 0 else "N/A"
                
                # Image
                img_loc = card.locator('img').first
                image = "N/A"
                if img_loc.count() > 0:
                    image = img_loc.get_attribute('src') or img_loc.get_attribute('data-src') or "N/A"
                
                products.append({
                    "name": title,
                    "price": price,
                    "category": category_name,
                    "image": image,
                    "link": link
                })
                
            except Exception as e:
                logger.debug(f"Failed to parse a product card: {str(e)}")
                continue
                
        return products
