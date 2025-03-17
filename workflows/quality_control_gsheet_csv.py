"""
Quality Control for Google Sheets CSV Data

This script analyzes the Doentes.csv file and provides quality control
information via terminal output. The original file is not modified.
"""
import os
import sys
import pandas as pd
from pathlib import Path
import logging

# Add project root to path for imports
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

# Import project modules
from core.paths import paths


# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("QualityControl")


def find_doentes_csv() -> Path:
    """
    Locate the Doentes.csv file in the spreadsheets directory.
    
    Returns:
        Path: The path to the Doentes.csv file
    """
    # Default location based on project structure
    csv_path = paths.SPREADSHEET_SOURCE / "Doentes.csv"
    
    if not csv_path.exists():
        logger.error(f"Doentes.csv not found at {csv_path}")
        raise FileNotFoundError(f"Could not find Doentes.csv at {csv_path}")
        
    return csv_path


def display_file_info(csv_path: Path, df: pd.DataFrame = None) -> None:
    """
    Display basic information about the CSV file.
    
    Args:
        csv_path: Path to the CSV file
        df: Optional pre-loaded DataFrame
    """
    try:
        # Read the CSV file if not provided
        if df is None:
            df = pd.read_csv(csv_path)
        
        # File information
        print("\n" + "="*80)
        print(f"📊 FILE ANALYSIS: {csv_path.name}")
        print("="*80)
        
        print(f"\n📍 File Location:")
        print(f"   {csv_path.absolute()}")
        
        # Size information
        file_size_kb = os.path.getsize(csv_path) / 1024
        print(f"\n💾 File Size: {file_size_kb:.2f} KB")
        
        # Column information
        print(f"\n📋 Column Information:")
        print(f"   Total Columns: {len(df.columns)}")
        print("\n   Column Names:")
        
        # Format column names in multiple rows for readability
        col_width = max(len(col) for col in df.columns) + 2
        cols_per_row = max(1, 80 // col_width)
        
        for i in range(0, len(df.columns), cols_per_row):
            cols_chunk = df.columns[i:i+cols_per_row]
            print("   " + "  ".join(f"{col:{col_width}}" for col in cols_chunk))
        
        # Row information
        print(f"\n🔢 Row Information:")
        print(f"   Total Rows: {len(df)}")
        
        print("\n" + "="*80 + "\n")
        
    except Exception as e:
        logger.error(f"Error analyzing file: {str(e)}")
        print(f"❌ Error: {str(e)}")


def analyze_id_column(df: pd.DataFrame) -> None:
    """
    Analyze the ID column for missing and duplicate values.
    
    Args:
        df: DataFrame containing the patient data
    """
    print("\n" + "="*80)
    print("🔍 ID COLUMN ANALYSIS")
    print("="*80)
    
    # Check if ID column exists
    if 'ID' not in df.columns:
        print("\n⚠️ Warning: 'ID' column not found in the dataset!")
        return
    
    # 1. Check for missing values in ID column
    missing_ids = df['ID'].isnull()
    missing_count = missing_ids.sum()
    
    print("\n📑 Missing ID Analysis:")
    if missing_count == 0:
        print("   ✅ No missing IDs found")
    else:
        print(f"   ⚠️ Found {missing_count} missing IDs ({missing_count/len(df):.2%} of total records)")
        print("\n   Rows with missing IDs:")
        # Add 2 to row index (1 for 0-indexing, 1 for header row in CSV)
        missing_rows = df[missing_ids].index + 2  
        
        # Show up to 10 missing rows, with ellipsis if more
        if len(missing_rows) <= 10:
            missing_rows_display = ", ".join(str(row) for row in missing_rows)
        else:
            first_rows = ", ".join(str(row) for row in missing_rows[:10])
            missing_rows_display = f"{first_rows}, ... ({len(missing_rows) - 10} more)"
            
        print(f"   {missing_rows_display}")
    
    # 2. Check for duplicate IDs
    # First, exclude rows with missing IDs
    non_null_ids = df.dropna(subset=['ID'])
    
    # Find duplicates
    duplicate_mask = non_null_ids.duplicated(subset=['ID'], keep=False)
    duplicate_count = duplicate_mask.sum()
    
    print("\n🔄 Duplicate ID Analysis:")
    if duplicate_count == 0:
        print("   ✅ No duplicate IDs found")
    else:
        print(f"   ⚠️ Found {duplicate_count} rows with duplicate IDs ({duplicate_count/len(df):.2%} of total records)")
        
        # Group and display duplicate values
        if duplicate_count > 0:
            duplicate_ids = non_null_ids[duplicate_mask]['ID'].unique()
            print(f"\n   Duplicated ID values ({len(duplicate_ids)} unique values):")
            
            # Display each duplicated ID with its row numbers
            for i, dup_id in enumerate(duplicate_ids, 1):
                if i <= 10:  # Limit to first 10 duplicate IDs
                    # Find rows with this ID
                    rows_with_id = df[df['ID'] == dup_id].index + 2  # +2 for 1-indexing and header
                    rows_str = ", ".join(str(row) for row in rows_with_id)
                    print(f"   {i}. ID '{dup_id}' found in rows: {rows_str}")
                
            # If more than 10 duplicate IDs, show ellipsis
            if len(duplicate_ids) > 10:
                print(f"   ... and {len(duplicate_ids) - 10} more duplicated IDs")
    
    print("\n" + "="*80)


def main():
    """
    Main quality control workflow.
    """
    try:
        # Find the CSV file
        csv_path = find_doentes_csv()
        
        # Load the dataframe once to avoid reading multiple times
        df = pd.read_csv(csv_path)
        
        # Display basic file information
        display_file_info(csv_path, df)
        
        # Analyze ID column
        analyze_id_column(df)
        
    except Exception as e:
        logger.error(f"Quality control failed: {str(e)}")
        print(f"❌ Quality control failed: {str(e)}")
        return 1
        
    return 0
        
if __name__ == "__main__":
    main()
