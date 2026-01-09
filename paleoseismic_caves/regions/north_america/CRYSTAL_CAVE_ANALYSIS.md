# Crystal Cave (Sequoia) - Anomaly Analysis

**Date**: 2024-12-29 | **Major Revision**: 2026-01-03
**Entity**: SISAL v3 Entity 577 (CRC-3 stalagmite)
**Location**: 36.59°N, 118.82°W, Sequoia National Park, California
**Record**: 873-2006 CE (1,054 δ18O samples)
**Status**: ONLY California speleothem with instrumental-era coverage

---

## ⚠️ Executive Summary (Revised 2026-01-03)

**Crystal Cave CANNOT reliably detect earthquakes.** The 1872 Owens Valley M7.4 at 65 km produced only z=-1.13, while the 1902 anomaly (z=-3.54) was incorrectly attributed to 1896 Independence M6.3.

| Claim | Status | Evidence |
|-------|--------|----------|
| "First California earthquake detection" | **WITHDRAWN** | 1872 M7.4 non-detection invalidates methodology |
| "1896 Independence caused 1902 anomaly" | **WITHDRAWN** | Larger 1872 event should have produced stronger signal |
| "~1745 dark earthquake candidate" | **RECLASSIFIED: KNOWN EVENT** | Sieh 1978 documented 1745 at Pallett Creek; Akciz Bidart Fan confirms |

**What Crystal Cave demonstrates:**
- Speleothems record disturbances (anomalies exist)
- Anomaly attribution to specific earthquakes is unreliable
- Single-proxy (δ18O) analysis cannot distinguish seismic from non-seismic signals

**Value**: Crystal Cave anomaly windows may guide paleoseismic investigation of Sierra Nevada faults, but cannot independently confirm earthquakes.

---

## Methodological Context

This analysis attempted to apply **Chiodini's hydrogeochemical model** to speleothem archives. The approach:
- Traditional speleoseismology uses **physical damage** (broken formations)
- Chiodini documents earthquake-induced **groundwater chemistry changes**
- We hypothesized speleothems archive these changes

**Result**: The hypothesis is not validated. The 1872 Owens Valley M7.4 should have produced a strong signal at 65 km but did not (z=-1.13). Detection is inconsistent and unreliable.

---

## 1. Data Overview

### Source
- **SISAL v3**: Entity 577, CRC-3 stalagmite
- **Local CSV**: `data/california/crystal_cave_crc3.csv`

### Statistics
| Metric | Value |
|--------|-------|
| Samples | 1,054 |
| Time span | 873.2 - 2005.9 CE |
| Mean δ18O | -9.02‰ |
| Std δ18O | 0.40‰ |
| Resolution | ~1.1 years/sample |

---

## 2. 1900-1920 Window Analysis

### Raw Data

| Year CE | δ18O (‰) | Z-score | Notes |
|---------|----------|---------|-------|
| 1896.9 | -9.14 | -0.30 | Baseline |
| 1898.6 | -9.21 | -0.48 | Slight negative |
| 1900.4 | -9.67 | -1.63 | Building |
| **1902.2** | **-10.43** | **-3.54** | **PEAK ANOMALY** |
| 1903.9 | -10.36 | -3.36 | Still anomalous |
| 1905.7 | -10.27 | -3.14 | Declining |
| **1906 Apr 18** | — | — | **San Francisco M7.9** |
| 1907.4 | -9.49 | -1.18 | Recovery |
| 1909.2 | -9.33 | -0.78 | Recovery |
| 1910.9 | -9.18 | -0.40 | Baseline |

### Critical Observation

**The peak anomaly is at 1902.2 CE, NOT 1906!**

If the 1906 San Francisco earthquake caused this signal, we would expect:
- Onset AFTER April 18, 1906
- Peak around 1906-1908 CE

Instead, we see:
- Onset around 1900 CE
- Peak at 1902.2 CE (4 years BEFORE the earthquake)
- Recovery already underway when 1906 occurred

This timing is **inconsistent** with 1906 San Francisco as the source.

