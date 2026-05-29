from playwright.sync_api import BrowserContext
import random
import os
import json
from urllib.parse import quote
from config import MAX_PRODUCTS_PER_PLATFORM, SCROLL_PAUSE_TIME, LOGS_DIR, EXPORTS_DIR, HEADLESS
from utils.logger import logger
from utils.cleaner import DataCleaner

# ─────────────────────────────────────────────────────────────────────────────
# JavaScript: Text-based / render-based product extraction.
#
# Strategy:
#   1. Find ALL leaf-ish DOM elements whose visible text contains "Rp"
#   2. For each price node, walk UP the DOM (max 6 levels) until we find
#      a container that also has a title (>10 chars, not just the price)
#   3. Inside that container extract:
#        - name  → longest text node that is NOT a price / sold string
#        - price → the "Rp…" string
#        - sold  → "terjual" pattern
#        - link  → any <a> href inside the container (optional)
#        - image → first <img> src (optional)
#   4. Deduplicate on (name, price_raw)
# ─────────────────────────────────────────────────────────────────────────────
_JS_TEXT_BASED = """
() => {
    const RpPattern     = /Rp\s?[\d.,]+/;
    const SoldPattern   = /[\d.]+\s*(rb\s+)?terjual/i;
    const RatingPattern = /^[1-5](\.\d)?$/;

    function getText(el) {
        return (el ? (el.innerText || el.textContent || "") : "").trim();
    }
    function isVisible(el) {
        try {
            const r = el.getBoundingClientRect();
            return r.width > 0 && r.height > 0;
        } catch(e) { return false; }
    }

    // ── Step 1: find all elements that directly display a price ──────────
    const allEls = Array.from(document.querySelectorAll("*"));
    const priceNodes = [];
    for (const el of allEls) {
        // Skip containers with many children — we want the price leaf
        if (el.children.length > 4) continue;
        const t = getText(el);
        if (RpPattern.test(t) && t.length < 50 && isVisible(el)) {
            priceNodes.push(el);
        }
    }

    // ── Step 2–3: walk up DOM to find product container ──────────────────
    const seenKey = new Set();
    const products = [];

    for (const priceEl of priceNodes) {
        let container = priceEl.parentElement;
        let foundContainer = null;

        for (let level = 0; level < 6; level++) {
            if (!container) break;
            const cText = getText(container);

            // Container must have meaningful title text beyond the price alone
            const textWithoutPrice = cText.replace(RpPattern, "").trim();
            if (textWithoutPrice.length > 15) {
                foundContainer = container;
                break;
            }
            container = container.parentElement;
        }

        if (!foundContainer) continue;

        const cText = getText(foundContainer);

        // ── Price ──────────────────────────────────────────────────────
        const priceMatch = cText.match(RpPattern);
        const price_raw = priceMatch ? priceMatch[0].trim() : "";
        if (!price_raw) continue;

        // ── Sold ───────────────────────────────────────────────────────
        const soldMatch = cText.match(SoldPattern);
        const sold_raw = soldMatch ? soldMatch[0].trim() : "";

        // ── Rating ─────────────────────────────────────────────────────
        const ratingMatch = cText.match(RatingPattern);
        const rating_raw = ratingMatch ? ratingMatch[0].trim() : "";

        // ── Name: longest line not matching price/sold/rating ──────────
        const lines = cText.split(/\\n+/).map(l => l.trim()).filter(l => l.length > 5);
        let name = "";
        for (const line of lines) {
            if (RpPattern.test(line)) continue;
            if (SoldPattern.test(line)) continue;
            if (RatingPattern.test(line)) continue;
            if (line.length > name.length) name = line;
        }
        if (!name || name.length < 5) continue;

        // ── Dedup ──────────────────────────────────────────────────────
        const key = name.slice(0, 40) + "|" + price_raw;
        if (seenKey.has(key)) continue;
        seenKey.add(key);

        // ── Link ───────────────────────────────────────────────────────
        const linkEl = foundContainer.querySelector("a[href]");
        const link = linkEl ? (linkEl.href || linkEl.getAttribute("href") || "") : "";

        // ── Image ──────────────────────────────────────────────────────
        const imgEl = foundContainer.querySelector("img");
        const image = imgEl
            ? (imgEl.src || imgEl.getAttribute("data-src") || imgEl.getAttribute("data-lazy-src") || "")
            : "";

        // ── Store ──────────────────────────────────────────────────────
        const storeEl = foundContainer.querySelector(
            '[data-testid*="Shop"], [class*="shop"], [class*="Store"], [class*="seller"]'
        );
        const store = storeEl ? getText(storeEl) : "";

        products.push({ name, price_raw, sold_raw, rating_raw, store, link, image });

        if (products.length >= 120) break;
    }

    return products;
}
"""


