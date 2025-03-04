import requests
import json
import os
from datetime import datetime

# Retrieve your SimBrief API key from environment variable
SIMBRIEF_API_KEY = os.getenv("SIMBRIEF_API_KEY")

# Check if the API key is set properly
if not SIMBRIEF_API_KEY:
    raise ValueError("SimBrief API key not found. Please set the SIMBRIEF_API_KEY environment variable.")

# List of ICAOs for freighter aircraft
freighter_icaos = {
    "B77F", "B744F", "MD11F", "A306F", "B752F", "B763F", "A332F",
    "B731F", "B732F", "B733F", "B734F", "B735F", "B738F", "DC10F",
    "B727F", "B721F", "B722F", "A321F", "A300F", "ATR72F", "ATR42F",
    "B737F", "A310F", "A320F", "B757F", "B767F", "B777F", "A330F", "A340F", "B787F"
}

# Long cabin layout dictionary with all the ICAOs
cabin_layouts = {
    "A318": {"F": 0, "J": 0, "Y": 132},
    "A319": {"F": 0, "J": 0, "Y": 140},
    "A320": {"F": 0, "J": 12, "Y": 138},
    "A321": {"F": 0, "J": 20, "Y": 178},
    "A330": {"F": 20, "J": 30, "Y": 200},
    "A340": {"F": 20, "J": 30, "Y": 230},
    "A350": {"F": 30, "J": 60, "Y": 250},
    "A380": {"F": 50, "J": 80, "Y": 400},
    "B737": {"F": 0, "J": 12, "Y": 112},
    "B747": {"F": 12, "J": 40, "Y": 200},
    "B757": {"F": 0, "J": 16, "Y": 150},
    "B767": {"F": 0, "J": 30, "Y": 180},
    "B777": {"F": 10, "J": 40, "Y": 280},
    "B787": {"F": 20, "J": 40, "Y": 220},
    "CRJ700": {"F": 0, "J": 0, "Y": 70},
    "CRJ900": {"F": 0, "J": 0, "Y": 90},
    "E170": {"F": 0, "J": 12, "Y": 60},
    "E175": {"F": 0, "J": 12, "Y": 70},
    "E190": {"F": 0, "J": 12, "Y": 100},
    "E195": {"F": 0, "J": 12, "Y": 120},
    "MD80": {"F": 0, "J": 12, "Y": 140},
    "MD11": {"F": 0, "J": 40, "Y": 250},
    "DC10": {"F": 0, "J": 40, "Y": 240},
    "F100": {"F": 0, "J": 0, "Y": 100},
    "F50": {"F": 0, "J": 0, "Y": 50},
    "B737MAX": {"F": 0, "J": 12, "Y": 150},
    "B787MAX": {"F": 20, "J": 40, "Y": 220},
    "B737MAX8": {"F": 0, "J": 12, "Y": 175},
    "AN24": {"F": 0, "J": 0, "Y": 40},
    "AN26": {"F": 0, "J": 0, "Y": 40},
    "B738M": {"F": 0, "J": 12, "Y": 140},
    "C25C": {"F": 0, "J": 0, "Y": 50},
    "E110": {"F": 0, "J": 0, "Y": 30},
    "IL18": {"F": 0, "J": 0, "Y": 80},
    "IL96": {"F": 20, "J": 40, "Y": 200},
    "KODI": {"F": 0, "J": 0, "Y": 19},
    "L410": {"F": 0, "J": 0, "Y": 19},
    "PC12": {"F": 0, "J": 0, "Y": 9},
    "TBM9": {"F": 0, "J": 0, "Y": 6},
    "YK40": {"F": 0, "J": 0, "Y": 50}
}

# Default passenger weight assumptions
PASSENGER_WEIGHT_LBS = 185
BAGGAGE_WEIGHT_LBS = 50

# Function to fetch SimBrief default aircraft data
def fetch_simbrief_aircraft_data():
    url = f"https://www.simbrief.com/api/xml.fetcher.php?apikey={SIMBRIEF_API_KEY}&json=1"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()["aircraft"]
    else:
        print("Error fetching SimBrief data.")
        return {}

# Function to calculate cargo capacity
def calculate_cargo_capacity(icao, pax_capacity, max_payload):
    if icao in freighter_icaos:
        return max_payload  # Freighters use full payload as cargo
    else:
        pax_weight = pax_capacity * PASSENGER_WEIGHT_LBS
        baggage_weight = pax_capacity * BAGGAGE_WEIGHT_LBS
        return max(0, max_payload - (pax_weight + baggage_weight))  # Remaining capacity

# Function to adjust seat distribution
def adjust_seat_distribution(layout, default_pax):
    total_seats = layout["F"] + layout["J"] + layout["Y"]

    if total_seats < default_pax:  # Add missing seats to Economy
        layout["Y"] += default_pax - total_seats
    elif total_seats > default_pax:  # Reduce seats from Economy
        layout["Y"] -= total_seats - default_pax
    
    return layout

# Generate filename with current date and time
def generate_filename(base_name):
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{current_time}.json"

# Main function to process aircraft data
def process_aircraft_data():
    aircraft_data = fetch_simbrief_aircraft_data()
    final_data = {}
    unknown_icaos = []

    for aircraft in aircraft_data:
        icao = aircraft["icao"]
        pax_capacity = int(aircraft["default_pax"])
        max_payload = int(aircraft["max_payload_lbs"])

        if icao in cabin_layouts:
            # Assign seating layout and adjust to match SimBrief pax count
            layout = cabin_layouts[icao]
            adjusted_layout = adjust_seat_distribution(layout, pax_capacity)
        elif icao in freighter_icaos:
            # Freighters get only cargo
            adjusted_layout = {"F": 0, "J": 0, "Y": 0}
        else:
            # Unknown aircraft - collect for review
            unknown_icaos.append({
                "icao": icao,
                "default_pax": pax_capacity,
                "max_payload_lbs": max_payload
            })
            continue  # Skip unknown aircraft from being processed

        # Calculate cargo capacity
        cargo_capacity = calculate_cargo_capacity(icao, pax_capacity, max_payload)

        # Store structured data
        final_data[icao] = {
            "F": adjusted_layout["F"],
            "J": adjusted_layout["J"],
            "Y": adjusted_layout["Y"],
            "CGO": cargo_capacity  # Add cargo capacity to the data
        }

    # Output final data with date and time in the filename
    output_filename = generate_filename("aircraft_data")
    with open(output_filename, 'w') as outfile:
        json.dump(final_data, outfile, indent=4)

    # Output unknown ICAOs with date and time in the filename
    if unknown_icaos:
        unknown_filename = generate_filename("unknown_aircrafts")
        with open(unknown_filename, 'w') as unknown_file:
            json.dump(unknown_icaos, unknown_file, indent=4)

        print(f"Unknown ICAOs found and saved to: {unknown_filename}")
    else:
        print("No unknown ICAOs found.")

if __name__ == "__main__":
    process_aircraft_data()
