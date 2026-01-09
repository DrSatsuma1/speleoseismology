#!/usr/bin/env python3
"""
Find the 1257 Samalas volcanic spike in Bàsura Cave (BA18-4)
using the Hu2022 data file.
"""

import pandas as pd
import numpy as np

# Load Hu2022 BA18-4 data
print("Loading Bàsura Cave (BA18-4) data...")
data_file = "paleoseismic_caves/data/papers/Hu2022-BA18-4.txt"

# Skip header lines (starts at line 154)
data = pd.read_csv(data_file, sep='\t', skiprows=153)

print(f"Loaded {len(data)} samples")

# Convert years BP to CE (present = 1950)
data['year_CE'] = 1950 - data['interp_age']

# Sort by age
data = data.sort_values('year_CE')

# Calculate z-scores for d18O
mean_d18O = data['d18O_measurement'].mean()
std_d18O = data['d18O_measurement'].std()
data['d18O_z'] = (data['d18O_measurement'] - mean_d18O) / std_d18O

# Calculate z-scores for Mg/Ca (where available)
mg_ca_data = data[data['Mg_Ca_measurement'].notna()].copy()
mean_mg = mg_ca_data['Mg_Ca_measurement'].mean()
std_mg = mg_ca_data['Mg_Ca_measurement'].std()
data['Mg_Ca_z'] = (data['Mg_Ca_measurement'] - mean_mg) / std_mg

print(f"\nBaseline statistics:")
print(f"δ18O Mean: {mean_d18O:.3f} permil, Std Dev: {std_d18O:.3f} permil")
print(f"Mg/Ca Mean: {mean_mg:.3f}, Std Dev: {std_mg:.3f}")
print(f"Record range: {data['year_CE'].min():.1f} to {data['year_CE'].max():.1f} CE")

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
    print("\nChecking nearby data...")
    nearby = data[(data['year_CE'] >= 1200) & (data['year_CE'] <= 1300)]
    if len(nearby) > 0:
        print(f"\nFound {len(nearby)} samples in 1200-1300 CE:")
        print(nearby[['year_CE', 'd18O_measurement', 'd18O_z', 'Mg_Ca_measurement', 'Mg_Ca_z']].to_string(index=False))
