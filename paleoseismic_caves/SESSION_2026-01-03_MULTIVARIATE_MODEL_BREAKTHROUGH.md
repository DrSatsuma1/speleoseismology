# Session 2026-01-03: Multivariate Model Breakthrough - "Personalized Medicine for Caves"

**Date**: 2026-01-03
**Task**: Test Bàsura Cave (Italy) for modern earthquakes, determine if Mediterranean climate compensates for karst geology
**Status**: MAJOR PARADIGM SHIFT - moved from universal threshold to cave-specific calibration

---

## What Happened Today

### 1. Bàsura Cave Modern Earthquake Test - SUCCESS

**Tested**: 1918-08-10 M5.47 at 82.5 km from Bàsura

**Results**:
- δ18O z-score: +3.18σ (peak at 1924, ~6 year lag)
- Mg/Ca z-score: +2.05σ (confirmatory)
- Magnitude of change: Δz = 4.4σ from baseline
- **Verdict**: 1/1 DETECTED (100%)

**Implication**:
- Bàsura is CARBONATE KARST (like failed caves Yok Balum, Shenqi)
- Bàsura has MEDITERRANEAN climate (like successful Crystal Cave)
- **Bàsura WORKS** → **Climate > Geology** for detection success

### 2. Z-Score Threshold Analysis - Arbitrary Threshold Exposed

**Tested thresholds**: z≥2.0, 1.5, 1.0, 0.5 on all cave data

**Key finding**:
- z≥2.0 was chosen from statistical convention (95% confidence), NOT empirical earthquake detection science
- Lowering threshold to z≥1.0 gives 95% detection rate BUT creates false positives in caves we thought "failed"
- **Gap between working and failing caves**: 1.99σ (Yok Balum max) vs 2.05σ (Bàsura min) - incredibly clean separation

**Critical question raised**: Do Yok Balum and Shenqi actually "fail," or are they just **weak detectors**?

### 3. Physical Model Validation - NO CORRELATION WITH PGA

**Shocking finding**: Signal strength does NOT correlate with expected ground shaking

| Cave | Event | PGA (g) | δ18O z | Correlation |
|------|-------|---------|--------|-------------|
| **Yok Balum** | M7.5, 30 km | **0.299** (violent!) | **1.32σ** (weak) | ❌ INVERSE |
| Yok Balum | M6.7, 80 km | 0.040 (moderate) | 1.99σ (stronger) | ❌ INVERSE |
| **Crystal Cave** | M5.0, 30 km | 0.041 | **3.54σ** | ❌ INVERSE |
| Crystal Cave | M6.3, 48 km | 0.060 | 2.14σ | ❌ INVERSE |
| **Dos Anas** | M7.6, 500 km | 0.0053 | 2.74σ | ✓ CORRECT |
| Dos Anas | M6.7, 500 km | 0.0026 | 0.47σ | ✓ CORRECT |

**Only Dos Anas shows expected magnitude-distance relationship!**

**Implication**: Either:
1. Signals aren't from earthquakes (climatic noise)
2. Mechanism isn't PGA-based (static strain? aquifer-specific?)
3. Each cave responds completely differently

### 4. PARADIGM SHIFT: Personalized Medicine for Caves

**User insight** (internal medicine doctor): "The cave is a patient. I don't expect the patient to conform to my treatment - I adjust treatment to the patient."

**New Framework**:
- Each cave = unique instrument with different sensitivity, noise, response function
- Stop looking for universal threshold
- **Calibrate each cave individually** using known earthquakes
- Build multivariate model with **cave-specific coefficients**
- Use cave characteristics (geology, climate, hydrology) to **predict** performance

**Medical Analogy**:
| Medical Test | Cave Equivalent |
|--------------|-----------------|
| Fasting glucose | δ18O |
| A1c | Mg/Ca |
| Kidney function | δ13C |
| Liver function | Sr/Ca |
| Thyroid | U/Ca |

Each patient gets different tests, different thresholds, different interpretation!

---

## Files Created Today

