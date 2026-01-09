# CLAUDE Reference Guide

## Comprehensive Reference for Databases, Proxies, Terminology & Publication

---

**When to read this**: You're interpreting geochemical data, conducting database searches, writing analysis, or need technical definitions.

---

# PART I: CORE CONCEPTS & TERMINOLOGY

## 1.1 Dark Earthquake

**Definition**: A seismic event that (1) actually occurred (physical evidence exists), (2) is absent from historical earthquake catalogs, (3) was "erased" or forgotten due to historical/political circumstances, and (4) can only be recovered through forensic multi-proxy paleoseismic methods.

**Project examples**:

| Event | Rank | Evidence | Catalog Status | Why Lost |
|-------|------|----------|----------------|----------|
| **1285** | #1 | -6.718 permil d18O | MISSING | War of Sicilian Vespers, Battle of Meloria, 4 monarchs died |
| **1394** | #3 | -6.625 permil d18O | MISSING | Great Western Schism, Genoese Revolution |

**Key distinction**: Not a "phantom earthquake" (never happened) but a real seismic event with physical traces that were simply not recorded by chroniclers.

## 1.2 Titan Event

**Definition**: A compound volcanic-seismic-hydrological catastrophe where major volcanic eruption triggers hydrological extremes and potentially couples with seismic activity on regional faults.

**Mechanism**:
1. Volcanic eruption injects sulfate into stratosphere
2. Volcanic winter -> climate anomaly -> hydrological forcing
3. Hydrological loading/unloading on crust triggers seismic slip
4. Seismic event releases aquifer fluids into cave system
5. Isotope anomaly records both components

**Project example - 1285 Titan Event**:
- **1286**: UE6 eruption (~15 Tg S, bipolar signal)
- **1285**: October Genoa flood + proposed Ligurian earthquake
- **Signature**: -6.718 permil d18O, sawtooth recovery (deep aquifer flush)

## 1.3 Recurrence Intervals

| Event Year | Interval from Previous |
|------------|------------------------|
| 1285 | -- |
| 1394 | 109 years |
| 1564 | 170 years |
| 1887 | 323 years |
| **2025** | **138 years** |

**Pattern**: Major events (M 5.8+) every 100-200 years on average.
**Implication**: 138 years since 1887 means we're in expected recurrence window.

---

# PART II: EVIDENCE TIER SYSTEM

## 2.1 Tier 1: Multi-Proxy Confirmation (Highest Confidence)

**Requirements**: d18O anomaly + d13C + trace elements (Mg/Ca and/or Sr/Ca) + strong historical documentation

**CRITICAL CAVEAT**: BA18-4 has **ZERO d13C measurements**. Full Tier 1 confirmation requires d13C analysis not currently available.

**Current Tier 1 Status (with available proxies)**:
| Event | d18O | Mg/Ca | Historical | d13C | Status |
|-------|------|-------|------------|------|--------|
| 1285 | -2.46sigma | +2.25sigma | Flood, notarial gap* | Cross-cave (Klapferloch) | **CVSE (Tier 1)** |
| 1394 | -2.31sigma | +1.60sigma | Vatican*, wills* | MISSING | **CANDIDATE** (lacks δ13C, short recovery) |

*Archival evidence based on index/metadata searches; requires independent verification of primary documents.

## 2.2 Tier 2: Strong Proxy + Historical (Good Confidence)

**Requirements**: d18O anomaly + strong historical record (limited geochemical confirmation)

**Examples**: 1816 Tambora, 1641 post-seismic, 1786-1787

## 2.3 Tier 3: Single Proxy or Weak Evidence (Lower Confidence)

**Requirements**: d18O anomaly alone, conflicting signals, or weak historical match

**Action**: Flag for future research. Don't publish as standalone finding.

---

# PART III: MULTI-PROXY INTERPRETATION GUIDE

## 3.1 d18O (Oxygen Isotopes) - Primary Anomaly Detector

**Role**: Identifies major environmental perturbations

**Interpretation**:
- **Negative spike** (lower d18O) = Wet conditions (seismic OR climatic - needs discrimination)
- **Positive spike** (higher d18O) = Dry conditions (typically climatic)
- **Magnitude ranking**: Use absolute Z-score (|Z| = |value - mean| / sigma)

