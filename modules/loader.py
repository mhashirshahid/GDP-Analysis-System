import csv
import os
from itertools import chain

def transform_row(row):
    country = row.get('Country Name')
    region = row.get('Continent')

    is_valid_year = lambda item: (
        item[0].isdigit() and len(item[0]) == 4 and item[1] and item[1].strip()
    )

    to_dict = lambda item: {
        'Country': country,
        'Year': int(item[0]),
        'GDP': float(item[1]),
        'Region': region
    }

    return list(map(to_dict, filter(is_valid_year, row.items())))

def load_data(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            return list(chain.from_iterable(map(transform_row, reader)))
    except Exception as e:
        print(f"Error: {e}")
        return []

#Testing
if __name__ == "__main__":
    data = load_data('data/gdp_data.csv')
    if data:
        print(f"Output format check: {type(data)}")
        print(f"Sample row: {data[0]}")