else:
    print(f"Found {len(window)} samples in 1250-1290 CE window:\n")
    print(window[['year_CE', 'd18O_measurement', 'd18O_z', 'Mg_Ca_measurement', 'Mg_Ca_z']].to_string(index=False))

    # Find the most negative d18O anomaly in this window
    min_idx = window['d18O_z'].idxmin()
    peak_anomaly = window.loc[min_idx]

    print("\n" + "="*70)
    print("PEAK d18O ANOMALY IN SAMALAS WINDOW:")
    print("="*70)
    print(f"Year: {peak_anomaly['year_CE']:.1f} CE")
    print(f"δ18O: {peak_anomaly['d18O_measurement']:.3f} permil (z = {peak_anomaly['d18O_z']:.2f})")
    if pd.notna(peak_anomaly['Mg_Ca_z']):
        print(f"Mg/Ca: {peak_anomaly['Mg_Ca_measurement']:.2f} (z = {peak_anomaly['Mg_Ca_z']:.2f})")
    else:
        print(f"Mg/Ca: NO DATA")

    # Compare to 1285 earthquake window
    eq_1285_window = data[(data['year_CE'] >= 1280) & (data['year_CE'] <= 1290)]
    if len(eq_1285_window) > 0:
        eq_min_idx = eq_1285_window['d18O_z'].idxmin()
        eq_peak = eq_1285_window.loc[eq_min_idx]

        print("\n" + "="*70)
        print("COMPARISON: 1285 EARTHQUAKE WINDOW (1280-1290 CE)")
        print("="*70)
        print(f"Peak year: {eq_peak['year_CE']:.1f} CE")
        print(f"δ18O: {eq_peak['d18O_measurement']:.3f} permil (z = {eq_peak['d18O_z']:.2f})")
        if pd.notna(eq_peak['Mg_Ca_z']):
            print(f"Mg/Ca: {eq_peak['Mg_Ca_measurement']:.2f} (z = {eq_peak['Mg_Ca_z']:.2f})")
        else:
            print(f"Mg/Ca: NO DATA")

        # Interpretation
        print("\n" + "="*70)
        print("CHRONOLOGY VALIDATION")
        print("="*70)

        if abs(peak_anomaly['year_CE'] - 1276) < 5:
            print("✅ SAMALAS SPIKE DETECTED at expected position (~1273-1280 CE)")
            print("✅ Chronology is ACCURATE")
        elif abs(peak_anomaly['year_CE'] - 1257) < 5:
            print("⚠️  Peak at eruption year (1257), not climatic peak (1273-1280)")
            print("   This could indicate immediate response or different mechanism")
        else:
            offset = peak_anomaly['year_CE'] - 1276
            print(f"⚠️  Peak anomaly at {peak_anomaly['year_CE']:.1f} CE")
            print(f"   Expected: ~1273-1280 CE")
            print(f"   Offset: {offset:+.1f} years")
            if abs(offset) > 10:
                print("⚠️  SIGNIFICANT OFFSET - Chronology may need adjustment")
                print(f"   Correction: Subtract {offset:.1f} years from all dates")

        print("\n" + "="*70)
        print("SIGNAL SEPARATION ANALYSIS")
        print("="*70)

        separation = abs(eq_peak['year_CE'] - peak_anomaly['year_CE'])
        if separation < 2:
            print("⚠️  WARNING: Samalas and 1285 earthquake signals OVERLAP")
            print("   Separation: <2 years")
            print("   This may be a COMPOUND EVENT (volcanic + seismic)")
            print("\n   Discrimination requires Mg/Ca trace element analysis:")
            if pd.notna(peak_anomaly['Mg_Ca_z']) and pd.notna(eq_peak['Mg_Ca_z']):
                if peak_anomaly['Mg_Ca_z'] < -1.0:
                    print(f"   - Peak anomaly Mg/Ca: {peak_anomaly['Mg_Ca_z']:.2f} → CLIMATIC (volcanic)")
                elif peak_anomaly['Mg_Ca_z'] > +1.0:
                    print(f"   - Peak anomaly Mg/Ca: {peak_anomaly['Mg_Ca_z']:.2f} → SEISMIC (deep water)")
                else:
                    print(f"   - Peak anomaly Mg/Ca: {peak_anomaly['Mg_Ca_z']:.2f} → AMBIGUOUS")

                if eq_peak['Mg_Ca_z'] > +1.0:
                    print(f"   - 1285 window Mg/Ca: {eq_peak['Mg_Ca_z']:.2f} → SEISMIC (deep water)")
                elif eq_peak['Mg_Ca_z'] < -1.0:
                    print(f"   - 1285 window Mg/Ca: {eq_peak['Mg_Ca_z']:.2f} → CLIMATIC")
                else:
                    print(f"   - 1285 window Mg/Ca: {eq_peak['Mg_Ca_z']:.2f} → AMBIGUOUS")
            else:
                print("   ⚠️  Mg/Ca data MISSING for key samples - cannot discriminate")
        else:
            print(f"✅ Samalas ({peak_anomaly['year_CE']:.1f} CE) and 1285 EQ ({eq_peak['year_CE']:.1f} CE) are SEPARATE")
            print(f"   Separation: {separation:.1f} years")
            print("   Two independent events can be distinguished")

# Show top 20 anomalies for reference
print("\n" + "="*70)
print("TOP 20 NEGATIVE δ18O ANOMALIES (FULL RECORD)")
print("="*70)
top_20 = data.nsmallest(20, 'd18O_z')[['year_CE', 'd18O_measurement', 'd18O_z', 'Mg_Ca_z']]
print(top_20.to_string(index=False))

# Save full dataset
output_file = "paleoseismic_caves/regions/italy/basura_d18O_complete.csv"
data[['depth_sample', 'year_CE', 'd18O_measurement', 'd18O_z', 'Mg_Ca_measurement', 'Mg_Ca_z']].to_csv(output_file, index=False)
print(f"\n✅ Full dataset saved to: {output_file}")
