import requests
import lxml.etree as ET
import json
import os
import time
import logging
import bs4

logger = logging.getLogger(__name__)

source_folder_name = "pubmed"
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

def extract_fulltext_link(pubmed_page) -> str:
    # There's usually a div with class 'full-text-links' that contains the links
    soup = bs4.BeautifulSoup(pubmed_page, 'html.parser')
    full_text_div = soup.find('div', class_='full-text-links-list')
    if full_text_div:
        link_tag = full_text_div.find('a', href=True)
        if link_tag:
            logger.info(f"Found full text link: {link_tag['href']}")
            return link_tag['href']
    return ""
    

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
        logger.warning(f"Failed to download paper from {url}. Status code: {response.status_code}. Skipping...")
        return False

def fetch_pubmed(query: str, max_results: int = 10, start: int = 0) -> int:
    # Step 1: Search PubMed for article IDs
    search_url = (
        f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}"
        f"&retstart={start}&retmax={max_results}&retmode=json"
    )
    logger.info(f"Fetching PubMed search URL: {search_url}")
    search_response = requests.get(search_url)
    logger.info(f"Response status code: {search_response.status_code}")
    logger.info(f"Waiting for {time_to_next_request} seconds to respect rate limiting...")
    time.sleep(time_to_next_request)
    entry_count = 0
    if search_response.status_code == 200:
        search_data = search_response.json()
        id_list = search_data.get('esearchresult', {}).get('idlist', [])
        entry_count = len(id_list)
        logger.info(f"Found {entry_count} PubMed IDs.")
        if entry_count == 0:
            logger.info("No more entries found in PubMed search response.")
        for pmid in id_list:
            filename_base = pmid
            if not exists_paper(f"{filename_base}.json") and not in_cache(f"{filename_base}.cache"):
                # Step 2: Fetch article metadata
                fetch_url = (
                    f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
                )
                fetch_response = requests.get(fetch_url)
                if fetch_response.status_code == 200:
                    root = ET.fromstring(fetch_response.content)
                    article = root.find('.//Article')
                    title = article.findtext('ArticleTitle', default='').strip() if article is not None else ''
                    summary = article.findtext('Abstract/AbstractText', default='').strip() if article is not None else ''
                    authors = []
                    if article is not None:
                        for author in article.findall('AuthorList/Author'):
                            last = author.findtext('LastName', default='')
                            first = author.findtext('ForeName', default='')
                            full = f"{first} {last}".strip()
                            if full:
                                authors.append(full)
                    published = ''
                    # Try to get publication date from PubDate or ArticleDate
                    pubdate_elem = root.find('.//PubDate')
                    if pubdate_elem is not None:
                        year = pubdate_elem.findtext('Year', default='')
                        month = pubdate_elem.findtext('Month', default='')
                        day = pubdate_elem.findtext('Day', default='')
                        published = f"{year}-{month}-{day}".strip('-')
                    if not published:
                        # fallback to ArticleDate
                        artdate_elem = root.find('.//ArticleDate')
                        if artdate_elem is not None:
                            year = artdate_elem.findtext('Year', default='')
                            month = artdate_elem.findtext('Month', default='')
                            day = artdate_elem.findtext('Day', default='')
                            published = f"{year}-{month}-{day}".strip('-')
                    link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                    metadata = {
                        "title": title,
                        "authors": authors,
                        "published": published,
                        "summary": summary,
                        "link": link
                    }
                    # Step 3: Download HTML version if available
                    # Search for full text link in the pubmed html page
                    pubmed_html_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                    pubmed_page_response = requests.get(pubmed_html_url)
                    if pubmed_page_response.status_code != 200:
                        logger.warning(f"Failed to fetch PubMed page for PMID {pmid}. Status code: {pubmed_page_response.status_code}")
                        continue
                    pubmed_page = pubmed_page_response.text
                    html_url = extract_fulltext_link(pubmed_page)
                    if not html_url:
                        logger.info(f"No full text link found for PMID {pmid}. Skipping download.")
                        continue
                    response_status = download_paper(html_url, f"{filename_base}.html")
                    if response_status:
                        logger.info(f"Downloaded and saved PubMed article {filename_base}")
                        save_metadata_as_json(metadata, f"{filename_base}.json")
                    else:
                        logger.warning(f"Failed to download full text for PMID {pmid}.")
                    logger.info(f"Waiting for {time_to_next_request} seconds to respect rate limiting...")
                    time.sleep(time_to_next_request)
                else:
                    logger.warning(f"Failed to fetch metadata for PMID {pmid}. Status code: {fetch_response.status_code}")
            else:
                if exists_paper(f"{filename_base}.json"):
                    logger.info(f"Paper {filename_base} already exists. Skipping download.")
                if in_cache(f"{filename_base}.cache"):
                    logger.info(f"Paper {filename_base} is in cache. Skipping download.")
    else:
        logger.error(f"Error fetching data from PubMed: {search_response.status_code}")
        logger.error(search_response.text)
    logger.info("Finished processing current batch from PubMed.")
    logger.info(f"Waiting for {time_to_next_request} seconds to respect rate limiting...")
    time.sleep(time_to_next_request)
    return entry_count

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

    done = False
    while processed < total and not done:
        entry_count = fetch_pubmed(query, max_results, processed)
        logger.info(f"Fetched {processed}+{entry_count} of {total} results.")
        processed += entry_count
        if entry_count == 0:
            logger.info("No more entries to process from PubMed. Ending fetch.")
            done = True

    total_elapsed = time.time() - start_time
    logger.info(f"Completed fetch of {total} items in {_format_seconds(total_elapsed)}.")
    os.chdir("..")