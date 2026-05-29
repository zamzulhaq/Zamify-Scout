# Research Notes

This document contains brainstorming and findings for future development.

## Competitor Analysis Strategies
- Many modern ecommerce sites use React/Vue (Single Page Applications). Simple HTML parsing might fail.
- **Future Solution**: Need to implement Playwright or Selenium in the `scraper/` module for dynamic sites.

## AI Possibilities (Gemini Integration)
- **Categorization**: Pass product titles to Gemini to return a standardized category.
- **Sentiment Analysis**: Scrape reviews later and use AI to determine product satisfaction.
- **Margin Prediction**: Provide Gemini with the retail price and ask it to estimate wholesale costs based on historical knowledge.

## Supplier Strategy
- To find suppliers, we can take the product image URL and use Reverse Image Search APIs, or search AliExpress/1688 using the extracted product title.

## Future Tech Stack Additions
- **FastAPI**: For turning this tool into a microservice.
- **Streamlit**: Easiest way to build the V3 web dashboard without a full frontend team.
- **Celery/Redis**: For scheduling automated daily scrapes.
