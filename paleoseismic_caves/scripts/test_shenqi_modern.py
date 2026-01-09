#!/usr/bin/env python3
"""
Test Shenqi Cave (China) - modern earthquake validation.

From validation matrix:
- 38 earthquakes M≥5.0 (1935-2014)
- Cave: SQ1 entity
- Coverage: -317 to 1964 CE
- Key events: 1974 M6.8 (70 km), 1952 M6.62 (60 km), 1936 M6.85 (90 km)
"""

import pandas as pd
import numpy as np
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
sisal_path = os.path.join(project_dir, 'data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv')

# Load data
d18o = pd.read_csv(os.path.join(sisal_path, 'd18O.csv'))
entity = pd.read_csv(os.path.join(sisal_path, 'entity.csv'))
sample = pd.read_csv(os.path.join(sisal_path, 'sample.csv'))
chronology = pd.read_csv(os.path.join(sisal_path, 'sisal_chronology.csv'))

# Find Shenqi (SQ1)
shenqi = entity[entity['entity_name'] == 'SQ1']
if len(shenqi) == 0:
    print("ERROR: SQ1 (Shenqi) not found")
    exit(1)

sq_id = shenqi.iloc[0]['entity_id']
print(f"=== Shenqi Cave (China) - SQ1 Entity ===")
print(f"Entity ID: {sq_id}\n")

# Get samples
sq_samples = sample[sample['entity_id'] == sq_id][['sample_id']]
sq_samples = sq_samples.merge(chronology[['sample_id', 'lin_interp_age']], on='sample_id', how='left')
sq_samples = sq_samples.rename(columns={'lin_interp_age': 'interp_age'})
sq_samples['year_CE'] = 1950 - sq_samples['interp_age']

# Get δ18O
sq_d18o = d18o[d18o['sample_id'].isin(sq_samples['sample_id'])].copy()
sq_d18o = sq_d18o.merge(sq_samples[['sample_id', 'year_CE']], on='sample_id')
sq_d18o = sq_d18o.sort_values('year_CE')

print(f"Coverage: {sq_d18o['year_CE'].min():.0f} - {sq_d18o['year_CE'].max():.0f} CE")
print(f"Measurements: {len(sq_d18o)}\n")

# Calculate z-scores
d18o_mean = sq_d18o['d18O_measurement'].mean()
d18o_std = sq_d18o['d18O_measurement'].std()
sq_d18o['z_score'] = (sq_d18o['d18O_measurement'] - d18o_mean) / d18o_std

print(f"Baseline: δ18O μ={d18o_mean:.2f}‰, σ={d18o_std:.2f}‰\n")

# Test major earthquakes (from validation matrix)
test_events = [
    {"year": 1936, "mag": 6.85, "dist_km": 90, "location": "Sichuan"},
    {"year": 1952, "mag": 6.62, "dist_km": 60, "location": "Xichang"},
]

print("="*90)
print("Testing Shenqi modern earthquakes (data ends 1964)")
print("="*90 + "\n")

if sq_d18o['year_CE'].max() < 1936:
    print(f"⚠️  Cave data ends at {sq_d18o['year_CE'].max():.0f} CE")
    print(f"    Cannot test earthquakes from 1936-1974 (no overlap)")
    print()
    exit(0)

results = []
for event in test_events:
    year = event['year']
    window = 5

    event_d18o = sq_d18o[(sq_d18o['year_CE'] >= year - window) &
                         (sq_d18o['year_CE'] <= year + window)]

    if len(event_d18o) > 0:
        z_min = event_d18o['z_score'].min()
        z_max = event_d18o['z_score'].max()
        z_extreme = z_min if abs(z_min) > abs(z_max) else z_max

        detection = "✓" if abs(z_extreme) >= 2.0 else "✗"

        print(f"{year} M{event['mag']:.1f} ({event['dist_km']} km) {event['location']:<15} | "
              f"{len(event_d18o):2d} samples | z={z_extreme:+.2f}σ | {detection}")

        results.append({
            'year': year,
            'detected': abs(z_extreme) >= 2.0
        })
    else:
        print(f"{year} M{event['mag']:.1f} ({event['dist_km']} km) {event['location']:<15} | NO DATA")

print("\n" + "="*90)
if len(results) > 0:
    detections = sum([r['detected'] for r in results])
    total = len(results)
    print(f"RESULT: {detections}/{total} detected ({100*detections/total:.0f}%)")
else:
    print("RESULT: No testable events (cave data too old)")
print("="*90)
