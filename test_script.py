"""
Test script to verify module imports are working correctly.
"""
# Test imports
from core.paths import paths
from core.config_gsheet import Config
from utils.data_tools import GoogleSheetsClient

def main():
    """Test module imports and basic functionality."""
    print("Testing module imports:")
    print(f"- paths: {paths}")
    print(f"- Config: {Config}")
    print(f"- GoogleSheetsClient: {GoogleSheetsClient}")
    
    # Test sheet ID retrieval (will raise error if not set)
    try:
        sheet_id = Config.get_sheet_id()
        print(f"- Sheet ID: {sheet_id}")
    except ValueError as e:
        print(f"- Sheet ID error: {e}")
    
    # Test client creation
    try:
        client = GoogleSheetsClient()
        print(f"- Client created successfully")
    except Exception as e:
        print(f"- Client creation error: {e}")

if __name__ == "__main__":
    main()