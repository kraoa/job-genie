# Job Genie - URL Content Scraper

A Python script to download text content from a list of URLs. This tool is useful for collecting job descriptions from multiple sources for further analysis.

## Features

- Reads URLs from a text file (one URL per line)
- Downloads the text content from each URL
- Cleans the content by removing scripts and style elements
- Saves each job description to a separate text file
- Provides a summary of successful and failed downloads

## Requirements

- Python 3.6 or higher
- Required Python packages:
  - requests
  - beautifulsoup4

## Installation

1. Clone this repository or download the script
2. Install the required packages:

```bash
pip install requests beautifulsoup4
```

## Usage

1. Create a text file containing URLs, with one URL per line. For example, `job_urls.txt`:

```
https://example.com/job/software-engineer
https://example.com/job/data-scientist
https://anothersite.com/careers/developer
```

2. Run the script with the path to your URL file:

```bash
python job_scraper.py job_urls.txt
```

3. The script will create a `downloaded_jobs` directory and save the content from each URL as a text file.

## Output

The script will:
- Create a `downloaded_jobs` directory (if it doesn't exist)
- Save each job description as a text file named after the domain and path
- Print progress information and a summary when complete

## Error Handling

The script includes error handling for:
- File not found errors
- Network request failures
- HTTP errors (4xx/5xx responses)
- General exceptions during processing

## License

MIT