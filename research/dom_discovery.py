"""
dom_discovery.py

DOM Discovery Mode for Tokopedia (and any SPA e-commerce site).

Instead of relying on hard-coded selectors like [data-testid="divProductWrapper"],
this module scans all visible DOM elements containing price/sold signals,
then analyses repeated parent structures to auto-detect the real product card container.

Outputs
-------
logs/rp_candidates.txt      – raw outerHTML of every matched element + parents
logs/product_candidates.json – structured candidate list
logs/best_selector.txt      – best candidate CSS selector + confidence score
"""

import json
import os
from collections import Counter
from playwright.sync_api import Page
from config import LOGS_DIR
from utils.logger import logger


# ─────────────────────────────────────────────
# JavaScript: collect every element containing
# "Rp" or "terjual" in its visible text, then
# walk up the tree two levels and record each
# ancestor's tag+class signature.
# ─────────────────────────────────────────────
_JS_DISCOVER = """
() => {
    const SIGNALS = ["Rp", "terjual"];

    function classSignature(el) {
        if (!el) return "NULL";
        const tag = el.tagName.toLowerCase();
        const cls = (el.getAttribute("class") || "").trim().split(/\\s+/).slice(0, 4).join(".");
        const testid = el.getAttribute("data-testid") || "";
        return testid ? `${tag}[data-testid="${testid}"]` : (cls ? `${tag}.${cls}` : tag);
    }

    function outerShort(el) {
        if (!el) return "";
        const raw = el.outerHTML || "";
        return raw.length > 800 ? raw.slice(0, 800) + "…" : raw;
    }

    function isVisible(el) {
        const r = el.getBoundingClientRect();
        return r.width > 0 && r.height > 0;
    }

    const results = [];
    const allEls = Array.from(document.querySelectorAll("*"));

    for (const el of allEls) {
        // Only direct text nodes, not the whole page body
        if (el.children.length > 6) continue;
        const text = (el.innerText || el.textContent || "").trim();
        const matched = SIGNALS.some(s => text.includes(s));
        if (!matched || !isVisible(el)) continue;

        const parent = el.parentElement;
        const grandparent = parent ? parent.parentElement : null;

        results.push({
            tag: el.tagName.toLowerCase(),
            text_preview: text.slice(0, 120),
            self_sig: classSignature(el),
            parent_sig: classSignature(parent),
            grandparent_sig: classSignature(grandparent),
            self_html: outerShort(el),
            parent_html: outerShort(parent),
            grandparent_html: outerShort(grandparent),
        });

        if (results.length >= 200) break;   // cap to avoid huge dumps
    }
    return results;
}
"""

# ─────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────

def discover(page: Page) -> dict:
    """
    Run DOM discovery on the current page.

    Returns a dict with:
        candidates      list of raw candidate objects
        best_selector   best CSS selector string (or None)
        confidence      float 0-1
        container_count int
    """
    logger.info("[info]DOM Discovery Mode: scanning live DOM for price/sold signals...[/info]")

    try:
        candidates: list = page.evaluate(_JS_DISCOVER)
    except Exception as e:
        logger.error(f"[error]DOM discovery JS failed: {e}[/error]")
        return {"candidates": [], "best_selector": None, "confidence": 0.0, "container_count": 0}

    logger.info(f"[info]DOM Discovery: {len(candidates)} raw signal elements found.[/info]")

    # ── Save raw text dump ───────────────────
    txt_path = os.path.join(LOGS_DIR, "rp_candidates.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        for i, c in enumerate(candidates):
            f.write(f"\n{'='*60}\n")
            f.write(f"[{i}] SIGNAL TEXT: {c['text_preview']}\n")
            f.write(f"  SELF     : {c['self_sig']}\n")
            f.write(f"  PARENT   : {c['parent_sig']}\n")
            f.write(f"  GRAND    : {c['grandparent_sig']}\n")
            f.write(f"\n  -- SELF HTML --\n{c['self_html']}\n")
            f.write(f"\n  -- PARENT HTML --\n{c['parent_html']}\n")
            f.write(f"\n  -- GRANDPARENT HTML --\n{c['grandparent_html']}\n")
    logger.info(f"[info]Saved raw candidates to {txt_path}[/info]")

    # ── Save structured JSON ─────────────────
    json_path = os.path.join(LOGS_DIR, "product_candidates.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)
    logger.info(f"[info]Saved structured candidates to {json_path}[/info]")

    # ── Detect repeated parent structures ────
    # We vote on grandparent signature because product cards are usually
    # siblings inside a common grid container.
    parent_counter: Counter = Counter()
    grandparent_counter: Counter = Counter()
    for c in candidates:
        if c["parent_sig"] and c["parent_sig"] != "NULL":
            parent_counter[c["parent_sig"]] += 1
        if c["grandparent_sig"] and c["grandparent_sig"] != "NULL":
            grandparent_counter[c["grandparent_sig"]] += 1

    logger.info(f"[info]Top-5 parent signatures: {parent_counter.most_common(5)}[/info]")
    logger.info(f"[info]Top-5 grandparent signatures: {grandparent_counter.most_common(5)}[/info]")

    # ── Pick best candidate ──────────────────
    best_selector = None
    container_count = 0
    confidence = 0.0

    # Prefer parent-level: most repeated = most likely the card container
    if parent_counter:
        best_sig, best_count = parent_counter.most_common(1)[0]
        total = len(candidates)
        confidence = round(min(best_count / max(total, 1), 1.0), 2)
        container_count = best_count

        # Convert signature back to a usable CSS selector string
        best_selector = _sig_to_selector(best_sig)
        logger.info(
            f"[info]Best candidate selector: '{best_selector}' "
            f"| count={container_count} | confidence={confidence}[/info]"
        )

    # ── Save best selector report ────────────
    report_path = os.path.join(LOGS_DIR, "best_selector.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("DOM DISCOVERY REPORT\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Best Selector  : {best_selector}\n")
        f.write(f"Confidence     : {confidence * 100:.1f}%\n")
        f.write(f"Container Count: {container_count}\n\n")
        f.write("Top Parent Signatures:\n")
        for sig, cnt in parent_counter.most_common(10):
            f.write(f"  {cnt:4d}x  {sig}\n")
        f.write("\nTop Grandparent Signatures:\n")
        for sig, cnt in grandparent_counter.most_common(10):
            f.write(f"  {cnt:4d}x  {sig}\n")
    logger.info(f"[info]Best-selector report saved to {report_path}[/info]")

    return {
        "candidates": candidates,
        "best_selector": best_selector,
        "confidence": confidence,
        "container_count": container_count,
        "parent_counter": dict(parent_counter.most_common(10)),
        "grandparent_counter": dict(grandparent_counter.most_common(10)),
    }


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _sig_to_selector(sig: str) -> str:
    """
    Convert a class-signature string like:
        div.a.b.c.d
    or
        div[data-testid="xyz"]
    into a usable CSS selector.
    """
    if not sig or sig == "NULL":
        return "*"
    # Already looks like an attribute selector
    if "[" in sig:
        return sig
    # tag.class1.class2 → tag.class1.class2 (CSS selector already)
    return sig
