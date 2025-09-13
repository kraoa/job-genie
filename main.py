#!/usr/bin/env python3

"""
Job Genie - Resume Tailoring Application

This application helps users tailor their resumes to specific job descriptions
by highlighting relevant skills and experiences.
"""

import os
import sys
import tkinter as tk

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow


def main():
    """Run the main application."""
    # Create the root window
    root = tk.Tk()
    
    # Create the main window
    app = MainWindow(root)
    
    # Start the main loop
    root.mainloop()


if __name__ == "__main__":
    main()