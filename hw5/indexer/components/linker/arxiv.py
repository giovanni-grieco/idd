from domain.figure import Figure
from domain.table import Table

import bs4


# <a class="ltx_ref" ...
def parse_references(paragraph_text: str) -> list[str]:
    soup = bs4.BeautifulSoup(paragraph_text, 'html.parser')
    references = []
    for a in soup.find_all('a', class_='ltx_ref'):
        ref_id = a.get('href', '').lstrip('#')
        if ref_id:
            references.append(ref_id)
    return references

def linker(paragraphs: list[str], figures: list[str], tables: list[str]) -> dict[str, str]:
    result = {}
    for p in paragraphs:
        references = parse_references(p['text'])
        for f in figures:
            if f['figure_id'] in references:
                # Link the figure to the paragraph
                result[f['figure_id']] = p['paragraph_id']
        for t in tables:
            if t['table_id'] in references:
                # Link the table to the paragraph
                result[t['table_id']] = p['paragraph_id']
    return result
