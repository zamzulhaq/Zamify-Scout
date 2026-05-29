from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from utils.logger import logger
from config import HEADLESS, BROWSER_TIMEOUT, SCROLL_DELAY
import time

class BrowserAgent:
    """
    Manages the Playwright browser lifecycle.
    """
    def __init__(self):
        self.playwright = None
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None

    def start(self):
        """Launches the browser and creates a new context/page."""
        logger.info("Launching browser...")
        self.playwright = sync_playwright().start()
        
        # Launch Chromium (can be changed to firefox or webkit)
        self.browser = self.playwright.chromium.launch(
            headless=HEADLESS,
            args=["--start-maximized"]
        )
        
        # Create a context that simulates a real user
        self.context = self.browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        
        self.page = self.context.new_page()
        # Prevent timeouts on slow loading pages
        self.page.set_default_timeout(BROWSER_TIMEOUT)

    def stop(self):
        """Closes the browser resources safely."""
        logger.info("Closing browser...")
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def navigate(self, url: str):
        """Navigates to a URL and waits for network idle."""
        if not url.startswith("http"):
            url = "https://" + url
            
        logger.info(f"Opening website: {url}")
        self.page.goto(url, wait_until="domcontentloaded")
        
    def human_scroll(self, scroll_count: int = 3):
        """
        Simulates human scrolling to trigger lazy-loaded elements.
        """
        logger.debug(f"Executing human scroll ({scroll_count} times)")
        for _ in range(scroll_count):
            self.page.mouse.wheel(0, 800)
            time.sleep(SCROLL_DELAY)
