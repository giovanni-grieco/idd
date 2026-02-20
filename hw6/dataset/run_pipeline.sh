python3 align_schema.py
python3 match_table.py -o match_table.csv a_used_cars_data.csv a_vehicles.csv
python3 make_pairs.py -o pairs.csv match_table.csv a_used_cars_data.csv a_vehicles.csv