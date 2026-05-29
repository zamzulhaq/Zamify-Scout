"""
research/aggregator.py

Combines results from multiple platform agents into a single dataset.
"""

from utils.logger import logger


class Aggregator:
    """Merge product lists from active ecommerce platforms."""

    @staticmethod
    def combine(*platform_results: list) -> list:
        """
        Accepts any number of result lists and merges them.

        Usage:
            all_data = Aggregator.combine(tokopedia_data)
        """
        combined = []
        for results in platform_results:
            if results:
                combined.extend(results)

        # Summary per platform
        platforms = {}
        for item in combined:
            plat = item.get("platform", "unknown")
            platforms[plat] = platforms.get(plat, 0) + 1

        logger.info(f"[info]Aggregator: {len(combined)} total products prepared.[/info]")
        for plat, count in platforms.items():
            logger.info(f"[info]  • {plat}: {count} products[/info]")

        return combined
