"""
Core package for the Monkey Do project.
Contains fundamental components and utilities used throughout the application.
"""
from .paths import paths, ProjectPaths

# Export the paths singleton for easy imports
__all__ = ['paths', 'ProjectPaths']