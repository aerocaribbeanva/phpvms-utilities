import csv
import os
import shutil
import json
import random
import time
import argparse
from datetime import datetime, timedelta
import requests
import sys

# Constants
GLOB_FILTER_SUBFLEETS=[]
CACHE_FILE = "distance_cache.json"
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
        "J" : ["BBJ2","H60","C402","DHC6","EC35","EC45","B734","B733","SH36","SH33","TRIS","BN2P","GA8","MI8","AN2","C172","B789","B78X","B762","BCS1","BCS3","A306","SU95","C208","B736","A20N","A21N","A310","A319","A320","A321","A332","A333","A346","A359","A388","AN24","AN26","AT45","AT46","AT75","AT76","B38M","B712","B732","B735","B737","B738","B739","B744","B752","B753","B763","B764","B77L","B77W","B788","C25C","DH8D","E110","E140","E145","E175","E190","E195","IL18","IL96","KODI","L410","PC12","TBM9","YK40"], #passengers subfleet string
        "F" : ["A333F","B738F","AN26F","SH36F","SH33F","A124","AT76F","E190F","A225","A30F","B48F","B74F","B75F","B76F","B77F","MD1F"], #freighter subfleet
    }
}

aircrafts_range_by_icao = {'BBJ2':'3400','A333F':'6350','B738F':'3400','AN26F':'1100','H60':'700','C402':'920','DHC6':'771','EC35':'342','EC45':'351','SH36F':'800','SH33F':'600','B734':'2060','B733':'2255','SH36':'800','SH33':'600','TRIS':'620','BN2P':'620','GA8':'730','MI8':'335','AN2':'450','A124':'3200','AT76F':'1000','E190F':'2300','C172':'600','B789':'7600','B78X':'6300','B762':'3900','BCS1':'3400','BCS3':'3300','A306':'4000','SU95':'2700','C208':'1000','B736':'3600','A225': '3900','A20N': '3500', 'A21N': '4000', 'A30F': '4200', 'A310': '5150', 'A319': '3700', 'A320': '3300', 'A321': '2300', 'A332': '7250', 'A333': '6350', 'A346': '7900', 'A359': '8100', 'A388': '8000', 'AN24': '1000', 'AN26': '1100', 'AT45': '850', 'AT46': '800', 'AT75': '825', 'AT76': '950', 'B38M': '3550', 'B48F': '4200', 'B712': '2060', 'B732': '2300', 'B735': '1600', 'B737': '3350', 'B738': '3400', 'B739': '3200', 'B744': '7260', 'B74F': '4970', 'B752': '3900', 'B753': '3800', 'B75F': '3600', 'B763': '6000', 'B764': '6000', 'B76F': '3255', 'B77F': '8555', 'B77L': '8555', 'B77W': '7370', 'B788': '7355', 'C25C': '2165', 'DH8D': '1100', 'E110': '1200', 'E140': '1600', 'E145': '1550', 'E175': '2000', 'E190': '2400', 'E195': '2200', 'IL18': '2200', 'IL96': '6000', 'KODI': '1132', 'L410': '800', 'MD1F': '3800', 'PC12': '1845', 'TBM9': '1730', 'YK40': '1000'}

def _auto_yes():
    # --yes flag set in argparse below, or CI env present
    return getattr(sys.modules[__name__], "_assume_yes", False) or os.environ.get("CI") == "true"

def calculate_flight_times(distance_nm):
    dpt_hour = random.randint(5, 22)
    dpt_minute = random.choice([0, 15, 30, 45])
    dpt_time = datetime.strptime(f"{dpt_hour:02}:{dpt_minute:02}", TIME_FMT)
    avg_speed_knots = 300
    flight_time_min = (distance_nm / avg_speed_knots) * 60
    arr_time = dpt_time + timedelta(minutes=flight_time_min)
    return (dpt_time.strftime(TIME_FMT), arr_time.strftime(TIME_FMT), str(int(flight_time_min)))

def _load_cache(path=CACHE_FILE):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # Corrupt file? start fresh.
            return {}
    return {}

def _save_cache(cache: dict, path=CACHE_FILE):
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2, sort_keys=True)
    os.replace(tmp, path)

