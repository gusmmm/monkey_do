"""
Google Sheets API integration using gspread.
Handles authentication and sheet operations.
"""
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

# Now we can import from core
from core.paths import paths

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