# CLAUDE.md - Paleoseismic Cave Research Project

## Project Overview

This project uses speleothem (cave formation) geochemistry to **identify time windows and locations warranting investigation** for possible seismic activity. Speleothems record disturbances through oxygen isotope (δ18O) and carbon isotope (δ13C) anomalies, but **cannot independently confirm earthquakes** due to signal complexity and multiple competing mechanisms.

**Goal**: Develop speleothem anomaly analysis as a **targeting tool** for paleoseismic investigation - directing where to look for unmapped faults and when to search for undocumented events. Publication focus shifts from "earthquake detection" to "anomaly-guided paleoseismic exploration."

### ⚠️ Strategic Pivot (2026-01-03)

**What speleothems CAN do:**
- Record that *something* disturbed the cave system at a given time
- Identify anomaly clusters that may warrant investigation
- Provide time windows for paleoseismic trench targeting
- Flag regions where unmapped faults may exist

**What speleothems CANNOT reliably do:**
- Distinguish seismic from climatic/volcanic/hydrological signals with δ18O alone
- Detect earthquakes consistently (1872 Owens Valley M7.4 at 65 km produced only z=-1.13)
- Attribute specific anomalies to specific earthquakes without independent confirmation

**The path forward**: Multivariate analysis combining multiple proxies, multiple caves, and independent verification (paleoseismic trenches, tree rings, lake turbidites, DEM lineament analysis).

### Validation Status (Revised)

Previous claims of 6/6 detection rate are **withdrawn**. The 1872 Owens Valley M7.4 non-detection (z=-1.13 at 65 km) demonstrates inconsistent response. Post-hoc selection of "detected" events created confirmation bias. True detection capability remains **unvalidated**.

### Methodological Approach (2024-12-29)

**We are not aware of prior work combining these approaches.** Traditional speleoseismology uses **physical damage** (broken formations, tilted stalagmites). We apply **Chiodini's hydrogeochemical model** (earthquake → CO2 flux → groundwater chemistry change) to **speleothem geochemistry** (δ18O, Mg/Ca, δ13C anomalies). Literature searches have not identified similar methodologies, but absence of evidence is not evidence of absence.