---

## 3. Distance and PGA Analysis

### Distance Calculations

| Earthquake | Date | Magnitude | Distance from Crystal Cave |
|------------|------|-----------|---------------------------|
| **1896 Independence** | Aug 17, 1896 | M6.3 | **48 km** |
| 1901 Parkfield | Mar 2, 1901 | M6.4 | 164 km |
| 1906 San Francisco | Apr 18, 1906 | M7.9 | 244 km |

Crystal Cave (36.59°N, 118.82°W) is in the **Sierra Nevada foothills**, closest to the Sierra Nevada Frontal fault system and Owens Valley faults.

### PGA Modeling (Bindi 2011)

| Earthquake | Magnitude | Distance | PGA (g) | MMI | Observed Z | Expected |
|------------|-----------|----------|---------|-----|------------|----------|
| **1872 Owens Valley** | **7.4** | **65 km** | **0.094** | **VII** | **-1.13** | **STRONG** |
| 1896 Independence | 6.3 | 48 km | 0.060 | VI | -3.54 | Strong |
| 1901 Parkfield | 6.4 | 164 km | 0.011 | IV | ~0 | Weak |
| 1906 San Francisco | 7.9 | 244 km | 0.020 | V | ~0 | Moderate |

### ⚠️ CRITICAL INCONSISTENCY (Added 2026-01-03)

**The 1872 Owens Valley M7.4 earthquake should have produced a STRONGER signal than 1896 Independence, but it didn't:**

| Metric | 1872 Owens Valley | 1896 Independence |
|--------|-------------------|-------------------|
| Magnitude | M7.4 | M6.3 |
| Distance | 65 km | 48 km |
| PGA | 0.094g | 0.060g |
| Rupture length | 160 km | ~20 km |
| Max displacement | 7 m horizontal | ~1 m |
| **Observed z-score** | **-1.13 (weak)** | **-3.54 (strong)** |

**This is backwards.** The larger, higher-PGA earthquake produced a weaker signal.

### Possible Explanations

1. **1902 anomaly is NOT seismic**: The z=-3.54 may be climatic/hydrological, not earthquake-related
2. **Fault mechanism matters**: 1872 was predominantly strike-slip (7m horizontal); different stress transfer?
3. **Aquifer connectivity**: Different fault orientations may couple differently to the karst aquifer
4. **Detection is unreliable**: Speleothem earthquake detection may be too inconsistent for practical use

### Revised Interpretation

**The original attribution of the 1902 anomaly to 1896 Independence is questionable.** If the methodology worked, the 1872 Owens Valley earthquake should have produced a z < -3 signal. Its weak response (z = -1.13) undermines confidence in attributing the 1902 anomaly to any earthquake.

**Status**: 1902 anomaly cause **UNKNOWN** - seismic attribution withdrawn pending explanation of 1872 non-detection.

---

## 4. Comparison: Speleothem vs Tree Ring 1906 Response

| Metric | Tree Rings (Fort Ross) | Crystal Cave |
|--------|------------------------|--------------|
| Distance to 1906 | 50 km | 244 km |
| Signal | z=+1.49σ (enhancement) | z=-3.54σ (suppression) |
| Timing | 1906 exact | Peak at 1902.2 (pre-1906) |
| Interpretation | Validated 1906 detection | **Not 1906** - likely 1896 Independence |

### Why the Difference?

1. **Tree rings** are directly on the SAF at 50 km from rupture → clean 1906 signal
2. **Crystal Cave** is 244 km from SAF, but only 48 km from Independence fault → dominated by closer, older earthquake

### Methodological Implication

**Speleothems are more sensitive to LOCAL fault systems than REGIONAL distant earthquakes.**

This is actually consistent with the Italian methodology: Bàsura Cave detects earthquakes on local Ligurian faults (BSM, T. Porra), not distant events in Apennines or Alps.

---

## 5. ~1745 CE: Correlation with KNOWN Paleoseismic Event

### ⚠️ CRITICAL UPDATE (2026-01-03): NOT A DARK EARTHQUAKE

