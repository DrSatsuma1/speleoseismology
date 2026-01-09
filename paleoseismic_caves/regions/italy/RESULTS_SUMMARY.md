# Speleothem-Earthquake Correlation: Proof-of-Concept Results

## VERDICT: CONDITIONAL GO

**A statistically suggestive (p=0.004) correlation was found between geochemical anomalies and historical earthquakes, but the result does not survive strict multiple testing correction and is based on severely limited data.**

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Speleothems with historical coverage | **1** (BÃ sura cave, Liguria) |
| Time coverage | 1198-1945 AD |
| Sampling resolution | ~2.8 years |
| Anomalies detected | 32 |
| Mâ‰¥6.5 earthquakes in period | 34 (Italy-wide) |
| Earthquakes within 500km | 6 |
| Best correlation | 5/6 hits at 0-10 year lag |
| p-value (uncorrected) | 0.004 |
| p-value threshold (Bonferroni) | 0.0033 |
| **Result** | Marginally misses strict threshold |

---

## Key Findings

### 1. Geographic Mismatch Problem (CRITICAL)
Only **1 of 33 Italian speleothems** has substantial coverage in the historical earthquake catalog period (1000-2020 AD). Most Italian speleothem records span glacial/interglacial timescales (50,000-400,000 years BP), not historical time.

The single usable record (BÃ sura cave, NW Italy) is located far from Italy's most seismically active zones (Calabria, Sicily, Central Apennines). This is a fundamental data availability problem, not a methodological one.

### 2. Statistically Suggestive Correlation Found
At 500km radius and 0-10 year lag window:
- 5 of 6 earthquakes matched to geochemical anomalies
- Expected by chance: 2.0 matches
- Z-score: +2.65
- p-value: 0.004

The 10-year lag is consistent with published karst aquifer transit times.

### 3. Individual Matches

| Earthquake | Distance | Anomaly Year | Lag |
|------------|----------|--------------|-----|
| 1703 Valnerina M6.9 | 420km | 1710 | 7y |
| 1703 Aquilano M6.7 | 449km | 1710 | 7y |
| 1781 Cagliese M6.5 | 350km | 1786 | 5y |
| 1915 Marsica M7.1 | 487km | 1925 | 10y |
| 1920 Garfagnana M6.5 | 166km | 1925-1928 | 4-8y |
| 1461 Aquilano M6.5 | 473km | â€” | no match |

### 4. Critical Limitations
- **Multiple testing**: 15 tests performed; Bonferroni threshold = 0.0033
- **Sample size**: n=1 speleothem, 6 earthquakes
- **Confounders**: 20th century anomaly cluster overlaps with climate warming
- **Selection bias**: Cannot test whether matched anomalies have non-seismic causes

---

## Interpretation

The correlation is **intriguing but not conclusive**. The pattern could represent:

1. **Real seismic signal**: Earthquakes perturb regional aquifers, altering drip water chemistry with 5-10 year lag
2. **Climate confounding**: Both earthquakes and isotope anomalies cluster in certain periods by coincidence
3. **Statistical artifact**: With only 6 earthquakes, random variation produces apparent patterns

The fact that the nearest earthquake (1920 Garfagnana, 166km) produced the strongest anomaly cluster is consistent with a real signal, but one data point proves nothing.

---

## Recommendations

### For Publication Viability

**This specific analysis is NOT publishable** in its current form due to:
- Single speleothem
- Marginal statistical significance
- Uncontrolled confounders

**However, the methodology is sound and the preliminary signal is worth pursuing.**

### Next Steps for a Viable Study

1. **Expand geographic scope**: Target regions with BOTH high-resolution Holocene speleothems AND active seismicity:
   - Southwest China (Wenchuan region)
   - Eastern Mediterranean (Turkey, Israel)
   - New Zealand

2. **Acquire new data**: Commission high-resolution trace element analysis on existing speleothem samples from caves near active faults with documented paleoseismic records

3. **Use physical damage as anchor**: Start with speleothems that have DATED physical earthquake damage (broken stalactites); these provide independent confirmation of earthquake timing to validate any geochemical signal

4. **Multi-proxy approach**: Combine Î´18O, Î´13C, Mg/Ca, Sr/Ca to improve signal detection

### Publication Strategy

A **methods paper** documenting this feasibility study could be published in a journal like *Quaternary Geochronology* or *Earth-Science Reviews*, framing it as:

> "Can speleothem geochemistry detect historical earthquakes? A feasibility assessment using the SISAL database and Italian earthquake catalog"

Key selling point: First systematic attempt to correlate geochemical (not physical) speleothem anomalies with seismic events. Even a null/weak result advances the field.

---

## Data Files Produced

| File | Description |
|------|-------------|
| italy_sites.csv | 13 Italian cave sites |
| italy_entities.csv | 33 Italian speleothems |
| italy_quakes_m65.csv | 39 Mâ‰¥6.5 earthquakes (1005-2020) |
| basura_timeseries.csv | BÃ sura cave Î´18O time series |
| basura_anomalies.csv | Detected anomalies with z-scores |

---

## Final Assessment

| Question | Answer |
|----------|--------|
| Is the hypothesis testable? | Yes |
| Does the data exist? | Barely (1 speleothem) |
| Was a signal detected? | Marginally (p=0.004) |
| Is the signal conclusive? | No |
| Is further research warranted? | **Yes** |
| Is this publishable as-is? | No, needs expansion |

**Bottom line**: You found a weak but suggestive signal. This justifies a larger study but does not prove the hypothesis. The main obstacle is data availabilityâ€”most speleothem records don't overlap with historical earthquake catalogs. A targeted sampling campaign in seismically active regions with young speleothems would be the logical next step.
