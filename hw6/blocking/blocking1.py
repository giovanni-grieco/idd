# This file will contain a strategy by reading from both datasets and adding a block_id column.
# Don't know yet if we'll keep them separated or merge them into a single dataset with a block_id column.
# Both dataset have indipendent row_id, so a simple merge won't work, we need to keep track of the original row_id


from collections import defaultdict
import jellyfish
import argparse
import os
import pandas as pd
import hashlib
import logging

WORKING_DIR = "blocks1"


def get_typo_tolerant_keys(row) -> int:
    # 1. Clean the data
    brand = str(row.get('Marca', '')).lower().strip()
    model = str(row.get('Modello', '')).lower().strip()
    year  = str(row.get('Anno', '')).strip()
    #print(f"Processing brand: {brand}, model: {model}, year: {year}")
    brand_key = jellyfish.soundex(brand)
    model_key = jellyfish.soundex(model)
    key_string = f"{brand_key}_{model_key}"
    #print(f"Generated key: {key_string}")
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    return key_hash

def handle_row(working_dir, row, blocks: set):
    key = get_typo_tolerant_keys(row._asdict())
    block_file = os.path.join(working_dir, f"{key}")
    if key not in blocks:
        blocks.add(key)
    with open(block_file, 'a') as f:
        f.write(f"{row.row_id}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create blocks based on typo-tolerant keys.")
    parser.add_argument("table1", help="Path to the first aligned CSV file (e.g., aligned_used_cars_data.csv)")
    args = parser.parse_args()

    os.makedirs(WORKING_DIR, exist_ok=True)
    # create folder named like table1 without extension
    table1_name = os.path.splitext(os.path.basename(args.table1))[0]
    working_dir = os.path.join(WORKING_DIR, table1_name)
    os.makedirs(working_dir, exist_ok=True)

    blocks = set()


    # Process first table
    for chunk in pd.read_csv(args.table1, chunksize=100000):
        for row in chunk.itertuples(index=False):
            handle_row(working_dir, row, blocks)