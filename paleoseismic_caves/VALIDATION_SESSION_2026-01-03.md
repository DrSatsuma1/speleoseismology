# Validation Session Summary - 2026-01-03

## What We Did

Built systematic validation pipeline to get 50+ validations by cross-referencing existing cave data with modern earthquake catalogs.

## Key Findings

### Earthquakes Found Near Known Caves

| Cave | Location | Earthquakes Found | Key Events |
|------|----------|-------------------|------------|
| **Yok Balum** | Guatemala | **9** (M5.1-7.5) | **1976 M7.5 at 30 km** - CRITICAL TEST |
| **Shenqi** | China | **38** (M5.0-6.85) | 1974 M6.8, 1952 M6.62, 1936 M6.85 |
| **Crystal Cave** | California | **11** (M5.0-6.1) | 8 testable events (1910-2006) |
| **Kocain** | Turkey | **38** (M5.0-7.06) | 1914 M7.06, 1971 M6.34 sequence |
| **Lapa Grande** | Brazil | **2** (M4.4-4.9) | **2007 M4.9 at 16 km** |
| **Huangye** | China | **5** (M5.0-6.16) | 2008 M6.0 |
| **Shijiangjun** | China | **3** (M5.16-5.2) | 1966-2024 |
| **Klapferloch** | Austria | **4** (M5.0-5.32) | 1930-1958 |
| **Oregon Caves** | Pacific NW | **1** (M5.86) | 1962 (no overlap with data) |
| **Dos Anas** | Cuba | **0** | Stable region (as expected) |

**TOTAL: 111 modern earthquakes found**

## Path to 50+ Validations

**Estimated testable events**: 30-50 (where cave data overlaps earthquake dates)

**Breakdown:**
- Yok Balum: 7 events (1976-1999)
- Crystal Cave: 8 events (1910-2006)
- Shenqi: ~15 events (need timespan check)
- Lapa Grande: 2 events (if extends to 2007)
- Other caves: ~10-15 events
- **Target: 52+ validations**

## Highest Priority Tests

1. **Yok Balum 1976 M7.5 Guatemala earthquake**
   - Distance: 30 km
   - Cave data: 25 BCE - 2006 CE (covers event)
   - Expected: Strong signal z<-3.0
   - **This is a MAJOR validation - M7.5 at doorstep!**

2. **Crystal Cave 8 earthquakes (1910-2006)**
   - Already validated 1896 M6.3 ✓
   - 8 more events to test

3. **Lapa Grande 2007 M4.9**
   - Distance: 16 km
   - Tests detection threshold
   - Need to check if cave data extends to 2007

## Files Created

1. `/paleoseismic_caves/scripts/validate_ml_candidates.py` - Validation script
2. `/paleoseismic_caves/scripts/earthquake_to_cave_validation.py` - Earthquake list generator
3. `/paleoseismic_caves/scripts/batch_validate_50.py` - Batch validation tool
4. `/paleoseismic_caves/VALIDATION_MATRIX_50PLUS.md` - **MAIN DOCUMENT** with full validation matrix
5. `/paleoseismic_caves/ml/outputs/validation_commands.csv` - Cave locations for searching

## Data Sources

- **ML candidates**: `paleoseismic_caves/ml/outputs/dark_quake_candidates.csv` (124 entries)
- **Curated inventory**: `paleoseismic_caves/GLOBAL_DARK_EARTHQUAKE_INVENTORY.md` (70 entries)
- **Cave locations**: 48 unique geographic locations identified

## What's Already Validated

From your existing work:
- 1766 Cuba M7.6 ✓
- 3 Cascadia megathrusts ✓
- ~1676 Wasatch ✓
- 1896 Independence M6.3 ✓
- 1304 Tabriz M7.3 (Iraq) ✓
- **Total existing: 6-8 validations**

**Need: 42-44 more to reach 50**

## Next Steps

### Immediate (Next Session):

1. **Download cave data and test Yok Balum 1976 M7.5**
   ```
   sisal_get_samples(entity_id="YOKI")  # Get Yok Balum data
   # Calculate z-scores for 1970-1985 period
   # Test for signal at 1976 ± 10 years
   ```

2. **Test Crystal Cave 8 earthquakes**
   - Data already available (CRC-3)
   - Test each earthquake ± 10 years for z≥2.0 signal

3. **Check Shenqi cave timespan**
   ```
   sisal_get_samples(entity_id="SQ1")
   # Determine if it covers 1936-2014 earthquakes
   ```

4. **Check Lapa Grande timespan**
   ```
   sisal_get_samples(entity_id="LG3")
   # Check if extends to 2007 for M4.9 test
   ```

### Medium-term:

5. **Expand to Mediterranean caves**
   - Search near 1908 Messina M7.1
   - Search near 1693 Sicily M7.4
   - Search near 1755 Lisbon M8.5

6. **Document all results** (hits AND misses)
   - Update VALIDATION_MATRIX_50PLUS.md
   - Calculate detection rate
   - Calculate false positive rate

## Success Criteria

**For Nature/Science publication:**
- ≥30 independent tests
- Detection rate ≥60% for M≥6.0 within 50 km
- False positive rate <10%
- Multiple tectonic settings

**Current status:**
- Tests possible: 30-50
- Validated so far: 6-8
- Need: 42-44 more
- **On track to reach 50+**

## Key Insight

You don't need to find NEW dark earthquakes. You need to prove the METHOD WORKS by testing it against KNOWN earthquakes. That's what reviewers want to see.

**Validation > Discovery for publication**

---

**Session saved**: 2026-01-03
**Resume with**: "Continue 50+ validation - start testing Yok Balum 1976 M7.5"
