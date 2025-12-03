import arxiv_adapter
import pubmed_adapter

arxiv_query = "text-to-sql+OR+\"Natural language to SQL\""
pubmed_query = ""
total_amount = 3000


def main():
    arxiv_adapter.fetch(arxiv_query, total_amount, 100)
    pubmed_adapter.fetch(pubmed_query, total_amount)


if __name__ == "__main__":
    main()