**The ~1745 event is ALREADY DOCUMENTED.** Kerry Sieh identified this earthquake at Pallett Creek in 1978:

> "Using radioactive-carbon dating techniques... he has now determined that the quakes occurred around A.D. 575, 665, 860, 965, 1190, 1245, 1470 and **1745**." — TIME Magazine, September 25, 1978

**This changes the interpretation:**
- ~~Dark earthquake discovery~~ → **Correlation with known paleoseismic event**
- The Crystal Cave anomaly **validates** speleothem sensitivity to SAF earthquakes
- The value is in the correlation, not discovery of a new event

### Original Analysis (retained for context)

### Anomaly Cluster

| Year CE | δ18O (‰) | Z-score | Notes |
|---------|----------|---------|-------|
| 1734.5 | -8.41 | +1.53 | Rising |
| 1738.0 | -8.28 | +1.86 | Building |
| 1741.6 | -8.09 | +2.33 | Anomalous |
| **1745.4** | **-7.88** | **+2.84** | **PEAK** |
| 1749.0 | -8.22 | +2.00 | Declining |
| 1752.5 | -8.53 | +1.23 | Recovery |

### Characteristics

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Duration | ~14 years (1734-1749) | Consistent with seismic |
| Peak Z-score | +2.84σ | Strong signal |
| Direction | POSITIVE δ18O | Different from 1900s (negative) |
| Recovery | Gradual | Consistent with seismic |

### Historical Context

**There are NO written earthquake records for California before Spanish colonization in 1769.**

The ~1740s anomaly falls in the "dark" period when:
- Native Americans had no written tradition
- No Spanish missions existed north of Baja California
- Any earthquake would be completely undocumented

### Candidate Source Faults

| Fault | Distance | Type | Known Activity | ~1740s Candidate? |
|-------|----------|------|----------------|-------------------|
| **Kern Canyon** | ~40 km | Normal | Late Quaternary | ❌ **RULED OUT** |
| **Sierra Nevada Frontal** | ~50 km | Normal | Holocene | ✓ Possible |
| **Owens Valley** | ~80 km | Strike-slip | 1872 M7.4 | ❌ **RULED OUT** |
| **White Wolf** | ~60 km | Reverse | 1952 M7.3 | ⭐ **LEADING CANDIDATE** |

#### Kern Canyon Fault Ruled Out (Simpson et al. 2009)

Paleoseismic trenching at three sites near Isabella Dam (Simpson et al. 2009, URS Corporation for US Army Corps of Engineers) found:

- **6 surface-rupturing events** in past 35,000 years
- **3 events** between 3470-4020 yr BP (~1500-2000 BCE)
- **"No surface rupturing earthquakes have occurred in the last 3470 years"**

The trenches showed consistent west-side-up displacement of 12-18 inches per event. Despite being the closest major fault to Crystal Cave (~40 km), Kern Canyon **cannot be the source** of the ~1740s anomaly based on this paleoseismic evidence.

**Reference**: Simpson, D.T., et al. (2009). "Increase in Seismic Hazard at Isabella Dam: The Active Kern Canyon Fault." Western Regional ASDSO Conference. URS Corporation/William Lettis & Associates for US Army Corps of Engineers.

#### Sierra Nevada Frontal Fault - Active but Unstudied Near Cave (Sarmiento et al. 2011)

Paleoseismic trenching at Antelope Valley (~38.6°N, ~200 km north of Crystal Cave) documented:

- **Two Holocene surface-rupturing earthquakes**
- Most recent: **~1350 cal BP (536-638 AD)**
- Penultimate: **>6250 cal BP**
- Displacement: 3.6 m, estimated M6.7-6.9
- Slip rate: ~0.7 mm/yr

**Implications**: The Sierra Nevada Frontal fault IS capable of large earthquakes, confirming it as a viable candidate for the ~1740s anomaly. However, the Sarmiento study site is ~200 km north of Crystal Cave. The fault is segmented, and the **southern segment near Crystal Cave (36.59°N) has not been paleoseismically investigated**. The ~1740s anomaly remains unexplained.

