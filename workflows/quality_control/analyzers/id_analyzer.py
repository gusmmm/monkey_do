# workflows/quality_control/analyzers/id_analyzer.py
import pandas as pd
from .base import BaseAnalyzer
from typing import Dict, Any, List, Set

class IDAnalyzer(BaseAnalyzer):
    """Analyzer for the ID column."""
    
    def is_applicable(self) -> bool:
        """Check if ID column exists in the dataframe."""
        return 'ID' in self.df.columns
    
    def analyze(self) -> dict:
        """Analyze ID column for issues."""
        results = {}
        
        # Run all analysis functions
        results['missing'] = self._analyze_missing_ids()
        results['duplicates'] = self._analyze_duplicate_ids()
        results['sequences'] = self._analyze_id_sequences()
        results['pattern'] = self._analyze_id_pattern_consistency()
        
        self.results = results
        return results
    
    def _analyze_missing_ids(self) -> dict:
        """Check for missing values in ID column."""
        missing_ids = self.df['ID'].isnull()
        missing_count = missing_ids.sum()
        
        result = {
            'count': int(missing_count),
            'percentage': float(missing_count / len(self.df) if len(self.df) > 0 else 0),
            'rows': self.df[missing_ids].index.tolist() if missing_count > 0 else []
        }
        
        return result
    
    def _analyze_duplicate_ids(self) -> dict:
        """Check for duplicate IDs."""
        # First, exclude rows with missing IDs
        non_null_ids = self.df.dropna(subset=['ID'])
        
        # Find duplicates
        duplicate_mask = non_null_ids.duplicated(subset=['ID'], keep=False)
        duplicate_count = duplicate_mask.sum()
        
        result = {
            'count': int(duplicate_count),
            'percentage': float(duplicate_count / len(self.df) if len(self.df) > 0 else 0),
            'duplicates': []
        }
        
        # Collect details about duplicates
        if duplicate_count > 0:
            duplicate_ids = non_null_ids[duplicate_mask]['ID'].unique()
            
            for dup_id in duplicate_ids:
                rows_with_id = self.df[self.df['ID'] == dup_id].index.tolist()
                result['duplicates'].append({
                    'id': dup_id,
                    'rows': rows_with_id
                })
                
        return result
        
    def _analyze_id_sequences(self) -> dict:
        """Analyze ID sequences by year."""
        # Convert ID column to string if it's not already
        self.df['ID'] = self.df['ID'].astype(str)
        
        # Create helper columns for analysis
        df_analysis = self.df.copy()
        
        # Extract year (first 2 digits) and serial (remaining digits)
        df_analysis['year'] = df_analysis['ID'].str[:2].astype(str)
        df_analysis['serial'] = df_analysis['ID'].str[2:].astype(str).str.lstrip('0')
        
        # Convert serial to integer for numerical analysis
        df_analysis['serial_num'] = pd.to_numeric(df_analysis['serial'], errors='coerce')
        
        # Group by year
        year_groups = df_analysis.groupby('year')
        
        result = {
            'years': []
        }
        
        # Analyze each year
        for year, group in sorted(year_groups):
            year_result = {
                'year': year,
                'count': len(group)
            }
            
            # Find min and max serial numbers - handle NaN values
            min_serial = group['serial_num'].min()
            max_serial = group['serial_num'].max()
            
            # Skip this year if we have invalid data
            if pd.isna(min_serial) or pd.isna(max_serial):
                year_result['valid'] = False
                year_result['error'] = "Invalid data - cannot analyze sequence"
                result['years'].append(year_result)
                continue
            
            # Convert to integers for analysis
            min_serial_int = int(min_serial)
            max_serial_int = int(max_serial)
            
            # Find missing serials
            existing_serials = set(group['serial_num'].dropna().astype(int))
            expected_serials = set(range(min_serial_int, max_serial_int + 1))
            missing_serials = expected_serials - existing_serials
            
            year_result.update({
                'valid': True,
                'min_serial': min_serial_int,
                'max_serial': max_serial_int,
                'missing_count': len(missing_serials),
                'missing_percentage': len(missing_serials) / (max_serial_int - min_serial_int + 1) if max_serial_int >= min_serial_int else 0,
                'missing_serials': sorted(list(missing_serials))
            })
            
            result['years'].append(year_result)
        
        return result
    
    def _analyze_id_pattern_consistency(self) -> dict:
        """Check if ID pattern follows the expected format."""
        # Convert ID column to string if it's not already
        self.df['ID'] = self.df['ID'].astype(str)
        
        # Expected pattern: 2 digits for year + 1-3 digits for serial
        valid_pattern = self.df['ID'].str.match(r'^\d{3,5}$')
        invalid_count = (~valid_pattern).sum()
        
        result = {
            'valid_count': valid_pattern.sum(),
            'invalid_count': invalid_count,
            'invalid_examples': []
        }
        
        # Get examples of invalid IDs
        if invalid_count > 0:
            invalid_ids = self.df.loc[~valid_pattern, 'ID']
            for i, invalid_id in enumerate(invalid_ids):
                if i < 5:  # Limit to 5 examples
                    result['invalid_examples'].append({
                        'id': invalid_id,
                        'row': self.df[self.df['ID'] == invalid_id].index[0]
                    })
        
        # Check year patterns
        years = self.df['ID'].str[:2].unique().tolist()
        result['years'] = sorted(years)
        
        # Check for unusual patterns
        current_year = pd.Timestamp.now().year % 100
        future_years = [year for year in years if int(year) > current_year + 1]
        very_old_years = [year for year in years if int(year) < current_year - 10]
        
        result['future_years'] = future_years
        result['very_old_years'] = very_old_years
        
        return result