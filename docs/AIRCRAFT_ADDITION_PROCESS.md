# Aircraft Addition Process

This document describes the process for adding new aircraft to the fleet configuration.

## For Staff Members: How to Request a New Aircraft

### Step 1: Create an Issue

1. Go to the [Issues tab](https://github.com/aerocaribbeanva/phpvms-utilities/issues)
2. Click **"New Issue"**
3. Select **"🛩️ New Aircraft Request"**
4. Fill out all required fields

### Step 2: Validate Aircraft Specifications

**Required Information:**
- ICAO code (e.g., B738, A20N, B733F)
- Full aircraft name
- Type (Passenger/Freighter)
- Range in nautical miles (NM)
- MTOW (Maximum Takeoff Weight) in lbs
- OEW (Operating Empty Weight) in lbs
- Maximum payload in lbs
- SimBrief profile status

**Important:** All weights must be in **pounds (lbs)** as phpVMS stores weights in pounds in the database.

**Where to Find Specs:**

1. **Airport Planning Manuals (APM)** - Best source
   - Boeing: https://www.boeing.com/commercial/airports/plan_manuals.page
   - Airbus: https://www.airbus.com/en/airport-operations-and-technical-data/aircraft-characteristics

2. **Type Certificate Data Sheets**
   - FAA TCDS: https://www.faa.gov/aircraft/air_cert/design_approvals/tcds
   - Search by aircraft model

3. **Wikipedia** - Good starting point
   - Search for aircraft model (e.g., "Boeing 737-300")
   - Check "Specifications" section
   - Verify with other sources

4. **Airliners.net**
   - https://www.airliners.net/aircraft-data
   - Comprehensive database

### Step 3: Weight Validation Ranges

Use these guidelines to validate that weights are reasonable:

**Passenger Aircraft:**
- OEW typically 40-50% of MTOW
- Payload typically 20-30% of MTOW
- Range: 1,500 - 8,500 NM for commercial jets

**Freighter Aircraft:**
- OEW typically 45-55% of MTOW (heavier due to cargo floor)
- Payload typically 25-35% of MTOW (higher than passenger)
- Range: 2,000 - 4,500 NM (typically less than passenger variant)

**Validation Formula:**
```
MTOW = OEW + Max Payload + Max Fuel
```

If `OEW + Max Payload > MTOW`, something is wrong!

### Step 4: SimBrief Profile Requirements

**Standard SimBrief Profiles:**
- Most common aircraft already have profiles
- Check SimBrief dispatch: https://www.simbrief.com/system/dispatch.php

**Custom Profile Needed:**
- Uncommon variants (e.g., B733F)
- Heavily modified aircraft
- Freighter conversions without standard profiles

**Modified Profiles:**
- Based on existing variant (e.g., A339 → A339F)
- Key changes:
  - OEW adjustment (freighter is ~3-5% heavier)
  - Remove passenger cabin weight, add cargo deck
  - Update fuel capacity if changed
  - Adjust performance data

## For Administrators: Processing Aircraft Requests

### Step 1: Review the Issue

1. Check all required fields are filled
2. Verify source URL is legitimate
3. Validate weights are within expected ranges

### Step 2: Add to aircraft_config.json

Edit `aircraft_config.json` at repository root:

```json
{
  "B733F": {
    "range": "2400",
    "airlines": {
      "CRN": ["F"]
    }
  },
  "A339": {
    "range": "7200",
    "airlines": {
      "CRN": ["J"]
    }
  },
  "A339F": {
    "range": "4200",
    "airlines": {
      "CRN": ["F"]
    }
  }
}
```

**Format:**
- `range`: String, nautical miles
- `airlines`: Object with airline codes
- `CRN`: Aerocaribbean airline code
- `["J"]`: Passenger, `["F"]`: Freighter, `["J","F"]`: Both

### Step 3: Create SimBrief Profile (if needed)

For custom profiles:

1. Log into SimBrief admin panel
2. Navigate to Aircraft Types → Add New
3. Use validated weights from issue:
   - Operating Empty Weight (OEW)
   - Maximum Takeoff Weight (MTOW)
   - Maximum Payload
4. Set performance data:
   - Cruise speed (typical: M0.78-M0.82)
   - Fuel burn rates
   - Service ceiling
5. Save and test with sample flight plan

**Freighter Conversions:**
```
Passenger → Freighter adjustments:
- OEW: +3-5% (structural reinforcement, cargo handling)
- MTOW: Usually unchanged
- Payload: +20-40% (no passenger seats/amenities)
- Range: -15-25% (heavier empty weight)
```

### Step 4: Test & Commit

```bash
# 1. Add to aircraft_config.json
vim aircraft_config.json

# 2. Test locally (if you have routes)
cd flights-generator
python generate_flights.py LEGACY MUHA --yes

# 3. Commit
git add aircraft_config.json
git commit -m "Add B733F, A339, A339F to fleet configuration

- B733F: Boeing 737-300 Freighter (range: 2400 NM)
- A339: Airbus A330-900neo (range: 7200 NM)
- A339F: Airbus A330-900neo Freighter (range: 4200 NM)

Source: [URL from issue]
Closes #[issue-number]"

git push origin main
```

### Step 5: Automated Workflow

Once `aircraft_config.json` is pushed:

1. **generate-legacy-routes.yml** workflow triggers
2. Regenerates ALL legacy routes with new aircraft
3. Commits updated `ROUTES_IMPORT_FILES_SPLITTED/` files
4. New aircraft now available in all route subfleets (where range permits)

## Weight Validation Examples

### Example 1: Boeing 737-300F (B733F)

**Source:** Boeing 737 Airport Planning Manual

- MTOW: 62,820 kg (138,500 lb)
- OEW: 33,200 kg (73,200 lb)
- Max Payload: 18,200 kg (40,100 lb)
- Range: 2,400 NM (with max payload)

**Validation:**
```
OEW + Max Payload = 33,200 + 18,200 = 51,400 kg
51,400 < 62,820 ✅ Valid (allows ~11,420 kg fuel)
OEW/MTOW = 53% ✅ Normal for freighter
```

### Example 2: Airbus A330-900neo (A339)

**Source:** Airbus A330 Aircraft Characteristics

- MTOW: 251,000 kg (553,360 lb)
- OEW: 131,000 kg (288,800 lb)
- Max Payload: 52,000 kg (114,640 lb) ~287 pax
- Range: 7,200 NM (typical config)

**Validation:**
```
OEW + Max Payload = 131,000 + 52,000 = 183,000 kg
183,000 < 251,000 ✅ Valid (allows ~68,000 kg fuel)
OEW/MTOW = 52% ✅ Normal for wide-body passenger
```

### Example 3: A330-900neo Freighter (A339F - Theoretical)

**Source:** Estimated from A330-200F specifications

- MTOW: 233,000 kg (estimated, reduced from passenger)
- OEW: 134,000 kg (estimated, +2.3% vs passenger)
- Max Payload: 65,000 kg (increased cargo capacity)
- Range: 4,200 NM (with max payload)

**Validation:**
```
OEW + Max Payload = 134,000 + 65,000 = 199,000 kg
199,000 < 233,000 ✅ Valid (allows ~34,000 kg fuel)
OEW/MTOW = 58% ⚠️ Higher than typical, but acceptable for freighter
Payload increase: (65,000-52,000)/52,000 = 25% ✅ Reasonable
```

## Common Issues & Solutions

### Issue: Weight source doesn't match ICAO code

**Problem:** Found specs for B737-300, but need B733F (freighter)

**Solution:**
1. Find passenger variant specs
2. Apply freighter conversion factors:
   - OEW: +3-5%
   - MTOW: Usually same or -5%
   - Payload: +20-40%
3. Search for actual freighter specs to verify
4. Document assumptions in issue

### Issue: Multiple weight variants exist

**Problem:** Aircraft has multiple MTOW options (e.g., A330-900 has different variants)

**Solution:**
1. Use "typical" or "standard" configuration
2. Check which variant is most common in virtual airlines
3. Document which variant was chosen in commit message
4. Can always add additional variants later (e.g., A339H for high-weight)

### Issue: SimBrief profile doesn't exist

**Problem:** Custom aircraft not in SimBrief database

**Solution:**
1. Create custom SimBrief profile (requires admin access)
2. Use closest similar aircraft as base
3. Adjust weights and performance
4. Test with sample flight plans
5. Document profile ID in phpVMS aircraft configuration

## Reference Links

### Official Sources
- Boeing APM: https://www.boeing.com/commercial/airports/plan_manuals.page
- Airbus Aircraft Characteristics: https://www.airbus.com/en/airport-operations-and-technical-data/aircraft-characteristics
- FAA TCDS: https://www.faa.gov/aircraft/air_cert/design_approvals/tcds
- EASA TCDS: https://www.easa.europa.eu/en/document-library/type-certificates

### Databases
- Airliners.net: https://www.airliners.net/aircraft-data
- Wikipedia Aircraft Specs: https://en.wikipedia.org/wiki/List_of_aircraft
- SimBrief Aircraft Types: https://www.simbrief.com/system/dispatch.php

### Tools
- Unit Converter: https://www.unitconverters.net/ (kg ↔ lb, NM ↔ km)
- Range Calculator: https://www.greatcirclemap.com/

## Questions?

Open an issue with the label `question` or contact the fleet management team.
