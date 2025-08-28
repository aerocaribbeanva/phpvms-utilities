# ✈️ phpVMS7 Flight Schedule Generator

⚠️ **WARNING: Do NOT Remove Lines from `airports.txt`**

> Never remove lines from the `airports.txt` file once you have generated and imported flights into phpVMS7. Doing so will cause flight numbers to shift, leading to broken or duplicate entries. **Only add new lines at the end.**

---

## ⚡ Quick Reference

### Regular Mode:

```bash
python generate_flights.py BASE_AIRPORT_ICAO BASE_AIRPORT_IATA_CODE
```

Example:

```bash
python generate_flights.py MUCC CCC
```

**Input File:**  
Place a `airports.txt` file in the folder `MUCC_CCC/`.

```
MUCC-CCC,KEYW-EYW
MUCC-CCC,MKJS-MBJ
MUCC-CCC,TNCM-SXM
```

Each route pair generates **4 flights**:
- 2 Passenger flights (outbound + return)
- 2 Cargo flights (outbound + return)

---

### 🧭 Tour Mode:

```bash
python generate_flights.py TOUR TOURCODE
```

Example:

```bash
python generate_flights.py TOUR RPCT
```

**Folder Structure:**

```
TOURS/
└── RPCT/
    ├── legs.txt         # Required (same format as airports.txt, 1 leg per line)
    └── config.csv       # Required (see below)
```

**`legs.txt` example:**
```
MUHA-HAV,MMAA-ACA
MMAA-ACA,MMTP-TAP
...
```

**`config.csv` required columns:**

| flight_type | pilot_pay | notes                  | start_flight_number | start_date   | end_date     |
|-------------|------------|------------------------|----------------------|--------------|--------------|
| J           |            | Ruta del Pacifico 2025 | 8050                 | 2025-09-01   | 2025-10-30   |

- `flight_type`: Use `J` (passenger) or `F` (freighter)
- `start_flight_number`: First flight number in tour (default `8000`)
- `start_date` and `end_date`: Mandatory tour date range
- `pilot_pay` and `notes`: Optional

Each leg generates **1 flight** with sequential numbering and the tour code as `route_code`.

---

## 📌 Description

This Python script automates generation of flight schedules for phpVMS v7 based on ICAO-IATA route pairs.  
It calculates distances using the [AirportGap API](https://airportgap.com/) and assigns subfleets based on range.

---

## 📌 Features

- 🔁 Generates passenger & cargo roundtrip flights from route pairs
- 🧭 Tour mode: create sequential flights with custom pay, notes, date range
- 📏 Calculates flight distance using AirportGap API
- 🛫 Auto-assigns subfleets based on flight distance
- 🧠 Validates:
  - Duplicate lines in `airports.txt` or `legs.txt`
  - ICAO-IATA format (`AAAA-BBB`)
  - IATA-ICAO match via AirportGap API
- ⛔ Aborts on invalid lines
- 🗂️ Splits large flight sets into multiple CSVs

---

## ⚙️ Requirements

- Python 3.7+
- `requests` module (`pip install requests`)
- [AirportGap API token](https://airportgap.com/) (free)

---

## 📂 Folder Structure

```
project_root/
│
├── generate_flights.py
├── MUCC_CCC/
│   └── airports.txt
├── TOURS/
│   └── RPCT/
│       ├── legs.txt
│       └── config.csv
├── validated_airports.json (future)
└── README.md
```

---

## 🔑 Setup

1. Clone or download this repo
2. Install dependencies:

```bash
pip install requests
```

3. Export your AirportGap token:

- macOS/Linux:
```bash
export AIRPORT_GAP_TOKEN=your_api_token
```

- Windows:
```powershell
setx AIRPORT_GAP_TOKEN "your_api_token"
```

---

## ✅ Validations

- Duplicate lines in `airports.txt` or `legs.txt` → ❌ Abort
- Invalid line format (must be `AAAA-BBB`) → ❌ Abort
- ICAO-IATA mismatch via AirportGap API → ❌ Abort
- `config.csv` is **required** for TOURS
- `start_date` and `end_date` must be present

> Local cache of validated airports will be supported in a future version

---

## 📜 License

MIT License – Free for Virtual Airline use

---

## ✈️ Credits

- Developed for **Aerocaribbean Virtual Airline**
- Uses [AirportGap API](https://airportgap.com/)