"""
Demonstration script for Google Sheets integration.

This script shows how to use the GoogleSheetsClient class
to interact with Google Sheets data in different ways.
"""
import sys
from pathlib import Path
1
# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.data_tools import GoogleSheetsClient
from core.config_gsheet import Config
from core.paths import paths

def show_available_worksheets():
    """Show all available worksheets in the default spreadsheet."""
    client = GoogleSheetsClient()
    sheets = client.list_worksheets()
    
    print("Available worksheets:")
    for i, sheet in enumerate(sheets, 1):
        print(f"  {i}. {sheet}")
    
    return sheets

def download_specific_worksheet(sheet_name):
    """Download a specific worksheet by name."""
    client = GoogleSheetsClient()
    path = client.download_worksheet(sheet_name=sheet_name)
    print(f"Downloaded to: {path}")
    
def download_all_worksheets():
    """Download all worksheets from the default spreadsheet."""
    client = GoogleSheetsClient()
    results = client.download_all_worksheets()
    
    print(f"\nDownloaded {len(results)} worksheets:")
    for sheet, path in results.items():
        print(f"  - {sheet}: {path}")

def interactive_mode():
    """Run the interactive worksheet downloader."""
    client = GoogleSheetsClient()
    client.interactive_worksheet_download()

def main():
    """Main function with command selection menu."""
    print("🌟 Google Sheets Demo 🌟\n")
    print("1. Show available worksheets")
    print("2. Download specific worksheet")
    print("3. Download all worksheets")
    print("4. Interactive mode")
    print("5. Exit")
    
    choice = input("\nEnter your choice (1-5): ")
    
    if choice == '1':
        show_available_worksheets()
    elif choice == '2':
        sheets = show_available_worksheets()
        if sheets:
            idx = input(f"\nEnter worksheet number (1-{len(sheets)}): ")
            try:
                sheet_name = sheets[int(idx) - 1]
                download_specific_worksheet(sheet_name)
            except (ValueError, IndexError):
                print("Invalid selection")
    elif choice == '3':
        download_all_worksheets()
    elif choice == '4':
        interactive_mode()
    elif choice == '5':
        print("Goodbye!")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()