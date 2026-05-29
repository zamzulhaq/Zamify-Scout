# AI Agent Developer Rules

These rules dictate how AI agents should interact, build, and extend the AI Ecommerce Intelligence project.

## 🧠 Architecture Philosophy
- **"Simple but Scalable"**: Do not overengineer. Build features that solve immediate problems but keep interfaces abstract enough to extend later.
- **Modular Mindset**: Every major feature (Scraping, UI, Export, AI Analysis) must live in its own directory and file. Avoid "monster files".
- **Beginner Friendly**: Keep code readable. Use clear variable names and avoid overly cryptic list comprehensions or lambda functions where a simple loop is more readable.

## 🎨 Coding Style
- Follow PEP 8 standard.
- Use Type Hinting (e.g., `def parse(url: str) -> dict:`).
- Keep functions small and focused on a single responsibility (SOLID principles).

## 🗂️ Naming Conventions
- Directories and files: `snake_case` (e.g., `website_scraper.py`).
- Classes: `PascalCase` (e.g., `DataExporter`).
- Functions and variables: `snake_case` (e.g., `extract_prices`).
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`).

## 📝 Comments & Documentation
- Every file must have a module-level docstring explaining its purpose.
- Every class and non-trivial function must have docstrings.
- Add inline comments for complex logic blocks.

## 🖥️ Terminal UI Standard
- Always use the `rich` library for terminal outputs.
- No standard `print()` for the main user flow.
- Maintain the "startup / AI automation vibe" using progress bars, spinners, and structured panels.
- Colors: `cyan` for primary elements, `green` for success, `red` for errors, `yellow` for warnings.

## 📋 Logging Standard
- Do NOT use `print()` for debugging. Use the central logger (`utils.logger.logger`).
- Log files are saved to `logs/app.log`.
- `INFO`: General progress steps.
- `DEBUG`: Detailed developer information.
- `ERROR`/`WARNING`: Expected and unexpected failures.
