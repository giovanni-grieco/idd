import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filemode='w', filename='pubmed_adapter.log')

def fetch(query: str, total_amount: int):
    pass