# Northern Expansion Analysis Plan
## Testing if Database Gap is Systematic or Isolated

**Date**: 2026-01-02
**Status**: Planning phase
**Motivation**: Verify if NIFZ/RCFZ gap (85 km, 41% unmapped) is unique or part of systematic offshore fault database deficiency

---

## Hypothesis to Test

**H0 (Null)**: The 85 km Rose Canyon gap is an isolated case specific to complex tectonic transition between LA Basin and San Diego

**H1 (Alternative)**: USGS Quaternary Fault Database systematically underrepresents offshore fault segments across Southern California

**Test strategy**: Apply identical microseismicity overlay analysis to adjacent offshore fault systems

---

## Phase 1: Palos Verdes Fault (Offshore LA/Long Beach)

### Target Fault System
**USGS Fault ID**: 86 (Palos Verdes fault zone)

**Geographic extent**:
- North: Santa Monica Bay (~34.0°N)
- South: San Pedro Bay to Dana Point (~33.45°N)
- Total length: ~100 km (primarily offshore)

**Tectonic setting**:
- Right-lateral strike-slip
- Part of Inner Continental Borderland (ICB) deformation
- Passes within 8 km of Ports of LA/Long Beach ($500B/year cargo)

**Hazard significance**:
- M7.0-7.3 potential (comparable to NIFZ/RCFZ)
- Submarine landslide + tsunami risk (1933 Long Beach earthquake analog)
- Direct threat to:
  - Ports of LA/Long Beach (40% of US containerized imports)
  - Oil/gas infrastructure (numerous offshore platforms)
  - 10+ million people in greater LA metro

### Data Sources

**USGS Database**:
- Download fault sections for ID 86
- Check section count and geographic coverage
- Identify "less well defined" segments

**Microseismicity**:
- USGS catalog (1980-2025), region: 33.4°N-34.1°N, -119.0°W to -117.8°W
- M≥1.0 events
- Depth filter: 0-25 km

**DEM/Bathymetry**:
- USGS 3DEP (onshore)
- NOAA bathymetry (offshore LA shelf)
- Multibeam data if available

**Published mapping**:
- Ryan et al. (2009) - Marine seismic imaging of Palos Verdes
- Freeman et al. (2010) - Offshore fault geometry
- SCEC CFM v5.3 - 3D fault model

### Analysis Pipeline

1. **Download USGS database sections for Fault ID 86**
   - Extract to GeoJSON
   - Calculate total mapped length
   - Identify section boundaries

2. **Download microseismicity** (same parameters as Rose Canyon)
   - 1980-2025 USGS catalog
   - Filter to study region

3. **Orphan earthquake analysis**
   - Calculate distance from each earthquake to nearest mapped fault
   - Thresholds: 3 km, 5 km
   - Calculate percentage in "unmapped" zones

4. **Compare to published geometry**
   - Overlay SCEC CFM traces
   - Identify gaps between USGS database and modern mapping

5. **Create comparison figures**
   - 4-panel layout (same as Rose Canyon analysis)
   - Highlight any gaps with seismicity concentration

### Expected Outcome

**If H0 (isolated case)**:
- Palos Verdes fault fully mapped in USGS database
- Low orphan earthquake percentage (<10%)
- Good agreement between USGS and modern studies

**If H1 (systematic problem)**:
- Similar gap pattern (offshore segments "less well defined")
- High orphan earthquake percentage (>30%)
- Database reflects legacy pre-2000 interpretations

---

## Phase 2: Northern NIFZ Segments (LA Basin)

### Target Sections
**USGS Fault ID 127** (same system as Rose Canyon):
- Section 127a: Newport-Inglewood North Branch (Beverly Hills to Dominguez Hills)
- Section 127b: Newport-Inglewood South Branch (Dominguez Hills to Newport Beach)

**Purpose**: Verify that onshore urban portions are well-mapped (control case)

### Analysis

1. Extract sections 127a and 127b from database
2. Overlay LA Basin microseismicity
3. Calculate orphan percentage
4. **Expected result**: Low orphan % because onshore + oil field mapping

**Why this matters**: Confirms our methodology is sound - onshore faults should show good database coverage

---

## Phase 3: Central California Offshore Faults

### Target: Hosgri Fault (Offshore San Luis Obispo)

**USGS Fault ID**: 55

**Critical infrastructure**:
- **Diablo Canyon Nuclear Power Plant** (2.3 GW, recently relicensed)
- Located 5 km from mapped Hosgri Fault
- Offshore continuation of fault poorly constrained

**Hypothesis**: If USGS systematically under-maps offshore faults, Hosgri may show similar gaps despite proximity to nuclear facility

### Analysis

1. Download USGS database for Fault ID 55
2. Check section coverage (onshore vs. offshore)
3. Overlay microseismicity (1980-2025)
4. Compare to:
   - PG&E seismic surveys (required for nuclear licensing)
   - USGS professional papers on Hosgri geometry
   - SCEC CFM representation

**Red flag scenario**: If database gap exists near active nuclear plant, this becomes a regulatory/safety issue beyond scientific interest