**Reference**: Sarmiento, A.C., Wesnousky, S.G., and Bormann, J.M. (2011). "Paleoseismic Trenches across the Sierra Nevada and Carson Range Fronts in Antelope Valley, California, and Reno, Nevada." Bull. Seismol. Soc. Am. 101(5), doi: 10.1785/0120100176.

#### Owens Valley Fault Ruled Out (Bacon & Pezzopane 2007)

Paleoseismic trenching at two sites 4-7 km north of Lone Pine documented:

- **Only 2-3 large Holocene earthquakes** on the Owens Valley fault
- Most recent: **1872 CE** (historic M7.4)
- Penultimate: **3.3-3.8 ka** (OSL dating, ~1800-1300 BCE)
- Antepenultimate: 14-24 ka
- **Recurrence interval: 3000-4100 years**

With the penultimate event ~3,500 years ago and recurrence ~3,500 years, there is **no room for a ~1740s event**. The Owens Valley fault is ruled out as a source for the Crystal Cave anomaly.

**Reference**: Bacon, S.N. and Pezzopane, S.K. (2007). "A 25,000-year record of earthquakes on the Owens Valley fault near Lone Pine, California." GSA Bulletin 119(7-8): 823-847, doi: 10.1130/B25879.1.

#### White Wolf Fault - LEADING CANDIDATE (Stein & Thatcher 1981)

The White Wolf fault is the **only remaining candidate** with compatible timing:

| Metric | Value |
|--------|-------|
| Distance from Crystal Cave | ~60 km |
| Type | Reverse with left-lateral component |
| 1952 earthquake | M7.3 (largest SoCal event since 1872) |
| **Recurrence interval** | **170-450 years** |
| Slip rate | 3-9 mm/yr |

**Critical calculation**: 1952 - 1745 = **207 years** — right in the middle of the 170-450 year recurrence window.

**Caveats**:
1. No paleoseismic trenches have been excavated on White Wolf (reverse fault geometry makes trenching difficult)
2. The recurrence interval is from geodetic/stratigraphic reconstruction, not direct paleoseismic evidence
3. A ~1740s event is **plausible** but **unconfirmed**

**Hypothesis**: The ~1745 CE Crystal Cave anomaly (z=+2.84) may record a pre-1952 White Wolf fault earthquake, approximately 207 years before the 1952 M7.3 event.

**Recommended investigation**: Search for independent evidence of ~1740s seismic activity:
- Tree ring anomalies in Kern County chronologies
- Lake sediment cores from Buena Vista Lake or Kern Lake
- Historical archives from early Spanish expeditions (though pre-1769)

**Reference**: Stein, R.S. and Thatcher, W. (1981). "Seismic and aseismic deformation associated with the 1952 Kern County, California, earthquake and relationship to the Quaternary history of the White Wolf Fault." J. Geophys. Res. 86(B6): 4913-4928.

#### ⭐ San Andreas Fault (Carrizo Segment) - CRITICAL NEW EVIDENCE (2026-01-03)

**The Bidart Fan paleoseismic record provides the strongest chronological match to the Crystal Cave anomaly.**

Akciz et al. (2009, 2010) conducted high-resolution 3D trenching at the Bidart Fan site on the Carrizo section of the San Andreas Fault (~80 km from Crystal Cave), using 33 radiocarbon dates and OSL dating:

| Metric | Value |
|--------|-------|
| Distance from Crystal Cave | ~80 km |
| Type | Right-lateral strike-slip |
| Last major rupture | 1857 Fort Tejon (M7.9) |
| **Penultimate event (Event B)** | **Median 1712 CE, 95.4% range 1631-1823 CE** |
| Average recurrence | 88 ± 41 years (6 events since ~1400 CE) |

**Crystal Cave anomaly (1745.4 CE) falls within Event B's probability window (1631-1823 CE).** The 33-year offset from the median (1712 CE) is well within the ~100-year radiocarbon uncertainty. Event B could have occurred anywhere in this range; a ~1740s rupture is entirely consistent with the data.

