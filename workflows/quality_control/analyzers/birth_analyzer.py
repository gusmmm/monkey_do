import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional
from .base import BaseAnalyzer

class BirthDateAnalyzer(BaseAnalyzer):
    """Analyzer for birth dates (data_nasc column)."""
    
    def is_applicable(self) -> bool:
        """Check if data_nasc column exists in the dataframe."""
        return 'data_nasc' in self.df.columns
    
    def analyze(self) -> dict:
        """Analyze birth date column for issues."""
        results = {}
        
        # Check for admission date column (required for age calculation)
        has_admission_dates = 'data_ent' in self.df.columns
        
        # Run analysis functions
        results['missing'] = self._analyze_missing_dates()
        results['format'] = self._analyze_date_format()
        results['validity'] = self._analyze_date_validity()
        
        if has_admission_dates:
            results['age'] = self._analyze_age_stats()
        else:
            results['age'] = {'error': 'Admission date column not found'}
        
        self.results = results
        return results
    
    def _analyze_missing_dates(self) -> dict:
        """Check for missing values in birth date column."""
        missing_dates = self.df['data_nasc'].isna() | (self.df['data_nasc'] == '')
        missing_count = missing_dates.sum()
        
        result = {
            'count': int(missing_count),
            'percentage': float(missing_count / len(self.df) if len(self.df) > 0 else 0),
            'rows': self.df[missing_dates].index.tolist() if missing_count > 0 else []
        }
        
        return result
    
    def _analyze_date_format(self) -> dict:
        """Check if birth dates follow dd-mm-yyyy format."""
        # Regular expression for dd-mm-yyyy format (allowing single digits for day/month)
        date_pattern = r'^\d{1,2}-\d{1,2}-\d{4}$'
        
        # Filter rows with non-empty dates
        non_empty = ~(self.df['data_nasc'].isna() | (self.df['data_nasc'] == ''))
        date_df = self.df[non_empty].copy()
        
        # Check format using regex
        valid_format = date_df['data_nasc'].astype(str).str.match(date_pattern)
        invalid_format = ~valid_format
        invalid_count = invalid_format.sum()
        
        result = {
            'valid_count': int(valid_format.sum()),
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
                        'date': row['data_nasc'],
                        'row': idx
                    })
        
        return result
    
    def _analyze_date_validity(self) -> dict:
        """Check for unreasonable birth dates (before 1900 or in the future)."""
        # Regular expression for dd-mm-yyyy format
        date_pattern = r'^\d{1,2}-\d{1,2}-\d{4}$'
        
        # Filter for rows with valid date formats
        non_empty = ~(self.df['data_nasc'].isna() | (self.df['data_nasc'] == ''))
        date_df = self.df[non_empty].copy()
        valid_format = date_df['data_nasc'].astype(str).str.match(date_pattern)
        valid_dates_df = date_df[valid_format].copy()
        
        result = {
            'too_old_examples': [],
            'future_examples': [],
            'too_old_count': 0,
            'future_count': 0
        }
        
        if valid_dates_df.empty:
            return result
        
        try:
            # Extract year component first to avoid datetime conversion issues
            valid_dates_df['birth_year'] = valid_dates_df['data_nasc'].str.split('-').str[-1].astype(int)
            
            # Define thresholds
            min_acceptable_year = 1900
            current_year = datetime.now().year
            
            # Check for birthdates before 1900
            too_old = valid_dates_df['birth_year'] < min_acceptable_year
            too_old_count = too_old.sum()
            result['too_old_count'] = int(too_old_count)
            
            # Check for birthdates in the future
            future = valid_dates_df['birth_year'] > current_year
            future_count = future.sum()
            result['future_count'] = int(future_count)
            
            # Collect examples of unreasonable birthdates
            if too_old_count > 0:
                too_old_rows = valid_dates_df[too_old]
                for i, (idx, row) in enumerate(too_old_rows.iterrows()):
                    if i < 10:  # Limit to 10 examples
                        result['too_old_examples'].append({
                            'id': row['ID'],
                            'date': row['data_nasc'],
                            'year': row['birth_year'],
                            'row': idx
                        })
            
            if future_count > 0:
                future_rows = valid_dates_df[future]
                for i, (idx, row) in enumerate(future_rows.iterrows()):
                    if i < 10:  # Limit to 10 examples
                        result['future_examples'].append({
                            'id': row['ID'],
                            'date': row['data_nasc'],
                            'year': row['birth_year'],
                            'row': idx
                        })
                
        except Exception as e:
            result['error'] = f"Error analyzing date validity: {str(e)}"
        
        return result
    
    def _analyze_age_stats(self) -> dict:
        """Calculate age statistics based on admission date."""
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
                (~self.df['data_nasc'].isna()) & 
                (self.df['data_ent'] != '') & 
                (self.df['data_nasc'] != '')
            ].copy()
            
            # Skip empty dataset
            if len(valid_dates_df) == 0:
                result['count'] = 0
                result['error'] = 'No records with both admission and birth dates'
                return result
            
            # Filter for rows with valid date formats
            admission_date_pattern = valid_dates_df['data_ent'].astype(str).str.match(date_pattern)
            birth_date_pattern = valid_dates_df['data_nasc'].astype(str).str.match(date_pattern)
            valid_format_df = valid_dates_df[admission_date_pattern & birth_date_pattern].copy()
            
            # Skip if no valid pairs
            if len(valid_format_df) == 0:
                result['count'] = 0
                result['error'] = 'No records with valid date formats'
                return result
            
            # Safely convert to datetime and handle problematic dates
            try:
                # Extract year components to calculate age without full datetime conversion
                valid_format_df['admission_year'] = valid_format_df['data_ent'].str.split('-').str[-1].astype(int)
                valid_format_df['admission_month'] = valid_format_df['data_ent'].str.split('-').str[1].astype(int)
                valid_format_df['admission_day'] = valid_format_df['data_ent'].str.split('-').str[0].astype(int)
                
                valid_format_df['birth_year'] = valid_format_df['data_nasc'].str.split('-').str[-1].astype(int)
                valid_format_df['birth_month'] = valid_format_df['data_nasc'].str.split('-').str[1].astype(int)
                valid_format_df['birth_day'] = valid_format_df['data_nasc'].str.split('-').str[0].astype(int)
                
                # Filter out birthdates before 1900 or after current year
                current_year = datetime.now().year
                valid_years = (valid_format_df['birth_year'] >= 1900) & (valid_format_df['birth_year'] <= current_year)
                valid_format_df = valid_format_df[valid_years]
                
                if len(valid_format_df) == 0:
                    result['count'] = 0
                    result['error'] = 'No records with valid birth years'
                    return result
                
                # Calculate approximate age at admission in years
                # More precise calculation would account for exact day of month
                valid_format_df['age_at_admission'] = (
                    valid_format_df['admission_year'] - valid_format_df['birth_year'] - 
                    ((valid_format_df['admission_month'] < valid_format_df['birth_month']) | 
                     ((valid_format_df['admission_month'] == valid_format_df['birth_month']) & 
                      (valid_format_df['admission_day'] < valid_format_df['birth_day']))).astype(int)
                )
            
            except Exception as e:
                result['error'] = f"Error during age calculation: {str(e)}"
                return result
            
            # Calculate statistics
            result['count'] = len(valid_format_df)
            result['mean_age'] = float(valid_format_df['age_at_admission'].mean())
            result['median_age'] = float(valid_format_df['age_at_admission'].median())
            result['min_age'] = int(valid_format_df['age_at_admission'].min())
            result['max_age'] = int(valid_format_df['age_at_admission'].max())
            
            # Age distribution by decade
            age_counts = valid_format_df['age_at_admission'].apply(lambda x: int(x / 10) * 10).value_counts().sort_index()
            result['age_distribution'] = {f"{decade}-{decade+9}": int(count) for decade, count in age_counts.items()}
            
            # Find potentially unusual ages
            very_young = valid_format_df[valid_format_df['age_at_admission'] < 5]
            very_old = valid_format_df[valid_format_df['age_at_admission'] > 100]
            negative_age = valid_format_df[valid_format_df['age_at_admission'] < 0]
            
            # Collect examples of unusual ages
            result['unusual_ages'] = {
                'very_young': [],
                'very_young_count': len(very_young),
                'very_old': [],
                'very_old_count': len(very_old),
                'negative': [],
                'negative_count': len(negative_age)
            }
            
            # Collect examples of very young patients
            for i, (idx, row) in enumerate(very_young.iterrows()):
                if i < 5:
                    result['unusual_ages']['very_young'].append({
                        'id': row['ID'],
                        'age': int(row['age_at_admission']),
                        'birth_date': row['data_nasc'],
                        'admission_date': row['data_ent'],
                        'row': idx
                    })
            
            # Collect examples of very old patients
            for i, (idx, row) in enumerate(very_old.iterrows()):
                if i < 5:
                    result['unusual_ages']['very_old'].append({
                        'id': row['ID'],
                        'age': int(row['age_at_admission']),
                        'birth_date': row['data_nasc'],
                        'admission_date': row['data_ent'],
                        'row': idx
                    })
            
            # Collect examples of negative ages
            for i, (idx, row) in enumerate(negative_age.iterrows()):
                if i < 5:
                    result['unusual_ages']['negative'].append({
                        'id': row['ID'],
                        'age': int(row['age_at_admission']),
                        'birth_date': row['data_nasc'],
                        'admission_date': row['data_ent'],
                        'row': idx
                    })
                    
        except Exception as e:
            result['error'] = f"Error calculating age statistics: {str(e)}"
            
        return result