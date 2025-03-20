"""
Command-line interface for patient data processing.

This module provides a user-friendly command-line interface for
converting patient data from CSV to JSON.
"""
from pathlib import Path
from typing import Optional

from .processor import PatientDataProcessor

def process_patients_to_json():
    """
    Entry point function to process patient data from CSV to JSON.
    
    This function creates a PatientDataProcessor and runs the conversion process.
    """
    print("\n" + "="*80)
    print("🏥 PATIENT DATA PROCESSOR - CSV TO JSON 🏥".center(80))
    print("="*80 + "\n")
    
    print("This tool will process patient records from the Doentes.csv file")
    print("and convert them to individual JSON files ready for MongoDB import.\n")
    
    # Get year filter choice
    print("Choose processing scope:")
    print("  1. Process all records")
    print("  2. Process records from a specific year (e.g., 25 for 2025)")
    print("  3. Process records from a year range (e.g., 25-20 for 2025 to 2020)")
    print("\nNote: Years are determined by the first 2 digits of the ID column.")
    
    year_filter = None
    
    while True:
        choice = input("\n👉 Enter your choice [1-3]: ").strip()
        
        if choice == "1":
            break
            
        elif choice == "2":
            year = input("👉 Enter year (e.g., 25 for 2025): ").strip()
            if year.isdigit() and len(year) <= 2:
                year_filter = year
                break
            else:
                print("❌ Invalid year format. Please enter a 1-2 digit number (e.g., 25)")
                
        elif choice == "3":
            year_range = input("👉 Enter year range (e.g., 25-20 for 2025 to 2020): ").strip()
            if "-" in year_range:
                parts = year_range.split("-")
                if len(parts) == 2 and all(part.isdigit() and len(part) <= 2 for part in parts):
                    year_filter = year_range
                    break
            print("❌ Invalid year range format. Please use format YY-YY (e.g., 25-20)")
            
        else:
            print("❌ Please enter a number between 1 and 3")
    
    # Create processor with filter
    processor = PatientDataProcessor(year_filter=year_filter)
    
    # Show filter information
    print(f"\n📂 Source CSV: {processor.csv_path}")
    print(f"📂 Output directory: {processor.json_dir}")
    
    if year_filter:
        if "-" in year_filter:
            start, end = year_filter.split("-")
            print(f"🔍 Filter: Records from years 20{end} to 20{start}")
        else:
            print(f"🔍 Filter: Records from year 20{year_filter} only")
    else:
        print("🔍 Filter: All records")
    
    # Generate preview of first record that would be processed
    print("\nGenerating preview of first record to be processed...")
    preview = processor.process_csv(preview_only=True)
    
    if not preview:
        print("\n❌ No records match the specified filter or an error occurred.")
        return
        
    print("\n📝 PREVIEW OF FIRST RECORD:")
    print("-" * 40)
    print(preview)
    print("-" * 40)
    
    # Confirm before proceeding
    response = input("\nDoes this look correct? Proceed with processing? [Y/n]: ").lower()
    if response in ['', 'y', 'yes']:
        print("\nStarting conversion process...")
        success = processor.process_csv()
        
        if success:
            print("\n✅ Processing complete!")
            print(f"Successfully processed {processor.processed_records} patient records")
            if processor.error_records > 0:
                print(f"⚠️ Encountered {processor.error_records} errors during processing")
            print(f"\nJSON files are saved in: {processor.json_dir}")
        else:
            print("\n❌ Processing failed. Check the logs for details.")
    else:
        print("\n❌ Operation cancelled by user.")