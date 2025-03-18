import pandas as pd
import numpy as np
from datetime import datetime
from .base import BaseAnalyzer

class AdmissionDateAnalyzer(BaseAnalyzer):
    """Analyzer for admission dates (data_ent column)."""
    
    def is_applicable(self) -> bool:
        """Check if data_ent column exists in the dataframe."""
        return 'data_ent' in self.df.columns
    
    def analyze(self) -> dict:
        """Analyze admission date column for issues."""
        results = {}
        
        # Run all analysis functions
        results['missing'] = self._analyze_missing_dates()
        results['format'] = self._analyze_date_format()
        results['year_consistency'] = self._analyze_year_consistency()
        
        self.results = results
        return results
    
    def _analyze_missing_dates(self) -> dict:
        """Check for missing values in admission date column."""
        missing_dates = self.df['data_ent'].isna() | (self.df['data_ent'] == '')
        missing_count = missing_dates.sum()
        
        result = {
            'count': int(missing_count),
            'percentage': float(missing_count / len(self.df) if len(self.df) > 0 else 0),
            'rows': self.df[missing_dates].index.tolist() if missing_count > 0 else []
        }
        
        return result
    
    def _analyze_date_format(self) -> dict:
        """Check if dates follow dd-mm-yyyy format."""
        # Regular expression for dd-mm-yyyy format (allowing single digits for day/month)
        date_pattern = r'^\d{1,2}-\d{1,2}-\d{4}$'
        
        # Filter rows with non-empty dates
        non_empty = ~(self.df['data_ent'].isna() | (self.df['data_ent'] == ''))
        date_df = self.df[non_empty].copy()
        
        # Check format using regex
        valid_format = date_df['data_ent'].astype(str).str.match(date_pattern)
        invalid_format = ~valid_format
        invalid_count = invalid_format.sum()
        
        result = {
            'valid_count': valid_format.sum(),
            'invalid_count': int(invalid_count),
            'invalid_examples': []
        }
        
        # Collect examples of invalid formats
        if invalid_count > 0:
            invalid_dates = date_df[invalid_format]
            for i, (idx, row) in enumerate(invalid_dates.iterrows()):
                if i < 10:  # Limit to 10 examples
                    result['invalid_examples'].append({
                        'id': row['ID'],
                        'date': row['data_ent'],
                        'row': idx
                    })
        
        return result
    
    def _analyze_year_consistency(self) -> dict:
        """Compare year in admission date with ID prefix."""
        result = {
            'consistent_count': 0,
            'inconsistent_count': 0,
            'inconsistent_examples': []
        }
        
        try:
            # Regular expression for dd-mm-yyyy format
            date_pattern = r'^\d{1,2}-\d{1,2}-\d{4}$'
            
            # Filter rows with non-empty dates and IDs
            valid_rows = (
                ~(self.df['data_ent'].isna() | (self.df['data_ent'] == '')) & 
                ~(self.df['ID'].isna() | (self.df['ID'] == ''))
            )
            
            if valid_rows.sum() == 0:
                return result
                
            # Further filter for valid date formats
            date_df = self.df[valid_rows].copy()
            valid_format = date_df['data_ent'].astype(str).str.match(date_pattern)
            date_df = date_df[valid_format].copy()
            
            if len(date_df) == 0:
                return result
            
            # Convert to datetime
            date_df['date_obj'] = pd.to_datetime(date_df['data_ent'], format='%d-%m-%Y', errors='coerce')
            
            # Extract year components
            date_df['year'] = date_df['date_obj'].dt.year
            date_df['year_suffix'] = date_df['year'].astype(str).str[-2:]
            date_df['id_prefix'] = date_df['ID'].astype(str).str[:2]
            
            # Find inconsistencies
            consistent = date_df['year_suffix'] == date_df['id_prefix']
            inconsistent = ~consistent
            
            result['consistent_count'] = int(consistent.sum())
            result['inconsistent_count'] = int(inconsistent.sum())
            
            # Collect examples of inconsistencies
            if inconsistent.sum() > 0:
                inconsistent_rows = date_df[inconsistent]
                for i, (idx, row) in enumerate(inconsistent_rows.iterrows()):
                    if i < 20:  # Collect up to 20 examples
                        result['inconsistent_examples'].append({
                            'id': row['ID'],
                            'id_prefix': row['id_prefix'],
                            'date': row['data_ent'],
                            'year': int(row['year']),
                            'row': idx
                        })
            
        except Exception as e:
            result['error'] = str(e)
            
        return result