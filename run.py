#!/usr/bin/env python3

"""
Run script for Job Genie application

This script provides a simple way to start the Job Genie application.
"""

import os
import sys
import tkinter as tk

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import the main window
try:
    from ui.main_window import MainWindow
except ImportError as e:
    print(f"Error importing application modules: {e}")
    print("Make sure you have installed all required dependencies:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def main():
    """Run the main application."""
    try:
        # Create the root window
        root = tk.Tk()
        
        # Create the main window
        app = MainWindow(root)
        
        # Start the main loop
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()