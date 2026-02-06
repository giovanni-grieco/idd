from domain.paragraph import Paragraph

class Figure:
    
    paragraphs: list[Paragraph]

    def __init__(self, paper_id: str, figure_id: str, caption: str, image_url: str):
        self.paper_id = paper_id
        self.figure_id = figure_id
        self.caption = caption
        self.image_url = image_url
        self.paragraphs = []