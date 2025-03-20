#!/usr/bin/env python3
"""
Test script for the refactored patient_data package.

This script tests various components of the patient_data package
to ensure everything is working correctly after refactoring.
"""
import os
import sys
import csv  # Added missing csv import
import json
import shutil
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Test imports from the new structure
from utils.data_tools.patient_data.models import Patient
from utils.data_tools.patient_data.filters import parse_year_filter, is_in_year_range
from utils.data_tools.patient_data.processor import PatientDataProcessor

# Test back-compatibility imports
from utils.data_tools.patient_data import Patient as LegacyPatient
from utils.data_tools.patient_data import PatientDataProcessor as LegacyProcessor

# For colored output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_subheader(text):
    """Print a formatted subheader."""
    print(f"\n{Colors.OKBLUE}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'-' * len(text)}{Colors.ENDC}")

def print_success(message):
    """Print a success message."""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_warning(message):
    """Print a warning message."""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def print_error(message):
    """Print an error message."""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def test_patient_model():
    """Test the Patient model."""
    print_subheader("Testing Patient Model")
    
    # Test creating a valid patient
    print("Creating a valid patient...")
    try:
        patient = Patient(
            _id="2501",
            nome="John Doe",
            processo="12345",
            data_ent="01-01-2025",
            data_alta="15-01-2025",
            sexo="M",
            data_nasc="01-01-1980",
            destino="Home",
            origem="Emergency"
        )
        print_success("Patient created successfully")
        
        # Test ID field
        assert patient.ID == "2501"
        print_success("ID field is correct")
        
        # Test date parsing
        assert isinstance(patient.data_ent, datetime)
        assert patient.data_ent.day == 1
        assert patient.data_ent.month == 1
        assert patient.data_ent.year == 2025
        print_success("Date parsing works correctly")
        
        # Test gender validation
        assert patient.sexo == "M"
        print_success("Gender validation works correctly")
        
        # Test processo conversion
        assert patient.processo == 12345
        assert isinstance(patient.processo, int)
        print_success("Processo conversion works correctly")
        
        # Test year extraction
        assert patient.get_year_from_id() == 25
        print_success("Year extraction from ID works correctly")
        
        # Test JSON serialization
        json_data = patient.model_dump_json()
        data_dict = json.loads(json_data)
        assert data_dict["_id"] == "2501"
        assert data_dict["data_ent"] == "01-01-2025"
        print_success("JSON serialization works correctly")
        print(f"Sample JSON output:\n{json.dumps(data_dict, indent=2)}\n")
        
    except Exception as e:
        print_error(f"Error creating patient: {str(e)}")
        return False
    
    # Test validation errors
    print("\nTesting validation errors...")
    try:
        # Test missing ID
        try:
            invalid_patient = Patient(nome="No ID")
            print_error("Should have raised an error for missing ID")
            return False
        except ValueError:
            print_success("Correctly raised error for missing ID")
        
        # Test invalid gender
        patient = Patient(_id="2502", nome="Invalid Gender", sexo="X")
        assert patient.sexo is None
        print_success("Correctly handled invalid gender")
        
        # Test invalid date
        patient = Patient(_id="2503", nome="Invalid Date", data_ent="not-a-date")
        assert patient.data_ent is None
        print_success("Correctly handled invalid date")
        
    except Exception as e:
        print_error(f"Unexpected error in validation tests: {str(e)}")
        return False
    
    return True

def test_filters():
    """Test the year filter functionality."""
    print_subheader("Testing Year Filters")
    
    # Test parse_year_filter
    print("Testing parse_year_filter...")
    
    # Single year
    year_range = parse_year_filter("25")
    assert year_range == (25, 25)
    print_success("Single year filter parsed correctly")
    
    # Year range
    year_range = parse_year_filter("25-20")
    assert year_range == (25, 20)
    print_success("Year range filter parsed correctly")
    
    # Invalid format
    year_range = parse_year_filter("invalid")
    assert year_range is None
    print_success("Invalid filter handled correctly")
    
    # Test is_in_year_range
    print("\nTesting is_in_year_range...")
    
    # Create test patients
    patient_25 = Patient(_id="2501", nome="Patient 2025")
    patient_24 = Patient(_id="2401", nome="Patient 2024")
    patient_23 = Patient(_id="2301", nome="Patient 2023")
    
    # Test single year filter
    year_range = (25, 25)  # Only 2025
    assert is_in_year_range(patient_25, year_range) == True
    assert is_in_year_range(patient_24, year_range) == False
    print_success("Single year filter works correctly")
    
    # Test year range
    year_range = (25, 23)  # 2023 to 2025
    assert is_in_year_range(patient_25, year_range) == True
    assert is_in_year_range(patient_24, year_range) == True
    assert is_in_year_range(patient_23, year_range) == True
    
    # Test year outside range
    patient_22 = Patient(_id="2201", nome="Patient 2022")
    assert is_in_year_range(patient_22, year_range) == False
    print_success("Year range filter works correctly")
    
    return True

