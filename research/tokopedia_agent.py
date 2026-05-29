from playwright.sync_api import BrowserContext
import random
import os
from urllib.parse import quote
from config import MAX_PRODUCTS_PER_PLATFORM, SCROLL_PAUSE_TIME, LOGS_DIR
from utils.logger import logger
from utils.cleaner import DataCleaner

# ─────────────────────────────────────────────────────────────
# JavaScript: Link-first, pattern-based product extraction.
#
# Strategy:
#   1. Find all <a href*="/p/"> links (product links)
#   2. Walk UP the DOM (max 6 ancestors) until we find a box
#      that contains BOTH a price ("Rp") AND a title (anchor text)
#   3. Inside that container, extract:
#        - name  → <a href="/p/"> text
#        - price → first node whose text includes "Rp"
#        - sold  → first node whose text includes "terjual"
#        - image → first <img> src
#        - link  → the href
# ─────────────────────────────────────────────────────────────
_JS_LINK_FIRST = """
() => {
    function getText(el) {
        return (el ? el.innerText || el.textContent || "" : "").trim();
    }

    function isVisible(el) {
        const r = el.getBoundingClientRect();
        return r.width > 0 && r.height > 0;
    }

    // Walk ancestors up to maxLevels, return the first that
    // contains BOTH a price signal and non-trivial text
    function findProductContainer(anchor, maxLevels) {
        let el = anchor.parentElement;
        for (let i = 0; i < maxLevels; i++) {
            if (!el) break;
            const text = getText(el);
            if (text.includes("Rp") && text.length > 30) return el;
            el = el.parentElement;
        }
        return null;
    }

    // Find the first text node / descendant matching a pattern
    function findTextNode(container, pattern) {
        const all = Array.from(container.querySelectorAll("*"));
        for (const node of all) {
            // Only leaf-ish nodes (few children)
            if (node.children.length > 3) continue;
            const t = getText(node);
            if (pattern.test(t)) return t;
        }
        return "";
    }

    const RpPattern     = /Rp[\s\d.,]+/;
    const SoldPattern   = /\\d+[\\s.]*(rb\\s+)?terjual/i;
    const RatingPattern = /^[1-5](\\.[0-9])?$/;

    // ── Collect all product links ───────────────────────────
    const anchors = Array.from(document.querySelectorAll('a[href*="/p/"]'));
    const seen_hrefs = new Set();
    const products = [];

    for (const anchor of anchors) {
        const href = anchor.href || anchor.getAttribute("href") || "";
        if (!href || seen_hrefs.has(href)) continue;
        if (!isVisible(anchor)) continue;
        seen_hrefs.add(href);

        // ── Find product container ─────────────────────────
        const container = findProductContainer(anchor, 6);
        if (!container) continue;

        const containerText = getText(container);

        // ── Name ──────────────────────────────────────────
        const name = getText(anchor).replace(/\\n/g, " ").trim() ||
                     anchor.getAttribute("title") || "";
        if (!name || name.length < 5) continue;

        // ── Price ─────────────────────────────────────────
        const priceMatch = containerText.match(RpPattern);
        const price_raw = priceMatch ? priceMatch[0].trim() : "";
        if (!price_raw) continue;  // skip non-product links

        // ── Sold ──────────────────────────────────────────
        const soldMatch = containerText.match(SoldPattern);
        const sold_raw = soldMatch ? soldMatch[0].trim() : "";

        // ── Rating ────────────────────────────────────────
        const ratingMatch = containerText.match(RatingPattern);
        const rating_raw = ratingMatch ? ratingMatch[0].trim() : "";

        // ── Image ─────────────────────────────────────────
        const img = container.querySelector("img");
        const image_src = img
            ? (img.src || img.getAttribute("data-src") || img.getAttribute("data-lazy-src") || "")
            : "";

        // ── Store ─────────────────────────────────────────
        // store name often appears after price/sold block, skip data-testid strategy
        const store_el = container.querySelector('[data-testid*="Shop"], [class*="shop"], [class*="Store"]');
        const store = store_el ? getText(store_el) : "";

        products.push({
            name,
            price_raw,
            sold_raw,
            rating_raw,
            store,
            link: href,
            image: image_src,
        });

        if (products.length >= 100) break;
    }

    return products;
}
"""


