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
from geopy.distance import geodesic

# Constants
GLOB_FILTER_SUBFLEETS=[]
CACHE_FILE = "distance_cache.json"
AIRPORTS_JSON_FILE = "airports.json"  # Local backup database (28,000+ airports)
CUSTOM_AIRPORTS_CSV = "custom_airports.csv"  # Custom managed airports
MISSING_AIRPORTS_FILE = "missing_airports.json"
START_FLIGHT_NUMBER = 1000
API_URL = "https://airportgap.com/api/airports/distance"
AIRPORTDB_IO_API_URL = "https://airportdb.io/api/v1/airport"
VACENTRAL_API_URL = "https://api.vacentral.net/api/airports"
PHPVMSV7_ENDPOINT = os.getenv("PHPVMSV7_ENDPOINT")
PHPVMSV7_API_KEY = os.getenv("PHPVMSV7_API_KEY")
TOKEN = os.getenv("AIRPORT_GAP_TOKEN")
AIRPORTDB_TOKEN = os.getenv("AIRPORT_DB_TOKEN")
HEADERS = {"Authorization": f"Bearer token={TOKEN}"}
TIME_FMT = '%H:%M'
MAX_REQUESTS_PER_MIN = 100

special_code_to_airline = {
    "CRC" : "CRN"
}

v5_flight_type_to_v7 = {
    "P" : "J",
    "C" : "F"
}

airline_subfleet_by_flight_type = {
    "CRN" : {
        "J" : ["BBJ2","H60","C402","DHC6","EC35","EC45","B734","B733","SH36","SH33","TRIS","BN2P","GA8","MI8","AN2","C172","B789","B78X","B762","BCS1","BCS3","A306","SU95","C208","B736","A20N","A21N","A310","A319","A320","A321","A332","A333","A346","A359","A388","AN24","AN26","AT45","AT46","AT75","AT76","B38M","B712","B732","B735","B737","B738","B739","B744","B752","B753","B763","B764","B77L","B77W","B788","C25C","DH8D","E110","E140","E145","E175","E190","E195","IL18","IL96","KODI","L410","PC12","TBM9","YK40"],
        "F" : ["A333F","B738F","AN26F","SH36F","SH33F","A124","AT76F","E190F","A225","A30F","B48F","B74F","B75F","B76F","B77F","MD1F","IL18F"],
    }
}

aircrafts_range_by_icao = {'IL18F':'2200','BBJ2':'3400','A333F':'6350','B738F':'3400','AN26F':'1100','H60':'700','C402':'920','DHC6':'771','EC35':'342','EC45':'351','SH36F':'800','SH33F':'600','B734':'2060','B733':'2255','SH36':'800','SH33':'600','TRIS':'620','BN2P':'620','GA8':'730','MI8':'335','AN2':'450','A124':'3200','AT76F':'1000','E190F':'2300','C172':'600','B789':'7600','B78X':'6300','B762':'3900','BCS1':'3400','BCS3':'3300','A306':'4000','SU95':'2700','C208':'1000','B736':'3600','A225': '3900','A20N': '3500', 'A21N': '4000', 'A30F': '4200', 'A310': '5150', 'A319': '3700', 'A320': '3300', 'A321': '2300', 'A332': '7250', 'A333': '6350', 'A346': '7900', 'A359': '8100', 'A388': '8000', 'AN24': '1000', 'AN26': '1100', 'AT45': '850', 'AT46': '800', 'AT75': '825', 'AT76': '950', 'B38M': '3550', 'B48F': '4200', 'B712': '2060', 'B732': '2300', 'B735': '1600', 'B737': '3350', 'B738': '3400', 'B739': '3200', 'B744': '7260', 'B74F': '4970', 'B752': '3900', 'B753': '3800', 'B75F': '3600', 'B763': '6000', 'B764': '6000', 'B76F': '3255', 'B77F': '8555', 'B77L': '8555', 'B77W': '7370', 'B788': '7355', 'C25C': '2165', 'DH8D': '1100', 'E110': '1200', 'E140': '1600', 'E145': '1550', 'E175': '2000', 'E190': '2400', 'E195': '2200', 'IL18': '2200', 'IL96': '6000', 'KODI': '1132', 'L410': '800', 'MD1F': '3800', 'PC12': '1845', 'TBM9': '1730', 'YK40': '1000'}

