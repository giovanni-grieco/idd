# This will evaluate the blocking strategy by calculating TP, FP, TN, FN and then calculating Precision, Recall and F1 score.

import os
import argparse
import pandas as pd
import hashlib
import jellyfish

def calculate_amount_of_matching_blocks(blocks_root_dir: str) -> dict[str, int]:
    block_sub_folders = [os.path.join(blocks_root_dir, d) for d in os.listdir(blocks_root_dir) if os.path.isdir(os.path.join(blocks_root_dir, d))]
    
    block2amount = {}
    for block_sub_folder in block_sub_folders:
        block_files = [f for f in os.listdir(block_sub_folder) if os.path.isfile(os.path.join(block_sub_folder, f))]
        for block_file in block_files:
            block2amount[block_file] = block2amount.get(block_file, 0) + 1
    return block2amount

def calculate_precision_recall(match_table_file: str, blocks_dir: str, matching_blocks_in_both_datasets: list[str]) -> tuple[float, float, float]:
    # Read the match table and create a set of matching pairs
    match_table = pd.read_csv(match_table_file)
    matching_pairs = set(zip(match_table['row_id_used_cars'], match_table['row_id_vehicles']))
    print(matching_pairs)
    print(f"Total matching pairs in match table: {len(match_table)}")
    print(matching_pairs)
    tp = fp = fn = tn = 0
    block_sub_folders = [os.path.join(blocks_dir, d) for d in os.listdir(blocks_dir) if os.path.isdir(os.path.join(blocks_dir, d))]
    true_positive_pairs = set()
    for matching_block in matching_blocks_in_both_datasets:
        matching_block_A = os.path.join(block_sub_folders[0], matching_block)
        matching_block_B = os.path.join(block_sub_folders[1], matching_block)
        #print(f"Evaluating block: {matching_block}, Block A: {matching_block_A}, Block B: {matching_block_B}")
        with open(matching_block_A, 'r') as f:
            with open(matching_block_B, 'r') as g:
                block_A_rows = set(int(line.strip()) for line in f)
                block_B_rows = set(int(line.strip()) for line in g)
                for row_A in block_A_rows:
                    for row_B in block_B_rows:
                        pair = (row_A, row_B)
                        reversed_pair = (row_B, row_A)
                        #print(f"Evaluating pair: {pair} and reversed pair: {reversed_pair}")
                        if (pair in matching_pairs or reversed_pair in matching_pairs) and (pair not in true_positive_pairs or reversed_pair not in true_positive_pairs):
        
                            tp += 1
                            #print(f"Current TP: {tp}")
                            pair_to_print = None
                            true_positive_pairs.add(pair)
                            true_positive_pairs.add(reversed_pair)
                            if pair in matching_pairs:
                                pair_to_print = pair
                            else:
                                pair_to_print = reversed_pair
                            print(f"True Positive: {pair_to_print} is in matching pairs in {matching_block_A}-{matching_block_B}")
                        else:
                            fp += 1

    fn = len(matching_pairs) - tp
    precision = tp / (tp + fp) if tp + fp > 0 else 0
    recall = tp / (tp + fn) if tp + fn > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if precision + recall > 0 else 0
    return precision, recall, f1_score

### EXPERIMENTAL
def retrieve_row_by_id(row_id: int, block_sub_folders: list[str]) -> bool:
    for block_sub_folder in block_sub_folders:
        block_files = [f for f in os.listdir(block_sub_folder) if os.path.isfile(os.path.join(block_sub_folder, f))]
        for block_file in block_files:
            with open(os.path.join(block_sub_folder, block_file), 'r') as f:
                if str(row_id) in f.read():
                    return True
    return False

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

def is_matching_pair_in_blocks(pair: tuple[int, int], block_sub_folders: list[str]) -> bool:
    row_id_A, row_id_B = pair
    return retrieve_row_by_id(row_id_A, block_sub_folders) and retrieve_row_by_id(row_id_B, block_sub_folders)


def calculate_precision_recall_inverted(match_table_file: str, blocks_dir: str, matching_blocks_in_both_datasets: list[str]) -> tuple[float, float, float]:
    # Read the match table and create a set of matching pairs
    match_table = pd.read_csv(match_table_file)
    matching_pairs = set(zip(match_table['row_id_used_cars'], match_table['row_id_vehicles']))
    print(matching_pairs)
    print(f"Total matching pairs in match table: {len(match_table)}")
    print(matching_pairs)
    tp = fp = fn = tn = 0
    block_sub_folders = [os.path.join(blocks_dir, d) for d in os.listdir(blocks_dir) if os.path.isdir(os.path.join(blocks_dir, d))]
    for matching_pair in matching_pairs:
        if is_matching_pair_in_blocks(matching_pair, block_sub_folders):
            tp += 1
        else:
            fn += 1

    fn = len(matching_pairs) - tp
    precision = tp / (tp + fp) if tp + fp > 0 else 0
    recall = tp / (tp + fn) if tp + fn > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if precision + recall > 0 else 0
    return precision, recall, f1_score
### EXPERIMENTAL


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate the blocking strategy by calculating TP, FP, TN, FN and then calculating Precision, Recall and F1 score.")
    parser.add_argument("match_table", help="Path to the match table CSV file (e.g., match_table.csv)")
    parser.add_argument("blocks_dir", help="Path to the directory containing the blocks (e.g., blocks1/aligned_used_cars_data)")
    args = parser.parse_args()

    result = calculate_amount_of_matching_blocks(args.blocks_dir)


    matching_blocks_in_both_datasets = []
    
    for block_file, amount in result.items():
        if amount > 1:
            matching_blocks_in_both_datasets.append(block_file)
    print(f"Total blocks: {len(result)}")
    print(f"Matching blocks in both datasets: {len(matching_blocks_in_both_datasets)}")

    precision, recall, f1_score = calculate_precision_recall(args.match_table, args.blocks_dir, matching_blocks_in_both_datasets)
    print(f"Precision: {precision}, Recall: {recall}, F1 Score: {f1_score}")


