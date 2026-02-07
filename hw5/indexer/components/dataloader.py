
# Fornire un iterable che permette di leggere e creare il JSON da fornire ad un consumatore

import os
import json
import components.html_cleaner as html_cleaner
import logging

logger = logging.getLogger(__name__)

def is_metadata_file(filename: str) -> bool:
    return filename.endswith(".json") and not filename.endswith("_paragraphs.json") and not filename.endswith("_figures.json") and not filename.endswith("_tables.json") and not filename.endswith("_metadata.json")

def load_research_papers_data_from_directory(directory_path: str) -> iter:
    for metadata_filename in os.listdir(directory_path):
        if is_metadata_file(metadata_filename):
            filename = metadata_filename.replace(".json", ".html")
            # Ugly hack, 
            if directory_path == "output/pubmed":
                filename = filename.replace(".html", ".xml")
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
                    print("TEST")
                    yield document

def load_figures_data_from_directory(directory_path: str) -> iter:
    yield None

def load_tables_data_from_directory(directory_path: str) -> iter:
    yield None

