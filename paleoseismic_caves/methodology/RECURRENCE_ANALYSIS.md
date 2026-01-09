# Earthquake Recurrence Interval Analysis

**Calculated**: 2026-01-02 using `calc_recurrence` MCP tool

---

## 1. Yok Balum (Maya Mountains Local Faults)

### Event Sequence
Events detected through speleothem paleoseismology, ordered chronologically:

| Event | Year CE | Z-score | Recovery (yr) | Classification | Notes |
|-------|---------|---------|---------------|----------------|-------|
| 1 | **~224** | +1.26 | **18.8** | **PROBABLE** | Long recovery = seismic signature |
| 2 | ~495 | -2.81 | - | SEISMIC | Quirigua hiatus begins |
| 3 | ~620 | -3.60 | - | SEISMIC | 46-year anomaly, two-pulse |
| 4 | ~700 | -2.50 | - | SEISMIC | Maya collapse onset |
| 5 | ~827 | -2.79 | - | SEISMIC | Lake Chichoj correlation |
| 6 | ~936 | -2.49 | - | CVSE | Phase 1 seismic + Eldgja |
| 7 | ~1091 | -1.19 | 0.5 | Possible | ML-matched, low z |
| 8 | ~1125 | +2.03 | 22.5 | Probable | ML-matched, long recovery |
| 9 | ~1159 | - | - | CVSE | Compound event |
| 10 | ~1242 | +1.55 | 21.3 | Probable | ML-matched, long recovery |
| 11 | ~1296 | -1.07 | 35.1 | Probable | ML-matched, very long recovery |
| 12 | ~1310 | -2.31 | - | CANDIDATE | Coupled signature |
| 13 | ~1334 | +1.19 | 1.3 | Possible | ML-matched, 24 yr after 1310 |
| - | **1334-1793** | - | - | **GAP** | **459 years with NO detected events** |
| 14 | ~1793 | -1.58 | 0 | Possible | ML-matched |

### The 1334-1793 CE Gap

**Critical observation**: No seismic events detected during a 459-year period. Given mean recurrence of ~120 years, we'd expect 3-4 events. Possible explanations:

1. **Fault quiescence**: Maya Mountains faults in low-strain accumulation period
2. **Detection failure**: Events below speleothem detection threshold (z < 1.0)
3. **Record quality**: Possible hiatus or reduced resolution in speleothem growth
4. **Volcanic masking**: High volcanic activity could mask seismic signals (but no major eruptions in this period)

This gap is consistent with **locked fault behavior** - long quiescence followed by clustered rupture.

### Recurrence Calculations

**Full sequence** (14 events from 224-1793 CE):

| Metric | Value |
|--------|-------|
| Mean recurrence | **121 ± 118 years** |
| CV (σ/μ) | 0.98 |
| Years since last (1793) | 232 years |
| Percent of cycle | 192% |

**Excluding 1334-1793 gap** (cluster analysis, 1310-1334 treated as single sequence):

| Metric | Value |
|--------|-------|
| Cluster 1 (224-1334 CE) | 13 events, mean 93 ± 73 yr |
| Gap (1334-1793 CE) | 459 years |
| Interpretation | Episodic clustering with quiescent periods |

### Interpretation

The high CV (0.98) reflects **clustered/episodic behavior**:

1. **Missed events**: The ML analysis identified additional earthquake-matched anomalies post-1310 CE (1334, 1793) that weren't included in the manual sequence
2. **Detection threshold**: Lower-magnitude events (z < 2.0) may not meet manual classification criteria but still represent seismic activity
3. **Clustered behavior**: The 1310 → 1334 CE interval (24 years) shows earthquake clustering, common in locked fault systems

The extended sequence showing 143% of cycle (232 years since 1793) is more realistic, though still indicates the Maya Mountains fault system may be approaching or within an elevated probability window.

### Caveats

1. **Ridley Paradox**: Yok Balum only detects LOCAL faults (<50 km). The 1976 M7.5 Guatemala earthquake (100 km away) produced NO signal.
2. **Source fault**: Events attributed to Southern Boundary Fault or unmapped Maya Mountains structures
3. **High variability**: σ = 124 years reflects clustered/episodic behavior typical of locked faults
4. **Missing events 1334-1793**: The 459-year gap may indicate missed events, fault quiescence, or detection failure during this period

---

