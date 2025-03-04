# Aircraft Data Processor Script

This Python script retrieves aircraft data from the SimBrief API, processes the data, and generates a structured JSON output that includes:
- Seat configurations (Economy, Business, First Class)
- Cargo capacity (based on aircraft's payload and passenger weight)
- Handling of unknown aircraft ICAOs and freighter aircrafts

## Features

- **Fetches Aircraft Data**: Pulls aircraft information from the SimBrief API using your API key.
- **Seat Distribution**: Adjusts Economy, Business, and First Class seats to match the default passenger capacity from SimBrief.
- **Cargo Capacity Calculation**: 
  - For freighter aircraft, the full payload is used as cargo.
  - For passenger aircraft, only the passenger weight is deducted from the cargo capacity, assuming luggage is part of the cargo.
- **Unknown Aircraft Logging**: Any aircraft ICAOs not found in the predefined cabin layouts or freighter lists are logged for review.
- **Date and Time**: Generated JSON filenames include the current date and time for easy identification.
  
## Requirements

- Python 3.x
- `requests` library (can be installed using `pip install requests`)

## Setup

1. **Set up the SimBrief API Key**:
   - Set your SimBrief API key as an environment variable:
     ```bash
     export SIMBRIEF_API_KEY="your_simbrief_api_key"
     ```

2. **Install Required Python Libraries**:
   If you don't have `requests` installed, you can install it using:
   ```bash
   pip install requests
   ```

## Script Execution

Run the script using the following command:

```bash
python process_aircraft_data.py
```

### What Happens When You Run the Script:
- The script will connect to the SimBrief API to fetch aircraft data.
- For each aircraft, the script:
  - Retrieves the aircraft's default passenger capacity.
  - Applies the correct seat distribution and adjusts based on the passenger capacity.
  - Calculates the cargo capacity by deducting passenger weight from the total payload (for passenger aircraft).
  - Logs unknown aircraft ICAOs (those not found in the predefined cabin layouts or freighter lists) to a separate file.
  - Creates a JSON file with all the processed aircraft data, including:
    - Seat configurations for Economy (`Y`), Business (`J`), and First Class (`F`).
    - Cargo capacity (`CGO`).
  
### Output Files:

- **Processed Aircraft Data**: A JSON file with the aircraft configurations, seat distributions, and cargo capacities. The file is named with the current date and time, e.g., `aircraft_data_20250304_123045.json`.
  
- **Unknown Aircrafts**: If any aircraft ICAO is not found in the cabin layout or freighter lists, it will be logged into a separate file named with the current date and time, e.g., `unknown_aircrafts_20250304_123045.json`.

## File Format

### Aircraft Data JSON
The output JSON file will have the following structure:
```json
{
  "A320": {
    "F": 0,
    "J": 12,
    "Y": 138,
    "CGO": 5000
  },
  "B737": {
    "F": 0,
    "J": 12,
    "Y": 112,
    "CGO": 4500
  },
  ...
}
```

### Unknown Aircraft JSON
If any unknown aircraft ICAOs are encountered, the script will log them to a separate JSON file with the following structure:
```json
[
  {
    "icao": "AN24",
    "default_pax": 40,
    "max_payload_lbs": 5500
  },
  {
    "icao": "C25C",
    "default_pax": 50,
    "max_payload_lbs": 6000
  },
  ...
]
```

## Notes

- The **cargo capacity** for freighter aircraft is calculated by using the full payload of the aircraft.
- For passenger aircraft, the cargo capacity is calculated by subtracting the **passenger weight** from the aircraft's maximum payload. This assumes that **luggage is part of the cargo**.
- Unknown ICAOs (aircrafts not found in the predefined cabin layouts or freighter lists) will be logged for later review and updates to the cabin layouts.

## License

This script is open-source and available under the MIT license. Feel free to contribute or use it for your own projects.
