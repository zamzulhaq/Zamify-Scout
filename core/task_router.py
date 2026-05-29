from research.tokopedia_agent import TokopediaAgent
from utils.logger import logger

class TaskRouter:
    def __init__(self, context):
        self.context = context
        
    def route_and_execute(self, keyword: str):
        all_results = []
        
        # In the future, this loops over multiple platforms. For now, Tokopedia.
        logger.info("[info]Routing task to Tokopedia Agent...[/info]")
        tokopedia = TokopediaAgent(self.context)
        try:
            results = tokopedia.search(keyword)
            all_results.extend(results)
        except Exception as e:
            logger.error(f"[error]Tokopedia Agent failed: {e}[/error]")
            
        return all_results
