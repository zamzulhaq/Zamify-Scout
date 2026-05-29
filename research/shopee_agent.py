"""
research/shopee_agent.py

Shopee product scraper using text-based render extraction.
Same strategy as Tokopedia agent:
  1. Find price leaf nodes (text matching "Rp")
  2. Walk UP DOM to find product container
  3. Extract name, price, sold, image, link from container text
  4. Deduplicate by (name, price)

No CSS class dependencies — fully pattern-based.
"""

from playwright.sync_api import BrowserContext
import random
import os
import json
from urllib.parse import quote
from config import MAX_PRODUCTS_PER_PLATFORM, SCROLL_PAUSE_TIME, LOGS_DIR, EXPORTS_DIR
from utils.logger import logger
from utils.cleaner import DataCleaner

# ─────────────────────────────────────────────────────────────────────────────
# JavaScript: Text-based product extraction for Shopee.
#
# Shopee uses "Rp" for prices and "terjual" / "RB" for sold count.
# It also uses dynamic class names — so we rely purely on text patterns.
# ─────────────────────────────────────────────────────────────────────────────
_JS_SHOPEE_EXTRACT = """
() => {
    const RpPattern     = /Rp\\s?[\\d.,]+/;
    const SoldPattern   = /[\\d.,]+\\s*(RB\\s*\\+?\\s*|rb\\s*\\+?\\s*)?terjual/i;
    const RatingPattern = /[1-5](?:[.,]\\d)?/;

    function getText(el) {
        return (el ? (el.innerText || el.textContent || "") : "").trim();
    }
    function isVisible(el) {
        try {
            const r = el.getBoundingClientRect();
            return r.width > 0 && r.height > 0;
        } catch(e) { return false; }
    }

    // ── Step 1: find all leaf-ish elements displaying a price ─────────
    const allEls = Array.from(document.querySelectorAll("*"));
    const priceNodes = [];
    for (const el of allEls) {
        if (el.children.length > 4) continue;
        const t = getText(el);
        if (RpPattern.test(t) && t.length < 60 && isVisible(el)) {
            priceNodes.push(el);
        }
    }

    // ── Step 2-3: walk up DOM, find container, extract fields ─────────
    const seenKey = new Set();
    const products = [];

    for (const priceEl of priceNodes) {
        let container = priceEl.parentElement;
        let foundContainer = null;

        for (let level = 0; level < 6; level++) {
            if (!container) break;
            const cText = getText(container);
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
        // Shopee often shows rating as a bare number near a star icon
        const ratingMatch = cText.match(RatingPattern);
        const rating_raw = ratingMatch ? ratingMatch[0].trim() : "";

        // ── Name: longest line that isn't price/sold/rating ────────────
        const lines = cText.split(/\\n+/).map(l => l.trim()).filter(l => l.length > 5);
        let name = "";
        for (const line of lines) {
            if (RpPattern.test(line)) continue;
            if (SoldPattern.test(line)) continue;
            if (/^[1-5][.,]\\d$/.test(line)) continue;
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
        // Shopee store names live near the product card — heuristic search
        const storeEl = foundContainer.querySelector(
            '[class*="shop"], [class*="store"], [class*="seller"], [data-sqe*="shop"]'
        );
        const store = storeEl ? getText(storeEl) : "";

        products.push({ name, price_raw, sold_raw, rating_raw, store, link, image });

        if (products.length >= 120) break;
    }

    return products;
}
"""


