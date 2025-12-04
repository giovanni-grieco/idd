import requests
import lxml.etree as ET
import json
import os
import time
import logging
import tqdm


logger = logging.getLogger(__name__)

source_folder_name = "arxiv"
cache_folder_name = "cache"

time_to_next_request = 3  # seconds

def _format_seconds(sec: float) -> str:
    sec = max(0, int(sec))
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    if h:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:d}:{s:02d}"

def save_metadata_as_json(metadata: dict, filename: str) -> bool:
    with open(filename, 'w') as f:
        json.dump(metadata, f, indent=4)
    return True

def in_cache(filename: str) -> bool:
    result = False
    if not os.path.exists(cache_folder_name):
        os.makedirs(cache_folder_name)
    filepath = os.path.join(cache_folder_name, filename)
    if os.path.exists(filepath):
        result = True
    else:
        with open(filepath, 'w') as f:
            f.write('1')
    return result

def exists_paper(filename: str) -> bool:
    return os.path.exists(filename)

def download_paper(url: str, filename: str) -> bool:
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        return True
    else:
        #print(f"Failed to download paper from {url}. Status code: {response.status_code}")
        logger.warning(f"Failed to download paper from {url}. Status code: {response.status_code}. Skipping...")
        return False



# Fetch the candidate papers with arxiv search API
# Filter only the ones that have HTML papers
def fetch_arxiv(query: str, max_results: int = 10, start: int = 0, bar=None):
    search_query = f"all:{query}"
    url=f'http://export.arxiv.org/api/query?search_query={search_query}&start={start}&max_results={max_results}'
    logger.info(f"Fetching arXiv API URL: {url}")

    response = requests.get(url)
    logger.info(f"Response status code: {response.status_code}")

    if response.status_code == 200:
        root = ET.fromstring(response.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        logger.info(f"Parsing {len(root.findall('atom:entry', ns))} entries from arXiv API response.")
        for entry in root.findall('atom:entry', ns):
            start_time = time.time()
            
            title = (entry.find('atom:title', ns).text or '').strip()
            summary = (entry.find('atom:summary', ns).text or '').strip()
            published = (entry.find('atom:published', ns).text or '').strip()
            arxiv_id = (entry.find('atom:id', ns).text or '').strip()
            authors = [a.text for a in entry.findall('atom:author/atom:name', ns)]
            link: str = next((l.get('href') for l in entry.findall('atom:link', ns) if l.get('rel') == 'alternate'), "")
            

            #print("Title:", title)
            #print("Authors:", ", ".join(authors))
            #print("Published:", published)
            #print("Link:", link or arxiv_id)
            #print("Summary:", summary[:300].replace("\n", " ") + "...")
            # Check for HTML version link
            html_link = link.replace('abs', 'html').replace("arxiv", "export.arxiv") if link else None
            filename_base = arxiv_id.split('/')[-1]
            if not exists_paper(f"{filename_base}.json") and not in_cache(f"{filename_base}.cache"):
                response_status = download_paper(html_link, f"{filename_base}.html") if html_link else None
                if response_status:
                    #print("HTML version available at:", html_link)
                    # If it's available, we will format the metadata into a JSON and download the paper itself as a file.
                    # The metadata is gonna be a json structure file
                    metadata = {"title": title,"authors": authors,"published": published, "summary": summary,"link": link or arxiv_id}
                    save_metadata_as_json(metadata, f"{filename_base}.json")
                    logger.info(f"Downloaded and saved paper {filename_base}")
                # We wait regardless of success to respect rate limiting
                logger.info(f"Waiting for {time_to_next_request} seconds to respect rate limiting...")
                time.sleep(time_to_next_request)
            else:
                if exists_paper(f"{filename_base}.json"):
                    logger.info(f"Paper {filename_base} already exists. Skipping download.")
                if in_cache(f"{filename_base}.cache"):
                    logger.info(f"Paper {filename_base} is in cache. Skipping download.")

            elapsed = time.time() - start_time
            if bar:
                bar.update(1)


    else:
        logger.error(f"Error fetching data from arXiv API: {response.status_code}")
        logger.error(response.text)
    logger.info("Finished processing current batch from arXiv API.")
    logger.info(f"Waiting for {time_to_next_request} seconds to respect rate limiting...")

    time.sleep(time_to_next_request)

def fetch(query: str, total_amount: int, max_results: int = 10, start: int = 0):

    # create source folder if not exists
    if not os.path.exists(source_folder_name):
        os.makedirs(source_folder_name)
    os.chdir(source_folder_name)

    total = max(0, int(total_amount))
    if total == 0:
        logger.info("Nothing to fetch (total_amount is 0).")
        return

    if total <= max_results:
        max_results = total

    processed = start
    start_time = time.time()

    with tqdm.tqdm(total=total, initial=processed, desc="Fetching", unit="paper", ncols=100) as bar:
        while processed < total:
            batch_size = min(max_results, total - processed)
            # fetch the batch (fetch_arxiv already respects rate limiting per entry)
            fetch_arxiv(query, batch_size, processed, bar)
            processed += batch_size
            logger.info(f"Fetched {processed} of {total} results.")

    total_elapsed = time.time() - start_time
    logger.info(f"Completed fetch of {total} items in {_format_seconds(total_elapsed)}.")
    os.chdir("..")