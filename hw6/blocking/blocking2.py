# High-recall blocking strategy: multiple keys per row

from collections import defaultdict
import jellyfish
import argparse
import os
import pandas as pd
import hashlib

WORKING_DIR = "blocks2"

def get_typo_tolerant_keys(row) -> list[str]:
    brand = str(row.get('Marca', '')).lower().strip()
    model = str(row.get('Modello', '')).lower().strip()
    year  = str(row.get('Anno', '')).strip()

    keys = []

    # 1. Brand+Model soundex (as in blocking1)
    brand_key = jellyfish.soundex(brand)
    model_key = jellyfish.soundex(model)
    key1 = f"{brand_key}_{model_key}"
    keys.append(key1)

    # 2. Brand+Model first char
    if brand and model:
        key2 = f"{brand}_{model[0]}"
        keys.append(key2)

    # 3. Brand only (soundex)
    if brand:
        key3 = f"{brand_key}"
        keys.append(key3)

    # 4. Model only (soundex)
    if model:
        key4 = f"{model_key}"
        keys.append(key4)

    # 5. Year (if present and valid)
    if year.isdigit() and len(year) == 4:
        key5 = f"{year}"
        keys.append(key5)

    # Hash all keys for filename safety
    hashed_keys = [hashlib.md5(k.encode()).hexdigest() for k in keys]
    return hashed_keys

def handle_row(working_dir, row, blocks: set):
    keys = get_typo_tolerant_keys(row._asdict())
    for key in keys:
        block_file = os.path.join(working_dir, f"{key}")
        if key not in blocks:
            blocks.add(key)
        with open(block_file, 'a') as f:
            f.write(f"{row.row_id}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create blocks for high recall based on multiple typo-tolerant keys.")
    parser.add_argument("table1", help="Path to the first aligned CSV file (e.g., aligned_used_cars_data.csv)")
    args = parser.parse_args()

    os.makedirs(WORKING_DIR, exist_ok=True)
    table1_name = os.path.splitext(os.path.basename(args.table1))[0]
    working_dir = os.path.join(WORKING_DIR, table1_name)
    os.makedirs(working_dir, exist_ok=True)

    blocks = set()

    for chunk in pd.read_csv(args.table1, chunksize=100000):
        for row in chunk.itertuples(index=False):
            handle_row(working_dir, row, blocks)