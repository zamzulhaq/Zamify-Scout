import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rich.console import Console
from rich.prompt import Prompt

from core.travel_controller import TravelController
from ui.banner import get_banner
from ui.terminal_theme import sentinel_theme


console = Console(theme=sentinel_theme)


def main():
    console.print(get_banner())

    keyword = Prompt.ask(
        "\n[bold cyan]Enter Travel Keyword (e.g. 'hotel murah bandung', 'penginapan bali')[/bold cyan]"
    )

    if not keyword.strip():
        console.print("[error]Keyword cannot be empty. Exiting.[/error]")
        sys.exit(1)

    controller = TravelController()
    controller.start_research(keyword.strip())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[warning]Operation cancelled by user. Exiting...[/warning]")
        sys.exit(0)
    except ValueError as exc:
        console.print(f"[error]{exc}[/error]")
        sys.exit(1)

