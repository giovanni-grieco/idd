import logging

logger = logging.getLogger(__name__)

import bs4
from domain.figure import Figure


def extract_figures_from_html(html_content: str, paper_id: str) -> list[Figure]:
    # Placeholder for actual HTML parsing and paragraph extraction logic
    figures = []
    soup = bs4.BeautifulSoup(html_content, 'html.parser')
    # extract all paragraph with class ltx_p
    figure_tags = soup.find_all("figure", class_='ltx_figure')
    for figure_tag in figure_tags:
        caption_tag = figure_tag.find('figcaption', class_='ltx_caption')
        img_tag = figure_tag.find('img')
        if caption_tag and img_tag:
            caption_text = caption_tag.decode_contents().strip()
            image_url = img_tag.get('src', '')
            figure_id = figure_tag.get('id', 'unknown_id')
            figures.append(Figure(paper_id, figure_id, caption_text, image_url))
    return figures