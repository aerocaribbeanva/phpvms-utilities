import requests
import json
import copy
from datetime import datetime

# Constants
SIMBRIEF_URL = "https://www.simbrief.com/api/inputs.airframes.json"
PASSENGER_WEIGHT_LBS = 175  # Standard simbrief passenger weight in pounds

# Predefined cabin layouts per aircraft ICAO
CABIN_LAYOUTS = {
    "A225": {"F": 0, "J": 0, "Y": 0},
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
    "AN2": {"F": 0, "J": 0, "Y": 12},
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
    "YK40": {"F": 0, "J": 0, "Y": 50},
    "A306": {"F": 12, "J": 30, "Y": 232},
    "A30B": {"F": 12, "J": 30, "Y": 227},
    "A310": {"F": 12, "J": 30, "Y": 198},
    "A20N": {"F": 0, "J": 20, "Y": 166},
    "A21N": {"F": 8, "J": 24, "Y": 188},
    "B461": {"F": 8, "J": 24, "Y": 158},
    "B462": {"F": 8, "J": 24, "Y": 148},
    "B463": {"F": 8, "J": 24, "Y": 178},
    "BA11": {"F": 8, "J": 24, "Y": 118},
    "BAC1": {"F": 0, "J": 12, "Y": 108},
    "B703": {"F": 8, "J": 24, "Y": 188},
    "B721": {"F": 0, "J": 12, "Y": 130},
    "B722": {"F": 0, "J": 12, "Y": 140},
    "B732": {"F": 0, "J": 8, "Y": 102},
    "B733": {"F": 0, "J": 8, "Y": 122},
    "B734": {"F": 0, "J": 8, "Y": 132},
    "B735": {"F": 0, "J": 8, "Y": 118},
    "B736": {"F": 0, "J": 8, "Y": 102},
    "B737CL": {"F": 0, "J": 8, "Y": 128},
    "B739": {"F": 0, "J": 16, "Y": 164},
    "CL30": {"F": 0, "J": 0, "Y": 19},
    "D328": {"F": 0, "J": 0, "Y": 33},
    "DC85": {"F": 8, "J": 24, "Y": 148},
    "DC93": {"F": 8, "J": 24, "Y": 158},
    "E120": {"F": 0, "J": 0, "Y": 30},
    "J328": {"F": 0, "J": 0, "Y": 32},
    "L101": {"F": 12, "J": 30, "Y": 258},
    "T134": {"F": 0, "J": 0, "Y": 80},
    "T154": {"F": 0, "J": 12, "Y": 138},
    "TU3": {"F": 0, "J": 6, "Y": 42},
    "VC10": {"F": 8, "J": 24, "Y": 118},
    "YK42": {"F": 0, "J": 12, "Y": 108},
    "A332": {"F": 12, "J": 30, "Y": 251},
    "A333": {"F": 16, "J": 40, "Y": 279},
    "A338": {"F": 12, "J": 30, "Y": 251},
    "A339": {"F": 16, "J": 40, "Y": 279},
    "A342": {"F": 12, "J": 30, "Y": 219},
    "A343": {"F": 12, "J": 30, "Y": 235},
    "A345": {"F": 20, "J": 40, "Y": 315},
    "A346": {"F": 30, "J": 60, "Y": 350},
    "A359": {"F": 16, "J": 40, "Y": 259},
    "A35K": {"F": 20, "J": 50, "Y": 299},
    "A388": {"F": 30, "J": 60, "Y": 381},
    "AT43": {"F": 0, "J": 6, "Y": 42},
    "AT45": {"F": 0, "J": 6, "Y": 42},
    "AT46": {"F": 0, "J": 6, "Y": 42},
    "AT72": {"F": 0, "J": 8, "Y": 58},
    "AT73": {"F": 0, "J": 8, "Y": 58},
    "AT75": {"F": 0, "J": 8, "Y": 60},
    "AT76": {"F": 0, "J": 8, "Y": 62},
    "B190": {"F": 0, "J": 0, "Y": 18},
    "B350": {"F": 0, "J": 0, "Y": 12},
    "B712": {"F": 0, "J": 12, "Y": 122},
    "BBJ1": {"F": 0, "J": 10, "Y": 53},
    "B738": {"F": 0, "J": 16, "Y": 168},
    "BBJ2": {"F": 0, "J": 10, "Y": 53},
    "B38M": {"F": 0, "J": 16, "Y": 173},
    "BBJ3": {"F": 0, "J": 10, "Y": 53},
    "B742": {"F": 20, "J": 50, "Y": 296},
    "B744": {"F": 30, "J": 60, "Y": 310},
    "B748": {"F": 30, "J": 60, "Y": 320},
    "B752": {"F": 8, "J": 24, "Y": 207},
    "B753": {"F": 12, "J": 30, "Y": 247},
    "B762": {"F": 8, "J": 24, "Y": 184},
    "B763": {"F": 12, "J": 30, "Y": 248},
    "B764": {"F": 12, "J": 30, "Y": 254},
    "B772": {"F": 16, "J": 40, "Y": 264},
    "B77L": {"F": 16, "J": 40, "Y": 264},
    "B77W": {"F": 20, "J": 50, "Y": 316},
    "B788": {"F": 12, "J": 30, "Y": 258},
    "B789": {"F": 16, "J": 40, "Y": 294},
    "B78X": {"F": 20, "J": 50, "Y": 320},
    "BCS1": {"F": 0, "J": 12, "Y": 123},
    "BCS3": {"F": 0, "J": 16, "Y": 144},
    "BE20": {"F": 0, "J": 0, "Y": 9},
    "BE24": {"F": 0, "J": 0, "Y": 3},
    "BE36": {"F": 0, "J": 0, "Y": 5},
    "BE58": {"F": 0, "J": 0, "Y": 5},
    "BE60": {"F": 0, "J": 0, "Y": 5},
    "BE6G": {"F": 0, "J": 0, "Y": 5},
    "B60T": {"F": 0, "J": 0, "Y": 5},
    "BN2P": {"F": 0, "J": 0, "Y": 16},
    "C130": {"F": 0, "J": 0, "Y": 90},
    "C160": {"F": 0, "J": 0, "Y": 93},
    "C17": {"F": 0, "J": 0, "Y": 102},
    "C172": {"F": 0, "J": 0, "Y": 3},
    "C182": {"F": 0, "J": 0, "Y": 3},
    "R182": {"F": 0, "J": 0, "Y": 3},
    "C208": {"F": 0, "J": 0, "Y": 8},
    "C25A": {"F": 0, "J": 0, "Y": 8},
    "C25B": {"F": 0, "J": 0, "Y": 9},
    "C310": {"F": 0, "J": 0, "Y": 5},
    "C337": {"F": 0, "J": 0, "Y": 5},
    "C404": {"F": 0, "J": 0, "Y": 9},
    "C408": {"F": 0, "J": 0, "Y": 19},
    "C414": {"F": 0, "J": 0, "Y": 7},
    "C46":  {"F": 0, "J": 0, "Y": 3},
    "C510": {"F": 0, "J": 0, "Y": 5},
    "C550": {"F": 0, "J": 0, "Y": 11},
    "C56X": {"F": 0, "J": 0, "Y": 9},
    "C680": {"F": 0, "J": 0, "Y": 12},
    "C700": {"F": 0, "J": 0, "Y": 10},
    "C750": {"F": 0, "J": 0, "Y": 12},
    "CL35": {"F": 0, "J": 0, "Y": 9},
    "CL60": {"F": 0, "J": 0, "Y": 12},
    "CONI": {"F": 0, "J": 12, "Y": 69},
    "CONS": {"F": 0, "J": 10, "Y": 51},
    "CRJ2": {"F": 0, "J": 6, "Y": 44},
    "CRJ5": {"F": 0, "J": 6, "Y": 44},
    "CRJ7": {"F": 0, "J": 10, "Y": 68},
    "CRJ9": {"F": 0, "J": 12, "Y": 78},
    "CRJX": {"F": 0, "J": 12, "Y": 92},
    "DA42": {"F": 0, "J": 0, "Y": 4},
    "DA62": {"F": 0, "J": 0, "Y": 6},
    "DC3":  {"F": 0, "J": 0, "Y": 26},
    "DC6":  {"F": 0, "J": 8, "Y": 60},
    "DC86": {"F": 12, "J": 30, "Y": 217},
    "DH8A": {"F": 0, "J": 6, "Y": 31},
    "DH8B": {"F": 0, "J": 6, "Y": 31},
    "DH8C": {"F": 0, "J": 8, "Y": 42},
    "DH8D": {"F": 0, "J": 10, "Y": 64},
    "DHC2": {"F": 0, "J": 0, "Y": 4},
    "DHC6": {"F": 0, "J": 0, "Y": 16},
    "DHC7": {"F": 0, "J": 6, "Y": 44},
    "E135": {"F": 0, "J": 6, "Y": 31},
    "E13L": {"F": 0, "J": 0, "Y": 12},
    "E140": {"F": 0, "J": 4, "Y": 40},
    "E145": {"F": 0, "J": 6, "Y": 44},
    "E19L": {"F": 0, "J": 0, "Y": 19},
    "E50P": {"F": 0, "J": 0, "Y": 5},
    "E55P": {"F": 0, "J": 0, "Y": 8},
    "EA50": {"F": 0, "J": 0, "Y": 5},
    "EVAL": {"F": 0, "J": 0, "Y": 9},
    "F28":  {"F": 0, "J": 8, "Y": 57},
    "F70":  {"F": 0, "J": 10, "Y": 62},
    "FA50": {"F": 0, "J": 0, "Y": 8},
    "GLF4": {"F": 0, "J": 0, "Y": 19},
    "H25B": {"F": 0, "J": 0, "Y": 15},
    "HDJT": {"F": 0, "J": 0, "Y": 6},
    "IL76": {"F": 0, "J": 0, "Y": 5},
    "JS41": {"F": 0, "J": 4, "Y": 26},
    "LJ25": {"F": 0, "J": 0, "Y": 8},
    "LJ35": {"F": 0, "J": 0, "Y": 8},
    "LJ45": {"F": 0, "J": 0, "Y": 9},
    "MD82": {"F": 0, "J": 12, "Y": 160},
    "MD83": {"F": 0, "J": 12, "Y": 160},
    "MD88": {"F": 0, "J": 12, "Y": 160},
    "MD90": {"F": 0, "J": 12, "Y": 160},
    "MU2":  {"F": 0, "J": 0, "Y": 6},
    "P06T": {"F": 0, "J": 0, "Y": 3},
    "P180": {"F": 0, "J": 0, "Y": 7},
    "P212": {"F": 0, "J": 0, "Y": 9},
    "P46T": {"F": 0, "J": 0, "Y": 5},
    "M600": {"F": 0, "J": 0, "Y": 5},
    "PA24": {"F": 0, "J": 0, "Y": 4},
    "PA34": {"F": 0, "J": 0, "Y": 6},
    "PA44": {"F": 0, "J": 0, "Y": 3},
    "RJ70": {"F": 0, "J": 12, "Y": 70},
    "RJ85": {"F": 0, "J": 14, "Y": 86},
    "RJ1H": {"F": 0, "J": 16, "Y": 96},
    "SB20": {"F": 0, "J": 6, "Y": 44},
    "SF34": {"F": 0, "J": 4, "Y": 30},
    "SF50": {"F": 0, "J": 0, "Y": 6},
    "SH33": {"F": 0, "J": 3, "Y": 30},
    "SH36": {"F": 0, "J": 4, "Y": 32},
    "SR22": {"F": 0, "J": 0, "Y": 3},
    "SR2T": {"F": 0, "J": 0, "Y": 3},
    "SU95": {"F": 0, "J": 12, "Y": 86},
    "SW4":  {"F": 0, "J": 0, "Y": 19},
    "T204": {"F": 8, "J": 20, "Y": 182},
    "TBM8": {"F": 0, "J": 0, "Y": 6},
    "MI17": {"F": 0, "J": 0, "Y": 30},
    "GA8": {"F": 0, "J": 0, "Y": 7}
}


