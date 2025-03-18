# workflows/quality_control/analyzers/base.py
from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any

class BaseAnalyzer(ABC):
    """Base class for all data analyzers."""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize analyzer with dataframe."""
        self.df = df
        self.results = {}
        
    @abstractmethod
    def analyze(self) -> dict:
        """Perform analysis and return results dictionary."""
        pass
        
    def is_applicable(self) -> bool:
        """Check if this analyzer can be applied to the dataframe."""
        return True
    
    def get_results(self) -> Dict[str, Any]:
        """Return the analysis results."""
        return self.results