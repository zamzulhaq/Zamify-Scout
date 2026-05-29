import sys
import os

# Add current dir to path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.prompt import Prompt
from ui.banner import get_banner
from ui.terminal_theme import sentinel_theme
from core.ai_controller import AIController

console = Console(theme=sentinel_theme)

def main():
    console.print(get_banner())
    
    # User Input
    keyword = Prompt.ask("\n[bold cyan]Enter Market / Product Keyword (e.g. 'celana cargo pria')[/bold cyan]")
    
    if not keyword.strip():
        console.print("[error]Keyword cannot be empty. Exiting.[/error]")
        sys.exit(1)
        
    controller = AIController()
    controller.start_research(keyword.strip())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[warning]Operation cancelled by user. Exiting...[/warning]")
        sys.exit(0)