def _auto_yes():
    return getattr(sys.modules[__name__], "_assume_yes", False) or os.environ.get("CI") == "true"

def calculate_flight_times(distance_nm, avg_speed_knots=250):
    dpt_hour = random.randint(5, 22)
    dpt_minute = random.choice([0, 15, 30, 45])
    dpt_time = datetime.strptime(f"{dpt_hour:02}:{dpt_minute:02}", TIME_FMT)
    flight_time_min = (distance_nm / avg_speed_knots) * 60
    arr_time = dpt_time + timedelta(minutes=flight_time_min)
    return (dpt_time.strftime(TIME_FMT), arr_time.strftime(TIME_FMT), str(int(flight_time_min)))

def _load_cache(path=CACHE_FILE):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save_cache(cache: dict, path=CACHE_FILE):
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2, sort_keys=True)
    os.replace(tmp, path)

def _key_for_route(from_code: str, to_code: str) -> str:
    a, b = from_code.strip().upper(), to_code.strip().upper()
    return f"{min(a,b)}-{max(a,b)}"

def load_missing_airports(path=MISSING_AIRPORTS_FILE):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_missing_airports(missing_airports: dict, path=MISSING_AIRPORTS_FILE):
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(missing_airports, f, ensure_ascii=False, indent=2, sort_keys=True)
    os.replace(tmp, path)

def log_missing_airport(icao_code, found_in=None, coordinates=None):
    missing_airports = load_missing_airports()
    icao_upper = icao_code.strip().upper()
    
    if icao_upper not in missing_airports:
        entry = {
            "icao": icao_upper,
            "first_seen": datetime.now().isoformat(),
            "found_in": found_in,
            "status": "found" if found_in else "not_found"
        }
        
        if coordinates:
            entry["latitude"] = coordinates[0]
            entry["longitude"] = coordinates[1]
        
        missing_airports[icao_upper] = entry
        save_missing_airports(missing_airports)
        
        if found_in:
            print(f"📝 Logged {icao_upper} as missing from VAcentral (found in {found_in})")
        else:
            print(f"📝 Logged {icao_upper} as missing from VAcentral (NOT FOUND ANYWHERE)")

def load_custom_airports_csv(path=CUSTOM_AIRPORTS_CSV):
    if not os.path.exists(path):
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'icao', 'iata', 'name', 'location', 'country', 'timezone', 
                'hub', 'lat', 'lon', 'ground_handling_cost', 
                'fuel_100ll_cost', 'fuel_jeta_cost', 'fuel_mogas_cost', 'notes'
            ])
        return {}
    
    airports = {}
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            icao = row['icao'].strip().upper()
            airports[icao] = {
                'icao': icao,
                'iata': row.get('iata', '').strip().upper(),
                'name': row.get('name', '').strip(),
                'location': row.get('location', '').strip(),
                'country': row.get('country', '').strip(),
                'timezone': row.get('timezone', '').strip(),
                'hub': row.get('hub', '').strip(),
                'lat': float(row['lat']) if row.get('lat') else None,
                'lon': float(row['lon']) if row.get('lon') else None,
                'ground_handling_cost': row.get('ground_handling_cost', '').strip(),
                'fuel_100ll_cost': row.get('fuel_100ll_cost', '').strip(),
                'fuel_jeta_cost': row.get('fuel_jeta_cost', '').strip(),
                'fuel_mogas_cost': row.get('fuel_mogas_cost', '').strip(),
                'notes': row.get('notes', '').strip()
            }
    
    print(f"✅ Loaded {len(airports)} custom airports from CSV")
    return airports

def get_airport_from_custom_csv(icao_code, custom_airports=None):
    if custom_airports is None:
        custom_airports = load_custom_airports_csv()
    
    icao_upper = icao_code.strip().upper()
    
    if icao_upper in custom_airports:
        airport = custom_airports[icao_upper]
        lat = airport.get('lat')
        lon = airport.get('lon')
        
        if lat is not None and lon is not None:
            print(f"📍 Found {icao_code} in custom airports CSV")
            return (float(lat), float(lon))
    
    return None

