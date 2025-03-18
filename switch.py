#!/usr/bin/env python3
"""
Interactive Terminal Menu for Monkey Do Project

This module provides a user-friendly terminal interface for accessing
the main functionalities of the Monkey Do project.
"""
import os
import sys
import time
from pathlib import Path
import argparse
from typing import Optional, Callable

# Add project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Import project modules
from core.paths import paths
from utils.data_tools.gsheet import GoogleSheetsClient
from workflows.quality_control import run_quality_control


def clear_screen() -> None:
    """Clear the terminal screen based on operating system."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title: str) -> None:
    """Print a formatted header with the given title."""
    terminal_width = os.get_terminal_size().columns
    print("\n" + "=" * terminal_width)
    print(f"{title:^{terminal_width}}")
    print("=" * terminal_width + "\n")


def print_menu(title: str, options: dict) -> None:
    """
    Print a formatted menu with the given title and options.
    
    Args:
        title: The menu title
        options: Dictionary mapping option numbers to their descriptions
    """
    clear_screen()
    print_header(title)
    
    for key, value in options.items():
        print(f"  {key}. {value}")
    
    print("\n" + "-" * os.get_terminal_size().columns)


def get_user_choice(max_choice: int) -> int:
    """
    Get a valid numerical choice from the user.
    
    Args:
        max_choice: The maximum allowed choice number
        
    Returns:
        int: The user's choice
    """
    while True:
        try:
            choice = input("\n👉 Enter your choice: ")
            choice_num = int(choice)
            
            if 1 <= choice_num <= max_choice:
                return choice_num
            else:
                print(f"❌ Please enter a number between 1 and {max_choice}")
        except ValueError:
            print("❌ Please enter a valid number")


def worksheet_download_menu() -> None:
    """Handle the interactive Google Sheets download functionality."""
    clear_screen()
    print_header("📊 Google Sheets Download")
    
    print("This option allows you to interactively download worksheets from Google Sheets.\n")
    print("You'll be able to:")
    print("  • Connect to a Google Spreadsheet")
    print("  • View available worksheets")
    print("  • Select which worksheet to download")
    print("  • Compare with existing files to check for changes")
    print("  • Download the selected worksheet")
    
    proceed = input("\n👉 Ready to proceed? [Y/n]: ").lower()
    if proceed in ['', 'y', 'yes']:
        try:
            # Initialize client
            gs_client = GoogleSheetsClient()
            
            # Use the interactive function
            gs_client.interactive_worksheet_download()
            
            input("\n✅ Process completed. Press Enter to return to the main menu...")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            input("\nPress Enter to return to the main menu...")
    else:
        print("\n⏭️ Returning to main menu...")
        time.sleep(1)


def quality_control_menu() -> None:
    """Handle the quality control workflow with options for year filtering."""
    clear_screen()
    print_header("🔍 Quality Control Analysis")
    
    print("This option runs quality control checks on the patient data CSV file.\n")
    print("You can analyze:")
    print("  • The entire dataset")
    print("  • Records from a specific year (e.g., 25 for 2025)")
    print("  • Records from a range of years (e.g., 25-20 for 2025 to 2020)")
    print("\nNote: Years are determined by the first 2 digits of the ID column.")
    
    # Menu options
    options = {
        "1": "Analyze entire dataset",
        "2": "Analyze single year",
        "3": "Analyze year range",
        "4": "Return to main menu"
    }
    
    for key, value in options.items():
        print(f"\n  {key}. {value}")
    
    while True:
        try:
            choice = input("\n👉 Enter your choice: ")
            choice_num = int(choice)
            
            if choice_num == 1:
                # Analyze entire dataset
                print("\n📊 Running quality control on the entire dataset...")
                run_quality_control()
                break
            elif choice_num == 2:
                # Analyze single year
                year = input("\n👉 Enter year (e.g., 25 for 2025): ").strip()
                if year.isdigit() and len(year) == 2:
                    print(f"\n📊 Running quality control for year 20{year}...")
                    run_quality_control(year_filter=year)
                    break
                else:
                    print("❌ Please enter a valid 2-digit year (e.g., 25 for 2025)")
            elif choice_num == 3:
                # Analyze year range
                year_range = input("\n👉 Enter year range (e.g., 25-20 for 2025 to 2020): ").strip()
                if "-" in year_range:
                    start_year, end_year = year_range.split("-")
                    if (start_year.isdigit() and end_year.isdigit() and 
                        len(start_year) == 2 and len(end_year) == 2):
                        print(f"\n📊 Running quality control for years 20{end_year} to 20{start_year}...")
                        run_quality_control(year_filter=year_range)
                        break
                    else:
                        print("❌ Please enter a valid year range (e.g., 25-20)")
                else:
                    print("❌ Please enter a valid year range with format YY-YY (e.g., 25-20)")
            elif choice_num == 4:
                # Return to main menu
                print("\n⏭️ Returning to main menu...")
                time.sleep(1)
                return
            else:
                print(f"❌ Please enter a number between 1 and {len(options)}")
        except ValueError:
            print("❌ Please enter a valid number")
    
    input("\n✅ Quality control completed. Press Enter to return to the main menu...")


def main_menu() -> None:
    """Display main menu and handle user selection."""
    menu_options = {
        "1": "Download Google Sheets Data",
        "2": "Run Quality Control Analysis",
        "3": "Exit"
    }
    
    # Define menu to function mapping
    menu_actions = {
        1: worksheet_download_menu,
        2: quality_control_menu,
        3: lambda: sys.exit(0)  # Exit action
    }
    
    while True:
        print_menu("🐵 MONKEY DO - MAIN MENU 🐵", menu_options)
        choice = get_user_choice(len(menu_options))
        
        # Call the corresponding function
        menu_actions[choice]()


def main() -> None:
    """Main entry point."""
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Program terminated by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()