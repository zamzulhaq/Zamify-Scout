import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Ensure dirs exist
os.makedirs(EXPORTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Playwright settings
HEADLESS = False
USER_DATA_DIR = "C:/Users/arisb/AppData/Local/Google/Chrome/User Data/EcomBot"

# Agents settings
MAX_PRODUCTS_PER_PLATFORM = 50
SCROLL_PAUSE_TIME = 1.5
