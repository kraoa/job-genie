#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Skills Analyzer Module

This module analyzes job descriptions to identify required skills,
compares them with the user's resume skills, and suggests missing skills
along with relevant online certifications.
"""

import re
import nltk
import spacy
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Ensure NLTK data is downloaded
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    import os
    print("Downloading spaCy model...")
    os.system('python -m spacy download en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')


class SkillsAnalyzer:
    """Class to analyze job descriptions and suggest missing skills and certifications."""
    
    # Common technical skills categories and related skills
    TECH_SKILLS = {
        'programming_languages': [
            'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Ruby', 'Go', 'Swift', 'Kotlin', 'PHP',
            'TypeScript', 'Rust', 'Scala', 'Perl', 'R', 'MATLAB', 'Shell', 'SQL', 'HTML', 'CSS'
        ],
        'frameworks_libraries': [
            'React', 'Angular', 'Vue.js', 'Django', 'Flask', 'Spring', 'Express.js', 'TensorFlow',
            'PyTorch', 'Pandas', 'NumPy', 'scikit-learn', 'Node.js', 'jQuery', 'Bootstrap', 'Laravel',
            'ASP.NET', 'Ruby on Rails', 'Symfony', 'FastAPI'
        ],
        'databases': [
            'MySQL', 'PostgreSQL', 'MongoDB', 'SQLite', 'Oracle', 'SQL Server', 'Redis', 'Cassandra',
            'DynamoDB', 'Firebase', 'Elasticsearch', 'MariaDB', 'Neo4j', 'CouchDB', 'Firestore'
        ],
        'cloud_platforms': [
            'AWS', 'Azure', 'Google Cloud', 'Heroku', 'DigitalOcean', 'IBM Cloud', 'Oracle Cloud',
            'Alibaba Cloud', 'Salesforce', 'VMware', 'OpenStack', 'Kubernetes', 'Docker'
        ],
        'tools_platforms': [
            'Git', 'GitHub', 'GitLab', 'Bitbucket', 'JIRA', 'Confluence', 'Jenkins', 'Travis CI',
            'CircleCI', 'Docker', 'Kubernetes', 'Terraform', 'Ansible', 'Puppet', 'Chef', 'Prometheus',
            'Grafana', 'ELK Stack', 'Nginx', 'Apache'
        ],
        'soft_skills': [
            'Communication', 'Teamwork', 'Problem-solving', 'Critical thinking', 'Time management',
            'Leadership', 'Adaptability', 'Creativity', 'Emotional intelligence', 'Conflict resolution',
            'Decision making', 'Project management', 'Attention to detail', 'Customer service'
        ]
    }
    
    # Mapping of skills to recommended certifications
    CERTIFICATION_RECOMMENDATIONS = {
        # Programming Languages
        'Python': [
            {'name': 'Python Institute PCEP', 'provider': 'Python Institute', 'url': 'https://pythoninstitute.org/certification/pcep-certification-entry-level/'},
            {'name': 'Python Institute PCAP', 'provider': 'Python Institute', 'url': 'https://pythoninstitute.org/certification/pcap-certification-associate/'},
            {'name': 'Microsoft Certified: Azure Developer Associate', 'provider': 'Microsoft', 'url': 'https://learn.microsoft.com/en-us/certifications/azure-developer/'}
        ],
        'Java': [
            {'name': 'Oracle Certified Associate Java Programmer', 'provider': 'Oracle', 'url': 'https://education.oracle.com/oracle-certified-associate-java-se-8-programmer/trackp_333'},
            {'name': 'Oracle Certified Professional Java Programmer', 'provider': 'Oracle', 'url': 'https://education.oracle.com/oracle-certified-professional-java-se-8-programmer/trackp_357'}
        ],
        'JavaScript': [
            {'name': 'JavaScript Institute Certification', 'provider': 'W3Schools', 'url': 'https://www.w3schools.com/cert/cert_javascript.asp'},
            {'name': 'Certified JavaScript Developer', 'provider': 'DevSkiller', 'url': 'https://devskiller.com/certifications/'}
        ],
        
        # Frameworks & Libraries
        'React': [
            {'name': 'Meta React Developer Professional Certificate', 'provider': 'Coursera', 'url': 'https://www.coursera.org/professional-certificates/meta-front-end-developer'},
            {'name': 'React.js Certification', 'provider': 'W3Schools', 'url': 'https://www.w3schools.com/cert/cert_react.asp'}
        ],
        'Angular': [
            {'name': 'Angular Certification', 'provider': 'Angular.io', 'url': 'https://angular.io/guide/certification'},
            {'name': 'Angular Developer Certification', 'provider': 'Udemy', 'url': 'https://www.udemy.com/course/angular-certification/'}
        ],
        'Django': [
            {'name': 'Django Developer Certification', 'provider': 'Udemy', 'url': 'https://www.udemy.com/course/django-python-advanced/'},
            {'name': 'Python Django Full Stack Developer Bootcamp', 'provider': 'Udemy', 'url': 'https://www.udemy.com/course/python-and-django-full-stack-web-developer-bootcamp/'}
        ],
        
        # Databases
        'MySQL': [
            {'name': 'Oracle MySQL Database Administration', 'provider': 'Oracle', 'url': 'https://education.oracle.com/mysql-database-administration/pexam_1Z0-888'},
            {'name': 'MySQL Developer Certification', 'provider': 'Oracle', 'url': 'https://education.oracle.com/mysql-5-developer/pexam_1Z0-882'}
        ],
        'MongoDB': [
            {'name': 'MongoDB Certified Developer Associate', 'provider': 'MongoDB', 'url': 'https://university.mongodb.com/certification/developer/about'},
            {'name': 'MongoDB Certified DBA Associate', 'provider': 'MongoDB', 'url': 'https://university.mongodb.com/certification/dba/about'}
        ],
        
        # Cloud Platforms
        'AWS': [
            {'name': 'AWS Certified Cloud Practitioner', 'provider': 'Amazon', 'url': 'https://aws.amazon.com/certification/certified-cloud-practitioner/'},
            {'name': 'AWS Certified Solutions Architect - Associate', 'provider': 'Amazon', 'url': 'https://aws.amazon.com/certification/certified-solutions-architect-associate/'},
            {'name': 'AWS Certified Developer - Associate', 'provider': 'Amazon', 'url': 'https://aws.amazon.com/certification/certified-developer-associate/'}
        ],
        'Azure': [
            {'name': 'Microsoft Certified: Azure Fundamentals', 'provider': 'Microsoft', 'url': 'https://learn.microsoft.com/en-us/certifications/azure-fundamentals/'},
            {'name': 'Microsoft Certified: Azure Administrator Associate', 'provider': 'Microsoft', 'url': 'https://learn.microsoft.com/en-us/certifications/azure-administrator/'}
        ],
        'Google Cloud': [
            {'name': 'Google Cloud Digital Leader', 'provider': 'Google', 'url': 'https://cloud.google.com/certification/cloud-digital-leader'},
            {'name': 'Google Cloud Associate Engineer', 'provider': 'Google', 'url': 'https://cloud.google.com/certification/cloud-engineer'}
        ],
        
        # Tools & Platforms
        'Docker': [
            {'name': 'Docker Certified Associate', 'provider': 'Docker', 'url': 'https://training.mirantis.com/certification/dca-certification-exam/'},
            {'name': 'Docker and Kubernetes: The Complete Guide', 'provider': 'Udemy', 'url': 'https://www.udemy.com/course/docker-and-kubernetes-the-complete-guide/'}
        ],
        'Kubernetes': [
            {'name': 'Certified Kubernetes Administrator (CKA)', 'provider': 'CNCF', 'url': 'https://www.cncf.io/certification/cka/'},
            {'name': 'Certified Kubernetes Application Developer (CKAD)', 'provider': 'CNCF', 'url': 'https://www.cncf.io/certification/ckad/'}
        ],
        
        # Data Science & AI
        'Machine Learning': [
            {'name': 'Machine Learning Specialization', 'provider': 'Coursera', 'url': 'https://www.coursera.org/specializations/machine-learning-introduction'},
            {'name': 'Professional Certificate in Machine Learning and Artificial Intelligence', 'provider': 'edX', 'url': 'https://www.edx.org/professional-certificate/ibm-machine-learning'}
        ],
        'Data Science': [
            {'name': 'IBM Data Science Professional Certificate', 'provider': 'Coursera', 'url': 'https://www.coursera.org/professional-certificates/ibm-data-science'},
            {'name': 'Microsoft Certified: Azure Data Scientist Associate', 'provider': 'Microsoft', 'url': 'https://learn.microsoft.com/en-us/certifications/azure-data-scientist/'}
        ],
        'TensorFlow': [
            {'name': 'TensorFlow Developer Certificate', 'provider': 'TensorFlow', 'url': 'https://www.tensorflow.org/certificate'},
            {'name': 'DeepLearning.AI TensorFlow Developer Professional Certificate', 'provider': 'Coursera', 'url': 'https://www.coursera.org/professional-certificates/tensorflow-in-practice'}
        ],
        
        # General
        'Project Management': [
            {'name': 'Project Management Professional (PMP)', 'provider': 'PMI', 'url': 'https://www.pmi.org/certifications/project-management-pmp'},
            {'name': 'Certified Associate in Project Management (CAPM)', 'provider': 'PMI', 'url': 'https://www.pmi.org/certifications/certified-associate-capm'}
        ],
        'Agile': [
            {'name': 'Professional Scrum Master I (PSM I)', 'provider': 'Scrum.org', 'url': 'https://www.scrum.org/professional-scrum-certifications/professional-scrum-master-i-assessment'},
            {'name': 'PMI Agile Certified Practitioner (PMI-ACP)', 'provider': 'PMI', 'url': 'https://www.pmi.org/certifications/agile-acp'}
        ],
        'Cybersecurity': [
            {'name': 'CompTIA Security+', 'provider': 'CompTIA', 'url': 'https://www.comptia.org/certifications/security'},
            {'name': 'Certified Information Systems Security Professional (CISSP)', 'provider': 'ISC2', 'url': 'https://www.isc2.org/Certifications/CISSP'}
        ]
    }
    
    def __init__(self):
        """Initialize the SkillsAnalyzer."""
        self.stop_words = set(stopwords.words('english'))
        # Flatten the skills list for easier matching
        self.all_skills = []
        for category, skills in self.TECH_SKILLS.items():
            self.all_skills.extend(skills)
    
    def extract_skills_from_job_description(self, job_description):
        """Extract required skills from a job description.
        
        Args:
            job_description (str): The job description text
            
        Returns:
            list: List of identified skills
        """
        # Preprocess the job description
        job_description = job_description.lower()
        
        # Extract skills using pattern matching
        extracted_skills = set()
        
        # Check for each skill in our database
        for skill in self.all_skills:
            # Create a pattern that matches the skill as a whole word
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, job_description, re.IGNORECASE):
                extracted_skills.add(skill)
        
        # Use NLP to extract additional potential skills
        doc = nlp(job_description)
        
        # Look for noun phrases that might be skills
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.strip()
            # Filter out very short or very long phrases
            if 3 <= len(chunk_text) <= 30:
                # Check if this chunk might be a skill (e.g., contains technical terms)
                for skill in self.all_skills:
                    if skill.lower() in chunk_text.lower():
                        extracted_skills.add(skill)
        
        return list(extracted_skills)
    
    def identify_missing_skills(self, resume_skills, job_skills):
        """Identify skills that are in the job description but not in the resume.
        
        Args:
            resume_skills (list): Skills extracted from the resume
            job_skills (list): Skills extracted from the job description
            
        Returns:
            list: List of missing skills
        """
        # Normalize skills for comparison
        resume_skills_normalized = [skill.lower() for skill in resume_skills]
        
        # Find missing skills
        missing_skills = []
        for skill in job_skills:
            if skill.lower() not in resume_skills_normalized:
                missing_skills.append(skill)
        
        return missing_skills
    
    def suggest_certifications(self, missing_skills):
        """Suggest certifications based on missing skills.
        
        Args:
            missing_skills (list): List of skills missing from the resume
            
        Returns:
            dict: Dictionary mapping skills to recommended certifications
        """
        certification_suggestions = {}
        
        for skill in missing_skills:
            # Check if we have certification recommendations for this skill
            if skill in self.CERTIFICATION_RECOMMENDATIONS:
                certification_suggestions[skill] = self.CERTIFICATION_RECOMMENDATIONS[skill]
        
        return certification_suggestions
    
    def analyze(self, resume_skills, job_description):
        """Analyze the resume skills against the job description.
        
        Args:
            resume_skills (list): Skills extracted from the resume
            job_description (str): The job description text
            
        Returns:
            dict: Analysis results including missing skills and certification suggestions
        """
        # Extract skills from job description
        job_skills = self.extract_skills_from_job_description(job_description)
        
        # Identify missing skills
        missing_skills = self.identify_missing_skills(resume_skills, job_skills)
        
        # Suggest certifications for missing skills
        certification_suggestions = self.suggest_certifications(missing_skills)
        
        return {
            'job_skills': job_skills,
            'missing_skills': missing_skills,
            'certification_suggestions': certification_suggestions
        }