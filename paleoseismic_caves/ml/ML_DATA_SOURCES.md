# ML Data Sources for Paleoseismic Analysis

**Last Updated**: 2025-12-28

This document catalogs all machine learning and satellite data sources available for earthquake detection and validation.

---

## 1. SPELEOTHEM DATA (Primary)

### SISAL v3 Database
- **Location**: `../SISAL3/sisalv3_database_mysql_csv/sisalv3_csv/`
- **Records**: 447,171 δ18O measurements
- **Caves**: 366 sites, 903 entities globally
- **Time span**: Holocene to present
- **Status**: ✅ LOADED - `ml/sisal_loader.py`

| Table | Records | Description |
|-------|---------|-------------|
| d18O.csv | 447,171 | Oxygen isotope ratios |
| d13C.csv | 286,634 | Carbon isotope ratios |
| Mg_Ca.csv | 26,486 | Magnesium/calcium trace element |
| Sr_Ca.csv | 23,963 | Strontium/calcium trace element |
| Ba_Ca.csv | 15,144 | Barium/calcium trace element |
| U_Ca.csv | 11,048 | Uranium/calcium trace element |

---

## 2. SATELLITE DATA

### GPS-TEC (Total Electron Content)
- **Source**: NASA CDDIS / IGS
- **URL**: `https://cddis.nasa.gov/archive/gnss/products/ionex/`
- **Format**: IONEX (ASCII grid files)
- **Resolution**: 2-hour temporal, 2.5° lat × 5° lon spatial
- **Coverage**: 1998 - present
- **Status**: ✅ WORKING - `ml/ionex_parser.py`

| Provider | File Prefix | Quality | Latency |
|----------|-------------|---------|---------|
| JPL | jplg | Best | ~3 days |
| IGS Combined | igsg | Excellent | ~11 days |
| CODE | codg | Very good | ~3 days |
| ESA | esag | Good | ~1 day (rapid) |

**Validated Test Case**: Ridgecrest M7.1 (2019-07-06)
- Precursor detected: June 28-29 (z = +1.74)
- Data saved: `data/ridgecrest_tec_2019.csv`

### GRACE/GRACE-FO (Gravity/Groundwater)
- **Source**: NASA JPL
- **URL**: `https://grace.jpl.nasa.gov/data/get-data/`
- **Format**: NetCDF, ASCII grids
- **Resolution**: Monthly, ~300 km spatial
- **Coverage**: April 2002 - present
- **Status**: ✅ IMPLEMENTED - `ml/grace_download.py`
- **Script**: `python3 grace_download.py --region liguria` or `--validate`

**Validation Targets**:
| Event | Date | Magnitude | Expected Signal |
|-------|------|-----------|-----------------|
| Ridgecrest | 2019-07-06 | M7.1 | Moderate groundwater |
| Tohoku | 2011-03-11 | M9.0 | -15 μGal, years recovery |
| Chile | 2010-02-27 | M8.8 | -8 μGal, 18-month recovery |
| Nepal | 2015-04-25 | M7.8 | Continental response |

### InSAR (Ground Deformation)
- **Source**: ASF DAAC (Alaska Satellite Facility)
- **URL**: `https://search.asf.alaska.edu/`
- **Format**: GeoTIFF (SLC for interferometry, GRD for amplitude)
- **Resolution**: 10-30m spatial
- **Coverage**: 2014 - present (Sentinel-1)
- **Status**: ✅ IMPLEMENTED - `ml/insar_download.py`
- **Script**: `python3 insar_download.py --region liguria --pairs`

**Predefined Regions**:
| Region | Description | Target Faults |
|--------|-------------|---------------|
| liguria | Ligurian Alps | T. Porra Fault, 1285 source |
| motagua | Guatemala | Motagua-Polochic system |
| cascadia | Oregon coast | Subduction zone |
| tabriz | NW Iran | North Tabriz Fault |

