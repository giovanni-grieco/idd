import logging

logger = logging.getLogger(__name__)

import os

def collect_files(data_path: str) -> list[str]:
    output = []
    if os.path.exists(data_path):
        for f in os.listdir(data_path):
            if f.endswith('.html') or f.endswith(".xml") : #Non universale, perchè pubmed usa .xml
                logger.info(f"Found: {os.path.join(data_path, f)}")
                output.append(os.path.join(data_path, f).replace(".html", "").replace(".xml", ""))
    logger.info(f"Total files collected: {len(output)}")
    return output

def extract_paragraphs(file: str, data_path: str, extract_paragraphs_from_html: function):
    filepath = f"{file}.html"
    if not os.path.exists(filepath):
        filepath = f"{file}.xml"
    output_filepath = f"{file}_paragraphs.json"
    with open(filepath, 'r') as f:
            paper = f.read()
            extracted_paragraphs = extract_paragraphs_from_html(paper, file.replace(data_path + "/", ""))
            paragraphs = [{'paragraph_id': para.paragraph_id, 'text': para.text} for para in extracted_paragraphs]
            with open(output_filepath, 'w') as out_f:
                import json
                json.dump(paragraphs, out_f, indent=4)
            logger.info(f"Extracted paragraphs saved to {output_filepath}")

def extract_figures(file: str, data_path: str, extract_figures_from_html: function):
    filepath = f"{file}.html"
    if not os.path.exists(filepath):
        filepath = f"{file}.xml"
    output_filepath = f"{file}_figures.json"
    with open(filepath, 'r') as f:
            paper = f.read()
            extracted_figures = extract_figures_from_html(paper, file.replace(data_path + "/", ""))
            figures = [{'figure_id': fig.figure_id, 'caption': fig.caption, 'image_url': fig.image_url} for fig in extracted_figures]
            with open(output_filepath, 'w') as out_f:
                import json
                json.dump(figures, out_f, indent=4)
            logger.info(f"Extracted figures saved to {output_filepath}")

def extract_tables(file: str, data_path: str, extract_tables_from_html: function):
    filepath = f"{file}.html"
    if not os.path.exists(filepath):
        filepath = f"{file}.xml"
    output_filepath = f"{file}_tables.json"
    with open(filepath, 'r') as f:
            paper = f.read()
            extracted_tables = extract_tables_from_html(paper, file.replace(data_path + "/", ""))
            tables = [{'table_id': table.table_id, 'caption': table.caption, 'data': table.data} for table in extracted_tables]
            with open(output_filepath, 'w') as out_f:
                import json
                json.dump(tables, out_f, indent=4)
            logger.info(f"Extracted tables saved to {output_filepath}")

def extract(data_path: str, extract_paragraphs_from_html: function = None, extract_figures_from_html: function = None, extract_tables_from_html: function = None):
    logger.info("Extracting...")
    files = collect_files(data_path)
    for file in files:
        extract_paragraphs(file, data_path, extract_paragraphs_from_html)
        extract_figures(file, data_path, extract_figures_from_html)
        extract_tables(file, data_path, extract_tables_from_html)

    logger.info("Paragraph extraction completed.")