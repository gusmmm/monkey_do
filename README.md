# Monkey Do

A full-stack data management and processing system.

## Project Overview

Monkey Do is a system for extracting, processing, and managing data from various sources including Google Sheets and PDF files.

## Dependencies

This project uses `uv` for dependency management, which provides faster, more reliable package installation than traditional pip.

### Installing Dependencies

```bash
# Install uv if not already installed
pip install uv

# Install project dependencies
uv pip install -r requirements.txt
```

### Adding New Dependencies

```bash
# Add a new package
uv pip install package_name

# Update requirements.txt
uv pip freeze > requirements.txt
```

## Project Structure

```
monkey_do/
├── core/                # Core project components
│   ├── __init__.py
│   └── paths.py         # Centralized path management
├── data/                # Data storage
│   ├── source/          # Original data sources
│   │   ├── pdf/
│   │   └── spreadsheets/
│   └── processed/       # Processed data
│       ├── markdown/
│       └── json/
├── utils/               # Utility modules
│   └── data_tools/      # Data processing tools
│       └── google_sheets.py
├── credentials/         # API credentials (gitignored)
├── frontend/            # React JS frontend
├── backend/             # FastAPI backend
├── scripts/             # Utility scripts
└── main.py             # Main application entry point
```

## Usage

Run the main application:

```bash
python main.py
```

Download data from Google Sheets:

```bash
python scripts/download_sheet_data.py YOUR_SPREADSHEET_ID
```

## Development

This project follows modular design principles with clear separation of concerns. Key components:

1. **Path Management**: Centralized in `core/paths.py`
2. **Data Tools**: Utilities for data processing in `utils/data_tools/`
3. **Backend API**: FastAPI implementation in `backend/`
4. **Frontend**: React JS application in `frontend/`