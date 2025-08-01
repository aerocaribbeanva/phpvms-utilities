import csv
import json
from datetime import datetime

PASSENGER_WEIGHT_LBS = 175  # Standard simbrief passenger weight in pounds

# File paths
CSV_INPUT = 'subfleets-7-5-25.csv'
JSON_INPUT = 'aircraft_data_20250705_084347.json'
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
CSV_OUTPUT = f'updated_fares_{timestamp}.csv'

# non simbrief aircraft data - this are aircrafts not available in simbrief and require a custom profile
# custom_fare_data = {
#         "ICAO" : {
#             "profile_url" : "",    
#             "icao": "",
#             "aircraft_name": "",
#             "base_type": "",
#             "default_pax": 0,
#             "mzfw_lbs": 0.0,
#             "oei_lbs": 0.0,
#             "is_freighter": False,
#             "F": 0,
#             "J": 0,
#             "Y": 0
#         }
# }

custom_fare_data = {
        "E190F" : {
            "simbrief_profile_url" : "https://dispatch.simbrief.com/airframes/share/1098250_1749676018149",    
            "icao": "E190",
            "aircraft_name": "Embraer E190F",
            "base_type": "E190",
            "default_pax": 0,
            "mzfw_lbs": 90169.0,
            "oei_lbs": 60519.0,
            "is_freighter": True,
            "F": 0,
            "J": 0,
            "Y": 0
        },
        "AT76F" : {
            "profile_url" : "https://dispatch.simbrief.com/airframes/share/1098250_1749677098517",    
            "icao": "AT76",
            "aircraft_name": "ATR-72-600F",
            "base_type": "AT76",
            "default_pax": 0,
            "mzfw_lbs": 46296.0,
            "oei_lbs": 26682.0,
            "is_freighter": True,
            "F": 0,
            "J": 0,
            "Y": 0
        },
        "A124" : {
            "profile_url" : "https://dispatch.simbrief.com/airframes/share/1098250_1748055323449",    
            "icao": "A124",
            "aircraft_name": "Antonov Ruslan AN124",
            "base_type": "A225",
            "default_pax": 88,
            "mzfw_lbs": 660000.0,
            "oei_lbs": 385800.0,
            "is_freighter": True,
            "F": 0,
            "J": 0,
            "Y": 88
        },
        "AN2" : {
            "profile_url" : "https://dispatch.simbrief.com/airframes/share/1098250_1748055373206",    
            "icao": "AN2",
            "aircraft_name": "Antonov AN-2",
            "base_type": "DHC2",
            "default_pax": 12,
            "mzfw_lbs": 10582.0,
            "oei_lbs": 7606.0,
            "is_freighter": False,
            "F": 0,
            "J": 0,
            "Y": 12
        },
        "MI8" : {
            "profile_url" : "https://dispatch.simbrief.com/airframes/share/1098250_1749677736521",    
            "icao": "MI8",
            "aircraft_name": "Mil Mi-17",
            "base_type": "DHC6",
            "default_pax": 0,
            "mzfw_lbs": 23982.0,
            "oei_lbs": 15961.0,
            "is_freighter": False,
            "F": 0,
            "J": 0,
            "Y": 24
        },
        "GA8" : {
            "profile_url" : "https://dispatch.simbrief.com/airframes/share/1098250_1749679355475",    
            "icao": "GA8",
            "aircraft_name": "Gippsland GA-8",
            "base_type": "C208",
            "default_pax": 7,
            "mzfw_lbs": 3474.0,
            "oei_lbs": 2198.0,
            "is_freighter": False,
            "F": 0,
            "J": 0,
            "Y": 7
        },
        "TRIS" : {
            "profile_url" : "https://dispatch.simbrief.com/airframes/share/1098250_1751717690590",    
            "icao": "TRIS",
            "aircraft_name": "BN-2 Trislander",
            "base_type": "C337",
            "default_pax": 9,
            "mzfw_lbs": 7700.0,
            "oei_lbs": 5800.0,
            "is_freighter": False,
            "F": 0,
            "J": 0,
            "Y": 9
        },
        "SH33F" : {
            "profile_url" : "https://dispatch.simbrief.com/airframes/share/1098250_1751718297516",    
            "icao": "SH33",
            "aircraft_name": "Short 330 Freigther",
            "base_type": "SH33",
            "default_pax": 0,
            "mzfw_lbs": 21140.0,
            "oei_lbs": 14200.0,
            "is_freighter": True,
            "F": 0,
            "J": 0,
            "Y": 0
        },
        "SH36F" : {
            "profile_url" : "https://dispatch.simbrief.com/airframes/share/1098250_1751718371090",    
            "icao": "SH36",
            "aircraft_name": "Short 360 Freighter",
            "base_type": "SH36",
            "default_pax": 0,
            "mzfw_lbs": 23140.0,
            "oei_lbs": 15350.0,
            "is_freighter": True,
            "F": 0,
            "J": 0,
            "Y": 0
        }
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
