import csv,time,os,json
from datetime import datetime,timedelta
from argparse import ArgumentParser

# Constants
AIRCRAFT_CONFIG_FILE = "aircraft_config.json"

def load_aircraft_config(config_file=AIRCRAFT_CONFIG_FILE):
    """
    Load aircraft configuration from JSON file.

    Returns:
        dict: Aircraft configuration with ICAO codes as keys
    """
    # Try to load from current directory first, then parent directory
    config_paths = [
        config_file,
        os.path.join(os.path.dirname(__file__), config_file),
        os.path.join(os.path.dirname(__file__), '..', config_file)
    ]

    for path in config_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    print(f"✅ Loaded aircraft configuration from {path}")
                    return config
            except Exception as e:
                print(f"⚠️ Error loading aircraft config from {path}: {e}")

    print(f"❌ Aircraft configuration file not found. Searched:")
    for path in config_paths:
        print(f"   - {path}")
    raise FileNotFoundError(f"Aircraft configuration file '{config_file}' not found")

def build_airline_subfleet_by_flight_type(aircraft_config):
    """
    Build airline_subfleet_by_flight_type dictionary from aircraft config.

    Args:
        aircraft_config: Aircraft configuration dictionary

    Returns:
        dict: Nested dictionary {airline: {flight_type: [aircraft_icao, ...]}}
    """
    result = {}

    for icao, data in aircraft_config.items():
        airlines = data.get('airlines', {})
        for airline, flight_types in airlines.items():
            if airline not in result:
                result[airline] = {}

            for flight_type in flight_types:
                if flight_type not in result[airline]:
                    result[airline][flight_type] = []
                result[airline][flight_type].append(icao)

    return result

def build_aircrafts_range_by_icao(aircraft_config):
    """
    Build aircrafts_range_by_icao dictionary from aircraft config.

    Args:
        aircraft_config: Aircraft configuration dictionary

    Returns:
        dict: Dictionary {aircraft_icao: range_nm}
    """
    return {icao: data['range'] for icao, data in aircraft_config.items()}

# Load aircraft configuration from JSON
_aircraft_config = load_aircraft_config()
airline_subfleet_by_flight_type = build_airline_subfleet_by_flight_type(_aircraft_config)
aircrafts_range_by_icao = build_aircrafts_range_by_icao(_aircraft_config)

special_code_to_airline = {
    "CRC" : "CRN"
}

v5_flight_type_to_v7 = {
    "P" : "J", # vuelos comerciales scheduled
    "C" : "F"  # vuelos de carga scheduled
}