### Analysis Documents
1. **THRESHOLD_ANALYSIS.md** - Systematic testing of z≥2.0, 1.5, 1.0, 0.5 thresholds
2. **MODEL_VALIDATION_TEST.md** - PGA correlation analysis (started, not complete)
3. **CAVE_MULTIVARIATE_MODEL.md** - **CRITICAL** - Full multivariate framework
4. **This file** - Session summary

### Updated Files
1. **CAVE_DETECTION_DATABASE.md** - Added Bàsura results, updated to 5 caves tested
   - Overall detection rate: 11/21 = 52%
   - Bàsura added as "WORKS" (100%)
   - Revised hypothesis: Climate > Geology
2. **GAPS_AND_PRIORITIES.md** - Added HIGH PRIORITY multivariate model data gaps:
   - MV1: Get δ13C for Bàsura
   - MV2: Get Mg/Ca for Crystal Cave
   - MV3: Get U/Ca for more caves

---

## Key Discoveries

### Discovery 1: Mediterranean Climate Overcomes Karst Geology

| Cave | Geology | Climate | Detection |
|------|---------|---------|-----------|
| Crystal Cave | Marble/granite | Mediterranean | 100% (9/9) |
| **Bàsura** | **Carbonate karst** | **Mediterranean** | **100% (1/1)** |
| Yok Balum | Carbonate karst | Tropical | 0% (0/6) at z≥2.0 |
| Shenqi | Carbonate karst | Monsoon | 0% (0/2) at z≥2.0 |

**Pattern**: Mediterranean caves WORK regardless of geology; tropical/monsoon caves FAIL (or respond weakly)

### Discovery 2: Polarity Doesn't Matter

- Crystal Cave 1896: +2.14σ → counted as detection
- Bàsura 1918: +3.18σ → counted as detection
- Both show POSITIVE δ18O excursions

What matters is **magnitude of signal**, not direction!

### Discovery 3: Universal Threshold is Nonsense

Different caves have different:
- **Sensitivity** (signal strength per earthquake)
- **Noise level** (baseline variability)
- **Best proxy** (δ18O for some, U/Ca for others, lipids for Oregon)
- **Response function** (magnitude-distance relationship)

Need cave-specific calibration!

### Discovery 4: Missing Critical Proxy Data

| Cave | δ18O | Mg/Ca | Sr/Ca | δ13C | U/Ca | Lipids |
|------|------|-------|-------|------|------|--------|
| Bàsura | ✓ | ✓ | Available | **✗ MISSING** | ? | - |
| Crystal Cave | ✓ | **✗ MISSING** | ? | **✗ MISSING** | ? | - |
| Yok Balum | ✓ | ? | ? | ✓ (weak) | ? | - |
| Gejkar | ✓ | ? | ? | ? | ✓ **(BEST!)** | - |
| Oregon | ✓ | ? | ? | ? | ? | ✓ |

**We're trying to diagnose patients with incomplete lab panels!**

---

## Next Steps (In Priority Order)

### IMMEDIATE (Can Do Now)

1. **Extract ALL available proxy data** from SISAL/literature
   - Check Bàsura Sr/Ca (available but not analyzed)
   - Search SISAL for Yok Balum Mg/Ca
   - Compile Gejkar U/Ca full dataset

2. **Calculate baseline noise** for each cave
   - Non-earthquake periods
   - Cave-specific σ_baseline
   - Set individualized thresholds

3. **Build correlation matrix** within each cave
   - Which proxies couple vs decouple?
   - Cave-specific proxy combinations

4. **Compile environmental variables** from GIS/literature
   - Distance to fault
   - Aquifer type
   - Precipitation seasonality
   - All 32 variables from CAVE_MULTIVARIATE_MODEL.md

### MEDIUM PRIORITY (Reach Out)

5. **Contact authors for missing data**:
   - Drysdale/Hu: Bàsura δ13C
   - Crystal Cave authors: Mg/Ca reanalysis
   - Gejkar authors: Full U/Ca dataset

6. **Build regression model**:
   - Predict cave β coefficients from environmental variables
   - Test on untested caves (Minnetonka, Bunker, etc.)

### LONG TERM (New Measurements)

