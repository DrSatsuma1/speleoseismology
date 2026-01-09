# Dos Anas Cave Dark Earthquake Database Verification

## Research Date: 2026-01-03

## Executive Summary

**FINDING**: The ~1400 CE and ~1062 CE dark earthquake candidates at Dos Anas Cave are **PRE-COLUMBIAN earthquakes on MAPPED faults**, not "dark earthquakes" in the sense of unknown source faults. Western Cuba has MAPPED active faults in modern databases, but lacks paleoseismic trenching data to establish prehistoric event chronologies.

**Classification**: These events are "dark" only in the historical sense (predating Spanish colonization), NOT in the geological sense (unmapped structures).

---

## 1. Caribbean Fault Databases Available

### 1.1 GEM Caribbean & Central America Active Fault Database (CCAF-DB)

**Status**: ✅ **EXISTS** - Primary modern fault database for the region

- **Coverage**: ~250 active fault traces from Mexico to Panama, including Greater and Lesser Antilles
- **Published**: Styron et al. (2020), *Natural Hazards and Earth System Sciences*
- **Format**: Shapefile, GeoJSON, KML, GeoPackage
- **Repository**: https://github.com/GEMScienceTools/CCAF-DB
- **Attributes**: Fault geometry, kinematics, slip rates, data quality, uncertainty

**Key Features**:
- Public, open-source (CC-BY 4.0 license)
- Iterative development with community contributions
- Designed for Probabilistic Seismic Hazard Analysis (PSHA)

