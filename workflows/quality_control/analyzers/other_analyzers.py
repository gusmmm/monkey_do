import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Set
from collections import Counter
from .base import BaseAnalyzer

class ProcessoAnalyzer(BaseAnalyzer):
    """Analyzer for processo column (medical record numbers)."""
    
    def is_applicable(self) -> bool:
        """Check if processo column exists in the dataframe."""
        return 'processo' in self.df.columns
    
    def analyze(self) -> dict:
        """Analyze processo column for issues."""
        results = {}
        
        # Run analysis functions
        results['missing'] = self._analyze_missing_values()
        results['invalid'] = self._analyze_invalid_values()
        
        self.results = results
        return results
    
    def _analyze_missing_values(self) -> dict:
        """Check for missing values in processo column."""
        missing_values = self.df['processo'].isna() | (self.df['processo'] == '')
        missing_count = missing_values.sum()
        
        result = {
            'count': int(missing_count),
            'percentage': float(missing_count / len(self.df) if len(self.df) > 0 else 0),
            'examples': []
        }
        
        # Collect examples of missing values
        if missing_count > 0:
            missing_rows = self.df[missing_values]
            for i, (idx, row) in enumerate(missing_rows.iterrows()):
                if i < 10:  # Limit to 10 examples
                    result['examples'].append({
                        'id': row['ID'],
                        'row': idx
                    })
        
        return result
    
    def _analyze_invalid_values(self) -> dict:
        """Check for non-numeric values in processo column."""
        # Filter out missing values first
        non_missing = ~(self.df['processo'].isna() | (self.df['processo'] == ''))
        data_to_check = self.df[non_missing].copy()
        
        # Convert processo values to string
        data_to_check['processo'] = data_to_check['processo'].astype(str)
        
        # Check for non-numeric values (allowing digits and possibly some formatting characters)
        # This regex allows digits, possibly with spaces or dashes as separators
        valid_pattern = data_to_check['processo'].str.match(r'^[\d\s\-]+$')
        invalid_values = ~valid_pattern
        invalid_count = invalid_values.sum()
        
        result = {
            'count': int(invalid_count),
            'percentage': float(invalid_count / len(data_to_check) if len(data_to_check) > 0 else 0),
            'examples': []
        }
        
        # Collect examples of invalid values
        if invalid_count > 0:
            invalid_rows = data_to_check[invalid_values]
            for i, (idx, row) in enumerate(invalid_rows.iterrows()):
                if i < 10:  # Limit to 10 examples
                    result['examples'].append({
                        'id': row['ID'],
                        'value': row['processo'],
                        'row': idx
                    })
        
        return result


class NomeAnalyzer(BaseAnalyzer):
    """Analyzer for nome column (patient names)."""
    
    def is_applicable(self) -> bool:
        """Check if nome column exists in the dataframe."""
        return 'nome' in self.df.columns
    
    def analyze(self) -> dict:
        """Analyze nome column for issues."""
        results = {}
        
        # Run analysis function
        results['missing'] = self._analyze_missing_values()
        
        self.results = results
        return results
    
    def _analyze_missing_values(self) -> dict:
        """Check for missing values in nome column."""
        missing_values = self.df['nome'].isna() | (self.df['nome'] == '')
        missing_count = missing_values.sum()
        
        result = {
            'count': int(missing_count),
            'percentage': float(missing_count / len(self.df) if len(self.df) > 0 else 0),
            'examples': []
        }
        
        # Collect examples of missing values
        if missing_count > 0:
            missing_rows = self.df[missing_values]
            for i, (idx, row) in enumerate(missing_rows.iterrows()):
                if i < 10:  # Limit to 10 examples
                    result['examples'].append({
                        'id': row['ID'],
                        'row': idx
                    })
        
        return result


