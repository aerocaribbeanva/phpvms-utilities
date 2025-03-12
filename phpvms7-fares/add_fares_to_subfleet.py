import csv
import json
from datetime import datetime

# File paths
CSV_INPUT = 'subfleets.csv'
JSON_INPUT = 'aircraft_data_20250311_202737.json'
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
CSV_OUTPUT = f'updated_fares_{timestamp}.csv'

# Load JSON fare data
with open(JSON_INPUT, 'r') as json_file:
    fare_data = json.load(json_file)

# Read and update CSV
with open(CSV_INPUT, 'r', newline='', encoding='utf-8') as csvfile_in:
    reader = csv.DictReader(csvfile_in)
    rows = list(reader)
    fieldnames = reader.fieldnames

for row in rows:
    aircraft_type = row['type']
    fares = []
    if aircraft_type in fare_data:
        for cabin in ['F', 'Y', 'J', 'CGO']:
            value = fare_data[aircraft_type].get(cabin, 0)
            if value > 0:
                fares.append(f'{cabin}?capacity={int(value)}')
    row['fares'] = ';'.join(fares)

# Write updated CSV
with open(CSV_OUTPUT, 'w', newline='', encoding='utf-8') as csvfile_out:
    writer = csv.DictWriter(csvfile_out, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f'Updated CSV saved as {CSV_OUTPUT}')