**Recovery patterns** (critical for seismic identification):
- **Sawtooth shape** with 15-20 year recovery = Deep aquifer disturbance (SEISMIC)
- **Spike with rapid recovery** (1-3 years) = Climate event

## 3.2 d13C (Carbon Isotopes) - Seismic vs. Biogenic Discriminator

**CRITICAL CAVEAT**: BA18-4 has ZERO d13C measurements. This methodology CANNOT be applied without new sample analysis.

**Theoretical interpretation**:
- **d13C > -8 permil** = Geogenic CO2 from deep faults (SEISMIC)
- **d13C < -10 permil** = Biogenic CO2 from soil/vegetation (CLIMATIC)
- **d13C -8 to -10 permil** = Mixed signal (needs additional proxies)

**Chiodini Mass Balance** (quantifies geogenic fraction):
```
f_geog = (d13C_sample - d13C_background) / (d13C_deep - d13C_background)

Where:
- d13C_background = biogenic baseline (~-12.5 permil)
- d13C_deep = deep crustal source (~-3.0 permil)

Result:
- f_geog > 40% = Quantitative proof of fault degassing
- f_geog < 20% = Primarily biogenic/climatic
```

## 3.3 Mg/Ca Ratio - Aquifer Fracture Signature

**Role**: Confirms seismic activity by detecting deep water dissolution

**Interpretation**:
- **HIGH Mg/Ca** = Deep, high-temperature groundwater (SEISMIC)
  - Longer water-rock interaction time
  - Aquifer fracture allows deep water to reach speleothem
- **LOW Mg/Ca** = Fresh, shallow meteoric water (CLIMATIC)
  - Quick transit from surface (rainfall)
  - Dilution by flood waters

**Project examples**:
| Event | Mg/Ca Z-score | Interpretation |
|-------|---------------|----------------|
| 1285 | +2.25sigma | SEISMIC (deep water) |
| 1394 | +1.60sigma | SEISMIC (deep water) |
| 1649 | -0.57sigma | CLIMATIC (meteoric) |
| 1656 | -0.48sigma | CLIMATIC (meteoric) |

## 3.4 Sr/Ca Ratio - Rock-Water Interaction

**Role**: Supports Mg/Ca findings through independent dissolution pathway

- **HIGH Sr/Ca** = Old water or enhanced dissolution (supports seismic)
- **LOW Sr/Ca** = Fresh meteoric water (supports climatic)

**Strategy**: Always interpret Sr/Ca alongside Mg/Ca (should agree)

## 3.5 Pattern Combinations (Most Diagnostic)

| Pattern | Interpretation |
|---------|----------------|
| High Mg/Ca + Negative d18O + d13C > -8 permil | **SEISMIC CONFIRMED** |
| Low Mg/Ca + Negative d18O + d13C < -10 permil | **CLIMATIC CONFIRMED** |
| Mg/Ca decoupled from d18O | **Diagnostic** (depth change without surface change) |

## 3.6 Recovery Time Analysis

| Type | Recovery Time | Pattern |
|------|---------------|---------|
| SEISMIC | >10 years (often 15-20) | Sawtooth as aquifer drains |
| CLIMATIC | 1-3 years | Spike then rapid return to baseline |

**Measurement**: Time from anomaly onset to return to +/-2sigma of pre-event baseline

---

# PART IV: DATABASE ACCESS & SEARCH STRATEGIES

## 4.1 Speleothem Data

### SISAL v3 (Primary Database)
- **URL**: https://doi.org/10.5287/ora-2nanwp4rk
- **Documentation**: https://essd.copernicus.org/articles/16/1933/2024/
- **Contents**: 1,271 speleothem records globally with d18O, d13C, Mg/Ca, Sr/Ca, Ba/Ca

**Query strategy for this project**:
1. Filter location: Italy (lat 36-47 deg N, lon 6-19 deg E)
2. Look for: Trace element data (Mg/Ca, Sr/Ca, Ba/Ca)
3. Time window: Medieval period (1000-1600 CE minimum)
4. Priority caves: Basura, Corchia, Renella, other Ligurian sites

### NOAA BA18-4 Archive
- **URL**: https://www.ncei.noaa.gov/access/paleo-search/study/40703
- **Data types**: d18O (265 samples), Mg/Ca, Sr/Ca, Ba/Ca (171 samples each)
- **Time coverage**: 1198-1946 CE
- **Key**: This is THE critical database for 1285 seismic signature