class CategoricalAnalyzer(BaseAnalyzer):
    """Generic analyzer for categorical columns."""
    
    def __init__(self, df: pd.DataFrame, column_name: str, expected_values: Optional[Set[str]] = None):
        """Initialize with dataframe, column name, and optional expected values."""
        super().__init__(df)
        self.column_name = column_name
        self.expected_values = expected_values
    
    def is_applicable(self) -> bool:
        """Check if the specified column exists in the dataframe."""
        return self.column_name in self.df.columns
    
    def analyze(self) -> dict:
        """Analyze the categorical column for issues."""
        results = {}
        
        # Run analysis functions
        results['missing'] = self._analyze_missing_values()
        results['frequency'] = self._analyze_value_frequency()
        
        if self.expected_values is not None:
            results['unexpected'] = self._analyze_unexpected_values()
            
        self.results = results
        return results
    
    def _analyze_missing_values(self) -> dict:
        """Check for missing values in the column."""
        missing_values = self.df[self.column_name].isna() | (self.df[self.column_name] == '')
        missing_count = missing_values.sum()
        
        result = {
            'count': int(missing_count),
            'percentage': float(missing_count / len(self.df) if len(self.df) > 0 else 0),
            'examples': []
        }
        
        # Collect examples of missing values
        if missing_count > 0:
            missing_rows = self.df[missing_values]
            for i, (idx, row) in enumerate(missing_rows.iterrows()):
                if i < 10:  # Limit to 10 examples
                    example = {
                        'id': row['ID'] if 'ID' in row else "Unknown",
                        'row': idx
                    }
                    result['examples'].append(example)
        
        return result
    
    def _analyze_value_frequency(self) -> dict:
        """Analyze the frequency of each value in the column."""
        # Filter out missing values
        non_missing = ~(self.df[self.column_name].isna() | (self.df[self.column_name] == ''))
        data_to_count = self.df.loc[non_missing, self.column_name]
        
        # Count frequencies
        value_counts = data_to_count.value_counts().to_dict()
        
        # Calculate percentages
        total_count = sum(value_counts.values())
        value_percentages = {
            value: count / total_count if total_count > 0 else 0 
            for value, count in value_counts.items()
        }
        
        result = {
            'unique_count': len(value_counts),
            'frequencies': {
                str(value): {
                    'count': int(count),
                    'percentage': float(value_percentages[value])
                }
                for value, count in value_counts.items()
            }
        }
        
        return result
    
    def _analyze_unexpected_values(self) -> dict:
        """Check for values outside the expected set."""
        if self.expected_values is None:
            return {'count': 0, 'examples': []}
        
        # Filter out missing values
        non_missing = ~(self.df[self.column_name].isna() | (self.df[self.column_name] == ''))
        data_to_check = self.df[non_missing].copy()
        
        # Find unexpected values
        unexpected_values = ~data_to_check[self.column_name].isin(self.expected_values)
        unexpected_count = unexpected_values.sum()
        
        result = {
            'count': int(unexpected_count),
            'percentage': float(unexpected_count / len(data_to_check) if len(data_to_check) > 0 else 0),
            'examples': []
        }
        
        # Collect examples of unexpected values
        if unexpected_count > 0:
            unexpected_rows = data_to_check[unexpected_values]
            for i, (idx, row) in enumerate(unexpected_rows.iterrows()):
                if i < 10:  # Limit to 10 examples
                    result['examples'].append({
                        'id': row['ID'],
                        'value': row[self.column_name],
                        'row': idx
                    })
        
        return result


class SexoAnalyzer(CategoricalAnalyzer):
    """Analyzer for sexo column (patient sex/gender)."""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize with dataframe and expected values for sexo column."""
        expected_values = {'M', 'F'}  # M for male, F for female
        super().__init__(df, 'sexo', expected_values)


class DestinoAnalyzer(CategoricalAnalyzer):
    """Analyzer for destino column (patient destination)."""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize with dataframe for destino column."""
        super().__init__(df, 'destino')


