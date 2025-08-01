import csv
import os
import random
import time
import argparse
from datetime import datetime, timedelta
import requests

# Constants
START_FLIGHT_NUMBER = 1000
API_URL = "https://airportgap.com/api/airports/distance"
TOKEN = os.getenv("AIRPORT_GAP_TOKEN")
HEADERS = {"Authorization": f"Bearer token={TOKEN}"}
TIME_FMT = '%H:%M'
MAX_REQUESTS_PER_MIN = 100

special_code_to_airline = {
    "CRC" : "CRN"
}

v5_flight_type_to_v7 = {
    "P" : "J", # vuelos comerciales scheduled
    "C" : "F"  # vuelos de carga scheduled
}

airline_subfleet_by_flight_type = {
    "CRN" : {
        "J" : ["B734","B733","SH36","SH33","TRIS","BN2P","GA8","MI8","AN2","C172","B789","B78X","B762","BCS1","BCS3","A306","SU95","C208","B736","A20N","A21N","A310","A319","A320","A321","A332","A333","A346","A359","A388","AN24","AN26","AT45","AT46","AT75","AT76","B38M","B712","B732","B735","B737","B738","B739","B744","B752","B753","B763","B764","B77L","B77W","B788","C25C","DH8D","E110","E140","E145","E175","E190","E195","IL18","IL96","KODI","L410","PC12","TBM9","YK40"], #passengers subfleet string
        "F" : ["SH36F","SH33F","A124","AT76F","E190F","A225","A30F","B48F","B74F","B75F","B76F","B77F","MD1F"], #freighter subfleet
    }
}

aircrafts_range_by_icao = {'SH36F':'800','SH33F':'600','B734':'2060','B733':'2255','SH36':'800','SH33':'600','TRIS':'620','BN2P':'620','GA8':'730','MI8':'335','AN2':'450','A124':'3200','AT76F':'1000','E190F':'2300','C172':'600','B789':'7600','B78X':'6300','B762':'3900','BCS1':'3400','BCS3':'3300','A306':'4000','SU95':'2700','C208':'1000','B736':'3600','A225': '3900','A20N': '3500', 'A21N': '4000', 'A30F': '4200', 'A310': '5150', 'A319': '3700', 'A320': '3300', 'A321': '2300', 'A332': '7250', 'A333': '6350', 'A346': '7900', 'A359': '8100', 'A388': '8000', 'AN24': '1000', 'AN26': '1100', 'AT45': '850', 'AT46': '800', 'AT75': '825', 'AT76': '950', 'B38M': '3550', 'B48F': '4200', 'B712': '2060', 'B732': '2300', 'B735': '1600', 'B737': '3350', 'B738': '3400', 'B739': '3200', 'B744': '7260', 'B74F': '4970', 'B752': '3900', 'B753': '3800', 'B75F': '3600', 'B763': '6000', 'B764': '6000', 'B76F': '3255', 'B77F': '8555', 'B77L': '8555', 'B77W': '7370', 'B788': '7355', 'C25C': '2165', 'DH8D': '1100', 'E110': '1200', 'E140': '1600', 'E145': '1550', 'E175': '2000', 'E190': '2400', 'E195': '2200', 'IL18': '2200', 'IL96': '6000', 'KODI': '1132', 'L410': '800', 'MD1F': '3800', 'PC12': '1845', 'TBM9': '1730', 'YK40': '1000'}


def calculate_flight_times(distance_nm):
    dpt_hour = random.randint(5, 22)
    dpt_minute = random.choice([0, 15, 30, 45])
    dpt_time = datetime.strptime(f"{dpt_hour:02}:{dpt_minute:02}", TIME_FMT)
    avg_speed_knots = 300
    flight_time_min = (distance_nm / avg_speed_knots) * 60
    arr_time = dpt_time + timedelta(minutes=flight_time_min)
    return (dpt_time.strftime(TIME_FMT), arr_time.strftime(TIME_FMT), str(int(flight_time_min)))

def fetch_distance(from_iata, to_iata):
    response = requests.post(API_URL, data={"from": from_iata, "to": to_iata}, headers=HEADERS)
    while response.status_code == 429:
        print("Rate limit hit. Waiting 60 seconds...")
        time.sleep(60)
        response = requests.post(API_URL, data={"from": from_iata, "to": to_iata}, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return int(data['data']['attributes']['nautical_miles'])
    else:
        raise Exception(f"Failed to fetch distance: {response.status_code}, {response.text}")

def parse_airport_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.read().strip().splitlines()
    pairs = []
    for line in lines:
        parts = line.split(',')
        a1_icao, a1_iata = parts[0].split('-')
        a2_icao, a2_iata = parts[1].split('-')
        pairs.append(((a1_icao, a1_iata), (a2_icao, a2_iata)))
    return pairs

def generate_flights(pairs, route_code, start_flight_number, output_csv):
    current_number = start_flight_number
    records = []
    requests_made = 0
    for (a1_icao, a1_iata), (a2_icao, a2_iata) in pairs:
        # Rate limit handling
        if requests_made >= MAX_REQUESTS_PER_MIN:
            print("Reached 100 API requests, sleeping for 60 seconds...")
            time.sleep(60)
            requests_made = 0
        distance = fetch_distance(a1_iata, a2_iata)
        requests_made += 1

        # Generate Passenger Outbound
        dpt, arr, flt = calculate_flight_times(distance)
        records.append([
            "CRN", current_number, route_code, "", "", a1_icao, a2_icao, "", "1234567",
            dpt, arr, "", distance, flt, "J", "", "", "", "", "", "", "", "1", "", "", "", "", ""
        ])
        current_number += 1

        # Passenger Return
        dpt, arr, flt = calculate_flight_times(distance)
        records.append([
            "CRN", current_number, route_code, "", "", a2_icao, a1_icao, "", "1234567",
            dpt, arr, "", distance, flt, "J", "", "", "", "", "", "", "", "1", "", "", "", "", ""
        ])
        current_number += 1

        # Cargo Outbound
        dpt, arr, flt = calculate_flight_times(distance)
        records.append([
            "CRN", current_number, route_code, "", "", a1_icao, a2_icao, "", "1234567",
            dpt, arr, "", distance, flt, "F", "", "", "", "", "", "", "", "1", "", "", "", "", ""
        ])
        current_number += 1

        # Cargo Return
        dpt, arr, flt = calculate_flight_times(distance)
        records.append([
            "CRN", current_number, route_code, "", "", a2_icao, a1_icao, "", "1234567",
            dpt, arr, "", distance, flt, "F", "", "", "", "", "", "", "", "1", "", "", "", "", ""
        ])
        current_number += 1

    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "airline", "flight_number", "route_code", "callsign", "route_leg", "dpt_airport",
            "arr_airport", "alt_airport", "days", "dpt_time", "arr_time", "level", "distance",
            "flight_time", "flight_type", "load_factor", "load_factor_variance", "pilot_pay",
            "route", "notes", "start_date", "end_date", "active", "subfleets", "fares", "fields",
            "event_id", "user_id"
        ])
        writer.writerows(records)