class ShopeeAgent:
    def __init__(self, context: BrowserContext):
        self.context = context
        self.platform = "Shopee"

    # ── Helpers ───────────────────────────────────────────────────────────

    def _human_scroll(self, page, rounds: int = 14):
        """Gradual human-like scrolling to trigger lazy-loaded content."""
        for _ in range(rounds):
            step = random.randint(250, 650)
            page.mouse.wheel(0, step)
            page.wait_for_timeout(random.uniform(0.4, SCROLL_PAUSE_TIME) * 1000)
        # Scroll back up slightly
        page.mouse.wheel(0, -random.randint(200, 500))
        page.wait_for_timeout(1500)

    def _soft_wait(self, page):
        """Non-blocking waits for price text to appear."""
        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except Exception as e:
            logger.debug(f"Shopee networkidle soft-timeout: {e}")
        try:
            page.wait_for_function(
                "() => document.body.innerText.includes('Rp')",
                timeout=8000
            )
            logger.debug("Shopee: 'Rp' text confirmed visible.")
        except Exception as e:
            logger.debug(f"Shopee soft wait for 'Rp' timed out: {e}")

    def _live_debug(self, page):
        """Print live DOM stats for debugging."""
        try:
            rp_count = page.evaluate(
                "() => Array.from(document.querySelectorAll('*'))"
                ".filter(el => el.children.length < 4 && (el.innerText||'').includes('Rp')).length"
            )
            logger.info(f"[info]Shopee live DOM: {rp_count} 'Rp' nodes visible[/info]")
        except Exception as e:
            logger.debug(f"Shopee live debug failed: {e}")

    def _run_js_extraction(self, page) -> list:
        """Run the text-based JavaScript extraction."""
        try:
            raw = page.evaluate(_JS_SHOPEE_EXTRACT)
            return raw if isinstance(raw, list) else []
        except Exception as e:
            logger.error(f"[error]Shopee JS extraction error: {e}[/error]")
            return []

    # ── Main ──────────────────────────────────────────────────────────────

    def search(self, keyword: str):
        page = self.context.new_page()
        
        # ── Step 1 & 2: Safe Navigation & Login Flow ───────────────────────
        logger.info("[info]Shopee: Navigating to homepage for safe initialization...[/info]")
        try:
            page.goto("https://shopee.co.id", wait_until="domcontentloaded", timeout=60000)
            logger.info("[warning]Shopee: Pausing for manual login/verification. Please complete it in the browser window.[/warning]")
            logger.info("[warning]Click 'Resume' in the Playwright Inspector once you are ready.[/warning]")
            page.pause()
            
            # ── Step 3: Human Behavior Simulation ─────────────────────────
            logger.info("[info]Shopee: Resuming... Simulating human behavior...[/info]")
            page.wait_for_timeout(5000)
            page.mouse.move(200, 300)
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(3000)
            
            search_url = f"https://shopee.co.id/search?keyword={quote(keyword)}"
            logger.info(f"[info]Navigating to search: {search_url}[/info]")
            page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(4000)  # Shopee SPA hydration is slower
        except Exception as e:
            logger.error(f"[error]Shopee page navigation error: {e}[/error]")
            return {"platform": "shopee", "status": "blocked", "data": []}

        # ── Scroll + retry loop ───────────────────────────────────────────
        raw_candidates = []
        max_attempts = 3

        try:
            for attempt in range(max_attempts):
                logger.info(f"[info]Shopee attempt {attempt+1}/{max_attempts}: scrolling + detecting...[/info]")
                page.screenshot(path=os.path.join(LOGS_DIR, f"shopee_{attempt}_before.png"))

                self._human_scroll(page, rounds=14)
                self._soft_wait(page)

                page.screenshot(path=os.path.join(LOGS_DIR, f"shopee_{attempt}_after.png"))
                self._live_debug(page)

                raw_candidates = self._run_js_extraction(page)
                logger.info(f"[info]Shopee attempt {attempt+1}: {len(raw_candidates)} raw candidates[/info]")

                if raw_candidates:
                    first = raw_candidates[0]
                    logger.info(
                        f"[info]Shopee sample → name: '{first.get('name','')[:60]}' | "
                        f"price: '{first.get('price_raw','')}' | "
                        f"sold: '{first.get('sold_raw','')}'[/info]"
                    )
                    break
                else:
                    logger.warning(f"[warning]Shopee: 0 candidates on attempt {attempt+1}. Retrying...[/warning]")
                    if attempt < max_attempts - 1:
                        page.wait_for_timeout(3000)
        except Exception as e:
            logger.error(f"[error]Shopee extraction loop failed: {e}[/error]")

        # ── Debug snapshot if empty ───────────────────────────────────────
        if not raw_candidates:
            logger.warning("[warning]Shopee: all attempts failed — saving debug snapshot and returning blocked status.[/warning]")
            page.screenshot(path=os.path.join(LOGS_DIR, "shopee_debug_0_products.png"))
            with open(os.path.join(LOGS_DIR, "shopee_debug_dom.html"), "w", encoding="utf-8") as f:
                f.write(page.content())
            page.close()
            return {"platform": "shopee", "status": "blocked", "data": []}

        # ── Save raw candidates ───────────────────────────────────────────
        raw_json_path = os.path.join(EXPORTS_DIR, "raw_shopee.json")
        try:
            with open(raw_json_path, "w", encoding="utf-8") as f:
                json.dump(raw_candidates, f, ensure_ascii=False, indent=2)
            logger.info(f"[info]Shopee raw candidates saved to {raw_json_path}[/info]")
        except Exception as e:
            logger.debug(f"Could not save Shopee raw JSON: {e}")

        # ── Clean & build final product list ──────────────────────────────
        products = DataCleaner.clean_batch(
            raw_candidates[:MAX_PRODUCTS_PER_PLATFORM],
            platform=self.platform.lower(),
            category=keyword,
        )
        logger.info(f"[info]Shopee clean_batch: {len(raw_candidates)} raw → {len(products)} valid[/info]")

        page.screenshot(path=os.path.join(LOGS_DIR, "shopee_debug_final.png"))
        page.close()
        logger.info(f"[info]Shopee done. {len(products)} valid products extracted.[/info]")
        
        return products
