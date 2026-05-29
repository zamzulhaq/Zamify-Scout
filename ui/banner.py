from rich.panel import Panel
from rich.align import Align
from rich.console import Console
from rich.text import Text

console = Console()

def show_banner():
    """
    Displays a modern, professional terminal banner for the application.
    """
    title = Text("AI ECOMMERCE INTELLIGENCE", style="bold cyan", justify="center")
    subtitle = Text("Powered by Zamify | V1.0", style="dim", justify="center")
    
    content = Text()
    content.append("\n")
    content.append(title)
    content.append("\n")
    content.append(subtitle)
    content.append("\n")
    
    panel = Panel(
        content,
        border_style="cyan",
        padding=(1, 2),
        title="[bold green]System Ready",
        expand=False
    )
    
    console.print(Align.center(panel))
    console.print()
