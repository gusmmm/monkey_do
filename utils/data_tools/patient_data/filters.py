"""
Data filtering utilities for patient data.

This module provides functions for filtering patient data by year
and other criteria.
"""
from typing import Optional, Tuple, Dict, Any, List
from .models import Patient
from .utils import get_logger

logger = get_logger(__name__)

def parse_year_filter(year_filter: Optional[str]) -> Optional[Tuple[int, int]]:
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


def is_in_year_range(patient: Patient, year_range: Optional[Tuple[int, int]]) -> bool:
    """
    Check if a patient record falls within the specified year range.
    
    Args:
        patient: Patient object to check
        year_range: Tuple of (start_year, end_year) or None
        
    Returns:
        bool: True if in range or no filter set, False otherwise
    """
    # If no year range filter, include all records
    if not year_range:
        return True
        
    # Get year from ID
    year = patient.get_year_from_id()
    if year is None:
        # If year can't be determined, skip record
        return False
        
    # Check if year is within range (inclusive)
    start_year, end_year = year_range
    return end_year <= year <= start_year