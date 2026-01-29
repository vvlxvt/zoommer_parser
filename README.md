# Zoommer Parser

## Description
CLI tool that fetches Zoommer.ge products by category and brand and stores them in SQLite. It keeps only id, name, price and updates records when prices change.

## Features
- Pick category and enter brand via prompts
- Fetch products from Zoommer.ge API
- Save to SQLite (zoommer.db) with SQLAlchemy
- Update existing items when price changes
- Console notice on price change

## Tech Stack
- Python 3.10+
- requests
- SQLAlchemy
- SQLite

## How to Run
1. Create and activate a virtual environment (Windows PowerShell):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

## Tech Stack
- Language: [Python 3.10+]
- Framework/Libraries: [e.g., requests, beautifulsoup4, pandas]
- Tooling: [e.g., pip, venv]
- Database/Storage: [e.g., SQLite/CSV/None]
- Other: [e.g., Docker]

## How to Run
Follow one of the options below.

### Option A: Local environment
1. Ensure prerequisites are installed:
   - Python 3.10+
   - pip
2. (Recommended) Create and activate a virtual environment:
   - Windows (PowerShell):
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment (if applicable):
   - Create a `.env` file or set environment variables.
   - Example:
     ```env
     # SAMPLE
     APP_ENV=development
     LOG_LEVEL=INFO
     ```
5. Run the application:
   ```bash
   python main.py
   ```

### Option B: Docker (optional)
1. Build the image:
   ```bash
   docker build -t zoommerparser:latest .
   ```
2. Run the container:
   ```bash
   docker run --rm -it \
     -e APP_ENV=development \
     zoommerparser:latest
   ```

## Notes
- Replace placeholders in this README with your actual app details.
- If the entry point is not `main.py`, update the run command accordingly.
- Add any gotchas, known issues, or tips here.