class TokopediaAgent:
    def __init__(self, context: BrowserContext):
        self.context = context
        self.platform = "Tokopedia"

    # ── Private helpers ────────────────────────────────────────────────────

    def _human_scroll(self, page, rounds: int = 14):
        """Gradual human-like scrolling to trigger lazy-loaded content."""
        for _ in range(rounds):
            step = random.randint(250, 650)
            page.mouse.wheel(0, step)
            page.wait_for_timeout(random.uniform(0.4, SCROLL_PAUSE_TIME) * 1000)
        # Scroll back up slightly (like a real user re-reading)
        page.mouse.wheel(0, -random.randint(200, 500))
        page.wait_for_timeout(1500)

    def _soft_wait_for_products(self, page):
        """Wait non-blockingly until price text appears."""
        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except Exception as e:
            logger.debug(f"Soft networkidle timeout: {e}")
        try:
            page.wait_for_function(
                "() => document.body.innerText.includes('Rp') && document.querySelectorAll('a[href*=\"/p/\"]').length > 0",
                timeout=8000
            )
        except Exception as e:
            logger.debug(f"Soft signal wait timeout: {e}")

    def _run_js_extraction(self, page) -> list:
        """Run the link-first JavaScript extraction. Returns raw candidate list."""
        try:
            raw = page.evaluate(_JS_LINK_FIRST)
            return raw if isinstance(raw, list) else []
        except Exception as e:
            logger.error(f"[error]JS extraction failed: {e}[/error]")
            return []

    # ── Main search method ─────────────────────────────────────────────────

    def search(self, keyword: str) -> list:
        page = self.context.new_page()
        search_url = f"https://www.tokopedia.com/search?q={quote(keyword)}"
        logger.info(f"[info]Navigating to: {search_url}[/info]")

        try:
            page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3000)
        except Exception as e:
            logger.error(f"[error]Page navigation error: {e}[/error]")

        # ── Scroll + retry loop ────────────────────────────────────────────
        raw_candidates = []
        max_attempts = 3

        for attempt in range(max_attempts):
            logger.info(f"[info]Attempt {attempt+1}/{max_attempts}: scrolling + waiting for products...[/info]")
            page.screenshot(path=os.path.join(LOGS_DIR, f"toko_attempt_{attempt}_before.png"))

            self._human_scroll(page, rounds=14)
            self._soft_wait_for_products(page)

            page.screenshot(path=os.path.join(LOGS_DIR, f"toko_attempt_{attempt}_after.png"))

            # Live DOM counter debug
            link_count = page.locator('a[href*="/p/"]').count()
            logger.info(f"[info]Live DOM: {link_count} product links found (a[href*='/p/'])[/info]")

            raw_candidates = self._run_js_extraction(page)
            logger.info(f"[info]JS extraction: {len(raw_candidates)} raw product candidates[/info]")

            if raw_candidates:
                # Print first candidate for debug
                first = raw_candidates[0]
                logger.info(
                    f"[info]First candidate → name: {first.get('name','')[:60]} | "
                    f"price: {first.get('price_raw','')} | "
                    f"sold: {first.get('sold_raw','')}[/info]"
                )
                break
            else:
                logger.warning(f"[warning]0 candidates on attempt {attempt+1}, retrying...[/warning]")
                if attempt < max_attempts - 1:
                    page.wait_for_timeout(3000)

        # ── Debug snapshot if still empty ─────────────────────────────────
        if not raw_candidates:
            logger.warning("[warning]All attempts failed. Saving debug snapshot.[/warning]")
            page.screenshot(path=os.path.join(LOGS_DIR, "tokopedia_debug_0_products.png"))
            with open(os.path.join(LOGS_DIR, "tokopedia_debug_dom.html"), "w", encoding="utf-8") as f:
                f.write(page.content())

        # ── Clean & build product list ────────────────────────────────────
        products = []
        for raw in raw_candidates[:MAX_PRODUCTS_PER_PLATFORM]:
            try:
                name  = DataCleaner.clean_text(raw.get("name", ""))
                price = DataCleaner.clean_price(raw.get("price_raw", ""))
                link  = raw.get("link", "N/A")
                image = raw.get("image", "N/A") or "N/A"
                sold  = DataCleaner.clean_text(raw.get("sold_raw", "")) or "N/A"
                store = DataCleaner.clean_text(raw.get("store", "")) or "N/A"
                rating = DataCleaner.clean_text(raw.get("rating_raw", "")) or "N/A"

                if name and price > 0:
                    products.append({
                        "name":     name,
                        "price":    price,
                        "rating":   rating,
                        "sold":     sold,
                        "store":    store,
                        "link":     link,
                        "image":    image,
                        "category": keyword,
                        "platform": self.platform
                    })
            except Exception as e:
                logger.debug(f"Failed cleaning candidate: {e}")

        page.screenshot(path=os.path.join(LOGS_DIR, "tokopedia_debug_final.png"))
        page.close()
        logger.info(f"[info]Final result: {len(products)} valid products extracted.[/info]")
        return products
