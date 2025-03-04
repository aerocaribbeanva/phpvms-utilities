
# SimBrief Aircraft Data Processing Script

This Python script interacts with the SimBrief API to fetch aircraft data and processes it for use in aircraft layouts and cargo capacity calculations. It adjusts seat distributions for different aircraft types and calculates the cargo capacity based on the aircraft's maximum payload and passenger data. It also identifies unknown ICAOs that are not found in the cabin layout dictionary and prints them for further updates.

## Features

- Fetches aircraft data from SimBrief API.
- Adjusts seat configuration for Economy, Business, and First Class according to the aircraft's default passenger capacity.
- Calculates cargo capacity, including the cargo fare "CGO" value.
- Identifies and logs unknown ICAOs for review.
- Supports freighter aircraft with adjusted calculations for cargo only.

## Requirements

- Python 3.6 or higher.
- Required Python libraries:
  - `requests`
  - `json`
  - `os` (for environment variable handling)
  
You can install the necessary Python libraries using pip:

```bash
pip install requests
```

## Setup

1. **Get your SimBrief API Key**:
   - To use the SimBrief API, you will need an API key. If you don’t have one, you can get it from the [SimBrief API](https://www.simbrief.com) page.
   
2. **Set your API key**:
   - It's recommended to store your API key in an environment variable for security.
   - On Linux or MacOS, you can set it like this:
   
     ```bash
     export SIMBRIEF_API_KEY="your_api_key_here"
     ```
   
   - On Windows, use this command in the Command Prompt:
   
     ```bash
     set SIMBRIEF_API_KEY="your_api_key_here"
     ```

3. **Run the script**:
   - Once your environment variable is set, run the script by executing:
   
     ```bash
     python simbrief_aircraft_processing.py
     ```

## How it Works

1. **Fetching SimBrief Data**: 
   - The script sends a request to the SimBrief API, fetching aircraft data in JSON format.

2. **Processing the Data**:
   - The script checks whether each aircraft has a known cabin layout from the predefined `cabin_layouts` dictionary.
   - If the aircraft has a known layout, the script adjusts the number of Economy, Business, and First Class seats to match the aircraft's default passenger capacity from SimBrief.
   - If the aircraft is a freighter (as identified in the `freighter_icaos` dictionary), it calculates cargo capacity based only on the maximum payload, skipping passenger seat configurations.

3. **Cargo Calculation**:
   - The cargo capacity for each aircraft is calculated. If it’s a freighter, it takes the full maximum payload as cargo. For passenger aircraft, the weight of passengers and their luggage is subtracted from the maximum payload to determine available cargo space.

4. **Output**:
   - The final data, including adjusted seat configurations and cargo capacity, is saved to a JSON file named `aircraft_data.json`.
   - If any unknown ICAOs are found, the script will print them along with their passenger and payload details for manual review.

## Output Example

The `aircraft_data.json` file will contain a structure like this:

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
    "CGO": 4000
  },
  ...
}
```

Where:
- `"F"` is the number of First Class seats.
- `"J"` is the number of Business Class seats.
- `"Y"` is the number of Economy Class seats.
- `"CGO"` is the cargo capacity in pounds.

## Updating Unknown ICAOs

If any unknown ICAOs are encountered, they will be printed to the console for further review. You can manually update the cabin layout dictionary to include the missing aircrafts.

## Can You Make the Code Public?

Yes, you can definitely upload this code to a public GitHub repository. However, **DO NOT** upload your actual API key to GitHub or any public repository. Instead, ensure that the API key is stored securely, such as in an environment variable, to prevent unauthorized access.

## License

This script is free to use and modify. You are welcome to fork or contribute to it on GitHub.
