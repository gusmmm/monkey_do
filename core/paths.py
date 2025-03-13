"""
Central path configuration for the Monkey Do project.
Defines and manages all project paths in a centralized way.
"""
from pathlib import Path


class ProjectPaths:
    """
    Manages all project paths consistently throughout the application.
    Ensures all required directories exist upon initialization.
    """
    
    def __init__(self):
        # Root directory - works regardless of where code is executed from
        self.ROOT = Path(__file__).parent.parent.absolute()
        
        # Main directories
        self.CORE = self.ROOT / "core"
        self.UTILS = self.ROOT / "utils"
        self.DATA = self.ROOT / "data"
        self.FRONTEND = self.ROOT / "frontend"
        self.BACKEND = self.ROOT / "backend"
        
        # Add credentials directory
        self.CREDENTIALS = self.ROOT / "credentials"
        
        # Utils subdirectories based on project requirements
        self.DATA_TOOLS = self.UTILS / "data_tools"
        
        # Data directories
        self.DATA_SOURCE = self.DATA / "source"
        self.PDF_SOURCE = self.DATA_SOURCE / "pdf"
        self.SPREADSHEET_SOURCE = self.DATA_SOURCE / "spreadsheets"
        
        # Processed data directories
        self.DATA_PROCESSED = self.DATA / "processed"
        self.MARKDOWN = self.DATA_PROCESSED / "markdown"
        self.JSON = self.DATA_PROCESSED / "json"
        
        # Create all directories
        self._create_directories()
    
    def _create_directories(self):
        """Create all defined directories if they don't exist."""
        directories = [
            self.UTILS, self.DATA_TOOLS, 
            self.DATA, self.FRONTEND, self.BACKEND,
            self.DATA_SOURCE, self.PDF_SOURCE, self.SPREADSHEET_SOURCE,
            self.DATA_PROCESSED, self.MARKDOWN, self.JSON,
            self.CREDENTIALS,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
    def __str__(self):
        """Return a string representation of all paths for debugging."""
        return f"Project root at: {self.ROOT}"


# Create a singleton instance to be imported by other modules
paths = ProjectPaths()