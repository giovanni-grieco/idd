import arxiv_adapter

def main():
    query = "text-to-sql"
    total_amount = 1000
    arxiv_adapter.fetch(query, total_amount, 100)

if __name__ == "__main__":
    main()