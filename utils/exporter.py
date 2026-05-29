import pandas as pd
import os
from datetime import datetime
from config import EXPORTS_DIR

class DataExporter:
    @staticmethod
    def export_results(keyword: str, data: list):
        if not data:
            empty_path = os.path.join(EXPORTS_DIR, "debug_empty_result.json")
            pd.DataFrame([]).to_json(empty_path, orient='records', indent=4)
            return {"json": empty_path}
            
        df = pd.DataFrame(data)
        
        safe_keyword = "".join([c for c in keyword if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        safe_keyword = safe_keyword.replace(' ', '_').lower()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        csv_path = os.path.join(EXPORTS_DIR, f"{safe_keyword}_{timestamp}.csv")
        xlsx_path = os.path.join(EXPORTS_DIR, f"{safe_keyword}_{timestamp}.xlsx")
        json_path = os.path.join(EXPORTS_DIR, f"{safe_keyword}_{timestamp}.json")
        
        df.to_csv(csv_path, index=False)
        df.to_excel(xlsx_path, index=False)
        df.to_json(json_path, orient='records', indent=4)
        
        return {
            "csv": csv_path,
            "xlsx": xlsx_path,
            "json": json_path
        }
