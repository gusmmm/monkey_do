"""
Google Sheets API Integration Module

This module provides a class-based interface for interacting with Google Sheets
using the gspread library. It handles authentication, data retrieval, and
file export operations.

Technical decisions:
- Class-based design for better encapsulation and state management
- Type hints for improved code clarity and IDE support
- Explicit error handling for better debugging
- Lazy initialization of connections to improve performance
- Configurable output formats and paths
"""
import sys
import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
import pandas as pd

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))

# Import project modules
from core.paths import paths
from core.config_gsheet import Config

# Third-party imports
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("GoogleSheetsClient")


class GoogleSheetsClient:
    """
    Client for interacting with Google Sheets API.
    
    This class handles authentication, sheet operations, and data export
    functionality for Google Sheets integration.
    
    Attributes:
        credentials_file (Path): Path to the service account credentials file
        scopes (List[str]): OAuth scopes required for API access
        client (gspread.Client): Authenticated gspread client
    """
    
    def __init__(self, credentials_file: Optional[Union[str, Path]] = None) -> None:
        """
        Initialize the Google Sheets client with credentials.
        
        Args:
            credentials_file: Path to service account JSON file.
                             If None, uses default path from paths.CREDENTIALS.
                             
        Raises:
            FileNotFoundError: If credentials file doesn't exist
            Exception: For authentication errors
        """
        # Set up logging
        self.logger = logger
        
        # Set credentials file path
        if credentials_file is None:
            self.credentials_file = paths.CREDENTIALS / "credentials_gsheet.json"
        else:
            self.credentials_file = Path(credentials_file)
            
        # Define required API scopes
        self.scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        
        # Initialize client
        self.client = self._authenticate()
        
    def _authenticate(self) -> gspread.Client:
        """
        Authenticate with Google Sheets API.
        
        Returns:
            gspread.Client: Authenticated gspread client
            
        Raises:
            FileNotFoundError: If credentials file doesn't exist
            Exception: For authentication errors
        """
        try:
            self.logger.info(f"Authenticating with credentials from: {self.credentials_file}")
            
            creds = Credentials.from_service_account_file(
                str(self.credentials_file),
                scopes=self.scopes
            )
            
            client = gspread.authorize(creds)
            self.logger.info("Authentication successful")
            
            return client
            
        except FileNotFoundError:
            self.logger.error(f"Credentials file not found at {self.credentials_file}")
            raise FileNotFoundError(
                f"Credentials file not found at {self.credentials_file}. "
                "Please make sure the file exists in the credentials directory."
            )
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            raise Exception(f"Authentication error: {str(e)}")
    
    def open_spreadsheet(self, spreadsheet_id: Optional[str] = None) -> gspread.Spreadsheet:
        """
        Open a Google Spreadsheet by its ID.
        
        Args:
            spreadsheet_id: The ID from the spreadsheet URL.
                           If None, uses the ID from Config.
                           
        Returns:
            gspread.Spreadsheet: The opened spreadsheet object
            
        Raises:
            ValueError: If spreadsheet_id is not provided and not in Config
            Exception: For spreadsheet access errors
        """
        try:
            # Use provided ID or get from environment
            if spreadsheet_id is None:
                spreadsheet_id = Config.get_sheet_id()
                self.logger.info(f"Using spreadsheet ID from environment: {spreadsheet_id}")
            
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            self.logger.info(f"Opened spreadsheet: '{spreadsheet.title}'")
            
            return spreadsheet
            
        except Exception as e:
            self.logger.error(f"Error opening spreadsheet: {str(e)}")
            raise
    
    def list_worksheets(self, spreadsheet_id: Optional[str] = None) -> List[str]:
        """
        List all worksheets in a spreadsheet.
        
        Args:
            spreadsheet_id: The ID from the spreadsheet URL.
                           If None, uses the ID from Config.
                           
        Returns:
            List[str]: List of worksheet titles
        """
        spreadsheet = self.open_spreadsheet(spreadsheet_id)
        worksheets = [sheet.title for sheet in spreadsheet.worksheets()]
        
        self.logger.info(f"Found {len(worksheets)} worksheets: {', '.join(worksheets)}")
        return worksheets
    
    def get_worksheet_data(self, 
                          sheet_name: Optional[str] = None, 
                          sheet_index: int = 0,
                          spreadsheet_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get data from a specific worksheet as a list of dictionaries.
        
        Args:
            sheet_name: Name of the worksheet to access
            sheet_index: Index of the worksheet if name not provided (default: 0)
            spreadsheet_id: The spreadsheet ID (if None, uses Config value)
            
        Returns:
            List[Dict[str, Any]]: List of rows as dictionaries with column headers as keys
            
        Raises:
            gspread.exceptions.WorksheetNotFound: If sheet_name doesn't exist
            IndexError: If sheet_index is out of range
        """
        spreadsheet = self.open_spreadsheet(spreadsheet_id)
        
        # Get the specified worksheet
        try:
            if sheet_name:
                worksheet = spreadsheet.worksheet(sheet_name)
                self.logger.info(f"Accessed worksheet '{sheet_name}'")
            else:
                worksheet = spreadsheet.get_worksheet(sheet_index)
                self.logger.info(f"Accessed worksheet at index {sheet_index}: '{worksheet.title}'")
        
            # Get all records (list of dictionaries)
            data = worksheet.get_all_records()
            self.logger.info(f"Retrieved {len(data)} rows of data")
            
            return data
            
        except gspread.exceptions.WorksheetNotFound:
            self.logger.error(f"Worksheet '{sheet_name}' not found")
            raise
        except IndexError:
            self.logger.error(f"Worksheet index {sheet_index} is out of range")
            raise
    
    def get_worksheet_as_dataframe(self, 
                                  sheet_name: Optional[str] = None, 
                                  sheet_index: int = 0,
                                  spreadsheet_id: Optional[str] = None) -> pd.DataFrame:
        """
        Get worksheet data as a pandas DataFrame.
        
        Args:
            sheet_name: Name of the worksheet to access
            sheet_index: Index of the worksheet if name not provided (default: 0)
            spreadsheet_id: The spreadsheet ID (if None, uses Config value)
            
        Returns:
            pandas.DataFrame: DataFrame containing the worksheet data
        """
        data = self.get_worksheet_data(sheet_name, sheet_index, spreadsheet_id)
        return pd.DataFrame(data)
    
    def download_worksheet(self, 
                          sheet_name: Optional[str] = None, 
                          sheet_index: int = 0,
                          spreadsheet_id: Optional[str] = None,
                          output_format: str = "csv",
                          output_dir: Optional[Path] = None,
                          filename: Optional[str] = None) -> Path:
        """
        Download worksheet data to a file in the specified format.
        
        Args:
            sheet_name: Name of the worksheet to download
            sheet_index: Index of the worksheet if name not provided (default: 0)
            spreadsheet_id: The spreadsheet ID (if None, uses Config value)
            output_format: File format - "csv", "excel", or "json" (default: "csv")
            output_dir: Directory to save the file (default: paths.SPREADSHEET_SOURCE)
            filename: Custom filename without extension (default: worksheet name)
            
        Returns:
            Path: Path to the downloaded file
            
        Raises:
            ValueError: For unsupported output formats
        """
        # Get data as DataFrame
        df = self.get_worksheet_as_dataframe(sheet_name, sheet_index, spreadsheet_id)
        
        if df.empty:
            self.logger.warning("No data found in worksheet")
            return None
        
        # Determine output directory
        if output_dir is None:
            output_dir = paths.SPREADSHEET_SOURCE
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get worksheet name if not specified (for filename)
        if sheet_name is None:
            spreadsheet = self.open_spreadsheet(spreadsheet_id)
            sheet_name = spreadsheet.get_worksheet(sheet_index).title
        
        # Use custom filename or create one from sheet name
        if filename is None:
            # Sanitize sheet name for filename
            filename = sheet_name.replace(' ', '_').replace('/', '_')
        
        # Construct full output path with appropriate extension
        if output_format.lower() == "csv":
            output_path = output_dir / f"{filename}.csv"
            df.to_csv(output_path, index=False)
        elif output_format.lower() == "excel":
            output_path = output_dir / f"{filename}.xlsx"
            df.to_excel(output_path, index=False)
        elif output_format.lower() == "json":
            output_path = output_dir / f"{filename}.json"
            df.to_json(output_path, orient='records', indent=2)
        else:
            raise ValueError(f"Unsupported output format: {output_format}. "
                            "Supported formats: csv, excel, json")
        
        self.logger.info(f"Data saved to {output_path}")
        return output_path
    
    def download_all_worksheets(self, 
                               spreadsheet_id: Optional[str] = None,
                               output_format: str = "csv") -> Dict[str, Path]:
        """
        Download all worksheets from a spreadsheet.
        
        Args:
            spreadsheet_id: The spreadsheet ID (if None, uses Config value)
            output_format: File format - "csv", "excel", or "json" (default: "csv")
            
        Returns:
            Dict[str, Path]: Dictionary mapping worksheet names to output file paths
        """
        # Get list of all worksheets
        worksheet_names = self.list_worksheets(spreadsheet_id)
        
        # Download each worksheet
        results = {}
        for name in worksheet_names:
            try:
                output_path = self.download_worksheet(
                    sheet_name=name,
                    spreadsheet_id=spreadsheet_id,
                    output_format=output_format
                )
                results[name] = output_path
            except Exception as e:
                self.logger.error(f"Error downloading worksheet '{name}': {str(e)}")
                # Continue with other worksheets even if one fails
        
        return results

    def interactive_worksheet_download(self, 
                                      spreadsheet_id: Optional[str] = None,
                                      output_format: str = "csv") -> Optional[Path]:
        """
        Interactive interface for selecting and downloading worksheets with intelligent updating.
        
        This method guides the user through:
        1. Connecting to the Google spreadsheet
        2. Listing available worksheets
        3. Selecting which worksheet to work with
        4. Determining if data needs updating
        5. Downloading only when necessary
        
        Args:
            spreadsheet_id: ID of the spreadsheet (if None, uses Config)
            output_format: Format to save data in ("csv", "excel", or "json")
            
        Returns:
            Path: Path to the downloaded file if successful, otherwise None
        """
        try:
            # Connect to spreadsheet
            self.logger.info("Connecting to Google Spreadsheet...")
            spreadsheet = self.open_spreadsheet(spreadsheet_id)
            print(f"\n📊 Connected to: '{spreadsheet.title}'")
            
            # Get available worksheets
            worksheet_names = self.list_worksheets(spreadsheet_id)
            if not worksheet_names:
                print("❌ No worksheets found in this spreadsheet.")
                return None
            
            # Display worksheet selection menu
            print("\n🔍 Available worksheets:")
            for i, name in enumerate(worksheet_names, 1):
                print(f"  {i}. {name}")
            
            # Get user selection
            while True:
                try:
                    selection = input("\n👉 Enter worksheet number to download: ")
                    index = int(selection) - 1
                    if 0 <= index < len(worksheet_names):
                        selected_worksheet = worksheet_names[index]
                        break
                    else:
                        print(f"❌ Please enter a number between 1 and {len(worksheet_names)}")
                except ValueError:
                    print("❌ Please enter a valid number")
            
            print(f"\n✅ Selected: '{selected_worksheet}'")
            
            # Determine output path
            filename = selected_worksheet.replace(' ', '_').replace('/', '_')
            output_path = paths.SPREADSHEET_SOURCE / f"{filename}.{output_format}"
            
            # Check if file already exists
            file_exists = output_path.exists()
            
            if file_exists:
                print(f"\n🔄 Found existing file: {output_path}")
                
                # Compare with current data
                try:
                    should_download = self._check_for_updates(
                        output_path, selected_worksheet, spreadsheet_id)
                except Exception as e:
                    self.logger.error(f"Error comparing files: {str(e)}")
                    print(f"⚠️ Could not compare files: {str(e)}")
                    should_download = self._prompt_download_confirmation()
            else:
                print("\n🆕 No existing file found. Will download fresh data.")
                should_download = True
            
            # Download if needed
            if should_download:
                print(f"\n⬇️ Downloading '{selected_worksheet}' to {output_path}")
                result_path = self.download_worksheet(
                    sheet_name=selected_worksheet,
                    spreadsheet_id=spreadsheet_id,
                    output_format=output_format,
                    filename=filename
                )
                print(f"✅ Download complete: {result_path}")
                return result_path
            else:
                print("\n⏭️ Skipping download as requested.")
                return output_path if file_exists else None
                
        except Exception as e:
            self.logger.error(f"Error in interactive download: {str(e)}")
            print(f"\n❌ Error: {str(e)}")
            return None
            
    def _check_for_updates(self, 
                          file_path: Path, 
                          worksheet_name: str,
                          spreadsheet_id: Optional[str] = None) -> bool:
        """
        Compare local CSV file with current Google Sheet data to check for differences.
        
        Args:
            file_path: Path to the local CSV file
            worksheet_name: Name of the worksheet to compare
            spreadsheet_id: ID of the spreadsheet (if None, uses Config)
            
        Returns:
            bool: True if updates are needed, False if data is identical
        """
        self.logger.info(f"Checking for updates between {file_path} and {worksheet_name}")
        
        # Load local data
        try:
            local_df = pd.read_csv(file_path)
            local_records = local_df.to_dict('records')
        except Exception as e:
            self.logger.error(f"Error reading local file: {str(e)}")
            print(f"⚠️ Error reading local file - will download fresh data")
            return True
        
        # Get current sheet data
        current_data = self.get_worksheet_data(worksheet_name, spreadsheet_id=spreadsheet_id)
        
        # Quick check: row count
        if len(local_records) != len(current_data):
            diff = len(current_data) - len(local_records)
            print(f"🆕 Found {abs(diff)} {'new' if diff > 0 else 'fewer'} rows in the Google Sheet")
            return self._prompt_download_confirmation()
        
        # Check for changes in existing data
        try:
            # Convert to sets of tuples for comparison (need hashable type)
            # First, ensure both datasets have the same columns
            all_keys = set()
            for record in local_records + current_data:
                all_keys.update(record.keys())
                
            # Convert to comparable format
            def record_to_hashable(record, keys):
                return tuple((k, record.get(k, None)) for k in sorted(keys))
                
            local_set = {record_to_hashable(r, all_keys) for r in local_records}
            current_set = {record_to_hashable(r, all_keys) for r in current_data}
            
            # Find differences
            new_records = current_set - local_set
            removed_records = local_set - current_set
            
            if new_records or removed_records:
                print(f"🔄 Found {len(new_records)} new and {len(removed_records)} removed items")
                for i, record in enumerate(new_records, 1):
                    if i <= 3:  # Show only first 3 differences
                        print(f"  ➕ New: {dict(record)}")
                    elif i == 4:
                        print(f"  ... and {len(new_records) - 3} more changes")
                        break
                return self._prompt_download_confirmation()
            else:
                print("✅ Local file is up to date with Google Sheet")
                return self._prompt_download_confirmation(default=False)
                
        except Exception as e:
            self.logger.error(f"Error comparing data: {str(e)}")
            print(f"⚠️ Could not properly compare data: {str(e)}")
            return self._prompt_download_confirmation()
            
    def _prompt_download_confirmation(self, default: bool = True) -> bool:
        """
        Ask user to confirm download.
        
        Args:
            default: Default answer if user just presses Enter
            
        Returns:
            bool: True if user confirms, False otherwise
        """
        default_text = "Y/n" if default else "y/N"
        while True:
            response = input(f"\n❓ Download/update the file? [{default_text}]: ").strip().lower()
            
            if not response:  # Empty response, use default
                return default
                
            if response in ('y', 'yes'):
                return True
            elif response in ('n', 'no'):
                return False
            else:
                print("Please answer with 'y' or 'n'")


def main():
    """
    Example usage when script is run directly.
    """
    try:
        # Load environment variables
        env_file = paths.ROOT / ".env"
        load_dotenv(dotenv_path=env_file)
        
        # Initialize client
        gs_client = GoogleSheetsClient()
        
        # Use the interactive function
        print("\n🌟 Interactive Google Sheets Downloader 🌟\n")
        gs_client.interactive_worksheet_download()
            
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()