from collections import defaultdict
import jellyfish
import argparse
import os
import pandas as pd
import hashlib
import logging

WORKING_DIR = "blocks1"
COLUMN_NAMES = []
SUFFIXES = []

def init():
    with open("schema.txt", "r") as f:
        with open("suffixes.txt", "r") as suffix_file:
            for line in f:
                column_name = line.strip()
                COLUMN_NAMES.append(column_name)
            for line in suffix_file:
                suffix = line.strip()
                SUFFIXES.append(suffix)

            

def get_typo_tolerant_keys(row) -> str:
    brand = str(row.get('Marca', '')).lower().strip()
    model = str(row.get('Modello', '')).lower().strip()
    brand_key = jellyfish.soundex(brand)
    model_key = jellyfish.soundex(model)
    key_string = f"{brand_key}_{model_key}"
    key_hash = hashlib.md5(key_string.encode()).hexdigest()
    return key_hash


def handle_row(row):
    # A row contains a pair now so we need to calculate the hash for both used_cars and vehicles and if they match
    # They survive, if they don't, we drop them.
    first_row = pd.Series({col: getattr(row, f"{col}_used_cars") for col in COLUMN_NAMES})
    second_row = pd.Series({col: getattr(row, f"{col}_vehicles") for col in COLUMN_NAMES})
    first_key = get_typo_tolerant_keys(first_row)
    second_key = get_typo_tolerant_keys(second_row)
    if first_key == second_key:
        return row
    return None

def main():
    init()
    parser = argparse.ArgumentParser(description="Create blocks based on typo-tolerant keys.")
    parser.add_argument("table1", help="Path to the first aligned CSV file (e.g., aligned_used_cars_data.csv)")
    parser.add_argument("-o", "--output", help="Path to the output csv file", default="blocked_pairs.csv")
    args = parser.parse_args()

    os.makedirs(WORKING_DIR, exist_ok=True)
    # create folder named like table1 without extension
    table1_name = os.path.splitext(os.path.basename(args.table1))[0]
    working_dir = os.path.join(WORKING_DIR, table1_name)
    os.makedirs(working_dir, exist_ok=True)

    # Process first table
    for chunk in pd.read_csv(args.table1, chunksize=100000):
        for row in chunk.itertuples(index=False):
            row = handle_row(row)
            if row:
                output_path = os.path.join(working_dir, f"{row.block_id}.csv")
                row.to_frame().T.to_csv(output_path, mode='a', index=False, header=not os.path.exists(output_path))

if __name__ == "__main__":
    main()

