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
        try:
            if filename:
                metadata_filename = ""
                if filename.endswith(".html"):
                    metadata_filename = filename.replace(".html", ".json")
                elif filename.endswith(".xml"):
                    metadata_filename = filename.replace(".xml", ".json")
                #print(metadata_filename)
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
        except Exception as e:
            logger.error(f"Error loading document from file {filename}: {e}")

def load_figures_data_from_directory(directory_path: str) -> iter:
    for filename in collect_papers(directory_path):
        try:
            clean_filename = filename.replace(".html", "").replace(".xml", "")
            figures_filename = f"{clean_filename}_figures.json"
            paragraphs_filename = f"{clean_filename}_paragraphs.json"
            links_filename = f"{clean_filename}_links.json"
            
            figures_path = os.path.join(directory_path, figures_filename)
            paragraphs_path = os.path.join(directory_path, paragraphs_filename)
            links_path = os.path.join(directory_path, links_filename)

            if os.path.exists(figures_path) and os.path.exists(paragraphs_path) and os.path.exists(links_path):
                with open(figures_path, 'r', encoding='utf-8') as f:
                    figures_data = json.load(f)
                
                with open(paragraphs_path, 'r', encoding='utf-8') as f:
                    paragraphs_data = json.load(f)
                
                with open(links_path, 'r', encoding='utf-8') as f:
                    links_data = json.load(f)

                for figure in figures_data:
                    figure_id = figure.get("figure_id")
                    
                    referencing_text = []
                    links = links_data.get(figure_id, [])
                    
                    if links:
                        for paragraph in paragraphs_data:
                            text = paragraph.get("text", "")
                            #clean the text to remove HTML tags and special characters
                            text = html_cleaner.clean_html(text)
                            # Check if the paragraph contains any of the IDs that link to this figure
                            if any(link in text for link in links):
                                referencing_text.append(text)
                            
                    blob_data = "\n".join(referencing_text)
                    blob_data = html_cleaner.clean_html(blob_data)

                    yield {
                        "figure_id": figure_id,
                        "caption": figure.get("caption"),
                        "paper_id": figure.get("paper_id"),
                        "image_url": figure.get("image_url"),
                        "blob_data": blob_data
                    }

        except Exception as e:
            logger.error(f"Error loading figure data from file {filename}: {e}")

def load_tables_data_from_directory(directory_path: str) -> iter:
    yield None

