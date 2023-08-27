import requests
from bs4 import BeautifulSoup
import re

def get_subpages(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    proxies = {"http": None, "https": None}  # Bypass system's default proxy settings

    subpages = []  # Using a list to maintain order

    try:
        response = requests.get(url, headers=headers, proxies={}, timeout=10)
        response.raise_for_status()
    except requests.ConnectionError:
        print("Failed to connect to the server.")
        return []
    except requests.Timeout:
        print("Request timed out.")
        return []
    except requests.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extracting subpage links based on the date pattern
    for span in soup.find_all('span', class_='exUpD'):
        date_pattern = re.search(r'\(\d{2}-\d{2}-\d{4}\)', span.text)
        if date_pattern:
            link_tag = span.find_next('a', href=True)
            if link_tag:
                full_link = "https://www.netcarshow.com" + link_tag['href']
                if full_link not in subpages:  # Check for duplicates
                    subpages.append(full_link)

    return subpages

def main():
    url = "https://www.netcarshow.com/updates.html"
    subpages = get_subpages(url)

    # Writing the subpages to a txt file
    with open("subpages.txt", "w") as file:
        for subpage in subpages:
            file.write(subpage + "\n")

    print(f"Saved {len(subpages)} subpages to subpages.txt")

if __name__ == "__main__":
    main()
