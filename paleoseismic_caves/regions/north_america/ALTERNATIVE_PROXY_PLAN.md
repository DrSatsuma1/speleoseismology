# Alternative Proxy Integration Plan

## Purpose

Since all California speleothem records in SISAL v3 are prehistoric (ending before 1700 CE), detecting "lost" 1800s California earthquakes requires alternative proxy sources.

This document outlines the integration strategy for combining:
1. **Tree ring data** (dendroseismology)
2. **Lake sediment seismites**
3. **Paleoseismic trench records**
4. **Indigenous oral traditions** (Pacific NW - Cascadia events)

---

## Target Earthquakes (USGS-Verified 2024-12-25)

California earthquakes verified against USGS Historical Earthquake Catalog:

| Date | Location | Magnitude | Verification | Priority |
|------|----------|-----------|--------------|----------|
| **Jan 26, 1700** | Cascadia | M9.0 | Japanese tsunami + ghost forests | **HIGHEST** |
| **Dec 8, 1812** | Southern CA (Wrightwood) | ~M7 | USGS - eastern segment | HIGH |
| **Dec 21, 1812** | Santa Barbara | ~M7 | USGS - western segment | HIGH |
| **June 1838** | San Francisco Peninsula | ~M7 | USGS - Hazel Dell trench confirms | **HIGH** |
| **Jan 9, 1857** | Fort Tejon | M7.9 | USGS - 350 km rupture | MEDIUM |
| **1865** | Santa Cruz | M6.5 | Debated if on SAF | HIGH |
| **1868** | Hayward | M6.8 | Fair documentation | LOW |
| **Mar 26, 1872** | Owens Valley | M7.4-7.9 | USGS - fault scarps visible | MEDIUM |
| **pre-1800** | Unknown | M6.5-6.9 | Likely unrecorded "dark" events | **HIGHEST** |

**Source**: See `GEMINI_BACKUP_DATA.md` for USGS verification details.

---

## Data Sources

### 1. Tree Ring Data (Dendroseismology)

**Source**: International Tree-Ring Data Bank (ITRDB)
**URL**: https://www.ncei.noaa.gov/products/paleoclimatology/tree-ring

| Dataset | Location | Coverage | Proximity to SAF |
|---------|----------|----------|------------------|
| Fort Ross Redwoods | Northern CA | 1569-2023 CE | ~10 km |
| Gualala Redwoods | Northern CA | 1397-2023 CE | ~15 km |
| Wrightwood Trees | Southern CA | Medieval-1900s | ~5 km |

**Key References**:
- Jacoby et al. (1988) Science 241:196-199 - 1812 earthquake evidence
- USGS Data Releases for Fort Ross/Gualala

**Seismic Indicators in Tree Rings**:
- Growth anomalies (ring width changes)
- Traumatic resin ducts
- Reaction wood formation
- Tree death dates
- Fire scars (secondary effects)

### 2. Lake Sediment Seismites

**Source**: USGS ScienceBase
**Pallett Creek Data**: https://doi.org/10.5066/P917R4F9 (downloadable)

| Site | Data Type | Coverage | Download |
|------|-----------|----------|----------|
| Pallett Creek | Trench stratigraphy | ~700 years | USGS ScienceBase |
| Lake Tahoe | Turbidite cores | ~12,000 years | Published papers |
| Clear Lake | Sediment cores | Holocene | NOAA Paleoclimate |

**Seismic Indicators in Lake Sediments**:
- Turbidites (earthquake-triggered sediment flows)
- Soft sediment deformation
- Homogenites (post-seismic settling)
- Liquefaction features

### 3. Paleoseismic Trench Data

**Source**: USGS Quaternary Fault Database
**URL**: https://www.usgs.gov/natural-hazards/earthquake-hazards/faults

**California Sites**: 38+ paleoseismic trenches

