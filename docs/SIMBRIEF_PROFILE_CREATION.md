# SimBrief Custom Profile Creation Guide

This guide explains how to create custom SimBrief aircraft profiles for aircraft not in the standard SimBrief database.

## Automated SimBrief Validation

**NEW**: The aircraft addition workflow automatically checks the SimBrief database!

When you submit an aircraft request via GitHub issue:
1. **First**: Workflow checks local `phpvms7-fares/aircraft_data_*.json` file (latest version)
2. **If found locally**: Extracts OEW, MZFW, Max Payload from local file
3. **Then**: Fetches https://www.simbrief.com/api/inputs.airframes.json for MTOW (if needed)
4. **If not found locally**: Checks SimBrief API for all weights
5. Validates provided weights against SimBrief data (warns if >5% difference)
6. If not found anywhere: PR indicates custom profile is needed
7. **Data source tracked**: Shows whether data came from `local`, `api`, or `local+api`

**Benefits**:
- Instant validation against official SimBrief data
- Prioritizes local aircraft data file (faster, includes custom aircraft)
- Falls back to SimBrief API for additional data or missing aircraft
- Reduces manual weight verification for standard aircraft
- Identifies which aircraft need custom profiles
- Ensures consistency with flight planning tools

## When Custom Profiles Are Needed

Custom SimBrief profiles are required when:
1. Aircraft is NOT in the SimBrief database (workflow will indicate this)
2. Using custom freighter conversions
3. Using heavily modified aircraft variants
4. Specific airline configurations differ significantly from standard profiles

**To check manually**: Visit https://www.simbrief.com/api/inputs.airframes.json and search for your aircraft ICAO code.

## SimBrief Profile Creation Steps

### Option 1: Create Custom Airframe (Recommended for Individual Aircraft)

SimBrief allows users to create custom airframes that can be shared and reused.

1. **Access SimBrief Dispatch**:
   - Go to https://dispatch.simbrief.com/
   - Log into your SimBrief account

2. **Navigate to Airframe Manager**:
   - Click on your profile/settings
   - Select "Manage Airframes" or "Create New Airframe"

3. **Create Custom Airframe**:
   - Select "Create New Airframe"
   - Choose base aircraft type or start from scratch
   - Configure all specifications (see detailed steps below)

4. **Share the Airframe**:
   - Once created, SimBrief generates a shareable URL
   - Example format: `https://dispatch.simbrief.com/airframes/share/XXXXXX_YYYYYYYYYYYY`
   - Reference: E190F custom profile example: https://dispatch.simbrief.com/airframes/share/1098250_1749676018149

5. **Document the Profile Link**:
   - Save the shareable URL in documentation
   - Add to aircraft addition issue/PR
   - Include in phpVMS aircraft configuration notes

### Option 2: Admin Panel (For System-Wide Aircraft Types)

1. Log into SimBrief admin account
2. Navigate to: **Aircraft Types** → **Add New**
3. Select appropriate base aircraft (if modifying existing)

### Step 2: Basic Information
```
ICAO Code: [Aircraft ICAO, e.g., B738F]
Name: [Full name, e.g., Boeing 737-800 Freighter]
Category: [Narrowbody/Widebody/Regional/etc.]
Engines: [Number and type]
```

### Step 3: Weight Configuration
**CRITICAL**: All weights must be in **pounds (lbs)** to match phpVMS database storage.

```
Operating Empty Weight (OEW): [lbs]
Maximum Takeoff Weight (MTOW): [lbs]
Maximum Landing Weight (MLW): [lbs]
Maximum Zero Fuel Weight (MZFW): [lbs]
Maximum Fuel Capacity: [lbs] or [gallons]
```

**Calculate MZFW** (if not provided):
```
MZFW = OEW + Max Payload
```

**Example (Freighter)**:
```
OEW: 91,300 lbs
MTOW: 174,200 lbs
Max Payload: 46,200 lbs
MZFW: 91,300 + 46,200 = 137,500 lbs
Max Fuel: 174,200 - 137,500 = 36,700 lbs (structural limit)
```

### Step 4: Performance Data
```
Cruise Speed: [Mach number, e.g., M0.78]
Max Speed: [Mach number]
Service Ceiling: [feet, e.g., 41,000]
```

**Typical Values by Aircraft Type**:
- Narrowbody (737, A320): M0.74-M0.78, 41,000 ft
- Widebody (A330, 787): M0.82-M0.85, 43,000 ft
- Regional (E175, CRJ): M0.70-M0.74, 37,000 ft

### Step 5: Fuel Burn Configuration
SimBrief calculates fuel burn based on:
- Aircraft weight
- Cruise altitude
- Cruise speed
- Engine type

**Reference Fuel Burns** (cruise, per hour):
- B737-300: ~5,000-6,000 lbs/hr
- A330-900: ~12,000-14,000 lbs/hr

You can copy fuel burn data from similar aircraft or let SimBrief estimate.

### Step 6: Passenger/Cargo Configuration

