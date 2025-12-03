import requests
from lxml import etree as ET
import json
import os

source_folder_name = "arxiv"

time_to_next_request = 3  # seconds

def save_metadata_as_json(metadata: dict, filename: str) -> bool:
    with open(filename, 'w') as f:
        json.dump(metadata, f, indent=4)
    return True

def download_paper(url: str, filename: str) -> bool:
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        return True
    else:
        print(f"Failed to download paper from {url}. Status code: {response.status_code}")
        return False



# Fetch the candidate papers with arxiv search API
# Filter only the ones that have HTML papers
def fetch_arxiv(query: str, max_results: int = 10, start: int = 0):
    search_query = f"all:{query}"
    url=f'http://export.arxiv.org/api/query?search_query={search_query}&start={start}&max_results={max_results}'

    response = requests.get(url)
    print(response.status_code)

    if response.status_code == 200:
        root = ET.fromstring(response.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}

        for entry in root.findall('atom:entry', ns):
            title = (entry.find('atom:title', ns).text or '').strip()
            summary = (entry.find('atom:summary', ns).text or '').strip()
            published = (entry.find('atom:published', ns).text or '').strip()
            arxiv_id = (entry.find('atom:id', ns).text or '').strip()
            authors = [a.text for a in entry.findall('atom:author/atom:name', ns)]
            link: str = next((l.get('href') for l in entry.findall('atom:link', ns) if l.get('rel') == 'alternate'), None)
            

            print("Title:", title)
            print("Authors:", ", ".join(authors))
            print("Published:", published)
            print("Link:", link or arxiv_id)
            print("Summary:", summary[:300].replace("\n", " ") + "...")
            # Check for HTML version link
            html_link = link.replace('abs', 'html') if link else None
            filename_base = arxiv_id.split('/')[-1]
            response_status = download_paper(html_link, f"{filename_base}.html") if html_link else None
            if response_status:
                print("HTML version available at:", html_link)
                # If it's available, we will format the metadata into a JSON and download the paper itself as a file.
                # The metadata is gonna be a json structure file
                metadata = {"title": title,"authors": authors,"published": published, "summary": summary,"link": link or arxiv_id}
                save_metadata_as_json(metadata, f"{filename_base}.json")
    else:
        print("Error fetching data from arXiv API:", response.status_code)

def fetch(query: str, total_amount: int, max_results: int = 10, start: int = 0):

    # create source folder if not exists
    if not os.path.exists(source_folder_name):
        os.makedirs(source_folder_name)
    os.chdir(source_folder_name)

    if total_amount <= max_results:
        max_results = total_amount

    while start < total_amount:
        fetch_arxiv(query, start, max_results)
        print(f"Fetched {min(start + max_results, total_amount)} of {total_amount} results.\n")
        start += max_results