def _key_for_route(from_iata: str, to_iata: str) -> str:
    """Symmetric cache key so A-B and B-A hit the same entry."""
    a, b = from_iata.strip().upper(), to_iata.strip().upper()
    return f"{min(a,b)}-{max(a,b)}"

def fetch_distance(from_iata, to_iata, cache_path: str = CACHE_FILE):
    """
    Fetch great-circle distance in nautical miles between two IATA codes.
    Uses a JSON file cache to avoid repeated API calls.
    """
    cache = _load_cache(cache_path)
    key = _key_for_route(from_iata, to_iata)

    # 1) Cache hit
    if key in cache:
        return int(cache[key])
    
    # 2) Cache miss → call API with basic rate-limit handling
    payload = {"from": from_iata, "to": to_iata}
    print("Cache miss → call API with basic rate-limit handling")
    print(f"Retrieve distance {payload}")
    backoff = 30  # seconds
    max_wait = 5 * 60  # cap total wait per call (optional)

    waited = 0
    while True:
        response = requests.post(API_URL, data=payload, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            nm = int(data["data"]["attributes"]["nautical_miles"])
            cache[key] = nm
            _save_cache(cache, cache_path)
            return nm

        if response.status_code == 429:
            # Rate limited → wait and retry with exponential backoff (capped)
            sleep_s = min(backoff, max_wait - waited) if max_wait else backoff
            if sleep_s <= 0:
                raise TimeoutError("Rate limit persisted too long; aborting.")
            print(f"Rate limit hit. Waiting {sleep_s} seconds...")
            time.sleep(sleep_s)
            waited += sleep_s
            backoff = min(backoff * 2, 120)  # grow to a max of 2 min
            continue

        # Other non-200 responses → raise with details
        try:
            err_txt = response.text
        except Exception:
            err_txt = "<no body>"
        raise Exception(f"Failed to fetch distance ({response.status_code}): {err_txt}")

def parse_airport_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.read().strip().splitlines()
    pairs = []
    for line in lines:
        # if line has a comment ignore that comment
        if '#' in line:
            # save the line without the comment
            line = line.split('#')[0].strip()
        parts = line.split(',')
        a1_icao, a1_iata = parts[0].split('-')
        a2_icao, a2_iata = parts[1].split('-')
        pairs.append(((a1_icao, a1_iata), (a2_icao, a2_iata)))
    return pairs

def has_duplicates(pairs):
    # convert the pairs to a set which removes duplicates
    set_pairs = set(pairs)
    if len(pairs) != len(set_pairs):
        # if the lenght is not equal we found duplicates
        print("Duplicate entries found aborting flight generation.\nRemove duplicated lines")
        # print any duplicated lines
        pairs_dict = dict()
        for index,pair in enumerate(pairs):
            if pair not in pairs_dict.keys():
                pairs_dict[pair] = 1
            else:
                pairs_dict[pair] +=1
                print(f"Line {index + 1}: {pair} has been found {pairs_dict[pair]} times on file")
        return True
    return False


def generate_flights(pairs, route_code, start_flight_number, output_csv,is_tour_mode=False, tour_config={}):
    current_number = start_flight_number
    records = []
    requests_made = 0

    if is_tour_mode:
        print("Generating Tours Legs")
        try:
            current_number = int(tour_config.get("start_flight_number", "8000"))
        except ValueError:
            print("❌ Invalid 'start_flight_number' in tour config. Falling back to 8000.")
            current_number = 8000
        flight_type = tour_config.get("flight_type", "J").strip().upper()
        pilot_pay = tour_config.get("pilot_pay", "").strip()
        notes = tour_config.get("notes", "").strip()
        start_date = tour_config.get("start_date","").strip()
        end_date = tour_config.get("end_date","").strip()
        filter_subfleets = tour_config.get("subfleets",[])
        if len(filter_subfleets) > 0:
            print("---TOUR SUBFLEET---")
            print(filter_subfleets)
            global GLOB_FILTER_SUBFLEETS
            GLOB_FILTER_SUBFLEETS = filter_subfleets

        for leg_number, ((a1_icao, a1_iata), (a2_icao, a2_iata)) in enumerate(pairs, start=1):
            if requests_made >= MAX_REQUESTS_PER_MIN:
                print("Reached 100 API requests, sleeping for 60 seconds...")
                time.sleep(60)
                requests_made = 0
            distance = fetch_distance(a1_iata, a2_iata)
            requests_made += 1

            dpt, arr, flt = calculate_flight_times(distance)

            records.append([
                "CRN", current_number, route_code.upper(), "", leg_number, a1_icao, a2_icao, "", "1234567",
                dpt, arr, "", distance, flt, flight_type, "", "", pilot_pay,
                "", notes, start_date, end_date, "0", "", "", "", "", ""
            ])
            current_number += 1
    else:
        print("Generating Scheduled Flights")
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
                "CRN", current_number, route_code, current_number, "", a1_icao, a2_icao, "", "1234567",
                dpt, arr, "", distance, flt, "J", "", "", "", "", "", "", "", "1", "", "", "", "", ""
            ])
            current_number += 1

            # Passenger Return
            dpt, arr, flt = calculate_flight_times(distance)
            records.append([
                "CRN", current_number, route_code, current_number, "", a2_icao, a1_icao, "", "1234567",
                dpt, arr, "", distance, flt, "J", "", "", "", "", "", "", "", "1", "", "", "", "", ""
            ])
            current_number += 1

            # Cargo Outbound
            dpt, arr, flt = calculate_flight_times(distance)
            records.append([
                "CRN", current_number, route_code, current_number, "", a1_icao, a2_icao, "", "1234567",
                dpt, arr, "", distance, flt, "F", "", "", "", "", "", "", "", "1", "", "", "", "", ""
            ])
            current_number += 1

            # Cargo Return
            dpt, arr, flt = calculate_flight_times(distance)
            records.append([
                "CRN", current_number, route_code, current_number, "", a2_icao, a1_icao, "", "1234567",
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

def update_subfleets(airport_icao,route_code,time_generated,CSV_INPUT,is_tour_mode=False,filter_subfleets=[]):
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
                if len(filter_subfleets) > 0:
                    if (aircraft_icao in filter_subfleets):
                        # if filter subfleet is passed only add aircraft if is in list               
                        subfleets.append(aircraft_icao)
                else:
                    # if no subfleet filter is passed just add the aircraft
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
    if is_tour_mode:
        os.makedirs(f"TOURS/{route_code}/{time_generated}/", exist_ok=True)
        CSV_OUTPUT = f"TOURS/{route_code}/{time_generated}/exported_{CSV_INPUT}"
        with open(CSV_OUTPUT, 'w', newline='', encoding='utf-8') as csvfile_out:
            writer = csv.DictWriter(csvfile_out, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        # copy the file to the main directory to keep track of the changes in git
        shutil.copyfile(CSV_OUTPUT,f"TOURS/{route_code}/DS_Tour_{route_code}_Legs.csv")   
    else:
        os.makedirs(f"{airport_icao}_{route_code}/{time_generated}/", exist_ok=True)
        CSV_OUTPUT = f"{airport_icao}_{route_code}/{time_generated}/exported_{CSV_INPUT}"
        with open(CSV_OUTPUT, 'w', newline='', encoding='utf-8') as csvfile_out:
            writer = csv.DictWriter(csvfile_out, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        shutil.copyfile(CSV_OUTPUT,f"{airport_icao}_{route_code}/{airport_icao}_{route_code}_Flights.csv")   


    print(f'Updated CSV saved as {CSV_OUTPUT}')

    # if file has more than 500 schedules separate in files of 500 flights per file
    if len(rows) > 500:
        print("Spliting schedules into multiple files for import")
        with open(CSV_OUTPUT,'r') as file:
            split(file,row_limit=500,output_path=f"{route_code}/{time_generated}")

def validate_file(file_path):
    # Validate if the file exists
    if os.path.isfile(file_path):
        print(f"\n✅ Found file: {file_path}\n")
        if has_duplicates(parse_airport_file(file_path)):
            raise ValueError(f"Duplicates found on {file_path}")
        print("📄 File Content:")
        print("-" * 50)
        with open(file_path, "r", encoding="utf-8") as file:
            print(file.read())
        print("-" * 50)

        # Ask user for confirmation (non-interactive friendly)
        if _auto_yes():
            print("CI/--yes detected → proceeding without prompt.")
            return

        try:
            user_input = input("\nDo you want to continue? (Y/N): ").strip().lower()
        except EOFError:
            # No TTY; default to 'yes' in CI, otherwise abort
            if _auto_yes():
                print("No TTY, CI mode → proceeding.")
                return
            print("❌ No TTY available and not in CI/--yes mode. Aborting.")
            sys.exit(1)

        if user_input not in ('y', 'yes'):
            print("❌ Execution aborted by user.")
            sys.exit(1)
    else:
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

def parse_tour_config(config_path):
    config = {}
    if not os.path.exists(config_path):
        return config

    with open(config_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        first_row = next(reader, {})

        flight_type = first_row.get('flight_type', 'J').strip().upper()
        if flight_type not in ['J', 'F']:
            print("❌ Invalid flight_type in config. Falling back to 'J'.")
            flight_type = 'J'

        config['flight_type'] = flight_type
        config['pilot_pay'] = first_row.get('pilot_pay', '').strip()
        config['notes'] = f"<p>{first_row.get('notes', '').strip()}</p>"
        config['start_flight_number'] = first_row.get('start_flight_number', '8000').strip()
        config['start_date'] = "" # f"{first_row.get('start_date').strip()} 00:00:00"
        config['end_date'] = "" # f"{first_row.get('end_date').strip()} 00:00:00"
        filter_subfleets = first_row.get('subfleets', '').strip().upper()
        if filter_subfleets != '':
            config['subfleets'] = filter_subfleets.split(';')
        else:
            config['subfleets'] = []
    return config

# Example usage (uncomment to run):
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate phpVMS flights.")
    parser.add_argument("airport_icao", help="Base Airport ICAO (e.g., MUHA)")
    parser.add_argument("route_code", help="Airport IATA (e.g., HAV)")
    parser.add_argument("--yes", "-y", action="store_true",help="Proceed without interactive confirmation")
    args = parser.parse_args()
    _assume_yes = args.yes  # makes --yes visible to _auto_yes()
    AIRPORT_ICAO=args.airport_icao
    route_code=args.route_code
    is_tour_mode = AIRPORT_ICAO.upper() == "TOUR"
    time_generated = time.strftime("%Y%m%d-%H%M%S")
    if is_tour_mode:
        print("Tour mode")
        os.makedirs(f"TOURS/{route_code}", exist_ok=True)
        file_path = f"TOURS/{route_code}/legs.txt"
        config_path = f"TOURS/{route_code}/config.csv"
        validate_file(file_path)
        pairs = parse_airport_file(file_path)
        generate_flights(pairs,route_code,8000,f"DS_Tour_{route_code}_Legs_{time_generated}.csv",True,parse_tour_config(config_path))
        update_subfleets(AIRPORT_ICAO,route_code,time_generated,f"DS_Tour_{route_code}_Legs_{time_generated}.csv",True,filter_subfleets=GLOB_FILTER_SUBFLEETS)
        # cleanup the file without subfleets
        os.remove(f"DS_Tour_{route_code}_Legs_{time_generated}.csv")
    else:
        print("Schedules mode")
        os.makedirs(f"{AIRPORT_ICAO}_{route_code}", exist_ok=True)
        file_path = f"{AIRPORT_ICAO}_{route_code}/airports.txt"
        validate_file(file_path)
        pairs = parse_airport_file(file_path)
        generate_flights(pairs, route_code, START_FLIGHT_NUMBER, f"{AIRPORT_ICAO}_{route_code}_{time_generated}_generated_phpvms_flights.csv")
        update_subfleets(AIRPORT_ICAO,route_code,time_generated,f"{AIRPORT_ICAO}_{route_code}_{time_generated}_generated_phpvms_flights.csv") #add the subfleets based on flight distance
        # cleanup the file without subfleets
        os.remove(f"{AIRPORT_ICAO}_{route_code}_{time_generated}_generated_phpvms_flights.csv")