# Utility: Generate filename with current timestamp
def generate_filename(prefix):
    return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

# Utility: Calculate cargo capacity
def calculate_cargo_capacity(mzfw, oew, pax_count):
    return max(0, mzfw - oew - (pax_count * PASSENGER_WEIGHT_LBS))

# Utility: Adjust layout to match SimBrief pax count
def adjust_layout(layout, pax):
    total_seats = layout["F"] + layout["J"] + layout["Y"]
    layout = layout.copy()
    if total_seats < pax:
        layout["Y"] += pax - total_seats
    elif total_seats > pax:
        layout["Y"] -= total_seats - pax
    return layout

# Main processing function
def process_aircraft_data():
    # Fetch aircraft data from SimBrief's public endpoint
    response = requests.get(SIMBRIEF_URL)
    if response.status_code != 200:
        raise Exception("Failed to fetch aircraft data from SimBrief public API.")

    data = response.json()
    processed = {}
    unknown = []

    # Loop through each aircraft type by ICAO
    for icao, details in data.items():
        base = details.get("airframes", [])[0] if details.get("airframes") else {}
        aircraft_name = details.get("aircraft_name")
        options = base.get("airframe_options", {})

        # Extract weight and passenger data
        try:
            basetype = options.get('basetype','')
            aircraft_icao = options.get('icao','')
            pax = int(options.get("maxpax", 0))
            oew = float(options.get("oew", 0))
            mzfw = float(options.get("mzfw", 0))
        except ValueError:
            continue  # Skip if any data is invalid

        # Determine if the aircraft is a freighter
        is_freighter = pax == 0 or details.get("aircraft_is_cargo", False)

        # Calculate CGO capacity
        cargo = calculate_cargo_capacity(mzfw, oew, pax)

        # Base data structure for the aircraft
        aircraft_data = {
            "icao": aircraft_icao,
            "aircraft_name": aircraft_name,
            "base_type": basetype,
            "default_pax": pax,
            "mzfw_lbs": mzfw,
            "oei_lbs": oew,
            "CGO": cargo,
            "is_freighter": is_freighter
        }

        # If not a freighter and we have layout, include seats
        if not is_freighter and icao in CABIN_LAYOUTS:
            layout = adjust_layout(copy.deepcopy(CABIN_LAYOUTS[icao]), pax)
            aircraft_data.update(layout)
        elif not is_freighter:
            # Aircraft not in layouts: log for review
            unknown.append({ "icao": icao, **aircraft_data })
            continue

        # If freighter and max passengers bigger than 0 add all seats as economy seats
        if is_freighter and pax > 0:
            layout = {"F": 0, "J": 0, "Y": pax}
            aircraft_data.update(layout)
        elif is_freighter and pax == 0:
            layout = {"F": 0, "J": 0, "Y": 0}
            aircraft_data.update(layout)
        # Save to final dataset
        processed[icao] = aircraft_data

        # special case for Boeing 737,738,739 BCF and BDFS
        # check if there are any other airframes for cargo for this icao if the base isn't already a cargo
        if not is_freighter and details.get("airframes") and len(details.get("airframes")) > 1:
            non_base_airframes = details.get("airframes")[1:]
            for nairframe in non_base_airframes:
                nairframe_icao = nairframe.get("airframe_icao")
                nairframe_name = nairframe.get("airframe_name")
                nairframe_type = nairframe.get("airframe_base_type")
                noptions = nairframe.get("airframe_options",{})
                if aircraft_name != nairframe_name:
                    naircraft_id = f"{nairframe_icao}{nairframe_name.replace(aircraft_name,'')}"
                    if naircraft_id not in processed.keys():
                        # Extract weight and passenger data
                        try:
                            nbasetype = nairframe_type
                            naircraft_icao = nairframe_icao
                            npax = int(noptions.get("maxpax", 0))
                            noew = float(noptions.get("oew", 0))
                            nmzfw = float(noptions.get("mzfw", 0))
                        except ValueError:
                            continue  # Skip if any data is invalid

                        # Determine if the aircraft is a freighter
                        nis_freighter = npax == 0 or is_freighter

                        # Calculate CGO capacity
                        ncargo = calculate_cargo_capacity(nmzfw, noew, npax)

                        # Base data structure for the aircraft
                        naircraft_data = {
                            "icao": nairframe_icao,
                            "aircraft_name": nairframe_name,
                            "base_type": nairframe_type,
                            "default_pax": npax,
                            "mzfw_lbs": nmzfw,
                            "oei_lbs": noew,
                            "CGO": ncargo,
                            "is_freighter": nis_freighter
                        }

                        # If not a freighter skip
                        if not nis_freighter:
                            continue

                        # If freighter and max passengers bigger than 0 add all seats as economy seats
                        if nis_freighter and npax > 0:
                            nlayout = {"F": 0, "J": 0, "Y": npax}
                            naircraft_data.update(nlayout)
                        elif nis_freighter and pax == 0:
                            nlayout = {"F": 0, "J": 0, "Y": 0}
                            naircraft_data.update(nlayout)
                        # Save to final dataset
                        processed[naircraft_id] = naircraft_data


    # Write processed aircraft data to file
    out_file = f"./{generate_filename('aircraft_data')}"
    with open(out_file, "w") as f:
        json.dump(processed, f, indent=4)

    # Write unknown aircraft to separate file if any
    if unknown:
        unk_file = f"./{generate_filename('unknown_aircrafts')}"
        with open(unk_file, "w") as f:
            json.dump(unknown, f, indent=4)
        print(f"Unknown aircraft saved to {unk_file}")

    print(f"Processed aircraft data saved to {out_file}")

# Run the main function
if __name__ == "__main__":
    process_aircraft_data()