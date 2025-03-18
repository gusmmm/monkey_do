import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional
from .base import BaseAnalyzer

class DischargeDateAnalyzer(BaseAnalyzer):
    """Analyzer for discharge dates (data_alta column)."""
    
    def is_applicable(self) -> bool:
        """Check if data_alta column exists in the dataframe."""
        return 'data_alta' in self.df.columns
    
    def analyze(self) -> dict:
        """Analyze discharge date column for issues."""
        results = {}
        
        # Check for admission date column which is required for some analyses
        has_admission_dates = 'data_ent' in self.df.columns
        
        # Run analysis functions
        results['format'] = self._analyze_date_format()
        
        if has_admission_dates:
            results['chronology'] = self._analyze_chronology()
            results['duration'] = self._analyze_duration_stats()
        else:
            results['chronology'] = {'error': 'Admission date column not found'}
            results['duration'] = {'error': 'Admission date column not found'}
        
        self.results = results
        return results
    
    def _analyze_date_format(self) -> dict:
        """Check if discharge dates follow dd-mm-yyyy format."""
        # Regular expression for dd-mm-yyyy format (allowing single digits for day/month)
        date_pattern = r'^\d{1,2}-\d{1,2}-\d{4}$'
        
        # Filter rows with non-empty discharge dates
        non_empty_dates = ~(self.df['data_alta'].isna() | (self.df['data_alta'] == ''))
        date_df = self.df[non_empty_dates].copy()
        
        # Count total non-empty dates
        non_empty_count = len(date_df)
        
        # Check format using regex
        if non_empty_count > 0:
            valid_format = date_df['data_alta'].astype(str).str.match(date_pattern)
            invalid_format = ~valid_format
            invalid_count = invalid_format.sum()
            valid_count = valid_format.sum()
        else:
            invalid_count = 0
            valid_count = 0
        
        result = {
            'total_count': non_empty_count,
            'valid_count': int(valid_count),
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
                        'date': row['data_alta'],
                        'row': idx
                    })
        
        return result
    
    def _analyze_chronology(self) -> dict:
        """Check if discharge dates are after or on admission dates."""
        result = {
            'chronology_errors': [],
            'error_count': 0
        }
        
        if 'data_ent' not in self.df.columns:
            result['error'] = 'Admission date column not found'
            return result
        
        try:
            # Regular expression for dd-mm-yyyy format
            date_pattern = r'^\d{1,2}-\d{1,2}-\d{4}$'
            
            # Filter for rows with both dates present
            valid_dates_df = self.df[
                (~self.df['data_ent'].isna()) & 
                (~self.df['data_alta'].isna()) & 
                (self.df['data_ent'] != '') & 
                (self.df['data_alta'] != '')
            ].copy()
            
            # Skip empty dataset
            if len(valid_dates_df) == 0:
                result['valid_pairs_count'] = 0
                return result
            
            # Filter for rows with valid date formats
            admission_date_pattern = valid_dates_df['data_ent'].astype(str).str.match(date_pattern)
            discharge_date_pattern = valid_dates_df['data_alta'].astype(str).str.match(date_pattern)
            valid_format_df = valid_dates_df[admission_date_pattern & discharge_date_pattern].copy()
            
            result['valid_pairs_count'] = len(valid_format_df)
            
            # Convert to datetime for comparison
            valid_format_df['admission_date'] = pd.to_datetime(valid_format_df['data_ent'], format='%d-%m-%Y')
            valid_format_df['discharge_date'] = pd.to_datetime(valid_format_df['data_alta'], format='%d-%m-%Y')
            
            # Find records where discharge date is before admission date
            chronology_errors = valid_format_df['discharge_date'] < valid_format_df['admission_date']
            error_count = chronology_errors.sum()
            
            result['error_count'] = int(error_count)
            
            # Collect details of chronology errors
            if error_count > 0:
                error_rows = valid_format_df[chronology_errors]
                for i, (idx, row) in enumerate(error_rows.iterrows()):
                    if i < 15:  # Limit to 15 examples
                        result['chronology_errors'].append({
                            'id': row['ID'],
                            'admission_date': row['data_ent'],
                            'discharge_date': row['data_alta'],
                            'row': idx
                        })
        
        except Exception as e:
            result['error'] = str(e)
            
        return result
    
    def _analyze_duration_stats(self) -> dict:
        """Calculate statistics on hospitalization duration."""
        result = {}
        
        if 'data_ent' not in self.df.columns:
            result['error'] = 'Admission date column not found'
            return result
        
        try:
            # Regular expression for dd-mm-yyyy format
            date_pattern = r'^\d{1,2}-\d{1,2}-\d{4}$'
            
            # Filter for rows with both dates present
            valid_dates_df = self.df[
                (~self.df['data_ent'].isna()) & 
                (~self.df['data_alta'].isna()) & 
                (self.df['data_ent'] != '') & 
                (self.df['data_alta'] != '')
            ].copy()
            
            # Skip empty dataset
            if len(valid_dates_df) == 0:
                result['count'] = 0
                result['error'] = 'No records with both admission and discharge dates'
                return result
            
            # Filter for rows with valid date formats
            admission_date_pattern = valid_dates_df['data_ent'].astype(str).str.match(date_pattern)
            discharge_date_pattern = valid_dates_df['data_alta'].astype(str).str.match(date_pattern)
            valid_format_df = valid_dates_df[admission_date_pattern & discharge_date_pattern].copy()
            
            # Skip if no valid pairs
            if len(valid_format_df) == 0:
                result['count'] = 0
                result['error'] = 'No records with valid date formats'
                return result
            
            # Convert to datetime for comparison
            valid_format_df['admission_date'] = pd.to_datetime(valid_format_df['data_ent'], format='%d-%m-%Y')
            valid_format_df['discharge_date'] = pd.to_datetime(valid_format_df['data_alta'], format='%d-%m-%Y')
            
            # Calculate duration
            valid_format_df['days_hospitalized'] = (valid_format_df['discharge_date'] - valid_format_df['admission_date']).dt.days
            
            # Calculate statistics
            result['count'] = len(valid_format_df)
            result['mean_days'] = float(valid_format_df['days_hospitalized'].mean())
            result['median_days'] = float(valid_format_df['days_hospitalized'].median())
            result['min_days'] = int(valid_format_df['days_hospitalized'].min())
            result['max_days'] = int(valid_format_df['days_hospitalized'].max())
            
            # Find potentially unusual long stays
            long_stays = valid_format_df[valid_format_df['days_hospitalized'] > 60].sort_values('days_hospitalized', ascending=False)
            result['long_stays_count'] = len(long_stays)
            
            # Collect examples of long stays
            result['long_stays'] = []
            if not long_stays.empty:
                for i, (idx, row) in enumerate(long_stays.iterrows()):
                    if i < 5:  # Limit to 5 examples
                        result['long_stays'].append({
                            'id': row['ID'],
                            'days': int(row['days_hospitalized']),
                            'admission_date': row['data_ent'],
                            'discharge_date': row['data_alta'],
                            'row': idx
                        })
                        
        except Exception as e:
            result['error'] = str(e)
            
        return result