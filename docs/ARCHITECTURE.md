# Architecture

Zamify Sentinel uses a clean, modular architecture:

1. **AI Controller (`ai_controller.py`)**: The entry point that receives user keywords and plans the execution.
2. **Task Router (`task_router.py`)**: Directs the research tasks to specific platform agents.
3. **Browser Agent (`browser_agent.py`)**: Singleton/Manager for the Playwright browser context. Handles headless/headed states.
4. **Platform Agents (`research/*_agent.py`)**: Implement the actual DOM traversal, scrolling, and data extraction for each site.
5. **Market Analyzer (`market_analyzer.py`)**: Aggregates data from all agents to produce pricing insights and trend reports.
6. **UI Layer (`ui/`)**: Decoupled from core logic, uses the `Rich` library to provide real-time visual feedback to the user.
