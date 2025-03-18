from pathlib import Path
from typing import Dict, Any
import pandas as pd

def find_doentes_csv() -> Path:
    """
    Locate the Doentes.csv file in the spreadsheets directory.
    
    Returns:
        Path: The path to the Doentes.csv file
    """
    # Import paths from project core
    from core.paths import paths
    
    # Default location based on project structure
    csv_path = paths.SPREADSHEET_SOURCE / "Doentes.csv"
    
    if not csv_path.exists():
        raise FileNotFoundError(f"Could not find Doentes.csv at {csv_path}")
        
    return csv_path

def collect_analysis_results(df: pd.DataFrame, csv_path: Path) -> Dict[str, Dict[str, Any]]:
    """Collect analysis results from all analyzers."""
    from ..analyzers.file_analyzer import FileAnalyzer
    from ..analyzers.id_analyzer import IDAnalyzer
    from ..analyzers.admission_analyzer import AdmissionDateAnalyzer
    from ..analyzers.discharge_analyzer import DischargeDateAnalyzer
    from ..analyzers.birth_analyzer import BirthDateAnalyzer
    from ..analyzers.other_analyzers import (
        ProcessoAnalyzer, NomeAnalyzer, SexoAnalyzer,
        DestinoAnalyzer, OrigemAnalyzer
    )
    
    results = {}
    
    # File analysis
    file_analyzer = FileAnalyzer(df, csv_path)
    results['file'] = file_analyzer.analyze()
    
    # ID analysis
    id_analyzer = IDAnalyzer(df)
    if id_analyzer.is_applicable():
        results['id'] = id_analyzer.analyze()
    
    # Date analyses
    admission_analyzer = AdmissionDateAnalyzer(df)
    if admission_analyzer.is_applicable():
        results['data_ent'] = admission_analyzer.analyze()
    
    discharge_analyzer = DischargeDateAnalyzer(df)
    if discharge_analyzer.is_applicable():
        results['data_alta'] = discharge_analyzer.analyze()
    
    birth_analyzer = BirthDateAnalyzer(df)
    if birth_analyzer.is_applicable():
        results['data_nasc'] = birth_analyzer.analyze()
    
    # Other analyses
    processo_analyzer = ProcessoAnalyzer(df)
    if processo_analyzer.is_applicable():
        results['processo'] = processo_analyzer.analyze()
    
    nome_analyzer = NomeAnalyzer(df)
    if nome_analyzer.is_applicable():
        results['nome'] = nome_analyzer.analyze()
    
    sexo_analyzer = SexoAnalyzer(df)
    if sexo_analyzer.is_applicable():
        results['sexo'] = sexo_analyzer.analyze()
    
    destino_analyzer = DestinoAnalyzer(df)
    if destino_analyzer.is_applicable():
        results['destino'] = destino_analyzer.analyze()
    
    origem_analyzer = OrigemAnalyzer(df)
    if origem_analyzer.is_applicable():
        results['origem'] = origem_analyzer.analyze()
    
    return results

def filter_dataframe_by_year(df: pd.DataFrame, year_filter: str = None) -> pd.DataFrame:
    """
    Filter dataframe rows by year extracted from ID column.
    
    Args:
        df: Dataframe to filter
        year_filter: String in format "YY" for single year or "YY-YY" for range
                    (e.g., "25" for 2025 or "25-20" for 2025 to 2020)
    
    Returns:
        Filtered dataframe
    """
    if not year_filter or 'ID' not in df.columns:
        return df
    
    # Make sure ID is string type
    df['ID'] = df['ID'].astype(str)
    
    # Parse year filter
    if '-' in year_filter:
        # Handle year range
        start_year, end_year = year_filter.split('-')
        # Validate input
        if not (start_year.isdigit() and end_year.isdigit() and len(start_year) == 2 and len(end_year) == 2):
            raise ValueError(f"Invalid year range format: {year_filter}. Expected format: 'YY-YY'")
            
        # Convert to integers for comparison (higher year number = more recent year)
        start_year_num = int(start_year)
        end_year_num = int(end_year)
        
        # Ensure start year is greater than or equal to end year for proper filtering
        if start_year_num < end_year_num:
            start_year, end_year = end_year, start_year
            start_year_num, end_year_num = end_year_num, start_year_num
        
        # Extract year from ID and filter
        year_filter_mask = df['ID'].str.match(r'^\d{2}')  # Ensure ID starts with digits
        filtered_df = df[year_filter_mask].copy()
        
        if not filtered_df.empty:
            # Extract first two characters of ID as year
            filtered_df['year'] = filtered_df['ID'].str[:2].astype(int)
            # Filter by year range
            filtered_df = filtered_df[(filtered_df['year'] <= start_year_num) & 
                                     (filtered_df['year'] >= end_year_num)]
            # Remove temporary column
            filtered_df.drop('year', axis=1, inplace=True)
            
            # We'll handle printing in the main function now
    
    else:
        # Handle single year
        if not (year_filter.isdigit() and len(year_filter) == 2):
            raise ValueError(f"Invalid year format: {year_filter}. Expected format: 'YY'")
            
        # Simple filter for IDs starting with the specified year
        year_pattern = f"^{year_filter}"
        filtered_df = df[df['ID'].str.match(year_pattern)]
        
        # We'll handle printing in the main function now
    
    return filtered_df