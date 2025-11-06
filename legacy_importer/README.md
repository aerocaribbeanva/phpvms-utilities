# 📦 phpVMS v5 → v7 CSV Import Helper (Legacy)

This tool helps you **convert and massage phpVMS v5 CSV exports** into a format that phpVMS **v7** understands.  
It also includes helpers to **validate subfleets**, **export aircraft**, and **recalculate flight times & subfleets** for existing CSVs.

> Built for Aerocaribbean VA conventions but generic enough to adapt.

---

## ⚡ Quick Start

```bash
# Schedules (v5 → v7)
python legacy_v5_to_v7.py -f schedules_v5.csv -t schedules

# Aircraft (v5 → v7 subfleet CSV)
python legacy_v5_to_v7.py -f aircraft_v5.csv -t aircrafts

# Add/refresh subfleets & flight_time on an existing v7 CSV
python legacy_v5_to_v7.py -f exported-20250101-120000-schedules_v7.csv -t add-subfleets-v7

# Validate that aircraft types referenced exist in configured airline fleets and ranges
python legacy_v5_to_v7.py -f aircraft_v5.csv -t validate-subfleet
```

The script prints the **output file path** when finished (e.g. `exported-YYYYMMDD-HHMMSS-<input>.csv`).

---

## ✅ What It Supports

### 1) `-t schedules`  → Convert v5 Schedules to v7 CSV
- Accepts a **phpVMS v5 schedules CSV** (headers like: `code, flightnum, depicao, arricao, daysofweek, deptime, arrtime, distance, flighttype, price`).
- Normalizes and maps:
  - **Airline code**: `CRC` → `CRN` (via `special_code_to_airline`)
  - **Flight Type**: v5 `P`/`C` → v7 `J`/`F` (Passengers / Freighter)
  - **Days**: replaces Sunday `0` with `7` for v7
  - **Times**: strips trailing `UTC` and seconds if present (`HH:MM:SS` → `HH:MM`)
  - **Flight Time (minutes)**: computed as `arr_time - dpt_time` (absolute value, in minutes)
- Populates v7 columns:
  - `airline, flight_number, route_code, callsign, route_leg, dpt_airport, arr_airport, alt_airport, days, dpt_time, arr_time, level, distance, flight_time, flight_type, load_factor, load_factor_variance, pilot_pay, route, notes, start_date, end_date, active, subfleets, fares, fields, event_id, user_id`
- **Subfleets**: assigned by comparing route distance vs. each aircraft **range** (from `aircrafts_range_by_icao`) inside the airline fleet for the derived `flight_type`. Multiple matches are joined with `;`.

> Rows with unrecognized airline codes or unknown flight types are **skipped** and logged.

---

### 2) `-t aircrafts` → Export Aircraft to v7-style Subfleet CSV
- Accepts a **v5 aircraft CSV** (headers like: `icao, name, registration, weight, range, ...`)
- Filters aircraft to only those with registrations starting with **`AC-T`** or **`AC-C`** (adjust in code as needed).
- Writes a v7-ready aircraft CSV with columns:
  - `subfleet, iata, icao, hub_id, airport_id, name, registration, fin, hex_code, selcal, dow, zfw, mtow, mlw, status, simbrief_type`
- Detects **new or larger ranges** and prints a summary so you can update `aircrafts_range_by_icao` in the code.

---

### 3) `-t add-subfleets-v7` → Recalculate & Add Subfleets on Existing v7 CSV
- Recomputes **`flight_time`** if missing/incomplete using `dpt_time/arr_time` (or an average speed of **300 kt** when `arr_time` is empty).
- Re-derives **subfleets** using distance vs. `aircrafts_range_by_icao` for `J`/`F`.
- Drops flights with `flight_number` < **100**.
- Writes an `Updated CSV` into a **timestamped directory** and **splits** the file into chunks of 500 rows if needed.

---

