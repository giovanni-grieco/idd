import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', filemode='w', filename= "fetch.log")
logger = logging.getLogger(__name__)

import asyncio
import components.fetcher.arxiv_fetcher as arxiv_fetcher
import components.fetcher.pubmed_fetcher as pubmed_fetcher


arxiv_query = "text-to-sql+OR+\"Natural language to SQL\""
pubmed_query = "glyphosate+AND+cancer+risk"
total_amount = 3000


async def main():
    print("Fetching and indexing research papers...")
    #arxiv_fetcher.fetch(arxiv_query, total_amount, 1000)
    #pubmed_fetcher.fetch(pubmed_query, total_amount)
    # use asyncio to run both fetchers concurrently
    loop = asyncio.get_running_loop()
    tasks = [
        loop.run_in_executor(None, arxiv_fetcher.fetch, arxiv_query, total_amount, 1000),
        loop.run_in_executor(None, pubmed_fetcher.fetch, pubmed_query, total_amount)
    ]
    loop.run_until_complete(asyncio.gather(*tasks))
    print("Fetched research papers from arXiv and PubMed.")


if __name__ == "__main__":
    asyncio.run(main())