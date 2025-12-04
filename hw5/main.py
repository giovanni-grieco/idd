import arxiv_adapter
import pubmed_adapter
import dataloader
from indexer import Indexer

arxiv_query = "text-to-sql+OR+\"Natural language to SQL\""
pubmed_query = ""
total_amount = 3000


def main():
    #arxiv_adapter.fetch(arxiv_query, total_amount, 100)
    #pubmed_adapter.fetch(pubmed_query, total_amount)
    indexer: Indexer = Indexer("research_papers")
    indexer.create_index()
    indexer.index_documents_bulk(dataloader.load_data_from_directory("arxiv"))


if __name__ == "__main__":
    main()