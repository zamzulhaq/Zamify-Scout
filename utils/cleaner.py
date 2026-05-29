import re

class DataCleaner:
    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        cleaned = re.sub(r'\s+', ' ', text)
        return cleaned.strip()

    @staticmethod
    def clean_price(raw_price: str) -> int:
        if not raw_price:
            return 0
        matches = re.findall(r'\d+', raw_price.replace('.', '').replace(',', ''))
        if matches:
            return int(matches[0])
        return 0
