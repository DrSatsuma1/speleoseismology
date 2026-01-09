#!/usr/bin/env python3
"""
Test Yok Balum Cave response to ALL modern earthquakes from validation matrix.

Events to test:
- 1976-02-04 M7.5 (30 km) - Motagua Fault mainshock
- 1976-02-08 M5.6 (50 km) - Aftershock
- 1976-02-09 M5.2 (10 km) - Aftershock
- 1980-08-08 M6.4 (60 km) - Puerto Barrios
- 1980-09-02 M5.3 (70 km) - Honduras
- 1999-07-11 M6.7 (80 km) - Honduras
"""

import pandas as pd
import numpy as np
import os

# Set up paths
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
sisal_path = os.path.join(project_dir, 'data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv')

# Load SISAL data
d18o = pd.read_csv(os.path.join(sisal_path, 'd18O.csv'))
d13c = pd.read_csv(os.path.join(sisal_path, 'd13C.csv'))
entity = pd.read_csv(os.path.join(sisal_path, 'entity.csv'))
sample = pd.read_csv(os.path.join(sisal_path, 'sample.csv'))
chronology = pd.read_csv(os.path.join(sisal_path, 'sisal_chronology.csv'))

# Find Yok Balum entity (YOKI)
yb_id = 209

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

# Calculate z-scores
d18o_mean = yb_d18o['d18O_measurement'].mean()
d18o_std = yb_d18o['d18O_measurement'].std()
yb_d18o['z_score'] = (yb_d18o['d18O_measurement'] - d18o_mean) / d18o_std

d13c_mean = yb_d13c['d13C_measurement'].mean()
d13c_std = yb_d13c['d13C_measurement'].std()
yb_d13c['z_score'] = (yb_d13c['d13C_measurement'] - d13c_mean) / d13c_std

print(f"=== Yok Balum Cave (YOKI) - Modern Earthquake Validation ===\n")
print(f"Data coverage: {yb_d18o['year_CE'].min():.0f} - {yb_d18o['year_CE'].max():.0f} CE")
print(f"Baseline: δ18O μ={d18o_mean:.2f}‰ σ={d18o_std:.2f}‰")
print(f"          δ13C μ={d13c_mean:.2f}‰ σ={d13c_std:.2f}‰\n")

# Define test events
test_events = [
    {"date": "1976-02-04", "year": 1976.1, "mag": 7.5, "dist_km": 30, "location": "Los Amates (Motagua)", "window": 5},
    {"date": "1976-02-08", "year": 1976.1, "mag": 5.6, "dist_km": 50, "location": "Aftershock", "window": 2},
    {"date": "1976-02-09", "year": 1976.1, "mag": 5.2, "dist_km": 10, "location": "Aftershock", "window": 2},
    {"date": "1980-08-08", "year": 1980.6, "mag": 6.4, "dist_km": 60, "location": "Puerto Barrios", "window": 5},
    {"date": "1980-09-02", "year": 1980.7, "mag": 5.3, "dist_km": 70, "location": "Honduras", "window": 5},
    {"date": "1999-07-11", "year": 1999.5, "mag": 6.7, "dist_km": 80, "location": "Honduras", "window": 5},
]

print("="*90)
print(f"{'Event':<20} {'Mag':<6} {'Dist':<8} {'δ18O z':<12} {'δ13C z':<12} {'Detection':<12}")
print("="*90)

results = []

for event in test_events:
    year = event['year']
    window = event['window']

    # Get data in window
    event_d18o = yb_d18o[(yb_d18o['year_CE'] >= year - window) &
                         (yb_d18o['year_CE'] <= year + window)]
    event_d13c = yb_d13c[(yb_d13c['year_CE'] >= year - window) &
                         (yb_d13c['year_CE'] <= year + window)]

    if len(event_d18o) > 0 and len(event_d13c) > 0:
        d18o_min = event_d18o['z_score'].min()
        d18o_max = event_d18o['z_score'].max()
        d13c_min = event_d13c['z_score'].min()
        d13c_max = event_d13c['z_score'].max()

        # Use most extreme deviation
        d18o_z = d18o_min if abs(d18o_min) > abs(d18o_max) else d18o_max
        d13c_z = d13c_min if abs(d13c_min) > abs(d13c_max) else d13c_max

        # Check for detection
        if abs(d18o_z) >= 2.0 or abs(d13c_z) >= 2.0:
            if abs(d18o_z) >= 2.0 and abs(d13c_z) >= 2.0:
                detection = "✓ STRONG"
            else:
                detection = "✓ WEAK"
        else:
            detection = "✗ NONE"

        print(f"{event['date']:<20} M{event['mag']:<5.1f} {event['dist_km']:>3d} km   "
              f"{d18o_z:+6.2f}σ      {d13c_z:+6.2f}σ      {detection:<12}")

        results.append({
            'event': event['date'],
            'mag': event['mag'],
            'dist_km': event['dist_km'],
            'd18o_z': d18o_z,
            'd13c_z': d13c_z,
            'detection': detection
        })
    else:
        print(f"{event['date']:<20} M{event['mag']:<5.1f} {event['dist_km']:>3d} km   NO DATA")

print("="*90)

# Summary
detections = [r for r in results if '✓' in r['detection']]
print(f"\nSummary: {len(detections)}/{len(results)} events detected (z≥2.0 threshold)")

if len(detections) == 0:
    print("\n⚠️ CRITICAL FINDING: NO modern earthquakes detected at Yok Balum Cave!")
    print("\nThis suggests:")
    print("1. Local Motagua Fault earthquakes don't trigger speleothem response")
    print("2. Strike-slip mechanism may not produce hydrological signal")
    print("3. Cave stopped growing or became insensitive after ~1793 CE")
    print("4. Previous detections (~495, ~620, ~700 CE) may have been from DIFFERENT fault systems")
