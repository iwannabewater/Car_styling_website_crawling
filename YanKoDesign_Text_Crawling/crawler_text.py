import requests
from bs4 import BeautifulSoup
import json
import time

def fetch_content(url, max_retries=5, delay_between_retries=5):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)  # Added a timeout
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            start_tag = soup.find('h1')
            end_tag = soup.find('h2')
            
            if not start_tag or not end_tag:
                print(f"Could not find the specified start or end tags in the content for URL: {url}. Skipping.")
                return None
            
            segments = []
            current_tag = start_tag.find_next()
            while current_tag and current_tag != end_tag:
                if current_tag.name == 'p':
                    text = current_tag.text.strip()
                    if text:
                        segments.append(text)
                current_tag = current_tag.find_next()
            
            return {
                "article_url": url,
                "segments": segments
            }
        
        except (requests.RequestException, requests.ConnectionError) as e:
            if attempt < max_retries - 1:  # i.e. not the last attempt
                print(f"Error fetching content from the URL {url}. Retrying in {delay_between_retries} seconds...")
                time.sleep(delay_between_retries)
                continue
            else:
                print(f"Failed to fetch content from the URL {url} after {max_retries} attempts. Error: {e}")
                return None

def main():
    all_data = []
    success_count = 0
    fail_count = 0
    
    with open("all_pages.txt", "r", encoding="utf-8") as file:
        urls = [line.strip() for line in file.readlines() if line.strip()]
    
    for url in urls:
        print(f"Fetching content from URL: {url}...")
        content = fetch_content(url)
        if content:
            all_data.append(content)
            success_count += 1
        else:
            fail_count += 1
    
    file_name = "all_output.json"
    try:
        with open(file_name, "w", encoding="utf-8") as file:
            json.dump(all_data, file, indent=4, ensure_ascii=False)
        print(f"Content successfully saved to {file_name}!")
    except IOError as e:
        print(f"Error saving content to file: {e}")
    
    print(f"Finished fetching content. {success_count} URLs fetched successfully, {fail_count} failed.")

if __name__ == "__main__":
    main()


