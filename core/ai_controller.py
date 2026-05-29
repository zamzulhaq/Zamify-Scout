from core.browser_agent import BrowserAgent
from core.task_router import TaskRouter
from research.market_analyzer import MarketAnalyzer
from utils.exporter import DataExporter
from utils.logger import logger
from ui.loading import get_progress_bar

class AIController:
    def __init__(self):
        self.browser_agent = BrowserAgent()
        
    def start_research(self, keyword: str):
        logger.info(f"[info]Initiating Autonomous Research for:[/info] [accent]{keyword}[/accent]")
        
        progress = get_progress_bar()
        with progress:
            task1 = progress.add_task("[cyan]Launching browser...", total=100)
            context = self.browser_agent.start()
            progress.update(task1, advance=100)
            
            task2 = progress.add_task("[cyan]Searching Tokopedia...", total=100)
            router = TaskRouter(context)
            results = router.route_and_execute(keyword)
            progress.update(task2, advance=100)
            
            task3 = progress.add_task("[cyan]Analyzing products...", total=100)
            if results:
                logger.info(f"[success]Found {len(results)} products.[/success]")
            else:
                logger.warning("[warning]No products found. Exporting empty debug file.[/warning]")
                
            # Always attempt to export (exporter handles empty case)
            DataExporter.export_results(keyword, results)
            logger.info("[success]Export process completed[/success]")
            
            progress.update(task3, advance=100)
            
            task4 = progress.add_task("[cyan]Collecting market intelligence...", total=100)
            self.browser_agent.close()
            progress.update(task4, advance=100)
            
        if results:
            MarketAnalyzer.analyze(keyword, results)
            
        logger.info("\n[success]SUCCESS ✓[/success]")
