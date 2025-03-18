# workflows/quality_control/main.py
import pandas as pd
from pathlib import Path
import logging
import sys
from datetime import datetime
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QualityControl")

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

# Import report generator
from .report_generator import MarkdownReportGenerator

def find_doentes_csv() -> Path:
    """
    Locate the Doentes.csv file in the spreadsheets directory.
    
    Returns:
        Path: The path to the Doentes.csv file
    """
    # Import paths from project core
    from core.paths import ProjectPaths
    paths = ProjectPaths()
    
    # Default location based on project structure
    csv_path = paths.SPREADSHEET_SOURCE / "Doentes.csv"
    
    if not csv_path.exists():
        logger.error(f"Doentes.csv not found at {csv_path}")
        raise FileNotFoundError(f"Could not find Doentes.csv at {csv_path}")
        
    return csv_path

def collect_analysis_results(df: pd.DataFrame, csv_path: Path) -> dict:
    """Collect analysis results from all analyzers."""
    results = {}
    
    try:
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
        
    except Exception as e:
        logger.error(f"Error collecting analysis results: {str(e)}")
        logger.error(traceback.format_exc())
        raise
    
    return results

def run_quality_control(csv_path: Path = None, year_filter: str = None) -> int:
    """
    Run the quality control workflow on the specified CSV file.
    
    Args:
        csv_path: Path to CSV file (if None, will look for default location)
        year_filter: String specifying year filter (e.g., "25" for 2025 or "25-20" for range)
        
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
        
        # Track filter info for reporting
        filter_info = {
            "is_filtered": False,
            "filter_type": None,
            "filter_value": None,
            "total_records": len(df),
            "filtered_records": len(df)
        }
        
        # Apply year filter if specified
        if year_filter:
            filter_info["is_filtered"] = True
            
            # Determine filter type (single year or range)
            if '-' in year_filter:
                start_year, end_year = year_filter.split('-')
                if start_year.isdigit() and end_year.isdigit():
                    # Ensure start year is greater than or equal to end year for consistent display
                    if int(start_year) < int(end_year):
                        start_year, end_year = end_year, start_year
                    filter_info["filter_type"] = "range"
                    filter_info["filter_value"] = f"20{start_year} to 20{end_year}"
            else:
                if year_filter.isdigit():
                    filter_info["filter_type"] = "single"
                    filter_info["filter_value"] = f"20{year_filter}"
            
            # Apply the filter
            original_count = len(df)
            from .utils.helpers import filter_dataframe_by_year
            df = filter_dataframe_by_year(df, year_filter)
            filtered_count = len(df)
            
            filter_info["filtered_records"] = filtered_count
            
            if filtered_count == 0:
                print(f"❌ No records found matching year filter '{year_filter}'")
                return 1
                
            # Show clear filtering information
            if filter_info["filter_type"] == "single":
                print(f"📊 FILTERED VIEW: Analyzing records from year {filter_info['filter_value']} only")
            elif filter_info["filter_type"] == "range":
                print(f"📊 FILTERED VIEW: Analyzing records from years {filter_info['filter_value']}")
            
            print(f"📄 Records: {filtered_count:,} of {original_count:,} total ({filtered_count/original_count:.1%})")
        else:
            print(f"📊 FULL DATABASE: Analyzing all {len(df):,} records")
        
        # Add a separator line for better readability
        print("\n" + "="*80)
        
        # Initialize reporter for console output
        reporter = ConsoleReporter()
        
        # Run file analysis for console output
        file_analyzer = FileAnalyzer(df, csv_path)
        reporter.report_file_analysis(file_analyzer.analyze())
        
        # Run ID analysis for console output
        id_analyzer = IDAnalyzer(df)
        if id_analyzer.is_applicable():
            reporter.report_id_analysis(id_analyzer.analyze())
        
        # Run admission date analysis for console output
        admission_analyzer = AdmissionDateAnalyzer(df)
        if admission_analyzer.is_applicable():
            reporter.report_admission_analysis(admission_analyzer.analyze())
        
        # Run discharge date analysis for console output
        discharge_analyzer = DischargeDateAnalyzer(df)
        if discharge_analyzer.is_applicable():
            reporter.report_discharge_analysis(discharge_analyzer.analyze())
        
        # Run birth date analysis for console output
        birth_analyzer = BirthDateAnalyzer(df)
        if birth_analyzer.is_applicable():
            reporter.report_birth_analysis(birth_analyzer.analyze())
        
        # Run processo analysis for console output
        processo_analyzer = ProcessoAnalyzer(df)
        if processo_analyzer.is_applicable():
            reporter.report_processo_analysis(processo_analyzer.analyze())
        
        # Run nome analysis for console output
        nome_analyzer = NomeAnalyzer(df)
        if nome_analyzer.is_applicable():
            reporter.report_nome_analysis(nome_analyzer.analyze())
        
        # Run sexo analysis for console output
        sexo_analyzer = SexoAnalyzer(df)
        if sexo_analyzer.is_applicable():
            reporter.report_sexo_analysis(sexo_analyzer.analyze())
        
        # Run destino analysis for console output
        destino_analyzer = DestinoAnalyzer(df)
        if destino_analyzer.is_applicable():
            reporter.report_destino_analysis(destino_analyzer.analyze())
        
        # Run origem analysis for console output
        origem_analyzer = OrigemAnalyzer(df)
        if origem_analyzer.is_applicable():
            reporter.report_origem_analysis(origem_analyzer.analyze())
        
        # For the markdown report, collect all results separately
        logger.info("Collecting analysis results for markdown report...")
        results = collect_analysis_results(df, csv_path)
        
        # Generate and save markdown report
        try:
            from core.paths import ProjectPaths
            paths = ProjectPaths()
            
            # Create report generator with filter info
            logger.info("Creating markdown report...")
            report_generator = MarkdownReportGenerator(results, csv_path, filter_info)
            report_generator.generate_file_analysis_section()
            report_generator.generate_id_analysis_section()
            report_generator.generate_date_analysis_section("data_ent", "Admission Date Analysis")
            report_generator.generate_date_analysis_section("data_alta", "Discharge Date Analysis")
            report_generator.generate_date_analysis_section("data_nasc", "Birth Date Analysis")
            report_generator.generate_processo_analysis_section()
            report_generator.generate_nome_analysis_section()
            report_generator.generate_categorical_analysis_section("sexo", "Sexo Analysis")
            report_generator.generate_categorical_analysis_section("destino", "Destino Analysis")
            report_generator.generate_categorical_analysis_section("origem", "Origem Analysis")
            
            # Define report output path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            report_file_name = f"report_quality_gsheet_{timestamp}.md"
            
            # Make sure the reports directory exists
            paths.REPORTS.mkdir(parents=True, exist_ok=True)
            report_output_path = paths.REPORTS / report_file_name
            
            # Save the report
            report_generator.save_report(report_output_path)
            print(f"\n✅ Quality control analysis completed successfully. Report saved to: {report_output_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate markdown report: {str(e)}")
            logger.error(traceback.format_exc())
            print(f"\n⚠️ Console analysis completed, but markdown report failed: {str(e)}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Quality control failed: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"❌ Quality control failed: {str(e)}")
        return 1