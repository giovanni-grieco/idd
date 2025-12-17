import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w', filename= "fetch.log")
logger = logging.getLogger(__name__)

import components.fetcher.arxiv_fetcher as arxiv_fetcher
import components.fetcher.pubmed_fetcher as pubmed_fetcher


arxiv_query = "text-to-sql+OR+\"Natural language to SQL\""
pubmed_query = ""
total_amount = 3000


def main():
    print("Fetching and indexing research papers...")
    arxiv_fetcher.fetch(arxiv_query, total_amount, 1000)
    pubmed_fetcher.fetch(pubmed_query, total_amount)
    print("Fetched research papers from arXiv and PubMed.")


if __name__ == "__main__":
    main()