# US Dark Earthquake Database Verification Plan

**Date**: 2026-01-03
**Objective**: Recheck all US "dark" earthquake candidates against updated fault databases
**Trigger**: Discovery that USGS Quaternary Fault Database is 7-27 years outdated and missing significant fault segments

---

## Problem Statement

The USGS Quaternary Fault Database was found to be incomplete:
- **Last update**: Some sections from 1999 (27-year lag)
- **Coverage gaps**: 41% of Newport-Inglewood-Rose Canyon offshore segment unmapped
- **Methodology**: Reflects 1990s interpretations, not modern marine geophysics

This means "dark earthquakes" attributed to "no mapped fault" may actually be on **known but unmapped-in-USGS** faults.

---

## US Dark Earthquake Inventory

### From Speleothems (SISAL v3)

| Event | Cave | Date | Z-Score | Recovery (yr) | Current Attribution | Status |
|-------|------|------|---------|---------------|---------------------|--------|
| **1741** | Crystal Cave (Sequoia) | 1734-1749 CE | +2.84 | 15 | Kern Canyon / Sierra Nevada Frontal | **NEEDS VERIFICATION** |
| **930 CE** | Oregon Caves | ~930 CE | -1.37 | 18 | ? | **LOW PRIORITY** (weak signal) |
| **~1676** | Minnetonka Cave | 1675-1678 CE | +2.63 | 3 | Wasatch Fault (Nephi segment) | **NEEDS VERIFICATION** |

### From Tree Rings

| Event | Proxy Sites | Date | Signal | Current Attribution | Status |
|-------|-------------|------|--------|---------------------|--------|
| **1580** | Fort Ross + Gualala | 1580 ± 3 yr | z=-3.25, -2.13 (divergence) | San Andreas (Carrizo 1540-1630) | **NEEDS VERIFICATION** |
| **1825** | Fort Ross + Gualala | 1825 ± 1 yr | z=-4.43 (Gualala massive) | San Andreas? | **NEEDS VERIFICATION** |
| **1741** | Mt. Laguna + Palomar | 1741 ± 1 yr | z=-1.09, -1.10 (convergent) | Rose Canyon Fault | **NEEDS REVISION** (see audit) |

---

## Modern Fault Databases for US Verification

### National / Regional

| Database | Coverage | Update Frequency | Access | Priority |
|----------|----------|------------------|--------|----------|
| **SCEC CFM v6.0** | Southern California | 2020s | https://www.scec.org/research/cfm | **PRIMARY** for CA |
| **GEM Global Active Faults** | Worldwide | 2018+ updates | https://github.com/GEMScienceTools/gem-global-active-faults | **SECONDARY** |
| **CGS Fault Database** | California | Ongoing | https://maps.conservation.ca.gov/cgs/fam/ | **PRIMARY** for CA |
| USGS Quaternary Faults | US-wide | **1990s-2000s** | https://www.usgs.gov/quaternary-faults | ⚠️ **OUTDATED** |

### State Geological Surveys

| State | Survey | Fault Database | Access |
|-------|--------|----------------|--------|
| **California** | CGS | Fault Activity Map (FAM), FER series | https://maps.conservation.ca.gov/ |
| **Utah** | UGS | Quaternary Fault Database | https://ugspub.nr.utah.gov/ |
| **Oregon** | DOGAMI | Active Fault Database | https://www.oregongeology.org/ |

### Published Studies (Post-2010)

These supersede government databases for specific regions:

| Region | Key Study | Year | Faults Mapped |
|--------|-----------|------|---------------|
| **Rose Canyon** | Sahakian et al. | 2017 | Offshore segment (marine seismic) |
| **Rose Canyon** | CGS FER 265 | 2021 | Updated onshore/offshore geometry |
| **San Andreas (Carrizo)** | Akciz et al. (JGR) | 2009 | Paleoseismic chronology |
| **Wasatch** | DuRoss et al. (BSSA) | 2016 | Nephi segment paleoseismic |
| **Sierra Nevada** | Unruh et al. | 2003-2018 | Sierra Nevada Frontal Fault Zone |

---

## Verification Protocol

For each US "dark" earthquake candidate:

