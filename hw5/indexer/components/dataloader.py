import os
import json
import components.html_cleaner as html_cleaner
import logging

logger = logging.getLogger(__name__)

def collect_papers(directory_path:str) -> list[str]:
    papers = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".html") or filename.endswith(".xml"):
            #print(f"Found paper file: {filename}")
            papers.append(filename)
    #print(f"Collected {len(papers)} papers from directory: {directory_path}")
    return papers

def load_research_papers_data_from_directory(directory_path: str) -> iter:
    for filename in collect_papers(directory_path):
        if filename:
            metadata_filename = ""
            if filename.endswith(".html"):
                metadata_filename = filename.replace(".html", ".json")
            elif filename.endswith(".xml"):
                metadata_filename = filename.replace(".xml", ".json")
            
            metadata_file_path = os.path.join(directory_path, metadata_filename)
            file_path = os.path.join(directory_path, filename)
            with open(metadata_file_path, 'r', encoding='utf-8') as metadata_file:
                with open(file_path, 'r', encoding='utf-8') as content_file:
                    content = content_file.read()
                    content = html_cleaner.clean_html(content)
                    #print(content)
                    metadata = json.load(metadata_file)
                    document = {
                        "title": metadata.get("title", ""),
                        "authors": metadata.get("authors", []),
                        "published": metadata.get("published", ""),
                        "summary": metadata.get("summary", ""),
                        "link": metadata.get("link", ""),
                        "content": content
                    }
                    logger.info(f"Loaded document: {metadata.get('title', 'N/A')}. Paper content size: {len(content)} characters.")
                    #print(f"{document['title']}")
                    yield document

def load_figures_data_from_directory(directory_path: str) -> iter:
    yield None

def load_tables_data_from_directory(directory_path: str) -> iter:
    yield None

