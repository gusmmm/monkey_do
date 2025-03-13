"""
Main application entry point for Monkey Do.
"""
from core.paths import paths

def main():
    """Main application entry point."""
    print(f"Starting Monkey Do application")
    print(f"Project root: {paths.ROOT}")
    print(f"Data directory: {paths.DATA}")
    print(f"Utility modules: {paths.UTILS}")
    
    # Add your application initialization here

if __name__ == "__main__":
    main()