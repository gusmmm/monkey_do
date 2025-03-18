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

def analyze_id_sequences(df: pd.DataFrame) -> None:
    """
    Analyze ID sequences by year.
    
    Args:
        df: DataFrame containing the patient data
    """
    print("\n" + "="*80)
    print("🔢 ID SEQUENCE ANALYSIS BY YEAR")
    print("="*80)
    
    # Check if ID column exists
    if 'ID' not in df.columns:
        print("\n⚠️ Warning: 'ID' column not found in the dataset!")
        return
    
    # Convert ID column to string if it's not already
    df['ID'] = df['ID'].astype(str)
    
    # Create helper columns for analysis
    df_analysis = df.copy()
    
    # Extract year (first 2 digits) and serial (remaining digits)
    df_analysis['year'] = df_analysis['ID'].str[:2].astype(str)
    df_analysis['serial'] = df_analysis['ID'].str[2:].astype(str).str.lstrip('0')
    
    # Convert serial to integer for numerical analysis
    df_analysis['serial_num'] = pd.to_numeric(df_analysis['serial'], errors='coerce')
    
    # Group by year
    year_groups = df_analysis.groupby('year')
    
    print("\n📊 ID Analysis by Year:")
    print("   Year  Count  Min Serial  Max Serial  Missing Values")
    print("   ----  -----  ----------  ----------  --------------")
    
    for year, group in sorted(year_groups, reverse=True):
        # Count entries for this year
        count = len(group)
        
        # Find min and max serial numbers - handle NaN values
        min_serial = group['serial_num'].min()
        max_serial = group['serial_num'].max()
        
        # Skip this year if we have invalid data
        if pd.isna(min_serial) or pd.isna(max_serial):
            print(f"   {year}    {count:4d}  Invalid data - cannot analyze sequence")
            continue
        
        # Convert to integers for analysis
        min_serial_int = int(min_serial)
        max_serial_int = int(max_serial)
        
        # Find missing serials
        existing_serials = set(group['serial_num'].dropna().astype(int))
        expected_serials = set(range(min_serial_int, max_serial_int + 1))
        missing_serials = expected_serials - existing_serials
        
        # Format for display
        if missing_serials:
            if len(missing_serials) <= 5:
                missing_display = ", ".join(str(s) for s in sorted(missing_serials))
            else:
                first_five = ", ".join(str(s) for s in sorted(missing_serials)[:5])
                missing_display = f"{first_five}, ... ({len(missing_serials) - 5} more)"
                
            missing_count = f"{len(missing_serials)} ({len(missing_serials) / (max_serial_int - min_serial_int + 1):.1%})"
        else:
            missing_display = "None"
            missing_count = "0"
        
        # Print row - use proper format specifiers for integers
        print(f"   {year}    {count:4d}  {min_serial_int:10d}  {max_serial_int:10d}  {missing_count}")
        
        # If missing values, show details
        if missing_serials:
            print(f"      Missing in {year}: {missing_display}")
    
    print("\n" + "="*80)


def analyze_id_pattern_consistency(df: pd.DataFrame) -> None:
    """
    Check if ID pattern follows the expected format.
    
    Args:
        df: DataFrame containing the patient data
    """
    print("\n" + "="*80)
    print("🔍 ID PATTERN CONSISTENCY CHECK")
    print("="*80)
    
    # Check if ID column exists
    if 'ID' not in df.columns:
        print("\n⚠️ Warning: 'ID' column not found in the dataset!")
        return
    
    # Convert ID column to string if it's not already
    df['ID'] = df['ID'].astype(str)
    
    # Expected pattern: 2 digits for year + 1-3 digits for serial
    valid_pattern = df['ID'].str.match(r'^\d{3,5}$')
    
    # Check if all values follow the pattern
    if valid_pattern.all():
        print("\n✅ All ID values follow the expected format (YYXXX)")
    else:
        invalid_count = (~valid_pattern).sum()
        print(f"\n⚠️ Found {invalid_count} ID values with unexpected format")
        
        # Display examples of invalid IDs
        invalid_ids = df.loc[~valid_pattern, 'ID']
        if not invalid_ids.empty:
            print("\n   Examples of invalid ID formats:")
            for i, invalid_id in enumerate(invalid_ids.head(5), 1):
                print(f"   {i}. '{invalid_id}' at row {df[df['ID'] == invalid_id].index[0] + 2}")
            if len(invalid_ids) > 5:
                print(f"      ... and {len(invalid_ids) - 5} more")
    
    # Check year patterns
    years = df['ID'].str[:2].unique()
    print(f"\n📅 Years found in ID prefixes: {', '.join(sorted(years))}")
    
    # Check for unusual patterns
    current_year = pd.Timestamp.now().year % 100
    future_years = [year for year in years if int(year) > current_year + 1]
    if future_years:
        print(f"\n⚠️ Warning: Found IDs with future years: {', '.join(future_years)}")
    
    # Check for very old years
    very_old_years = [year for year in years if int(year) < current_year - 10]
    if very_old_years:
        print(f"\n⚠️ Warning: Found IDs with potentially old years: {', '.join(very_old_years)}")
    
    print("\n" + "="*80)


