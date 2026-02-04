import logging

logger = logging.getLogger(__name__)

import bs4
from domain.figure import Figure

def extract_figures_from_html(html_content: str, paper_id: str) -> list[Figure]:
    pass