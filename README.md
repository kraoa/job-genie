# Job Genie

Job Genie is an application that takes a master resume (4+ pages) and creates a new tailored resume according to the skills and qualifications of a job application link. The application analyzes both your comprehensive resume and the job description to generate a targeted 1-2 page PDF resume that highlights your most relevant qualifications.

## Original Requirements

1. Master Resume of 5 pages (Details of everything)
2. Compare that with the job description and condense it to 1-2 pages based on the main key requirements
3. Customizable template
4. Suggest missing skills and based on that suggest online certifications
5. Auto PDF export
6. AI interview agent

## Features

- **Resume Parsing**: Extract information from your master resume including education, skills, projects, work experience, internships, and awards.
- **Job Description Analysis**: Parse job descriptions to identify key requirements, skills, and qualifications.
- **Smart Tailoring**: Match your qualifications with job requirements to create a customized resume.
- **PDF Generation**: Generate a professional 1-2 page PDF resume.
- **User-Friendly Interface**: Simple and intuitive interface for easy use.
- **Skills Gap Analysis**: Identify missing skills and suggest relevant online certifications.

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/job-genie.git
   cd job-genie
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Download required NLTK data and spaCy models:
   ```python
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
   python -m spacy download en_core_web_sm
   ```

## Usage

1. Run the application:
   ```
   python app.py
   ```

2. Upload your master resume (PDF or DOCX format).

3. Enter the job posting URL or paste the job description text.

4. Click "Generate Tailored Resume" to create your customized resume.

5. Save the generated PDF to your desired location.

## How It Works

1. **Resume Parsing**: The application extracts structured information from your master resume, categorizing content into sections like education, skills, experience, etc.

2. **Job Description Analysis**: Using natural language processing, the application identifies key requirements, preferred skills, and qualifications from the job posting.

3. **Matching Algorithm**: A sophisticated algorithm matches your qualifications with job requirements, ranking your experiences and skills by relevance.

4. **Content Selection**: The most relevant content is selected to create a concise 1-2 page resume.

5. **PDF Generation**: A professionally formatted PDF resume is generated with your tailored content.