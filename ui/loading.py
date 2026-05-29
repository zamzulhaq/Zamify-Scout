from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from ui.terminal_theme import sentinel_theme

console = Console(theme=sentinel_theme)

def get_progress_bar():
    return Progress(
        SpinnerColumn("dots", style="accent"),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    )
