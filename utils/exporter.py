import pandas as pd
import os
from config import EXPORT_DIR
from utils.logger import logger
from datetime import datetime

class DataExporter:
    """
    Handles exporting data to various formats (CSV, XLSX, JSON).
    """
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def export(self, data: list, domain: str, format_type: str = "csv") -> str:
        """
        Exports the provided data list to the specified format.
        Returns the path to the saved file.
        """
        if not data:
            logger.warning("No data provided for export")
            return ""
            
        df = pd.DataFrame(data)
        
        # Clean domain for filename
        clean_domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
        base_filename = f"products_{clean_domain}_{self.timestamp}"
        
        filepath = ""
        
        try:
            if format_type.lower() == "csv":
                filepath = os.path.join(EXPORT_DIR, f"{base_filename}.csv")
                df.to_csv(filepath, index=False)
            elif format_type.lower() == "xlsx":
                filepath = os.path.join(EXPORT_DIR, f"{base_filename}.xlsx")
                df.to_excel(filepath, index=False)
            elif format_type.lower() == "json":
                filepath = os.path.join(EXPORT_DIR, f"{base_filename}.json")
                df.to_json(filepath, orient="records", indent=4)
            else:
                logger.error(f"Unsupported export format: {format_type}")
                return ""
                
            logger.info(f"Successfully exported {len(data)} items to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to export data to {format_type}: {str(e)}")
            return ""
