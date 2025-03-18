"""
Main application entry point for Monkey Do.
"""
from core.paths import paths
from switch import main as show_menu


def main():
    """Main application entry point."""
    print(f"Starting Monkey Do application")
    print(f"Project root: {paths.ROOT}")
    print(f"Data directory: {paths.DATA}")
    print(f"Utility modules: {paths.UTILS}")
    print(f"Starting Monkey Do application")
    
    # Launch the interactive menu
    show_menu()
    # Add your application initialization here

if __name__ == "__main__":
    main()