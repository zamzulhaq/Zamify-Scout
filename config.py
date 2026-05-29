import os

# Project root path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data export settings
EXPORT_DIR = os.path.join(BASE_DIR, "exports")

# Logging settings
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Create required directories if they don't exist
os.makedirs(EXPORT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Playwright & Scraper configuration
HEADLESS = False  # Set to False to watch the AI navigate
BROWSER_TIMEOUT = 30000  # 30 seconds
SCROLL_DELAY = 1.5  # Seconds between scrolls to simulate human behavior
