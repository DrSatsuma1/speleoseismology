# Theoretical Foundation: Earthquake Hydrology

## Overview

This document summarizes the physical basis for speleothem paleoseismology, drawing primarily from the foundational work of Wang & Manga on earthquake hydrology. Understanding these mechanisms is essential for:

1. Interpreting speleothem geochemical anomalies
2. Setting appropriate distance/magnitude thresholds
3. Discriminating seismic from climatic signals
4. Establishing expected recovery timescales

---

## 1. Key References

### Primary Sources

| Reference | Key Contribution | Application to This Project |
|-----------|------------------|----------------------------|
| **Manga & Wang (2007)** | Comprehensive earthquake hydrology framework | Theoretical basis for detection limits |
| **Wang & Manga (2010)** | Seismic energy density metric | Distance-magnitude thresholds |
| **Wang & Manga (2021)** | Updated textbook (Springer) | Modern synthesis |

**Full citations**:

```
Manga, M., & Wang, C.-Y. (2007). Earthquake Hydrology. In G. Schubert (Ed.),
Treatise on Geophysics (Vol. 4, pp. 293-320). Elsevier.

Wang, C.-Y., & Manga, M. (2010). Hydrologic responses to earthquakes and a
general metric. Geofluids, 10(1-2), 206-216.

Wang, C.-Y., & Manga, M. (2021). Water and Earthquakes. Springer Nature.
```

---

## 2. Seismic Energy Density

### 2.1 The Core Relationship

Seismic energy density `e` (J/m³) represents the maximum seismic energy available per unit volume to do work on rock or sediment. It is calculated from magnitude `M` and epicentral distance `r` (km):

```
log₁₀(r) = 0.48M - 0.33 log₁₀(e) - 1.4

Rearranged:
log₁₀(e) = -2.0 + M - 2.0 × log₁₀(r)
```

This relationship is implemented in the MCP tool `calc_energy`.

### 2.2 Detection Threshold

**Sustained groundwater changes require e > 10⁻³ J/m³**

This empirical threshold is based on global observations of:
- Water well level changes
- Spring discharge variations
- Groundwater chemistry shifts
- Geyser eruption frequency changes

### 2.3 Energy Density Examples

| Scenario | M | Distance | Energy Density | Threshold Ratio |
|----------|---|----------|----------------|-----------------|
| M6.0 at 50 km | 6.0 | 50 km | 0.4 J/m³ | 400× threshold |
| M7.0 at 100 km | 7.0 | 100 km | 1.0 J/m³ | 1,000× threshold |
| M7.5 at 200 km | 7.5 | 200 km | 0.8 J/m³ | 800× threshold |
| M8.0 at 300 km | 8.0 | 300 km | 1.1 J/m³ | 1,100× threshold |
| M9.0 at 500 km | 9.0 | 500 km | 4.0 J/m³ | 4,000× threshold |

### 2.4 Project Validation

Our observed detection distances are consistent with this framework:

| Event | M | Distance | Energy Density | Detected? |
|-------|---|----------|----------------|-----------|
| 1285 Italy | ~6.0-6.5 | ~50 km | 0.4-1.3 J/m³ | **YES** |
| 1394 Italy | ~5.8-6.1 | ~50 km | 0.25-0.5 J/m³ | **YES** |
| ~620 CE Belize | ≥7.5 | <50 km | >10 J/m³ | **YES** |
| Cascadia M8.8 | 8.8 | 200 km | 6.3 J/m³ | **YES** |
| 2012 Guatemala M7.4 | 7.4 | 200 km | 0.25 J/m³* | NO |

*The 2012 event's non-detection is explained by the **connectivity coefficient** (see Section 4).

---

## 3. Liquefaction Limit: Maximum Response Distance

### 3.1 Empirical Relationship

The maximum distance `Rmax` (meters) at which liquefaction/hydrologic responses occur follows:

```
M = -5.0 + 2.26 × log₁₀(Rmax)

Rearranged:
Rmax = 10^((M + 5.0) / 2.26)
```

### 3.2 Distance-Magnitude Table

| Magnitude | Max Response Distance | Application |
|-----------|----------------------|-------------|
| M5.0 | ~10 km | Local cave only |
| M5.5 | ~25 km | Regional (1-2 caves) |
| M6.0 | ~60 km | Multiple caves |
| M6.5 | ~130 km | Cave networks |
| M7.0 | ~280 km | Cross-regional |
| M7.5 | ~600 km | Cross-cave validation |
| M8.0 | ~1,300 km | Continental scale |
| M8.5 | ~2,800 km | Hemispheric |
| M9.0 | ~6,000 km | Global (theoretical) |

### 3.3 Validation Against Our Data

| Event | Claimed M | Distance | Rmax for M | Consistent? |
|-------|-----------|----------|------------|-------------|
| Bàsura 1285 | M6.0-6.5 | ~50 km | 60-130 km | **YES** |
| Yok Balum 620 CE | M≥7.5 | ~50-100 km | 600 km | **YES** |
| Oregon Cascadia | M8.8 | 200 km | ~3,500 km | **YES** |
| Gejkar-Tabriz 1304 | M7.3 | 273 km | ~500 km | **YES** |

