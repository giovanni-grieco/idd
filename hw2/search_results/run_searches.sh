#!/usr/bin/env bash
set -euo pipefail

queries=(
  "Computer Science"
  "Distributed Systems"
  "Kubernetes"
  "Data Engineering"
  "Oscar winning movies"
  "Machine Learning algorithms and applications"
  "Climate Change impacts"
  "Quantum Computing advancements"
  "Artificial Intelligence ethics and regulations"
  "Blockchain technology in finance"
)

for q in "${queries[@]}"; do
  # build JSON with the query value inserted (close/open quotes so $q expands)
  json='{"query":{"multi_match":{"query":"'"$q"'","fields":["title^2","content"]}}}'
  # filename uses the query value; use braces and replace slashes/spaces if needed
  safe_name="${q// /_}"
  safe_name="${safe_name//\//-}"
  elastic_gopher search wikipedia "$json" >> "${safe_name}_results.json"
done