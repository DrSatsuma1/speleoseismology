# San Diego DEM Lineament Analysis - Implementation Plan
**Date**: 2026-01-02
**Objective**: Map Rose Canyon Fault trace and search for unmapped segments using DEM analysis + microseismicity overlay
**Target Event**: 1741 ± 1 yr Dark Earthquake (tree ring evidence)

---

## Background

**Evidence for 1741 Rose Canyon Rupture:**
- **Tree rings**: Mt. Laguna (z=-1.09σ) + Palomar (z=-1.10σ) = CONVERGENT (spread=0.01)
- **Paleoseismic**: Singleton et al. 2019 - "mid-1700s" radiocarbon window (~1700-1760 CE)
- **Magnitude**: Largest Rose Canyon rupture in 3,300 years
- **Status**: Pre-Spanish (Mission San Diego founded 1769) = guaranteed Dark Earthquake

**Research Questions:**
1. Can we map the **full 1741 rupture extent** using DEM lineament analysis?
2. Are there **unmapped fault segments** parallel to Rose Canyon?
3. Does microseismicity show clustering along unmapped structures?
4. Can we identify **paleoseismic trenching targets** for 1741 validation?

---

## Methodology (Italy Template Applied to San Diego)

### Phase 1: Data Acquisition

**A. DEM Data Sources (Priority Order):**

1. **USGS 3DEP (Primary)** - https://apps.nationalmap.gov/downloader/
   - Resolution: 1/3 arc-second (~10m) - BEST
   - Coverage: Full San Diego County
   - Format: GeoTIFF
   - Cost: FREE
   - Quality: Excellent for urban/coastal areas

2. **OpenTopography (Alternative)** - https://opentopography.org/
   - Resolution: 1m lidar (if available)
   - Coverage: May be limited to specific surveys
   - Format: LAS/LAZ point clouds or raster
   - Cost: FREE (academic use)
   - Quality: Superior for fault geomorphology

3. **USGS EarthExplorer (Backup)** - https://earthexplorer.usgs.gov/
   - SRTM 30m (global, lower resolution)

**B. Geographic Extent:**

**Primary Study Area (Rose Canyon Fault):**
- Lat: 32.6° to 33.2°N (La Jolla to Oceanside, ~65 km)
- Lon: -117.3° to -117.1°W (coast to inland)
- Extent: 20km × 70km (covers full known RCF trace)

**Extended Study Area (search for parallel structures):**
- Lat: 32.5° to 33.3°N
- Lon: -117.4° to -116.9°W
- Extent: 50km × 90km (includes Newport-Inglewood, Elsinore fault zones)

**Target Resolution**: 10m (matches Italy analysis)

**C. Microseismicity Data:**

**USGS Earthquake Catalog:**
- URL: https://earthquake.usgs.gov/earthquakes/search/
- Parameters:
  - Lat: 32.5-33.3°N, Lon: -117.4 to -116.9°W
  - Date range: 1980-2025 (modern catalog)
  - Min magnitude: 1.0 (include microseismicity)
  - Format: CSV export

**SCEDC (Southern California Earthquake Data Center):**
- URL: https://scedc.caltech.edu/data/
- Higher quality locations for Southern California
- Includes offshore events

**D. Fault Databases:**

1. **USGS Quaternary Fault Database:**
   - https://www.usgs.gov/programs/earthquake-hazards/faults
   - Rose Canyon, Newport-Inglewood, Elsinore traces

2. **SCEC CFM (Community Fault Model):**
   - https://www.scec.org/research/cfm
   - 3D fault surfaces for Rose Canyon

3. **California Geological Survey:**
   - https://maps.conservation.ca.gov/cgs/fam/
   - Alquist-Priolo zones, trenching sites

---

### Phase 2: DEM Processing

**A. Create Rose Canyon Fault DEM (20km × 70km):**

```python
# Script: scripts/san_diego_dem_processing.py

import rasterio
from rasterio.merge import merge
from rasterio.mask import mask
from shapely.geometry import box

# Define Rose Canyon extent
rcf_bounds = {
    'min_lon': -117.3,
    'max_lon': -117.1,
    'min_lat': 32.6,
    'max_lat': 33.2
}

# Download 3DEP tiles covering this extent
# Mosaic tiles
# Crop to exact bounds
# Reproject to UTM 11N (EPSG:26911) for consistent analysis
```

**B. Create Extended Regional DEM (50km × 90km):**
- Same process, larger extent
- Search for parallel unmapped structures

**Output:**
- `rose_canyon_dem_20x70km.tif` (primary analysis)
- `san_diego_regional_dem_50x90km.tif` (regional context)

---

### Phase 3: Lineament Analysis

**A. Edge Detection (Reuse Italy Script):**

