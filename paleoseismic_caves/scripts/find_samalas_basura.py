#!/usr/bin/env python3
"""
Find the 1257 Samalas volcanic spike in Bàsura Cave (BA18-4)
to validate chronological accuracy.
"""

import pandas as pd
import numpy as np

# Load SISAL v3 data
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)  # paleoseismic_caves/
BASE_PATH = os.path.join(project_root, "data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv/")

print("Loading SISAL v3 data...")
samples = pd.read_csv(BASE_PATH + "sample.csv")
d18O_data = pd.read_csv(BASE_PATH + "d18O.csv")
chronology = pd.read_csv(BASE_PATH + "sisal_chronology.csv")

# Get BA18-4 samples (entity_id = 297)
print("\nFiltering BA18-4 samples...")
ba18_samples = samples[samples['entity_id'] == 297]['sample_id'].values
print(f"Found {len(ba18_samples)} BA18-4 samples")

# Get d18O values
print("\nMerging d18O data...")
ba18_d18O = d18O_data[d18O_data['sample_id'].isin(ba18_samples)].copy()
print(f"Found {len(ba18_d18O)} d18O measurements")

# Get chronology (lin_interp_age in years BP)
print("\nMerging chronology...")
ba18_chron = chronology[chronology['sample_id'].isin(ba18_samples)].copy()
print(f"Found {len(ba18_chron)} chronology points")

# Merge all data
print("\nMerging datasets...")
data = ba18_d18O.merge(ba18_chron[['sample_id', 'lin_interp_age']], on='sample_id')

# Convert years BP to CE (assuming present = 1950)
data['year_CE'] = 1950 - data['lin_interp_age']

# Sort by age
data = data.sort_values('year_CE')

# Calculate z-scores
mean_d18O = data['d18O_measurement'].mean()
std_d18O = data['d18O_measurement'].std()
data['z_score'] = (data['d18O_measurement'] - mean_d18O) / std_d18O

print(f"\nBaseline statistics:")
print(f"Mean d18O: {mean_d18O:.3f} permil")
print(f"Std Dev: {std_d18O:.3f} permil")

# Look for 1257 Samalas window (expect peak response ~1273-1280 CE)
print("\n" + "="*70)
print("SEARCHING FOR 1257 SAMALAS VOLCANIC SPIKE")
print("="*70)
print("\nExpected response window: 1257-1285 CE")
print("(Eruption 1257, peak climatic response ~1273-1280)\n")

# Extract 1250-1290 CE window
window = data[(data['year_CE'] >= 1250) & (data['year_CE'] <= 1290)].copy()

if len(window) == 0:
    print("⚠️  NO DATA in 1250-1290 CE window!")
    print("\nChecking full record range...")
    print(f"First date: {data['year_CE'].min():.1f} CE")
    print(f"Last date: {data['year_CE'].max():.1f} CE")
else:
    print(f"Found {len(window)} samples in 1250-1290 CE window:\n")
    print(window[['year_CE', 'd18O_measurement', 'z_score']].to_string(index=False))

    # Find the most negative anomaly in this window
    min_idx = window['z_score'].idxmin()
    peak_anomaly = window.loc[min_idx]

    print("\n" + "="*70)
    print("PEAK ANOMALY IN SAMALAS WINDOW:")
    print("="*70)
    print(f"Year: {peak_anomaly['year_CE']:.1f} CE")
    print(f"d18O: {peak_anomaly['d18O_measurement']:.3f} permil")
    print(f"Z-score: {peak_anomaly['z_score']:.2f}")

    # Compare to 1285 earthquake
    eq_1285_window = data[(data['year_CE'] >= 1280) & (data['year_CE'] <= 1290)]
    if len(eq_1285_window) > 0:
        eq_min_idx = eq_1285_window['z_score'].idxmin()
        eq_peak = eq_1285_window.loc[eq_min_idx]

        print("\n" + "="*70)
        print("COMPARISON: 1285 EARTHQUAKE WINDOW (1280-1290 CE)")
        print("="*70)
        print(f"Peak year: {eq_peak['year_CE']:.1f} CE")
        print(f"d18O: {eq_peak['d18O_measurement']:.3f} permil")
        print(f"Z-score: {eq_peak['z_score']:.2f}")

        # Interpretation
        print("\n" + "="*70)
        print("INTERPRETATION")
        print("="*70)

        if abs(peak_anomaly['year_CE'] - 1276) < 5:
            print("✅ SAMALAS SPIKE DETECTED at expected position (~1273-1280 CE)")
            print("✅ Chronology appears accurate")
        else:
            print(f"⚠️  Peak anomaly at {peak_anomaly['year_CE']:.1f} CE")
            print(f"   Expected: ~1273-1280 CE")
            print(f"   Offset: ~{peak_anomaly['year_CE'] - 1276:.1f} years")
            print("⚠️  Chronology may need adjustment")

        if abs(eq_peak['year_CE'] - peak_anomaly['year_CE']) < 2:
            print("\n⚠️  WARNING: Samalas and 1285 earthquake signals OVERLAP")
            print("   This may be a COMPOUND EVENT (volcanic + seismic)")
        else:
            print(f"\n✅ Samalas ({peak_anomaly['year_CE']:.1f}) and 1285 EQ ({eq_peak['year_CE']:.1f}) are SEPARATE")
            print(f"   Separation: {abs(eq_peak['year_CE'] - peak_anomaly['year_CE']):.1f} years")

# Show top 20 anomalies for reference
print("\n" + "="*70)
print("TOP 20 NEGATIVE ANOMALIES (FULL RECORD)")
print("="*70)
top_20 = data.nsmallest(20, 'z_score')[['year_CE', 'd18O_measurement', 'z_score']]
print(top_20.to_string(index=False))

# Save full dataset
output_file = os.path.join(project_root, "regions/italy/basura_d18O_with_ages.csv")
data[['sample_id', 'year_CE', 'd18O_measurement', 'z_score']].to_csv(output_file, index=False)
print(f"\n✅ Full dataset saved to: {output_file}")