### Step 1: Check SCEC CFM (if in Southern California)
- Download CFM v6.0 shapefile
- Buffer cave/proxy location by 50 km
- Identify all faults within detection threshold
- Record fault names, distances, geometry

### Step 2: Check State Geological Survey
- California: CGS Fault Activity Map + FER series
- Utah: UGS Quaternary Fault Database
- Oregon: DOGAMI Active Fault Database

### Step 3: Literature Search (Google Scholar)
- Search: `[fault name] paleoseismic [year range]`
- Filter: Publications 2010-2025
- Check for updated fault mapping, slip rates, paleoseismic chronology

### Step 4: Cross-Reference with Paleoseismic Studies
- Check if event date overlaps published trench studies
- Compare dating methods (radiocarbon vs. U-Th vs. tree ring)
- Determine if event is "dark" (unknown) or "prehistoric" (pre-documented on known fault)

### Step 5: Classification Decision

| Condition | Classification | Label |
|-----------|----------------|-------|
| Event matches known fault + published paleoseismic date | **VALIDATED** (not dark) | "Speleothem detection of known paleoseismic event" |
| Event on known fault (SCEC/CGS) but NO prior paleoseismic date | **PRE-HISTORICAL** | "Undocumented earthquake on mapped fault" |
| Event in region with NO mapped faults (after CFM + literature search) | **DARK EARTHQUAKE** | "Earthquake on unmapped structure" |
| Event predates all records, fault unknown | **PREHISTORIC** | "Prehistoric earthquake, source uncertain" |

---

## Detailed Verification Plans

### 1. Crystal Cave 1741 (Sequoia)

**Location**: 36.59°N, 118.82°W

**Current claim**: "Dark earthquake" on Kern Canyon or Sierra Nevada Frontal Fault

**Databases to check**:
- [ ] SCEC CFM v6.0 - Check for Sierra Nevada fault traces
- [ ] CGS Fault Activity Map - Kern Canyon Fault status
- [ ] Unruh et al. (2003, 2018) - Sierra Nevada Frontal Fault Zone mapping
- [ ] USGS Quaternary Faults - Baseline comparison

**Key questions**:
1. Is Kern Canyon Fault in SCEC CFM? (May not be - outside main Southern California focus)
2. Is Sierra Nevada Frontal Fault Zone mapped as active Quaternary fault?
3. Are there published paleoseismic studies for either fault?
4. Distance from cave to nearest mapped fault?

**Expected outcome**:
- If Kern Canyon IS in CGS but NOT in USGS → Database gap (like Rose Canyon)
- If NO fault in any database → Truly dark
- If fault IS mapped → Reclassify as "pre-Spanish earthquake on known fault"

---

### 2. Rose Canyon 1741 (San Diego)

**Status**: Already audited in DARK_EARTHQUAKE_AUDIT.md

**Finding**: Fault IS mapped in SCEC CFM, Sahakian et al. (2017), CGS FER 265 (2021)

**Required action**:
- [x] Identified in audit (COMPLETE)
- [ ] Update ROSE_CANYON_1741_DARK_EARTHQUAKE.md with revised classification
- [ ] Change framing from "dark earthquake (no fault)" to "pre-Spanish earthquake (known fault)"

---

### 3. San Andreas 1580 & 1825 (Tree Rings)

**Current claim**: "Probable dark earthquakes" based on tree ring suppression

**Issue**: San Andreas IS a known fault. These can't be "dark" in the sense of "unknown fault"

**Databases to check**:
- [ ] SCEC CFM v6.0 - San Andreas Fault geometry
- [ ] Akciz et al. (2009) - Carrizo Plain paleoseismic dates
- [ ] Biasi & Weldon (2006) - SAF slip rate compilation
- [ ] Tree ring literature - See if 1580/1825 previously detected

