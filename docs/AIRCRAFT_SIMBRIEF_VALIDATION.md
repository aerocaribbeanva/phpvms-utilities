# Aircraft SimBrief Validation Results

Validation performed: 2026-02-02
SimBrief API endpoint: https://www.simbrief.com/api/inputs.airframes.json

## Summary

**Total aircraft in SimBrief database**: 14 aircraft types
- All are Airbus A320 family, Airbus A300 family, and Antonov variants
- **No Boeing 737 variants present**
- **No Airbus A330-900neo variants present**

## Validation Results

### B733F - Boeing 737-300 Freighter
**Status**: ❌ NOT FOUND in SimBrief database
**Action Required**: Create custom SimBrief profile

**Specifications** (from /tmp/aircraft_specs_lbs.md):
- Range: 2,400 NM (with max payload)
- MTOW: 138,500 lbs (62,820 kg)
- OEW: 73,200 lbs (33,200 kg)
- Max Payload: 40,100 lbs (18,200 kg)
- Cruise Speed: M0.74-M0.78
- Type: Freighter conversion
- Source: Boeing 737 Specifications

**Validation**:
```
OEW + Max Payload = 73,200 + 40,100 = 113,300 lbs
113,300 < 138,500 ✅ Valid (allows ~25,200 lbs fuel)
OEW/MTOW = 53% ✅ Normal for freighter
```

### A339 - Airbus A330-900neo
**Status**: ❌ NOT FOUND in SimBrief database
**Action Required**: Create custom SimBrief profile

**Specifications** (from /tmp/aircraft_specs_lbs.md):
- Range: 7,200 NM (typical, with 287 pax)
- Max Range: 7,530 NM (with reduced payload)
- MTOW: 553,360 lbs (251,000 kg)
- OEW: 288,800 lbs (131,000 kg)
- Max Payload: 114,640 lbs (52,000 kg) ~287 passengers
- Cruise Speed: M0.82
- Type: Wide-body passenger
- Source: Airbus A330neo Specifications

**Validation**:
```
OEW + Max Payload = 288,800 + 114,640 = 403,440 lbs
403,440 < 553,360 ✅ Valid (allows ~149,920 lbs fuel)
OEW/MTOW = 52% ✅ Normal for wide-body passenger
```

### A339F - Airbus A330-900neo Freighter
**Status**: ❌ NOT FOUND in SimBrief database (theoretical aircraft)
**Action Required**: Create custom SimBrief profile based on A339 passenger + A330-200F conversion factors

**Note**: No official A339F exists. This is a theoretical freighter conversion.

**Specifications** (from /tmp/aircraft_specs_lbs.md):
- Range: 4,200 NM (estimated with max payload)
- MTOW: 513,780 lbs (233,000 kg estimated, reduced from passenger)
- OEW: 295,400 lbs (134,000 kg estimated, +2.3% vs passenger)
- Max Payload: 143,300 lbs (65,000 kg)
- Cruise Speed: M0.82
- Type: Custom freighter conversion
- Source: Estimated from A330-200F + A339 passenger specifications

**Validation**:
```
OEW + Max Payload = 295,400 + 143,300 = 438,700 lbs
438,700 < 513,780 ✅ Valid (allows ~75,080 lbs fuel)
OEW/MTOW = 57% ⚠️ Higher than typical, but acceptable for freighter
Payload increase: (143,300-114,640)/114,640 = 25% ✅ Reasonable for freighter conversion
```

## SimBrief Aircraft Database Content

The following aircraft types are currently in SimBrief (as of 2026-02-02):

**Airbus A320 Family:**
- A318 (A318-100)
- A319 (A319-100)
- A320 (A320-200)
- A20N (A320-200N/A320neo)
- A321 (A321-200)

**Airbus A220 Family:**
- BCS1 (A220-100)
- BCS3 (A220-300)

**Airbus A300 Family:**
- A30B (A300B4-200)
- A306 (A300B4-600)
- A30F (A300F4-600R Freighter)
- A3ST (A300F4-608ST Super Transporter/Beluga)
- A310 (A310-304)

**Antonov:**
- A148 (An-148)
- A225 (An-225 Mriya)

## Custom SimBrief Profile Requirements

All three aircraft require custom SimBrief profiles to be created. The profiles should include:

### For B733F (Boeing 737-300 Freighter):
- Base aircraft: Boeing 737-300
- Modifications: Freighter conversion
- Key parameters:
  - OEW: 73,200 lbs
  - MTOW: 138,500 lbs
  - Max Payload: 40,100 lbs
  - Cruise: M0.74-M0.78
  - Range: 2,400 NM

### For A339 (Airbus A330-900neo):
- Base aircraft: Airbus A330-300 (similar size/performance)
- Modifications: NEO engines, updated performance
- Key parameters:
  - OEW: 288,800 lbs
  - MTOW: 553,360 lbs
  - Max Payload: 114,640 lbs (287 pax)
  - Cruise: M0.82
  - Range: 7,200 NM

### For A339F (Airbus A330-900neo Freighter):
- Base aircraft: A339 (custom profile above)
- Modifications: Freighter conversion from passenger variant
- Key parameters:
  - OEW: 295,400 lbs (+2.3% vs passenger)
  - MTOW: 513,780 lbs
  - Max Payload: 143,300 lbs (cargo only)
  - Cruise: M0.82
  - Range: 4,200 NM

## Next Steps

1. Create custom SimBrief profiles for all three aircraft
2. Document SimBrief profile IDs once created
3. Add aircraft to `aircraft_config.json` with profile ID references
4. Update phpVMS aircraft configuration to reference custom SimBrief profiles
5. Test flight planning with custom profiles

## References

- Boeing 737 Airport Planning Manual: https://www.boeing.com/commercial/airports/plan_manuals.page
- Airbus A330 Aircraft Characteristics: https://www.airbus.com/en/airport-operations-and-technical-data/aircraft-characteristics
- SimBrief API: https://www.simbrief.com/api/inputs.airframes.json
