from playwright.sync_api import sync_playwright
from config import HEADLESS, USER_DATA_DIR
from utils.logger import logger

class BrowserAgent:
    def __init__(self):
        self.playwright = None
        self.context = None
        
    def start(self):
        logger.info("[info]Starting Playwright engine with persistent context...[/info]")
        self.playwright = sync_playwright().start()
        
        try:
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=HEADLESS,
                viewport={'width': 1280, 'height': 800},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                args=["--disable-blink-features=AutomationControlled"]
            )
        except Exception as e:
            logger.error(f"[error]Failed to launch persistent context (is Chrome open?): {e}[/error]")
            raise
            
        return self.context
        
    def close(self):
        logger.info("[info]Closing Playwright engine...[/info]")
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()