| Approach | Method | Reference |
|----------|--------|-----------|
| Traditional speleoseismology | Physical damage | [Forti 2001](https://digitalcommons.usf.edu/kip_articles/4746/), [Pace 2020](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2020TC006289) |
| Chiodini hydrogeochemistry | Groundwater monitoring | [Chiodini 2011](https://www.sciencedirect.com/science/article/abs/pii/S0012821X11000872) |
| **Our methodology** | Chiodini model + speleothem archives | **No prior work found (to our knowledge)** |

### Anomaly-Earthquake Correlations (Not Validated Detections)

**Some anomalies correlate with known earthquakes, but correlation ≠ detection:**

| Anomaly | Correlation | Independent Record | Status |
|---------|-------------|-------------------|--------|
| 1766 Cuba z=-2.74 | Temporal match | Historical M7.6 | Correlation only |
| Cascadia T5, S, W | Within windows | Goldfinger turbidites | Correlation only |
| ~1676 Wasatch z=+2.63 | Temporal match | DuRoss paleoseismic | Correlation only |
| **1902 Crystal Cave z=-3.54** | **Attributed to 1896** | **BUT 1872 M7.4 not detected** | **WITHDRAWN** |

**Critical failure**: Crystal Cave shows z=-3.54 around 1902 (attributed to 1896 M6.3 at 48 km) but only z=-1.13 for 1872 M7.4 at 65 km. The larger, closer earthquake produced a weaker signal. This inconsistency invalidates the detection claim.

**Correlations may be coincidental.** Without consistent detection of known events, we cannot claim validated methodology. See `regions/north_america/CRYSTAL_CAVE_ANALYSIS.md` for full discussion.

### Paleoseismic Trench Correlations (2026-01-01)

**Some anomaly time windows overlap with independently dated paleoseismic events:**

| Anomaly Window | Paleoseismic Source | Overlap | Interpretation |
|----------------|---------------------|---------|----------------|
| ~1285 | Pallett Creek (Sieh 1984) | 1257-1322 CE | Time window overlap |
| ~1580 | Carrizo Plain (Akciz 2009) | 1540-1630 CE | Time window overlap |
| ~1741 | Old Town (Singleton 2019) | "mid-18th century" | Time window overlap |
| ~402 CE | Lake Ladik (Fraser 2009) | 17-585 AD | Time window overlap |

**These overlaps are encouraging but do not validate detection.** Radiocarbon windows are wide (50-100+ years), and coincidental overlap is possible. The value is in **targeting**: anomaly windows can direct paleoseismologists to investigate specific time periods.

**Reframed purpose**: Speleothem anomalies identify *when to look*, paleoseismic trenches confirm *what happened*.

---

## The Multivariate Path Forward

Single-proxy speleothem analysis (δ18O alone) cannot reliably distinguish seismic from non-seismic signals. The path forward requires adding variables:

### Required Data Types

| Category | Variables | Purpose |
|----------|-----------|---------|
| **Multi-proxy** | δ18O, δ13C, Mg/Ca, Sr/Ca, Ba/Ca, U/Ca | Discriminate mechanisms (e.g., δ13C for CO2 source) |
| **Multi-cave** | 2+ caves in same seismic zone | Distinguish local vs regional signals |
| **Independent records** | Tree rings, lake turbidites, trenches | Cross-validate time windows |
| **Fault databases** | SCEC CFM, GEM, DISS, state surveys | Verify "dark" claims |
| **DEM analysis** | Lineaments, drainage anomalies, hillshade | Find unmapped structures |
| **Historical archives** | Church records, newspapers, diaries | Pre-catalog documentation |

### Workflow

**⚠️ MANDATORY STEP 0: WEB SEARCH FIRST (Added 2026-01-03)**

Before ANY analysis, do simple web searches (5 minutes max):

```
"[approximate year] earthquake [region]"
"[fault name] paleoseismic"
"[cave name] earthquake"
```

**Why this is critical:** We spent hours analyzing the Crystal Cave ~1745 anomaly as a potential "dark earthquake" when a simple Google search for `1745 earthquake california -cascadia` immediately found that Kerry Sieh documented this event at Pallett Creek in 1978 (TIME Magazine). This pattern has repeated multiple times.

**Examples of searches that would have saved time:**
- "1745 earthquake California" → Sieh 1978 Pallett Creek
- "1394 earthquake Italy Liguria" → Check for known events
- "1285 earthquake Italy" → Check for known events

**Red flag:** If you think you've found a "dark earthquake" or novel event, STOP and search first. Most "discoveries" turn out to be rediscoveries of known events.

1. **Flag**: Identify anomaly windows (|z| ≥ 2.0) in speleothem record
2. **Characterize**: Check volcanic databases, climatic records for alternative explanations
3. **Web Search**: Search for known earthquakes in that time window (Step 0 reminder)
4. **Target**: If unexplained AND no known events, investigate with independent methods:
   - Search paleoseismic literature for overlapping trench events
   - Run DEM lineament analysis for unmapped faults
   - Check historical archives for undocumented accounts
5. **Verify**: Only claim seismic origin if independent confirmation exists

### What This Means for Publication

- **Cannot publish**: "Speleothems detect earthquakes"
- **Can publish**: "Speleothem anomalies as targeting tools for paleoseismic investigation"
- **Value proposition**: Efficiently direct expensive field campaigns (trenching, coring) to high-probability time windows

---

## Preliminary Findings (Pending Peer Review)

**See regional files for full details. Summary of key findings:**

### Italy (Bàsura Cave)
- **1285 ± 85 yr CVSE**: Multi-proxy evidence (δ18O, Mg/Ca) correlates with 11 documented earthquakes (1273-1287 CE). See `regions/italy/THE_1285_CVSE.md`
- **1394 ± 13 yr candidate**: Strong signal but lacks δ13C validation. See `regions/italy/THE_1394_DARK_EARTHQUAKE.md`

### Central America (Yok Balum Cave)
- **14 Motagua events (224-1793 CE)**: 7 seismic + 2 CVSEs, recurrence 121±118 yr. Notable: ~495 CE (strongest δ13C), ~620 CE (Quirigua destruction), ~936 CE (Eldgjá compound event). See `regions/central_america/`

### North America (Oregon, California, Minnetonka)
- **Cascadia**: 7/15 megathrusts detected (46.7%), including T5 ~436 CE, S ~854 CE (CVSE candidate), W ~1117 CE
- **California**: 3 prehistoric SAF events (~1285, ~1580, ~1825); 1741 pre-Spanish events on Kern Canyon & Rose Canyon faults (NOT dark - faults mapped). See `US_DARK_QUAKE_VERIFICATION_SUMMARY.md`
- **Wasatch**: ~1676 CE matches paleoseismic trenching. See `regions/north_america/MINNETONKA_WASATCH_VALIDATION.md`

### Middle East (Gejkar Cave, Iraq)
- **1304 Tabriz M7.3** detected at 273 km (U/Ca z=+6.87σ). Non-Italian support for Chiodini model.

### Caribbean (Dos Anas, Cuba)
- **1766 M7.6 detected** (z=-2.74, strongest in 1,253-yr record) + 7 pre-instrumental candidates

### Brazil (Lapa Grande/Tamboril)
- **~96 CE**: 71-year recovery (longest in dataset). **~867, ~1006 CE**: Post-hoc tests on 2 known colonial events. See `regions/brazil/`

### Romania (Closani Cave)
- **~1541-1543 CE** (z=-3.59σ): Interpreted as local shallow crustal event, not distant Vrancea

---

## Directory Structure

| Folder | Contents |
|--------|----------|
| `regions/` | Italy (Bàsura), Central America (Yok Balum), North America (Oregon, CA, San Diego), Brazil, Romania, Turkey, Japan |
| `methodology/` | METHODOLOGY.md, THEORETICAL_FOUNDATION.md, CLAUDE_REFERENCE.md, DATA_SOURCES.md |
| `publication/` | PAPER_2_DARK_EARTHQUAKES.md, PUBLICATION_STRATEGY.md, COLLABORATOR_OUTREACH.md |
| `catalogs/` | ANOMALY_TRACKING.md (Italy), ANOMALY_CATALOG.md (Americas) |
| `ml/` | ML pipeline scripts, ML_DATA_SOURCES.md |
| `data/` | Raw data, tree rings |
| `memory/` | SESSION_LOG.md, FACTS.md, DECISIONS.md, DEAD_ENDS.md |
| `../dem_tiles/` | TINITALY DEM, ITHACA faults, hillshade products |

---

## Session Memory

Read at session start: `memory/SESSION_LOG.md`, `memory/FACTS.md`, `memory/DECISIONS.md`, `memory/DEAD_ENDS.md`

Update `SESSION_LOG.md` at session end with accomplishments, decisions, dead ends, and next focus.

---

## Research Tools

Located in `tools/` directory. See `tools/README.md` for full CLI usage and setup.

**MCP Tools** (available in Claude): `sisal_search_caves`, `sisal_get_samples`, `earthquake_search`, `calc_pga`, `calc_chiodini`, `calc_distance`, `calc_recurrence`, `rag_search`, `rag_index`

---

## Quick Start by Task

| If you're... | Read... |
|--------------|---------|
| **Starting fresh** | This file, then `memory/` files, then regional READMEs |
| **Interpreting geochemistry** | `methodology/CLAUDE_REFERENCE.md` |
| **Understanding theory** | `methodology/THEORETICAL_FOUNDATION.md` (Manga & Wang earthquake hydrology) |
| **Planning publication** | `publication/PUBLICATION_STRATEGY.md` |
| **Understanding methodology** | `methodology/METHODOLOGY.md` |
| **Checking anomaly status** | `catalogs/ANOMALY_TRACKING.md` (Italy) or `catalogs/ANOMALY_CATALOG.md` (Americas) |
| **Cross-validation evidence** | `methodology/CROSS_VALIDATION_COMPLETE.md` |

---

## Seismic vs. Climatic Discrimination

**⚠️ UNVALIDATED**: These are proposed discriminators, not proven ones. The 1872 Owens Valley non-detection shows we cannot reliably distinguish signal types with current methods.

| Proxy | Seismic Signal | Climatic Signal | Notes |
|-------|----------------|-----------------|-------|
| **Mg/Ca magnitude** | High (+Z: deep water) | Low (-Z: dilution) | Bàsura: 171 records available |
| **Mg/Ca temporal shape** ⭐ | SHARK FIN (>0.5 σ/mm onset) | HUMP (<0.5 σ/mm onset) | **NEW 2024-12-31**: Validated on 1285, 1394 Italy - See TEMPORAL_SHAPE_VALIDATION.md |
| **Sr/Ca** | High (old water) | Low (fresh) | Bàsura: available |
| **δ13C** | > -8‰ (geogenic CO₂) | < -10‰ (biogenic) | Yok Balum: validated; Bàsura: NO DATA |
| **Recovery time** | 5-71 years (n=8 observed) | 1-7 years (volcanic max) | Order-of-magnitude gap is diagnostic; See METHODOLOGY.md Part VII |
| **Profile shape** | Sawtooth | Spike/gradual | All caves |
| **Lipid P(m)** | >70% (microbial) | <50% (plant) | Oregon Caves: Rushdi et al. 2010 - NEW |
| **Cholesterol** | Present (deep biota) | Absent | Hypothetical seismic marker - NEW |
| **🔥 Wildfire** | +1-3σ Ca/Mg | Variable | ⚠️ **PROVISIONAL (n=1)**: Marble Fork showed +12-13σ, but may vary by region; See METHODOLOGY.md Section 2.6 |

**⭐ Methodological Development (2024-12-31)**: Temporal shape analysis may discriminate seismic from climatic using **rate of change** (Δ(Mg/Ca)/Δt), potentially addressing the "deep water mimic" problem where both earthquakes and droughts produce elevated Mg/Ca. Tested on Bàsura Cave:
- **1285 ± 85 yr**: Onset slope +1.116 σ/mm → SHARK FIN → Seismic ✓
- **1394 ± 13 yr**: Onset slope +0.867 σ/mm → SHARK FIN → Seismic ✓
- **1649 CE**: LOW Mg/Ca (-1.49σ) → Climatic (volcanic recovery) ✓

**Key Examples**:
- **1285 ± 85 yr Italy**: δ18O -2.46σ + Mg/Ca +2.25σ → SEISMIC (Tier 1 evidence)
- **~620 CE Belize (617-663 CE)**: δ18O -3.6σ + δ13C -2.36σ + 46-year duration → SEISMIC
- **1649 Italy**: δ18O -5.833‰ + Mg/Ca -0.57σ → CLIMATIC (volcanic recovery)

**Volcanic False Positives Rejected (Yok Balum)**:

| Period | δ18O Z | δ13C Z | Volcanic Event | VSSI (Tg S) | Ranking |
|--------|--------|--------|----------------|-------------|---------|
| 1273-1279 CE | -3.77 | -1.18 | 1257 Samalas | 59.42 | #1 |
| 1228-1238 CE | -2.93 | -1.91 | 1230 Unknown | 23.78 | #4 |
| 1105-1125 CE | -2.98 | ~-1.3 | 1108 Unknown | 19.16 | #5 |

All three show **decoupled proxies** (δ18O >> δ13C), single-pulse structure, and direct ice core correlation → **VOLCANIC, not seismic**.

**See**: `regions/central_america/YOK_BALUM_1105CE_ANALYSIS.md`, `YOK_BALUM_1228CE_ANALYSIS.md`

**⚠️ CRITICAL CAVEAT**: The absence of volcanic activity does NOT automatically indicate a seismic event. An anomaly must show **positive seismic indicators** (coupled proxies, elevated Mg/Ca, prolonged recovery >10 years) — not merely lack of volcanic correlation. Drought, local hydrological changes, or other climatic factors can produce anomalies during volcanically quiet periods.

### Distance Threshold: Inconsistent Results

**Hypothesis (2025-01-01)**: Speleothems detect **static strain** (permanent rock deformation, 1/r³ decay), not **dynamic strain** (seismic shaking, 1/r decay).

**⚠️ PROBLEM (2026-01-03)**: Crystal Cave results are inconsistent:

| Cave | Earthquake | Distance | PGA | Z-score | Expected |
|------|------------|----------|-----|---------|----------|
| Crystal Cave | 1872 Owens Valley M7.4 | 65 km | 0.094g | **-1.13** | Strong |
| Crystal Cave | 1896 Independence M6.3 | 48 km | 0.060g | -3.54 | Strong |

The larger earthquake (M7.4, 7m displacement, 160 km rupture) produced a **weaker** signal than the smaller one. This is backwards and unexplained.

**Possible explanations:**
1. The 1902 anomaly is NOT from 1896 Independence (wrong attribution)
2. Strike-slip vs dip-slip mechanisms couple differently to aquifers
3. Detection is unreliable and inconsistent

**The Ridley Paradox remains unresolved** until we understand why M7.4 at 65 km produces z=-1.13 while M6.3 at 48 km supposedly produces z=-3.54.

**See**: `regions/north_america/CRYSTAL_CAVE_ANALYSIS.md` for full discussion.

---

## Scientific Standards

**Evidence hierarchy**: Direct data > historical records > inference

**Verification Standards**:
- **One source = coincidence** (interesting but unverified)
- **Two sources = clue** (worth investigating further)
- **Three sources = verified** (minimum for confident claims)
- Multiple independent lines of evidence are REQUIRED for any major claim

**Uncertainty language**:
- "proposed" = unconfirmed hypothesis
- "likely" = probable based on multiple lines (2+ sources)
- "confirmed" = multi-proxy validation (3+ independent sources)
- NEVER use "100%", "MUST", "has to be", "definitely", "certainly" - maintain scientific skepticism
- Prefer "suggests", "indicates", "consistent with", "supports"

**Requirements**:
- Always consider alternative explanations
- Flag temporal resolution limits and dating uncertainties
- Never overstate certainty (this is frontier research)
- **Red flag check**: If you think you've made a discovery that no one has found before, that's a sign to rethink the logic
- **Breakthrough skepticism**: Double-check any "critical finding" or "breakthrough" for simple logic flaws, arithmetic errors, or confirmation bias
- If the conclusion seems too clean or perfect, look harder for what you might have missed

### ⚠️ Dating Uncertainty Notation

**All event dates should include uncertainty ranges.** Different proxies have different uncertainties:

| Dating Method | Typical Uncertainty | Notation Format |
|---------------|---------------------|-----------------|
| U-Th dating | ±50-100 years | `1285 ± 85 yr (U-Th: 1237-1322 CE)` |
| Speleothem anomaly window | Duration of anomaly | `~620 CE (anomaly: 617-663 CE, 46 yr)` |
| Turbidite correlation | Goldfinger window | `436 CE (T5 window: 300-500 CE)` |
| Tree ring dating | ±1-5 years | `1580 ± 3 yr` |
| Radiocarbon | ±30-100 years | `830 ± 50 14C yr` |

**Examples of correct notation**:
- **Italy**: "1285 ± 85 yr (U-Th: 1237-1322 CE)" NOT "1285 CE"
- **Belize**: "~620 CE (anomaly: 617-663 CE)" NOT "~620 CE"
- **Cascadia**: "T5 ~436 CE (window: 300-500 CE)" NOT "~436 CE"

**Key principle**: The uncertainty range is as important as the central estimate. A "1285 CE earthquake" implies unjustified precision; "1285 ± 85 yr" more accurately conveys the dating resolution.

### Citation Standards

**Wikipedia is NEVER an acceptable primary source.** When Wikipedia is used for initial research:
1. Identify the primary sources cited in the Wikipedia article
2. Verify claims against those primary sources
3. Cite the primary source, NOT Wikipedia
4. If no primary source is available, mark the claim as "requires verification"

**Acceptable sources** (in order of preference):
1. **Peer-reviewed publications**: SISAL, INGV, Nature, Science, JGR, etc.
2. **Official databases**: CFTI5Med, CPTI15, SISAL v3, USGS, ITHACA
3. **Archival documents**: Vatican (AAV), Archivio di Stato, diocesan records
4. **Government/institutional portals**: Soprintendenza, Cultura in Liguria, BRGM
5. **Published monographs**: Academic press books with ISBN

**Unacceptable as primary sources**: Wikipedia, travel blogs, general news articles, forum posts

---

## Terminology Guidelines

**Use context-appropriate language** - the same concept has different names depending on audience:

| Context | Term | Example |
|---------|------|---------|
| **Title/Abstract** | "Dark Earthquakes" | "Detecting Dark Earthquakes Using Speleothem Geochemistry" |
| **Introduction** | "historically undocumented seismic events" | "We identify historically undocumented seismic events through..." |
| **Methods** | "paleoseismic geochemical anomalies" | "We identified a paleoseismic geochemical anomaly at 1285 ± 15 CE consistent with local fault rupture." |
| **Results** | "seismically-induced isotopic excursions" | "The seismically-induced isotopic excursion shows..." |

**Rationale**: "Dark Earthquakes" is memorable and accurate (invisible to the historical record), appropriate for titles. In methodology sections, "paleoseismic geochemical anomalies" sounds like geophysics, not ghost hunting.

**Do NOT use "PGA"** as an acronym - it collides with "Peak Ground Acceleration" in seismology. Spell out "paleoseismic geochemical anomaly" each time.

---

## Key Definitions

**⚠️ MAJOR REVISION 2026-01-03**: Strategic pivot from "earthquake detection" to "anomaly-guided exploration."

### Core Terminology (Revised)

- **Speleothem Anomaly**: A statistically significant (|z| ≥ 2.0) isotopic excursion. **Does NOT imply seismic origin.** May be climatic, volcanic, hydrological, anthropogenic, or seismic.
- **Anomaly Window**: Time period containing anomaly, suitable for targeting paleoseismic investigation. NOT a detection claim.
- **Investigation Target**: Location/time where anomaly suggests further study (trenching, DEM analysis, archive research).

### Legacy Terminology (Use With Caution)

- **Dark Earthquake**: Seismic event with physical evidence but **no mapped source fault**. ⚠️ We cannot confirm dark earthquakes from speleothems alone - requires independent paleoseismic verification.
- **Pre-Spanish / Pre-Historical Earthquake**: Event predating written records on a **known, mapped fault**. Speleothems may flag time windows but cannot confirm events.
- **Paleoseismic Correlation**: Anomaly window overlaps independently dated trench event. Correlation only - not validation of detection methodology.
- **CVSE (Compound Volcanic-Seismic Event)**: Compound volcanic-seismic-hydrological catastrophe with evidence for ALL THREE components:
  1. Volcanic forcing (documented eruption in ice cores)
  2. Seismic signal (Mg/Ca or δ13C proxy confirmation)
  3. Hydrological expression (documented floods or aquifer disruption)
  - **CVSE-1285**: 1285 Italy (UE6 eruption + earthquake + Genoa floods) — Strongest evidence (all 3 components well-documented)
  - **CVSE-1159**: 1159 Belize (1171 eruption + seismic pulse + aquifer disruption) — Moderate evidence (volcanic timing uncertain)
  - **CVSE-936**: 936 Belize (939 Eldgjá basaltic flood + seismic + global floods) — Strong evidence (seismic precedes eruption)
  - **CVSE-853**: 853 CE Pacific Northwest (Churchill VEI 6 + Cascadia Event S + NW drought) — Moderate evidence (needs additional validation)
- **Evidence Tier 1**: Multi-proxy validation (δ18O + Mg/Ca or δ13C + cross-cave + historical)
- **Evidence Tier 2**: δ18O + strong historical documentation or single additional proxy
- **Evidence Tier 3**: Single proxy or weak correlation

---

## Project Statistics

**Note**: "Anomaly windows" are time periods with |z| ≥ 2.0 excursions. They are investigation targets, NOT confirmed seismic events.

| Region | Proxy | Time Span | Measurements | Anomalies | Anomaly Windows (investigation targets) |
|--------|-------|-----------|--------------|-----------|-------------------------------------|
| Italy | Bàsura δ18O | 1198-1946 CE | 265 | 32 | 1 supported (**1285 ± 85 yr**) + 1 candidate (**1394 ± 13 yr** - lacks δ13C) |
| **Romania (Vrancea)** | **Closani Cave δ18O** | -1843 - 1986 CE | 1,832 | 10 (z<-2.5) | **1**: ~1541-1543 CE (z=-3.59σ) - Interpreted as shallow crustal event (2025-12-31). Strong signal suggests local event, not distant Vrancea |
| Central America | Yok Balum δ18O | 25 BCE - 2006 CE | 4,048 | 203 (z>2) | **~620 CE correlates with KNOWN Quirigua hiatus (495-653 CE)**. Other candidates: ~495, ~700, ~827, ~1075, ~1310 + 2 CVSEs (~936, ~1159). Recurrence: 121 ± 118 yr |
| North America | Oregon Caves δ18O | 6236 BCE - 1687 CE | 2,680 | 35 (z>2) | 10 Cascadia events (7 detected + 3 possible): T11 ~3940 BCE (strongest, z=-3.32), T5 ~436, **S ~854 (CVSE-853)**, W ~1117 |
| **California (SAF)** | **Paleoseismic + Tree Rings** | ~650-2023 CE | 4 convergent | **0 dark** / 3 prehistoric | **3 prehistoric on known fault**: ~1285 (1280-1380), ~1580 ± 3, ~1825 ± 1 |
| **California (Sierra)** | **Crystal Cave δ18O** | 873-2006 CE | 1,054 | 47 (z>2) | **0 dark** / **1 KNOWN**: ~1745 correlates with Sieh 1978 Pallett Creek SAF event |
| **San Diego (Rose Canyon)** | **Tree Rings** | 1640-1995 CE | 2 sites | 2 (convergent) | **0 dark** / **1 pre-Spanish**: 1741 ± 1 yr on Rose Canyon Fault (mapped in SCEC CFM) |
| **Middle East** | **Gejkar multi-proxy** | ~-400 - 2013 CE | 841 (δ18O) + 435 (U/Ca) | 2 events | **1** volcanic (1286 UE6) + **1** seismic (1304 Tabriz, ~1306 ± 7 yr peak) |
| **Brazil** | **Lapa Grande/Tamboril δ18O** | ~96-1036 CE | 4 caves | 10 | **3 candidates**: Lapa Grande ~96 CE (71-yr recovery), Tamboril ~867 CE, Tamboril ~1006 CE. Post-hoc test: 2/2 known colonial events detected (n=2 insufficient for statistics) |
| **Turkey (NAF)** | **Sofular Cave δ18O+δ13C** | 50,106 BP - 1997 CE | 3,977 | 53 seismic | **402 CE ± 100 yr supported by multiple lines** + 8 Holocene candidates |
| **Turkey (FBFZ)** | **Kocain Cave δ18O** | ~115-712 CE | ~50 | 1 (z=+1.74) | **417 CE Cibyra supported** (2026-01-02). Archaeological: 50cm fault offset. See `regions/turkey/KOCAIN_417CE_VALIDATION.md` |
| **Caribbean (Cuba)** | **Dos Anas + Santo Tomas** | 747-2000 CE + 6915-81528 BP | 2,328 | 8 (z<-2) | **1766 M7.6 detected** (post-hoc test on known event) + 7 candidates + 1 prehistoric (~8756 ± 200 BP) |
| **Basin & Range** | **Minnetonka Cave δ18O** | ~1370-1986 CE | ~65 | 1 (z>2.5) | **0 dark** / **1 post-hoc test**: ~1676 CE matches Wasatch Nephi "~350 yr ago" event |

### ML Pipeline

See `ml/ML_DATA_SOURCES.md` for full details. **Summary**: 458 change points across 114 caves, 123 dark EQ candidates, 7 high-confidence.

---

## Data Sources

**SISAL v3**: `../SISAL3/sisalv3_database_mysql_csv/sisalv3_csv/`

**Earthquake Catalogs**: Italy (CPTI15, CFTI5Med, DBMI15), US (USGS), Central America (Brocard 2016)

**⚠️ CRITICAL: USGS Quaternary Fault Database has 9-27 year lag and incomplete offshore coverage**
- **Before claiming "dark earthquake"**, cross-reference: SCEC CFM v7.0 (California, downloaded to `data/fault_databases/`), state surveys (CGS, ITHACA, UGS), published studies (2015+), DEM lineament analysis
- **Italy faults**: DISS v3.3.1 (PRIMARY, https://diss.ingv.it), ITHACA, QUIN
- **California faults**: SCEC CFM v7.0 (PRIMARY), CGS Fault Activity Map, CGS FER
- **Central America faults**: GEM CCAF-DB (https://github.com/GEMScienceTools/CCAF-DB), GEM Global
- See `US_DARK_QUAKE_VERIFICATION_SUMMARY.md` for database lag documentation

**Alternative proxies**: Tree rings (ITRDB CA610/CA611), lake sediments (Pallett Creek). See `data/tree_rings/TREE_RING_ANALYSIS.md`

**Discovery tools**: Google Scholar, ITRDB, SISAL v3, SCEC

---

## ⚠️ MANDATORY: Documentation Workflow

**After completing ANY analysis**, update these documents in order:

| Step | Document | What to Update |
|------|----------|----------------|
| 1 | **Analysis doc** | Create/update regional analysis file (e.g., `YOK_BALUM_*_ANALYSIS.md`) |
| 2 | **Database verification** | If claiming "dark" - verify against modern fault databases (see `US_DARK_QUAKE_DATABASE_VERIFICATION.md`) |
| 3 | **PAPER_2_DARK_EARTHQUAKES.md** | Add findings to appropriate section if publication-worthy |
| 4 | **ANOMALY_CATALOG.md** or **ANOMALY_TRACKING.md** | Update anomaly status (SUMMARY only) |
| 5 | **GAPS_AND_PRIORITIES.md** | Mark task complete, add any new tasks discovered |
| 6 | **This file (CLAUDE.md)** | Update Project Statistics, Major Discoveries if significant |

### ⚠️ GAPS_AND_PRIORITIES.md Guidelines

**GAPS is for TASK TRACKING, not analysis storage.** Keep it lean.

| ✅ SHOULD be in GAPS | ❌ SHOULD NOT be in GAPS |
|----------------------|--------------------------|
| Task lists (TODO, PENDING, DONE) | Full analysis with tables |
| Brief status summaries (1-2 lines) | Email templates |
| Pointers to other documents | Contact details |
| Blocking issues | Detailed methodology |
| New tasks discovered | Data that's already in PAPER_2_DARK_EARTHQUAKES.md |

**When adding to GAPS**:
1. Check if the content is already in another document
2. If YES → add a 1-line pointer: "See `file.md` for details"
3. If NO → add it to the correct document FIRST, then add pointer to GAPS

**Content should flow**: Analysis docs → PAPER_2_DARK_EARTHQUAKES.md → GAPS (task status only)

**Moved content locations**:
- Contact info → `COLLABORATOR_OUTREACH.md`
- Ruled-out approaches → `memory/DEAD_ENDS.md`
- Full analysis → Regional files or `PAPER_2_DARK_EARTHQUAKES.md`

### ⚠️ CRITICAL: PAPER_2_DARK_EARTHQUAKES.md is the Authoritative Source

**PAPER_2_DARK_EARTHQUAKES.md contains the full analysis. Catalogs are summaries.**

- **DO**: Add full details (tables, evidence, interpretation) to PAPER_2_DARK_EARTHQUAKES.md FIRST
- **DO**: Summarize key findings in ANOMALY_CATALOG.md AFTER updating the paper
- **DON'T**: Add new findings to catalogs without updating the paper
- **DON'T**: Put detailed analysis in catalogs that isn't in the paper

**Why this order matters**: The paper is 57k+ tokens and can't be read in one pass. If catalogs have details the paper lacks, sync issues occur. The paper must always be the most complete source.

**To read specific paper sections**: Use `Grep` to find the section, then `Read` with `offset`/`limit`.

**Never leave an analysis undocumented.** Each finding should be traceable from raw data → analysis doc → paper → catalog (summary).

### Critical Findings Protocol

When you discover something critical (new dark earthquake, compound event, unexpected pattern), **immediately tell the user**:
- What you found (1 sentence)
- Why it matters (1 sentence)

Example: "Found a COMPOUND EVENT at 1159 CE - first evidence of seismic-volcanic coupling outside Italy, supports the CVSE hypothesis."

---

## Current Priorities

See `GAPS_AND_PRIORITIES.md` for full task list, regional status, and collaborator outreach (Rockwell, Zunino, Shen).

**🚨 TOP PRIORITY**: Contact Tom Rockwell (SDSU) - local SAF paleoseismologist whose dates overlap our findings.

### NEW: Paleoclimate Event Cross-Reference (2024-12-31)

Systematic literature search identified major events overlapping our time windows for cross-validation:

**High Priority**:
- **Complete Cascadia chronology** (Goldfinger 2012): 19 total events - we've validated 3, need to check 16 more
- **Mount Mazama eruption** (~5700 BCE): VEI 7 - tests volcanic discrimination at extreme scale
- **8.2 kiloyear event** (~6200 BCE): At Oregon Caves record start - establishes climate baseline
- **Maya Terminal Classic droughts** (871-1021 CE): Validates seismic vs climatic discrimination in Yok Balum

**Why this matters**: Strengthens statistical validation (3→15+ Cascadia events = 60-80% detection rate), validates volcanic/climate discrimination methodology, establishes negative controls.

See `GAPS_AND_PRIORITIES.md` Section "Cross-Reference Additional Paleoclimate Events" (Tasks PE1-PE12) for complete task list.

---

## Modern Earthquake Validation

See `MODERN_EARTHQUAKE_VALIDATION.md` for full details.

**Summary**: Tree rings (1906 M7.9 ✅), Aquifer monitoring (Gran Sasso 2016 ✅), Speleothems (inconclusive - resolution gap).