class OrigemAnalyzer(CategoricalAnalyzer):
    """Analyzer for origem column (patient origin)."""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize with dataframe for origem column."""
        super().__init__(df, 'origem')


# Console reporter extension for these analyzers
def report_processo_analysis(reporter, results: Dict[str, Any]) -> None:
    """Format processo column analysis results for console."""
    print("\n" + "="*80)
    print("📝 PROCESSO (MEDICAL RECORD) ANALYSIS")
    print("="*80)
    
    # Report missing values
    missing = results.get('missing', {})
    print("\n🔍 Missing Values Analysis:")
    if missing.get('count', 0) == 0:
        print("   ✅ No missing processo values found")
    else:
        print(f"   ⚠️ Found {missing['count']} missing processo values ({missing['percentage']:.2%} of total records)")
        print("\n   Examples of records with missing processo:")
        
        for i, example in enumerate(missing.get('examples', []), 1):
            print(f"   {i}. ID '{example['id']}' at row {example['row'] + 2}")
    
    # Report invalid values
    invalid = results.get('invalid', {})
    print("\n🔢 Non-numeric Values Analysis:")
    if invalid.get('count', 0) == 0:
        print("   ✅ All processo values are numeric")
    else:
        print(f"   ⚠️ Found {invalid['count']} non-numeric processo values ({invalid['percentage']:.2%} of non-missing values)")
        print("\n   Examples of records with non-numeric processo values:")
        
        for i, example in enumerate(invalid.get('examples', []), 1):
            print(f"   {i}. ID '{example['id']}' has '{example['value']}' at row {example['row'] + 2}")
    
    print("\n" + "="*80)


def report_nome_analysis(reporter, results: Dict[str, Any]) -> None:
    """Format nome column analysis results for console."""
    print("\n" + "="*80)
    print("👤 PATIENT NAME ANALYSIS")
    print("="*80)
    
    # Report missing values
    missing = results.get('missing', {})
    print("\n🔍 Missing Names Analysis:")
    if missing.get('count', 0) == 0:
        print("   ✅ No missing patient names found")
    else:
        print(f"   ⚠️ Found {missing['count']} missing patient names ({missing['percentage']:.2%} of total records)")
        print("\n   Records with missing names:")
        
        for i, example in enumerate(missing.get('examples', []), 1):
            print(f"   {i}. ID '{example['id']}' at row {example['row'] + 2}")
    
    print("\n" + "="*80)


def report_categorical_analysis(reporter, results: Dict[str, Any], column_name: str, title: str) -> None:
    """Format categorical column analysis results for console."""
    print("\n" + "="*80)
    print(f"{title}")
    print("="*80)
    
    # Report missing values
    missing = results.get('missing', {})
    print(f"\n🔍 Missing {column_name.capitalize()} Analysis:")
    if missing.get('count', 0) == 0:
        print(f"   ✅ No missing {column_name} values found")
    else:
        print(f"   ⚠️ Found {missing['count']} missing {column_name} values ({missing['percentage']:.2%} of total records)")
        print(f"\n   Records with missing {column_name}:")
        
        for i, example in enumerate(missing.get('examples', []), 1):
            print(f"   {i}. ID '{example['id']}' at row {example['row'] + 2}")
    
    # Report value frequencies
    frequencies = results.get('frequency', {})
    print(f"\n📊 {column_name.capitalize()} Value Distribution:")
    
    if frequencies.get('unique_count', 0) == 0:
        print(f"   ℹ️ No {column_name} values found (all missing)")
    else:
        print(f"   Found {frequencies['unique_count']} unique {column_name} values")
        print(f"\n   Frequency breakdown:")
        
        # Sort by frequency (descending)
        sorted_values = sorted(
            frequencies.get('frequencies', {}).items(),
            key=lambda x: x[1]['count'], 
            reverse=True
        )
        
        for value, details in sorted_values:
            count = details['count']
            percentage = details['percentage']
            bar_length = int(percentage * 40)  # Scale for reasonable bar length
            bar = "█" * bar_length
            print(f"   {value:15} : {count:4d} ({percentage:6.2%}) {bar}")
    
    # Report unexpected values if applicable
    unexpected = results.get('unexpected', {})
    if unexpected is not None and 'count' in unexpected:
        print(f"\n⚠️ Unexpected {column_name.capitalize()} Values:")
        
        if unexpected.get('count', 0) == 0:
            print(f"   ✅ All {column_name} values match expected format")
        else:
            print(f"   ⚠️ Found {unexpected['count']} unexpected {column_name} values ({unexpected['percentage']:.2%} of non-missing values)")
            print(f"\n   Examples of unexpected values:")
            
            for i, example in enumerate(unexpected.get('examples', []), 1):
                print(f"   {i}. ID '{example['id']}' has '{example['value']}' at row {example['row'] + 2}")
    
    print("\n" + "="*80)