**Key questions**:
1. Do Carrizo Plain dates CONFIRM these events? (1580 overlaps 1540-1630, but that's WIDE)
2. Are there other paleoseismic trenches with matching dates?
3. Should we call these "dark" or "prehistoric"?

**Expected outcome**: Reclassify as "prehistoric San Andreas earthquakes" - NOT "dark" (fault is known)

---

### 4. Minnetonka Cave ~1676 (Utah/Idaho)

**Location**: Near Bear Lake, Utah/Idaho border

**Current claim**: Correlates with Wasatch Fault (Nephi segment) paleoseismic event

**Databases to check**:
- [ ] UGS Quaternary Fault Database
- [ ] DuRoss et al. (2016) - Wasatch Nephi segment paleoseismic
- [ ] USGS Quaternary Faults - Wasatch Fault System

**Key questions**:
1. What is the radiocarbon date range for DuRoss event? (1048-1448 CE or 1293-1719 CE)
2. Does 1676 fall within uncertainty?
3. Distance from cave to Nephi segment?

**Expected outcome**: If date matches DuRoss → **VALIDATED** (not dark). If outside range → May be separate event on Wasatch or other fault.

---

### 5. Oregon Caves 930 CE (Low Priority)

**Signal**: Weak (z=-1.37), short recovery (0 yr)

**Current claim**: None - just flagged by ML

**Databases to check**:
- [ ] DOGAMI Active Fault Database (Oregon)
- [ ] Cascadia paleoseismic chronology (Goldfinger 2012)
- [ ] USGS Quaternary Faults - Coastal Oregon

**Expected outcome**: Likely CLIMATIC (weak signal, no recovery). Not a priority for verification.

---

## Timeline & Priorities

### Immediate (Next Session)
1. **Download SCEC CFM v6.0** for Southern California
2. **Verify Crystal Cave 1741** - Most significant US cave-based dark EQ candidate
3. **Update Rose Canyon 1741** - Change classification per audit findings

### High Priority (This Week)
4. **Verify San Andreas 1580/1825** - Clarify "dark" vs "prehistoric" terminology
5. **Verify Minnetonka ~1676** - Cross-check with DuRoss paleoseismic

### Lower Priority
6. Oregon Caves 930 CE (weak signal)
7. Systematic review of ALL tree ring sites for additional candidates

---

## Expected Outcomes

### Likely Reclassifications

| Event | Current Label | Expected New Label | Reasoning |
|-------|---------------|-------------------|-----------|
| Rose Canyon 1741 | "Dark earthquake" | "Pre-Spanish earthquake on mapped fault" | Fault IS in SCEC CFM, Sahakian 2017 |
| San Andreas 1580/1825 | "Dark earthquakes" | "Prehistoric San Andreas earthquakes" | SAF is world-famous fault, not "dark" |
| Crystal Cave 1741 | "Dark earthquake" | **TBD** | Depends on CGS/SCEC CFM verification |
| Minnetonka 1676 | "Dark earthquake" | **Possibly VALIDATED** | May match DuRoss paleoseismic |

### Revised "Dark Earthquake" Count for US

**Current claim**: 3-4 US dark earthquakes (1741 Rose Canyon, 1741 Crystal, 1580/1825 SAF)

**Expected after verification**:
- **0-1 true "dark"** (only if Crystal Cave has no mapped source)
- **2-3 "pre-historical"** (Rose Canyon, SAF events - known faults, pre-Spanish)
- **1 possible "validated"** (Minnetonka matches DuRoss)

### Impact on Publication

This is NOT a negative finding. It's actually BETTER science:

**Stronger framing**:
- "Speleothem paleoseismology **validates** existing paleoseismic chronologies" (Minnetonka, SAF)
- "Extends earthquake catalogs into **pre-historical period**" (1741 pre-Spanish events)
- "May reveal **true dark earthquakes** where no fault is mapped" (Crystal Cave TBD)

**Weaker framing**:
- "Discovers many dark earthquakes with unknown sources" ← Only if we don't check databases properly

---

## Next Steps

1. Download SCEC CFM v6.0
2. Create verification script to:
   - Buffer cave locations
   - Intersect with fault traces
   - Calculate distances
   - Output fault candidates
3. Document findings in regional files
4. Update CLAUDE.md with revised statistics
5. Update PAPER_2_DARK_EARTHQUAKES.md with corrected classifications

---

**Status**: PLAN CREATED
**Owner**: Claude Code
**Next action**: Download SCEC CFM and verify Crystal Cave 1741
