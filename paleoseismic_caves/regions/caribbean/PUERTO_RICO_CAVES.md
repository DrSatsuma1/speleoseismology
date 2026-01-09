# Puerto Rico Speleothem Analysis

## Extraction Date: 2024-12-25

## Summary

Extracted speleothem data from two Puerto Rico caves near the Puerto Rico Trench subduction zone. Both records are **PREHISTORIC ONLY** - no historical earthquake validation possible.

---

## Tectonic Context

| Feature | Value |
|---------|-------|
| Subduction Zone | Puerto Rico Trench |
| Trench Depth | 8,380 m (deepest in Atlantic) |
| Plate Motion | North American → Caribbean (oblique) |
| Historical Earthquakes | 1787 M8.1, 1867 M7.3, 1918 M7.1 |
| Recurrence Interval | ~200 years (M7+) |

---

## Cave Data Summary

### Perdida Cave (Site 173)

| Parameter | Value |
|-----------|-------|
| Location | 18°N, 67°W |
| Elevation | 350 m |
| Entity | 81 (stm2) |
| Age Range | **83,432 - 128,199 BP** |
| Resolution | ~237 years/sample |
| δ18O Samples | 189 |
| δ13C Samples | 189 |
| Mg/Ca | Not available |

**Key Statistics:**
- δ18O Mean: -5.15‰, Std: 1.34‰
- δ13C Mean: -11.36‰, Std: 0.59‰
- δ18O Anomalies (|z|>2): 1
- δ13C Anomalies (|z|>2): 6

**Interpretation:** Late Pleistocene glacial period. Single δ18O anomaly at 127,878 BP (z=-2.02) may correspond to climatic shift during MIS 5e-5d transition.

---

### Larga Cave (Site 325)

**Two entities available with different coverage:**

#### Entity 150 (ED1) - Older Record
| Parameter | Value |
|-----------|-------|
| Age Range | 7,350 - 10,988 BP |
| δ18O Samples | 160 |
| Mg/Ca | Not available |

#### Entity 812 (PR-LA-1) - Deglacial Record (PRIMARY)
| Parameter | Value |
|-----------|-------|
| Age Range | **15,320 - 46,398 BP** |
| Resolution | ~15.2 years/sample |
| δ18O Samples | 2,049 |
| Mg/Ca Samples | 2,024 |

**Key Statistics:**
- δ18O Mean: -0.64‰, Std: 0.63‰
- Mg/Ca Mean: 0.99, Std: 0.28
- δ18O Anomalies (|z|>2): 78
- Mg/Ca Anomalies (|z|>2): 40

**Top 10 δ18O Anomalies:**
| Age (BP) | δ18O (‰) | Z-score |
|----------|----------|---------|
| 15,579 | +2.86 | +5.53 |
| 15,631 | +2.36 | +4.74 |
| 15,527 | +2.27 | +4.59 |
| 16,346 | +2.20 | +4.48 |
| 16,145 | +2.11 | +4.34 |
| 15,684 | +2.03 | +4.22 |
| 16,196 | +2.01 | +4.18 |
| 16,396 | +1.97 | +4.12 |
| 16,246 | +1.94 | +4.07 |
| 16,296 | +1.87 | +3.96 |

**Top 10 Mg/Ca Anomalies:**
| Age (BP) | Mg/Ca | Z-score |
|----------|-------|---------|
| 15,423 | 5.91 | +17.45 |
| 15,371 | 5.72 | +16.78 |
| 15,320 | 5.31 | +15.33 |
| 15,475 | 5.14 | +14.72 |
| 15,527 | 3.79 | +9.94 |
| 15,579 | 3.44 | +8.70 |
| 15,992 | 2.53 | +5.47 |
| 15,684 | 2.38 | +4.94 |
| 16,296 | 2.32 | +4.73 |
| 15,736 | 2.26 | +4.52 |

---

## Multi-Proxy Analysis

### Seismic Signature Check

Applied the Chiodini discrimination model to Larga Cave entity 812:
- **Expected seismic signature:** Negative δ18O + Positive Mg/Ca (deep water influx)
- **Result:** 0 events match seismic signature

### Interpretation

The strongest anomalies cluster at **15,320-16,400 BP** during the **Oldest Dryas / Heinrich Event 1** period. These signals show:

1. **POSITIVE δ18O** (up to +2.86‰) - indicates warmer/wetter conditions
2. **POSITIVE Mg/Ca** (up to 5.91) - could indicate:
   - Prior calcite precipitation (PCP) during warm periods
   - Evaporative concentration
   - NOT the expected seismic deep-water signature

**Conclusion:** The Larga Cave anomalies are **CLIMATIC**, not seismic. They record the major climate oscillations during the last deglaciation, not earthquake events.

---

## Potential Paleoseismic Applications

While no seismic signals were detected, these records could be useful for:

1. **Prehistoric Earthquake Correlation**
   - If paleoseismic trenching identifies Puerto Rico Trench events in the 15-46 ka range
   - The Larga record provides independent chronology

2. **Climate Baseline**
   - Establishes non-seismic behavior during major climate shifts
   - Useful for distinguishing seismic from climatic signals in other caves

3. **Methodology Validation**
   - Confirms that climatic events produce different proxy patterns than seismic events
   - Positive δ18O + positive Mg/Ca = climate (validated)
   - Negative δ18O + positive Mg/Ca = seismic (expected but not found here)

---

## Data Files Created

| File | Contents |
|------|----------|
| `perdida_timeseries.csv` | Perdida entity 81: sample_id, age_BP, δ18O, δ13C |
| `larga_timeseries.csv` | Larga entity 150: sample_id, age_BP, δ18O |
| `larga_812_complete.csv` | Larga entity 812: sample_id, depth, age_BP, δ18O, Mg/Ca |
| `analyze_puerto_rico.py` | Analysis script |

---

## Other Caribbean Caves in SISAL v3

| Cave | Location | Site ID | Proxies | Age Range |
|------|----------|---------|---------|-----------|
| Santo Tomas | Cuba | 177 | δ18O, Mg/Ca | 6,915 - 81,528 BP |
| Dos Anas | Cuba | 183 | δ18O | TBD |
| Venado | Costa Rica | 281 | δ18O, δ13C | TBD |
| Palco | Puerto Rico | 294 | None | No isotope data |

**Note:** Santo Tomas Cave (Cuba) has 1,656 Mg/Ca measurements - could be analyzed for Cuban seismicity.

---

## Limitations

1. **No Historical Coverage**
   - Cannot validate against known 1787, 1867, 1918 Puerto Rico earthquakes
   - Historical speleothem records needed for this region

2. **Deglacial Noise**
   - Larga 812 record spans Heinrich Event 1 and major climate shifts
   - Difficult to isolate seismic signals during this volatile period

3. **Single Cave**
   - No cross-cave validation possible
   - Perdida and Larga 812 don't overlap in time

---

## Recommendations

1. **Search for Historical Caribbean Speleothem Records**
   - Check publications beyond SISAL v3
   - Contact researchers working on Caribbean paleoclimate

2. **Analyze Santo Tomas Cave (Cuba)**
   - Has Mg/Ca data (1,656 samples)
   - May provide seismic signals from Cuban faults

3. **Correlation with Paleoseismic Studies**
   - Cross-reference Larga anomalies with Puerto Rico Trench paleoseismology
   - Check if any trenching studies cover 15-46 ka period

---

*Document created: 2024-12-25*
*SISAL v3 data extracted from: /data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv/*