**For Passenger Aircraft**:
```
Typical Seating:
- First Class: [seats, weight per pax: 220 lbs]
- Business Class: [seats, weight per pax: 220 lbs]
- Economy: [seats, weight per pax: 200 lbs]

Example: 162 pax economy → 162 * 200 = 32,400 lbs
```

**For Freighter Aircraft**:
```
Passenger Capacity: 0
Cargo Capacity: [Max Payload in lbs]

Example: 46,200 lbs cargo capacity
```

### Step 7: Save and Test
1. Save the custom profile
2. **Document the SimBrief Profile ID** (e.g., custom_12345)
3. Test with sample flight plan:
   - Short route (500 NM)
   - Medium route (2,000 NM)
   - Max range route
4. Verify:
   - Fuel calculations are reasonable
   - Payload doesn't exceed limits
   - Flight time estimates are accurate

### Step 8: Document Profile in phpVMS
Once the SimBrief profile is created, update phpVMS aircraft configuration:

1. Log into phpVMS admin panel
2. Navigate to: **Fleet** → **Aircraft** → [Select Aircraft]
3. Update SimBrief Type field:
   ```
   SimBrief Type: [ICAO code or custom profile ID]
   ```
4. Save aircraft configuration

---

## Profile Validation Checklist

Before activating a custom SimBrief profile, verify:

- [ ] MTOW ≥ OEW + Max Payload + Min Fuel Reserve
- [ ] MZFW = OEW + Max Payload (approximately)
- [ ] OEW/MTOW ratio is reasonable:
  - Passenger: 40-50%
  - Freighter: 45-55%
- [ ] Range matches expected performance for payload
- [ ] Cruise speed matches aircraft specifications
- [ ] Fuel burn is comparable to similar aircraft
- [ ] Test flight plans generate without errors
- [ ] Payload capacity matches phpVMS aircraft configuration

---

## Freighter Conversion Guidelines

When converting a passenger aircraft to freighter:

### Weight Adjustments
```
OEW Change: +2-5% (cargo floor, reinforcement)
MTOW Change: 0 to -10% (structural/operational limits)
Payload Change: +20-40% (no passenger amenities)
Range Change: -15-25% (heavier empty weight)
```

### Example Calculation (Passenger → Freighter):
```
Base (Passenger):
- OEW: 174,200 lbs
- MTOW: 174,200 lbs
- Payload: 46,200 lbs (264 pax)
- Range: 3,400 NM

Freighter:
- OEW: 174,200 + 3% = 179,426 lbs (cargo floor added)
- MTOW: 174,200 - 5% = 165,490 lbs (reduced for cargo ops)
- Payload: 55,000 lbs (cargo only, +19%)
- Range: 3,400 - 20% = 2,720 NM (reduced with max cargo)
```

### Configuration Changes
1. **Remove**:
   - All passenger seats
   - Galleys and lavatories
   - Entertainment systems
   - Passenger cabin amenities

2. **Add**:
   - Reinforced cargo floor
   - Cargo handling systems
   - Additional cargo doors
   - Fire suppression systems

3. **Keep**:
   - Flight deck configuration
   - Engine performance
   - Avionics systems
   - Base aerodynamics

---

## Common SimBrief Profile Issues

### Issue: Fuel calculation errors
**Symptoms**: Flight plans show impossible fuel loads or "fuel exceeds capacity"

**Solutions**:
- Verify MTOW - MZFW = Max Fuel Capacity
- Check that OEW + Payload + Fuel ≤ MTOW
- Ensure fuel capacity in gallons matches pounds (Jet A: ~6.7 lbs/gal)

### Issue: Payload exceeds limits
**Symptoms**: SimBrief warns "payload exceeds maximum"

**Solutions**:
- Verify MZFW = OEW + Max Payload
- Check passenger weight assumptions (200-220 lbs/pax)
- Ensure cargo capacity doesn't exceed structural limits

### Issue: Range calculations incorrect
**Symptoms**: Aircraft can't reach destination or has excessive reserve fuel

**Solutions**:
- Verify cruise speed and altitude settings
- Check fuel burn rates against similar aircraft
- Ensure range specification matches max payload configuration

---

## Reference Data Sources

### Official Manufacturer Sources
- **Boeing APM**: https://www.boeing.com/commercial/airports/plan_manuals.page
- **Airbus Aircraft Characteristics**: https://www.airbus.com/en/airport-operations-and-technical-data/aircraft-characteristics

### Type Certificate Data
- **FAA TCDS**: https://www.faa.gov/aircraft/air_cert/design_approvals/tcds
- **EASA TCDS**: https://www.easa.europa.eu/en/document-library/type-certificates

### Aircraft Databases
- **Airliners.net**: https://www.airliners.net/aircraft-data
- **Wikipedia Aircraft Specs**: https://en.wikipedia.org/wiki/List_of_aircraft

### SimBrief Resources
- **SimBrief Dispatch**: https://dispatch.simbrief.com/
- **SimBrief API**: https://www.simbrief.com/api/inputs.airframes.json
- **SimBrief Forums**: https://forum.navigraph.com/c/simbrief/

---

## Questions?

For SimBrief profile creation assistance:
- Open an issue with label `simbrief`
- Contact the fleet management team
- Reference this guide