```bash
# Modify dem_lineament_analysis.py for San Diego

DEM_FILE = 'rose_canyon_dem_20x70km.tif'
FAULT_FILE = 'usgs_quaternary_faults_sandiego.geojson'
EQ_FILE = 'usgs_sandiego_microseismicity.txt'

# Edge detection methods:
# 1. Sobel magnitude (omnidirectional)
# 2. Sobel directional (340° N-S for RCF)
# 3. Canny edges

# Output: edge_detection/rcf_*.tif
```

**Expected Rose Canyon Strike**: ~340° (N-S to NNW-SSE)

**B. Drainage Analysis:**
- Flow accumulation (fault-controlled drainages)
- Stream network extraction
- Drainage density mapping

**C. Hillshade Multi-Azimuth:**
- 315°, 45°, 135°, 225° (reveal lineaments at all orientations)
- Composite hillshade for publication

---

### Phase 4: Microseismicity Overlay

**A. Orphan Earthquake Analysis (Italy Method):**

```python
# Identify earthquakes >3km from mapped faults
# Cluster analysis for linear patterns
# Check for N-S trending clusters parallel to RCF
```

**B. Temporal Analysis:**
- Plot seismicity 1980-2025
- Check for swarms or clusters
- Identify potential unmapped segments

**C. Depth Analysis:**
- Rose Canyon is shallow crustal (<15 km)
- Filter deep events (>20 km)

---

### Phase 5: Visualization & Interpretation

**Figure 1: Rose Canyon Fault Trace (4-panel)**
- Panel A: Sobel composite (magnitude + directional)
- Panel B: Canny edges + USGS faults
- Panel C: Drainage analysis
- Panel D: Integrated (edges + microseismicity + faults)

**Figure 2: Regional Context (50km × 90km)**
- Full DEM extent
- All microseismicity (1980-2025)
- USGS Quaternary faults
- Search for unmapped parallel structures

**Figure 3: 1741 Rupture Extent Candidate**
- Zoom to segments showing:
  - Clear topographic expression
  - Microseismicity alignment
  - Paleoseismic site locations (Singleton 2019, Rose et al. 2023)

**Figure 4: Trenching Target Sites**
- High-resolution crops (1km × 1km)
- Identify offset streams, scarps, sag ponds
- GPS coordinates for field reconnaissance

---

## Key Differences from Italy Analysis

| Aspect | Italy (Ligurian Alps) | San Diego (Rose Canyon) |
|--------|----------------------|-------------------------|
| **Known vs Unknown** | Unmapped structure | **Known fault** (RCF mapped) |
| **Goal** | Discover new fault | Map **1741 rupture extent** |
| **Challenges** | Dense vegetation | **Urban development** (obscures scarps) |
| **DEM Quality** | TINITALY 10m (excellent) | USGS 3DEP 10m or lidar 1m |
| **Microseismicity** | 593 events (dense) | Moderate (RCF is locked?) |
| **Tectonic Setting** | Compressional (Alpine) | **Strike-slip** (transform) |
| **Offshore Component** | Coastal plain | RCF extends **offshore** |
| **Validation** | None yet | **Paleoseismic trenches exist** |

---

## Expected Outcomes

### High Confidence Scenarios:

**1. Map 1741 Rupture Extent:**
- Clear N-S topographic lineament
- Microseismicity shows segment boundaries
- Extent: 20-40 km (M6.0-6.5 consistent with tree ring + paleo)

**2. Identify Unmapped Segments:**
- Parallel structures east/west of main RCF trace
- Offshore continuation (compare with marine surveys)
- Splays or stepovers

**3. Trenching Target Identification:**
- Offset streams with <5m vertical separation (optimal for trenching)
- Sag ponds (sediment traps for dating)
- Undisturbed sites (parks, open space)

### Moderate Confidence:

**4. Cryptic Fault Expression:**
- Urban development obscures surface trace
- Fault may be blind (no surface rupture in 1741)
- Rely on microseismicity + drainage offsets

---

## Timeline & Resources

| Phase | Duration | Tools/Data Required |
|-------|----------|---------------------|
| **1. Data Download** | 1-2 days | USGS 3DEP, earthquake catalog |
| **2. DEM Processing** | 1 day | Python (rasterio, GDAL) |
| **3. Lineament Analysis** | 2-3 days | Modify Italy script |
| **4. Microseismicity** | 1 day | USGS/SCEDC data parsing |
| **5. Visualization** | 2-3 days | Matplotlib, QGIS for publication figs |
| **6. Interpretation** | 2-4 days | Compare with Singleton 2019, CFM |
| **7. Documentation** | 1-2 days | Write SAN_DIEGO_DEM_FINDINGS.md |
| **TOTAL** | **10-16 days** | |

---

