# Global Orphan Earthquake Analysis Summary

## Methodology

**Core Insight**: Modern microseismicity reveals active faults TODAY that also existed in the PAST. By identifying "orphan clusters" (earthquakes >5 km from any mapped fault), we find unmapped active structures that may be sources of historical "dark earthquakes" detectable in nearby speleothem records.

**Validation**: This approach was validated in Italy where the NNW orphan cluster (80% orphan rate) revealed an unmapped fault, now the primary candidate for the 1285/1394 dark earthquakes at Basura Cave.

---

## Regional Analysis Summary

| Region | Cave | Orphan Rate | M5+ (Orphans) | Top Cluster | Dark EQ Candidate |
|--------|------|-------------|---------------|-------------|-------------------|
| **Italy** | Basura | 80% | N/A | NNW (T. Porra) | **1285, 1394 CE** |
| **Turkey** | Sofular | 57.2% | 6 (4) | SW 210-240° | **~402 CE** |
| **Lebanon** | Jeita | TBD | - | DST/Cyprus Arc | TBD |
| **Romania** | Closani | TBD | - | 2023 Gorj | ~1541 CE (reinterpreted) |

---

## Phase 1 Results

### 1. Turkey - Sofular Cave (NAF)

**Location**: 41.4167°N, 31.9333°E (Black Sea coast)
**Seismic Context**: North Anatolian Fault Zone - one of world's most active strike-slip faults

**Microseismicity (2000-2025)**:
- Total earthquakes: 257 within 200 km
- **Orphan rate: 57.2%** (147 orphans)
- GEM faults in region: 178
- M5+ events: 6 total, **4 are orphans**

**Primary Orphan Cluster**: SW direction (210-240°)
- 45 orphan earthquakes at avg 106 km from Sofular
- Average depth: 9.8 km (shallow crustal)
- M4+ events: 14
- **Interpretation**: Unmapped splay or branch fault off main NAF

**Dark Earthquake Candidate**: ~402 CE ± 7 yr
- δ18O: +2.91σ
- δ13C: +1.58σ
- Total coupled signal: 4.49
- **Duration**: ~15 years (395-410 CE)
- **Historical gap**: 45 years BEFORE documented 447 CE Constantinople earthquake
- **Proposed magnitude**: M6.5-7.0

**Data Products**:
- `data/turkey/sofular_microseismicity.csv`
- `scripts/analyze_sofular_microseismicity.py`
- `regions/turkey/SOFULAR_ANALYSIS.md`

---

### 2. Lebanon - Jeita Cave (DST)

**Location**: 33.95°N, 35.65°E (near Beirut)
**Seismic Context**: Dead Sea Transform - major plate boundary

**Microseismicity (2000-2025)**:
- Total earthquakes: 152 within 200 km
- Major features: Dead Sea Transform, Cyprus Arc
- 2008 offshore swarm activity noted

**Historical Context**:
- 1202 CE: Major earthquake destroyed Beirut
- 749 CE: Galilee earthquake
- Active tectonics with sparse historical records

**Status**: Microseismicity queried; speleothem analysis pending

---

### 3. Romania - Closani Cave (Vrancea)

**Location**: 45.1°N, 22.8°E (Carpathians)
**Seismic Context**: Vrancea intermediate-depth earthquakes (unique in Europe)

**Microseismicity (2000-2025)**:
- Total earthquakes: 68 within 200 km
- **Key finding**: 2023 Gorj cluster (M5.2-5.7) at ~10 km depth
- This is **shallow crustal**, NOT Vrancea deep zone

**Significance**: The 2023 Gorj cluster is only ~50 km from Closani Cave. This shallow seismicity may explain why the ~1541 CE anomaly (z=-3.59σ) is so strong despite being 150+ km from the Vrancea deep zone.

**Reinterpretation (2025-12-31)**: The 1541 CE signal may be from a **local shallow crustal event**, not a distant Vrancea earthquake.

**Database Verification (2026-01-03)**: ✅ COMPLETE - **FAULTS ARE MAPPED**
- **2023 Gorj faults documented**: NW-SW and E-W strike-slip systems (Bălă et al. 2025)
- **RODASEF database**: Gorj/Oltenia region included as active seismogenic zone (Bala et al. 2015)
- **EFSM20 coverage**: Unclear (M≥5.5 threshold may exclude Gorj)
- **CLASSIFICATION**: **PRE-INSTRUMENTAL EARTHQUAKE ON MAPPED FAULT** (NOT "dark")
- **See**: `regions/romania/CLOSANI_CAVE_FAULT_DATABASE_VERIFICATION.md`

**Status**: ~~Microseismicity queried; fault distance analysis pending~~ **VERIFICATION COMPLETE**

---

## Phase 2: Global Pipeline

The `scripts/global_orphan_analysis.py` pipeline can analyze any SISAL cave:

```bash
# Analyze specific cave
python global_orphan_analysis.py --cave sofular --earthquakes eq_data.json

# Custom location
python global_orphan_analysis.py --lat 41.42 --lon 31.93 --name "Custom Cave" --earthquakes eq_data.json
```

### Priority Caves for Future Analysis

| Cave | Entity | Location | Seismic Zone | Samples |
|------|--------|----------|--------------|---------|
| Larga | 812 | Puerto Rico 18.3°N, 66.8°W | PR Trench | 2,050 |
| Chen Ha | 404 | Belize 16.7°N, 89.1°W | Motagua | 1,573 |
| Corchia | 669 | Italy 44.0°N, 10.2°E | Apennines | 1,542 |
| Pozzo Cucu | 838 | Italy 40.9°N, 17.2°E | Apulia | 2,658 |
| Sahiya | 132 | India 30.6°N, 77.9°E | Himalaya | 3,846 |
| Dandak | 278 | India 19.0°N, 82.0°E | Central India | 1,874 |
| Shatuca | 434 | Peru -5.7°S, 77.9°W | Andes | 1,772 |

---

## Key Findings

### 1. Orphan Rates Indicate Unmapped Faults
- Italy (Basura): 80% orphan → confirmed unmapped T. Porra Fault
- Turkey (Sofular): 57.2% orphan → SW cluster suggests unmapped NAF splay
- **High orphan rate = more potential for dark earthquakes**

### 2. Shallow Crustal Events May Dominate
- Romania: 2023 Gorj cluster at 10 km depth (not 100+ km Vrancea)
- This explains "too strong" signals from supposedly distant earthquakes

### 3. Modern Microseismicity Reveals Historical Sources
- The methodology successfully identifies:
  - Active fault segments
  - Orphan clusters (unmapped structures)
  - Depth profiles (shallow vs deep)
  - Azimuth patterns from cave location

---

## Files Created

| File | Description |
|------|-------------|
| `scripts/global_orphan_analysis.py` | Reusable analysis pipeline |
| `scripts/analyze_sofular_microseismicity.py` | Turkey-specific script |
| `data/turkey/sofular_microseismicity.csv` | Sofular earthquake data |
| `regions/turkey/SOFULAR_ANALYSIS.md` | Turkey analysis documentation |
| `GLOBAL_ORPHAN_SUMMARY.md` | This file |

---

## Next Steps

1. **Complete Lebanon/Romania analysis**: Run full fault-distance analysis, identify orphan clusters
2. **Analyze speleothem records**: Check Jeita and Closani for dark earthquake candidates
3. **Expand to priority caves**: Puerto Rico, India, Peru (high seismicity + good SISAL coverage)
4. **Systematic pipeline**: Automate analysis for all 50+ SISAL caves with 100+ samples
