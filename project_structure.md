# Job Genie Project Structure

```
job-genie/
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── app.py                # Main application entry point
├── utils/
│   ├── __init__.py
│   ├── resume_parser.py   # Resume parsing functionality
│   ├── job_parser.py      # Job description parsing functionality
│   ├── pdf_generator.py   # PDF generation functionality
│   └── tailoring.py       # Resume tailoring algorithm
├── ui/
│   ├── __init__.py
│   └── main_window.py     # UI components
└── tests/                 # Unit tests
    ├── __init__.py
    ├── test_resume_parser.py
    ├── test_job_parser.py
    ├── test_tailoring.py
    └── test_pdf_generator.py
```