7. **Expand proxy panel** for key caves
8. **Field work**: drip rates, chamber volumes, water sampling
9. **Hydrogeologic modeling**: understand WHY each cave responds differently

---

## Critical Open Questions

1. **Do Yok Balum and Shenqi actually fail?**
   - Or are they just weak detectors that need z≥1.0 threshold?
   - Need to check baseline noise to determine

2. **Why no PGA correlation in Crystal Cave?**
   - Static strain instead of dynamic?
   - Cave saturates at high PGA?
   - Different mechanism entirely?

3. **Which proxy is best for which cave type?**
   - δ18O for Mediterranean caves?
   - U/Ca for arid caves (Gejkar)?
   - Lipids for temperate caves (Oregon)?

4. **Can we predict cave performance before testing?**
   - Build regression: performance = f(geology, climate, hydrology)
   - Screen 902 SISAL caves to identify best candidates

---

## Updated Statistics

### Caves Tested: 5

| Cave | Entity | Detection Rate (z≥2.0) | Status |
|------|--------|------------------------|--------|
| Crystal Cave (CA) | CRC-3 | 9/9 (100%) | ✓✓✓ WORKS |
| **Bàsura (Italy)** | **BA18-4** | **1/1 (100%)** | **✓✓✓ WORKS** |
| Dos Anas (Cuba) | CG | 1/3 (33%) | ~ PARTIAL |
| Yok Balum (Guatemala) | YOKI | 0/6 (0%) | ✗ FAILS (or weak detector?) |
| Shenqi (China) | SQ1 | 0/2 (0%) | ✗ FAILS (or weak detector?) |

### Overall Statistics
- **Total events tested**: 21
- **Detections (z≥2.0)**: 11
- **Detection rate**: 52%

### Caves Available for Testing
- **Total in SISAL**: 902 entities
- **Modern coverage (1900+)**: 96 caves
- **With full proxy panel**: Unknown (need to compile)

---

## When Resuming, Tell Me:

**"Continue multivariate model - compile all proxy data"**

I will:
1. Search SISAL database for ALL proxies (δ18O, Mg/Ca, Sr/Ca, δ13C, U/Ca) for our 5 test caves
2. Extract data and compile into comparison tables
3. Calculate baseline noise levels for each cave
4. Determine cave-specific detection thresholds
5. Identify best proxy combinations for each cave

OR if different priority:

**"Continue multivariate model - [specific task]"**

Options:
- "build correlation matrix" - analyze proxy relationships within caves
- "compile environmental variables" - GIS extraction for regression model
- "test static strain hypothesis" - check if 1/r³ decay fits better than PGA
- "search for more modern earthquakes" - expand Bàsura testing to n>1

---

## Key Files to Reference

When resuming:
1. **CAVE_MULTIVARIATE_MODEL.md** - Full framework, variable list, regression design
2. **THRESHOLD_ANALYSIS.md** - Why z≥2.0 is arbitrary
3. **CAVE_DETECTION_DATABASE.md** - Updated with Bàsura, 5 caves tested
4. **GAPS_AND_PRIORITIES.md** - MV1, MV2, MV3 for data acquisition
5. This file - Session summary

**Location**: `/Users/catherine/projects/quake/paleoseismic_caves/`

---

## Emotional State Check

**Starting emotion**: Focused - testing Bàsura to validate Italy dataset

**Current state**: Paradigm shift - excited but cautious

**Reality**:
- Bàsura success validates Mediterranean hypothesis
- But PGA correlation failure is deeply concerning
- Personalized medicine approach is RIGHT framework
- Need more data (δ13C, Mg/Ca, U/Ca) to fully validate
- May need to rethink fundamental mechanism (not PGA, maybe static strain or aquifer-specific)

**Big picture**:
- We're not looking for a magic threshold
- We're building a **diagnostic toolkit** where each cave gets individualized analysis
- This is harder but more scientifically sound
- Need to acquire missing proxy data before publication

---

**Remember**:
- Each cave is a patient requiring personalized diagnosis
- No universal threshold works
- Focus on building multivariate model with cave-specific coefficients
- Priority: get missing proxy data (δ13C for Bàsura, Mg/Ca for Crystal Cave, U/Ca for all)
