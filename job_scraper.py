#!/usr/bin/env python3

import requests
import os
import sys
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import time

def read_urls_from_file(file_path):
    """Read URLs from a text file, one URL per line."""
    try:
        with open(file_path, 'r') as file:
            # Strip whitespace and filter out empty lines
            urls = [line.strip() for line in file if line.strip()]
        return urls
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

def download_content(url, output_dir="downloaded_jobs"):
    """Download content from a URL and save it to a file."""
    try:
        # Add a small delay to avoid overwhelming the server
        time.sleep(1)
        
        # Make the request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        # Extract text content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract text from the page (removing script and style elements)
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text(separator='\n', strip=True)
        
        # Create a filename based on the URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        path = parsed_url.path.replace('/', '_')
        if not path:
            path = '_index'
        filename = f"{domain}{path}.txt"
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the content to a file
        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(f"Source URL: {url}\n\n")
            file.write(text)
        
        print(f"Successfully downloaded: {url} -> {output_path}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error processing {url}: {e}")
        return False

def main():
    # Check if a file path was provided
    if len(sys.argv) < 2:
        print("Usage: python job_scraper.py <url_file_path>")
        sys.exit(1)
    
    url_file = sys.argv[1]
    urls = read_urls_from_file(url_file)
    
    print(f"Found {len(urls)} URLs in {url_file}")
    
    # Create a directory for downloaded content
    output_dir = "downloaded_jobs"
    
    # Track success and failure counts
    success_count = 0
    failure_count = 0
    
    # Process each URL
    for i, url in enumerate(urls, 1):
        print(f"Processing {i}/{len(urls)}: {url}")
        if download_content(url, output_dir):
            success_count += 1
        else:
            failure_count += 1
    
    # Print summary
    print("\nDownload Summary:")
    print(f"Total URLs: {len(urls)}")
    print(f"Successfully downloaded: {success_count}")
    print(f"Failed: {failure_count}")
    print(f"Downloaded content saved to: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    main()