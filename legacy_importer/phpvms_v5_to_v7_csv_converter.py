import csv,time,os
from datetime import datetime,timedelta
from argparse import ArgumentParser

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
                print(f"{aircraft_type} not found on airline range dict, chack passengers and freighter aircrafts\n--------")

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
                    "callsign": "",
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
            match filetype:
                case "aircrafts":
                    imported_aircarft_data = import_aircraft(filename)
                    export_aircrafts(imported_aircarft_data,filename)
                case "schedules":
                    imported_schedules_data = import_schedules(filename)
                    # print([imported_schedules_data[0]])
                    # print_data([imported_schedules_data[0]])
                    export_flights(imported_schedules_data,filename)
                case "add-subfleets-v7":
                    update_subfleets(filename)
                case "validate-subfleet":
                    validate_subfleets(filename)
                    print(f"Completed subfleet validation: {filename}")
                case _: 
                    print("Unknown filetype")
        else:
            raise Exception("'filetype' not defined")

    except Exception as e:
        print(f"ERROR: {e}\n")
        parser.print_help()



if __name__ == "__main__":
    main()
