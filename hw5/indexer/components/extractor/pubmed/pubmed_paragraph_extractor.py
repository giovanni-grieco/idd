import logging

logger = logging.getLogger(__name__)

import bs4
from domain.paragraph import Paragraph

def extract_paragraphs_from_html(html_content: str, paper_id: str) -> list[Paragraph]:
    pass