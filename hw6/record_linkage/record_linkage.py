import recordlinkage
import pandas as pd

# 1. Load the blocked pairs
# Use a sample or the full file
input_file = "blocked1_test.csv"  # Ensure this path matches your file location
df_pairs = pd.read_csv(input_file)

# 2. Separate the pairs back into two DataFrames
# Define the suffixes based on your schema
suffix_a = "_used_cars"
suffix_b = "_vehicles"
columns_to_drop = ["match_label", f"vin{suffix_a}", f"vin{suffix_b}"]

# Filter columns for A and B
cols_a = [c for c in df_pairs.columns if c.endswith(suffix_a)]
cols_b = [c for c in df_pairs.columns if c.endswith(suffix_b)]

# Create dfA and dfB
# We effectively reset the index so row 0 in dfA corresponds to row 0 in dfB
dfA = df_pairs[cols_a].copy()
dfB = df_pairs[cols_b].copy()

# 3. Clean up DataFrames
# Remove cheating columns if they exist
for col in columns_to_drop:
    a_col = col  # Specific logic might be needed if column names vary slightly
    if a_col in dfA.columns:
        dfA.drop(columns=[a_col], inplace=True)
    if a_col in dfB.columns:
        dfB.drop(columns=[a_col], inplace=True)

# Rename columns to remove suffixes so the comparator knows they represent the same feature
dfA.columns = [c.replace(suffix_a, "") for c in dfA.columns]
dfB.columns = [c.replace(suffix_b, "") for c in dfB.columns]

# Ensure indices are unique identifiers.
# Since row N in df_pairs corresponds to row N in separate dfs, we can use the default integer index.
dfA.index.name = "id_a"
dfB.index.name = "id_b"

# 4. Construct the Candidate Links
# Since the input file IS the list of pairs, we simply link index i of dfA to index i of dfB.
# This creates a diagonal mapping: (0,0), (1,1), (2,2)...
candidate_links = pd.MultiIndex.from_arrays(
    [dfA.index, dfB.index],
    names=["id_a", "id_b"]
)

# 5. Define Comparison Logic
compare_cl = recordlinkage.Compare()

# Exact matches
compare_cl.exact("year", "year", label="year")
compare_cl.exact("body_type", "body_type", label="body_type")
compare_cl.exact("fuel_type", "fuel_type", label="fuel_type")

# String comparisons
compare_cl.string("manufacturer", "manufacturer", method="jarowinkler", threshold=0.85, label="manufacturer")
compare_cl.string("model", "model", method="jarowinkler", threshold=0.85, label="model")
compare_cl.string("color", "color", method="levenshtein", threshold=0.80, label="color")

# Description is often messy, lower threshold
compare_cl.string("description", "description", method="jarowinkler", threshold=0.60, label="description")

# Numeric comparisons (e.g., price, mileage)
# Using 'step' or 'linear' allows for small differences
compare_cl.numeric("price", "price", method="gauss", offset=100.0, scale=1000.0, label="price")
compare_cl.numeric("mileage", "mileage", method="gauss", offset=500.0, scale=5000.0, label="mileage")

# 6. Compute Features
print("Computing features...")
features = compare_cl.compute(candidate_links, dfA, dfB)

print("\n--- Features Head ---")
print(features.head())

# 7. Simple Classification (Example)
# Summing up the comparison vector (0 or 1 for exact/string thresh matches)
# Numeric comparisons return 0.0 to 1.0
matches = features[features.sum(axis=1) > 5]  # Arbitrary threshold
print(f"\nFound {len(matches)} matches out of {len(features)} pairs.")
