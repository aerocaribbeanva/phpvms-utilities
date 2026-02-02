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

## Current Aircraft Requiring Custom Profiles

### B733F - Boeing 737-300 Freighter
**Status**: ✅ Added to aircraft_config.json
**SimBrief Profile**: ⚠️ Needs to be created

**Specifications** (validated):
- ICAO Code: B733F
- Full Name: Boeing 737-300 Freighter
- MTOW: 138,500 lbs
- OEW: 73,200 lbs
- Max Payload: 40,100 lbs
- Range: 2,400 NM (with max payload)
- Cruise Speed: M0.74-M0.78
- Type: Freighter conversion

**Base Aircraft for Profile**: Boeing 737-300 (B733 passenger variant)

**Key Modifications**:
- Remove passenger cabin configuration
- Add cargo floor reinforcement (+1,000 lbs to OEW estimated)
- Update payload capacity: 40,100 lbs (cargo only)
- Reduce range: 2,400 NM (vs 2,255 NM passenger)
- No passenger weight calculations needed

---

### A339 - Airbus A330-900neo
**Status**: ✅ Added to aircraft_config.json
**SimBrief Profile**: ⚠️ Needs to be created

**Specifications** (validated):
- ICAO Code: A339
- Full Name: Airbus A330-900neo
- MTOW: 553,360 lbs
- OEW: 288,800 lbs
- Max Payload: 114,640 lbs (~287 passengers)
- Range: 7,200 NM (typical configuration)
- Max Range: 7,530 NM (reduced payload)
- Cruise Speed: M0.82
- Type: Wide-body passenger

**Base Aircraft for Profile**: Airbus A330-300 (A333 closest match)

**Key Modifications**:
- Update to NEO engines (higher efficiency)
- Increased range: 7,200 NM (vs A333: 6,350 NM)
- Similar passenger capacity: ~287 pax (A333: similar)
- Update MTOW: 553,360 lbs (vs A333: varies)
- Update OEW: 288,800 lbs
- Cruise: M0.82 (same as A333)

---

### A339F - Airbus A330-900neo Freighter
**Status**: ✅ Added to aircraft_config.json
**SimBrief Profile**: ⚠️ Needs to be created

**Note**: This is a **theoretical/custom freighter conversion**. No official A339F variant exists.

**Specifications** (estimated from A330-200F + A339):
- ICAO Code: A339F
- Full Name: Airbus A330-900neo Freighter (Custom)
- MTOW: 513,780 lbs (reduced from passenger)
- OEW: 295,400 lbs (+2.3% vs A339 passenger)
- Max Payload: 143,300 lbs (cargo only)
- Range: 4,200 NM (with max payload)
- Cruise Speed: M0.82
- Type: Freighter conversion (custom)

**Base Aircraft for Profile**: A339 (custom profile above) or A330-200F (A33F)

**Key Modifications from A339 Passenger**:
- Remove all passenger seats/amenities (-18,000 lbs estimated)
- Add cargo floor and handling systems (+25,000 lbs estimated)
- Net OEW increase: +6,600 lbs (+2.3%)
- Update MTOW: 513,780 lbs (reduced for cargo operations)
- Increase payload: 143,300 lbs (vs 114,640 lbs passenger)
- Reduce range: 4,200 NM (vs 7,200 NM passenger)

---

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
ICAO Code: [Aircraft ICAO, e.g., B733F]
Name: [Full name, e.g., Boeing 737-300 Freighter]
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

**Example for B733F**:
```
OEW: 73,200 lbs
MTOW: 138,500 lbs
Max Payload: 40,100 lbs
MZFW: 73,200 + 40,100 = 113,300 lbs
Max Fuel: 138,500 - 113,300 = 25,200 lbs (structural limit)
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

**For Passenger Aircraft (A339)**:
```
Typical Seating:
- First Class: [seats, weight per pax: 220 lbs]
- Business Class: [seats, weight per pax: 220 lbs]
- Economy: [seats, weight per pax: 200 lbs]

Example A339: 287 pax economy → 287 * 200 = 57,400 lbs
```

**For Freighter Aircraft (B733F, A339F)**:
```
Passenger Capacity: 0
Cargo Capacity: [Max Payload in lbs]

Example B733F: 40,100 lbs cargo capacity
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
   SimBrief Type: B733F (or custom profile ID)
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

When converting a passenger aircraft to freighter (like A339 → A339F):

### Weight Adjustments
```
OEW Change: +2-5% (cargo floor, reinforcement)
MTOW Change: 0 to -10% (structural/operational limits)
Payload Change: +20-40% (no passenger amenities)
Range Change: -15-25% (heavier empty weight)
```

### Example Calculation (A339 → A339F):
```
Base (A339 Passenger):
- OEW: 288,800 lbs
- MTOW: 553,360 lbs
- Payload: 114,640 lbs (287 pax)
- Range: 7,200 NM

Freighter (A339F):
- OEW: 288,800 + 2.3% = 295,400 lbs (cargo floor added)
- MTOW: 553,360 - 7.2% = 513,780 lbs (reduced for cargo ops)
- Payload: 143,300 lbs (cargo only, +25%)
- Range: 7,200 - 41.7% = 4,200 NM (reduced with max cargo)
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

## Custom Profile URLs for Current Aircraft

Once created, document the SimBrief profile URLs here:

### B733F - Boeing 737-300 Freighter
- **SimBrief Profile URL**: *[To be created]*
- **Profile Type**: Custom Airframe
- **Base Aircraft**: Boeing 737-300 (if using existing) or custom configuration
- **Status**: ⚠️ Pending creation

### A339 - Airbus A330-900neo
- **SimBrief Profile URL**: *[To be created]*
- **Profile Type**: Custom Airframe
- **Base Aircraft**: Airbus A330-300 or custom configuration
- **Status**: ⚠️ Pending creation

### A339F - Airbus A330-900neo Freighter
- **SimBrief Profile URL**: *[To be created]*
- **Profile Type**: Custom Airframe
- **Base Aircraft**: A339 custom profile (above) or A330-200F
- **Status**: ⚠️ Pending creation

---

## Next Steps for Current Aircraft

1. **Create SimBrief custom airframe profiles** for B733F, A339, A339F using specifications in `AIRCRAFT_SIMBRIEF_VALIDATION.md`
2. **Generate shareable URLs** for each profile
3. **Test each profile** with sample flight plans (short, medium, max range)
4. **Document profile URLs** in this file and in phpVMS aircraft configuration
5. **Update aircraft addition issue** with profile links
6. **Notify flight operations team** when profiles are ready for use

## Questions?

For SimBrief profile creation assistance:
- Open an issue with label `simbrief`
- Contact the fleet management team
- Reference this guide and `AIRCRAFT_SIMBRIEF_VALIDATION.md`
