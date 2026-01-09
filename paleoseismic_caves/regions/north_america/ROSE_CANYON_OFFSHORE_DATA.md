# Rose Canyon Fault Offshore Seismic Data Inventory

## Overview

This document inventories offshore geophysical data relevant to Rose Canyon Fault paleoseismology and the proposed 1741 dark earthquake hypothesis. Primary data source: Scripps Institution of Oceanography (SIO) cruises funded by Southern California Edison for SONGS (San Onofre Nuclear Generating Station) seismic hazard assessment.

---

## Primary Dataset: NH1320 Processed MCS Seismic

### Citation
```
Driscoll, Neal; Kent, Graham; Bormann, Jayne (2018). Processed multi-channel seismic
data (stacks and migrations) offshore California acquired during the R/V New Horizon
expedition NH1320 (2013) using a sparker source. Marine Geoscience Data System (MGDS).
doi:10.1594/IEDA/500041
```

### Details
| Field | Value |
|-------|-------|
| **DOI** | [10.1594/IEDA/500041](https://www.marine-geo.org/doi/10.1594/IEDA/500041) |
| **Vessel** | R/V New Horizon |
| **Dates** | October 2013 |
| **Platform** | Multi-channel seismic array |
| **Source** | Sparker + Boomer |
| **Format** | SEGY (processed - stacks and migrations) |
| **License** | CC BY-NC-SA 3.0 |

### Fault Systems Imaged
- **Newport-Inglewood Fault**
- **Rose Canyon Fault** (primary target)
- **Oceanside Blind Thrust Faults**
- Coronado Bank Fault
- Palos Verdes Fault
- San Diego Trough Fault
- San Clemente Fault System

### Scientific Objectives (from abstract)
> "The objectives included imaging the fault geometry in the seismogenic zone and **determining the recurrence interval for the fault systems**."

### Download Status
- **P190 Navigation**: ✅ Downloaded (162MB) - `/tmp/MGDS_Download/NH1320/` (116 files)
- **SEGY Seismic**: ❌ NOT YET DOWNLOADED - need to select "Seismic Reflection/Refraction" on MGDS page
- **Target location**: `paleoseismic_caves/data/california/nh1320_segy/`
- **Processing**: Use `segyio` or `obspy` Python libraries

### How to Download SEGY Files
1. Go to: https://www.marine-geo.org/tools/search/entry.php?id=NH1320
2. Under "Data Sets", click **"Seismic Reflection/Refraction"** (NOT Navigation)
3. Download SEGY files (formats: 4-byte int for lines 001-027, IEEE float for later)
4. Also download: Cruise report PDF, Reprocessing report PDF

---

## Related Cruises

### Neal Driscoll SONGS Cruises (2013)

| Cruise | Year | Vessel | Target | Data Type | Availability |
|--------|------|--------|--------|-----------|--------------|
| MV1311 | 2013 | Melville | SONGS Offshore Multibeam | Multibeam | R2R |
| MV1316 | 2013 | Melville | SONGS 2D Shallow Seismic (NI/RC/OBT) | Underway only | Limited |
| **NH1320** | 2013 | New Horizon | **SONGS Sparker/Boomer** | **SEGY** | **MGDS DOI:10.1594/IEDA/500041** |
| **NH1323** | 2013 | New Horizon | **SONGS 3D Shallow Seismic** | **SEGY** | **MGDS (verified)** |
| TN336 | 2016 | Thompson | S. California Borderlands Coring | Cores | SIO Repository |

### NH1323 - Additional Seismic Dataset (VERIFIED)

| Field | Value |
|-------|-------|
| **Cruise DOI** | [10.7284/903024](https://www.marine-geo.org/tools/search/entry.php?id=NH1323) |
| **Project** | SONGS 3D Shallow Marine Seismic Reflection Survey |
| **Chief Scientist** | Driscoll, Neal (SIO) |
| **Dates** | 2013-10-10 to 2013-11-04 |
| **Data Format** | ASCII, P1, PDF, SEGY |
| **Repository** | MGDS |
| **Contributors** | Bormann, Jayne (UNR); Driscoll, Neal (SIO); Kent, Graham |

**Note**: This 3D shallow seismic survey complements NH1320 sparker/boomer data. Same team, same fault systems.

### Cruises NOT Relevant (Verified 2024-12-29)

| Cruise | Chief | Project | Why Not Useful |
|--------|-------|---------|----------------|
| MV1209 | Frieder, Christina | SD-SeaFEx (Climate) | CTD/gravity only, no seismic |
| MV1217 | Grupe, Benjamin | SD-SeaFEx (Climate) | CTD/gravity only, no seismic |

*Initial suggestions that MV1209/MV1217 had CHIRP data were incorrect - verified via R2R.*

### TN336 Sediment Cores (2016)
- **Project**: Coring-Southern California Borderlands
- **Status**: Core data not yet publicly available on MGDS
- **Physical cores**: Likely stored at SIO Marine Geology Collections
- **Relevance**: May contain turbidite records for paleoseismic reconstruction
- **Action needed**: Contact SIO repository or Neal Driscoll

---

## Relevance to Paleoseismic Research

### Connection to 1741 Rose Canyon Dark Earthquake Hypothesis

The NH1320 seismic data directly supports investigation of:

1. **Fault geometry**: High-resolution imaging of Rose Canyon Fault offshore extent
2. **Recurrence intervals**: Stated objective of the SONGS study
3. **Seismogenic zone depth**: Critical for magnitude estimation
4. **Rupture segmentation**: Connection between onshore/offshore fault segments

### ML Turbidite Detection Approach

1. **Training data**: Processed SEGY sections show stratigraphic horizons
2. **Ground truth**: TN336 cores (if accessible) could provide turbidite samples
3. **Target features**:
   - Turbidite layers in basin sediments
   - Mass transport deposits
   - Fault displacement offsets

### Integration with Speleothem Record

If a major Rose Canyon earthquake occurred in 1741:
- Cave proxies (Crystal Cave, Minnetonka) may show δ18O anomalies
- Offshore seismic data constrains fault capability
- Turbidite cores provide independent paleoseismic evidence

---

## Data Access Links

### Primary Data
- **MGDS DOI page**: https://www.marine-geo.org/doi/10.1594/IEDA/500041
- **Download**: "Download Data" button on DOI page

### R2R Cruise Pages
- NH1320: https://www.rvdata.us/search/cruise/NH1320
- NH1323: https://www.rvdata.us/search/cruise/NH1323
- TN336: https://www.rvdata.us/search/cruise/TN336
- MV1316: https://www.rvdata.us/search/cruise/MV1316

### MGDS Data Pages
- NH1320 Processed SEGY: https://www.marine-geo.org/doi/10.1594/IEDA/500041
- NH1323 Entry: https://www.marine-geo.org/tools/search/entry.php?id=NH1323

### Related Publications
- AGU Fall Meeting 2014: [Paper/30549](https://agu.confex.com/agu/fm14/meetingapp.cgi#Paper/30549)
- Processing report: [mv1316_processingrpt.pdf](http://www.ig.utexas.edu/sdc/functions/download.php?file=/DBother/mv1316/mv1316_processingrpt.pdf)

---

## Author Contact Required

**IMPORTANT**: Before using this data in publication, contact the PIs:

| Name | Institution | Email |
|------|-------------|-------|
| **Neal Driscoll** | Scripps Institution of Oceanography | (find via SIO directory) |
| **Graham Kent** | University of Nevada, Reno | (find via UNR directory) |
| **Jayne Bormann** | - | - |

**Reasons to contact**:
1. CC BY-NC-SA 3.0 license requires attribution
2. They may have unpublished fault recurrence data
3. Potential collaboration opportunity
4. Professional courtesy

---

## Processing Notes

### SEGY File Handling
```python
import segyio
import numpy as np

# Read SEGY file
with segyio.open('line_xxx.segy', 'r') as f:
    data = segyio.tools.cube(f)
    traces = f.trace.raw[:]

# Or use obspy
from obspy.io.segy.segy import _read_segy
stream = _read_segy('line_xxx.segy')
```

### Expected File Structure
```
MGDS_download.tar
├── processed/
│   ├── stacks/         # Stacked sections
│   └── migrations/     # Migrated sections
├── navigation/         # P190 nav files
└── metadata/           # Processing logs
```

---

## File Locations (Project)
```
paleoseismic_caves/
├── data/
│   └── california/
│       ├── nh1320_segy/           # Processed seismic SEGY files
│       └── rose_canyon_faults.geojson  # Digitized fault traces (future)
└── regions/
    └── north_america/
        └── ROSE_CANYON_OFFSHORE_DATA.md  # This file
```

---

*Last updated: 2024-12-30*
*Data discovery via R2R and MGDS browser search*
*P190 nav downloaded; SEGY seismic pending*
