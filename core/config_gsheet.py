"""
Configuration management for environment variables and secrets.
Handles loading from .env file and provides validation.
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Import paths after defining paths module location
from core.paths import paths

# Load environment variables from .env file
env_file = paths.ROOT / ".env"
load_dotenv(dotenv_path=env_file)

class Config:
    """Configuration values loaded from environment variables with validation."""
    
    # Google Sheets settings
    GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration values are set."""
        missing = []
        
        if not cls.GOOGLE_SHEET_ID:
            missing.append("GOOGLE_SHEET_ID")
            
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}. "
                f"Please add them to your .env file at {env_file}"
            )
            
    @classmethod
    def get_sheet_id(cls):
        """Get the Google Sheet ID with validation."""
        if not cls.GOOGLE_SHEET_ID:
            raise ValueError("GOOGLE_SHEET_ID not set in environment variables")
        return cls.GOOGLE_SHEET_ID


# You can uncomment this to validate config on import
# Config.validate()