def validate_subfleets(file):
    with open(file,'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # check that the aircraft is on the airline subfleet dict and ranges dict
            # add schedule specific logic
            aircraft_in_fleet_dict = False
            aircraft_type = row.get("type")
            if aircraft_type in airline_subfleet_by_flight_type["CRN"]["J"]:
                # found aircraft in passangers fleet
                aircraft_in_fleet_dict = True
            elif aircraft_type in airline_subfleet_by_flight_type["CRN"]["F"]:
                # found aircraft in freighter fleet
                aircraft_in_fleet_dict = True
            
            if not aircraft_in_fleet_dict:
                print(f"{aircraft_type} not found on airline fleet dict, check passengers and freighter aircrafts\n--------")

            if aircraft_type not in aircrafts_range_by_icao:
                print(f"{aircraft_type} not found on airline range dict, check passengers and freighter aircrafts\n--------")

def import_aircraft(file):
    
    with open(file,'r') as csvfile:
        data = []
        reader = csv.DictReader(csvfile)
        for row in reader:
            # add aircraft specific logic
            registration = row.get("registration")
            if registration.startswith("AC-T") or registration.startswith("AC-C"):
                data.append(row)
    return data

def print_data(data):
    for row in data:
        for col,val in row.items():
            print(f"{col}:{val}")
        print("-----")
def import_schedules(file):
    
    with open(file,'r') as csvfile:
        data = []
        reader = csv.DictReader(csvfile)
        for row in reader:
            # add schedule specific logic
            code = row.get("code")
            if code.startswith("CRC") or code.startswith("CRN"):
                data.append(row)
    return data

def export_aircrafts(data,file):
    if len(data) > 0:
        timestr = time.strftime("%Y%m%d-%H%M%S")
        export_file = f"exported-{timestr}-{file}"
        with open(export_file,'w', newline='') as csvfile:
            columns = [
                "subfleet",
                "iata",
                "icao",
                "hub_id",
                "airport_id",
                "name",
                "registration",
                "fin",
                "hex_code",
                "selcal",
                "dow",
                "zfw",
                "mtow",
                "mlw",
                "status",
                "simbrief_type"
            ]
            writer = csv.DictWriter(csvfile,fieldnames=columns)
            writer.writeheader()
            new_aircrafts_range_by_icao = dict()
            for row in data:
                subfleet = f"{row.get('icao').replace(' ','')}"
                icao = f"{row.get('icao').replace(' ','')}"
                name = f"{row.get('name').strip()}"
                registration = f"{row.get('registration').replace(' ','')}"
                mtow = f"{row.get('weight').replace(' ','')}"
                range = f"{row.get('range').replace(' ','')}"
                # if needed populate the aircrafts range by ICAO to be used while creating flights and assigning subfleets
                if icao not in aircrafts_range_by_icao.keys():
                    if range != '':
                        new_aircrafts_range_by_icao[icao] = range
                elif int(aircrafts_range_by_icao[icao]) < int(range):
                    print(f"WARNING: Higher range identified for {icao}:\n\t\tStored:{aircrafts_range_by_icao[icao]}\n\t\tNew:{range}") 
                # write the aircraft info
                writer.writerow({
                    "subfleet":subfleet,
                    "iata":"",
                    "icao":icao,
                    "hub_id":"MUHA",
                    "airport_id":"MUHA",
                    "name":name,
                    "registration":registration,
                    "fin":"",
                    "hex_code":"",
                    "selcal":"",
                    "dow":"",
                    "zfw":"",
                    "mtow":mtow,
                    "mlw":"",
                    "status":"A",
                    "simbrief_type":""
                })
        print(f"Aircrafts exporter completed writing {export_file}")
        print(f"New aircraft ranges detected\n{new_aircrafts_range_by_icao}")
        return True
    
    print("No Aircrafts data available to export")
    return False

def remove_non_numeric(text):
    return "".join(filter(str.isdigit, text))

def export_flights(data,file):
    if len(data) > 0:
        timestr = time.strftime("%Y%m%d-%H%M%S")
        export_file = f"exported-{timestr}-{file}"
        with open(export_file,'w', newline='') as csvfile:
            columns = [
                "airline",
                "flight_number",
                "route_code",
                "callsign",
                "route_leg",
                "dpt_airport",
                "arr_airport",
                "alt_airport",
                "days",
                "dpt_time",
                "arr_time",
                "level",
                "distance",
                "flight_time",
                "flight_type",
                "load_factor",
                "load_factor_variance",
                "pilot_pay",
                "route",
                "notes",
                "start_date",
                "end_date",
                "active",
                "subfleets",
                "fares",
                "fields",
                "event_id",
                "user_id"
            ]
            writer = csv.DictWriter(csvfile,fieldnames=columns)
            writer.writeheader()
            
            for row in data:
                # in phpvms v5 sometimes sunday is '0' if that is found change it for '7'
                code = f"{row.get('code').replace(' ','')}"
                airline = code
                if airline != "CRN" and (airline in special_code_to_airline.keys()):
                    # get the special code
                    airline = special_code_to_airline[code]
                if airline != "CRN" and (airline not in special_code_to_airline.keys()):
                    # skip row if airline code is not tracked on special codes
                    print(f"unknow airline: '{airline}' skip row if airline code is not tracked on special codes")
                    continue
                        
                # in v7 flight type is 'F' for freighter and 'J' for passangers schedules
                flighttype = f"{row.get('flighttype').replace(' ','')}"
                if flighttype == "":
                    if code == "CRC":
                        flighttype = "C"
                    else:
                        flighttype = "P"
                flight_type = ""
                if flighttype in v5_flight_type_to_v7.keys():
                    flight_type = v5_flight_type_to_v7[flighttype]
                else:
                    # unknow flight type skip row
                    print(f"unknow flight type:'{flighttype}' skipped row!")
                    print(row)
                    continue
                # f"{row.get('').replace(' ','')}"
                days = f"{row.get('daysofweek').replace(' ','').replace('0','7')}"
                flight_number = f"{row.get('flightnum').replace(' ','')}"
                dpt_airport = f"{row.get('depicao').replace(' ','')}"
                arr_airport = f"{row.get('arricao').replace(' ','')}"
                distance = f"{row.get('distance').replace(' ','')}"
                dpt_time = f"{row.get('deptime').replace(' ','').replace('UTC','')}"
                arr_time = f"{row.get('arrtime').replace(' ','').replace('UTC','')}"
                # flight_time = f"{row.get('flighttime').replace(' ','')}" # flight time would be calculate using dpt_time and arr_time
                # flight time in v5 is a float that represents the total flight time in hours
                # flight time in v7 is a int that represents the total flight time in minutes
                # the flight time is a string of the absolute value converted to an integer of the (arr_time - dep_time)
                time_fmt = '%H:%M'
                if arr_time.count(':') == 2:
                    # remove seconds the last three characters
                    arr_time = arr_time[:-3]
                if dpt_time.count(':') == 2:
                    # remove seconds the last three characters
                    dpt_time = dpt_time[:-3]
                # print(flight_number)
                # print(arr_time)
                # print(dpt_time)
                arr_time_datetime = datetime.strptime(arr_time,time_fmt)
                dpt_time_datetime = datetime.strptime(dpt_time,time_fmt)
                dpt_arr_time_delta_in_minutes = (arr_time_datetime - dpt_time_datetime).total_seconds()/60
                flight_time_in_minutes = abs(int(dpt_arr_time_delta_in_minutes))
                flight_time = str(flight_time_in_minutes)
                pilot_pay = f"{row.get('price').replace(' ','')}"
                active = "1"
                # each flight needs a subfleet
                # based on the range by ICAO and type of flight we would assign the subfleet
                subfleets_list = []
                subfleets = ""
                # construct the subfleets list
                for aircraft_icao in airline_subfleet_by_flight_type[airline][flight_type]:
                    # if the subfleet icao has the range
                    if float(aircrafts_range_by_icao[aircraft_icao]) > float(distance):
                        # add the icao to the subfleet list for this flight
                        subfleets_list.append(aircraft_icao)
                if len(subfleets_list) > 0:
                    # convert the subfleet list to a string where each subfleet is separated by ';' example: 'A30F;B48F;B74F;B75F;B76F;B77F;MD1F'
                    subfleets = ';'.join(subfleets_list)
                writer.writerow({
                    "airline": airline,
                    "flight_number": flight_number, 
                    "route_code": "",
                    "callsign": flight_number,
                    "route_leg":"",
                    "dpt_airport":dpt_airport,
                    "arr_airport":arr_airport,
                    "alt_airport":"",
                    "days":days,
                    "dpt_time":dpt_time,
                    "arr_time":arr_time,
                    "level":"",
                    "distance":str(int(float(distance))),
                    "flight_time":flight_time,
                    "flight_type":flight_type,
                    "load_factor":"",
                    "load_factor_variance":"",
                    "pilot_pay":pilot_pay,
                    "route":"",
                    "notes":"",
                    "start_date":"",
                    "end_date":"",
                    "active":active,
                    "subfleets":subfleets,
                    "fares":"",
                    "fields":"",
                    "event_id":"",
                    "user_id":""
                })
        print(f"Flight exporter completed writing {export_file}")
        return True
    
    print("No flight data available to export")
    return False


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
            
def update_subfleets(CSV_INPUT):
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

        flight_type=row["flight_type"]
        callsign=row["callsign"]
        # check if callsign needs to be updated
        if flight_type == 'F':
            if callsign != 'CRF':
                row['callsign'] = 'CRF'
        elif flight_type == 'J':
            if callsign != '':
                row['callsign'] = ''
        flight_distance = int(row['distance'])
        dpt_time = row["dpt_time"]
        arr_time = row["arr_time"]
        average_speed_knots = 300
        avg_flight_time_min = (flight_distance / average_speed_knots) * 60
        # the flight time is a string of the absolute value converted to an integer of the (arr_time - dep_time)
        time_fmt = '%H:%M'
        if arr_time.count(':') == 2:
            # remove seconds the last three characters
            arr_time = arr_time[:-3]
        if dpt_time.count(':') == 2:
            # remove seconds the last three characters
            dpt_time = dpt_time[:-3]
        dpt_time_datetime = datetime.strptime(dpt_time,time_fmt)
        if arr_time == "":
            arr_time_datetime = dpt_time_datetime + timedelta(minutes=avg_flight_time_min)
            row['arr_time'] = arr_time_datetime.strftime(time_fmt)
        else:
            arr_time_datetime = datetime.strptime(arr_time,time_fmt)
        dpt_arr_time_delta_in_minutes = (arr_time_datetime - dpt_time_datetime).total_seconds()/60
        flight_time_in_minutes = abs(int(dpt_arr_time_delta_in_minutes))
        flight_time = str(flight_time_in_minutes)
        row["flight_time"] = flight_time
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
    os.makedirs(timestr, exist_ok=True)
    CSV_OUTPUT = f"{timestr}/exported-{timestr}-{CSV_INPUT}"
    with open(CSV_OUTPUT, 'w', newline='', encoding='utf-8') as csvfile_out:
        writer = csv.DictWriter(csvfile_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f'Updated CSV saved as {CSV_OUTPUT}')

    # if file has more than 500 schedules separate in files of 500 flights per file
    if len(rows) > 500:
        print("Spliting schedules into multiple files for import")
        with open(CSV_OUTPUT,'r') as file:
            split(file,row_limit=500,output_path=f"{timestr}")



def main():

    parser = ArgumentParser()
    parser.add_argument("-f", "--file", dest="filename",
                    help="phpvmsv5 csv file to read", metavar="filename.csv")
    parser.register('type', 'filetype', lambda s: s if s in ["aircrafts","schedules","add-subfleets-v7","validate-subfleet"] else None)
    parser.add_argument("-t", "--filetype", type="filetype",
                    help="phpvmsv5 type of file to read ('aircrafts'|'schedules'|'add-subfleets-v7'|'validate-subfleet')", metavar="aircrafts")

    try:
        filename = ""
        args = parser.parse_args()
        # Access arguments safely
        if args.filename:
            print(f"Defined argument: {args.filename}")
            filename = args.filename
        else:
            raise Exception("'file' not defined")
        if args.filetype and filename != "":
            filetype = args.filetype
            print(f"Defined argument: {filetype}")
            if filetype != "":
                if filetype == "aircrafts":
                    imported_aircarft_data = import_aircraft(filename)
                    export_aircrafts(imported_aircarft_data,filename)
                elif filetype == "schedules":
                    imported_schedules_data = import_schedules(filename)
                    # print([imported_schedules_data[0]])
                    # print_data([imported_schedules_data[0]])
                    export_flights(imported_schedules_data,filename)
                elif filetype == "add-subfleets-v7":
                    update_subfleets(filename)
                elif filetype == "validate-subfleet":
                    validate_subfleets(filename)
                    print(f"Completed subfleet validation: {filename}")
                else: 
                    print("Unknown filetype")
        else:
            raise Exception("'filetype' not defined")

    except Exception as e:
        print(f"ERROR: {e}\n")
        parser.print_help()



if __name__ == "__main__":
    main()
