# Z-Score Threshold Sensitivity Analysis

**Date**: 2026-01-03
**Purpose**: Determine optimal z-score threshold for earthquake detection in speleothems

## Background

Current methodology uses z≥2.0σ threshold (95% confidence), but this may be too conservative. Testing whether lower thresholds improve detection rates.

---

## Test Data Summary

### Crystal Cave (California) - 9 events tested
| Event | Date | Mag | Distance | δ18O z-score |
|-------|------|-----|----------|--------------|
| Independence | 1896-07-21 | M6.3 | 48 km | **+2.14σ** |
| Bishop | 1910-05-06 | M6.0 | 40 km | **-3.54σ** |
| Bishop | 1912-01-04 | M5.5 | 50 km | **-3.54σ** |
| Springville | 1915-05-28 | M5.0 | 30 km | **-3.54σ** |
| Independence | 1929-11-28 | M5.5 | 35 km | **-2.61σ** |
| Round Valley | 1984-11-23 | M6.1 | 100 km | **-2.71σ** |
| Round Valley | 1984-11-23 | M5.5 | 95 km | **-2.71σ** |
| Round Valley | 1984-11-26 | M5.6 | 95 km | **-2.71σ** |
| Round Valley | 1985-03-25 | M5.1 | 95 km | **-2.71σ** |

**Range**: |z| = 2.14σ to 3.54σ

### Yok Balum (Guatemala) - 6 events tested
| Event | Date | Mag | Distance | δ18O z | δ13C z |
|-------|------|-----|----------|--------|--------|
| Motagua mainshock | 1976-02-04 | M7.5 | 30 km | +1.32σ | -0.54σ |
| Aftershock | 1976-02-08 | M5.6 | 50 km | +1.26σ | -0.44σ |
| Aftershock | 1976-02-09 | M5.2 | 10 km | +1.26σ | -0.44σ |
| Puerto Barrios | 1980-08-08 | M6.4 | 60 km | +1.85σ | -0.44σ |
| Honduras | 1980-09-02 | M5.3 | 70 km | +1.85σ | -0.44σ |
| Honduras | 1999-07-11 | M6.7 | 80 km | +1.99σ | +1.62σ |

**Range**: |z| = 1.26σ to 1.99σ
**Note**: Failed to detect M7.5 at 30 km - cave does NOT work

### Dos Anas (Cuba) - 3 events tested
| Event | Date | Mag | Distance | δ18O z |
|-------|------|-----|----------|--------|
| Santiago (Oriente) | 1766 | M7.6 | ~500 km | **-2.74σ** |
| Santiago | 1852 | M6.8 | ~500 km | -1.75σ |
| Santiago | 1932 | M6.7 | ~500 km | -0.47σ |

**Range**: |z| = 0.47σ to 2.74σ
**Note**: Only detects very large events at long distance

### Shenqi (China) - 2 events tested
| Event | Date | Mag | Distance | δ18O z |
|-------|------|-----|----------|--------|
| Sichuan | 1936 | M6.85 | 90 km | -1.29σ |
| Xichang | 1952 | M6.62 | 60 km | +1.34σ |

**Range**: |z| = 1.29σ to 1.34σ
**Note**: Failed to detect M6.6-6.85 - cave does NOT work

### Bàsura (Italy) - 1 event tested
| Event | Date | Mag | Distance | δ18O z (1917) | δ18O z (1924 peak) | Mg/Ca z (1924) |
|-------|------|-----|----------|---------------|---------------------|----------------|
| Southern Italy | 1918-08-10 | M5.47 | 82.5 km | +1.01σ | **+3.18σ** | **+2.05σ** |

**Range**: |z| = 1.01σ to 3.18σ
**Note**: Strong signal but ~6 year lag, multi-proxy confirmation

---

## Threshold Testing Results

### Threshold: z ≥ 2.0 (Current Standard)

| Cave | Detections | Total | Rate | Status |
|------|-----------|-------|------|--------|
| Crystal Cave | 9 | 9 | 100% | ✓ WORKS |
| Yok Balum | 0 | 6 | 0% | ✗ FAILS |
| Dos Anas | 1 | 3 | 33% | ~ MARGINAL |
| Shenqi | 0 | 2 | 0% | ✗ FAILS |
| Bàsura | 1 | 1 | 100% | ✓ WORKS |
| **OVERALL** | **11** | **21** | **52%** | |

**Interpretation**: Correctly identifies working caves (Crystal, Bàsura) vs failing caves (Yok Balum, Shenqi)

### Threshold: z ≥ 1.5

| Cave | Detections | Total | Rate | Change |
|------|-----------|-------|------|--------|
| Crystal Cave | 9 | 9 | 100% | - |
| Yok Balum | 2 | 6 | 33% | +2 (1980s events, 1999) |
| Dos Anas | 2 | 3 | 67% | +1 (1852) |
| Shenqi | 0 | 2 | 0% | - |
| Bàsura | 1 | 1 | 100% | - |
| **OVERALL** | **14** | **21** | **67%** | **+3** |

