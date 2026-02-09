import json
import sys
import time
from elasticsearch import Elasticsearch
from typing import List, Dict, Any
import math
import os

ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")
ANNOTATIONS_PATH = os.path.join(os.path.dirname(__file__), "annotations.jsonl")

es = Elasticsearch(ES_HOST)

def run_queries(queries: List[Dict[str, Any]], top_k: int = 10):
    for q in queries:
        qid = q.get("id", q.get("query", str(time.time())))
        index = q.get("index")
        body = q.get("query_body") or {"query": {"multi_match": {"query": q["query"], "fields": ["title", "summary", "content"]}}}
        print(f"\nQuery {qid} on index={index}: {q.get('query')}\n")
        res = es.search(index=index, body=body, size=top_k)
        hits = res.get("hits", {}).get("hits", [])
        for rank, h in enumerate(hits, start=1):
            src = h.get("_source", {})
            title = src.get("title") or src.get("caption") or src.get("paper_id") or h.get("_id")
            snippet = src.get("summary") or src.get("content", "")[:100]
            url = src.get("link") or src.get("image_url") or src.get("table_url") or "N/A"
            print(f"[{rank}] id={h.get('_id')} score={h.get('_score')}\n  Title: {title}\n  Snippet: {snippet}\n  URL: {url}\n")
            ans = input("Relevant? (y/n/s=skip, q=quit): ").strip().lower()
            if ans == "q":
                print("Quitting and saving...")
                return
            if ans == "s":
                continue
            rel = 1 if ans == "y" else 0
            save_annotation({
                "query_id": qid,
                "index": index,
                "query": q.get("query"),
                "rank": rank,
                "doc_id": h.get("_id"),
                "score": h.get("_score"),
                "relevance": rel,
                "timestamp": int(time.time())
            })

def save_annotation(obj: Dict[str, Any]):
    with open(ANNOTATIONS_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def load_annotations() -> Dict[str, List[int]]:
    """Return a map: query_id -> list of relevances in rank order (1/0)."""
    by_query = {}
    if not os.path.exists(ANNOTATIONS_PATH):
        return by_query
    with open(ANNOTATIONS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            a = json.loads(line)
            qid = a["query_id"]
            by_query.setdefault(qid, []).append(a["relevance"])
    return by_query

def precision_at_k(rels: List[int], k: int) -> float:
    if len(rels) == 0:
        return 0.0
    k = min(k, len(rels))
    return sum(rels[:k]) / k

def average_precision(rels: List[int]) -> float:
    num_rel = sum(rels)
    if num_rel == 0:
        return 0.0
    score = 0.0
    rel_seen = 0
    for i, r in enumerate(rels, start=1):
        if r:
            rel_seen += 1
            score += rel_seen / i
    return score / num_rel

def dcg(rels: List[int], k: int) -> float:
    score = 0.0
    for i in range(min(k, len(rels))):
        gain = (2 ** rels[i] - 1)
        score += gain / math.log2(i + 2)
    return score

def ndcg_at_k(rels: List[int], k: int) -> float:
    actual = dcg(rels, k)
    ideal = dcg(sorted(rels, reverse=True), k)
    return actual / ideal if ideal > 0 else 0.0

def compute_metrics(k: int = 10):
    ann = load_annotations()
    precisions = []
    aps = []
    ndcgs = []
    for qid, rels in ann.items():
        precisions.append(precision_at_k(rels, k))
        aps.append(average_precision(rels))
        ndcgs.append(ndcg_at_k(rels, k))
    if not precisions:
        print("No annotations found.")
        return
    print(f"Precision@{k}: {sum(precisions)/len(precisions):.4f}")
    print(f"MAP: {sum(aps)/len(aps):.4f}")
    print(f"nDCG@{k}: {sum(ndcgs)/len(ndcgs):.4f}")

def main(query_file: str = None, top_k: int = 10):
    if query_file:
        with open(query_file, "r", encoding="utf-8") as f:
            queries = json.load(f)
    else:
        # example interactive single query
        q = input("Enter query text: ").strip()
        idx = input("Index name: ").strip()
        queries = [{"id": str(int(time.time())), "index": idx, "query": q}]
    run_queries(queries, top_k)
    compute_metrics(top_k)

if __name__ == "__main__":
    qf = sys.argv[1] if len(sys.argv) > 1 else None
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    main(qf, k)