def verify_airport_in_phpvms(icao_code, verbose=True):
    """
    Verify if an airport exists in phpVMS v7 system via API.
    
    Args:
        icao_code: Airport ICAO code
        verbose: Print debug information
    
    Returns:
        Airport data if found, None otherwise
    """
    if not PHPVMSV7_ENDPOINT or not PHPVMSV7_API_KEY:
        if verbose:
            print(f"⚠️ phpVMS v7 credentials not configured")
            print(f"   PHPVMSV7_ENDPOINT: {PHPVMSV7_ENDPOINT or 'NOT SET'}")
            print(f"   PHPVMSV7_API_KEY: {'SET (' + PHPVMSV7_API_KEY[:10] + '...)' if PHPVMSV7_API_KEY else 'NOT SET'}")
        return None
    
    icao_upper = icao_code.strip().upper()
    base_url = PHPVMSV7_ENDPOINT.rstrip('/')
    url = f"{base_url}/api/airports/{icao_upper}"
    headers = {"X-API-Key": PHPVMSV7_API_KEY}
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"phpVMS v7 API Check for {icao_upper}")
        print(f"{'='*60}")
        print(f"URL: {url}")
        print(f"Headers: X-API-Key: {PHPVMSV7_API_KEY[:10]}...{PHPVMSV7_API_KEY[-4:]}")
        print(f"{'='*60}")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if verbose:
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if verbose:
                    print(f"Response Body:")
                    print(json.dumps(data, indent=2))
                
                if 'data' in data:
                    print(f"✅ Verified {icao_code} exists in phpVMS v7")
                    if verbose:
                        print(f"{'='*60}\n")
                    return data['data']
                else:
                    print(f"⚠️ Response missing 'data' field")
                    if verbose:
                        print(f"Available keys: {list(data.keys())}")
                        print(f"{'='*60}\n")
                    return None
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON response: {e}")
                print(f"Raw response: {response.text[:500]}")
                if verbose:
                    print(f"{'='*60}\n")
                return None
                
        elif response.status_code == 404:
            if verbose:
                print(f"Response Body: {response.text}")
            print(f"❌ Airport {icao_code} NOT found in phpVMS v7")
            if verbose:
                print(f"{'='*60}\n")
            return None
        else:
            if verbose:
                print(f"Response Body: {response.text[:500]}")
            print(f"⚠️ phpVMS v7 API error ({response.status_code})")
            if verbose:
                print(f"{'='*60}\n")
            return None
            
    except requests.exceptions.Timeout:
        print(f"⏱️ Timeout connecting to phpVMS v7 ({url})")
        if verbose:
            print(f"{'='*60}\n")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to phpVMS v7: {e}")
        if verbose:
            print(f"{'='*60}\n")
        return None

def generate_csv_line_for_missing_airport(icao_code, coords=None, source=None):
    lat = coords[0] if coords else ''
    lon = coords[1] if coords else ''
    notes = f'Found in {source}' if source else 'Needs manual verification'
    
    return f"{icao_code.upper()},,,,,,{lat},{lon},,,,,{notes}"

