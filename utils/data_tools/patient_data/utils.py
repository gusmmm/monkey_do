"""
Utility functions for patient data processing.

This module provides common utility functions used throughout
the patient data processing package.
"""
import logging
from typing import Optional

def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)
    
    # Only add handlers if they don't exist
    if not logger.handlers:
        # Configure logging if not already configured
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger