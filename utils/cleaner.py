"""
utils/cleaner.py

Data cleaning module for raw scraped ecommerce text.

Public API
----------
DataCleaner.clean_text(text)         → str
DataCleaner.clean_price(text)        → int
DataCleaner.clean_sold(text)         → int
DataCleaner.clean_rating(text)       → float
DataCleaner.extract_product(raw, **) → dict | None
"""

import re
from typing import Optional

# ── Compiled patterns (reused across calls) ───────────────────────────────────

_RE_WHITESPACE  = re.compile(r'\s+')

# Price: "Rp125.000", "Rp 1.250.000", "125000"
_RE_PRICE_FULL  = re.compile(r'Rp\.?\s?([\d.,]+)', re.IGNORECASE)

# Sold: "1,2rb terjual", "1.2rb terjual", "230 terjual", "1rb terjual"
_RE_SOLD_RB     = re.compile(r'([\d.,]+)\s*rb\s*(?:\+\s*)?terjual', re.IGNORECASE)
_RE_SOLD_PLAIN  = re.compile(r'([\d.,]+)\s*(?:\+\s*)?terjual', re.IGNORECASE)

# Rating: "4.8", "4,8", "Rating 4.8"
_RE_RATING      = re.compile(r'\b([1-5][.,]\d|[1-5])\b')

# Lines to skip when hunting for product name
_SKIP_PATTERNS  = [
    re.compile(r'Rp', re.IGNORECASE),
    re.compile(r'terjual', re.IGNORECASE),
    re.compile(r'rating', re.IGNORECASE),
    re.compile(r'^\s*[1-5][.,]\d\s*$'),   # bare rating number
    re.compile(r'^\s*\d+\s*$'),            # bare number only
]


# ─────────────────────────────────────────────────────────────────────────────
class DataCleaner:
    """Static utility class: messy text → clean structured fields."""

    # ── Basic text cleanup ────────────────────────────────────────────────

    @staticmethod
    def clean_text(text: str) -> str:
        """Collapse whitespace and strip surrounding space."""
        if not text:
            return ""
        return _RE_WHITESPACE.sub(' ', text).strip()

    # ── Price ─────────────────────────────────────────────────────────────

    @staticmethod
    def clean_price(raw: str) -> int:
        """
        Extract integer price from strings like:
          "Rp125.000"  → 125000
          "Rp 1.250.000" → 1250000
          "125000"     → 125000
        Returns 0 if not parseable.
        """
        if not raw:
            return 0
        # Try explicit "Rp…" pattern first
        m = _RE_PRICE_FULL.search(raw)
        number_str = m.group(1) if m else raw
        # Remove thousand separators (dot or comma used as thousands)
        cleaned = number_str.replace('.', '').replace(',', '').replace(' ', '')
        digits = re.findall(r'\d+', cleaned)
        try:
            return int(''.join(digits)) if digits else 0
        except ValueError:
            return 0

    # ── Sold count ────────────────────────────────────────────────────────

    @staticmethod
    def clean_sold(raw: str) -> int:
        """
        Extract sold count from strings like:
          "1,2rb terjual"  → 1200
          "1.5rb terjual"  → 1500
          "230 terjual"    → 230
          "1rb+ terjual"   → 1000
        Returns 0 if not parseable.
        """
        if not raw:
            return 0

        # Case 1: "rb" (ribuan = thousands) multiplier
        m_rb = _RE_SOLD_RB.search(raw)
        if m_rb:
            num_str = m_rb.group(1).replace(',', '.').strip()
            try:
                return int(float(num_str) * 1000)
            except ValueError:
                pass

        # Case 2: plain number before "terjual"
        m_plain = _RE_SOLD_PLAIN.search(raw)
        if m_plain:
            num_str = m_plain.group(1).replace('.', '').replace(',', '').strip()
            try:
                return int(num_str)
            except ValueError:
                pass

        return 0

    # ── Rating ────────────────────────────────────────────────────────────

    @staticmethod
    def clean_rating(raw: str) -> float:
        """
        Extract rating from strings like "4.8", "Rating 4,8".
        Returns 0.0 if not parseable.
        """
        if not raw:
            return 0.0
        m = _RE_RATING.search(raw)
        if m:
            try:
                return float(m.group(1).replace(',', '.'))
            except ValueError:
                pass
        return 0.0

    # ── Name extraction ───────────────────────────────────────────────────

    @staticmethod
    def extract_name(text_block: str) -> str:
        """
        From a multi-line text block, pick the best candidate for product name:
        - Must NOT look like a price / sold / rating line
        - Prefer the longest qualifying line
        """
        lines = _RE_WHITESPACE.sub(' ', text_block).split('\n')
        best = ""
        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:
                continue
            if any(pat.search(line) for pat in _SKIP_PATTERNS):
                continue
            if len(line) > len(best):
                best = line
        return best.strip()

    # ── Full product extraction ───────────────────────────────────────────

    @staticmethod
    def extract_product(
        raw: dict,
        platform: str = "tokopedia",
        category: str = "",
    ) -> Optional[dict]:
        """
        Convert a raw scraped dict into a clean structured product dict.

        Expected raw keys (all optional strings):
            name, price_raw, sold_raw, rating_raw, store, link, image

        Returns None if price is missing/zero (skip invalid products).
        """
        # ── Name ──────────────────────────────────────────────────────────
        name_raw = raw.get("name", "")
        # If raw name is a multi-line block (JS innerText), try to clean it
        if "\n" in name_raw:
            name = DataCleaner.extract_name(name_raw)
        else:
            name = DataCleaner.clean_text(name_raw)

        # ── Price ─────────────────────────────────────────────────────────
        price = DataCleaner.clean_price(raw.get("price_raw", "") or raw.get("price", ""))
        if price == 0:
            return None  # Skip — no valid price

        # ── Sold ──────────────────────────────────────────────────────────
        sold = DataCleaner.clean_sold(raw.get("sold_raw", "") or raw.get("sold", ""))

        # ── Rating ────────────────────────────────────────────────────────
        rating = DataCleaner.clean_rating(raw.get("rating_raw", "") or raw.get("rating", ""))

        # ── Store / link / image ──────────────────────────────────────────
        store  = DataCleaner.clean_text(raw.get("store", ""))  or "N/A"
        link   = (raw.get("link",  "") or "N/A").strip()
        image  = (raw.get("image", "") or "N/A").strip()

        return {
            "name":     name or "N/A",
            "price":    price,
            "sold":     sold,
            "rating":   rating if rating > 0 else "N/A",
            "store":    store,
            "link":     link,
            "image":    image,
            "category": category,
            "platform": platform,
        }

    # ── Batch helper ──────────────────────────────────────────────────────

    @staticmethod
    def clean_batch(
        raw_list: list,
        platform: str = "tokopedia",
        category: str = "",
    ) -> list:
        """
        Process a list of raw dicts through extract_product(),
        skipping None results (invalid products).
        Returns a clean list ready for export / analytics.
        """
        products = []
        for raw in raw_list:
            try:
                cleaned = DataCleaner.extract_product(raw, platform=platform, category=category)
                if cleaned:
                    products.append(cleaned)
            except Exception:
                pass
        return products
