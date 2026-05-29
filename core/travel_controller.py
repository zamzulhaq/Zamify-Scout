from core.browser_agent import BrowserAgent
from travel.agent import TravelQueryParser, TravelResearchAgent
from travel.analyzer import TravelAnalyzer
from travel.exporter import TravelExporter
from ui.loading import get_progress_bar
from utils.logger import logger


class TravelController:
    def __init__(self):
        self.browser_agent = BrowserAgent()

    def start_research(self, keyword: str):
        travel_query = TravelQueryParser.parse(keyword)
        if not travel_query:
            raise ValueError("Travel keyword must include hotel, penginapan, or wisata.")

        category = travel_query.category
        location = travel_query.location
        logger.info(
            f"[info]Initiating AI Travel Price Intelligence for:[/info] "
            f"[accent]{category} di {location}[/accent]"
        )

        progress = get_progress_bar()
        with progress:
            task1 = progress.add_task("[cyan]Launching browser...", total=100)
            context = self.browser_agent.start()
            progress.update(task1, advance=100)

            task2 = progress.add_task("[cyan]Stage 1: discovering places on Google Maps...", total=100)
            travel_agent = TravelResearchAgent(context)
            discovered_names = travel_agent.discovery_agent.discover(category, location, limit=30)
            progress.update(task2, advance=100)

            task3 = progress.add_task("[cyan]Stage 2: validating prices from trusted sources...", total=100)
            places = travel_agent.detail_agent.research_all(discovered_names, location)
            progress.update(task3, advance=100)

            task4 = progress.add_task("[cyan]Analyzing travel intelligence...", total=100)
            analysis = TravelAnalyzer.analyze(category, location, places)
            TravelExporter.export_results(category, location, places, analysis)
            progress.update(task4, advance=100)

            task5 = progress.add_task("[cyan]Closing browser...", total=100)
            self.browser_agent.close()
            progress.update(task5, advance=100)

        TravelAnalyzer.print_report(analysis)
        logger.info("\n[success]TRAVEL RESEARCH COMPLETE[/success]")
        return analysis
