import logging
import os
from config import LOGS_DIR
from rich.logging import RichHandler
from ui.terminal_theme import sentinel_theme
from rich.console import Console

console = Console(theme=sentinel_theme)

log_format = "%(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    datefmt="[%X]",
    handlers=[
        RichHandler(console=console, rich_tracebacks=True, show_path=False),
        logging.FileHandler(os.path.join(LOGS_DIR, "sentinel.log"), encoding="utf-8")
    ]
)

logger = logging.getLogger("sentinel")