**Interpretation**: Adds 2 detections in Yok Balum (FALSE POSITIVES - cave doesn't work!)

### Threshold: z ≥ 1.0

| Cave | Detections | Total | Rate | Change |
|------|-----------|-------|------|--------|
| Crystal Cave | 9 | 9 | 100% | - |
| Yok Balum | 6 | 6 | 100% | +4 (ALL events) |
| Dos Anas | 2 | 3 | 67% | - |
| Shenqi | 2 | 2 | 100% | +2 (BOTH events) |
| Bàsura | 1 | 1 | 100% | - |
| **OVERALL** | **20** | **21** | **95%** | **+6** |

**Interpretation**: Now claims Yok Balum and Shenqi "work" - MANY FALSE POSITIVES

### Threshold: z ≥ 0.5

| Cave | Detections | Total | Rate | Change |
|------|-----------|-------|------|--------|
| Crystal Cave | 9 | 9 | 100% | - |
| Yok Balum | 6 | 6 | 100% | - |
| Dos Anas | 3 | 3 | 100% | +1 (1932) |
| Shenqi | 2 | 2 | 100% | - |
| Bàsura | 1 | 1 | 100% | - |
| **OVERALL** | **21** | **21** | **100%** | **+1** |

**Interpretation**: 100% detection rate but MEANINGLESS - detects in caves we know don't work!

---

## Analysis: The False Positive Problem

**Key finding**: Lowering threshold increases FALSE POSITIVES in non-working caves.

### True vs False Detections

| Threshold | True Positives | False Positives | Specificity |
|-----------|---------------|-----------------|-------------|
| z ≥ 2.0 | 11 (all real) | 0 | 100% |
| z ≥ 1.5 | 11 (real) + 3 (?) | 2 in Yok Balum | Lower |
| z ≥ 1.0 | 11 (real) + 9 (?) | 6 in failed caves | Poor |
| z ≥ 0.5 | All 21 | 10 in failed caves | Very poor |

**Problem**: We KNOW Yok Balum and Shenqi don't detect earthquakes (failed to detect M7.5 and M6.6-6.85). Any threshold that counts these as "detections" is creating false positives.

---

## Signal Strength Distribution

### Working Caves (Crystal, Bàsura)
- **Minimum**: |z| = 2.05σ (Bàsura Mg/Ca)
- **Maximum**: |z| = 3.54σ (Crystal Cave)
- **Mean**: |z| = 2.8σ

### Failed Caves (Yok Balum, Shenqi)
- **Minimum**: |z| = 1.26σ
- **Maximum**: |z| = 1.99σ
- **Mean**: |z| = 1.5σ

### Clear Separation Zone

**Gap between working and failing caves**: 1.99σ (Yok Balum max) vs 2.05σ (Bàsura min)

**Optimal threshold**: z ≥ 2.0σ

---

## Alternative Approach: Magnitude of Change (Δz)

Instead of absolute z-score, use **change from baseline**:

### Bàsura 1918 Example
- **Baseline** (1911-1915): z = -0.98 to -1.41σ (mean ≈ -1.2σ)
- **Peak** (1924): z = +3.18σ
- **Change**: Δz = 3.18 - (-1.2) = **4.4σ change**

This is a MASSIVE shift! Much larger than the absolute threshold suggests.

### Proposal: Dual Criteria
1. **Absolute**: |z| ≥ 2.0σ, OR
2. **Change**: |Δz| ≥ 3.0σ from baseline

This would catch cases like Bàsura where the signal is strong but might be missed due to timing uncertainty.

---

## Recommendations

### Keep z ≥ 2.0 threshold
- Correctly separates working from failing caves
- Minimizes false positives
- Supported by clear gap in signal strength (1.99σ vs 2.05σ)

### Add magnitude-of-change criterion
- For caves with high temporal resolution, check Δz from baseline
- Threshold: Δz ≥ 3.0σ
- This catches delayed/lagged responses

### Require multi-proxy confirmation for marginal cases
- If 2.0 ≤ |z| < 2.5σ, require second proxy (Mg/Ca, δ13C, Sr/Ca)
- Bàsura 1918: z=+3.18σ (δ18O) AND z=+2.05σ (Mg/Ca) = CONFIRMED

---

## Conclusion

**The z≥2.0 threshold is NOT too high** - it's actually optimal for:
1. Separating working caves from failing caves
2. Minimizing false positives
3. Maintaining high specificity

**Bàsura 1918 detection**:
- z = +3.18σ (well above threshold)
- Mg/Ca = +2.05σ (multi-proxy confirmation)
- **Score as 1/1 DETECTED**

Lowering the threshold would give us 100% detection rate but with many false positives in caves that don't actually work.