def split(filehandler, delimiter=',', row_limit=1000,
          output_name_template='output_%s.csv', output_path='.', keep_headers=True):
    reader = csv.reader(filehandler, delimiter=delimiter)
    current_piece = 1
    current_out_path = os.path.join(
        output_path,
        output_name_template % current_piece
    )
    current_out_writer = csv.writer(open(current_out_path, 'w',newline=''), delimiter=delimiter)
    current_limit = row_limit
    if keep_headers:
        headers = next(reader)
        current_out_writer.writerow(headers)
    for i, row in enumerate(reader):
        if i + 1 > current_limit:
            current_piece += 1
            current_limit = row_limit * current_piece
            current_out_path = os.path.join(
                output_path,
                output_name_template % current_piece
            )
            current_out_writer = csv.writer(open(current_out_path, 'w',newline=''), delimiter=delimiter)
            if keep_headers:
                current_out_writer.writerow(headers)
        current_out_writer.writerow(row)

def remove_non_numeric(text):
    return "".join(filter(str.isdigit, text))

def update_subfleets(airport_icao,route_code,time_generated,CSV_INPUT):
    # Read and update CSV
    with open(CSV_INPUT, 'r', newline='', encoding='utf-8') as csvfile_in:
        reader = csv.DictReader(csvfile_in)
        rows = list(reader)
        fieldnames = reader.fieldnames

    indexes_to_remove = []
    for idx,row in enumerate(rows):
        flight_number = int(remove_non_numeric(str(row['flight_number'])))
        if flight_number < 100:
            # skip and remove
            indexes_to_remove.append(idx)
            print(f"indx: {idx} | Flight: {flight_number} marked for deletion")
            continue

        flight_distance = int(row['distance'])
        flight_type = row["flight_type"] 
        subfleets = []
        for aircraft_icao in airline_subfleet_by_flight_type["CRN"][flight_type]:
                if flight_distance < int(aircrafts_range_by_icao[aircraft_icao]):
                    subfleets.append(aircraft_icao)
        row['subfleets'] = ';'.join(subfleets)

    
    # remove unwanted flights
    print("Checking flights that need to be removed")
    if len(indexes_to_remove) > 0:
        print(f"Total number of schedules is {len(rows)}")
        for idx,i in enumerate(indexes_to_remove):
            # print(f"Removing Flight: {rows[i-idx]}")
            del rows[i-idx]
        print(f"Completed removing {len(indexes_to_remove)} flights that don't meet flight number requirement of 3 or more digits")
        print(f"The new total number of schedules is {len(rows)}")
    else:
        print("No flights found that need to be removed")

    # Write updated CSV
    timestr = time.strftime("%Y%m%d-%H%M%S")
    os.makedirs(f"{airport_icao}_{route_code}/{time_generated}/", exist_ok=True)
    CSV_OUTPUT = f"{airport_icao}_{route_code}/{time_generated}/exported_{CSV_INPUT}"
    with open(CSV_OUTPUT, 'w', newline='', encoding='utf-8') as csvfile_out:
        writer = csv.DictWriter(csvfile_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f'Updated CSV saved as {CSV_OUTPUT}')

    # if file has more than 500 schedules separate in files of 500 flights per file
    if len(rows) > 500:
        print("Spliting schedules into multiple files for import")
        with open(CSV_OUTPUT,'r') as file:
            split(file,row_limit=500,output_path=f"{route_code}/{time_generated}")

# Example usage (uncomment to run):
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate phpVMS flights.")
    parser.add_argument("airport_icao", help="Base Airport ICAO (e.g., MUHA)")
    parser.add_argument("route_code", help="Airport IATA (e.g., HAV)")
    args = parser.parse_args()
    AIRPORT_ICAO=args.airport_icao
    route_code=args.route_code
    os.makedirs(f"{AIRPORT_ICAO}_{route_code}", exist_ok=True)
    time_generated = time.strftime("%Y%m%d-%H%M%S")
    generate_flights(parse_airport_file(f"{AIRPORT_ICAO}_{route_code}/airports.txt"), route_code, START_FLIGHT_NUMBER, f"{AIRPORT_ICAO}_{route_code}_{time_generated}_generated_phpvms_flights.csv")
    update_subfleets(AIRPORT_ICAO,route_code,time_generated,f"{AIRPORT_ICAO}_{route_code}_{time_generated}_generated_phpvms_flights.csv") #add the subfleets based on flight distance