def load_local_airports_db(json_file=AIRPORTS_JSON_FILE):
    if not os.path.exists(json_file):
        print(f"📥 airports.json not found. Attempting to download from GitHub...")
        download_url = "https://raw.githubusercontent.com/mwgg/Airports/master/airports.json"
        
        try:
            response = requests.get(download_url, timeout=30)
            response.raise_for_status()
            
            with open(json_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(f"✅ Successfully downloaded airports.json ({len(response.text) / 1024 / 1024:.2f} MB)")
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Could not download airports.json: {e}")
            print(f"   Continuing without local airport database...")
            return None
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            airports = json.load(f)
            print(f"✅ Loaded {len(airports)} airports from local database: {json_file}")
            return airports
    except Exception as e:
        print(f"⚠️ Error loading local airports database: {e}")
        return None

def get_airport_from_local_db(icao_code, airports_db):
    if airports_db is None:
        return None
    
    icao_upper = icao_code.strip().upper()
    
    if icao_upper in airports_db:
        airport = airports_db[icao_upper]
        lat = airport.get('lat')
        lon = airport.get('lon')
        
        if lat is not None and lon is not None:
            return (float(lat), float(lon))
    
    return None

def get_airport_from_airportdb_io(icao_code):
    if not AIRPORTDB_TOKEN:
        return None
    
    icao_upper = icao_code.strip().upper()
    url = f"{AIRPORTDB_IO_API_URL}/{icao_upper}?apiToken={AIRPORTDB_TOKEN}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            lat = data.get('latitude_deg')
            lon = data.get('longitude_deg')
            
            if lat is not None and lon is not None:
                print(f"📍 Found {icao_code} via AirportDB.io API")
                return (float(lat), float(lon))
            else:
                print(f"⚠️ Airport {icao_code} found in AirportDB.io but missing coordinates")
                return None
        elif response.status_code == 404:
            print(f"⚠️ Airport {icao_code} not found in AirportDB.io")
            return None
        elif response.status_code == 401:
            print(f"⚠️ AirportDB.io API authentication failed (check AIRPORT_DB_TOKEN)")
            return None
        else:
            print(f"⚠️ AirportDB.io API error ({response.status_code})")
            return None
            
    except ValueError as e:
        print(f"❌ Error parsing AirportDB.io response for {icao_code}: {e}")
        return None
    except requests.exceptions.Timeout:
        print(f"⏱️ Timeout fetching from AirportDB.io for {icao_code}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error with AirportDB.io for {icao_code}: {e}")
        return None

def get_airport_from_vacentral(icao_code):
    icao_upper = icao_code.strip().upper()
    url = f"{VACENTRAL_API_URL}/{icao_upper}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            lat = data.get('lat')
            lon = data.get('lon')
            
            if lat is not None and lon is not None:
                print(f"📍 Found {icao_code} via VAcentral API")
                return (float(lat), float(lon))
            else:
                print(f"⚠️ Airport {icao_code} found in VAcentral but missing coordinates")
                return None
        elif response.status_code == 404:
            print(f"⚠️ Airport {icao_code} not found in VAcentral API")
            return None
        else:
            print(f"⚠️ VAcentral API error ({response.status_code})")
            return None
            
    except ValueError as e:
        print(f"❌ Error parsing VAcentral response for {icao_code}: {e}")
        return None
    except requests.exceptions.Timeout:
        print(f"⏱️ Timeout fetching from VAcentral for {icao_code}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error with VAcentral for {icao_code}: {e}")
        return None

def get_airport_coordinates(icao_code, airports_db=None, custom_airports=None):
    """
    Retrieve airport coordinates using ICAO code.
    Priority order:
    1. VAcentral API (PRIMARY SOURCE - phpVMS community database)
    2. phpVMS v7 (OUR SYSTEM - checked IMMEDIATELY after VAcentral)
    3. Custom CSV (our managed airports for import)
    4. External sources (local DB, AirportDB.io) - only for finding NEW airports
    
    CRITICAL RULES:
    - If found in VAcentral → Use it (already in community DB)
    - If NOT in VAcentral BUT in phpVMS v7 → Use it (already in our system)
    - If NOT in VAcentral AND NOT in phpVMS v7 → Search externally
    - If found externally → MUST add to phpVMS v7 before continuing
    """
    icao_upper = icao_code.strip().upper()
    
    # TIER 1: Check VAcentral API (PRIMARY SOURCE)
    print(f"🔍 Checking VAcentral API for {icao_upper}...")
    coords = get_airport_from_vacentral(icao_code)
    if coords is not None:
        print(f"✅ {icao_upper} found in VAcentral - using community data")
        return coords
    
    # NOT in VAcentral - now check OUR phpVMS v7 system IMMEDIATELY
    print(f"⚠️ {icao_upper} not found in VAcentral API")
    print(f"🔍 Checking phpVMS v7 for {icao_upper}...")
    
    phpvms_data = verify_airport_in_phpvms(icao_code, verbose=True)
    
    if phpvms_data:
        # Airport IS in our phpVMS v7 system but NOT in VAcentral
        print(f"✅ {icao_upper} found in phpVMS v7 (not in VAcentral yet)")
        
        # Try to get coordinates from custom CSV first
        coords = get_airport_from_custom_csv(icao_code, custom_airports)
        if coords is not None:
            return coords
        
        # Extract coordinates from phpVMS v7 response
        lat = phpvms_data.get('lat')
        lon = phpvms_data.get('lon')
        
        if lat is not None and lon is not None:
            print(f"📍 Using coordinates from phpVMS v7: {lat}, {lon}")
            return (float(lat), float(lon))
        else:
            print(f"⚠️ {icao_upper} in phpVMS v7 but missing coordinates!")
            # Fall through to external search
    
    # NOT in VAcentral AND NOT in phpVMS v7 - search external sources
    print(f"⚠️ {icao_upper} not found in phpVMS v7, checking external sources...")
    
    found_source = None
    final_coords = None
    
    # Check custom CSV (for airports waiting to be imported)
    coords = get_airport_from_custom_csv(icao_code, custom_airports)
    if coords is not None:
        found_source = "custom_csv"
        final_coords = coords
    
    # Check local database (28,000+ airports)
    if final_coords is None and airports_db is not None:
        coords = get_airport_from_local_db(icao_code, airports_db)
        if coords is not None:
            print(f"📍 Found {icao_code} in local database")
            found_source = "local_db"
            final_coords = coords
    
    # Check AirportDB.io API
    if final_coords is None and AIRPORTDB_TOKEN:
        coords = get_airport_from_airportdb_io(icao_code)
        if coords is not None:
            found_source = "airportdb_io"
            final_coords = coords
    
    # Log as missing from VAcentral
    log_missing_airport(icao_code, found_source, final_coords)
    
    if final_coords:
        # Found in external source - MUST add to phpVMS v7
        csv_line = generate_csv_line_for_missing_airport(icao_code, final_coords, found_source)
        print(f"\n{'='*80}")
        print(f"❌ CRITICAL: {icao_upper} found in {found_source} but NOT in phpVMS v7!")
        print(f"{'='*80}")
        print(f"\n📋 Add this line to custom_airports.csv:")
        print(f"   {csv_line}")
        print(f"\n📝 Then:")
        print(f"   1. Import custom_airports.csv into phpVMS v7")
        print(f"   2. Verify the airport appears in phpVMS v7")
        print(f"   3. Re-run this script")
        print(f"\n{'='*80}\n")
        raise Exception(f"Airport {icao_upper} must be added to phpVMS v7 before continuing")
    
    # NOT found anywhere
    print(f"❌ Could not find airport {icao_code} in any database")
    csv_line = generate_csv_line_for_missing_airport(icao_code, None, None)
    print(f"\n{'='*80}")
    print(f"❌ CRITICAL: {icao_upper} NOT FOUND in any database!")
    print(f"{'='*80}")
    print(f"\n📋 Add this line to custom_airports.csv (ADD COORDINATES MANUALLY):")
    print(f"   {csv_line}")
    print(f"\n📝 Then:")
    print(f"   1. Research and add correct coordinates for {icao_upper}")
    print(f"   2. Import custom_airports.csv into phpVMS v7")
    print(f"   3. Verify the airport appears in phpVMS v7")
    print(f"   4. Re-run this script")
    print(f"\n💡 Tip: Search for '{icao_upper}' on:")
    print(f"   - https://www.airnav.com/airport/{icao_upper}")
    print(f"   - https://skyvector.com/airport/{icao_upper}")
    print(f"   - https://ourairports.com/airports/{icao_upper}/")
    print(f"\n{'='*80}\n")
    raise Exception(f"Airport {icao_upper} not found - add to custom_airports.csv and phpVMS v7")

def calculate_distance_by_icao(icao1, icao2, cache_path: str = CACHE_FILE, airports_db=None, custom_airports=None):
    cache = _load_cache(cache_path)
    key = _key_for_route(icao1, icao2)

    if key in cache:
        return int(cache[key])
    
    print(f"🌍 Calculating distance using ICAO codes: {icao1} → {icao2}")
    
    coords1 = get_airport_coordinates(icao1, airports_db, custom_airports)
    coords2 = get_airport_coordinates(icao2, airports_db, custom_airports)
    
    if coords1 is None or coords2 is None:
        print(f"❌ Could not retrieve coordinates for {icao1} or {icao2}")
        return None
    
    distance = geodesic(coords1, coords2)
    nm = int(distance.nautical)
    
    cache[key] = nm
    _save_cache(cache, cache_path)
    
    print(f"✅ Distance calculated: {nm} nautical miles")
    return nm

def fetch_distance(from_iata, to_iata, from_icao=None, to_icao=None, cache_path: str = CACHE_FILE, airports_db=None, custom_airports=None):
    cache = _load_cache(cache_path)
    
    if from_iata and to_iata and from_iata.strip() and to_iata.strip():
        key = _key_for_route(from_iata, to_iata)

        if key in cache:
            return int(cache[key])
        
        payload = {"from": from_iata, "to": to_iata}
        print(f"📡 API call for IATA distance: {from_iata} → {to_iata}")
        backoff = 30
        max_wait = 5 * 60

        waited = 0
        while True:
            response = requests.post(API_URL, data=payload, headers=HEADERS)
            if response.status_code == 200:
                data = response.json()
                nm = int(data["data"]["attributes"]["nautical_miles"])
                cache[key] = nm
                _save_cache(cache, cache_path)
                print(f"✅ IATA distance retrieved: {nm} nautical miles")
                return nm

            if response.status_code == 429:
                sleep_s = min(backoff, max_wait - waited) if max_wait else backoff
                if sleep_s <= 0:
                    print("⚠️ Rate limit persisted, falling back to ICAO calculation")
                    break
                print(f"⏳ Rate limit hit. Waiting {sleep_s} seconds...")
                time.sleep(sleep_s)
                waited += sleep_s
                backoff = min(backoff * 2, 120)
                continue

            print(f"⚠️ IATA API failed ({response.status_code}), trying ICAO fallback")
            break
    else:
        print(f"⚠️ Missing IATA codes (from: '{from_iata}', to: '{to_iata}'), using ICAO fallback")
    
    if from_icao and to_icao and from_icao.strip() and to_icao.strip():
        distance = calculate_distance_by_icao(from_icao, to_icao, cache_path, airports_db, custom_airports)
        if distance is not None:
            return distance
    
    error_msg = f"Failed to fetch distance between airports:\n"
    error_msg += f"  Origin: {from_icao} (IATA: {from_iata or 'N/A'})\n"
    error_msg += f"  Destination: {to_icao} (IATA: {to_iata or 'N/A'})\n"
    raise Exception(error_msg)

def parse_airport_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.read().strip().splitlines()
    pairs = []
    for line in lines:
        if '#' in line:
            line = line.split('#')[0].strip()
        parts = line.split(',')
        a1_icao, a1_iata = parts[0].split('-')
        a2_icao, a2_iata = parts[1].split('-')
        pairs.append(((a1_icao, a1_iata), (a2_icao, a2_iata)))
    return pairs

def has_duplicates(pairs):
    set_pairs = set(pairs)
    if len(pairs) != len(set_pairs):
        print("Duplicate entries found aborting flight generation.\nRemove duplicated lines")
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
    
    airports_db = load_local_airports_db()
    custom_airports = load_custom_airports_csv()

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
        
        try:
            avg_speed = int(tour_config.get("avg_speed_knots", "250"))
            if avg_speed <= 0:
                print("⚠️ Invalid avg_speed_knots in config (must be > 0). Using default 250 knots.")
                avg_speed = 250
            else:
                print(f"✈️ Using custom average speed: {avg_speed} knots")
        except ValueError:
            print("⚠️ Invalid avg_speed_knots in config. Using default 250 knots.")
            avg_speed = 250
        
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
            distance = fetch_distance(a1_iata, a2_iata, a1_icao, a2_icao, airports_db=airports_db, custom_airports=custom_airports)
            requests_made += 1

            dpt, arr, flt = calculate_flight_times(distance, avg_speed)

            call_sign = ""

            if(flight_type == 'F'):
                call_sign = "CRF"

            records.append([
                "CRN", current_number, route_code.upper(), call_sign, leg_number, a1_icao, a2_icao, "", "1234567",
                dpt, arr, "", distance, flt, flight_type, "", "", pilot_pay,
                "", notes, start_date, end_date, "0", "", "", "", "", ""
            ])
            current_number += 1
    else:
        print("Generating Scheduled Flights")
        for (a1_icao, a1_iata), (a2_icao, a2_iata) in pairs:
            if requests_made >= MAX_REQUESTS_PER_MIN:
                print("Reached 100 API requests, sleeping for 60 seconds...")
                time.sleep(60)
                requests_made = 0
            distance = fetch_distance(a1_iata, a2_iata, a1_icao, a2_icao, airports_db=airports_db, custom_airports=custom_airports)
            requests_made += 1

            pax_callsign = ""

            dpt, arr, flt = calculate_flight_times(distance)
            records.append([
                "CRN", current_number, route_code, pax_callsign, "", a1_icao, a2_icao, "", "1234567",
                dpt, arr, "", distance, flt, "J", "", "", "", "", "", "", "", "1", "", "", "", "", ""
            ])
            current_number += 1

            dpt, arr, flt = calculate_flight_times(distance)
            records.append([
                "CRN", current_number, route_code, pax_callsign, "", a2_icao, a1_icao, "", "1234567",
                dpt, arr, "", distance, flt, "J", "", "", "", "", "", "", "", "1", "", "", "", "", ""
            ])
            current_number += 1

            cargo_callsign = "CRF"

            dpt, arr, flt = calculate_flight_times(distance)
            records.append([
                "CRN", current_number, route_code, cargo_callsign, "", a1_icao, a2_icao, "", "1234567",
                dpt, arr, "", distance, flt, "F", "", "", "", "", "", "", "", "1", "", "", "", "", ""
            ])
            current_number += 1

            dpt, arr, flt = calculate_flight_times(distance)
            records.append([
                "CRN", current_number, route_code, cargo_callsign, "", a2_icao, a1_icao, "", "1234567",
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
    with open(CSV_INPUT, 'r', newline='', encoding='utf-8') as csvfile_in:
        reader = csv.DictReader(csvfile_in)
        rows = list(reader)
        fieldnames = reader.fieldnames

    indexes_to_remove = []
    for idx,row in enumerate(rows):
        flight_number = int(remove_non_numeric(str(row['flight_number'])))
        if flight_number < 100:
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
                        subfleets.append(aircraft_icao)
                else:
                    subfleets.append(aircraft_icao)
                
        row['subfleets'] = ';'.join(subfleets)

    print("Checking flights that need to be removed")
    if len(indexes_to_remove) > 0:
        print(f"Total number of schedules is {len(rows)}")
        for idx,i in enumerate(indexes_to_remove):
            del rows[i-idx]
        print(f"Completed removing {len(indexes_to_remove)} flights that don't meet flight number requirement of 3 or more digits")
        print(f"The new total number of schedules is {len(rows)}")
    else:
        print("No flights found that need to be removed")

    timestr = time.strftime("%Y%m%d-%H%M%S")
    if is_tour_mode:
        os.makedirs(f"TOURS/{route_code}/{time_generated}/", exist_ok=True)
        CSV_OUTPUT = f"TOURS/{route_code}/{time_generated}/exported_{CSV_INPUT}"
        with open(CSV_OUTPUT, 'w', newline='', encoding='utf-8') as csvfile_out:
            writer = csv.DictWriter(csvfile_out, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
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

    if len(rows) > 500:
        print("Spliting schedules into multiple files for import")
        with open(CSV_OUTPUT,'r') as file:
            split(file,row_limit=500,output_path=f"{route_code}/{time_generated}")

def validate_file(file_path):
    if os.path.isfile(file_path):
        print(f"\n✅ Found file: {file_path}\n")
        if has_duplicates(parse_airport_file(file_path)):
            raise ValueError(f"Duplicates found on {file_path}")
        print("📄 File Content:")
        print("-" * 50)
        with open(file_path, "r", encoding="utf-8") as file:
            print(file.read())
        print("-" * 50)

        if _auto_yes():
            print("CI/--yes detected → proceeding without prompt.")
            return

        try:
            user_input = input("\nDo you want to continue? (Y/N): ").strip().lower()
        except EOFError:
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
        config['start_date'] = ""
        config['end_date'] = ""
        config['avg_speed_knots'] = first_row.get('avg_speed_knots', '250').strip()
        filter_subfleets = first_row.get('subfleets', '').strip().upper()
        if filter_subfleets != '':
            config['subfleets'] = filter_subfleets.split(';')
        else:
            config['subfleets'] = []
    return config

def cleanup_airports_db(json_file=AIRPORTS_JSON_FILE):
    if os.path.exists(json_file):
        try:
            os.remove(json_file)
            print(f"🧹 Cleaned up {json_file} (will download fresh copy next run)")
        except Exception as e:
            print(f"⚠️ Could not remove {json_file}: {e}")

def print_missing_airports_summary():
    missing_airports = load_missing_airports()
    
    if not missing_airports:
        print("\n✅ All airports were found in VAcentral API!")
        return
    
    print("\n" + "="*80)
    print("📋 AIRPORTS MISSING FROM VACENTRAL API - ACTION REQUIRED")
    print("="*80)
    
    found_elsewhere = [a for a in missing_airports.values() if a['status'] == 'found']
    not_found_anywhere = [a for a in missing_airports.values() if a['status'] == 'not_found']
    
    if found_elsewhere:
        print(f"\n🟡 Found in other sources ({len(found_elsewhere)} airports):")
        print("-"*80)
        print("\nAdd these lines to custom_airports.csv:\n")
        for airport in sorted(found_elsewhere, key=lambda x: x['icao']):
            coords = (airport.get('latitude'), airport.get('longitude'))
            csv_line = generate_csv_line_for_missing_airport(
                airport['icao'], 
                coords, 
                airport.get('found_in')
            )
            print(csv_line)
    
    if not_found_anywhere:
        print(f"\n🔴 NOT FOUND ANYWHERE ({len(not_found_anywhere)} airports):")
        print("-"*80)
        print("\n⚠️ REQUIRES MANUAL COORDINATES - Add these lines to custom_airports.csv:\n")
        for airport in sorted(not_found_anywhere, key=lambda x: x['icao']):
            csv_line = generate_csv_line_for_missing_airport(airport['icao'], None, None)
            print(csv_line)
    
    print("\n" + "="*80)
    print("📝 NEXT STEPS:")
    print("1. Add the lines above to custom_airports.csv")
    print("2. Fill in missing coordinates for airports not found anywhere")
    print("3. Import the CSV into phpVMS v7")
    print("4. Run the script again to verify")
    print("="*80 + "\n")

if __name__ == "__main__":
    # Print environment check at startup
    print("\n" + "="*80)
    print("ENVIRONMENT CHECK")
    print("="*80)
    print(f"PHPVMSV7_ENDPOINT: {PHPVMSV7_ENDPOINT or 'NOT SET'}")
    print(f"PHPVMSV7_API_KEY: {PHPVMSV7_API_KEY[:10] + '...' + PHPVMSV7_API_KEY[-4:] if PHPVMSV7_API_KEY else 'NOT SET'}")
    print("="*80 + "\n")
    
    parser = argparse.ArgumentParser(description="Generate phpVMS flights.")
    parser.add_argument("airport_icao", help="Base Airport ICAO (e.g., MUHA)")
    parser.add_argument("route_code", help="Airport IATA (e.g., HAV)")
    parser.add_argument("--yes", "-y", action="store_true",help="Proceed without interactive confirmation")
    args = parser.parse_args()
    _assume_yes = args.yes
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
        os.remove(f"DS_Tour_{route_code}_Legs_{time_generated}.csv")
        cleanup_airports_db()
    else:
        print("Schedules mode")
        os.makedirs(f"{AIRPORT_ICAO}_{route_code}", exist_ok=True)
        file_path = f"{AIRPORT_ICAO}_{route_code}/airports.txt"
        validate_file(file_path)
        pairs = parse_airport_file(file_path)
        generate_flights(pairs, route_code, START_FLIGHT_NUMBER, f"{AIRPORT_ICAO}_{route_code}_{time_generated}_generated_phpvms_flights.csv")
        update_subfleets(AIRPORT_ICAO,route_code,time_generated,f"{AIRPORT_ICAO}_{route_code}_{time_generated}_generated_phpvms_flights.csv")
        os.remove(f"{AIRPORT_ICAO}_{route_code}_{time_generated}_generated_phpvms_flights.csv")
        cleanup_airports_db()
    
    print_missing_airports_summary()