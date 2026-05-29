"""
utils/exporter.py

Exports cleaned product data to CSV, XLSX, and JSON.

Also saves a permanent raw_tokopedia.json for debugging
(written by tokopedia_agent.py — not duplicated here).
"""

import pandas as pd
import os
import json
from datetime import datetime
from config import EXPORTS_DIR
from utils.logger import logger


class DataExporter:

    @staticmethod
    def export_results(keyword: str, data: list) -> dict:
        """
        Save cleaned product list to:
          exports/<keyword>_<timestamp>.csv
          exports/<keyword>_<timestamp>.xlsx
          exports/<keyword>_<timestamp>.json

        Returns dict of file paths.
        """
        safe_keyword = (
            "".join(c for c in keyword if c.isalnum() or c == " ")
            .strip()
            .replace(" ", "_")
            .lower()
        )
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{safe_keyword}_{timestamp}"

        csv_path  = os.path.join(EXPORTS_DIR, f"{base_name}.csv")
        xlsx_path = os.path.join(EXPORTS_DIR, f"{base_name}.xlsx")
        json_path = os.path.join(EXPORTS_DIR, f"{base_name}.json")

        if not data:
            logger.warning("[warning]No products to export — writing empty debug file.[/warning]")
            empty_path = os.path.join(EXPORTS_DIR, "debug_empty_result.json")
            with open(empty_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)
            return {"json": empty_path}

        df = pd.DataFrame(data)

        # Ensure numeric columns are stored as numbers, not strings
        for col in ("price", "sold"):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

        for col in ("rating",):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # ── Export ────────────────────────────────────────────────────────
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        df.to_excel(xlsx_path, index=False)
        df.to_json(json_path, orient="records", indent=2, force_ascii=False)

        logger.info(f"[success]CSV  saved → {csv_path}[/success]")
        logger.info(f"[success]XLSX saved → {xlsx_path}[/success]")
        logger.info(f"[success]JSON saved → {json_path}[/success]")

        return {
            "csv":  csv_path,
            "xlsx": xlsx_path,
            "json": json_path,
        }