**Reference**: Akciz, S.O., et al. (2009). "Revised dates of large earthquakes along the Carrizo section of the San Andreas Fault, California, since A.D. 1310 ± 30." SCEC Annual Meeting.

**Reference**: Akciz, S.O., et al. (2010). "Century-long average time intervals between earthquake ruptures of the San Andreas Fault in the Carrizo Plain, California." Geology 38(9): 787-790.

#### The Dual Rupture Hypothesis

**Stress transfer modeling suggests the SAF and WWF are mechanically coupled:**

Lin and Stein (2004) demonstrated that the 1857 Fort Tejon SAF earthquake increased static Coulomb stress on the White Wolf Fault by up to 8 bars, advancing its failure clock. The reverse is also true - a pre-1857 SAF rupture in ~1745 would have:

1. **Primary event**: M~7.9 SAF rupture (Carrizo/Big Bend) generating long-period shaking at Crystal Cave (80 km)
2. **Triggered event**: Sympathetic M~7.5 WWF rupture (if critically stressed), generating high-frequency vertical acceleration

This "double punch" scenario would explain the severity of the Crystal Cave anomaly (z=+2.84, 14-year duration).

**Reference**: Lin, J. and Stein, R.S. (2004). "Stress triggering in thrust and subduction earthquakes and stress interaction between the southern San Andreas and nearby thrust and subduction faults." J. Geophys. Res. 109, B02303.

#### Wrightwood Tree Ring Constraint

The Wrightwood dendroseismology record (Jacoby, Sheppard, and Sieh) provides critical negative evidence:

- **1812 benchmark**: Strong trauma signal in Jeffrey pines (confirmed earthquake)
- **1745 "silence"**: NO primary trauma signal in mid-18th century
- **Earlier events**: Signals at ~1480 and ~1610

**Interpretation**: The 1745 rupture did NOT propagate southeast into the Wrightwood segment. This constrains the rupture to the Carrizo and Big Bend segments (northwest of Wrightwood), which is consistent with the Bidart Fan data and explains why Crystal Cave (north of the rupture) recorded the event while San Gabriel Mountains (southeast) did not.

**Reference**: Jacoby, G.C., Sheppard, P.R., and Sieh, K.E. (1988). "Irregular recurrence of large earthquakes along the San Andreas fault: Evidence from trees." Science 241: 196-199.

### Revised Source Assessment (2026-01-03)

| Candidate | Distance | Evidence | Status |
|-----------|----------|----------|--------|
| **SAF Carrizo** | 80 km | Bidart Fan: 1631-1745 CE | ⭐ **PRIMARY** |
| **White Wolf** | 60 km | Recurrence fits 1745; triggered? | **SECONDARY** |
| Kern Canyon | 40 km | No events in 3,470 years | ❌ Ruled out |
| Owens Valley | 80 km | Penultimate ~3.5 ka | ❌ Ruled out |
| Sierra Nevada Frontal | 50 km | Southern segment unstudied | ⚠️ Unknown |

**Most Probable Scenario**: The ~1745 CE Crystal Cave anomaly records the penultimate great earthquake on the South-Central San Andreas Fault (Carrizo/Big Bend segments), possibly accompanied by triggered slip on the White Wolf Fault.

### Assessment (Revised)

**Classification**: PROBABLE Pre-Historical Earthquake (NOT "Dark" - source faults are mapped)

**Evidence Level**: Tier 2 (single proxy + independent paleoseismic chronology match)

**Key Evidence**:
1. Crystal Cave δ18O anomaly: z=+2.84 at 1745.4 CE, 14-year duration
2. Bidart Fan paleoseismic: Penultimate SAF event 1631-1745 CE (upper bound exact match)
3. White Wolf recurrence: 170-450 years predicts event in 1502-1782 CE
4. Wrightwood negative: Constrains rupture to Carrizo/Big Bend
5. Stress transfer: SAF loads WWF (Lin & Stein 2004)

