import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w', filename='fetch_and_index.log')
logger = logging.getLogger(__name__)

import arxiv_adapter
import pubmed_adapter
import dataloader
from indexer import Indexer


arxiv_query = "text-to-sql+OR+\"Natural language to SQL\""
pubmed_query = ""
total_amount = 3000


def main():
    print("Fetching and indexing research papers...")
    arxiv_adapter.fetch(arxiv_query, total_amount, 1000)
    pubmed_adapter.fetch(pubmed_query, total_amount)
    print("Fetched research papers from arXiv and PubMed.")
    print("Creating index and indexing documents...")
    indexer: Indexer = Indexer("research_papers")
    indexer.create_index()
    indexer.index_documents_bulk(dataloader.load_data_from_directory("arxiv"))
    print("Indexing completed.")


if __name__ == "__main__":
    main()