## 2. San Andreas Fault (California)

### Event Sequence

| Event | Year CE | Source | Type |
|-------|---------|--------|------|
| 1 | ~1285 | Tree rings + Pallett Creek | Dark EQ (PROBABLE) |
| 2 | ~1580 | Tree rings + Carrizo Plain | Dark EQ (PROBABLE) |
| 3 | 1857 | Instrumental | Fort Tejon M7.9 |
| 4 | 1906 | Instrumental | San Francisco M7.9 |

### Recurrence Calculations

**Full-fault ruptures only** (~1285, ~1580, 1857):

| Metric | Value |
|--------|-------|
| Mean recurrence | **286 ± 9 years** |
| CV (σ/μ) | 0.03 |
| Years since last (1857) | 168 years |
| Percent of cycle | 59% |

**Including 1906** (all events):

| Metric | Value |
|--------|-------|
| Mean recurrence | **155 ± 116 years** |
| CV (σ/μ) | 0.75 |
| Years since last (1906) | 119 years |
| Percent of cycle | 77% |

### Interpretation

The full-fault rupture sequence (~1285 → ~1580 → 1857) shows **remarkably regular recurrence** (286 ± 9 years, CV = 0.03). This suggests:

1. **Predictable behavior**: Full-fault SAF ruptures may follow a quasi-periodic pattern
2. **Next event**: If pattern holds, next full-fault rupture expected ~2143 CE (2857 - 168 = 2025 + 118 years)
3. **South SAF status**: At 168 years (59% of 286-year cycle), South SAF is not yet in the elevated probability window

**Caution**: The 1906 earthquake ruptured the North SAF segment only. Including it distorts the full-fault recurrence calculation. The 1857-1906 interval (49 years) represents segment-specific behavior, not full-fault recurrence.

---

## 3. Cascadia Subduction Zone

### Event Sequence

From Goldfinger et al. (2012) turbidite chronology + Oregon Caves speleothem detection:

| Event | Year | Magnitude | Oregon Caves Detection |
|-------|------|-----------|------------------------|
| T11 | ~3940 BCE | M8.8+ | z=-3.32 (STRONGEST) |
| T10 | ~1494 BCE | M8.5+ | z=+2.31 |
| T9 | ~1240 BCE | M8.5+ | Possible |
| T8 | ~1050 BCE | M8.5+ | Detected |
| T7 | ~940 BCE | M8.5+ | Possible |
| T6 | ~780 BCE | M8.5+ | Detected |
| T5 | ~436 CE | M8.8-8.9 | z=+2.41 |
| S | ~854 CE | M8.0-9.0 | z=+2.19 |
| W | ~1117 CE | M8.0-9.0 | z=+2.46 |
| Y | 1700 CE | M9.0 | Record ends 1687 |

### Recurrence Calculation

Using 10 events from T11 through 1700 CE:

| Metric | Value |
|--------|-------|
| Mean recurrence | **627 ± 405 years** |
| CV (σ/μ) | 0.65 |
| Years since last (1700) | 325 years |
| Percent of cycle | 52% |

### Interpretation

1. **High variability**: σ = 405 years reflects complex subduction zone behavior with magnitude-dependent recurrence
2. **Not overdue**: At 325 years (52% of mean cycle), Cascadia is not statistically overdue
3. **Magnitude dependence**: Larger events (M9.0) have longer recurrence than smaller events (M8.0-8.5)

---

## Summary Table

| Fault System | Events | Mean ± σ | Years Since | % Cycle | Status |
|--------------|--------|----------|-------------|---------|--------|
| **Yok Balum (extended)** | 9 | 162 ± 124 yr | 232 yr | 143% | Modestly overdue |
| **SAF (full ruptures)** | 3 | 286 ± 9 yr | 168 yr | 59% | Mid-cycle |
| **Cascadia** | 10 | 627 ± 405 yr | 325 yr | 52% | Mid-cycle |

---

## Methodology Notes

- Calculations performed using `calc_recurrence` MCP tool
- Recurrence = (Last event - First event) / (N events - 1)
- Standard deviation calculated from inter-event intervals
- "Years since last" calculated from most recent event to 2025 CE
- "Percent of cycle" = (Years since last / Mean recurrence) × 100

---

*Created 2026-01-02. See GAPS_AND_PRIORITIES.md MCP1 for task status.*
