import sys
from rich.console import Console
from ui.banner import show_banner
from core.browser_agent import BrowserAgent
from core.task_router import TaskRouter
from utils.exporter import DataExporter
from utils.logger import logger

console = Console()

def main():
    try:
        show_banner()
        logger.info("Application started (Playwright Version)")
        
        # Get User Input
        website = console.input("[bold cyan]Enter website to analyze (e.g. example.com):[/] ").strip()
        if not website:
            console.print("[red]Website cannot be empty. Exiting.[/]")
            return
            
        max_items_input = console.input("[bold cyan]Max products to extract (default 10):[/] ").strip()
        max_items = int(max_items_input) if max_items_input.isdigit() else 10
        
        format_type = console.input("[bold cyan]Export format (csv/xlsx/json) [default: csv]:[/] ").strip().lower()
        if format_type not in ['csv', 'xlsx', 'json']:
            format_type = 'csv'

        console.print("\n[bold yellow][AI ECOMMERCE INTELLIGENCE][/]")
        
        agent = BrowserAgent()
        
        try:
            # Step 1: Launch Browser & Navigate
            console.print("[cyan][INFO] Launching browser...[/cyan]")
            agent.start()
            
            console.print(f"[cyan][INFO] Opening website: {website}...[/cyan]")
            agent.navigate(website)
            
            # Step 2: Human-like interaction
            console.print("[cyan][INFO] Simulating human behavior (scrolling)...[/cyan]")
            agent.human_scroll(2)
            
            # Step 3: Routing & Research
            router = TaskRouter(agent.page)
            products = router.execute_research(website, max_items)
            
            if not products:
                console.print("\n[bold red]FAILED ✗[/]")
                console.print("Could not find any products.")
                return

            # Step 4: Export
            console.print("[cyan][INFO] Exporting data...[/cyan]")
            exporter = DataExporter()
            filepath = exporter.export(products, website, format_type)

            if filepath:
                console.print("\n[bold green]SUCCESS ✓[/]")
                console.print(f"Found [bold cyan]{len(products)}[/] products.")
                console.print(f"Data saved to: [green]{filepath}[/]")
            else:
                console.print("\n[bold red]FAILED ✗[/]")
                console.print("Data extraction succeeded, but export failed.")
                
        finally:
            agent.stop()

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/]")
        logger.info("Application cancelled by user")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]An unexpected error occurred: {str(e)}[/]")
        logger.error(f"Unexpected error in main: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