**Reference**: [Styron et al. 2020, NHESS](https://nhess.copernicus.org/articles/20/831/2020/)

### 1.2 GEM Global Active Faults Database

**Status**: ✅ **INCLUDES Caribbean data from CCAF-DB**

- **Repository**: https://github.com/GEMScienceTools/gem-global-active-faults
- **Format**: Shapefile, interactive map, KML
- Incorporates CCAF-DB data into global compilation

### 1.3 USGS Faults of the Caribbean Region (flt6bg)

**Status**: ⚠️ **OUTDATED** (~2004, 22 years old)

- **Repository**: https://catalog.data.gov/dataset/faults-of-the-caribbean-region-flt6bg
- Basic fault traces WITHOUT detailed slip/hazard attributes
- Use only for broad structural context; prefer CCAF-DB

### 1.4 Cuban National Database

**Status**: ❌ **PARTIAL** - Published fault catalog exists, GIS availability unclear

- Cotilla & Córdoba (2011): "First catalogue of active regional faults of Cuba"
- **12 active faults identified** (out of 30 studied)
- Primary reference: Cotilla, M.O. & Córdoba Barba, D. (2011), *Russian Geology and Geophysics* 52(4): 449-460

---

## 2. Faults Mapped Near Dos Anas Cave

### 2.1 Guane Fault (PRIMARY CANDIDATE)

**Distance**: ~50 km from Dos Anas Cave (22.38°N, 83.97°W)

**Activity Status**: ✅ **HOLOCENE ACTIVE** (confirmed in multiple sources)

- **Seismicity**: ~100 earthquakes documented
- **Maximum magnitude**: M6.2
- **Recurrence**: ~130 years for M6+ events
- **Geographic extent**: Spans 4 provinces (Pinar del Río, Ciudad de La Habana, La Habana, Matanzas)
- **Tectonic mechanism**: Intraplate readjustments via transpression from Caribbean-North American plate interaction

**Historical Events**:
- **January 23, 1880**: San Cristóbal, Pinar del Río earthquake (M~6.2)
- December 16, 1982: Torriente-Jagüey Grande, Matanzas
- March 9, 1995: Pedro Pí-San José de las Lajas, La Habana

**Paleoseismic Status**: ❌ **NO trenching data available**

**References**:
- [Cotilla & Córdoba 2011, "The Guane Active Fault, Western Cuba"](https://www.redalyc.org/journal/4517/451748499007/html/)
- [Cotilla 2011, "Seismicity and seismoactive faults of Cuba"](https://www.sciencedirect.com/science/article/abs/pii/S1068797107001095)

### 2.2 North Cuban Fault

**Distance**: Passes through Pinar del Río region (exact distance to cave unknown)

**Activity Status**: ✅ **ACTIVE** (mapped in CCAF-DB)

- **Type**: Reverse fault
- **Dip direction**: South
- **Slip type**: Reverse
- **Geometry**: Extends from ~85°W to ~77°W along northern Cuba
- **Reference**: García et al. 2003, BSSA

**Paleoseismic Status**: ❌ **NO trenching data available**

**GEM Database Entry**: Catalog ID CA_165.0

### 2.3 Oriente Fault Zone (DISTANT)

**Distance**: ~500 km to eastern Cuba (source of 1766 M7.6)

**Activity Status**: ✅ **HOLOCENE ACTIVE** - Main seismogenic zone

- **Slip rate**: 9-11 mm/yr (GNSS + paleoseismology)
- **Type**: Left-lateral strike-slip (transform plate boundary)
- **Significance**: Accommodates 70% of Cuban seismicity
- **Locking depth**: 25 km
- **Part of**: Bartlett-Cayman fault system (Caribbean-North American plate boundary)

**Paleoseismic Status**: ⚠️ **LIMITED** - No published trench data for Oriente segment specifically

**References**:
- Symithe et al. 2015 (GNSS modeling)
- [García et al. 2003](https://nhess.copernicus.org/articles/20/831/2020/)

### 2.4 Septentrional Fault (DISTANT)

**Distance**: ~600 km (Hispaniola)

**Activity Status**: ✅ **HOLOCENE ACTIVE**

- **Slip rate**: 6-12 mm/yr (paleoseismology)
- **Recurrence**: 800-1200 years for M7+ events
- **Last event**: A.D. 1040-1230 (most recent ground-rupturing earthquake)
- **Penultimate event**: Post-A.D. 30

**Paleoseismic Status**: ✅ **TRENCHING COMPLETED** (Prentice et al. 2003)

- Minimum 4 m left-lateral slip + 2.3 m normal dip slip
- At least 2 paleoseismic surface breaks dated 30-40 B.C.
- Event chronology: A.D. 30 → A.D. 1040-1230

**References**:
- [Prentice et al. 2003, JGR](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2001jb000442)

---

## 3. Paleoseismic Data Availability

### 3.1 Paleoseismic Trenching

**Cuba**: ❌ **NONE AVAILABLE**

From project documentation (CUBA_CAVES_COMPLETE.md):
> "No paleoseismic trench data exists for the Oriente fault - Cuba's main seismic zone lacks prehistoric earthquake chronology"

**Caribbean Region**: ⚠️ **MINIMAL**

- Septentrional fault (Dominican Republic): ✅ Complete (Prentice et al. 2003)
- El Salvador fault zone: ✅ Available (mean recurrence 800 years)
- Oriente fault (Cuba): ❌ None
- Guane fault (western Cuba): ❌ None

### 3.2 Marine Turbidite Records

**Puerto Rico Trench**: ❌ **"LARGELY UNKNOWN"** (USGS)

From project documentation (CUBA_CAVES_COMPLETE.md):
> "Puerto Rico Trench turbidite ages are 'largely unknown' (USGS) - No submarine paleoseismic record available for cross-validation"

**Caribbean Basins**:
- Anegada Passage: Youngest turbidite ~2600 years old
- **No evidence** of turbidites from 1867 Virgin Islands M7.2 earthquake
- **No Medieval turbidites** documented for ~1400 CE or ~1062 CE windows

**Reference**: [USGS Event Sedimentation Study](https://www.usgs.gov/publications/event-sedimentation-low-latitude-deep-water-carbonate-basins-anegada-passage-northeast)

### 3.3 Historical Records

| Period | Documentation Status | Coverage |
|--------|---------------------|----------|
| **Pre-1492** | ❌ NO written records | Pre-Columbian - NO DATA |
| **1492-1515** | ⚠️ Minimal (exploration) | Spanish arrival, limited settlement |
| **1515-1578** | ⚠️ Sparse (early colonial) | Santiago de Cuba founded 1515 |
| **1578-present** | ✅ Systematic (colonial) | First documented earthquake 1578 |

**Catalog Extension**: Dos Anas speleothem extends record **831 years** (1578 → 747 CE)

---

## 4. Event Classification: "Dark" vs "Pre-Columbian"

### 4.1 Definitions (from CLAUDE.md)

**Dark Earthquake**:
> Seismic event with physical evidence but **no mapped source fault** after checking ALL modern databases (SCEC CFM, state surveys, published studies, DEM analysis). Does NOT mean merely "absent from historical catalogs."

**Pre-Historical / Pre-Columbian Earthquake**:
> Event predating written records in region (e.g., pre-1492 Caribbean) but occurs on a **known, mapped fault**. Extends earthquake catalogs but is NOT "dark."

### 4.2 Dos Anas Events: Classification

| Event | Date Window | Speleothem Signal | Historical Record | Mapped Faults Nearby | Classification |
|-------|-------------|-------------------|-------------------|---------------------|----------------|
| **1768 peak** | 1766 M7.6 | z=-2.74 (strongest in 1253 yr) | ✅ Santiago de Cuba | Oriente fault | **VALIDATED** |
| **~1400 CE** | Anomaly: 1393-1408 CE | z=-2.41, 7 samples z<-1.5 | ❌ Pre-Columbian | Guane (~50 km), N Cuban | **PRE-COLUMBIAN** |
| **~1062 CE** | Anomaly: 1058-1084 CE | z=-2.38, dual peaks | ❌ Pre-Columbian | Guane (~50 km), N Cuban | **PRE-COLUMBIAN** |
| **~1792 CE** | 26 yr after 1766 | z=-2.18 | ❌ Gap in catalog | Oriente (stress transfer?) | **CANDIDATE** |
| **~1533 CE** | Early colonial | z=-2.14, dual peaks 1523/1533 | ❌ Pre-1578 gap | Guane or Oriente | **CANDIDATE** |

### 4.3 Verdict: NOT "Dark Earthquakes"

**Reasoning**:
1. **Faults ARE mapped**: Guane Fault (50 km), North Cuban Fault, and Oriente fault (500 km) all appear in CCAF-DB
2. **Events predate records**: ~1400 CE and ~1062 CE occurred before Spanish colonization (1492)
3. **Paleoseismic gap**: No trenching exists to validate/refute these events, but lack of trenching ≠ unmapped fault

**Proper classification**: **PRE-COLUMBIAN EARTHQUAKES ON KNOWN FAULTS**

**Analogous to**:
- Crystal Cave 1741 CE (Kern Canyon Fault - Holocene active, pre-Spanish)
- Rose Canyon 1741 CE (Mapped fault, pre-Spanish)
- Minnetonka ~1676 CE (Wasatch Nephi segment - paleoseismic match)

---

## 5. Seismogenic Source Analysis

### 5.1 Distance vs Magnitude Threshold

From validation (CUBA_CAVES_COMPLETE.md):
- **1766 M7.6 at ~500 km**: z=-2.74 (STRONG signal)
- **1852 M6.75 at ~500 km**: z=-1.72 (WEAK signal)
- **Threshold**: M7.5+ required for detection at 500 km distance

### 5.2 Candidate Sources for ~1400 CE and ~1062 CE

**Option 1: Guane Fault (~50 km)**
- **Magnitude**: M6.2 maximum observed (1880 event)
- **Expected signal**: z > -3.0 if similar to Crystal Cave 1896 M6.3 (z=-3.54 at 48 km)
- **Observed signal**: ~1400 CE z=-2.41, ~1062 CE z=-2.38
- **Assessment**: **CONSISTENT** - signals match expected magnitude for local fault

**Option 2: Oriente Fault (~500 km)**
- **Magnitude**: M7.6 required for strong signal (1766 validation)
- **Observed signal**: ~1400 CE z=-2.41, ~1062 CE z=-2.38
- **Assessment**: **TOO WEAK** - signals weaker than 1766, suggesting smaller or more distant event

**Option 3: Septentrional Fault (~600 km)**
- **Last event**: A.D. 1040-1230 (Prentice et al. 2003)
- **~1062 CE timing**: Falls within paleoseismic window (1040-1230)
- **Magnitude**: M7+ expected (4 m slip)
- **Distance**: 600 km (even farther than Oriente)
- **Assessment**: **POSSIBLE CORRELATION** - timing matches, but distance problematic

### 5.3 Most Likely Scenario

**~1400 CE**: **Guane Fault M6-6.5 local event** (50 km)
- Signal strength consistent with local moderate earthquake
- 7-sample cluster suggests real seismic disturbance
- No alternative explanation (no volcanic forcing, no drought evidence)

**~1062 CE**: **DUAL POSSIBILITY**
1. **Guane Fault M6+ local event** (dual peaks 1062/1084 suggest earthquake doublet)
2. **Septentrional Fault M7+** (timing overlaps paleoseismic window 1040-1230, but distance problematic)

**Cross-check needed**: Compare ~1062 CE signal with Septentrional paleoseismic dates (Prentice et al. 2003)

---

## 6. What's Missing: The Paleoseismic Gap

### 6.1 Critical Data Gaps

**No paleoseismic trenching on**:
- Guane Fault (western Cuba)
- North Cuban Fault
- Oriente Fault (eastern Cuba)

**No turbidite chronology for**:
- Puerto Rico Trench
- Caribbean basins (Medieval period)

**Result**: **IMPOSSIBLE to independently validate pre-1578 earthquakes** using traditional paleoseismology

### 6.2 Why Dos Anas Matters

**Unique contribution**: Dos Anas speleothem provides the **ONLY paleoseismic record** for western Cuba

From CUBA_CAVES_COMPLETE.md:
> "Extensive search of historical records, archaeological literature, and paleoseismic databases reveals that the Dos Anas speleothem provides the **ONLY** paleoseismic record for pre-colonial Cuba."

**Scientific value**:
- Extends catalog 831 years (1578 → 747 CE)
- Identifies 7 candidate events (2 high confidence: ~1400, ~1062)
- May reveal previously unknown seismic cycle on Guane Fault

---

## 7. Implications for Publication

### 7.1 Correct Terminology

**DO NOT USE**: "Dark Earthquakes" for Dos Anas pre-Columbian events

**USE INSTEAD**:
- "Pre-Columbian earthquakes on mapped faults"
- "Historically undocumented seismic events"
- "Extending the Caribbean paleoseismic record before Spanish colonization"

### 7.2 Comparison to Other Findings

| Event | Fault Status | Record Status | Classification |
|-------|--------------|---------------|----------------|
| **Italy 1285** | ✅ Mapped (DBMI15 documented) | ✅ Historical validation | **VALIDATED** |
| **California 1741** | ✅ Mapped (Kern Canyon, Holocene active) | ❌ Pre-Spanish | **PRE-SPANISH** |
| **San Diego 1741** | ✅ Mapped (Rose Canyon, SCEC CFM) | ❌ Pre-Spanish | **PRE-SPANISH** |
| **Minnetonka ~1676** | ✅ Mapped (Wasatch Nephi segment) | ✅ Paleoseismic match | **VALIDATION** |
| **Cuba ~1400 CE** | ✅ Mapped (Guane Fault, CCAF-DB) | ❌ Pre-Columbian | **PRE-COLUMBIAN** |
| **Cuba ~1062 CE** | ✅ Mapped (Guane or Septentrional) | ❌ Pre-Columbian | **PRE-COLUMBIAN** |

**Pattern**: ALL US and Caribbean "dark" candidates occur on **KNOWN faults** after database verification

### 7.3 Updated Paper Framing

**Original framing** (incorrect):
> "Dark earthquakes with no mapped source fault"

**Corrected framing**:
> "Speleothem paleoseismology extends earthquake catalogs centuries before instrumental and historical records, revealing pre-Columbian seismicity on mapped faults that lack paleoseismic trenching data."

**Soundbite**:
> "We're not finding unknown faults - we're finding unknown earthquakes on known faults."

---

## 8. Recommendations

### 8.1 Immediate Actions

1. **Cross-reference Septentrional paleoseismic dates**
   - Check if Prentice et al. 2003 event (A.D. 1040-1230) could produce signal at 600 km
   - Calculate expected z-score for M7 at 600 km using Chiodini model

2. **Update PAPER_2_DARK_EARTHQUAKES.md**
   - Reclassify Dos Anas events as "PRE-COLUMBIAN" not "DARK"
   - Add fault database verification section
   - Emphasize unique contribution: only paleoseismic record for western Cuba

3. **Contact Cuban researchers**
   - Inquiry about Guane Fault paleoseismic trenching plans
   - Share speleothem findings to motivate field validation

### 8.2 Future Research

1. **Paleoseismic trenching on Guane Fault**
   - Target ~1400 CE and ~1062 CE event windows
   - Validate/refute speleothem candidates
   - Establish recurrence interval

2. **Marine core analysis**
   - Search for Caribbean turbidites in Medieval period
   - Cross-validate with speleothem dates

3. **Archaeological correlation**
   - Survey Taíno settlement patterns around ~1400 CE
   - Look for destruction layers in western Cuba sites

---

## 9. Sources

### Fault Databases
- [GEM CCAF-DB (Styron et al. 2020, NHESS)](https://nhess.copernicus.org/articles/20/831/2020/)
- [GEM Global Active Faults GitHub](https://github.com/GEMScienceTools/gem-global-active-faults)
- [USGS Faults of the Caribbean Region](https://catalog.data.gov/dataset/faults-of-the-caribbean-region-flt6bg)

### Cuban Faults
- [Cotilla & Córdoba 2011 - Guane Active Fault](https://www.redalyc.org/journal/4517/451748499007/html/)
- [Cotilla & Córdoba 2011 - Seismicity and Seismoactive Faults](https://www.sciencedirect.com/science/article/abs/pii/S1068797107001095)

### Septentrional Fault Paleoseismology
- [Prentice et al. 2003 - Slip Rate and Recurrence](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2001jb000442)

### Caribbean Turbidites
- [USGS - Event Sedimentation, Anegada Passage](https://www.usgs.gov/publications/event-sedimentation-low-latitude-deep-water-carbonate-basins-anegada-passage-northeast)
- [Annual Reviews - Submarine Paleoseismology](https://www.annualreviews.org/doi/abs/10.1146/annurev-marine-120709-142852)

### USGS Caribbean Studies
- [Caribbean Tsunami and Earthquake Hazards](https://www.usgs.gov/centers/whcmsc/science/caribbean-tsunami-and-earthquake-hazards-studies)
- [Historical Earthquakes in Northeastern Caribbean](https://www.usgs.gov/publications/accounts-damage-historical-earthquakes-northeastern-caribbean-aid-determination-their)

---

*Document created: 2026-01-03*
*Verification: GEM CCAF-DB, USGS Caribbean databases, published paleoseismic literature*
