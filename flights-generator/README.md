# ✈️ phpVMS7 Flight Schedule Generator

---

## ⚡ Quick Reference

**Usage:**

```bash
python generate_flights.py BASE_AIRPORT_ICAO BASE_AIRPORT_IATA_CODE
```

Example:

```bash
python generate_flights.py MUCC CCC
```

- **BASE_AIRPORT_ICAO** → ICAO of your main airport (e.g., MUCC)  
- **BASE_AIRPORT_IATA_CODE** → IATA code for grouping & file naming (e.g., CCC)

**Input File:**  
Place a `airports.txt` file in the folder `MUCC_CCC`:

```
MUCC-CCC,KEYW-EYW
MUCC-CCC,MKJS-MBJ
MUCC-CCC,TNCM-SXM
```

**Output:**  
Generates CSV files ready for phpVMS v7 import:

```
MUCC_CCC_YYYYMMDD-HHMMSS_generated_phpvms_flights.csv
```

Each route pair produces **4 flights**:
- 2 Passenger flights (Outbound + Return)
- 2 Cargo flights (Outbound + Return)

---

# 📌 Description

This Python script automates the generation of flight schedules for phpVMS v7.  
It reads a list of airport route pairs, calculates flight distances via the AirportGap API, and generates passenger and cargo roundtrip flights with subfleets automatically assigned based on aircraft range.

---

## 📌 Features

- Generate 4 flights per route pair (Passenger Outbound, Passenger Return, Cargo Outbound, Cargo Return).
- Automatically calculates flight distance using [AirportGap API](https://airportgap.com/).
- Generates departure and arrival times dynamically based on distance.
- Assigns subfleets automatically according to flight distance and aircraft range.
- Splits generated schedules into multiple CSV files if they exceed 500 flights (ready for phpVMS import).
- Designed for **Aerocaribbean VA** but can be adapted for other virtual airlines.

---

## ⚙️ Requirements

- Python 3.7+
- `requests` module (`pip install requests`)
- AirportGap API token (free account at [airportgap.com](https://airportgap.com/))

---

## 📂 Folder Structure

```
project_root/
│
├── generate_flights.py
├── MUCC_CCC/
│   └── airports.txt
└── README.md
```

---

## 🔑 Setup

1. Clone or download this repository.
2. Install required dependencies:
   ```bash
   pip install requests
   ```
3. Export your AirportGap API token:
   - **Linux/macOS:**
     ```bash
     export AIRPORT_GAP_TOKEN=your_api_token_here
     ```
   - **Windows (PowerShell):**
     ```powershell
     setx AIRPORT_GAP_TOKEN "your_api_token_here"
     ```

---

## 🚀 Usage

Run the script using:

```bash
python generate_flights.py BASE_AIRPORT_ICAO BASE_AIRPORT_IATA_CODE
```

Example:

```bash
python generate_flights.py MUCC CCC
```

---

### 📄 Example Input (`airports.txt`)

```
MUCC-CCC,KEYW-EYW
MUCC-CCC,MKJS-MBJ
MUCC-CCC,TNCM-SXM
```

---

### ✅ Example Output (`MUCC_CCC_YYYYMMDD-HHMMSS_generated_phpvms_flights.csv`)

```
airline,flight_number,route_code,callsign,route_leg,dpt_airport,arr_airport,alt_airport,days,dpt_time,arr_time,level,distance,flight_time,flight_type,load_factor,load_factor_variance,pilot_pay,route,notes,start_date,end_date,active,subfleets,fares,fields,event_id,user_id
CRN,1000,CCC,,,MUCC,KEYW,,1234567,18:45,19:30,,226,45,J
CRN,1001,CCC,,,KEYW,MUCC,,1234567,11:30,12:15,,226,45,J
CRN,1002,CCC,,,MUCC,KEYW,,1234567,11:45,12:30,,226,45,F
CRN,1003,CCC,,,KEYW,MUCC,,1234567,06:00,06:45,,226,45,F
```

---

## ⚠️ Notes

- API requests are limited to **100 per minute**; the script will pause automatically if the limit is reached.
- If no `airports.txt` file is found in the folder, the script will exit.
- Flight numbers start at **1000** and increment automatically.
- Tailored for Aerocaribbean VA (`airline_code=CRN`) but can be modified in the script.

---

## 🛠️ Customization

- **Airline code mapping:** Modify `special_code_to_airline` dictionary.
- **Aircraft subfleets:** Update `airline_subfleet_by_flight_type` dictionary.
- **Aircraft ranges:** Update `aircrafts_range_by_icao` dictionary.

---

## 👨‍💻 Example Workflow

1. Create a file `MUCC_CCC/airports.txt`.
2. Run:
   ```bash
   python generate_flights.py MUCC CCC
   ```
3. Confirm the script finds the input file.
4. Generated files appear in:
   ```
   MUCC_CCC/YYYYMMDD-HHMMSS/exported_MUCC_CCC_YYYYMMDD-HHMMSS_generated_phpvms_flights.csv
   ```
5. Import CSV files into phpVMS7.

---

## 📜 License

MIT License – Free to use and modify for your Virtual Airline needs.

---

## ✈️ Credits

- Developed for **Aerocaribbean Virtual Airline**  
- Based on phpVMS v7 CSV schedule format  
- Uses [AirportGap API](https://airportgap.com/) for distance calculations
