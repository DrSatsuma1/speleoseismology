#!/usr/bin/env python3
"""
Test Yok Balum Cave response to 1976 M7.5 Guatemala earthquake.

Event details:
- Date: 1976-02-04
- Magnitude: M7.5
- Distance: ~30 km from Yok Balum Cave
- Location: Los Amates, Guatemala (Motagua Fault rupture)
- Cave data coverage: 25 BCE - 2006 CE

Expected result: Strong signal (z < -3.0) at 1976 ± 5 years
"""

import pandas as pd
import numpy as np
import os

# Set up paths
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
sisal_path = os.path.join(project_dir, 'data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv')

# Load SISAL data
print("Loading SISAL data...")
d18o = pd.read_csv(os.path.join(sisal_path, 'd18O.csv'))
d13c = pd.read_csv(os.path.join(sisal_path, 'd13C.csv'))
entity = pd.read_csv(os.path.join(sisal_path, 'entity.csv'))
sample = pd.read_csv(os.path.join(sisal_path, 'sample.csv'))
chronology = pd.read_csv(os.path.join(sisal_path, 'sisal_chronology.csv'))

# Find Yok Balum entity (YOKI or YOKG, NOT YB-F1 which is Jersey Cave Australia!)
yb = entity[entity['entity_name'].isin(['YOKI', 'YOKG'])]
print(f"\n=== Yok Balum Cave Entities ===")
print(yb[['entity_id', 'entity_name']])

# Use YOKI (entity 209) which has the most complete record
yb_id = 209
print(f"\nUsing entity_id: {yb_id} (YOKI)")

# Get sample ages
yb_samples = sample[sample['entity_id'] == yb_id][['sample_id', 'depth_sample']]
yb_samples = yb_samples.merge(chronology[['sample_id', 'lin_interp_age']], on='sample_id', how='left')
yb_samples = yb_samples.rename(columns={'lin_interp_age': 'interp_age'})
yb_samples['year_CE'] = 1950 - yb_samples['interp_age']

# Get δ18O data
yb_d18o = d18o[d18o['sample_id'].isin(yb_samples['sample_id'])].copy()
yb_d18o = yb_d18o.merge(yb_samples[['sample_id', 'year_CE']], on='sample_id')
yb_d18o = yb_d18o.sort_values('year_CE')

# Get δ13C data
yb_d13c = d13c[d13c['sample_id'].isin(yb_samples['sample_id'])].copy()
yb_d13c = yb_d13c.merge(yb_samples[['sample_id', 'year_CE']], on='sample_id')
yb_d13c = yb_d13c.sort_values('year_CE')

print(f"\n=== Data Coverage ===")
print(f"δ18O: {yb_d18o['year_CE'].min():.0f} - {yb_d18o['year_CE'].max():.0f} CE ({len(yb_d18o)} measurements)")
print(f"δ13C: {yb_d13c['year_CE'].min():.0f} - {yb_d13c['year_CE'].max():.0f} CE ({len(yb_d13c)} measurements)")

# Calculate z-scores
d18o_mean = yb_d18o['d18O_measurement'].mean()
d18o_std = yb_d18o['d18O_measurement'].std()
yb_d18o['z_score'] = (yb_d18o['d18O_measurement'] - d18o_mean) / d18o_std

d13c_mean = yb_d13c['d13C_measurement'].mean()
d13c_std = yb_d13c['d13C_measurement'].std()
yb_d13c['z_score'] = (yb_d13c['d13C_measurement'] - d13c_mean) / d13c_std

print(f"\n=== Baseline Statistics ===")
print(f"δ18O: μ={d18o_mean:.2f}‰, σ={d18o_std:.2f}‰")
print(f"δ13C: μ={d13c_mean:.2f}‰, σ={d13c_std:.2f}‰")

# Test window: 1976 ± 10 years
event_year = 1976
test_window = 10

print(f"\n{'='*70}")
print(f"TESTING: 1976 M7.5 Guatemala Earthquake (30 km from cave)")
print(f"{'='*70}")

# Check δ18O around 1976
event_d18o = yb_d18o[(yb_d18o['year_CE'] >= event_year - test_window) &
                     (yb_d18o['year_CE'] <= event_year + test_window)]