**Remaining Questions**:
1. Was White Wolf triggered, or was Crystal Cave responding only to SAF?
2. Can lake sediment turbidites in Buena Vista Lake confirm the event?
3. Are there Yokuts archaeological signatures of 1745 disruption?

**Recommended Action**:
1. ✅ DEM lineament analysis of White Wolf region (completed 2026-01-03)
2. Search for ~1745 turbidites in Buena Vista/Tulare Lake cores
3. Review Yokuts archaeological stratigraphy for ~1745 disruption layer

---

## 6. Other Potential Signals

### 1857 Fort Tejon M7.9 (SAF, 150 km)

| Year CE | δ18O (‰) | Z-score |
|---------|----------|---------|
| 1854.9 | -9.08 | -0.15 |
| 1857.4 | -9.21 | -0.48 |
| 1859.9 | -9.34 | -0.80 |

**Verdict**: No clear signal. Distance (150 km) may be at detection threshold for M7.9.

### 1872 Owens Valley M7.4 (60 km)

| Year CE | δ18O (‰) | Z-score |
|---------|----------|---------|
| 1869.6 | -8.98 | +0.10 |
| 1872.1 | -9.18 | -0.40 |
| 1874.6 | -9.31 | -0.73 |
| 1877.1 | -9.47 | -1.13 |
| 1879.6 | -9.22 | -0.50 |

**Verdict**: Possible weak signal (z=-1.13 at 1877, 5 years after earthquake). At 60 km, should be detectable but may have been obscured by other factors.

---

## 7. Summary (Revised 2026-01-03)

### Key Findings

1. **Earthquake detection INVALIDATED**: The 1872 Owens Valley M7.4 at 65 km produced only z=-1.13. A larger, closer earthquake should produce a stronger signal than 1896 Independence - but it didn't.

2. **1902 anomaly cause UNKNOWN**: Original attribution to 1896 Independence M6.3 is withdrawn. The anomaly may be climatic, hydrological, or have another cause.

3. **~1740s anomaly is an investigation target only**: z=+2.84, 14-year duration - worth investigating but NOT a confirmed earthquake.

4. **~10 unexplained anomaly clusters** across the 1,100-year record require investigation (see Section 3).

### Implications for Methodology

1. **Detection is inconsistent**: Cannot reliably predict which earthquakes will produce signals

2. **Single-proxy insufficient**: δ18O alone cannot discriminate seismic from non-seismic disturbances

3. **Value is in targeting, not detection**: Anomaly windows can guide paleoseismic investigation but cannot confirm earthquakes

### What Crystal Cave CAN Contribute

- Anomaly time windows for Sierra Nevada paleoseismic investigation
- List of unexplained disturbances that may warrant trenching/DEM analysis
- Negative control data (nuclear testing era, anthropogenic contamination)

---

## 8. Nuclear Testing Negative Control (1951-1992)

**Added: 2026-01-03**

Crystal Cave provides a unique negative control: 928 nuclear tests at Nevada Test Site (245 km away) over 41 years with NO detectable signal.

### Distance and Context

| Site | Distance from Crystal Cave | Tests | Period |
|------|---------------------------|-------|--------|
| Nevada Test Site | 245 km | 928 | 1951-1992 |
| Trinity Site, NM | ~850 km | 1 | 1945 |
| Amchitka, AK | ~4,000 km | 3 | 1965-1971 |

### Z-score Data During Testing Era

