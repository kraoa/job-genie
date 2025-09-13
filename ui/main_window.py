#!/usr/bin/env python3

"""
Main Window UI Module

This module provides the main window UI for the Job Genie application.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class MainWindow:
    def __init__(self, root):
        """Initialize the main window UI.
        
        Args:
            root: The tkinter root window
        """
        self.root = root
        self.root.title("Job Genie - Resume Tailoring Tool")
        self.root.geometry("800x600")
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header
        self.create_header()
        
        # Create input section
        self.create_input_section()
        
        # Create action buttons
        self.create_action_buttons()
    
    def create_header(self):
        """Create the header section."""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(header_frame, text="Job Genie", font=("Arial", 18, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Subtitle
        subtitle_label = ttk.Label(header_frame, text="Tailor your resume to match job descriptions", font=("Arial", 10))
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0), pady=(5, 0))
    
    def create_input_section(self):
        """Create the input section."""
        input_frame = ttk.LabelFrame(self.main_frame, text="Input Files and Job Description")
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Resume file input
        resume_frame = ttk.Frame(input_frame, padding="5")
        resume_frame.pack(fill=tk.X, pady=5)
        
        resume_label = ttk.Label(resume_frame, text="Master Resume:")
        resume_label.pack(side=tk.LEFT)
        
        self.resume_path_var = tk.StringVar()
        resume_entry = ttk.Entry(resume_frame, textvariable=self.resume_path_var, width=50)
        resume_entry.pack(side=tk.LEFT, padx=(5, 5), fill=tk.X, expand=True)
        
        resume_button = ttk.Button(resume_frame, text="Browse", command=self.browse_resume)
        resume_button.pack(side=tk.LEFT)
        
        # Job description input
        job_frame = ttk.Frame(input_frame, padding="5")
        job_frame.pack(fill=tk.X, pady=5)
        
        job_label = ttk.Label(job_frame, text="Job URL:")
        job_label.pack(side=tk.LEFT)
        
        self.job_url_var = tk.StringVar()
        job_entry = ttk.Entry(job_frame, textvariable=self.job_url_var, width=50)
        job_entry.pack(side=tk.LEFT, padx=(5, 5), fill=tk.X, expand=True)
        
        # Job description text area
        job_text_frame = ttk.Frame(input_frame, padding="5")
        job_text_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        job_text_label = ttk.Label(job_text_frame, text="Or paste job description:")
        job_text_label.pack(anchor=tk.W)
        
        self.job_text = tk.Text(job_text_frame, height=10, width=50)
        self.job_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
    
    def create_action_buttons(self):
        """Create the action buttons section."""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Generate button
        generate_button = ttk.Button(button_frame, text="Generate Tailored Resume", command=self.generate_resume)
        generate_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        clear_button = ttk.Button(button_frame, text="Clear All", command=self.clear_all)
        clear_button.pack(side=tk.LEFT)
    
    def browse_resume(self):
        """Open file dialog to select master resume."""
        filetypes = [
            ("PDF files", "*.pdf"),
            ("Word documents", "*.docx"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(title="Select Master Resume", filetypes=filetypes)
        if filename:
            self.resume_path_var.set(filename)
    
    def generate_resume(self):
        """Generate tailored resume based on inputs."""
        # Get resume path
        resume_path = self.resume_path_var.get().strip()
        if not resume_path:
            messagebox.showerror("Error", "Please select a master resume file.")
            return
        
        # Get job description
        job_url = self.job_url_var.get().strip()
        job_text = self.job_text.get("1.0", tk.END).strip()
        
        if not job_url and not job_text:
            messagebox.showerror("Error", "Please provide a job URL or paste a job description.")
            return
        
        # Show a message that this is a demo
        messagebox.showinfo("Demo", "This is a demo version. In a full implementation, this would generate a tailored resume based on your inputs.")
    
    def clear_all(self):
        """Clear all input fields."""
        self.resume_path_var.set("")
        self.job_url_var.set("")
        self.job_text.delete("1.0", tk.END)