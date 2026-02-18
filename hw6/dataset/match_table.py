import pandas as pd
import argparse
import os

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Create a match table based on VIN from two aligned datasets.")
    parser.add_argument("table1", help="Path to the first aligned CSV file (e.g., aligned_used_cars_data.csv)")
    parser.add_argument("table2", help="Path to the second aligned CSV file (e.g., aligned_vehicles.csv)")
    parser.add_argument("-o", "--output", help="Path to the output match table CSV file (default: match_table.csv)", default="match_table.csv")
    args = parser.parse_args()

    # Remove output file if it exists to avoid header issues
    if os.path.exists(args.output):
        os.remove(args.output)

    for chunk_used_cars in pd.read_csv(args.table1, chunksize=1000):
        for chunk_vehicles in pd.read_csv(args.table2, chunksize=1000):
            # if VIN coincides, then we have a match and we save the row_ids in a third table
            merged = pd.merge(chunk_used_cars, chunk_vehicles, on="VIN", how="inner", suffixes=('_used_cars', '_vehicles'))
            if not merged.empty:
                merged[["row_id_used_cars", "row_id_vehicles"]].to_csv(
                    args.output, mode="a", index=False, header=not os.path.exists(args.output)
                )