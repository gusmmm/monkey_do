"""
Core functionality for the Monkey Do project.

This package contains fundamental components used throughout
the application, including path management and configuration.
"""
from .paths import paths
from .config_gsheet import Config

__all__ = ['paths', 'Config']