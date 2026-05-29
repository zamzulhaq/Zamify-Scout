# AI Ecommerce Intelligence

> An AI-powered automation tool for ecommerce competitor research, product scraping, and margin analysis.

![AI Ecommerce Intelligence Placeholder](https://via.placeholder.com/800x400?text=AI+Ecommerce+Intelligence)

## 🚀 Overview
AI Ecommerce Intelligence is a modern, modular, and scalable command-line tool built with Python and Playwright. It acts as an autonomous browser agent that navigates websites like a human to research competitors and extract product data.

## ✨ Key Features (V2 - Playwright Edition)
- **Autonomous Browser Agent**: Uses Playwright to render JS and simulate human scrolling.
- **Professional Terminal UI**: Rich and colorful terminal interface.
- **Dynamic Scraping**: Interacts with the DOM directly to find categories and products.
- **Data Export**: Support for CSV, XLSX, and JSON formats.
- **Clean Architecture**: Modular structure separated into core agent logic and parsing logic.

## 🗺️ Roadmap
We follow an iterative development approach. See [ROADMAP.md](ROADMAP.md) for future plans, including Gemini AI integration.

## 💻 Tech Stack
- **Python 3.10+**
- `playwright` (Browser Automation)
- `pandas` & `openpyxl` (Data Processing & Export)
- `rich` (Terminal UI)

## 🛠️ Installation

1. **Clone the repository** (or download the files)
2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 How to Run

Execute the main script from the terminal:
```bash
python main.py
```

Follow the on-screen prompts to input the target website, number of items, and export format.

## 📁 Project Structure
See [PROJECT_MAP.md](PROJECT_MAP.md) for a detailed breakdown of the folder structure and architecture mindset.

## 🤝 Future Plans
We are building a scalable ecosystem. The next versions will include AI analysis, intelligent product categorization, and supplier matching. Check out [RESEARCH_NOTES.md](RESEARCH_NOTES.md) for our brainstorming process.

---
*Created by Zamify*
