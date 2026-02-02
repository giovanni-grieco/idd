class Table:
    def __init__(self, paper_id: str, table_id: str, caption: str, data: str):
        self.paper_id = paper_id
        self.table_id = table_id
        self.caption = caption
        self.data = data