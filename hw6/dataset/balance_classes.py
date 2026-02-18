
import pandas as pd
import numpy as np
import os
from tqdm import tqdm

# File paths
MATCH_TABLE = "match_table.csv"
USED_CARS = "cleaned_used_cars_data.csv"
VEHICLES = "cleaned_vehicles.csv"
BALANCED_USED_CARS = "balanced_cleaned_used_cars_data.csv"
BALANCED_VEHICLES = "balanced_cleaned_vehicles.csv"
CHUNK_SIZE = 100_000

# Load match table (small)
match_df = pd.read_csv(MATCH_TABLE)
used_cars_match_ids = set(match_df["row_id_used_cars"].unique())
vehicles_match_ids = set(match_df["row_id_vehicles"].unique())
num_pairs = len(match_df)

def process_balanced(input_csv, match_ids, output_csv, num_pairs, id_col="row_id", chunk_size=CHUNK_SIZE, random_state=42):
	# Remove output if exists
	if os.path.exists(output_csv):
		os.remove(output_csv)

	# First pass: write all matches, count non-matches
	non_match_row_offsets = []
	total_rows = 0
	first_chunk = True
	for chunk in tqdm(pd.read_csv(input_csv, chunksize=chunk_size), desc=f"Finding matches in {input_csv}"):
		matches = chunk[chunk[id_col].isin(match_ids)]
		if not matches.empty:
			matches.to_csv(output_csv, mode="a", index=False, header=first_chunk)
			first_chunk = False
		# Record non-match row indices (relative to file)
		non_matches = chunk[~chunk[id_col].isin(match_ids)]
		if not non_matches.empty:
			non_match_row_offsets.extend(total_rows + i for i in non_matches.index)
		total_rows += len(chunk)

	# Randomly select non-match row offsets
	if len(non_match_row_offsets) < num_pairs:
		raise ValueError(f"Not enough non-matching rows to sample {num_pairs} from {input_csv}")
	np.random.seed(random_state)
	chosen_offsets = set(np.random.choice(non_match_row_offsets, size=num_pairs, replace=False))

	# Second pass: write sampled non-matches
	written = 0
	current_row = 0
	for chunk in tqdm(pd.read_csv(input_csv, chunksize=chunk_size), desc=f"Writing non-matches from {input_csv}"):
		chunk_indices = range(current_row, current_row + len(chunk))
		mask = [idx in chosen_offsets for idx in chunk_indices]
		sampled = chunk[mask]
		if not sampled.empty:
			sampled.to_csv(output_csv, mode="a", index=False, header=False)
			written += len(sampled)
		current_row += len(chunk)
		if written >= num_pairs:
			break

	print(f"Balanced file written: {output_csv}")

process_balanced(USED_CARS, used_cars_match_ids, BALANCED_USED_CARS, num_pairs)
process_balanced(VEHICLES, vehicles_match_ids, BALANCED_VEHICLES, num_pairs)