### Bathymetry (Offshore Faults)
- **Source**: EMODnet, GEBCO
- **URL**: `https://www.emodnet-bathymetry.eu/`
- **Format**: GeoTIFF
- **Resolution**: ~115m (EMODnet), ~450m (GEBCO)
- **Coverage**: European waters (EMODnet), Global (GEBCO)
- **Status**: ✅ DOWNLOADED - `ml/bathymetry_data/ligurian_sea/`
- **Script**: `python3 bathymetry_download.py --region ligurian_sea`

**Ligurian Sea Products** (2025-12-28):
| File | Size | Description |
|------|------|-------------|
| emodnet_bathymetry.tif | 15.7 MB | Raw depth grid (2400×1440 px) |
| processed/bathymetry_hillshade.tif | 3.5 MB | 315° illumination |
| processed/bathymetry_slope.tif | 13.8 MB | Slope for scarp detection |
| processed/bathymetry_color.tif | 10.4 MB | Color-coded depth |

**Offshore Fault Targets**:
- North Ligurian Fault System (~40 km from Bàsura)
- Monaco-Sanremo offshore segment (~35 km)
- Imperia lineaments (~20 km)
- Ligurian Trough axis (~50 km)

### Sentinel-2 (Optical Imagery)
- **Source**: Copernicus Data Space Ecosystem (CDSE)
- **URL**: `https://dataspace.copernicus.eu/`
- **Format**: GeoTIFF (multispectral)
- **Resolution**: 10m (RGB, NIR), 20m (SWIR)
- **Coverage**: 2015 - present
- **Status**: ✅ IMPLEMENTED - `ml/sentinel2_download.py`
- **Script**: `python3 sentinel2_download.py --region liguria --workflow`

**Fault Analysis Applications**:
- NDVI: Vegetation stress along fault traces
- SWIR composite: Geological discrimination
- Bare Soil Index: Expose fault traces
- Multi-temporal stacking: Identify persistent lineaments

---

## 3. EARTHQUAKE CATALOGS

### USGS Earthquake Catalog
- **URL**: `https://earthquake.usgs.gov/fdsnws/event/1/`
- **Coverage**: 1900 - present (global M4+), complete M5+ since 1973
- **Status**: ✅ WORKING - REST API in `ml/tec_fusion.py`

### CPTI15 (Italy)
- **URL**: `https://emidius.mi.ingv.it/CPTI15-DBMI15/`
- **Coverage**: 1000 - 2014 CE
- **Status**: ✅ Used for Italy validation

### ISC-GEM Global Catalog
- **URL**: `http://www.isc.ac.uk/iscgem/`
- **Coverage**: 1904 - present, M5.5+
- **Status**: 📋 Available

---

## 4. VOLCANIC CATALOGS

### eVolv2k v4
- **Location**: `../eVolv2k_v4_ds_1.xlsx`
- **Coverage**: 500 BCE - 1900 CE
- **Records**: 256 eruptions with sulfur injection estimates
- **Status**: ✅ LOADED - `ml/validate.py`

### IVI2 (Ice-core Volcanic Index)
- **Coverage**: 500 - 2000 CE
- **Status**: ✅ Used for volcanic discrimination

---

## 5. TREE RING DATA

### ITRDB (International Tree-Ring Data Bank)
- **URL**: `https://www.ncei.noaa.gov/products/paleoclimatology/tree-ring`
- **Coverage**: Global, up to 9,000 years
- **Status**: 📋 Identified - Sillett et al. 2014 network (328 CE - present)

### Carroll et al. 2025 (California Redwoods)
- **Location**: `data/tree_rings/`
- **Coverage**: Fort Ross 1569 CE, Gualala 1397 CE (partial)
- **Status**: ✅ ANALYZED - `data/tree_rings/TREE_RING_ANALYSIS.md`

---

## 6. FAULT DATABASES

