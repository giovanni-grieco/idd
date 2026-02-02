import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w', filename='extract.log')
logger = logging.getLogger(__name__)

import components.extractor.common as common_extractor
import components.extractor.arxiv.arxiv_paragraph_extractor as arxiv_para_extractor
import components.extractor.arxiv.arxiv_figures_extractor as arxiv_figures_extractor
import components.extractor.arxiv.arxiv_tables_extractor as arxiv_tables_extractor

def main():
    print("Extracting paragraphs from documents...")
    common_extractor.extract("output/arxiv", arxiv_para_extractor.extract_paragraphs_from_html, arxiv_figures_extractor.extract_figures_from_html, arxiv_tables_extractor.extract_table_from_html)
    print("Paragraph extraction completed.")

if __name__ == "__main__":
    main()