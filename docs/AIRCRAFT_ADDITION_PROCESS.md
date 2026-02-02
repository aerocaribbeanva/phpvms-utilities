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

### Automated Workflow (Recommended)

The repository includes an automated workflow that processes aircraft requests from GitHub issues.

**How it works:**
1. Staff member creates issue using "🛩️ New Aircraft Request" template
2. GitHub Actions workflow automatically triggers when issue is labeled with `aircraft`
3. Workflow validates all specifications:
   - ICAO code format (3-4 characters)
   - Range is numeric
   - Flight type is valid
   - Weight validation: OEW + Payload ≤ MTOW
4. **Workflow checks SimBrief database** (NEW):
   - **First**: Checks local `phpvms7-fares/aircraft_data_*.json` file (automatically finds latest version)
   - **If found locally**: Extracts OEW, MZFW, and Max Payload from local file
   - **Then**: Fetches https://www.simbrief.com/api/inputs.airframes.json for MTOW (if needed)
   - **If not found locally**: Checks SimBrief API for all weights
   - Validates provided weights against SimBrief data (warns if >5% difference)
   - If not found anywhere: flags that custom SimBrief profile is needed
   - **Data sources tracked**: `local`, `api`, or `local+api` (shown in PR)
5. Workflow checks if aircraft already exists in `aircraft_config.json`
6. If valid and new:
   - Creates feature branch: `feat/add-aircraft-{ICAO}-{issue-number}`
   - Adds aircraft to `aircraft_config.json` (alphabetically sorted)
   - Commits changes with detailed specifications and SimBrief validation
   - Creates Pull Request with validation summary including SimBrief data
   - Comments on original issue with PR link and SimBrief status

**Administrator Actions:**
1. Review the automatically created PR
2. Check SimBrief validation results in PR:
   - ✅ If found in SimBrief: weights are validated automatically
   - ⚠️ If NOT found: custom SimBrief profile must be created
3. Verify any weight difference warnings (>5% from SimBrief)
4. Verify specifications are correct
5. Merge PR to activate aircraft in all routes
6. Merging triggers automatic regeneration of legacy routes

**Workflow File**: `.github/workflows/add-aircraft-from-issue.yml`

### Manual Process (Alternative)

If the automated workflow fails or you prefer manual addition:

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

**Important**: Maintain alphabetical order by ICAO code

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

### Step 5: Automated Workflow Integration

Once `aircraft_config.json` is updated (via automated workflow PR merge or manual commit):

1. **generate-legacy-routes.yml** workflow automatically triggers
2. Regenerates ALL legacy routes with new aircraft included
3. Commits updated `ROUTES_IMPORT_FILES_SPLITTED/` files to the PR/branch
4. New aircraft now available in all route subfleets (where range permits)

**Workflow Trigger**: Any change to `aircraft_config.json` triggers regeneration of:
- All legacy routes in `flights-generator/_LEGACY/*/routes.csv`
- Split files in `flights-generator/_LEGACY/*/ROUTES_IMPORT_FILES_SPLITTED/`

This ensures all routes are immediately updated with the new aircraft.

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

## Automated Workflow Troubleshooting

### Workflow doesn't trigger

**Problem**: Issue created but no PR is generated

**Solutions**:
1. Ensure issue has the `aircraft` label
2. Check [workflow runs](https://github.com/aerocaribbeanva/phpvms-utilities/actions) for errors
3. Verify all required fields in issue are filled
4. Check that issue was created with the template (not blank issue)

### Weight validation fails

**Problem**: Workflow fails with "Weight validation failed" error

**Solution**:
```
OEW + Max Payload must be ≤ MTOW

If failing:
1. Verify MTOW is correct (check source)
2. Verify OEW is correct (check source)
3. Verify Max Payload is correct
4. Check for typos (commas instead of numbers, missing digits)
```

### Aircraft already exists

**Problem**: Workflow comments "Aircraft already exists"

**Solution**:
1. Check `aircraft_config.json` for existing entry
2. If updating existing aircraft, close issue and manually edit config
3. If duplicate request, close issue as duplicate

### PR created but legacy routes not regenerated

**Problem**: Aircraft added but routes not updated

**Solution**:
1. Check if PR was merged to `main` branch
2. Verify `generate-legacy-routes.yml` workflow ran after merge
3. Check workflow logs for errors
4. Manually trigger workflow if needed: Actions → Generate Legacy Routes → Run workflow

### SimBrief profile missing

**Problem**: Aircraft added but no SimBrief profile URL

**Solution**:
1. Create custom SimBrief profile (see `SIMBRIEF_PROFILE_CREATION.md`)
2. Update issue or PR with profile URL
3. Document URL in phpVMS aircraft configuration
4. Test profile with sample flight plans

## Questions?

Open an issue with the label `question` or contact the fleet management team.
