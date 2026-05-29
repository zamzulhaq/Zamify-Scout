from playwright.sync_api import sync_playwright
from config import HEADLESS
from utils.logger import logger

class BrowserAgent:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        
    def start(self):
        logger.info("[info]Starting Playwright engine...[/info]")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=HEADLESS)
        self.context = self.browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        return self.context
        
    def close(self):
        logger.info("[info]Closing Playwright engine...[/info]")
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
