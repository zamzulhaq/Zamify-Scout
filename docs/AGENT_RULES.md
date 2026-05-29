# Agent Rules

1. **No Hardcoding**: Selectors must be robust. Do not hardcode specific item IDs.
2. **Graceful Failures**: If a single product fails to parse, log the error and continue. Do not crash the entire run.
3. **Realistic Browsing**: Use `headless=False` where needed. Implement human-like delays and scrolling to ensure data loads (especially lazy-loaded images).
4. **Data Integrity**: Always clean prices (remove text, keep numeric ranges) and text (remove excess whitespace) before exporting.
