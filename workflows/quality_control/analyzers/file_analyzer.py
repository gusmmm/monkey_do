import os
import pandas as pd
from pathlib import Path
from .base import BaseAnalyzer

class FileAnalyzer(BaseAnalyzer):
    """Analyzer for basic file information."""
    
    def __init__(self, df: pd.DataFrame, file_path: Path):
        """Initialize with dataframe and file path."""
        super().__init__(df)
        self.file_path = file_path
        
    def analyze(self) -> dict:
        """Analyze basic file information."""
        results = {}
        
        # File metadata
        results['file_name'] = self.file_path.name
        results['file_path'] = str(self.file_path.absolute())
        results['file_size_kb'] = os.path.getsize(self.file_path) / 1024
        
        # DataFrame information
        results['row_count'] = len(self.df)
        results['column_count'] = len(self.df.columns)
        results['columns'] = list(self.df.columns)
        
        self.results = results
        return results