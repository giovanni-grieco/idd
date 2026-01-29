import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w', filename='index.log')
logger = logging.getLogger(__name__)

import components.dataloader as dataloader
from components.indexer import Indexer



def main():
    print("Indexing documents...")
    indexer: Indexer = Indexer("research_papers")
    status = indexer.index_documents_bulk(dataloader.load_research_papers_data_from_directory("output/arxiv"))
    print(f"Succeeded :{status[0]}, Failed: {status[1]}")
    status = indexer.index_documents_bulk(dataloader.load_research_papers_data_from_directory("output/pubmed"))
    print(f"Succeeded :{status[0]}, Failed: {status[1]}")
    indexer = Indexer("figures")
    #indexer.index_documents_bulk(dataloader.load_figures_data_from_directory("figures"))
    indexer = Indexer("tables")
    #indexer.index_documents_bulk(dataloader.load_tables_data_from_directory("tables"))
    print("Indexing completed.")


if __name__ == "__main__":
    main()