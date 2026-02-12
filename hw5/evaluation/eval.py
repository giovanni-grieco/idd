import json
import sys
import time
from elasticsearch import Elasticsearch
from typing import List, Dict, Any
import math
import os
import ext_llm

ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")
ANNOTATIONS_PATH = os.path.join(os.path.dirname(__file__), "annotations.jsonl")
DEFAULT_QUERIES_PATH = os.path.join(os.path.dirname(__file__), "queries.json")
FIELDS = {
    "research_papers": ["title", "authors", "summary", "link", "content"],
    "figures": ["figure_id", "caption", "paper_id", "image_url", "blob_data"],
    "tables": ["table_id", "caption", "paper_id", "data", "table_url", "blob_data"]
}
es = Elasticsearch(ES_HOST)

def run_queries(queries: List[Dict[str, Any]], top_k: int = 10):
    extllm = ext_llm.init(open("config.yaml", "r").read())
    llm_client = extllm.get_client("groq-llama")
    scheduler = extllm.get_scheduler(client=llm_client, retry_delay=10.0, initial_rate_limit=500, min_rate_limit=10, max_rate_limit=1000)
    scheduler.start()
    for q in queries:
        qid = q.get("id") or q.get("query_id") or q.get("query") or str(int(time.time()))
        index = q.get("index")
        query_param = {"multi_match": {"query": q.get("query"), "fields": FIELDS.get(index, ["title", "summary", "content"])}}

        print(f"\nQuery {qid} on index={index}: {q.get('query')}\n")
        res = es.search(index=index, query=query_param, size=top_k)
        hits = res.get("hits", {}).get("hits", [])
        print(f"hits={len(hits)}\n")
        futures= []
        for rank, h in enumerate(hits, start=1):
            src = h.get("_source", {})
            if index == "research_papers":
                title = src.get("title") or src.get("caption") or src.get("paper_id") or h.get("_id")
                summary = src.get("summary")
                content = src.get("content") or ""
                url = src.get("link")
                print(f"[{rank}] id={h.get('_id')} score={h.get('_score')}\n  Title: {title}\n  Summary: {summary}\n  Content: {content[:100]}...\n  URL: {url}\n")
                system_prompt = "You are an expert search result annotator. Given a query and a search result, determine if the result is relevant to the query. Respond with '1' if relevant and '0' if not relevant."
                prompt = f"Query: {q.get('query')}\nTitle: {title}\nSummary: {summary}\nContent: {content}\nURL: {url}"
                futures.append((rank, h, scheduler.submit_request(system_prompt, prompt)))

            elif index == "figures":
                caption = src.get("caption")
                image_url = src.get("image_url") or src.get("url")
                paper_id = src.get("paper_id")
                print(f"[{rank}] id={h.get('_id')} score={h.get('_score')}\n  Caption: {caption}\n  Image URL: {image_url}\n  Paper: {paper_id}\n")
                system_prompt = "You are an expert annotator. Given a query, figure caption and image, decide if the figure answers the user's information need. Respond with '1' for relevant and '0' for not relevant."
                prompt = f"Query: {q.get('query')}\nCaption: {caption}\nPaper: {paper_id}\nImageURL: {image_url}"
                try:
                    if hasattr(scheduler, "submit_multimodal_request"):
                        future = scheduler.submit_multimodal_request(system_prompt, prompt, image=image_url)
                    else:
                        future = scheduler.submit_request(system_prompt, prompt + f"\n(IMAGE_URL: {image_url})")
                except Exception:
                    future = scheduler.submit_request(system_prompt, prompt + f"\n(IMAGE_URL: {image_url})")
                futures.append((rank, h, future))

            elif index == "tables":
                caption = src.get("caption") or src.get("description")
                data = src.get("data") or ""
                table_url = src.get("table_url")
                print(f"[{rank}] id={h.get('_id')} score={h.get('_score')}\n  Caption: {caption}\n  Table URL: {table_url}\n  Data snippet: {str(data)[:200]}\n")
                system_prompt = "You are an expert annotator. Given a query and a table (caption and data), decide if the table is relevant to the query. Respond with '1' for relevant and '0' for not relevant."
                prompt = f"Query: {q.get('query')}\nCaption: {caption}\nTableURL: {table_url}\nDataSnippet: {data}"
                futures.append((rank, h, scheduler.submit_request(system_prompt, prompt)))
        for rank, h, future in futures:
            try:
                relevance_str = scheduler.get_result(future).content.strip()
                print("="*20)
                print(f"LLM response for rank {rank} id={h.get('_id')}: '{relevance_str}'")
                if "1" in relevance_str:
                    relevance = 1
                elif "0" in relevance_str:
                    relevance = 0
                else:
                    print(f"Unexpected LLM response for rank {rank} id={h.get('_id')}: '{relevance_str}'. Defaulting to relevance=0.")
                    relevance = 0
            except Exception as e:
                print(f"Error getting relevance for rank {rank} id={h.get('_id')}: {e}")
                relevance = 0
            print(f"Annotation for rank {rank} id={h.get('_id')}: relevance={relevance}\n")
            save_annotation({
                "query_id": qid,
                "index": index,
                "result_id": h.get("_id"),
                "rank": rank,
                "relevance": relevance
            })
    scheduler.stop()

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
            qid = a.get("query_id") or a.get("id") or a.get("query")
            # preserve rank so we can sort results into proper rank order
            rank = int(a.get("rank", 0))
            by_query.setdefault(qid, []).append((rank, int(a["relevance"])))
    # sort by rank and return only the relevance values in order
    sorted_by_query = {}
    for qid, items in by_query.items():
        items.sort(key=lambda x: x[0])
        sorted_by_query[qid] = [rel for _, rel in items]
    return sorted_by_query


def load_queries(query_file: str = None) -> List[Dict[str, Any]]:
    """Load queries from a JSON file. If no file is provided, load default queries.json next to this script.
    Supports the original grouped format (research_papers/tables/figures) or a flat list.
    """
    path = query_file or DEFAULT_QUERIES_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Queries file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    queries: List[Dict[str, Any]] = []
    if isinstance(data, dict):
        # handle grouped format
        for section, items in data.items():
            if isinstance(items, list):
                for it in items:
                    qid = it.get("id") or it.get("query_id") or it.get("query") or f"{section}-{int(time.time())}"
                    queries.append({
                        "id": qid,
                        "index": it.get("index") or section,
                        "query": it.get("query"),
                        "query_body": it.get("query_body")
                    })
    elif isinstance(data, list):
        for it in data:
            qid = it.get("id") or it.get("query_id") or it.get("query") or str(int(time.time()))
            queries.append({
                "id": qid,
                "index": it.get("index"),
                "query": it.get("query"),
                "query_body": it.get("query_body")
            })
    else:
        raise ValueError("Unsupported queries.json format")

    return queries

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
        print(f"Metrics for query_id={qid} with relevances={rels}")
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
        queries = load_queries(query_file)
    else:
        # load default queries.json automatically
        queries = load_queries()
    run_queries(queries, top_k)
    compute_metrics(top_k)

if __name__ == "__main__":
    qf = sys.argv[1] if len(sys.argv) > 1 else None
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    main(qf, k)