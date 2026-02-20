import argparse
import pandas as pd
import random
import os



# We will create the pairs to be saved in a CSV with a new column for their match label
# It will be balanced, using all the positives matches in the match_table and getting the same amount of random negative matches by randomly picking and checking that it's not present in the match_table

def match_chunk(chunk_a, chunk_b):
    merged = pd.merge(chunk_a, chunk_b, on="VIN", how="inner", suffixes=('_used_cars', '_vehicles'))
    if not merged.empty:
        merged["match_label"] = 1
        # Create explicit columns for both VINs to match negative pair schema
        merged["VIN_used_cars"] = merged["VIN"]
        merged["VIN_vehicles"] = merged["VIN"]
        # Drop the common key if you want strictly suffixed columns, or keep it. 
        # Usually better to drop to avoid ambiguity if downstream expects specific names.
        merged = merged.drop(columns=["VIN"])
    return merged


def create_negative_pairs(dataset1_path, dataset2_path, num_pairs):
    # Get total lines to know range for random sampling
    # Subtract 1 for header
    n_rows1 = sum(1 for _ in open(dataset1_path)) - 1
    n_rows2 = sum(1 for _ in open(dataset2_path)) - 1
    
    # Generate random indices
    # We use replacement because collisions are rare and acceptable for negative sampling 
    # (or we can use random.sample for unique if strictness required, but sample is safer for valid range)
    indices1 = sorted(random.sample(range(n_rows1), num_pairs))
    indices2 = sorted(random.sample(range(n_rows2), num_pairs))
    
    # Helper to load specific rows
    # Rows in CSV are 0-indexed (header), 1-indexed (data). 
    # We want data rows i where i is in indices (0-based relative to data start)
    # So in file line numbers (0-based): header is 0. Data row k is at line k+1.
    def load_rows_by_indices(path, indices):
        target_indices = set(indices)
        # skiprows: lineno -> bool. 
        # Line 0 is header (keep, so return False). 
        # Line k > 0 is data row k-1. We want to KEEP if (k-1) in target_indices.
        # So skip if (k-1) NOT in target_indices.
        return pd.read_csv(path, skiprows=lambda x: x > 0 and (x - 1) not in target_indices)
    
    print("Loading random rows from dataset 1...")
    df1 = load_rows_by_indices(dataset1_path, indices1)
    print("Loading random rows from dataset 2...")
    df2 = load_rows_by_indices(dataset2_path, indices2)
    
    # Shuffle to decouple the sorted loading order
    df1 = df1.sample(frac=1).reset_index(drop=True)
    df2 = df2.sample(frac=1).reset_index(drop=True)
    
    # Rename ALL columns including VIN
    df1_renamed = df1.rename(columns={c: f"{c}_used_cars" for c in df1.columns})
    df2_renamed = df2.rename(columns={c: f"{c}_vehicles" for c in df2.columns})

    candidates = pd.concat([df1_renamed, df2_renamed], axis=1)

    # Filter out accidental positive matches (same VIN)
    candidates = candidates[candidates['VIN_used_cars'] != candidates['VIN_vehicles']]

    candidates['match_label'] = 0

    print(f"Created {len(candidates)} negative pairs")
    return candidates.to_dict('records')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create pairs of records for matching")
    parser.add_argument("-o", "--output", type=str, default="pairs.csv", help="Output CSV file for pairs")
    parser.add_argument("match_table", type=str, help="CSV file containing the match table")
    parser.add_argument("dataset1", type=str, help="First dataset CSV file")
    parser.add_argument("dataset2", type=str, help="Second dataset CSV file")
    args = parser.parse_args()

    # Load datasets with chunks
    match_table = pd.read_csv(args.match_table)
    positive_pairs_amount = len(match_table)
    print(f"Number of positive pairs: {positive_pairs_amount}")

    
    for chunk_used_cars in pd.read_csv(args.dataset1, chunksize=100000):
        for chunk_vehicles in pd.read_csv(args.dataset2, chunksize=100000):
            positive_pairs = match_chunk(chunk_used_cars, chunk_vehicles)
            if not positive_pairs.empty:
                positive_pairs.to_csv(args.output, mode='a', index=False, header=not os.path.exists(args.output))
    
    negative_pairs = create_negative_pairs(args.dataset1, args.dataset2, positive_pairs_amount)
    # append negative pairs to the same output file
    pd.DataFrame(negative_pairs).to_csv(args.output, mode='a', index=False, header=not os.path.exists(args.output))

        
            