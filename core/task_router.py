from playwright.sync_api import Page
from scraper.category_scraper import CategoryScraper
from scraper.product_scraper import ProductScraper
from utils.logger import logger
from rich.console import Console

console = Console()

class TaskRouter:
    """
    Decides what to do based on the current page state.
    """
    def __init__(self, page: Page):
        self.page = page
        self.cat_scraper = CategoryScraper(page)
        self.prod_scraper = ProductScraper(page)

    def execute_research(self, base_url: str, max_items: int) -> list:
        """
        Main decision loop for the autonomous agent.
        Returns a list of extracted product dictionaries.
        """
        all_products = []
        
        # Phase 1: Try to find categories from the homepage
        console.print("[cyan][INFO] Detecting categories...[/cyan]")
        logger.info("Detecting categories on homepage")
        categories = self.cat_scraper.extract_categories(base_url)
        
        if categories:
            console.print(f"[cyan][INFO] Found {len(categories)} categories to explore.[/cyan]")
            
            # Phase 2: Explore each category
            for cat in categories:
                if len(all_products) >= max_items:
                    break
                    
                console.print(f"[cyan][INFO] Visiting category: {cat['name']}[/cyan]")
                logger.info(f"Navigating to category {cat['name']} - {cat['url']}")
                self.page.goto(cat['url'], wait_until="domcontentloaded")
                
                # Extract products from this category page
                products = self.prod_scraper.extract_products(cat['name'], limit=max_items - len(all_products))
                
                if products:
                    for p in products:
                        console.print(f"[green][SUCCESS] Product extracted:\n* {p['name']}\n* {p['price']}[/green]")
                    all_products.extend(products)
                    
        else:
            # Fallback: No categories found, try extracting products directly from homepage
            console.print("[yellow][WARNING] No clear categories found. Scanning homepage for products...[/yellow]")
            logger.info("No categories found. Scanning homepage directly.")
            products = self.prod_scraper.extract_products(category_name="Homepage", limit=max_items)
            
            if products:
                for p in products:
                    console.print(f"[green][SUCCESS] Product extracted:\n* {p['name']}\n* {p['price']}[/green]")
                all_products.extend(products)
                
        return all_products
