# System Architecture

## Architecture Philosophy
The system is built on a **Modular Monolith** concept. It is a single Python application but strictly divided into independent domains (UI, Scraping, Exporting). This prevents "spaghetti code" and makes it easy to replace a module later (e.g., swapping Terminal UI for Web UI).

## Data Flow

```text
User Input -> [ main.py ] -> delegates to modules
                 │
                 ├── 1. [ ui.banner & ui.loading ] -> Renders visual state
                 │
                 ├── 2. [ scraper.website_scraper ] -> Fetches HTML via HTTP
                 │         └── delegates to [ scraper.parser ] -> Extracts Product Data (List of Dicts)
                 │
                 ├── 3. [ utils.exporter ] -> Takes Product Data -> Writes to disk (CSV/XLSX)
                 │
                 └── 4. [ utils.logger ] -> Records actions to logs/app.log throughout the process
```

## Future Scalability
To accommodate V2 and beyond:
- **AI Module**: A new `ai/` folder will be created to handle Gemini API communication. It will act as a middleware between the scraper and exporter, enriching the scraped data before saving.
- **Database**: When we move to V3 (Trends), the exporter module can be extended to implement database connection (e.g., PostgreSQL/SQLite) via SQLAlchemy.
