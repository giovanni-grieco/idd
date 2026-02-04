import logging

logger = logging.getLogger(__name__)

import bs4
from domain.table import Table

def extract_tables_from_html(html_content: str, paper_id: str) -> list[Table]:
    pass