"""
Patient data models using Pydantic.

This module defines the data models for patient information,
with validation rules and utility methods.
"""
import json
from datetime import datetime
from typing import Optional, Dict, Any, ClassVar

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict

# Import logging
from .utils import get_logger
logger = get_logger(__name__)

# Helper function for datetime serialization
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