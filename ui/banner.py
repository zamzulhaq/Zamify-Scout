from rich.panel import Panel
from rich.align import Align
from rich.text import Text

def get_banner() -> Panel:
    banner_text = Text()
    banner_text.append("███████╗ █████╗ ███╗   ███╗██╗███████╗██╗   ██╗\n", style="bold blue")
    banner_text.append("╚══███╔╝██╔══██╗████╗ ████║██║██╔════╝╚██╗ ██╔╝\n", style="bold blue")
    banner_text.append("  ███╔╝ ███████║██╔████╔██║██║█████╗   ╚████╔╝ \n", style="bold cyan")
    banner_text.append(" ███╔╝  ██╔══██║██║╚██╔╝██║██║██╔══╝    ╚██╔╝  \n", style="bold cyan")
    banner_text.append("███████╗██║  ██║██║ ╚═╝ ██║██║██║        ██║   \n", style="bold cyan")
    banner_text.append("╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝        ╚═╝   \n", style="bold blue")
    banner_text.append("\n[ SENTINEL V2 - AUTONOMOUS ECOMMERCE RESEARCH ]\n", style="bold magenta")
    
    return Panel(
        Align.center(banner_text),
        border_style="blue",
        title="[bold white]STARTUP AI TOOL[/bold white]",
        padding=(1, 2)
    )
