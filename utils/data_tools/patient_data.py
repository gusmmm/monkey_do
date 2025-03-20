"""
Patient Data Processor Module

This module provides functionality to process patient data from CSV files,
convert it to structured Pydantic models, and save it as JSON files.
The JSON files are prepared for MongoDB import.

Features:
- Pydantic models for data validation and structure
- CSV to JSON conversion with error handling
- Date format validation and parsing
- Progress tracking during processing
- Year filtering options (single year or range)
- Preview capability before processing
"""
import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Union, Tuple, ClassVar, Callable

# Import Pydantic for data modeling
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("PatientDataProcessor")

# Import project paths
from core.paths import paths

# Custom JSON encoder for datetime objects
def datetime_to_string(dt: Optional[datetime]) -> Optional[str]:
    """Convert datetime to string in dd-mm-yyyy format."""
    if dt is None:
        return None
    return dt.strftime("%d-%m-%Y")

class Patient(BaseModel):
    """
    Pydantic model for patient data.
    
    This model defines the structure and validation rules for patient data.
    It includes fields for patient identification, admission and discharge dates,
    and other relevant information.
    """
    # ID field serves as both the MongoDB _id and the unique identifier
    ID: str = Field(alias="_id")
    
    # Patient record number (processo)
    processo: Optional[int] = None
    
    # Patient name
    nome: str
    
    # Admission date (dd-mm-yyyy)
    data_ent: Optional[datetime] = None
    
    # Discharge date (dd-mm-yyyy)
    data_alta: Optional[datetime] = None
    
    # Destination after discharge
    destino: Optional[str] = None
    
    # Gender (M or F)
    sexo: Optional[str] = None
    
    # Birth date (dd-mm-yyyy)
    data_nasc: Optional[datetime] = None
    
    # Origin/source of admission
    origem: Optional[str] = None
    
    # Configuration for the Pydantic model
    model_config: ClassVar[ConfigDict] = ConfigDict(
        # Allow population by name or alias
        populate_by_name=True
    )
    
    @field_validator('processo')
    @classmethod
    def validate_processo(cls, v: Any) -> Optional[int]:
        """Validate processo field to ensure it's a valid integer."""
        if v is None:
            return None
        
        # Convert to string first to clean any non-numeric characters
        if isinstance(v, str):
            # Remove any non-digit characters
            v = ''.join(c for c in v if c.isdigit())
            
            # If empty after cleaning, return None
            if not v:
                return None
            
            # Convert to integer
            try:
                return int(v)
            except ValueError:
                return None
        
        # If already an integer, return as is
        return v
    
    @field_validator('sexo')
    @classmethod
    def validate_sexo(cls, v: Any) -> Optional[str]:
        """Validate sex field to ensure it's either 'M' or 'F'."""
        if v is None:
            return None
        
        v = str(v).strip().upper()
        if v in ['M', 'F']:
            return v
        
        # If invalid, return None and log warning
        logger.warning(f"Invalid value for sexo: {v}. Must be 'M' or 'F'.")
        return None
    
    @field_validator('data_ent', 'data_alta', 'data_nasc', mode='before')
    @classmethod
    def parse_dates(cls, v: Any) -> Optional[datetime]:
        """
        Parse dates from dd-mm-yyyy format to datetime objects.
        
        This validator handles various date formats and errors.
        """
        if not v or v == '':
            return None
            
        # Handle dates in dd-mm-yyyy format
        try:
            # Try parsing with standard format
            return datetime.strptime(v, "%d-%m-%Y")
        except ValueError:
            try:
                # Try alternative format with single digit day/month
                if '-' in v:
                    day, month, year = v.split('-')
                    # Ensure 4-digit year
                    if len(year) == 2:
                        year = "20" + year
                    return datetime(int(year), int(month), int(day))
            except (ValueError, TypeError):
                logger.warning(f"Invalid date format: {v}")
                return None
        except TypeError:
            logger.warning(f"Invalid date type: {v}")
            return None
    
    @model_validator(mode='before')
    @classmethod
    def ensure_valid_id(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure ID is present and valid."""
        # Check for _id first (for MongoDB compatibility)
        id_value = data.get('_id')
        
        # If not found, check for ID
        if id_value is None:
            id_value = data.get('ID')
        
        if not id_value:
            raise ValueError("ID field is required")
        
        # Ensure ID is a string and set both fields
        id_value = str(id_value)
        data['_id'] = id_value
        data['ID'] = id_value
        
        return data
    
    def get_year_from_id(self) -> Optional[int]:
        """
        Extract the year part from the patient ID.
        
        The year is assumed to be the first two digits of the ID.
        Returns the year as a 2-digit integer (e.g., 25 for 2025)
        
        Returns:
            Optional[int]: The 2-digit year or None if not extractable
        """
        if not self.ID or len(self.ID) < 2:
            return None
            
        try:
            # Extract first 2 characters and convert to int
            year_part = self.ID[:2]
            return int(year_part)
        except ValueError:
            return None
    
    def model_dump_json(self, **kwargs) -> str:
        """
        Serialize model to JSON string with proper datetime handling.
        """
        # Get the model as a dict
        data = self.model_dump(by_alias=True, **kwargs)
        
        # Handle datetime fields manually
        for field_name, field_value in data.items():
            if isinstance(field_value, datetime):
                data[field_name] = datetime_to_string(field_value)
        
        # Ensure _id is in the output
        if '_id' not in data and 'ID' in data:
            data['_id'] = data['ID']
        
        # Convert to JSON
        return json.dumps(data)


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
        self.year_range = self._parse_year_filter(year_filter)
        
        # Ensure output directory exists
        self.json_dir.mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.total_records = 0
        self.filtered_records = 0
        self.processed_records = 0
        self.error_records = 0
        self.skipped_records = 0
        
    def _parse_year_filter(self, year_filter: Optional[str]) -> Optional[Tuple[int, int]]:
        """
        Parse the year filter string into a tuple of (start_year, end_year).
        
        Args:
            year_filter: Year filter string, either a single year or range
            
        Returns:
            Optional[Tuple[int, int]]: Tuple of (start_year, end_year) or None
        """
        if not year_filter:
            return None
            
        try:
            # Handle year range (e.g., "25-20")
            if "-" in year_filter:
                start_year, end_year = year_filter.split("-")
                
                # Validate year parts
                if not (start_year.isdigit() and end_year.isdigit()):
                    logger.error(f"Invalid year format in range: {year_filter}")
                    return None
                    
                # Convert to integers
                start_year_num = int(start_year)
                end_year_num = int(end_year)
                
                # Ensure start_year is the higher value (e.g., 25 in "25-20")
                if start_year_num < end_year_num:
                    start_year_num, end_year_num = end_year_num, start_year_num
                    
                return (start_year_num, end_year_num)
                
            # Handle single year (e.g., "25")
            elif year_filter.isdigit():
                year_num = int(year_filter)
                # For single year, both start and end are the same
                return (year_num, year_num)
                
            else:
                logger.error(f"Invalid year filter format: {year_filter}")
                return None
                
        except Exception as e:
            logger.error(f"Error parsing year filter: {str(e)}")
            return None
            
    def is_in_year_range(self, patient: Patient) -> bool:
        """
        Check if a patient record falls within the specified year range.
        
        Args:
            patient: Patient object to check
            
        Returns:
            bool: True if in range or no filter set, False otherwise
        """
        # If no year range filter, include all records
        if not self.year_range:
            return True
            
        # Get year from ID
        year = patient.get_year_from_id()
        if year is None:
            # If year can't be determined, skip record
            return False
            
        # Check if year is within range (inclusive)
        start_year, end_year = self.year_range
        return end_year <= year <= start_year
    
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
                        if self.is_in_year_range(patient):
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


def process_patients_to_json():
    """
    Entry point function to process patient data from CSV to JSON.
    
    This function creates a PatientDataProcessor and runs the conversion process.
    """
    print("\n" + "="*80)
    print("🏥 PATIENT DATA PROCESSOR - CSV TO JSON 🏥".center(80))
    print("="*80 + "\n")
    
    print("This tool will process patient records from the Doentes.csv file")
    print("and convert them to individual JSON files ready for MongoDB import.\n")
    
    # Get year filter choice
    print("Choose processing scope:")
    print("  1. Process all records")
    print("  2. Process records from a specific year (e.g., 25 for 2025)")
    print("  3. Process records from a year range (e.g., 25-20 for 2025 to 2020)")
    print("\nNote: Years are determined by the first 2 digits of the ID column.")
    
    year_filter = None
    
    while True:
        choice = input("\n👉 Enter your choice [1-3]: ").strip()
        
        if choice == "1":
            break
            
        elif choice == "2":
            year = input("👉 Enter year (e.g., 25 for 2025): ").strip()
            if year.isdigit() and len(year) <= 2:
                year_filter = year
                break
            else:
                print("❌ Invalid year format. Please enter a 1-2 digit number (e.g., 25)")
                
        elif choice == "3":
            year_range = input("👉 Enter year range (e.g., 25-20 for 2025 to 2020): ").strip()
            if "-" in year_range:
                parts = year_range.split("-")
                if len(parts) == 2 and all(part.isdigit() and len(part) <= 2 for part in parts):
                    year_filter = year_range
                    break
            print("❌ Invalid year range format. Please use format YY-YY (e.g., 25-20)")
            
        else:
            print("❌ Please enter a number between 1 and 3")
    
    # Create processor with filter
    processor = PatientDataProcessor(year_filter=year_filter)
    
    # Show filter information
    print(f"\n📂 Source CSV: {processor.csv_path}")
    print(f"📂 Output directory: {processor.json_dir}")
    
    if year_filter:
        if "-" in year_filter:
            start, end = year_filter.split("-")
            print(f"🔍 Filter: Records from years 20{end} to 20{start}")
        else:
            print(f"🔍 Filter: Records from year 20{year_filter} only")
    else:
        print("🔍 Filter: All records")
    
    # Generate preview of first record that would be processed
    print("\nGenerating preview of first record to be processed...")
    preview = processor.process_csv(preview_only=True)
    
    if not preview:
        print("\n❌ No records match the specified filter or an error occurred.")
        return
        
    print("\n📝 PREVIEW OF FIRST RECORD:")
    print("-" * 40)
    print(preview)
    print("-" * 40)
    
    # Confirm before proceeding
    response = input("\nDoes this look correct? Proceed with processing? [Y/n]: ").lower()
    if response in ['', 'y', 'yes']:
        print("\nStarting conversion process...")
        success = processor.process_csv()
        
        if success:
            print("\n✅ Processing complete!")
            print(f"Successfully processed {processor.processed_records} patient records")
            if processor.error_records > 0:
                print(f"⚠️ Encountered {processor.error_records} errors during processing")
            print(f"\nJSON files are saved in: {processor.json_dir}")
        else:
            print("\n❌ Processing failed. Check the logs for details.")
    else:
        print("\n❌ Operation cancelled by user.")


if __name__ == "__main__":
    # When run directly, process the patient data
    process_patients_to_json()