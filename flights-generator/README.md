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

### ▶️ Triggering the Tour Generator via Pull Request

This repo auto-generates phpVMS tour flights **when you open or update a PR** that adds/changes a tour under `flights-generator/TOURS/XXXX/`. The workflow will **only run for non-draft PRs** and when both required files exist.

#### 1) Create the tour folder (4-char code)
Use an alphanumeric **4-character** tour code (e.g., `RPCT`, `PR22`) and add the two required files:

```
flights-generator/
└── TOURS/
    └── RPCT/
        ├── legs.txt      # Required (same format as airports.txt, 1 leg per line)
        └── config.csv    # Required (see columns below)
```

**`legs.txt` format (one leg per line; comments with `#` allowed):**
```
MUHA-HAV,MMAA-ACA
MMAA-ACA,MMTP-TAP
# This is a comment
MMTP-TAP,MSLP-SAL
```

**`config.csv` required columns (one row):**

| flight_type | pilot_pay | notes                  | start_flight_number | start_date | end_date   |
|-------------|-----------|------------------------|---------------------|------------|------------|
| J           |           | Ruta del Pacifico 2025 | 8050                | 2025-09-01 | 2025-10-30 |

- `flight_type`: `J` (passenger) or `F` (freighter)  
- `start_flight_number`: first number for the tour (defaults to `8000` if omitted/invalid)  
- `start_date`, `end_date`: required, `YYYY-MM-DD`  
- `pilot_pay`, `notes`: optional (`notes` accepts HTML; we wrap it in `<p>…</p>`)

> Each **leg** produces **one tour flight**; flights are numbered sequentially and use the tour code as `route_code`.

#### 2) (Optional) Run locally

```bash
# From repo root
python generate_flights.py TOUR RPCT
```

This validates `legs.txt` (checks duplicates), loads config, and writes generated CSVs to `flights-generator/TOURS/RPCT/…` including a `DS_Tour_RPCT_Legs.csv` for easy review.

#### 3) Commit and open a PR

```bash
git checkout -b feature/tour-RPCT
git add flights-generator/TOURS/RPCT/legs.txt flights-generator/TOURS/RPCT/config.csv
git commit -m "Add RPCT tour"
git push -u origin feature/tour-RPCT
# Open a PR (make sure it's NOT a draft)
```

- As soon as the PR is **Ready for review**, the workflow runs.  
- The workflow executes the generator with `--yes` (non-interactive) and **commits** any outputs back to your PR branch.

#### 4) Verify the results

- Check the PR **Checks** tab for the workflow logs.  
- The action commits generated files (e.g., `TOURS/RPCT/DS_Tour_RPCT_Legs.csv` and timestamped exports) to your PR.  
- If you push more changes to `legs.txt` or `config.csv`, the workflow reruns automatically.

---

#### Notes & Tips

- **Tour code** must be exactly **4 alphanumeric chars** (`[A-Za-z0-9]{4}`).  
- **Secrets:** The workflow uses the `AIRPORT_GAP_TOKEN` secret (via the `flight-gen` environment). For PRs from **forks**, a maintainer may need to approve the run so secrets are available.  
- **Caching:** Distances are cached in `distance_cache.json` to reduce API calls.  
- **Non-interactive CI:** The workflow passes `--yes` to avoid blocking on prompts.  
- **Rate limits:** If the API returns 429s, the script backs off and retries automatically.

#### Troubleshooting

- **“No tour changes detected.”** Ensure you modified files under `flights-generator/TOURS/XXXX/` and your PR isn’t a draft.  
- **“Skipping XXXX (missing legs.txt or config.csv)”** Make sure **both** files exist in that tour folder.  
- **“Duplicate entries found…”** Remove duplicate legs in `legs.txt`. Comments are fine, but duplicates abort generation.  
- **“Failed to fetch distance (401/403)”** Verify `AIRPORT_GAP_TOKEN` is configured in the `flight-gen` environment and available to the PR run (forks may require approval).  
- **Nothing committed back** Confirm the workflow is checking out the **PR head branch** and that files weren’t excluded by `.gitignore`. The workflow prints a file list before committing.


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
- 🗄️ Uses a cache for distances to minimize AirportGap API calls  

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