def test_processor(test_csv_path):
    """Test the PatientDataProcessor."""
    print_subheader("Testing PatientDataProcessor")
    
    # Create a test output directory
    test_output_dir = PROJECT_ROOT / "test_output" / "json"
    test_output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Test CSV: {test_csv_path}")
    print(f"Test output directory: {test_output_dir}")
    
    # Test with no filter
    print("\nTesting with no year filter...")
    processor = PatientDataProcessor(csv_path=test_csv_path)
    processor.json_dir = test_output_dir
    
    # Get filtered rows
    rows = processor.get_filtered_rows()
    print(f"Found {len(rows)} rows without filtering")
    
    if rows:
        # Test preview
        preview = processor.process_csv(preview_only=True)
        print(f"Preview generated: {len(preview) > 0}")
        print(f"Sample preview:\n{preview[:200]}...\n")
        
        # Test processing a few records
        processor.process_csv()
        print(f"Processed {processor.processed_records} records")
        print(f"Errors: {processor.error_records}")
        
        # Check if files were created
        json_files = list(test_output_dir.glob("*.json"))
        print(f"Created {len(json_files)} JSON files")
        
        if json_files:
            # Check content of first file
            first_file = json_files[0]
            print(f"First file: {first_file.name}")
            with open(first_file, 'r') as f:
                content = f.read()
                data = json.loads(content)
                print(f"File content looks valid: {'_id' in data}")
    else:
        print_warning("No rows found in test CSV, skipping processor tests")
    
    # Test year filter
    print("\nTesting with year filter...")
    # Get first year from available data for testing
    first_year = None
    if rows and len(rows) > 0:
        for row in rows:
            id_val = row.get('ID', '')
            if id_val and len(id_val) >= 2 and id_val[:2].isdigit():
                first_year = id_val[:2]
                break
    
    if first_year:
        print(f"Testing filter with year {first_year}")
        processor = PatientDataProcessor(csv_path=test_csv_path, year_filter=first_year)
        processor.json_dir = test_output_dir
        filtered_rows = processor.get_filtered_rows()
        print(f"Found {len(filtered_rows)} rows with year filter {first_year}")
    else:
        print_warning("Could not determine a valid year from data, skipping filter test")
    
    # Clean up
    print("\nCleaning up test output...")
    if test_output_dir.exists():
        for file in test_output_dir.glob("*.json"):
            file.unlink()
        try:
            test_output_dir.rmdir()
            test_output_dir.parent.rmdir()
        except OSError:
            pass  # Directory might not be empty or might be used
    
    return True

def test_legacy_imports():
    """Test backward compatibility imports."""
    print_subheader("Testing Legacy Imports")
    
    # Test Patient class
    assert LegacyPatient == Patient
    print_success("Legacy Patient import works")
    
    # Test PatientDataProcessor class
    assert LegacyProcessor == PatientDataProcessor
    print_success("Legacy PatientDataProcessor import works")
    
    return True

def create_test_csv():
    """Create a test CSV file for testing."""
    test_data_dir = PROJECT_ROOT / "test_data"
    test_data_dir.mkdir(exist_ok=True)
    
    test_csv_path = test_data_dir / "test_patients.csv"
    
    # Sample data
    data = [
        {
            "ID": "2501", "nome": "John Doe", "processo": "12345", 
            "data_ent": "01-01-2025", "data_alta": "15-01-2025", 
            "sexo": "M", "data_nasc": "01-01-1980", 
            "destino": "Home", "origem": "Emergency"
        },
        {
            "ID": "2502", "nome": "Jane Smith", "processo": "12346", 
            "data_ent": "02-01-2025", "data_alta": "16-01-2025", 
            "sexo": "F", "data_nasc": "02-02-1985", 
            "destino": "Transfer", "origem": "Clinic"
        },
        {
            "ID": "2401", "nome": "Bob Johnson", "processo": "12347", 
            "data_ent": "03-03-2024", "data_alta": "10-03-2024", 
            "sexo": "M", "data_nasc": "03-03-1990", 
            "destino": "Home", "origem": "Emergency"
        }
    ]
    
    # Write to CSV
    with open(test_csv_path, 'w', newline='') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    return test_csv_path

def run_tests():
    """Run all tests."""
    print_header("Patient Data Package Test Suite")
    
    tests = {
        "Model Tests": test_patient_model,
        "Filter Tests": test_filters,
        "Legacy Import Tests": test_legacy_imports
    }
    
    success_count = 0
    total_tests = len(tests)
    
    # Create test data
    print("Creating test CSV data...")
    test_csv_path = create_test_csv()
    print(f"Test CSV created at {test_csv_path}")
    
    # Add processor test
    tests["Processor Tests"] = lambda: test_processor(test_csv_path)
    total_tests = len(tests)
    
    # Run tests
    for name, test_func in tests.items():
        print_header(name)
        try:
            result = test_func()
            if result:
                success_count += 1
                print(f"\n{Colors.OKGREEN}✓ {name} PASSED{Colors.ENDC}")
            else:
                print(f"\n{Colors.FAIL}✗ {name} FAILED{Colors.ENDC}")
        except Exception as e:
            print(f"\n{Colors.FAIL}✗ {name} ERROR: {str(e)}{Colors.ENDC}")
    
    # Print summary
    print_header("Test Summary")
    print(f"Tests passed: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}All tests passed! The refactored code is working correctly.{Colors.ENDC}")
    else:
        print(f"\n{Colors.WARNING}{Colors.BOLD}Some tests failed. Please review the output.{Colors.ENDC}")
    
    # Clean up
    try:
        if test_csv_path.exists():
            test_csv_path.unlink()
        test_csv_path.parent.rmdir()
    except OSError:
        pass  # Directory might not be empty or might be used

if __name__ == "__main__":
    run_tests()