**CRITICAL DATA GAP**: BA18-4 lacks d13C. Despite methodology references, d13C discrimination CANNOT be applied without new sample analysis.

## 4.2 Earthquake Catalogs

### CFTI5Med (Complete Catalog)
- **URL**: http://storing.ingv.it/cfti/cfti5/
- **Coverage**: Italy, M 4.5-6.5 events, extended historical period
- **Advantage**: Includes smaller earthquakes that CPTI15 misses

**Query strategy**:
- Region: Liguria (44-45 deg N, 7-9 deg E)
- Time: 1280-1295 CE and +/-50 years
- Search: "Liguria", "Genova", "Albenga", "Toirano"
- Note: Look for GAPS (absence = lost from catalogs)

### CPTI15 (Italian Earthquake Parameters)
- **URL**: https://emidius.mi.ingv.it/CPTI15-DBMI15/
- **Coverage**: Italy, M >= 4.5
- **Feature**: Parametric data (magnitude, depth, focal mechanism)

### DBMI-15 (Macroseismic Database)
- **URL**: https://emidius.mi.ingv.it/DBMI15/
- **Data type**: Intensity observations
- **Use case**: Historical intensity reports, building damage descriptions

### AHEAD (European Historical Earthquake Data)
- **URL**: https://www.emidius.eu/AHEAD/
- **Coverage**: All of Europe + Mediterranean
- **Use case**: Pan-Mediterranean event correlation

### SisFrance (French Historical Seismicity)
- **URL**: www.sisfrance.net
- **Managed by**: BRGM, EDF, IRSN consortium
- **Coverage**: French historical seismicity from 462 CE to present
- **Use case**: Cross-border verification for Western Liguria events
- **Query strategy**: Search 1280-1290 CE for Nice/Menton/Alpes-Maritimes
- **Note**: If SisFrance shows silence for 1285 in Provence, this constrains epicenter to Eastern Liguria (Toirano)

### ASMI (Italian Archive of Historical Earthquake Data)
- **URL**: https://emidius.mi.ingv.it/ASMI/index_en.php
- **Documentation**: https://essd.copernicus.org/articles/17/3109/2025/
- **Use case**: Raw historical sources behind CPTI15 entries

## 4.3 Volcanic Forcing (Ice Cores)

### eVolv2k v4
- **URL**: https://doi.org/10.1594/PANGAEA.971968
- **Reference**: Sigl & Toohey (2024)
- **Coverage**: 500 BCE - 1900 CE, 256 eruptions

### Sigl et al. Volcanic Chronology
- **Primary ref**: Sigl et al. (2015) Nature 10.1038/nature14565
- **What to extract**: Sulfate flux (kg/km2), core locations, VEI classification

**Key finding**: 1286 UE6 ~ 15 Tg S, bipolar signal, tropical eruption

### Cross-Validation Proxies

| Proxy | Source | Use |
|-------|--------|-----|
| Lake Savine floods | Wilhelm et al. 2017 | Hydrological component |
| Var Sedimentary Ridge | Hassoun et al. 2009 | Offshore turbidites |
| Alpine tree rings | NOAA Paleoclimatology | Growth disturbances |

---

# PART V: ARCHIVAL RESEARCH STRATEGIES

## 5.1 Archivio di Stato di Genova (ASGe)

**Collections**: Notai Antichi (medieval notaries)

**Search strategy for 1285 and 1394**:

| Document Type | Search Term | Expected Finding |
|---------------|-------------|------------------|
| Emergency wills | "timens subitaneam mortem" (in mortal danger) | Clustering in autumn 1285, 1394 |
| Regular wills | WITHOUT "infirmitate gravatus" | Distinguishes seismic from disease |
| Fiscal records (Gabelle) | Tax exemptions/reductions | 1395-1396 waiver for Albenga |
| Commercial records | Gift-pulse to monasteries | 1285-1286 donations |

## 5.2 Vatican Archives (Archivio Apostolico Vaticano)

**Collection**: Regesta Vaticana (papal registers)
- Volumes for 1285: 312-315 (approximate)
- Volumes for 1394: Gregory IX era

