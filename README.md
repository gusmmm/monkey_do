# Monkey Do

A full-stack data management and processing system with focus on healthcare data quality control.

## Project Overview

Monkey Do is a system for extracting, processing, and managing data from various sources including Google Sheets and PDF files. The current implementation focuses on:

1. **Data Extraction**: Download data from Google Sheets with an interactive selection interface
2. **Quality Control**: Comprehensive analysis of patient data with customizable year filters
3. **Reporting**: Generate beautiful console output and markdown reports of quality control findings

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
│   ├── processed/       # Processed data
│   │   ├── markdown/
│   │   └── json/
│   └── reports/         # Quality control reports
├── utils/               # Utility modules
│   └── data_tools/      # Data processing tools
│       └── gsheet.py    # Google Sheets client
├── workflows/           # Workflow modules
│   └── quality_control/ # Quality control analysis
│       ├── analyzers/   # Data analysis modules
│       ├── reporters/   # Output formatting
│       ├── utils/       # Helper utilities 
│       ├── __init__.py
│       ├── main.py      # Quality control workflow
│       └── report_generator.py # Markdown report generation
├── credentials/         # API credentials (gitignored)
├── frontend/            # React JS frontend (future)
├── backend/             # FastAPI backend (future)
├── instructions/        # Project guidelines
├── switch.py           # Interactive terminal menu
└── main.py             # Main application entry point
```

## Usage

### Interactive Menu

The easiest way to use Monkey Do is through its interactive terminal menu:

```bash
python switch.py
```

This will present a user-friendly menu with the following options:

1. **Download Google Sheets Data** - Interactive interface to select and download worksheets
2. **Run Quality Control Analysis** - Analyze patient data with customizable year filters
3. **Exit** - Exit the application

### Quality Control Analysis

The quality control system analyzes patient data for various quality issues:

1. **File Analysis** - Basic information about the data file
2. **ID Analysis** - Checks for missing, duplicate, or malformed IDs
3. **Date Analysis** - Validates admission, discharge, and birth dates
4. **Simple Column Analysis** - Checks for missing values and constraints in common fields

#### Year Filtering

You can filter the quality control analysis by year:

- **Full Dataset**: Analyze all records
- **Single Year**: Filter by a specific year (e.g., 25 for 2025)
- **Year Range**: Filter by a range of years (e.g., 25-20 for 2025 to 2020)

#### Generated Reports

Quality control analysis generates:

1. **Console Output** - Formatted terminal output with color-coded findings
2. **Markdown Report** - Comprehensive report saved to `data/reports/` with timestamp

### Command Line Usage

Direct command line usage is also supported:

```bash
# Run quality control on all data
python workflows/quality_control_gsheet_csv.py

# Run quality control on data from 2025
python workflows/quality_control_gsheet_csv.py --year 25

# Run quality control on data from 2020-2025
python workflows/quality_control_gsheet_csv.py --year 25-20

# Run quality control on a specific file
python workflows/quality_control_gsheet_csv.py --file path/to/file.csv
```

## Development

This project follows modular design principles with clear separation of concerns:

1. **Path Management**: Centralized in `core/paths.py`
2. **Data Tools**: Utilities for data processing in `utils/data_tools/`
3. **Workflows**: Process implementations in `workflows/`
4. **Analyzers**: Modular data quality analyzers
5. **Reporters**: Output formatting for different mediums

### Adding New Features

To add new functionality:

1. Create appropriate modules following the existing structure
2. Update the `switch.py` menu to include your new functionality
3. Ensure proper error handling and user feedback
4. Follow the project guidelines in `instructions/`

## Future Enhancements

Planned enhancements include:

1. **PDF Data Extraction** - Extract and process data from PDF files
2. **Backend API** - FastAPI implementation for data access
3. **Frontend Interface** - React JS application for visualization
4. **Additional Analysis Types** - Expand quality control capabilities

## License

[Your License Information Here]