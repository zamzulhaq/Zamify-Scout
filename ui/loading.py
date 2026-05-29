from rich.progress import Progress, SpinnerColumn, TextColumn
import time

def show_progress(task_description: str, duration: float = 2.0):
    """
    Shows a simple loading animation with rich progress bar.
    This simulates the "AI Automation Tool" vibe while processing.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(f"[cyan]{task_description}...", total=100)
        
        steps = int(duration * 10)
        sleep_time = duration / steps
        
        for _ in range(steps):
            time.sleep(sleep_time)
            progress.update(task, advance=(100 / steps))
