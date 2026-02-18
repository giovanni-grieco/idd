python3 splitter.py --fraction 0.06 cleaned_used_cars_data.csv 6per_cleaned_used_cars_data.csv
python3 splitter.py --fraction 0.6 cleaned_vehicles.csv 60per_cleaned_vehicles.csv

python3 match_table.py -o match_table_60v6.csv 6per_cleaned_used_cars_data.csv 60per_cleaned_vehicles.csv