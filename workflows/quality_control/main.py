# workflows/quality_control/main.py
import pandas as pd
from pathlib import Path
import logging
import sys

# Import analyzers
from .analyzers.file_analyzer import FileAnalyzer
from .analyzers.id_analyzer import IDAnalyzer
from .analyzers.admission_analyzer import AdmissionDateAnalyzer
from .analyzers.discharge_analyzer import DischargeDateAnalyzer
from .analyzers.birth_analyzer import BirthDateAnalyzer
from .analyzers.other_analyzers import (
    ProcessoAnalyzer, NomeAnalyzer, SexoAnalyzer, 
    DestinoAnalyzer, OrigemAnalyzer
)

# Import reporters
from .reporters.console_reporter import ConsoleReporter

# Configure logging
logger = logging.getLogger("QualityControl")

# Helper functions
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
        logger.error(f"Doentes.csv not found at {csv_path}")
        raise FileNotFoundError(f"Could not find Doentes.csv at {csv_path}")
        
    return csv_path

def run_quality_control(csv_path: Path = None) -> int:
    """
    Run the quality control workflow on the specified CSV file.
    
    Args:
        csv_path: Path to CSV file (if None, will look for default location)
        
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        # Find CSV file if not provided
        if csv_path is None:
            csv_path = find_doentes_csv()
            
        print(f"\n🔍 Starting quality control analysis on: {csv_path}")
        
        # Load the dataframe
        df = pd.read_csv(csv_path, dtype={'ID': str})  # Force ID column as string
        
        # Initialize reporter
        reporter = ConsoleReporter()
        
        # Run file analysis
        file_analyzer = FileAnalyzer(df, csv_path)
        reporter.report_file_analysis(file_analyzer.analyze())
        
        # Run ID analysis
        id_analyzer = IDAnalyzer(df)
        if id_analyzer.is_applicable():
            reporter.report_id_analysis(id_analyzer.analyze())
        
        # Run admission date analysis
        admission_analyzer = AdmissionDateAnalyzer(df)
        if admission_analyzer.is_applicable():
            reporter.report_admission_analysis(admission_analyzer.analyze())
        
        # Run discharge date analysis
        discharge_analyzer = DischargeDateAnalyzer(df)
        if discharge_analyzer.is_applicable():
            reporter.report_discharge_analysis(discharge_analyzer.analyze())
        
        # Run birth date analysis
        birth_analyzer = BirthDateAnalyzer(df)
        if birth_analyzer.is_applicable():
            reporter.report_birth_analysis(birth_analyzer.analyze())
        
        # Run processo analysis
        processo_analyzer = ProcessoAnalyzer(df)
        if processo_analyzer.is_applicable():
            reporter.report_processo_analysis(processo_analyzer.analyze())

        # Run nome analysis
        nome_analyzer = NomeAnalyzer(df)
        if nome_analyzer.is_applicable():
            reporter.report_nome_analysis(nome_analyzer.analyze())

        # Run sexo analysis
        sexo_analyzer = SexoAnalyzer(df)
        if sexo_analyzer.is_applicable():
            reporter.report_sexo_analysis(sexo_analyzer.analyze())

        # Run destino analysis
        destino_analyzer = DestinoAnalyzer(df)
        if destino_analyzer.is_applicable():
            reporter.report_destino_analysis(destino_analyzer.analyze())

        # Run origem analysis
        origem_analyzer = OrigemAnalyzer(df)
        if origem_analyzer.is_applicable():
            reporter.report_origem_analysis(origem_analyzer.analyze())
        
        print("\n✅ Quality control analysis completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Quality control failed: {str(e)}")
        print(f"❌ Quality control failed: {str(e)}")
        return 1