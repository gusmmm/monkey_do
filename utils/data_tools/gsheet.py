"""
Google Sheets API integration using gspread.
Handles authentication and sheet operations.
"""
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

# Now we can import from core
from core.paths import paths
from core.config_gsheet import Config  # Import the new Config class

import gspread
from google.oauth2.service_account import Credentials

# Define required scopes for Google Sheets API
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Construct the path to credentials file using paths module
credentials_file = paths.CREDENTIALS / "credentials_gsheet.json"

# Load credentials with proper error handling
try:
    creds = Credentials.from_service_account_file(
        str(credentials_file),
        scopes=scopes
    )
    
    # Initialize gspread client
    gc = gspread.authorize(creds)
    
    print(f"Successfully authenticated using credentials from: {credentials_file}")
    
except FileNotFoundError:
    raise FileNotFoundError(
        f"Credentials file not found at {credentials_file}. "
        "Please make sure the file exists in the credentials directory."
    )
except Exception as e:
    raise Exception(f"Authentication error: {str(e)}")

## Function to open a spreadsheet by its ID
def open_default_spreadsheet():
    """
    Open the default spreadsheet defined in environment variables.
    
    Returns:
        gspread.Spreadsheet: The spreadsheet object
    """
    try:
        sheet_id = Config.get_sheet_id()
        print(f"Opening spreadsheet with ID from environment: {sheet_id}")
        return gc.open_by_key(sheet_id)
    except Exception as e:
        print(f"Error opening spreadsheet: {str(e)}")
        raise

## Function to download a specific sheet as CSV
def download_sheet_as_csv(sheet_name=None, sheet_index=0, spreadsheet_id=None):
    """
    Download a specific sheet as CSV file.
    
    Args:
        sheet_name: Name of the sheet to download (optional)
        sheet_index: Index of the sheet if name not provided (default: 0)
        spreadsheet_id: Optional spreadsheet ID (defaults to .env value)
        
    Returns:
        Path to the saved CSV file
    """
    # Use provided ID or get from environment
    if spreadsheet_id is None:
        spreadsheet_id = Config.get_sheet_id()
    
    spreadsheet = gc.open_by_key(spreadsheet_id)
    
    # Get specific worksheet
    if sheet_name:
        worksheet = spreadsheet.worksheet(sheet_name)
    else:
        worksheet = spreadsheet.get_worksheet(sheet_index)
    
    # Get all data
    data = worksheet.get_all_records()
    
    # Get sheet name if not specified
    if sheet_name is None:
        sheet_name = worksheet.title
        
    # Sanitize filename
    filename = f"{sheet_name.replace(' ', '_')}.csv"
    output_path = paths.SPREADSHEET_SOURCE / filename
    
    # Convert to CSV
    import pandas as pd
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    
    print(f"Data saved to {output_path}")
    return output_path


if __name__ == "__main__":
    # Example usage
    try:
        # Load environment variables
        env_file = paths.ROOT / ".env"
        load_dotenv(dotenv_path=env_file)
        
        # Validate configuration
        Config.validate()
        
        # Open default spreadsheet
        spreadsheet = open_default_spreadsheet()
        
        # Download a specific sheet as CSV
        download_sheet_as_csv(sheet_name="Doentes")
        
    except Exception as e:
        print(f"Error: {str(e)}")