print(f"\n--- δ18O Analysis ({event_year} ± {test_window} years) ---")
if len(event_d18o) > 0:
    print(f"Found {len(event_d18o)} measurements in window")
    print(f"\nYear     δ18O      Z-score")
    print("-" * 35)
    for _, row in event_d18o.iterrows():
        print(f"{row['year_CE']:.1f}   {row['d18O_measurement']:+.2f}‰   {row['z_score']:+.2f}σ")

    min_z = event_d18o['z_score'].min()
    max_z = event_d18o['z_score'].max()
    mean_z = event_d18o['z_score'].mean()

    print(f"\nStatistics:")
    print(f"  Min z-score: {min_z:+.2f}σ")
    print(f"  Max z-score: {max_z:+.2f}σ")
    print(f"  Mean z-score: {mean_z:+.2f}σ")

    if min_z < -2.0:
        print(f"\n✓ DETECTION: Negative excursion z={min_z:.2f}σ < -2.0 threshold")
    elif max_z > 2.0:
        print(f"\n✓ DETECTION: Positive excursion z={max_z:.2f}σ > +2.0 threshold")
    else:
        print(f"\n✗ NO DETECTION: |z| < 2.0 threshold")
else:
    print("✗ NO DATA in this window")

# Check δ13C around 1976
event_d13c = yb_d13c[(yb_d13c['year_CE'] >= event_year - test_window) &
                     (yb_d13c['year_CE'] <= event_year + test_window)]

print(f"\n--- δ13C Analysis ({event_year} ± {test_window} years) ---")
if len(event_d13c) > 0:
    print(f"Found {len(event_d13c)} measurements in window")
    print(f"\nYear     δ13C      Z-score")
    print("-" * 35)
    for _, row in event_d13c.iterrows():
        print(f"{row['year_CE']:.1f}   {row['d13C_measurement']:+.2f}‰   {row['z_score']:+.2f}σ")

    min_z = event_d13c['z_score'].min()
    max_z = event_d13c['z_score'].max()
    mean_z = event_d13c['z_score'].mean()

    print(f"\nStatistics:")
    print(f"  Min z-score: {min_z:+.2f}σ")
    print(f"  Max z-score: {max_z:+.2f}σ")
    print(f"  Mean z-score: {mean_z:+.2f}σ")

    if min_z < -2.0:
        print(f"\n✓ DETECTION: Negative excursion z={min_z:.2f}σ < -2.0 threshold")
    elif max_z > 2.0:
        print(f"\n✓ DETECTION: Positive excursion z={max_z:.2f}σ > +2.0 threshold")
    else:
        print(f"\n✗ NO DETECTION: |z| < 2.0 threshold")
else:
    print("✗ NO DATA in this window")

# Check proxy coupling
print(f"\n--- Proxy Coupling Analysis ---")
if len(event_d18o) > 0 and len(event_d13c) > 0:
    d18o_min_z = event_d18o['z_score'].min()
    d13c_min_z = event_d13c['z_score'].min()

    print(f"δ18O min z-score: {d18o_min_z:+.2f}σ")
    print(f"δ13C min z-score: {d13c_min_z:+.2f}σ")

    if d18o_min_z < -1.5 and d13c_min_z < -1.5:
        print("\n✓ COUPLED: Both proxies show negative excursions (SEISMIC signal)")
    elif d18o_min_z < -2.0 and abs(d13c_min_z) < 1.0:
        print("\n⚠ DECOUPLED: δ18O negative but δ13C normal (VOLCANIC/CLIMATIC?)")
    else:
        print("\n✗ NO CLEAR COUPLING")

print(f"\n{'='*70}")
print(f"CONCLUSION")
print(f"{'='*70}\n")

# Final assessment
if len(event_d18o) > 0:
    d18o_detection = event_d18o['z_score'].min() < -2.0 or event_d18o['z_score'].max() > 2.0
else:
    d18o_detection = False

if len(event_d13c) > 0:
    d13c_detection = event_d13c['z_score'].min() < -2.0 or event_d13c['z_score'].max() > 2.0
else:
    d13c_detection = False

if d18o_detection and d13c_detection:
    print("RESULT: STRONG DETECTION (both proxies)")
    print("Expected: z < -3.0 for M7.5 at 30 km")
elif d18o_detection or d13c_detection:
    print("RESULT: PARTIAL DETECTION (one proxy)")
else:
    print("RESULT: NO DETECTION")
    print("\nPossible explanations:")
    print("1. Cave data ends before 1976 (check coverage)")
    print("2. Temporal resolution too coarse to capture signal")
    print("3. Local geology/hydrology prevented response")
    print("4. Cave growth hiatus during this period")

print()
