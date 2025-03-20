"""
Patient Data Processing Package

This package provides functionality to process patient data from CSV files,
convert it to structured Pydantic models, and save it as JSON files.
"""
from .models import Patient
from .processor import PatientDataProcessor
from .cli import process_patients_to_json

__all__ = ['Patient', 'PatientDataProcessor', 'process_patients_to_json']