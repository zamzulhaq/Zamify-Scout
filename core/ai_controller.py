from core.browser_agent import BrowserAgent
from core.task_router import TaskRouter
from research.aggregator import Aggregator
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
            platform_results = router.route_and_execute(keyword)
            progress.update(task2, advance=100)

            task3 = progress.add_task("[cyan]Preparing Tokopedia data...", total=100)
            tokopedia_result = platform_results.get("tokopedia", [])
            tokopedia_data = (
                tokopedia_result
                if isinstance(tokopedia_result, list)
                else tokopedia_result.get("data", [])
            )
            platform_statuses = {
                "tokopedia": (
                    tokopedia_result.get("status", "success")
                    if isinstance(tokopedia_result, dict)
                    else "success"
                )
            }
            all_data = Aggregator.combine(tokopedia_data)
            progress.update(task3, advance=100)

            task4 = progress.add_task("[cyan]Exporting results...", total=100)
            if all_data:
                logger.info(f"[success]Found {len(all_data)} Tokopedia products.[/success]")
            else:
                logger.warning("[warning]No Tokopedia products found. Exporting empty debug file.[/warning]")

            DataExporter.export_results(keyword, all_data)
            logger.info("[success]Export process completed[/success]")
            progress.update(task4, advance=100)

            task5 = progress.add_task("[cyan]Collecting market intelligence...", total=100)
            self.browser_agent.close()
            progress.update(task5, advance=100)

        if all_data or platform_statuses:
            MarketAnalyzer.analyze(keyword, all_data, platform_statuses)

        logger.info("\n[success]SUCCESS[/success]")
