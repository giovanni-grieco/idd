import os
import argparse
import pandas as pd
import random

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("table1", type=str, help="path to the first table")
    parser.add_argument("table2", type=str, help="path to the second table")
    parser.add_argument("match_table", type=str, help="path to the table containing the matches")
    parser.add_argument("--output", type=str, default="ditto_pairs.csv", help="output file name")
    parser.add_argument("--chunksize", type=int, default=10000, help="chunk size for reading csvs")
    args = parser.parse_args()

    # Carica la tabella dei match come set di tuple (row_id_x, row_id_y)
    match_table = set()
    with open(args.match_table) as f:
        for line in f:
            match_table.add(tuple(line.strip().split(",")))

    # 1. Estrai tutte le righe di table1 e table2 che servono per i positivi
    needed_row_id_x = set(row_id_x for row_id_x, _ in match_table)
    needed_row_id_y = set(row_id_y for _, row_id_y in match_table)

    df1_rows = {}
    for chunk in pd.read_csv(args.table1, chunksize=args.chunksize):
        chunk = chunk.drop(columns=["VIN"])
        chunk = chunk.rename(columns=lambda x: x + "_1" if x != "row_id" else "row_id_1")
        for _, row in chunk.iterrows():
            row_id_x = str(row["row_id_1"])
            if row_id_x in needed_row_id_x:
                df1_rows[row_id_x] = row

    df2_rows = {}
    for chunk in pd.read_csv(args.table2, chunksize=args.chunksize):
        chunk = chunk.drop(columns=["VIN"])
        chunk = chunk.rename(columns=lambda x: x + "_2" if x != "row_id" else "row_id_2")
        for _, row in chunk.iterrows():
            row_id_y = str(row["row_id_2"])
            if row_id_y in needed_row_id_y:
                df2_rows[row_id_y] = row

    # 2. Genera i positivi
    positive_pairs = []
    for row_id_x, row_id_y in match_table:
        if row_id_x in df1_rows and row_id_y in df2_rows:
            row_x = df1_rows[row_id_x]
            row_y = df2_rows[row_id_y]
            pair = pd.concat([row_x, row_y])
            pair["label"] = 1
            positive_pairs.append(pair)

    n_positive = len(positive_pairs)

    # 3. Estrai tutti i row_id possibili da table1 e table2 (in chunk)
    all_row_id_x = set()
    for chunk in pd.read_csv(args.table1, usecols=["row_id"], chunksize=args.chunksize):
        all_row_id_x.update(str(x) for x in chunk["row_id"].values)
    all_row_id_y = set()
    for chunk in pd.read_csv(args.table2, usecols=["row_id"], chunksize=args.chunksize):
        all_row_id_y.update(str(y) for y in chunk["row_id"].values)

    # 4. Genera candidati negativi (senza match)
    # Per evitare memoria, estraiamo a caso n_positive coppie negative
    all_row_id_x = list(all_row_id_x)
    all_row_id_y = list(all_row_id_y)
    negative_pairs_set = set()
    while len(negative_pairs_set) < n_positive:
        row_id_x = random.choice(all_row_id_x)
        row_id_y = random.choice(all_row_id_y)
        if (row_id_x, row_id_y) not in match_table and (row_id_x, row_id_y) not in negative_pairs_set:
            negative_pairs_set.add((row_id_x, row_id_y))

    # 5. Per i negativi, estrai le righe necessarie (chunked)
    needed_neg_row_id_x = set(row_id_x for row_id_x, _ in negative_pairs_set)
    needed_neg_row_id_y = set(row_id_y for _, row_id_y in negative_pairs_set)

    neg_df1_rows = {}
    for chunk in pd.read_csv(args.table1, chunksize=args.chunksize):
        chunk = chunk.drop(columns=["VIN"])
        chunk = chunk.rename(columns=lambda x: x + "_1" if x != "row_id" else "row_id_1")
        for _, row in chunk.iterrows():
            row_id_x = str(row["row_id_1"])
            if row_id_x in needed_neg_row_id_x:
                neg_df1_rows[row_id_x] = row

    neg_df2_rows = {}
    for chunk in pd.read_csv(args.table2, chunksize=args.chunksize):
        chunk = chunk.drop(columns=["VIN"])
        chunk = chunk.rename(columns=lambda x: x + "_2" if x != "row_id" else "row_id_2")
        for _, row in chunk.iterrows():
            row_id_y = str(row["row_id_2"])
            if row_id_y in needed_neg_row_id_y:
                neg_df2_rows[row_id_y] = row

    negative_pairs = []
    for row_id_x, row_id_y in negative_pairs_set:
        if row_id_x in neg_df1_rows and row_id_y in neg_df2_rows:
            row_x = neg_df1_rows[row_id_x]
            row_y = neg_df2_rows[row_id_y]
            pair = pd.concat([row_x, row_y])
            pair["label"] = 0
            negative_pairs.append(pair)

    # 6. Unisci e mescola
    all_pairs = positive_pairs + negative_pairs
    random.shuffle(all_pairs)

    # 7. Scrivi su disco a chunk
    # Per evitare di creare un DataFrame gigante, scriviamo a blocchi
    if all_pairs:
        # Prendi le colonne dal primo elemento
        out_cols = list(all_pairs[0].index)
        
        # Scrivi l'header
        with open(args.output, "w") as f:
            f.write(",".join(out_cols) + "\n")

        # Scrivi i dati a chunk
        chunk_size_write = 10000
        for i in range(0, len(all_pairs), chunk_size_write):
            chunk_pairs = all_pairs[i : i + chunk_size_write]
            df_chunk = pd.DataFrame(chunk_pairs)
            df_chunk.to_csv(args.output, mode="a", header=False, index=False)

    # 8. Genera train/valid/test per Ditto
    # Usiamo all_pairs che è già stato mescolato
    # Format: COL col1 VAL val1 ... \t COL col1 VAL val1 ... \t label
    
    print("Generazione file train/valid/test per Ditto...")
    
    def serialize_row(row):
        left_parts = []
        right_parts = []
        
        # Identifica colonne left e right
        for col, val in row.items():
            if col in ["label", "row_id_1", "row_id_2"]:
                continue
            
            val_str = str(val).strip().replace("\t", " ").replace("\n", " ")
            if val_str == "nan" or val_str == "":
                continue
                
            if col.endswith("_1"):
                clean_col = col[:-2]
                left_parts.append(f"COL {clean_col} VAL {val_str}")
            elif col.endswith("_2"):
                clean_col = col[:-2]
                right_parts.append(f"COL {clean_col} VAL {val_str}")
        
        left_str = " ".join(left_parts)
        right_str = " ".join(right_parts)
        label = str(int(row["label"]))
        
        return f"{left_str}\t{right_str}\t{label}"

    total_size = len(all_pairs)
    train_size = int(total_size * 0.8)
    valid_size = int(total_size * 0.1)
    # test size is the rest

    train_data = all_pairs[:train_size]
    valid_data = all_pairs[train_size : train_size + valid_size]
    test_data = all_pairs[train_size + valid_size :]

    def write_ditto_file(filename, data):
        with open(filename, "w") as f:
            for row in data:
                line = serialize_row(row)
                f.write(line + "\n")

    base_dir = os.path.dirname(args.output) if os.path.dirname(args.output) else "."
    write_ditto_file(os.path.join(base_dir, "train.txt"), train_data)
    write_ditto_file(os.path.join(base_dir, "valid.txt"), valid_data)
    write_ditto_file(os.path.join(base_dir, "test.txt"), test_data)

    print("File generated: train.txt, valid.txt, test.txt")