---

## Phase 4: Comparative Database Analysis

### Systematic Survey of All Southern California Offshore Faults

**Target faults**:
1. Palos Verdes (ID 86)
2. Redondo Canyon (if separate ID)
3. San Pedro Basin faults
4. Ferrelo (offshore San Diego/Mexico border)
5. Coronado Bank
6. San Clemente (offshore Channel Islands)

**Metrics to calculate**:
- Total fault length (USGS database)
- Offshore vs. onshore length ratio
- Number of sections marked "less well defined"
- Orphan earthquake percentage
- Database last review date

**Output**: Comparison table showing if offshore gaps are systematic

---

## Data Products

### For Each Fault System

1. **Analysis script**: `analyze_[fault_name]_gap.py`
2. **Figures**:
   - Database coverage map
   - Microseismicity overlay
   - Orphan earthquake analysis
   - Comparison to published modern mapping
3. **Statistics CSV**: Gap metrics, seismicity counts
4. **Findings document**: Markdown report

### Comparative Analysis

1. **Master comparison figure**: All fault systems on one map
2. **Summary table**: Gap statistics across all faults
3. **Report**: "Systematic Offshore Fault Database Deficiency in Southern California"

---

## Timeline & Resources

### Phase 1 (Palos Verdes)
- **Time**: 4-6 hours
- **Data downloads**:
  - USGS database sections (~5 MB)
  - Microseismicity catalog (~10 MB)
  - Optional: Bathymetry (~500 MB)
- **Deliverable**: Complete analysis matching Rose Canyon format

### Phase 2 (Northern NIFZ)
- **Time**: 2 hours
- **Purpose**: Control case verification
- **Deliverable**: Confirmation that onshore = well-mapped

### Phase 3 (Hosgri/Diablo Canyon)
- **Time**: 4-6 hours
- **Data downloads**: Same as Phase 1
- **Deliverable**: Nuclear facility proximity analysis

### Phase 4 (Systematic survey)
- **Time**: 8-12 hours
- **Scope**: 6+ fault systems
- **Deliverable**: Comprehensive report for publication/submission to USGS

---

## Success Criteria

### Isolated Case (H0 confirmed)
- Only NIFZ/RCFZ shows significant gap
- Other offshore faults well-represented
- Rose Canyon gap is unique due to complex Oceanside transition zone
- **Conclusion**: Specific database update needed for Fault ID 127

### Systematic Problem (H1 confirmed)
- Multiple offshore faults show >30% gaps
- Pattern: onshore = well-mapped, offshore = "less well defined"
- Correlation with "last review date" pre-2000
- **Conclusion**: Requires institutional response:
  - USGS policy change to integrate marine geophysics
  - Collaboration with NOAA/BOEM
  - Systematic update of offshore fault geometry nationwide

---

## Publication Strategy

### If Isolated Case
- Technical note in *Seismological Research Letters*
- Focus on NIFZ/RCFZ hazard implications
- Recommendation for database update

### If Systematic Problem
- **High-impact submission**: *Science* or *Nature Geoscience*
- Title: "Systematic Underrepresentation of Offshore Faults in U.S. Seismic Hazard Database"
- Co-authors: Invite USGS database managers, SCEC researchers
- Policy implications: National Seismic Hazard Map updates

---

## Next Steps (Immediate)

1. **Save current analysis** (already done)
2. **Create Phase 1 directory structure**:
   ```
   palos_verdes_gap_analysis/
   ├── scripts/
   ├── data/
   ├── figures/
   └── README.md
   ```
3. **Download Palos Verdes data**:
   - USGS database Fault ID 86
   - Microseismicity (33.4°N-34.1°N, -119.0°W to -117.8°W)
4. **Run identical analysis pipeline**
5. **Compare results to Rose Canyon**

---

## Risk Assessment

**What if we're wrong?**

Possible alternative explanations to investigate:
1. Our spatial filtering excluded offshore sections
2. GeoJSON export settings filtered "less confident" traces
3. Microseismicity location errors concentrated offshore (depth/azimuthal gap issues)
4. USGS database has separate "offshore fault" layer we didn't access

**Mitigation**:
- Download raw shapefile, not just GeoJSON
- Check all database export options
- Verify earthquake location quality (azimuthal gap, nearest station distance)
- Contact USGS database managers for clarification

---

## User's Skepticism: Valid & Important

> "This just can't be true"

**Why skepticism is appropriate**:
- Extraordinary claims require extraordinary evidence
- USGS is premier hazard assessment agency
- Hundreds of researchers use this database
- How could such a large gap persist unnoticed?

**Why we should still investigate**:
- Gemini independently verified (different methodology, same result)
- Our analysis is reproducible (code + data provided)
- Modern offshore mapping (Sahakian 2017) is peer-reviewed
- Institutional inertia can preserve legacy data structures

**The northern expansion analysis will either**:
- **Refute our claim** (only Rose Canyon shows gap → unique case)
- **Validate our claim** (multiple offshore faults show gaps → systematic)

Either outcome is scientifically valuable.