**Search terms**:
- "Albenga" (region)
- "ruina" or "reparatio" (destruction/repair)
- "propter ruinam et paupertatem" (due to destruction and poverty)
- "Savona", "Toiranum", "Sanctus Petrus de Montibus"

**Expected**: Supplications from Carthusian monasteries, repair writs

## 5.3 Other Archives

| Archive | Location | Use |
|---------|----------|-----|
| Albenga Diocesan | Local | Visite Pastorali, repair accounts |
| Messina Archives | Sicily | 1613 event verification |

## 5.4 Search Strategy Flowchart

For any orphan anomaly year:

1. **CFTI5Med/CPTI15** -> Any earthquake M 5-6.5?
2. **DBMI-15** -> Any intensity reports?
3. **Historical archives** -> Any damage documentation?
4. **AHEAD** -> Pan-European search?
5. **Ice cores** -> Volcanic eruption 1-5 years before?
6. **Lake records** -> Flood peak at same time?
7. **Offshore (Var)** -> Turbidite dated to same year?
8. **Tree rings** -> Growth disturbance?

**If ANY 2-3 independent sources confirm -> Publishable!**

---

# PART VI: MANUSCRIPT REQUIREMENTS

## 6.1 Target Journal Requirements

### Nature
- **Length**: ~8,000 words main text
- **Figures**: Max 4 (+ unlimited supplementary)
- **Key requirement**: "Fundamental significance"
- **Our angle**: Novel paleoseismic methodology + "dark earthquakes" discovery

### Science
- **Length**: ~7,000 words
- **Figures**: Max 5
- **Key requirement**: "Importance to broad scientific community"
- **Our angle**: Earthquake hazard + methodology advancement

## 6.2 Proposed Manuscript Structure

1. **Title**: "Speleothem geochemistry reveals unknown earthquakes: 750-year paleoseismic record from Basura Cave, Italy"

2. **Abstract** (300 words max)
   - 32 d18O anomalies correlated retrospectively; 6/6 blind validation test events detected
   - Two "dark earthquakes" discovery
   - Novel volcanic-seismic coupling
   - Mediterranean hazard implications

3. **Introduction** - Methods overview, research questions

4. **Methods** - Site description, isotope procedures, statistical analysis

5. **Results** - 32 anomalies, multi-proxy validation, 1285 and 1394 detail

6. **Discussion** - Methodology implications, coupling mechanism, hazard reassessment

7. **Conclusions** - Method validated, earthquakes recovered, future directions

8. **Supplementary Materials** - All 32 anomalies table, archival excerpts, ice core data

## 6.3 Red Flags to Avoid

### DON'T claim without supporting data:
- Don't publish 1285 seismic event without Mg/Ca confirmation (NOW AVAILABLE)
- Don't claim "dark earthquake" without archival evidence
- Don't use predictions instead of lab measurements in final manuscript

### DON'T overstate certainty:
- Use "proposed" and "likely" for features without independent verification
- Acknowledge alternative explanations explicitly
- Flag temporal resolution limits

### DON'T ignore methodology questions:
- Expect criticism on: single-cave bias, chronological uncertainty
- Pre-answer with: cross-cave confirmation, multiple dating methods, multi-proxy

---

# PART VII: WRITING STANDARDS

## 7.1 Evidence Statements

**Weak**: "The d18O anomaly at 1285 suggests an earthquake."

**Strong**: "The d18O anomaly at 1285 (-6.718 permil, |Z|=4.5, rank #1) matches predicted seismic signature: sawtooth recovery (15-20 years) consistent with deep aquifer fracture, confirmed by Mg/Ca (+2.25sigma)."

## 7.2 Hypothesis Language

| Term | Meaning |
|------|---------|
| **Confirmed** | Multi-proxy agreement + independent documentation |
| **Likely/Probable** | Multiple lines of evidence but some gaps |
| **Proposed** | Physical evidence present but alternatives exist |
| **Possibly/Candidate** | Single-proxy, needs confirmation |

## 7.3 Caveat Language

Always include:
- "Temporal resolution limits our ability to distinguish..."
- "Dating uncertainty (+/-X years) prevents definitive attribution to..."
- "This interpretation assumes... alternative explanation would be..."
- "Additional analysis needed: [specific next step]"

