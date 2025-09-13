#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Skills CLI

Command-line interface for analyzing skills from a resume against a job description,
identifying missing skills, and suggesting relevant online certifications.
"""

import os
import sys
import argparse
from utils.resume_parser import ResumeParser
from utils.skills_analyzer import SkillsAnalyzer


def main():
    """Main entry point for the CLI application."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Analyze resume skills against job description and suggest certifications."
    )
    parser.add_argument(
        "resume_path",
        help="Path to the master resume file (PDF or DOCX)"
    )
    parser.add_argument(
        "--job_file",
        help="Path to a text file containing the job description"
    )
    parser.add_argument(
        "--job_text",
        help="Job description text"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not os.path.isfile(args.resume_path):
        print(f"Error: Resume file '{args.resume_path}' not found.")
        sys.exit(1)
    
    if not args.job_file and not args.job_text:
        print("Error: Please provide either a job description file (--job_file) or job description text (--job_text).")
        sys.exit(1)
    
    # Get job description text
    job_description = ""
    if args.job_file:
        if not os.path.isfile(args.job_file):
            print(f"Error: Job description file '{args.job_file}' not found.")
            sys.exit(1)
        try:
            with open(args.job_file, 'r', encoding='utf-8') as file:
                job_description = file.read()
        except Exception as e:
            print(f"Error reading job description file: {str(e)}")
            sys.exit(1)
    else:
        job_description = args.job_text
    
    try:
        # Parse resume
        print("Parsing resume...")
        resume_parser = ResumeParser()
        resume_data = resume_parser.parse(args.resume_path)
        
        # Extract skills from resume
        resume_skills = resume_data.get('skills', [])
        print(f"\nExtracted {len(resume_skills)} skills from resume:")
        for skill in resume_skills:
            print(f"  • {skill}")
        
        # Analyze skills against job description
        print("\nAnalyzing skills against job description...")
        skills_analyzer = SkillsAnalyzer()
        analysis_results = skills_analyzer.analyze(resume_skills, job_description)
        
        # Display job skills
        job_skills = analysis_results['job_skills']
        print(f"\nIdentified {len(job_skills)} skills in job description:")
        for skill in job_skills:
            print(f"  • {skill}")
        
        # Display missing skills
        missing_skills = analysis_results['missing_skills']
        print(f"\nIdentified {len(missing_skills)} missing skills:")
        if not missing_skills:
            print("  No missing skills! Your resume already covers all the skills mentioned in the job description.")
        else:
            for skill in missing_skills:
                print(f"  • {skill}")
        
        # Display certification recommendations
        cert_suggestions = analysis_results['certification_suggestions']
        print("\nCertification recommendations for missing skills:")
        if not cert_suggestions:
            print("  No specific certification recommendations for the identified missing skills.")
        else:
            for skill, certifications in cert_suggestions.items():
                print(f"\nFor {skill}:")
                for cert in certifications:
                    print(f"  • {cert['name']}")
                    print(f"    Provider: {cert['provider']}")
                    print(f"    URL: {cert['url']}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()