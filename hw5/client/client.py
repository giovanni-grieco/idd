import tkinter as tk
from tkinter import scrolledtext
from elasticsearch import Elasticsearch

# Connect to Elasticsearch
es = Elasticsearch("http://localhost:9200")

def search():
    query = entry.get()
    if not query:
        return
    # Clear previous results
    result_box.delete(1.0, tk.END)
    # Perform search
    try:
        res = es.search(index="research_papers", query={"match": {"_all": query}})
        hits = res['hits']['hits']
        if not hits:
            result_box.insert(tk.END, "No results found.\n")
        for hit in hits:
            result_box.insert(tk.END, f"{hit['_source']}\n\n")
    except Exception as e:
        result_box.insert(tk.END, f"Error: {e}\n")

root = tk.Tk()
root.title("Elasticsearch Search Engine")

tk.Label(root, text="Enter your search query:").pack(pady=5)
entry = tk.Entry(root, width=50)
entry.pack(pady=5)

tk.Button(root, text="Search", command=search).pack(pady=5)

result_box = scrolledtext.ScrolledText(root, width=80, height=20)
result_box.pack(pady=10)

root.mainloop()