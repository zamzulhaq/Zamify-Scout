import logging
from config import LOG_FILE

def setup_logger():
    """
    Sets up a simple logger to write to logs/app.log
    """
    logger = logging.getLogger("ecom_ai")
    logger.setLevel(logging.DEBUG)
    
    # Prevent duplicate handlers
    if not logger.handlers:
        file_handler = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    return logger

# Create a global logger instance
logger = setup_logger()