### USGS Quaternary Fault Database
- **URL**: `https://earthquake.usgs.gov/hazards/qfaults/`
- **Coverage**: US faults with slip rates
- **Status**: ✅ API in `ml/dark_quakes.py`

### ITHACA (Italy)
- **Location**: `../dem_tiles/ithaca_liguria.geojson`
- **Records**: 231 Ligurian faults
- **Status**: ✅ Downloaded

### GEM Global Active Faults
- **URL**: `https://github.com/GEMScienceTools/gem-global-active-faults`
- **Coverage**: Global
- **Status**: 📋 Available

---

## 7. ML PIPELINE STATUS

| Script | Function | Status |
|--------|----------|--------|
| `sisal_loader.py` | Load SISAL v3 database | ✅ Working |
| `global_scan.py` | PELT change point detection | ✅ Working |
| `validate.py` | Cross-validate with EQ/volcanic catalogs | ✅ Working |
| `dark_quakes.py` | Dark earthquake classifier | ✅ Working |
| `ionex_parser.py` | Parse CDDIS TEC data | ✅ Working |
| `tec_fusion.py` | TEC anomaly detection | ✅ Working |
| `insar_download.py` | Search/download Sentinel-1 InSAR | ✅ Working |
| `grace_download.py` | GRACE gravity data access | ✅ Working |
| `bathymetry_download.py` | EMODnet/GEBCO seafloor data | ✅ Working |
| `sentinel2_download.py` | Optical imagery for fault mapping | ✅ Working |

### ML Results Summary
- **458 change points** detected across 114 caves
- **123 dark earthquake candidates** identified
- **7 high-confidence candidates** (score ≥70)
- **1 TEC precursor validated** (Ridgecrest 2019)

### Satellite Data Products (2025-12-28)
- **Ligurian Sea bathymetry**: 15.7 MB EMODnet grid + hillshade/slope derivatives
- **InSAR search**: ASF DAAC API functional for Liguria, Motagua, Cascadia, Tabriz regions
- **GRACE validation**: Protocol defined for Tohoku, Chile, Nepal, Ridgecrest benchmarks
- **Sentinel-2 workflow**: Fault analysis workflow documented (NDVI, SWIR, lineament extraction)

---

## 8. DATA ACCESS REQUIREMENTS

| Source | Authentication | Notes |
|--------|---------------|-------|
| CDDIS (TEC) | Earthdata login | Free registration |
| GRACE | Earthdata login | Free registration |
| ASF DAAC (InSAR) | Earthdata login | Free, bulk downloads |
| Copernicus CDSE | CDSE account | Free, replaced Scihub |
| EMODnet | None | Public WCS API |
| GEBCO | None | Manual download |
| USGS | None | Public API |
| SISAL | None | Downloaded locally |
| ITRDB | None | Public FTP |

**Earthdata Registration**: https://urs.earthdata.nasa.gov/
**CDSE Registration**: https://dataspace.copernicus.eu/

---

## 9. NEXT PRIORITIES

1. ✅ ~~GRACE integration~~ - Script implemented, validation protocol defined
2. ✅ ~~InSAR access~~ - ASF DAAC search working
3. ✅ ~~Bathymetry download~~ - Ligurian Sea EMODnet data acquired
4. ✅ ~~Sentinel-2 access~~ - CDSE API and workflow documented
5. **Extend TEC analysis** - Test on Tohoku 2011, Chile 2010
6. **ITRDB crossdating** - Anchor Carroll et al. floating chronology via Sillett et al.
7. **Turkey/Greece caves** - Extract from SISAL for Anatolian fault validation
8. **Ligurian offshore lineament analysis** - Use bathymetry slope to identify submarine faults
9. **InSAR time series** - Download Sentinel-1 stack for T. Porra deformation analysis

---

*Document created: 2025-12-27*
*Last major update: 2025-12-28 - Added InSAR, GRACE, Bathymetry, Sentinel-2 satellite data pipelines*
