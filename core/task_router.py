from research.tokopedia_agent import TokopediaAgent
from utils.logger import logger


class TaskRouter:
    """Routes ecommerce search tasks to active platform agents."""

    def __init__(self, context):
        self.context = context

    def route_and_execute(self, keyword: str) -> dict:
        """
        Run active platform agents and return results per-platform.

        Returns:
            dict with key "tokopedia" containing a list of products.
        """
        results = {}

        logger.info("[info]Routing task to Tokopedia Agent...[/info]")
        try:
            tokopedia = TokopediaAgent(self.context)
            results["tokopedia"] = tokopedia.search(keyword)
        except Exception as e:
            logger.error(f"[error]Tokopedia Agent failed: {e}[/error]")
            results["tokopedia"] = []

        return results
