import csv
import json
import os
from datetime import datetime

PASSENGER_WEIGHT_LBS = 175  # Standard simbrief passenger weight in pounds

# File paths
CSV_INPUT = os.environ.get('CSV_INPUT', 'subfleets-01-16-26.csv')
JSON_INPUT = 'aircraft_data_20260116_003044.json'
AIRCRAFT_CONFIG = os.path.join(os.path.dirname(__file__), '..', 'aircraft_config.json')
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
CSV_OUTPUT = f'final_subfleets_with_updated_fares.csv'

# Load custom SimBrief profiles from aircraft_config.json
# These are aircraft that require custom SimBrief profiles (not in standard SimBrief database)
with open(AIRCRAFT_CONFIG, 'r', encoding='utf-8') as f:
    aircraft_config = json.load(f)

custom_fare_data = {
    icao: entry['simbrief']
    for icao, entry in aircraft_config.items()
    if 'simbrief' in entry
}

# Utility: Calculate cargo capacity
def calculate_cargo_capacity(mzfw, oew, pax_count):
    return max(0, mzfw - oew - (pax_count * PASSENGER_WEIGHT_LBS))

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
    elif aircraft_type in custom_fare_data:
        for cabin in ['F', 'Y', 'J']:
            value = custom_fare_data[aircraft_type].get(cabin, 0)
            if value > 0:
                fares.append(f'{cabin}?capacity={int(value)}')
        cargo = calculate_cargo_capacity(custom_fare_data[aircraft_type].get('mzfw_lbs',0),
                                         custom_fare_data[aircraft_type].get('oei_lbs',0),
                                         custom_fare_data[aircraft_type].get('default_pax',0))
        fares.append(f'CGO?capacity={int(cargo)}')
        row['fares'] = ';'.join(fares)
        

# Write updated CSV
with open(CSV_OUTPUT, 'w', newline='', encoding='utf-8') as csvfile_out:
    writer = csv.DictWriter(csvfile_out, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f'Updated CSV saved as {CSV_OUTPUT}')