### 4) `-t validate-subfleet` → Check Fleet Dictionaries
- Verifies each aircraft `type` in the provided CSV exists in either the **Passengers** or **Freighter** configured fleets:
  - `airline_subfleet_by_flight_type["CRN"]["J"]`
  - `airline_subfleet_by_flight_type["CRN"]["F"]`
- Also checks if the `type` is present in the **range dictionary** (`aircrafts_range_by_icao`).  
- Prints a list of **missing types** to help you update the dictionaries.

---

## 🧠 Built‑in Conventions & Mappings

- **Airline fallback/mapping**: `special_code_to_airline = {"CRC": "CRN"}`  
  Unknown airlines (not `CRN` and not in mapping) are **skipped**.
- **Flight type mapping** (v5 → v7): `P`→`J`, `C`→`F`.  
  If empty, `CRC` defaults to `C`, otherwise to `P`.
- **Time handling**: removes trailing `UTC` and seconds; expects `HH:MM`.
- **Days of week**: converts any `0` to `7`.
- **Active flag**: `active = "1"` for all exported flights.
- **Subfleet assignment**: every flight gets a `subfleets` string containing all subfleets whose **range** is strictly **greater** than the route distance.

> Update `airline_subfleet_by_flight_type` and `aircrafts_range_by_icao` to match your VA’s fleet.

---

## 📁 Input Expectations

### Schedules CSV (v5)
Minimum columns used by the tool:
```
code,flightnum,depicao,arricao,daysofweek,deptime,arrtime,distance,flighttype,price
```
- `distance` is a **number** (NM).  
- `deptime`/`arrtime` are `HH:MM` (or `HH:MM:SS`/`HH:MM UTC`).

### Aircraft CSV (v5)
Minimum columns used by the tool:
```
icao,name,registration,weight,range
```

---

## 🔧 Usage Examples

```bash
# Convert v5 schedules to a v7-ready CSV (with subfleets)
python legacy_v5_to_v7.py -f schedules_v5.csv -t schedules

# Export aircraft to a v7-style subfleet CSV
python legacy_v5_to_v7.py -f aircraft_v5.csv -t aircrafts

# Validate that aircraft referenced are in your configured fleet dicts
python legacy_v5_to_v7.py -f aircraft_v5.csv -t validate-subfleet

# Recompute subfleets and flight_time for an existing v7 CSV
python legacy_v5_to_v7.py -f exported-20250101-120000-schedules_v7.csv -t add-subfleets-v7
```

Resulting files are written next to your script as:
```
exported-YYYYMMDD-HHMMSS-<input>.csv
# or (when using add-subfleets-v7)
<YYYYMMDD-HHMMSS>/exported-YYYYMMDD-HHMMSS-<input>.csv
```

---

## 🧩 Tips & Gotchas

- If some rows are **skipped**:
  - Unknown airline code (not `CRN` and not in `special_code_to_airline`)
  - Unknown flight type (not `P` or `C`)
- If `arr_time` is empty during `add-subfleets-v7`, the script will estimate arrival time using **300 kt** average.
- Subfleets are included when **range > distance**. Adjust the comparison if your policy differs.
- The script deletes flights with `flight_number < 100` during `add-subfleets-v7`.
- All times are treated as **local** strings; no timezone conversions are performed.

---

## 🛠 Customization Pointers

- **Map more airline codes** in `special_code_to_airline`
- **Change fleet membership** in `airline_subfleet_by_flight_type`
- **Tweak ranges** in `aircrafts_range_by_icao` (script will warn if it detects higher ranges in the aircraft CSV)
- **Registration filters** in `import_aircraft` (defaults to `AC-T` / `AC-C`)

---

## 📜 License

MIT — Use and modify freely for your Virtual Airline.

---

## 👤 Credits
- Script & docs: Aerocaribbean VA tooling
- Tested with: phpVMS v5 exports and v7 CSV import format