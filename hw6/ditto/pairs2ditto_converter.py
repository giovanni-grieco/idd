## This script creates a train.txt, validation.txt and test.txt expected by Ditto from reading a pairs.csv file.
## It MUST remove the column "match_label" and all columns that start with "VIN" because it will make ditto cheat

import pandas as pd
import argparse
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, default="pairs.csv", help="CSV file containing the pairs with match labels")
    parser.add_argument("-o", "--output_dir", type=str, default="ditto/data/used_cars_vehicles", help="Directory to save the train.txt, validation.txt and test.txt files")
    args = parser.parse_args()

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)





if __name__ == "__main__":
    main()