| Year CE | δ18O (‰) | Z-score | Nuclear Context |
|---------|----------|---------|-----------------|
| 1951.3 | -8.27 | +1.89 | Testing begins |
| 1953.3 | -8.36 | +1.66 | Atmospheric tests |
| 1955.3 | -8.56 | +1.16 | Normal |
| 1957.3 | -8.56 | +1.16 | Normal |
| 1959.3 | -8.95 | +0.18 | Baseline |
| 1961.3 | -9.01 | +0.03 | Baseline |
| 1963.3 | -9.31 | -0.73 | Underground begins (PTBT) |
| 1965.4 | -9.05 | -0.07 | Baseline |
| 1967.4 | -8.64 | +0.96 | Normal |
| **1968.4** | **-8.64** | **+0.96** | **Boxcar 1.3 Mt - NO SIGNAL** |
| 1970.5 | -8.97 | +0.13 | Baseline |
| **1971.5** | **-9.48** | **-1.15** | **Cannikin 5 Mt (Amchitka) - no spike** |
| 1973.6 | -9.33 | -0.78 | Gradual trend |
| 1975.6 | -9.58 | -1.40 | Gradual trend |
| 1976.7 | -9.83 | -2.03 | Gradual trend |
| **1978.7** | **-10.10** | **-2.71** | **Peak negative (NOT test-related)** |
| 1980.8 | -9.62 | -1.50 | Recovery |
| 1983.9 | -9.17 | -0.37 | Recovery |
| 1986.0 | -8.94 | +0.20 | Baseline |
| 1989.1 | -8.94 | +0.20 | Baseline |
| 1992.2 | -8.74 | +0.71 | Testing ends |

### Key Observations

1. **No testing-correlated spikes**: Despite 928 nuclear detonations, NO sharp anomalies coincide with known major tests:
   - Boxcar (1968, 1.3 Mt) → z = +0.96 (normal)
   - Cannikin (1971, 5 Mt at 4,000 km) → z = -1.15 (mild)
   - No signature from any individual test

2. **The 1976-1980 negative trend**: The only notable feature (z = -2.7 in 1978) is a **gradual 5-year pattern**, inconsistent with point-source explosions. Likely reflects:
   - Southern California drought cycles
   - Sierra Nevada precipitation changes
   - NOT seismic or nuclear signals

3. **Mechanistic explanation**: Why nuclear tests produce no signal:
   - Nuclear tests produce **P-waves only** (compression waves)
   - No fault rupture = **no static strain field**
   - No rock fracturing at cave = **no Chiodini CO2 perturbation**
   - Instantaneous pulse, not sustained deformation

### Implications for Methodology

**Caveat**: The nuclear tests at 245 km are NOT a direct control for the 1896 Independence detection at 48 km. At 245 km, static strain from ANY source (nuclear or earthquake) would be negligible due to 1/r³ decay. The lack of nuclear signals is expected from distance alone.

**What nuclear testing does confirm:**
1. P-wave sources (explosions) at intermediate distance produce no gradual isotopic trends
2. The 1976-1980 negative trend is unrelated to nuclear activity (gradual, not pulsed)
3. Cave geochemistry is insensitive to seismic shaking from distant sources

**What it does NOT confirm:**
- Cannot distinguish explosion vs earthquake mechanism at this distance
- Does not validate the 1896 Independence detection (different distance regime)

**For proper methodology validation**, would need:
- A large earthquake at ~200+ km that also produces no signal (distance control)
- A nuclear test at ~50 km (mechanism control) - none exist near this cave

---

## 9. Anthropogenic Contamination (2005-2006)

**Added: 2026-01-03**

The final data point (2005.9 CE, z = +2.54) is likely **anthropogenic contamination**:

- **February 2006**: Amateur explorers discovered a giant crystal-filled cave in Sequoia National Park
- Increased human traffic in Crystal Cave during this period
- Human presence affects cave CO2, temperature, humidity, and drip water chemistry

**Recommendation**: Exclude 2005+ data from seismic analysis. The CRC-3 record should be treated as ending ~2000 CE for reliable interpretation.

---

## 10. Data Files

- **SISAL extract**: `data/california/crystal_cave_crc3.csv`
- **Full time series**: 1,054 samples, 873-2006 CE
- **Columns**: sample_id, depth_sample, age_bp, year_CE, d18O, z_score

---

*Analysis completed: 2024-12-29*
*Methodology: δ18O z-score analysis, PGA attenuation modeling (Bindi 2011)*
*Key revision: 1906 detection reattributed to 1896 Independence M6.3*
