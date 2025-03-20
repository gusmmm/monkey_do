"""
Patient data processing module.

This module contains the main PatientDataProcessor class for
converting CSV data to JSON files.
"""
import csv
import json
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

from core.paths import paths
from .models import Patient
from .filters import parse_year_filter, is_in_year_range
from .utils import get_logger

logger = get_logger(__name__)

class PatientDataProcessor:
    """
    Process patient data from CSV to JSON files.
    
    This class handles the extraction of patient data from a CSV file,
    validates and transforms it using Pydantic models, and saves each
    patient record as a JSON file.
    """
    
    def __init__(self, 
                 csv_path: Optional[Path] = None, 
                 year_filter: Optional[str] = None):
        """
        Initialize the processor with a CSV file path and optional year filter.
        
        Args:
            csv_path: Path to the CSV file. If None, uses the default location.
            year_filter: Optional year filter, either a single year (e.g., "25")
                         or a range (e.g., "25-20")
        """
        self.csv_path = csv_path or paths.SPREADSHEET_SOURCE / "Doentes.csv"
        self.json_dir = paths.DATA / "processed" / "json"
        self.year_filter = year_filter
        
        # Parse year filter if provided
        self.year_range = parse_year_filter(year_filter)
        
        # Ensure output directory exists
        self.json_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.total_records = 0
        self.filtered_records = 0
        self.processed_records = 0
        self.error_records = 0
        self.skipped_records = 0
    
    def get_filtered_rows(self) -> List[Dict[str, Any]]:
        """
        Read the CSV and return rows that match the year filter.
        
        Returns:
            List[Dict[str, Any]]: Filtered rows from CSV
        """
        filtered_rows = []
        
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    try:
                        # Create a temporary patient object to check year
                        patient = Patient(
                            _id=row.get('ID', ''),
                            nome=row.get('nome', '')  # nome is required, others are optional
                        )
                        
                        # Apply year filter if set
                        if is_in_year_range(patient, self.year_range):
                            filtered_rows.append(row)
                    except Exception:
                        # Skip invalid rows
                        pass
        except Exception as e:
            logger.error(f"Error filtering rows: {str(e)}")
            
        return filtered_rows
    
    def create_patient_from_row(self, row: Dict[str, Any]) -> Optional[Patient]:
        """
        Create a Patient object from a row of CSV data.
        
        Args:
            row: Dictionary representing a row from the CSV
            
        Returns:
            Optional[Patient]: Patient object or None if creation fails
        """
        try:
            return Patient(
                _id=row.get('ID', ''),
                processo=row.get('processo', None),
                nome=row.get('nome', ''),
                data_ent=row.get('data_ent', None),
                data_alta=row.get('data_alta', None),
                destino=row.get('destino', None),
                sexo=row.get('sexo', None),
                data_nasc=row.get('data_nasc', None),
                origem=row.get('origem', None)
            )
        except Exception as e:
            logger.error(f"Error creating patient from row: {str(e)}")
            return None
    
    def preview_json(self, patient: Patient) -> str:
        """
        Generate a formatted preview of the patient data as JSON.
        
        Args:
            patient: Patient object to preview
            
        Returns:
            str: Formatted JSON preview
        """
        try:
            # Convert to JSON
            patient_dict = json.loads(patient.model_dump_json())
            
            # Format with indentation for readability
            return json.dumps(patient_dict, indent=2)
        except Exception as e:
            logger.error(f"Error generating preview: {str(e)}")
            return f"Error generating preview: {str(e)}"
    
    def process_csv(self, preview_only: bool = False) -> bool:
        """
        Process the CSV file and convert records to JSON.
        
        Args:
            preview_only: If True, only generate a preview without writing files
            
        Returns:
            bool: True if processing was successful, False otherwise
        """
        logger.info(f"Starting processing of {self.csv_path}")
        
        try:
            # Get filtered rows
            rows = self.get_filtered_rows()
            self.filtered_records = len(rows)
            
            if not rows:
                logger.warning("No records match the specified filter or file is empty")
                print("\n⚠️ No records match the specified filter or file is empty")
                return False
            
            # Generate preview of first record if requested
            if preview_only and rows:
                first_patient = self.create_patient_from_row(rows[0])
                if first_patient:
                    return self.preview_json(first_patient)
                return "Unable to generate preview"
            
            # Process all matching rows
            for i, row in enumerate(rows, 1):
                try:
                    # Create Patient object
                    patient = self.create_patient_from_row(row)
                    if not patient:
                        self.error_records += 1
                        continue
                    
                    # Save to JSON file
                    self._save_json(patient)
                    self.processed_records += 1
                    
                    # Log progress periodically
                    if i % 100 == 0 or i == len(rows):
                        self._log_progress(i, len(rows))
                        
                except Exception as e:
                    logger.error(f"Error processing row {i}: {str(e)}")
                    self.error_records += 1
                        
            # Log final statistics
            self._log_final_stats()
            return True
                
        except FileNotFoundError:
            logger.error(f"CSV file not found: {self.csv_path}")
            print(f"\n❌ Error: CSV file not found at {self.csv_path}")
            return False
            
        except Exception as e:
            logger.error(f"Error processing CSV: {str(e)}")
            print(f"\n❌ Error processing CSV: {str(e)}")
            return False
    
    def _save_json(self, patient: Patient):
        """
        Save a Patient object as a JSON file.
        
        Args:
            patient: The Patient object to save
        """
        # Use the ID as the filename
        filename = f"{patient.ID}.json"
        file_path = self.json_dir / filename
        
        # Convert to JSON
        patient_json = patient.model_dump_json()
        
        # Save to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(patient_json)
    
    def _log_progress(self, current_record: int, total_records: int):
        """
        Log progress during processing.
        
        Args:
            current_record: The current record number being processed
            total_records: The total number of records to process
        """
        if total_records > 0:
            percentage = (current_record / total_records) * 100
            logger.info(f"Processed {current_record}/{total_records} records ({percentage:.1f}%)")
    
    def _log_final_stats(self):
        """Log final processing statistics."""
        logger.info(f"Processing complete. Summary:")
        logger.info(f"  - Filtered records: {self.filtered_records}")
        logger.info(f"  - Successfully processed: {self.processed_records}")
        logger.info(f"  - Errors: {self.error_records}")
        logger.info(f"  - JSON files saved to: {self.json_dir}")