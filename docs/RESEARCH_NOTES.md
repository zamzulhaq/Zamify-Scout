# Research Notes

- Tokopedia lazy-loads images. We must trigger a scroll event to capture `src` or `data-src` properly.
- Shopee often blocks headless browsers without proper headers. We run Playwright in `headless=False` mode by default for these agents to minimize bot detection and provide a visible process to the user.
- Prices need normalization because they come with `Rp` prefixes and sometimes ranges.
