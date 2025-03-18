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