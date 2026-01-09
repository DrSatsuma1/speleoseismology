#!/usr/bin/env python3
"""
Test Dos Anas Cave (Cuba) - modern earthquake validation.

Known: 1766 M7.6 was detected (post-hoc test).
Need to test if cave responds to OTHER modern earthquakes.

Cave: CG entity (Dos Anas)
Coverage: 769-2016 CE
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

# Find Dos Anas (CG)
dos_anas = entity[entity['entity_name'] == 'CG']
if len(dos_anas) == 0:
    print("ERROR: CG (Dos Anas) not found")
    exit(1)

da_id = dos_anas.iloc[0]['entity_id']
print(f"=== Dos Anas Cave (Cuba) - CG Entity ===")
print(f"Entity ID: {da_id}\n")

# Get samples
da_samples = sample[sample['entity_id'] == da_id][['sample_id']]
da_samples = da_samples.merge(chronology[['sample_id', 'lin_interp_age']], on='sample_id', how='left')
da_samples = da_samples.rename(columns={'lin_interp_age': 'interp_age'})
da_samples['year_CE'] = 1950 - da_samples['interp_age']

# Get δ18O
da_d18o = d18o[d18o['sample_id'].isin(da_samples['sample_id'])].copy()
da_d18o = da_d18o.merge(da_samples[['sample_id', 'year_CE']], on='sample_id')
da_d18o = da_d18o.sort_values('year_CE')

print(f"Coverage: {da_d18o['year_CE'].min():.0f} - {da_d18o['year_CE'].max():.0f} CE")
print(f"Measurements: {len(da_d18o)}\n")

# Calculate z-scores
d18o_mean = da_d18o['d18O_measurement'].mean()
d18o_std = da_d18o['d18O_measurement'].std()
da_d18o['z_score'] = (da_d18o['d18O_measurement'] - d18o_mean) / d18o_std

print(f"Baseline: δ18O μ={d18o_mean:.2f}‰, σ={d18o_std:.2f}‰\n")

# Test modern earthquakes near Cuba (Oriente fault)
# From validation: Need to search for Cuban earthquakes 1800-2000
test_events = [
    {"year": 1766, "mag": 7.6, "location": "Santiago (Oriente)", "known": True},
    {"year": 1852, "mag": 6.8, "location": "Santiago", "known": False},
    {"year": 1932, "mag": 6.7, "location": "Santiago", "known": False},
]

print("="*80)
print("Testing Dos Anas modern earthquakes")
print("="*80 + "\n")

results = []
for event in test_events:
    year = event['year']
    window = 10

    event_d18o = da_d18o[(da_d18o['year_CE'] >= year - window) &
                         (da_d18o['year_CE'] <= year + window)]

    if len(event_d18o) > 0:
        z_min = event_d18o['z_score'].min()
        z_max = event_d18o['z_score'].max()
        z_extreme = z_min if abs(z_min) > abs(z_max) else z_max

        detection = "✓" if abs(z_extreme) >= 2.0 else "✗"
        status = "KNOWN" if event['known'] else "NEW"

        print(f"{year} M{event['mag']:.1f} {event['location']:<20} | "
              f"{len(event_d18o):2d} samples | z={z_extreme:+.2f}σ | {detection} {status}")

        results.append({
            'year': year,
            'detected': abs(z_extreme) >= 2.0
        })
    else:
        print(f"{year} M{event['mag']:.1f} {event['location']:<20} | NO DATA")

print("\n" + "="*80)
detections = sum([r['detected'] for r in results])
total = len(results)
print(f"RESULT: {detections}/{total} detected")
print("="*80)
