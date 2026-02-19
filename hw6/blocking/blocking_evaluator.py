# This will evaluate the blocking strategy by calculating TP, FP, TN, FN and then calculating Precision, Recall and F1 score.

import os
import argparse
from numpy import long
import pandas as pd
import hashlib
import jellyfish

def blocks_occurances(blocks_root_dir: str) -> dict[str, int]:
    block_sub_folders = [os.path.join(blocks_root_dir, d) for d in os.listdir(blocks_root_dir) if os.path.isdir(os.path.join(blocks_root_dir, d))]
    
    block2amount = {}
    for block_sub_folder in block_sub_folders:
        block_files = [f for f in os.listdir(block_sub_folder) if os.path.isfile(os.path.join(block_sub_folder, f))]
        for block_file in block_files:
            block2amount[block_file] = block2amount.get(block_file, 0) + 1
    return block2amount

def get_matching_blocks_in_both_datasets(blocks_dir: str) -> list[str]: 
    result = blocks_occurances(blocks_dir)
    matching_blocks_in_both_datasets = []
    
    for block_file, amount in result.items():
        if amount > 1:
            matching_blocks_in_both_datasets.append(block_file)
    return matching_blocks_in_both_datasets

def calculate_tp_fp_fn(match_table_file: str, blocks_dir: str, matching_blocks_in_both_datasets: list[str]) -> tuple[float, float, float]:
    # Read the match table and create a set of matching pairs
    match_table = pd.read_csv(match_table_file)
    matching_pairs = set(zip(match_table['row_id_used_cars'], match_table['row_id_vehicles']))
    print(matching_pairs)
    print(f"Total matching pairs in match table: {len(match_table)}")
    print(matching_pairs)
    tp = long(0)
    fp = long(0)
    fn = long(0)

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
    return tp, fp, fn

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate the blocking strategy by calculating TP, FP, TN, FN and then calculating Precision, Recall and F1 score.")
    parser.add_argument("match_table", help="Path to the match table CSV file (e.g., match_table.csv)")
    parser.add_argument("table1_csv", help="Path to the first table CSV file (e.g., aligned_used_cars_data.csv)")
    parser.add_argument("table2_csv", help="Path to the second table CSV file (e.g., aligned_vehicles_data.csv)")
    parser.add_argument("blocks_dir", help="Path to the directory containing the blocks (e.g., blocks1/aligned_used_cars_data)")
    args = parser.parse_args()

    result = blocks_occurances(args.blocks_dir)


    matching_blocks_in_both_datasets = get_matching_blocks_in_both_datasets(args.blocks_dir)
    print(f"Total blocks: {len(result)}")
    print(f"Matching blocks in both datasets: {len(matching_blocks_in_both_datasets)}")

    tp, fp, fn = calculate_tp_fp_fn(args.match_table, args.blocks_dir, matching_blocks_in_both_datasets)
    # we need tn we can calculate by measuring the amount of lines in both tables, multiplying them and then subtracting tp, fp and fn from it.
    table1_rows = sum(1 for line in open(args.table1_csv))
    table2_rows = sum(1 for line in open(args.table2_csv))
    tn = (table1_rows * table2_rows) - tp - fp - fn
    print(f"True Positives: {tp}")
    print(f"False Positives: {fp}")
    print(f"False Negatives: {fn}")
    print(f"True Negatives: {tn}")
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1_score:.4f}")
    


