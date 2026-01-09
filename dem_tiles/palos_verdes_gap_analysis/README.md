# Palos Verdes Fault Database Gap Analysis

**Date**: 2026-01-02
**Status**: Phase 1 - Active
**Purpose**: Test if Rose Canyon database gap is isolated or systematic

---

## Hypothesis Testing

**H0 (Null)**: Rose Canyon 85 km gap is an isolated case
**H1 (Alternative)**: USGS systematically under-maps offshore faults

**Test strategy**: Apply identical microseismicity overlay analysis to Palos Verdes Fault Zone

---

## Target Fault System

**USGS Fault ID**: 86 (Palos Verdes fault zone)

**Geographic extent**:
- North: Santa Monica Bay (~34.0°N)
- South: Dana Point (~33.45°N)
- Total length: ~100 km (primarily offshore)

**Tectonic setting**:
- Right-lateral strike-slip
- Part of Inner Continental Borderland (ICB) deformation
- Passes within 8 km of Ports of LA/Long Beach

**Hazard significance**:
- M7.0-7.3 potential
- Submarine landslide + tsunami risk
- Direct threat to Ports of LA/Long Beach (40% of US containerized imports)
- 10+ million people in greater LA metro

---

## Analysis Parameters

**Microseismicity**:
- USGS catalog: 1980-2025
- Region: 33.4°N-34.1°N, -119.0°W to -117.8°W
- M≥1.0 events
- Depth: 0-25 km

**Orphan earthquake thresholds**:
- 3 km from nearest mapped fault segment
- 5 km from nearest mapped fault segment

---

## Expected Outcomes

### If H0 confirmed (isolated case):
- Palos Verdes fully mapped in USGS database
- Low orphan earthquake percentage (<10%)
- Good agreement between USGS and modern studies
- **Conclusion**: Rose Canyon gap is unique

### If H1 confirmed (systematic problem):
- Similar gap pattern (offshore segments "less well defined")
- High orphan earthquake percentage (>30%)
- Database reflects legacy pre-2000 interpretations
- **Conclusion**: Institutional offshore mapping deficiency

---

## Directory Structure

```
palos_verdes_gap_analysis/
├── README.md               # This file
├── scripts/
│   └── analyze_palos_verdes_gap.py
├── data/
│   ├── usgs_palos_verdes_fault.geojson
│   └── usgs_palos_verdes_microseismicity_1980-2025.csv
└── figures/
    ├── palos_verdes_database_coverage.png
    ├── palos_verdes_microseismicity_overlay.png
    ├── palos_verdes_orphan_analysis.png
    └── palos_verdes_comparison_4panel.png
```

---

## Data Sources

- **USGS Quaternary Fault Database**: Fault ID 86
- **USGS Earthquake Catalog**: 1980-2025, study region
- **Published mapping**: Ryan et al. 2009, Freeman et al. 2010
- **SCEC Community Fault Model v5.3**: 3D fault geometry

---

## Analysis Pipeline

1. Download USGS database sections for Fault ID 86
2. Download microseismicity (1980-2025)
3. Calculate distance from each earthquake to nearest mapped fault
4. Calculate orphan earthquake percentage
5. Compare to published fault geometry
6. Generate comparison figures
7. Compare results to Rose Canyon analysis

---

## Success Metrics

**Quantitative comparison to Rose Canyon**:
- Total fault length (km)
- Number of database sections
- Microseismicity count
- Orphan percentage at 3 km threshold
- Orphan percentage at 5 km threshold
- Offshore vs. onshore length ratio

---

## References

- Ryan, H.F., et al. (2009). "Marine seismic imaging of Palos Verdes fault zone"
- Freeman, S.T., et al. (2010). "Offshore fault geometry and seismic hazard"
- SCEC CFM v5.3: Community Fault Model
- Sahakian, V.J., et al. (2017). "Seismic constraints on fault geometry" (Rose Canyon comparison)