class TokopediaAgent:
    def __init__(self, context: BrowserContext):
        self.context = context
        self.platform = "Tokopedia"

    # ── Helpers ───────────────────────────────────────────────────────────

    def _human_scroll(self, page, rounds: int = 14):
        """Multi-pass gradual scroll to trigger all lazy-loaded content."""
        for _ in range(rounds):
            step = random.randint(250, 650)
            page.mouse.wheel(0, step)
            page.wait_for_timeout(random.uniform(0.4, SCROLL_PAUSE_TIME) * 1000)
        # One gentle scroll back up (human behaviour)
        page.mouse.wheel(0, -random.randint(300, 600))
        page.wait_for_timeout(1500)

    def _soft_wait(self, page):
        """Non-blocking waits: networkidle + price text visible."""
        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except Exception as e:
            logger.debug(f"networkidle soft-timeout: {e}")
        try:
            page.wait_for_function(
                "() => document.body.innerText.includes('Rp')",
                timeout=8000
            )
            logger.debug("Price text 'Rp' confirmed visible in DOM.")
        except Exception as e:
            logger.debug(f"Soft wait for 'Rp' text timed out: {e}")

    def _live_debug(self, page):
        """Print live DOM stats for debugging."""
        try:
            rp_count = page.evaluate(
                "() => Array.from(document.querySelectorAll('*'))"
                ".filter(el => el.children.length < 4 && (el.innerText||'').includes('Rp')).length"
            )
            a_count = page.locator("a").count()
            logger.info(f"[info]Live DOM: {rp_count} 'Rp' nodes | {a_count} <a> tags visible[/info]")
        except Exception as e:
            logger.debug(f"Live debug failed: {e}")

    def _run_js_extraction(self, page) -> list:
        try:
            raw = page.evaluate(_JS_TEXT_BASED)
            return raw if isinstance(raw, list) else []
        except Exception as e:
            logger.error(f"[error]JS extraction error: {e}[/error]")
            return []

    # ── Main ──────────────────────────────────────────────────────────────

    def search(self, keyword: str) -> list:
        page = self.context.new_page()
        search_url = f"https://www.tokopedia.com/search?q={quote(keyword)}"
        logger.info(f"[info]Navigating to: {search_url}[/info]")

        try:
            page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(3500)
        except Exception as e:
            logger.error(f"[error]Page navigation error: {e}[/error]")

        # ── Debug pause (only in non-headless mode) ───────────────────────
        if not HEADLESS:
            logger.info("[info]Non-headless mode: pausing 3s for manual DOM inspection if needed.[/info]")
            # Uncomment the line below to pause Playwright Inspector:
            # page.pause()

        # ── Scroll + retry loop ───────────────────────────────────────────
        raw_candidates = []
        max_attempts   = 3

        for attempt in range(max_attempts):
            logger.info(f"[info]Attempt {attempt+1}/{max_attempts}: scrolling to render products...[/info]")
            page.screenshot(path=os.path.join(LOGS_DIR, f"toko_{attempt}_before.png"))

            self._human_scroll(page, rounds=14)
            self._soft_wait(page)

            page.screenshot(path=os.path.join(LOGS_DIR, f"toko_{attempt}_after.png"))
            self._live_debug(page)

            raw_candidates = self._run_js_extraction(page)
            logger.info(f"[info]Attempt {attempt+1}: {len(raw_candidates)} raw candidates found.[/info]")

            if raw_candidates:
                first = raw_candidates[0]
                logger.info(
                    f"[info]Sample → name: '{first.get('name','')[:60]}' | "
                    f"price: '{first.get('price_raw','')}' | "
                    f"sold: '{first.get('sold_raw','')}'[/info]"
                )
                break
            else:
                logger.warning(f"[warning]0 candidates on attempt {attempt+1}. Waiting 3s before retry...[/warning]")
                if attempt < max_attempts - 1:
                    page.wait_for_timeout(3000)

        # ── Debug snapshot if still empty ─────────────────────────────────
        if not raw_candidates:
            logger.warning("[warning]All attempts failed — saving full debug snapshot.[/warning]")
            page.screenshot(path=os.path.join(LOGS_DIR, "tokopedia_debug_0_products.png"))
            with open(os.path.join(LOGS_DIR, "tokopedia_debug_dom.html"), "w", encoding="utf-8") as f:
                f.write(page.content())
            logger.warning(
                "[warning]Check logs/tokopedia_debug_0_products.png and "
                "logs/tokopedia_debug_dom.html for clues.[/warning]"
            )

        # ── Save raw candidates for debugging ────────────────────────────────
        raw_json_path = os.path.join(EXPORTS_DIR, "raw_tokopedia.json")
        try:
            with open(raw_json_path, "w", encoding="utf-8") as f:
                json.dump(raw_candidates, f, ensure_ascii=False, indent=2)
            logger.info(f"[info]Raw candidates saved to {raw_json_path}[/info]")
        except Exception as e:
            logger.debug(f"Could not save raw JSON: {e}")

        # ── Clean & build final product list via DataCleaner.clean_batch() ───
        products = DataCleaner.clean_batch(
            raw_candidates[:MAX_PRODUCTS_PER_PLATFORM],
            platform=self.platform,
            category=keyword,
        )
        logger.info(f"[info]clean_batch: {len(raw_candidates)} raw → {len(products)} valid products.[/info]")

        page.screenshot(path=os.path.join(LOGS_DIR, "tokopedia_debug_final.png"))
        page.close()
        logger.info(f"[info]Done. {len(products)} valid products extracted.[/info]")
        return products
