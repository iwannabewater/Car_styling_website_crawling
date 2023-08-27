import requests
from bs4 import BeautifulSoup
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def crawl_website(url, session):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = session.get(url, headers=headers, proxies={}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extracting text data
        paragraphs = soup.find_all('p')
        segments = [para.text.strip() for para in paragraphs]

        data = {
            "url": url,
            "segments": segments
        }
        return data
    except requests.RequestException as e:
        print(f"Error fetching the URL {url}: {e}")
        return None

def save_to_json(data, filename="output.json"):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def read_urls_from_file(filename="subpages.txt"):
    with open(filename, 'r') as f:
        return [line.strip() for line in f.readlines()]

if __name__ == "__main__":
    urls = read_urls_from_file()
    all_data = []
    session = create_session()
    successful_crawls = 0

    for url in urls:
        print(f"Crawling: {url}")
        crawled_data = crawl_website(url, session)
        if crawled_data:
            all_data.append(crawled_data)
            successful_crawls += 1

    save_to_json(all_data)
    print(f"Data saved to output.json. Successfully crawled {successful_crawls} out of {len(urls)} URLs.")
