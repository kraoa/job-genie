#!/usr/bin/env python3

"""
Main Window UI Module

This module provides the main window UI for the Job Genie application.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from utils.resume_parser import ResumeParser
from utils.skills_analyzer import SkillsAnalyzer

class MainWindow:
    def __init__(self, root):
        """Initialize the main window UI.
        
        Args:
            root: The tkinter root window
        """
        self.root = root
        self.root.title("Job Genie - Resume Tailoring Tool")
        self.root.geometry("800x600")
        
        # Initialize parsers and analyzers
        self.resume_parser = ResumeParser()
        self.skills_analyzer = SkillsAnalyzer()
        
        # Store parsed data
        self.resume_data = None
        self.job_analysis = None
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create header
        self.create_header()
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 10))
        
        # Create tabs
        self.input_tab = ttk.Frame(self.notebook)
        self.skills_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.input_tab, text="Resume & Job")
        self.notebook.add(self.skills_tab, text="Skills Analysis")
        
        # Create input section in the first tab
        self.create_input_section()
        
        # Create skills analysis section in the second tab
        self.create_skills_analysis_section()
        
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
        input_frame = ttk.LabelFrame(self.input_tab, text="Input Files and Job Description")
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
    
    def create_skills_analysis_section(self):
        """Create the skills analysis section."""
        # Create frame for skills analysis
        skills_frame = ttk.LabelFrame(self.skills_tab, text="Skills Analysis & Certification Recommendations")
        skills_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create left and right frames for the split view
        left_frame = ttk.Frame(skills_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_frame = ttk.Frame(skills_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Missing Skills section (left side)
        missing_skills_label = ttk.Label(left_frame, text="Missing Skills:")
        missing_skills_label.pack(anchor=tk.W, pady=(5, 5))
        
        self.missing_skills_text = tk.Text(left_frame, height=10, width=30)
        self.missing_skills_text.pack(fill=tk.BOTH, expand=True)
        self.missing_skills_text.config(state=tk.DISABLED)
        
        # Certification Recommendations section (right side)
        cert_label = ttk.Label(right_frame, text="Recommended Certifications:")
        cert_label.pack(anchor=tk.W, pady=(5, 5))
        
        self.cert_text = tk.Text(right_frame, height=10, width=40)
        self.cert_text.pack(fill=tk.BOTH, expand=True)
        self.cert_text.config(state=tk.DISABLED)
        
        # Analyze button
        analyze_button = ttk.Button(skills_frame, text="Analyze Skills", command=self.analyze_skills)
        analyze_button.pack(pady=(10, 5))
    
    def create_action_buttons(self):
        """Create the action buttons section."""
        button_frame = ttk.Frame(self.input_tab)
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
        
        try:
            # Parse the resume
            self.resume_data = self.resume_parser.parse(resume_path)
            
            # Show a message that this is a demo
            messagebox.showinfo("Demo", "This is a demo version. In a full implementation, this would generate a tailored resume based on your inputs.")
            
            # Switch to the skills analysis tab
            self.notebook.select(1)  # Select the second tab (index 1)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while parsing the resume: {str(e)}")
    
    def analyze_skills(self):
        """Analyze skills based on resume and job description."""
        # Check if resume has been parsed
        if not self.resume_data:
            messagebox.showerror("Error", "Please generate a tailored resume first.")
            return
        
        # Get job description
        job_text = self.job_text.get("1.0", tk.END).strip()
        if not job_text:
            job_url = self.job_url_var.get().strip()
            if not job_url:
                messagebox.showerror("Error", "Please provide a job description.")
                return
            # In a full implementation, we would fetch the job description from the URL
            messagebox.showinfo("Demo", "In a full implementation, this would fetch the job description from the URL.")
            return
        
        try:
            # Get skills from resume
            resume_skills = self.resume_data.get('skills', [])
            
            # Analyze skills
            self.job_analysis = self.skills_analyzer.analyze(resume_skills, job_text)
            
            # Display missing skills
            self.display_missing_skills(self.job_analysis['missing_skills'])
            
            # Display certification recommendations
            self.display_certification_recommendations(self.job_analysis['certification_suggestions'])
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during skills analysis: {str(e)}")
    
    def display_missing_skills(self, missing_skills):
        """Display missing skills in the UI."""
        self.missing_skills_text.config(state=tk.NORMAL)
        self.missing_skills_text.delete("1.0", tk.END)
        
        if not missing_skills:
            self.missing_skills_text.insert(tk.END, "No missing skills identified. Your resume already covers all the skills mentioned in the job description!")
        else:
            for skill in missing_skills:
                self.missing_skills_text.insert(tk.END, f"• {skill}\n")
        
        self.missing_skills_text.config(state=tk.DISABLED)
    
    def display_certification_recommendations(self, cert_suggestions):
        """Display certification recommendations in the UI."""
        self.cert_text.config(state=tk.NORMAL)
        self.cert_text.delete("1.0", tk.END)
        
        if not cert_suggestions:
            self.cert_text.insert(tk.END, "No specific certification recommendations for the identified missing skills.")
        else:
            for skill, certifications in cert_suggestions.items():
                self.cert_text.insert(tk.END, f"For {skill}:\n")
                for cert in certifications:
                    self.cert_text.insert(tk.END, f"• {cert['name']}\n  Provider: {cert['provider']}\n  URL: {cert['url']}\n\n")
        
        self.cert_text.config(state=tk.DISABLED)
    
    def clear_all(self):
        """Clear all input fields."""
        self.resume_path_var.set("")
        self.job_url_var.set("")
        self.job_text.delete("1.0", tk.END)
        
        # Clear analysis results
        self.resume_data = None
        self.job_analysis = None
        
        # Clear skills analysis text fields
        self.missing_skills_text.config(state=tk.NORMAL)
        self.missing_skills_text.delete("1.0", tk.END)
        self.missing_skills_text.config(state=tk.DISABLED)
        
        self.cert_text.config(state=tk.NORMAL)
        self.cert_text.delete("1.0", tk.END)
        self.cert_text.config(state=tk.DISABLED)
        
        # Switch back to the first tab
        self.notebook.select(0)