import logging

logger = logging.getLogger(__name__)

import os
from domain.paragraph import Paragraph

def collect_files(data_path: str) -> list[str]:
    output = []
    if os.path.exists(data_path):
        for f in os.listdir(data_path):
            if f.endswith('.html') :
                logger.info(f"Found: {os.path.join(data_path, f)}")
                output.append(os.path.join(data_path, f).replace(".html", ""))
    logger.info(f"Total files collected: {len(output)}")
    return output

def extract_paragraphs(file: str, data_path: str, extract_paragraphs_from_html: function):
    html_filepath = f"{file}.html"
    output_filepath = f"{file}_paragraphs.json"
    with open(html_filepath, 'r') as f:
            paper = f.read()
            extracted_paragraphs = extract_paragraphs_from_html(paper, file.replace(data_path + "/", ""))
            paragraphs = [{'paragraph_id': para.paragraph_id, 'text': para.text} for para in extracted_paragraphs]
            with open(output_filepath, 'w') as out_f:
                import json
                json.dump(paragraphs, out_f, indent=4)
            logger.info(f"Extracted paragraphs saved to {output_filepath}")

def extract_figures(file: str, data_path: str, extract_paragraphs_from_html: function):
    pass  # Placeholder for future figure extraction logic

def extract_tables(file: str, data_path: str, extract_paragraphs_from_html: function):
    pass  # Placeholder for future table extraction logic

def extract(data_path: str, extract_paragraphs_from_html: function = None, extract_figures_from_html: function = None, extract_tables_from_html: function = None):
    logger.info("Extracting paragraphs from arXiv documents...")
    files = collect_files(data_path)
    for file in files:
        extract_paragraphs(file, data_path, extract_paragraphs_from_html)
        extract_figures(file, data_path, extract_figures_from_html)
        extract_tables(file, data_path, extract_tables_from_html)

    logger.info("Paragraph extraction completed.")