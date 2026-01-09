# Physical Model Validation: Does Signal Strength Correlate with Earthquake Strength?

**Date**: 2026-01-03
**Question**: Is the speleothem detection model physically valid, or just random noise?

---

## The Test

**If the model works**, we expect:
- Stronger earthquakes → stronger δ18O signals
- Closer earthquakes → stronger δ18O signals
- Expected relationship: |z-score| ∝ f(Magnitude, Distance)

**If the model is broken**:
- No correlation between earthquake strength and signal strength
- Random z-scores unrelated to seismic parameters

---

## Test Data: Calculate Expected PGA for All Events

Using Bindi et al. 2011 attenuation model (standard for Europe/global):

### Crystal Cave (California)

| Event | Date | Mag | Dist (km) | Expected PGA (g) | δ18O z-score | |z| |
|-------|------|-----|-----------|------------------|--------------|-----|
| Independence | 1896-07-21 | M6.3 | 48 | [calculating...] | +2.14σ | 2.14 |
| Bishop | 1910-05-06 | M6.0 | 40 | [calculating...] | -3.54σ | 3.54 |
| Bishop | 1912-01-04 | M5.5 | 50 | [calculating...] | -3.54σ | 3.54 |
| Springville | 1915-05-28 | M5.0 | 30 | [calculating...] | -3.54σ | 3.54 |
| Independence | 1929-11-28 | M5.5 | 35 | [calculating...] | -2.61σ | 2.61 |
| Round Valley | 1984-11-23 | M6.1 | 100 | [calculating...] | -2.71σ | 2.71 |
| Round Valley | 1984-11-23 | M5.5 | 95 | [calculating...] | -2.71σ | 2.71 |
| Round Valley | 1984-11-26 | M5.6 | 95 | [calculating...] | -2.71σ | 2.71 |
| Round Valley | 1985-03-25 | M5.1 | 95 | [calculating...] | -2.71σ | 2.71 |

### Yok Balum (Guatemala)

| Event | Date | Mag | Dist (km) | Expected PGA (g) | δ18O z-score | |z| |
|-------|------|-----|-----------|------------------|--------------|-----|
| Motagua | 1976-02-04 | M7.5 | 30 | [calculating...] | +1.32σ | 1.32 |
| Aftershock | 1976-02-08 | M5.6 | 50 | [calculating...] | +1.26σ | 1.26 |
| Aftershock | 1976-02-09 | M5.2 | 10 | [calculating...] | +1.26σ | 1.26 |
| Puerto Barrios | 1980-08-08 | M6.4 | 60 | [calculating...] | +1.85σ | 1.85 |
| Honduras | 1980-09-02 | M5.3 | 70 | [calculating...] | +1.85σ | 1.85 |
| Honduras | 1999-07-11 | M6.7 | 80 | [calculating...] | +1.99σ | 1.99 |

### Dos Anas (Cuba)

| Event | Date | Mag | Dist (km) | Expected PGA (g) | δ18O z-score | |z| |
|-------|------|-----|-----------|------------------|--------------|-----|
| Santiago | 1766 | M7.6 | 500 | [calculating...] | -2.74σ | 2.74 |
| Santiago | 1852 | M6.8 | 500 | [calculating...] | -1.75σ | 1.75 |
| Santiago | 1932 | M6.7 | 500 | [calculating...] | -0.47σ | 0.47 |

### Shenqi (China)

| Event | Date | Mag | Dist (km) | Expected PGA (g) | δ18O z-score | |z| |
|-------|------|-----|-----------|------------------|--------------|-----|
| Sichuan | 1936 | M6.85 | 90 | [calculating...] | -1.29σ | 1.29 |
| Xichang | 1952 | M6.62 | 60 | [calculating...] | +1.34σ | 1.34 |

### Bàsura (Italy)

| Event | Date | Mag | Dist (km) | Expected PGA (g) | δ18O z-score | |z| |
|-------|------|-----|-----------|------------------|--------------|-----|
| Southern Italy | 1918-08-10 | M5.47 | 82.5 | [calculating...] | +3.18σ | 3.18 |

---

## Calculating PGA...