| Fault Segment | Key Sites | Events Dated |
|---------------|-----------|--------------|
| SAF - Carrizo | Wallace Creek, Cholame | 1857, 1812, medieval |
| SAF - Mojave | Wrightwood, Pallett Creek | Multiple pre-historic |
| SAF - Peninsula | Point Reyes | 1906, 1838?, earlier |
| Hayward Fault | Fremont, Hayward | 1868, pre-historic |
| San Jacinto | Multiple | Pre-historic |

### 4. Indigenous Oral Traditions (Verified Sources Only)

**Relevance**: Pre-instrumental earthquake evidence from tribal oral histories.

**VERIFIED - Cascadia 1700**:

| Tribe | Account | Source |
|-------|---------|--------|
| Makah | Water receded from Neeah Bay "perfectly dry" for 4 days | [USGS](https://www.usgs.gov/centers/pacific-coastal-and-marine-science-center/native-american-legends-tsunamis-pacific) / Swan 1868 |
| Yurok/Hupa | "Earthquake Running" - shaking propagated along coast | USGS Native American Legends |
| Tolowa | Thunderbird vs. Whale - ground shaking + ocean invasion | USGS Native American Legends |

**VERIFIED - Santa Barbara 1812**:

| Tribe | Account | Source |
|-------|---------|--------|
| Chumash | Waters receded "several hundred yards" from Santa Rosa Island; islanders fled fearing engulfment | [UCSB 1812 Project](https://projects.eri.ucsb.edu/sb_eqs/1812/chumash.html) |

**Historical Quote**: "In 1812 the great earthquake occurred on the California coast and at that time every soul [Indian] left the island of Santa Rosa"

**Application**:
- Supports 1700 Cascadia as primary target for Oregon Caves tip sampling
- Confirms 1812 tsunami impact on Channel Islands

---

## Integration Strategy

### Phase 1: Data Download (Immediate)

1. Download Fort Ross/Gualala tree ring data from ITRDB
2. Download Pallett Creek paleoseismic data from USGS
3. Compile Lake Tahoe turbidite chronology from publications

### Phase 2: Temporal Alignment

Create unified timeline (1700-1910 CE) with:

```
Year | Tree Rings | Lake Sediments | Trench Events | Known EQs
-----|------------|----------------|---------------|----------
1857 | Check FRR  | Lake Tahoe?    | Carrizo/WW    | Fort Tejon M7.9
1838 | Check GUA  | ?              | Point Reyes?  | SF M6.8-7.4
1812 | Jacoby '88 | ?              | Carrizo       | S.CA M7 x2
...
```

### Phase 3: Orphan Detection

Identify proxy anomalies with NO catalog match:
1. Tree ring disturbances without known earthquake
2. Lake turbidites without catalog match
3. Trench events with wide date ranges

### Phase 4: Multi-Proxy Validation

For candidate "dark earthquakes":
- Require ≥2 independent proxy signals
- Check distance attenuation (should be stronger near epicenter)
- Verify timing consistency across proxies

---

## Expected Outputs

1. **CALIFORNIA_1800s_TIMELINE.csv** - Unified proxy timeline
2. **ORPHAN_ANOMALIES.md** - Candidate undocumented earthquakes
3. Updated EARTHQUAKE_MATCHING.md with 1800s California results

---

## Comparison to Italian Methodology

| Aspect | Italian (Bàsura) | California (This Plan) |
|--------|------------------|------------------------|
| Primary proxy | Speleothem δ18O/Mg/Ca | Tree rings + lake sediments |
| Backup proxy | Historical records | Paleoseismic trenches |
| Time resolution | ~Annual | ~Annual (trees), ~Decadal (lakes) |
| Spatial coverage | Single cave | Regional network |
| Discrimination | Mg/Ca ratio | Multi-proxy consensus |

---

## Next Steps

1. **Immediate**: Download ITRDB Fort Ross data, USGS Pallett Creek data
2. **Week 1**: Create Python script for tree ring anomaly detection
3. **Week 2**: Cross-reference with 1838, 1857, 1865 earthquakes
4. **Week 3**: Identify orphan signals requiring further investigation

---

*Created 2024-12-25*
*Part of US Speleothem Paleoseismic Project*
