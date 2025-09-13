#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Job Genie - Resume Tailoring Application

This application takes a master resume and job description to create
a tailored resume that highlights the most relevant qualifications.
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from ui.main_window import MainWindow


def main():
    """Main entry point for the application."""
    # Create the main application window
    root = tk.Tk()
    root.title("Job Genie - Resume Tailoring Application")
    
    # Set window size and position it in the center of the screen
    window_width = 900
    window_height = 700
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    # Create and pack the main window components
    app = MainWindow(root)
    app.pack(fill=tk.BOTH, expand=True)
    
    # Start the application main loop
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
        sys.exit(1)