def analyze_admission_dates(df: pd.DataFrame) -> None:
    """
    Analyze the admission dates (data_ent column) for:
    - Missing values
    - Proper date format (dd-mm-yyyy)
    - Year consistency with ID prefix (ID should start with year's last 2 digits)
    
    Args:
        df: DataFrame containing the patient data
    """
    print("\n" + "="*80)
    print("📅 ADMISSION DATE ANALYSIS")
    print("="*80)
    
    # Check if data_ent column exists
    if 'data_ent' not in df.columns:
        print("\n⚠️ Warning: 'data_ent' column not found in the dataset!")
        return
    
    # 1. Check for missing values
    missing_dates = df['data_ent'].isna() | (df['data_ent'] == '')
    missing_count = missing_dates.sum()
    
    print("\n🔍 Missing Date Analysis:")
    if missing_count == 0:
        print("   ✅ No missing admission dates found")
    else:
        print(f"   ⚠️ Found {missing_count} missing admission dates ({missing_count/len(df):.2%} of total records)")
        print("\n   Rows with missing admission dates:")
        missing_rows = df[missing_dates].index + 2  # +2 for 1-indexing and header row
        
        # Show up to 10 missing rows, with ellipsis if more
        if len(missing_rows) <= 10:
            missing_rows_display = ", ".join(str(row) for row in missing_rows)
        else:
            first_rows = ", ".join(str(row) for row in missing_rows[:10])
            missing_rows_display = f"{first_rows}, ... ({len(missing_rows) - 10} more)"
            
        print(f"   {missing_rows_display}")
    
    # 2. Check date format
    print("\n📋 Date Format Analysis:")
    
    # Regular expression for dd-mm-yyyy format (allowing single digits for day/month)
    date_pattern = r'^\d{1,2}-\d{1,2}-\d{4}$'
    
    # Filter rows with non-empty dates
    date_df = df[~missing_dates].copy()
    
    # Check format using regex
    invalid_format = ~date_df['data_ent'].astype(str).str.match(date_pattern)
    invalid_count = invalid_format.sum()
    
    if invalid_count == 0:
        print("   ✅ All dates follow the expected format (dd-mm-yyyy)")
    else:
        print(f"   ⚠️ Found {invalid_count} dates with unexpected format")
        print("\n   Records with invalid date formats:")
        
        invalid_dates = date_df[invalid_format]
        for i, (idx, row) in enumerate(invalid_dates.iterrows(), 1):
            if i <= 10:
                print(f"   {i}. ID '{row['ID']}' has date '{row['data_ent']}' at row {idx + 2}")
            else:
                print(f"      ... and {len(invalid_dates) - 10} more")
                break
    
    # 3. Compare year in date with ID prefix
    print("\n🔄 Year Consistency Check:")
    
    # Try to convert dates to datetime objects
    try:
        # Convert to datetime for valid format dates only
        date_df = date_df[~invalid_format].copy()
        date_df['date_obj'] = pd.to_datetime(date_df['data_ent'], format='%d-%m-%Y', errors='coerce')
        date_df['year'] = date_df['date_obj'].dt.year
        date_df['year_suffix'] = date_df['year'].astype(str).str[-2:]
        date_df['id_prefix'] = date_df['ID'].astype(str).str[:2]
        
        # Find inconsistencies
        inconsistent = date_df['year_suffix'] != date_df['id_prefix']
        inconsistent_count = inconsistent.sum()
        
        if inconsistent_count == 0:
            print("   ✅ All IDs match their admission year (first 2 digits of ID = last 2 digits of year)")
        else:
            print(f"   ⚠️ Found {inconsistent_count} IDs that don't match their admission year")
            print("\n   ID vs. Year inconsistencies:")
            
            inconsistent_rows = date_df[inconsistent]
            for i, (idx, row) in enumerate(inconsistent_rows.iterrows(), 1):
                if i <= 20:  # Show more of these since they're important
                    print(f"   {i}. ID '{row['ID']}' (prefix '{row['id_prefix']}') has date '{row['data_ent']}' (year '{row['year']}') at row {idx + 2}")
                else:
                    print(f"      ... and {len(inconsistent_rows) - 20} more")
                    break
    except Exception as e:
        print(f"   ⚠️ Error analyzing date consistency: {str(e)}")
    
    print("\n" + "="*80)


def main():
    """
    Main quality control workflow.
    """
    try:
        # Find the CSV file
        csv_path = find_doentes_csv()
        
        # Load the dataframe once to avoid reading multiple times
        df = pd.read_csv(csv_path, dtype={'ID': str})  # Force ID column as string
        
        # Display basic file information
        display_file_info(csv_path, df)
        
        # Analyze ID column
        analyze_id_column(df)
        
        # Analyze ID sequences
        analyze_id_sequences(df)
        
        # Analyze ID pattern consistency
        analyze_id_pattern_consistency(df)
        
        # Analyze admission dates
        analyze_admission_dates(df)

        
    except Exception as e:
        logger.error(f"Quality control failed: {str(e)}")
        print(f"❌ Quality control failed: {str(e)}")
        return 1
        
    return 0
        
if __name__ == "__main__":
    main()
