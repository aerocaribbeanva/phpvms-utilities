import csv
import time
from datetime import datetime
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
        "J" : ["A20N","A21N","A310","A319","A320","A321","A332","A333","A346","A359","A388","AN24","AN26","AT45","AT46","AT75","AT76","B38M","B712","B732","B735","B737","B738","B739","B744","B752","B753","B763","B764","B77L","B77W","B788","C25C","DH8D","E110","E140","E145","E175","E190","E195","IL18","IL96","KODI","L410","PC12","TBM9","YK40"], #passengers subfleet string
        "F" : ["A30F","B48F","B74F","B75F","B76F","B77F","MD1F"], #freighter subfleet
    }
}
# range_by_icao verified on 2/19/2025
aircrafts_range_by_icao = {'A20N': '3500', 'A21N': '4000', 'A30F': '4200', 'A310': '5150', 'A319': '3700', 'A320': '3300', 'A321': '2300', 'A332': '7250', 'A333': '6350', 'A346': '7900', 'A359': '8100', 'A388': '8000', 'AN24': '1000', 'AN26': '1100', 'AT45': '850', 'AT46': '800', 'AT75': '825', 'AT76': '950', 'B38M': '3550', 'B48F': '4200', 'B712': '2060', 'B732': '2300', 'B735': '1600', 'B737': '3350', 'B738': '3400', 'B739': '3200', 'B744': '7260', 'B74F': '4970', 'B752': '3900', 'B753': '3800', 'B75F': '3600', 'B763': '6000', 'B764': '6000', 'B76F': '3255', 'B77F': '8555', 'B77L': '8555', 'B77W': '7370', 'B788': '7355', 'C25C': '2165', 'DH8D': '1100', 'E110': '1200', 'E140': '1600', 'E145': '1550', 'E175': '2000', 'E190': '2400', 'E195': '2200', 'IL18': '2200', 'IL96': '6000', 'KODI': '1132', 'L410': '800', 'MD1F': '3800', 'PC12': '1845', 'TBM9': '1730', 'YK40': '1000'}

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
            if code.startswith("CRC") or code.startswith("CRC"):
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
                "route,notes",
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
                if airline != "CRN":
                    # check if it is a special code
                    if code in special_code_to_airline.keys():
                        airline = special_code_to_airline[code]
                else:
                    # skip row if airline code is not tracked on special codes
                    break
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
                arr_time_datetime = datetime.strftime(arr_time,time_fmt)
                dpt_time_datetime = datetime.strftime(dpt_time,time_fmt)
                dpt_arr_time_delta_in_minutes = (arr_time_datetime - dpt_time_datetime).total_seconds()/60
                flight_time_in_minutes = abs(int(dpt_arr_time_delta_in_minutes))
                flight_time = str(flight_time_in_minutes)
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
                    "distance":distance,
                    "flight_time":flight_time,
                    "flight_type":"",
                    "load_factor":"",
                    "load_factor_variance":"",
                    "pilot_pay":"",
                    "route,notes":"",
                    "start_date":"",
                    "end_date":"",
                    "active":"",
                    "subfleets":"",
                    "fares":"",
                    "fields":"",
                    "event_id":"",
                    "user_id":""
                })
        print(f"Flight exporter completed writing {export_file}")
        return True
    
    print("No flight data available to export")
    return False
            


def main():

    parser = ArgumentParser()
    parser.add_argument("-f", "--file", dest="filename",
                    help="phpvmsv5 csv file to read", metavar="filename.csv")
    parser.register('type', 'filetype', lambda s: s if s in ["aircrafts","schedules"] else None)
    parser.add_argument("-t", "--filetype", type="filetype",
                    help="phpvmsv5 type of file to read ('aircrafts'|'schedules')", metavar="aircrafts")

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
                    print([imported_schedules_data[0]])
                    print_data([imported_schedules_data[0]])
                    # export_flights(imported_data,filename)
                case _: 
                    print("Unknown filetype")
        else:
            raise Exception("'filetype' not defined")

    except Exception as e:
        print(f"ERROR: {e}\n")
        parser.print_help()



if __name__ == "__main__":
    main()
