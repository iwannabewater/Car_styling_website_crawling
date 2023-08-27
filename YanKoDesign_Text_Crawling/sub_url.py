import requests
from bs4 import BeautifulSoup
import re
import time

BASE_URL = "https://www.yankodesign.com/category/automotive/"

def crawl_page(url, page_num, max_pages, retries=3):
    # Stop the recursion if reached the maximum number of pages
    if page_num > max_pages:
        return

    for _ in range(retries):
        try:
            response = requests.get(url, timeout=10)  # Increased timeout
            response.raise_for_status()
            break  # If successful, break out of the retry loop
        except (requests.exceptions.ChunkedEncodingError, requests.exceptions.Timeout):
            time.sleep(5)  # Wait for 5 seconds before retrying
            continue
    else:
        # If exhausted all retries and still have an error, print a message and return
        print(f"Failed to fetch {url} after {retries} retries.")
        return

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the first h1 tag
    h1_tag = soup.find('h1')

    # Find the page-numbers section
    page_numbers = soup.find(class_='page-numbers')

    # Extract all siblings between the h1 tag and page-numbers section
    content_to_crawl = []
    for sibling in h1_tag.find_all_next():
        if sibling == page_numbers:
            break
        content_to_crawl.append(sibling)

    content_soup = BeautifulSoup(''.join(str(tag) for tag in content_to_crawl), 'html.parser')

    pattern = re.compile(r'https://www.yankodesign.com/\d{4}/\d{2}/\d{2}/[a-zA-Z0-9\-]+/')
    sub_urls = {a['href'] for a in content_soup.find_all('a', href=True) if pattern.match(a['href'])}

    # Save the sub-URLs to a file
    with open(f'sub_url_page{page_num}.txt', 'w') as f:
        for sub_url in sub_urls:
            f.write(sub_url + '\n')

    print(f"Page {page_num} done. Found {len(sub_urls)} sub-URLs.")

    # Find the next page URL using the class "next"
    next_page = soup.find('a', class_='next')
    if next_page:
        next_page_url = next_page['href']
        crawl_page(next_page_url, page_num + 1, max_pages)

def summarize_txt_files(max_pages):
    # Open the summary file for writing
    with open('all_pages.txt', 'w') as summary_file:
        # Loop through each page's txt file
        for page_num in range(1, max_pages + 1):
            file_name = f'sub_url_page{page_num}.txt'
            try:
                # Open the page's txt file for reading
                with open(file_name, 'r') as page_file:
                    # Write the content of the page's txt file to the summary file
                    summary_file.write(page_file.read())
                    summary_file.write('\n')  # Add a newline for separation
            except FileNotFoundError:
                # If the file doesn't exist, skip to the next one
                continue

    print(f"Summarized content of {max_pages} pages into all_pages.txt.")

# Number of pages to crawl
MAX_PAGES = 50

# Start the crawling from the first page
crawl_page(BASE_URL, 1, MAX_PAGES)

# Summarize the txt files
summarize_txt_files(MAX_PAGES)

