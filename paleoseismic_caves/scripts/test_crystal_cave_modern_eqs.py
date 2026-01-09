#!/usr/bin/env python3
"""
CRITICAL TEST: Crystal Cave response to modern earthquakes (1910-2006).

This test determines if the methodology survives. If Crystal Cave ALSO shows
0% detection like Yok Balum, the entire methodology is in serious trouble.

Known result:
- 1896 Independence M6.3 (48 km): ✓ DETECTED z=-3.54σ

Testing 8 additional events:
- 1910-05-06 M6.0 ~40 km Bishop, CA
- 1912-01-04 M5.5 ~50 km Bishop, CA
- 1915-05-28 M5.0 ~30 km Springville, CA
- 1929-11-28 M5.5 ~35 km Independence, CA
- 1984-11-23 M6.1 ~100 km Round Valley, CA
- 1984-11-23 M5.5 ~95 km Round Valley, CA
- 1984-11-26 M5.6 ~95 km Round Valley, CA
- 1985-03-25 M5.1 ~95 km Round Valley, CA
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
entity = pd.read_csv(os.path.join(sisal_path, 'entity.csv'))
sample = pd.read_csv(os.path.join(sisal_path, 'sample.csv'))
chronology = pd.read_csv(os.path.join(sisal_path, 'sisal_chronology.csv'))

# Find Crystal Cave entity (CRC-3)
crystal = entity[entity['entity_name'] == 'CRC-3']
if len(crystal) == 0:
    print("ERROR: CRC-3 not found. Searching for Crystal Cave...")
    crystal = entity[entity['entity_name'].str.contains('Crystal', case=False, na=False)]
    print(crystal[['entity_id', 'entity_name']])
    exit(1)

crystal_id = crystal.iloc[0]['entity_id']
print(f"\n=== Crystal Cave (CRC-3) ===")
print(f"Entity ID: {crystal_id}")

# Get sample ages
crystal_samples = sample[sample['entity_id'] == crystal_id][['sample_id', 'depth_sample']]
crystal_samples = crystal_samples.merge(chronology[['sample_id', 'lin_interp_age']], on='sample_id', how='left')
crystal_samples = crystal_samples.rename(columns={'lin_interp_age': 'interp_age'})
crystal_samples['year_CE'] = 1950 - crystal_samples['interp_age']

# Get δ18O data
crystal_d18o = d18o[d18o['sample_id'].isin(crystal_samples['sample_id'])].copy()
crystal_d18o = crystal_d18o.merge(crystal_samples[['sample_id', 'year_CE']], on='sample_id')
crystal_d18o = crystal_d18o.sort_values('year_CE')

print(f"\n=== Data Coverage ===")
print(f"δ18O: {crystal_d18o['year_CE'].min():.0f} - {crystal_d18o['year_CE'].max():.0f} CE ({len(crystal_d18o)} measurements)")

# Calculate z-scores
d18o_mean = crystal_d18o['d18O_measurement'].mean()
d18o_std = crystal_d18o['d18O_measurement'].std()
crystal_d18o['z_score'] = (crystal_d18o['d18O_measurement'] - d18o_mean) / d18o_std

print(f"\n=== Baseline Statistics ===")
print(f"δ18O: μ={d18o_mean:.2f}‰, σ={d18o_std:.2f}‰")

# Define test events
test_events = [
    {"date": "1896-07-21", "year": 1896.55, "mag": 6.3, "dist_km": 48, "location": "Independence", "window": 5, "known": True},
    {"date": "1910-05-06", "year": 1910.35, "mag": 6.0, "dist_km": 40, "location": "Bishop", "window": 5, "known": False},
    {"date": "1912-01-04", "year": 1912.01, "mag": 5.5, "dist_km": 50, "location": "Bishop", "window": 5, "known": False},
    {"date": "1915-05-28", "year": 1915.40, "mag": 5.0, "dist_km": 30, "location": "Springville", "window": 5, "known": False},
    {"date": "1929-11-28", "year": 1929.91, "mag": 5.5, "dist_km": 35, "location": "Independence", "window": 5, "known": False},
    {"date": "1984-11-23", "year": 1984.90, "mag": 6.1, "dist_km": 100, "location": "Round Valley", "window": 5, "known": False},
    {"date": "1984-11-23", "year": 1984.90, "mag": 5.5, "dist_km": 95, "location": "Round Valley (AS)", "window": 5, "known": False},
    {"date": "1984-11-26", "year": 1984.90, "mag": 5.6, "dist_km": 95, "location": "Round Valley (AS)", "window": 5, "known": False},
    {"date": "1985-03-25", "year": 1985.23, "mag": 5.1, "dist_km": 95, "location": "Round Valley (AS)", "window": 5, "known": False},
]

print(f"\n{'='*100}")
print(f"CRITICAL TEST: Crystal Cave Modern Earthquake Detection")
print(f"{'='*100}\n")

print(f"{'Event':<20} {'Mag':<6} {'Dist':<8} {'Data':<8} {'δ18O z':<12} {'Detection':<15} {'Status':<10}")
print("="*100)

results = []
detections = 0
non_detections = 0
no_data = 0

for event in test_events:
    year = event['year']
    window = event['window']

    # Get data in window
    event_d18o = crystal_d18o[(crystal_d18o['year_CE'] >= year - window) &
                              (crystal_d18o['year_CE'] <= year + window)]

    if len(event_d18o) > 0:
        d18o_min = event_d18o['z_score'].min()
        d18o_max = event_d18o['z_score'].max()

        # Use most extreme deviation
        d18o_z = d18o_min if abs(d18o_min) > abs(d18o_max) else d18o_max

        # Check for detection
        if abs(d18o_z) >= 2.0:
            detection = "✓ DETECTED"
            detections += 1
            status = "NEW" if not event['known'] else "KNOWN"
        else:
            detection = "✗ NO"
            non_detections += 1
            status = "FAILED"

        print(f"{event['date']:<20} M{event['mag']:<5.1f} {event['dist_km']:>3d} km   "
              f"{len(event_d18o):>2d} samp  {d18o_z:+6.2f}σ      {detection:<15} {status:<10}")

        results.append({
            'event': event['date'],
            'mag': event['mag'],
            'dist_km': event['dist_km'],
            'd18o_z': d18o_z,
            'n_samples': len(event_d18o),
            'detection': detection,
            'known': event['known']
        })
    else:
        print(f"{event['date']:<20} M{event['mag']:<5.1f} {event['dist_km']:>3d} km   NO DATA")
        no_data += 1

print("="*100)

# Summary
total_tested = len([r for r in results])
print(f"\n{'='*100}")
print(f"RESULTS SUMMARY")
print(f"{'='*100}\n")
print(f"Total events tested: {total_tested + no_data}")
print(f"Events with data: {total_tested}")
print(f"Events without data: {no_data}")
print(f"\nDETECTIONS: {detections}/{total_tested}")
print(f"NON-DETECTIONS: {non_detections}/{total_tested}")
print(f"\n**DETECTION RATE: {100*detections/total_tested if total_tested > 0 else 0:.1f}%**\n")

# Verdict
print("="*100)
print("VERDICT")
print("="*100 + "\n")

if detections >= 5:  # >50% detection rate
    print("✓ METHODOLOGY SURVIVES")
    print("  - High detection rate indicates reliable method")
    print("  - Yok Balum failure is cave-specific, not methodology-wide")
    print("  - Can proceed with confidence in prehistoric detections")
elif detections >= 2:  # 20-50% detection rate
    print("⚠️ METHODOLOGY UNCERTAIN")
    print("  - Moderate detection rate suggests limited reliability")
    print("  - Distance/magnitude thresholds unclear")
    print("  - Need more testing before publication")
elif detections == 1:  # Only the known 1896 event
    print("✗✗✗ METHODOLOGY FAILED ✗✗✗")
    print("  - Only 1896 detection (already known)")
    print("  - NO new detections despite good coverage")
    print("  - Same pattern as Yok Balum (0% modern detection)")
    print("  - ALL prehistoric detections now HIGHLY SUSPECT")
    print("\n  ** CRISIS: The methodology does not reliably detect earthquakes **")
else:
    print("✗✗✗ CATASTROPHIC FAILURE ✗✗✗")
    print("  - ZERO detections including known 1896 event")
    print("  - Methodology completely unreliable")
    print("  - Previous 1896 detection may have been sampling/analysis error")

print()

# Show distance vs magnitude pattern
if len(results) > 0:
    print("\n" + "="*100)
    print("DISTANCE vs MAGNITUDE ANALYSIS")
    print("="*100 + "\n")

    detected = [r for r in results if '✓' in r['detection']]
    not_detected = [r for r in results if '✗' in r['detection']]

    if len(detected) > 0:
        print(f"DETECTED events (n={len(detected)}):")
        for r in detected:
            print(f"  M{r['mag']:.1f} at {r['dist_km']} km → z={r['d18o_z']:+.2f}σ")

    if len(not_detected) > 0:
        print(f"\nNOT DETECTED events (n={len(not_detected)}):")
        for r in not_detected:
            print(f"  M{r['mag']:.1f} at {r['dist_km']} km → z={r['d18o_z']:+.2f}σ")

    print()