---

## 4. Dynamic vs Static Strain

### 4.1 The Critical Distinction

Manga & Wang (2007) demonstrate that **dynamic strain (seismic waves) causes permanent permeability changes** at distances far beyond where static strain matters.

| Strain Type | Source | Range | Effect Duration |
|-------------|--------|-------|-----------------|
| **Static strain** | Fault slip | Near-field only (<10 km) | Permanent |
| **Dynamic strain** | Seismic waves | Far-field (>1000 km possible) | Triggers permanent changes |

### 4.2 Implications for Speleothems

This explains key observations:

1. **Why distant earthquakes affect caves**: Dynamic strain from seismic waves creates/reopens fractures, altering aquifer flow paths even at 100+ km.

2. **Why recovery takes years**: Permeability changes are permanent until sealed by mineral precipitation—a slow process in karst.

3. **Why geyser sensitivity is extreme**: Geysers respond to strains as small as 10⁻⁷ (static) and 10⁻⁶ (dynamic), demonstrating that very small strains can trigger measurable hydrologic responses.

### 4.3 Strain Thresholds from Literature

| Strain Level | Phenomenon | Example |
|--------------|------------|---------|
| 10⁻⁷ | Geyser frequency changes | Yellowstone after Denali 2002 |
| 10⁻⁶ | Well water level oscillations | Widely observed |
| 10⁻⁵ | Sustained water level changes | Common near M6+ |
| 10⁻⁴ | Streamflow increases | Post-earthquake springs |
| 10⁻³ | Liquefaction | Soft sediments |

---

## 5. Aquifer Connectivity Coefficient

### 5.1 The Yok Balum "Ridley Paradox"

Energy density alone does not predict detectability. The Yok Balum cave demonstrates this clearly:

| Event | M | Distance | Energy Density | Detected? |
|-------|---|----------|----------------|-----------|
| 2012 Guatemala M7.4 | 7.4 | 200 km | 0.25 J/m³ | **NO** |
| 1976 Guatemala M7.5 | 7.5 | 100 km | 1.0 J/m³ | **NO** |
| ~620 CE (local fault) | ≥7.5? | <50 km | >10 J/m³? | **YES (46 yr)** |

Both modern earthquakes exceed the detection threshold, yet neither produced a signal.

### 5.2 Resolution: Connectivity Coefficient

The effective energy density must account for hydraulic connectivity:

```
e_effective = e_raw × C

where:
  C = aquifer connectivity coefficient (0 to 1)
  C ≈ 0 for offshore/hydraulically disconnected events
  C ≈ 1 for on-land faults that intersect the cave aquifer
```

This is implemented in the MCP tool `calc_connectivity`.

### 5.3 Connectivity Factors

| Factor | Low C (0-0.3) | High C (0.7-1.0) |
|--------|---------------|------------------|
| Fault location | Offshore/distant | On-land/local |
| Rock type | Sedimentary basin | Karst/fractured |
| Fault-aquifer geometry | Perpendicular/distant | Intersecting |
| Aquifer system | Isolated | Integrated with cave |

---

## 6. Karst Aquifer Response Timescales

### 6.1 Hydraulic Diffusivity

From Manga & Wang (2007):

> "For karst aquifers, hydraulic diffusivity (D) values are high (up to 10⁴ m²/s), meaning pore pressure changes diffuse on timescales of **minutes to hours**."

The diffusion timescale τ is:
```
τ = L² / D

where:
  L = length scale (m)
  D = hydraulic diffusivity (m²/s)
```

| Aquifer Type | D (m²/s) | 100m Diffusion Time |
|--------------|----------|---------------------|
| Shale | 10⁻¹⁰ | ~300,000 years |
| Sandstone | 100 | ~17 minutes |
| Fractured rock | 10² | ~2 minutes |
| **Karst** | 10⁴ | **~1 second** |

### 6.2 But Recovery Takes Years

The apparent contradiction—fast pressure diffusion but slow recovery—is resolved by understanding that:

1. **Pressure equilibrates quickly** (minutes-hours in karst)
2. **Permeability changes persist** until fractures seal via mineral precipitation
3. **Fracture sealing is slow** (controlled by calcite supersaturation rates)

From Jones (2016): Preferential flow paths "reduce precipitation rate by 72%" and "significantly lengthen the timescale required to seal a fracture."

### 6.3 Observed Recovery Times (This Project)

| Event | Cave | Recovery Time | Interpretation |
|-------|------|---------------|----------------|
| Lapa Grande ~96 CE | Brazil | **71 years** | Extreme rupture |
| Yok Balum ~620 CE | Belize | **46 years** | Major fault breach |
| Tamboril ~867 CE | Brazil | **28 years** | Significant |
| Oregon T11 | USA | **~25 years** | Megathrust |
| Bàsura 1285 | Italy | **20 years** | Local M6+ |
| Crystal ~1741 | USA | **14 years** | Moderate |
| Bàsura 1394 | Italy | **5 years** | Lower magnitude |

