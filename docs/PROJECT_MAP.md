# Project Map

This document outlines the folder structure and the responsibility of each file within the AI Ecommerce Intelligence project.

```text
ecom_ai/
│
├── scraper/                     # Handles data extraction logic
│   ├── website_scraper.py       # Main scraper class managing requests and session state
│   └── parser.py                # Beautifulsoup HTML parsing and data extraction heuristics
│
├── exports/                     # Auto-generated directory where final data files (CSV/JSON/XLSX) are saved
│
├── logs/                        # Auto-generated directory storing application logs
│   └── app.log                  # Central log file
│
├── ui/                          # Handles all user interface components
│   ├── banner.py                # The main title screen/startup branding
│   └── loading.py               # Rich progress bars and spinners
│
├── utils/                       # Shared utilities across the application
│   ├── exporter.py              # Logic to convert Python dicts to CSV/XLSX/JSON formats
│   └── logger.py                # Central logging configuration
│
├── config.py                    # Global configuration variables (Paths, Timeouts, Settings)
├── requirements.txt             # Python dependencies
├── main.py                      # Application entry point, coordinates UI, Scraper, and Exporter
│
└── [Documentation Files]        # README.md, LICENSE, AGENT_RULES.md, etc.
```

## Folder Responsibilities

- **`scraper/`**: Isolated web scraping logic. If we change from `requests` to `playwright` in the future, only this folder changes.
- **`ui/`**: Keeps the terminal aesthetics separate from business logic.
- **`utils/`**: Reusable generic tools (like exporting and logging).
- **`exports/`**: Purely for output files. Gitignored generally.
- **`logs/`**: Diagnostics and debug records.