## 7.4 Citation Standards

| Type | Format |
|------|--------|
| File references | "See MULTIPROXY_FRAMEWORK.md for methodology" |
| Database references | "SISAL v3 database shows [data]" |
| Archive references | "ASGe Notai Antichi documents [finding]" |
| Literature | Author (Year) |

---

# PART VIII: GEOLOGICAL CONTEXT - BASURA CAVE

## 8.1 Site Characteristics

**Location**: 44.13 deg N, 8.20 deg E, Toirano, Liguria, Italy
- ~30 km from Gulf of Genoa coast
- Alpine margin of Apennines

**Host Rock**: Dolostone (San Pietro dei Monti Formation)
- Dolomite (CaMg(CO3)2) more soluble than limestone
- Creates deeper, more complex cave systems

**Nearby Features**:
- Thermal/sulfidic springs 500 m away
- **Significance**: Indicates deep crustal connectivity
- **Consequence**: d13C > -8 permil at Basura is DEFINITELY geogenic

**Seismic Setting**:
- Toirano-Albenga fault zone
- Alpine collision margin
- Active stress accumulation

## 8.2 Why This Location Matters

The proximity to thermal springs means the cave system is hydraulically connected to deep crustal structures. When earthquakes fracture the aquifer, deep CO2-rich fluids can reach the speleothem quickly. This makes Basura exceptionally sensitive to seismic activity compared to caves in stable regions.

---

# PART IX: STATISTICAL METHODS

## 9.1 Anomaly Detection

**Z-score methodology**:
```
Z = (X - mu) / sigma

Where:
- X = measured d18O value (permil)
- mu = mean of background period
- sigma = standard deviation of background
```

**Significance thresholds**:
- |Z| > 2 = moderately unusual
- |Z| > 3 = statistically significant
- |Z| > 4 = extremely significant

**Project example**: 1285 anomaly has |Z| ~ 4.5+ (among highest in record)

## 9.2 PELT Changepoint Detection

**Method**: Automatic algorithm that finds regime shifts in time series
- Identifies when mean level changes
- Doesn't require manual threshold setting
- Used to find boundaries of anomalies

## 9.3 Monte Carlo Permutation Testing

**Method**: Randomize data many times; if real event matches documented historical dates > 99% of shuffled matches, it's significant (p < 0.01)

**Project result**: p = 0.004 for correlation between speleothem anomalies and documented earthquakes

**Plain language**: If we shuffled the record into random dates, we'd only randomly match this many events about 4 times in 1000 shuffles. The real-world match is not coincidence.

---

# PART X: QUICK REFERENCE CHECKLISTS

## 10.1 Interpreting a New Anomaly

1. **d18O magnitude**: Is it significant? (|Z| > 2?)
2. **Recovery pattern**: Sawtooth (>10 yrs) or spike (<3 yrs)?
3. **d13C** (if available): > -8 permil or < -10 permil?
4. **Mg/Ca** (if available): High or low? Coupled/decoupled?
5. **Sr/Ca** (if available): Does it agree with Mg/Ca?
6. **Historical record**: Documented event +/-5 years?
7. **Alternative explanations**: Climate? Volcanic? Flood?
8. **Confidence tier**: 1, 2, or 3?
9. **Next step**: What analysis would increase confidence?

## 10.2 Before Finishing Any Document

- [ ] All anomalies have Tier rating (1, 2, or 3)?
- [ ] Evidence hierarchy clear (data > historical > inference)?
- [ ] Caveats explicitly stated?
- [ ] Alternative explanations acknowledged?
- [ ] Source citations complete?
- [ ] No overstatement of certainty?
- [ ] Cross-references to related docs added?
- [ ] Status indicators present?

## 10.3 When Data is Missing

- No Mg/Ca? Use d13C + recovery time as discriminator
- No d13C? Assume multiple scenarios until proven (BA18-4 situation)
- No historical record? Classify as "orphan anomaly"
- Conflicting signals? Flag as "ambiguous"

**Always be transparent about what's missing and what's assumed.**

---

*Reference document consolidated December 2024*
*Merged from: CLAUDE_DATABASES.md, CLAUDE_PROXY_REFERENCE.md, CLAUDE_PUBLICATION.md, CLAUDE_TERMINOLOGY.md*
