import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

class MarkdownReportGenerator:
    """Generates a Markdown report of the quality control analysis."""
    
    def __init__(self, results: Dict[str, Dict[str, Any]], file_path: Path, filter_info: Dict[str, Any] = None):
        """Initialize with analysis results, file path, and optional filter info."""
        self.results = results
        self.file_path = file_path
        self.filter_info = filter_info or {"is_filtered": False}
        self.report_sections = []
    
    def add_section(self, title: str, content: str) -> None:
        """Add a section to the report."""
        self.report_sections.append(f"## {title}\n\n{content}")
    
    def generate_file_analysis_section(self) -> None:
        """Generate the file analysis section."""
        file_results = self.results.get('file', {})
        if not file_results:
            return
        
        content = f"""
        - **File Name:** {file_results['file_name']}
        - **File Path:** {file_results['file_path']}
        - **File Size:** {file_results['file_size_kb']:.2f} KB
        - **Total Rows:** {file_results['row_count']}
        - **Total Columns:** {file_results['column_count']}
        """
        
        columns_str = ", ".join(file_results['columns'])
        content += f"\n**Columns:** {columns_str}\n"
        
        self.add_section("File Analysis", content)
    
    def generate_id_analysis_section(self) -> None:
        """Generate the ID analysis section."""
        id_results = self.results.get('id', {})
        if not id_results:
            return
        
        content = ""
        
        # Missing IDs
        missing = id_results.get('missing', {})
        if missing.get('count', 0) > 0:
            content += f"- **Missing IDs:** {missing['count']} ({missing['percentage']:.2%})\n"
            if missing.get('rows'):
                rows_str = ", ".join(str(row + 2) for row in missing['rows'][:5])  # Show first 5 rows
                content += f"  - Examples: Rows {rows_str}\n"
        else:
            content += "- **Missing IDs:** None\n"
        
        # Duplicate IDs
        duplicates = id_results.get('duplicates', {})
        if duplicates.get('count', 0) > 0:
            content += f"- **Duplicate IDs:** {duplicates['count']} ({duplicates['percentage']:.2%})\n"
            if duplicates.get('duplicates'):
                for dup in duplicates['duplicates'][:3]:  # Show first 3 duplicates
                    rows_str = ", ".join(str(row + 2) for row in dup['rows'])
                    content += f"  - ID '{dup['id']}' in rows: {rows_str}\n"
        else:
            content += "- **Duplicate IDs:** None\n"
        
        # ID Sequences
        sequences = id_results.get('sequences', {})
        if sequences and sequences.get('years'):
            content += "\n**ID Sequence Analysis by Year:**\n"
            content += "| Year | Count | Min Serial | Max Serial | Missing Values |\n"
            content += "|------|-------|------------|------------|----------------|\n"
            for year_data in sequences['years']:
                year = year_data['year']
                count = year_data['count']
                min_serial = year_data.get('min_serial', 'N/A')
                max_serial = year_data.get('max_serial', 'N/A')
                missing_count = year_data.get('missing_count', 0)
                content += f"| {year} | {count} | {min_serial} | {max_serial} | {missing_count} |\n"
        
        # ID Pattern Consistency
        pattern = id_results.get('pattern', {})
        if pattern:
            content += "\n**ID Pattern Consistency:**\n"
            if pattern.get('invalid_count', 0) > 0:
                content += f"- Invalid IDs: {pattern['invalid_count']}\n"
                for example in pattern.get('invalid_examples', [])[:3]:
                    content += f"  - ID '{example['id']}' in row {example['row'] + 2}\n"
            else:
                content += "- All IDs follow the expected pattern.\n"
        
        self.add_section("ID Analysis", content)
    
    def generate_date_analysis_section(self, column_name: str, title: str) -> None:
        """Generate a date analysis section for a given column."""
        date_results = self.results.get(column_name, {})
        if not date_results:
            return
        
        content = ""
        
        # Missing Dates
        missing = date_results.get('missing', {})
        if missing.get('count', 0) > 0:
            content += f"- **Missing Dates:** {missing['count']} ({missing['percentage']:.2%})\n"
            if missing.get('rows'):
                rows_str = ", ".join(str(row + 2) for row in missing['rows'][:5])
                content += f"  - Examples: Rows {rows_str}\n"
        else:
            content += "- **Missing Dates:** None\n"
        
        # Format Issues
        format_issues = date_results.get('format', {})
        if format_issues.get('invalid_count', 0) > 0:
            content += f"- **Invalid Date Formats:** {format_issues['invalid_count']}\n"
            for example in format_issues.get('invalid_examples', [])[:3]:
                content += f"  - ID '{example['id']}' has date '{example['date']}'\n"
        else:
            content += "- **Invalid Date Formats:** None\n"
        
        # Validity Issues (for birth dates)
        validity_issues = date_results.get('validity', {})
        if validity_issues:
            if validity_issues.get('too_old_count', 0) > 0:
                content += f"- **Unusually Old Dates:** {validity_issues['too_old_count']}\n"
                for example in validity_issues.get('too_old_examples', [])[:3]:
                    content += f"  - ID '{example['id']}' has date '{example['date']}'\n"
            if validity_issues.get('future_count', 0) > 0:
                content += f"- **Future Dates:** {validity_issues['future_count']}\n"
                for example in validity_issues.get('future_examples', [])[:3]:
                    content += f"  - ID '{example['id']}' has date '{example['date']}'\n"
        
        # Chronology Issues (for discharge dates)
        chronology_issues = date_results.get('chronology', {})
        if chronology_issues and chronology_issues.get('error_count', 0) > 0:
            content += f"- **Chronology Errors:** {chronology_issues['error_count']}\n"
            for example in chronology_issues.get('chronology_errors', [])[:3]:
                content += f"  - ID '{example['id']}' has admission '{example['admission_date']}' and discharge '{example['discharge_date']}'\n"
        
        # Age Statistics (for birth dates)
        age_stats = date_results.get('age', {})
        if age_stats and age_stats.get('count', 0) > 0:
            content += f"\n**Age Statistics:**\n"
            content += f"- Mean Age: {age_stats['mean_age']:.1f}\n"
            content += f"- Median Age: {age_stats['median_age']:.1f}\n"
            content += f"- Min Age: {age_stats['min_age']}\n"
            content += f"- Max Age: {age_stats['max_age']}\n"
        
        self.add_section(title, content)
    
    def generate_categorical_analysis_section(self, column_name: str, title: str) -> None:
        """Generate a categorical analysis section for a given column."""
        categorical_results = self.results.get(column_name, {})
        if not categorical_results:
            return
        
        content = ""
        
        # Missing Values
        missing = categorical_results.get('missing', {})
        if missing.get('count', 0) > 0:
            content += f"- **Missing Values:** {missing['count']} ({missing['percentage']:.2%})\n"
            # FIX: Check type before accessing rows or examples
            if 'examples' in missing and missing['examples']:
                if isinstance(missing['examples'][0], dict) and 'row' in missing['examples'][0]:
                    # Handle case where examples are dictionaries with 'row' key
                    rows_str = ", ".join(str(example['row'] + 2) for example in missing['examples'][:5])
                    content += f"  - Examples: Rows {rows_str}\n"
                else:
                    # Fallback case
                    content += f"  - Examples: {len(missing['examples'])} found\n"
        else:
            content += "- **Missing Values:** None\n"
        
        # Value Frequencies
        frequencies = categorical_results.get('frequency', {})
        if frequencies and frequencies.get('frequencies'):
            content += "\n**Value Frequencies:**\n"
            for value, details in frequencies['frequencies'].items():
                content += f"- {value}: {details['count']} ({details['percentage']:.2%})\n"
        
        # Unexpected Values
        unexpected = categorical_results.get('unexpected', {})
        if unexpected and unexpected.get('count', 0) > 0:
            content += f"\n**Unexpected Values:** {unexpected['count']} ({unexpected['percentage']:.2%})\n"
            for example in unexpected.get('examples', [])[:3]:
                content += f"  - ID '{example['id']}' has value '{example['value']}'\n"
        
        self.add_section(title, content)
    
    def generate_processo_analysis_section(self) -> None:
        """Generate the processo analysis section."""
        processo_results = self.results.get('processo', {})
        if not processo_results:
            return
        
        content = ""
        
        # Missing Values
        missing = processo_results.get('missing', {})
        if missing.get('count', 0) > 0:
            content += f"- **Missing Values:** {missing['count']} ({missing['percentage']:.2%})\n"
            # FIX: Check type before accessing rows or examples
            if 'examples' in missing and missing['examples']:
                if isinstance(missing['examples'][0], dict) and 'row' in missing['examples'][0]:
                    # Handle case where examples are dictionaries with 'row' key
                    rows_str = ", ".join(str(example['row'] + 2) for example in missing['examples'][:5])
                    content += f"  - Examples: Rows {rows_str}\n"
                else:
                    # Fallback case
                    content += f"  - Examples: {len(missing['examples'])} found\n"
        else:
            content += "- **Missing Values:** None\n"
        
        # Invalid Values
        invalid = processo_results.get('invalid', {})
        if invalid.get('count', 0) > 0:
            content += f"- **Invalid Values:** {invalid['count']} ({invalid['percentage']:.2%})\n"
            if invalid.get('examples'):
                for example in invalid['examples'][:3]:
                    content += f"  - ID '{example['id']}' has value '{example['value']}'\n"
        else:
            content += "- **Invalid Values:** None\n"
        
        self.add_section("Processo Analysis", content)
    
    def generate_nome_analysis_section(self) -> None:
        """Generate the nome analysis section."""
        nome_results = self.results.get('nome', {})
        if not nome_results:
            return
        
        content = ""
        
        # Missing Values
        missing = nome_results.get('missing', {})
        if missing.get('count', 0) > 0:
            content += f"- **Missing Values:** {missing['count']} ({missing['percentage']:.2%})\n"
            # FIX: Check type before accessing rows or examples
            if 'examples' in missing and missing['examples']:
                if isinstance(missing['examples'][0], dict) and 'row' in missing['examples'][0]:
                    # Handle case where examples are dictionaries with 'row' key
                    rows_str = ", ".join(str(example['row'] + 2) for example in missing['examples'][:5])
                    content += f"  - Examples: Rows {rows_str}\n"
                else:
                    # Fallback case
                    content += f"  - Examples: {len(missing['examples'])} found\n"
        else:
            content += "- **Missing Values:** None\n"
        
        self.add_section("Nome Analysis", content)
    
    def generate_report(self) -> str:
        """Generate the full Markdown report."""
        report = f"# Quality Control Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        # Add file information
        report += f"**File:** {self.file_path}\n\n"
        
        # Add filter information if applicable
        if self.filter_info.get("is_filtered", False):
            filter_type = self.filter_info.get("filter_type")
            filter_value = self.filter_info.get("filter_value")
            total_records = self.filter_info.get("total_records", 0)
            filtered_records = self.filter_info.get("filtered_records", 0)
            
            if filter_type == "single":
                report += f"**Filter:** Showing records from year {filter_value} only\n"
            elif filter_type == "range":
                report += f"**Filter:** Showing records from years {filter_value}\n"
            
            percentage = (filtered_records / total_records) * 100 if total_records > 0 else 0
            report += f"**Records:** {filtered_records:,} of {total_records:,} total ({percentage:.1f}%)\n\n"
        else:
            report += "**Scope:** Full database (no filters applied)\n\n"
        
        report += "\n\n".join(self.report_sections)
        return report
    
    def save_report(self, output_path: Path) -> None:
        """Save the report to a Markdown file."""
        report = self.generate_report()
        with open(output_path, "w") as f:
            f.write(report)