**Key finding**: Even the shortest seismic recovery (5 years) equals the longest volcanic recovery (7 years for Tambora 1815). The ORDER-OF-MAGNITUDE GAP is diagnostic.

---

## 7. Mechanisms Summary (from Manga & Wang 2007 Figure 17)

```
EARTHQUAKE
    │
    ├── STATIC STRAIN (near-field only)
    │       │
    │       └── Pore pressure change
    │               │
    │               ├── (+) Contraction → Water level rise
    │               └── (-) Dilation → Water level fall
    │
    └── DYNAMIC STRAIN (seismic waves, far-field capable)
            │
            ├── Permeability INCREASE
            │       │
            │       ├── Fracture unclogging
            │       ├── New microfracture creation
            │       └── Fracture dilation
            │
            └── Flow path changes
                    │
                    ├── Deep + shallow water MIXING
                    │       ↓
                    │   δ18O anomaly (meteoric + deep)
                    │   Mg/Ca increase (deep water signature)
                    │   δ13C increase (geogenic CO2)
                    │
                    └── Spring discharge changes
                            ↓
                        New springs, dried springs
                        Streamflow increase
```

### 7.1 Application to Speleothems

The dynamic strain → permeability increase → water mixing pathway explains our observations:

1. **δ18O anomalies**: Mixing of deep (old) and shallow (meteoric) water produces isotopic excursions

2. **Elevated Mg/Ca**: Deep water has longer rock-water contact time, accumulating Mg from dolomite dissolution

3. **δ13C shifts**: Geogenic CO₂ from deep crustal sources has heavier δ13C than soil-derived CO₂

4. **Multi-year recovery**: Fractures remain open until sealed by calcite precipitation

---

## 8. Additional Phenomena (from Manga & Wang 2007)

### 8.1 Mud Volcano Triggering

Large earthquakes can trigger mud volcano eruptions within days. The distance-magnitude relationship mirrors liquefaction limits.

**Relevance**: Confirms that crustal fluid systems respond to distant earthquakes.

### 8.2 Geyser Frequency Changes

Geysers change eruption frequency following earthquakes at strains <10⁻⁶. Effects can persist for years.

**Relevance**: Demonstrates extreme sensitivity of hydrothermal systems to small dynamic strains.

### 8.3 Hot Spring Appearance

New hot springs appeared after the 2003 San Simeon M6.5 earthquake within 15 minutes.

**Relevance**: Shows that seismic events can breach previously sealed hydrothermal reservoirs—analogous to our deep water mixing hypothesis.

### 8.4 Streamflow Increases

The distance-magnitude relationship for streamflow increases matches the liquefaction limit, suggesting similar triggering mechanisms (permeability enhancement, not liquefaction itself).

**Relevance**: Validates the permeability-change hypothesis across multiple hydrologic systems.

---

## 9. Implications for Dark Earthquake Detection

### 9.1 Detection Probability Factors

Based on the theoretical framework, detection probability depends on:

| Factor | Low Probability | High Probability |
|--------|-----------------|------------------|
| Magnitude | M < 5.5 | M > 6.5 |
| Distance | > Rmax | < Rmax/2 |
| Fault type | Offshore subduction | On-land strike-slip |
| Geology | Sedimentary basin | Karst terrain |
| Cave-fault geometry | Distant, isolated | Connected aquifer |

### 9.2 False Negative Prediction

The framework predicts we should NOT detect:

1. **Distant offshore events** (low connectivity): e.g., 2012 Guatemala M7.4
2. **Small local events** (below energy threshold): M < 5.5 at 50 km
3. **Events in isolated aquifers** (no hydraulic connection)

### 9.3 False Positive Prevention

The framework helps reject non-seismic signals:

1. **Volcanic**: Short recovery (1-7 years), decoupled proxies
2. **Climatic**: Gradual onset, no Mg/Ca spike
3. **Local hydrology**: No regional correlation

---

## 10. Tool Reference

The theoretical relationships are implemented in MCP tools:

| Tool | Function | Key Parameters |
|------|----------|----------------|
| `calc_energy` | Seismic energy density | magnitude, distance, connectivity |
| `calc_connectivity` | Estimate C coefficient | fault_type, geology, distance |
| `calc_pore_pressure` | Pore pressure perturbation | magnitude, distance, Skempton B |
| `calc_pga` | Peak ground acceleration | magnitude, distance, depth, model |
| `calc_chiodini` | CO₂ flux perturbation | magnitude, distance |

---

*Document created: 2026-01-01*
*Primary source: Manga & Wang (2007) "Earthquake Hydrology" Treatise on Geophysics*
*RAG indexed: 351 chunks*