## Success Criteria

**Minimum (Publishable):**
- ✅ Full Rose Canyon trace mapped in 10m DEM
- ✅ Microseismicity overlay shows fault alignment
- ✅ 4 publication-quality figures
- ✅ Comparison with Singleton 2019 paleoseismic sites

**Ideal (High Impact):**
- ✅ 1741 rupture extent constrained to ±10 km
- ✅ Unmapped parallel fault identified
- ✅ 3+ trenching target sites with GPS coordinates
- ✅ Field reconnaissance plan ready

**Exceptional (Nature/Science Level):**
- ✅ Offshore RCF continuation mapped (if marine DEM available)
- ✅ Segment boundaries correlate with microseismicity gaps
- ✅ Direct comparison: tree ring signal strength vs rupture length
- ✅ Revised San Diego seismic hazard assessment

---

## Data Products to Generate

**Rasters (6 minimum):**
1. `rcf_sobel_magnitude.tif`
2. `rcf_sobel_directional_340.tif`
3. `rcf_canny_edges.tif`
4. `rcf_flow_accumulation.tif`
5. `rcf_stream_network.tif`
6. `rcf_drainage_density.tif`

**Figures (4 minimum):**
1. `fig1_rcf_sobel_composite.png`
2. `fig2_rcf_canny_overlay.png`
3. `fig3_rcf_drainage_analysis.png`
4. `fig4_rcf_integrated_analysis.png`

**Optional (if unmapped structure found):**
5. `fig5_rcf_regional_seismicity.png` (50km × 90km extent)
6. `fig6_rcf_1741_rupture_extent.png` (zoom to candidate)

**Analysis Document:**
- `regions/north_america/SAN_DIEGO_DEM_FINDINGS.md`

---

## Script Template (Adapt from Italy)

**File**: `scripts/san_diego_lineament_analysis.py`

```python
#!/usr/bin/env python3.11
"""
Rose Canyon Fault DEM Lineament Analysis
Based on Italy (Bàsura) methodology

Goals:
1. Map full RCF trace using edge detection
2. Identify 1741 rupture extent
3. Search for unmapped parallel structures
4. Generate trenching target coordinates
"""

# Reuse functions from dem_lineament_analysis.py:
# - load_dem()
# - compute_sobel_magnitude()
# - compute_sobel_directional(azimuth=340)  # N-S for RCF
# - compute_canny_edges()
# - compute_flow_accumulation_simple()
# - create_integrated_figure()

# Modifications:
# - UTM Zone 11N (EPSG:26911) instead of UTM 32N
# - Strike-slip geomorphology (linear valleys, offset streams)
# - Urban development masking (filter developed areas?)
```

---

## Key References to Cross-Check

**Paleoseismic:**
- Singleton et al. (2019) - Old Town San Diego trench, mid-1700s event
- Rose et al. (2023) - Rose Canyon Fault paleoseismology synthesis
- Rockwell & Klinger (2013) - Rose Canyon recurrence intervals

**Fault Geometry:**
- SCEC CFM v6.3 - 3D Rose Canyon Fault model
- Lindvall & Rockwell (1995) - RCF holocene slip rate
- Treiman (1993) - Rose Canyon Fault zone mapping

**Tree Ring Analysis:**
- Our data: `regions/north_america/ROSE_CANYON_1741_DARK_EARTHQUAKE.md`

---

## Next Steps After Completion

**If RCF analysis successful:**
1. Apply same method to **Newport-Inglewood Fault** (Los Angeles)
2. Extend to **Elsinore Fault** (search for 1580 SAF correlation)
3. Check **San Andreas Fault** offshore segments (Point Arena, Fort Ross)

**Publication Integration:**
- Add to `PAPER_2_DARK_EARTHQUAKES.md` Section 3.8 (San Diego)
- Create supplementary figures for 1741 rupture extent
- Compare DEM findings with tree ring signal strength

---

## Questions to Answer

1. **Does the 1741 rupture extend full 40 km RCF length?**
   - Check if topographic expression is continuous
   - Microseismicity gaps = segment boundaries?

2. **Why is RCF microseismicity low if it's "active"?**
   - Locked fault = strain accumulation
   - Check for creeping vs locked segments

3. **Are there unmapped splays offshore?**
   - Compare with marine surveys (if available)
   - Drainage patterns suggest offshore continuation?

4. **Can we identify 1741 trenching sites?**
   - Undisturbed parks: Rose Canyon Open Space, Tecolote Canyon
   - Offset drainages visible in DEM

---

**Status**: READY TO IMPLEMENT - All Italy methods are transferable to San Diego

**Priority**: HIGH - 1741 event has multi-proxy validation (tree rings + paleoseismic), DEM analysis can constrain rupture extent for hazard assessment
