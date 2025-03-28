#!/usr/bin/env python3
"""
Quality Control for Google Sheets CSV Data

This script analyzes the Doentes.csv file and provides quality control
information via terminal output. The original file is not modified.
"""
import sys
import os
from pathlib import Path
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

# Import the refactored quality control module
from workflows.quality_control import run_quality_control

def main():
    """
    Parse arguments and run the quality control workflow.
    You can now filter by year in two ways:

    Single Year:
    python workflows/quality_control_gsheet_csv.py --year 25
    This will analyze only records from 2025.

    Year Range:
    python workflows/quality_control_gsheet_csv.py --year 25-20
    This will analyze records from 2020 through 2025.

    With Custom File:
    python workflows/quality_control_gsheet_csv.py --file path/to/file.csv --year 25
    This will analyze only records from 2025 in the specified file.
    """
    parser = argparse.ArgumentParser(description="Run quality control checks on patient data CSV")
    parser.add_argument("--file", "-f", help="Path to CSV file to analyze (default: use standard location)")
    parser.add_argument("--year", "-y", help="Filter by year digits (e.g., '25' for 2025 or '25-20' for 2025-2020 range)")
    
    args = parser.parse_args()
    
    # Run quality control with optional file path and year filter
    if args.file:
        csv_path = Path(args.file)
        if not csv_path.exists():
            print(f"Error: File not found: {args.file}")
            return 1
        return run_quality_control(csv_path, args.year)
    else:
        return run_quality_control(year_filter=args.year)

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)