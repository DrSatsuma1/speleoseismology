#!/usr/bin/env python3
"""
Analyze Oregon Caves for 1600s anomalies - potential Cascadia pre-1700 signals
"""

import pandas as pd
import numpy as np

# Load Oregon Caves data
data = pd.read_csv("/Users/catherine/projects/quake/us_speleothem_project/california_oregon_caves_ocnm02-1.csv")

print("="*60)
print("OREGON CAVES ANALYSIS (Entity 294)")
print("="*60)

# Focus on δ18O
d18O = data[['year_CE', 'd18O_measurement', 'd13C_measurement']].dropna()
print(f"\nTotal samples with δ18O: {len(d18O)}")
print(f"Time range: {d18O['year_CE'].min():.0f} to {d18O['year_CE'].max():.0f} CE")

# Calculate Z-scores
mean = d18O['d18O_measurement'].mean()
std = d18O['d18O_measurement'].std()
print(f"\nδ18O statistics: mean = {mean:.3f}‰, std = {std:.3f}‰")

d18O['z_score'] = (d18O['d18O_measurement'] - mean) / std

# 1600s analysis (most recent ~90 years of record)
print("\n" + "="*60)
print("1600-1690 CE ANOMALIES (Final 90 years of record)")
print("="*60)

recent = d18O[(d18O['year_CE'] >= 1600) & (d18O['year_CE'] <= 1690)]
print(f"Samples in 1600-1690: {len(recent)}")

# Find anomalies
anomalies_1600s = recent[abs(recent['z_score']) > 1.5].sort_values('z_score')
print(f"\nAnomalies (|z| > 1.5): {len(anomalies_1600s)}")

if len(anomalies_1600s) > 0:
    print("\n" + "-"*60)
    print(f"{'Year CE':>10} {'δ18O (‰)':>10} {'δ13C (‰)':>10} {'Z-score':>10}")
    print("-"*60)
    for _, row in anomalies_1600s.iterrows():
        print(f"{row['year_CE']:>10.1f} {row['d18O_measurement']:>10.3f} {row['d13C_measurement']:>10.3f} {row['z_score']:>10.2f}")

# Check for 1687 specifically (closest to 1700 Cascadia)
print("\n" + "="*60)
print("DATA NEAREST TO 1700 CASCADIA M9.0")
print("="*60)

closest_to_1700 = d18O[d18O['year_CE'] >= 1680].sort_values('year_CE', ascending=False).head(10)
print(f"\n{'Year CE':>10} {'δ18O (‰)':>10} {'δ13C (‰)':>10} {'Z-score':>10}")
print("-"*60)
for _, row in closest_to_1700.iterrows():
    flag = "*" if abs(row['z_score']) > 1.5 else ""
    print(f"{row['year_CE']:>10.1f} {row['d18O_measurement']:>10.3f} {row['d13C_measurement']:>10.3f} {row['z_score']:>10.2f} {flag}")

# Historical anomaly clusters
print("\n" + "="*60)
print("LAST 2000 YEARS - TOP 20 ANOMALIES")
print("="*60)

last_2k = d18O[d18O['year_CE'] >= 0].copy()
last_2k_sorted = last_2k.sort_values('z_score')

print("\n** STRONGEST NEGATIVE (More negative δ18O = wetter/cooler?) **")
print(f"{'Year CE':>10} {'δ18O (‰)':>10} {'Z-score':>10}")
print("-"*40)
for _, row in last_2k_sorted.head(10).iterrows():
    print(f"{row['year_CE']:>10.1f} {row['d18O_measurement']:>10.3f} {row['z_score']:>10.2f}")

print("\n** STRONGEST POSITIVE (More positive δ18O = drier/warmer?) **")
print(f"{'Year CE':>10} {'δ18O (‰)':>10} {'Z-score':>10}")
print("-"*40)
for _, row in last_2k_sorted.tail(10).iterrows():
    print(f"{row['year_CE']:>10.1f} {row['d18O_measurement']:>10.3f} {row['z_score']:>10.2f}")

# Known Cascadia events check
print("\n" + "="*60)
print("CASCADIA MEGATHRUST EVENT WINDOWS")
print("="*60)

cascadia_windows = [
    ("Event Y (1700 CE)", 1700, 1700),  # Just after record ends
    ("Event W (~1100 CE)", 1030, 1160),
    ("Event S (~800 CE)", 700, 900),
    ("T5 (~400 CE)", 300, 500),
]

for name, start, end in cascadia_windows:
    window_data = d18O[(d18O['year_CE'] >= start) & (d18O['year_CE'] <= end)]
    if len(window_data) == 0:
        if start > d18O['year_CE'].max():
            print(f"\n{name}: RECORD ENDS BEFORE THIS EVENT")
        else:
            print(f"\n{name}: No data in window")
        continue

    anomalies = window_data[abs(window_data['z_score']) > 1.5]
    max_z = window_data['z_score'].max()
    min_z = window_data['z_score'].min()

    print(f"\n{name}")
    print(f"  Window: {start}-{end} CE")
    print(f"  Samples: {len(window_data)}")
    print(f"  Anomalies (|z|>1.5): {len(anomalies)}")
    print(f"  Z-score range: {min_z:.2f} to {max_z:.2f}")

    if len(anomalies) > 0:
        print("  Anomaly years:", [f"{y:.0f}" for y in anomalies['year_CE'].values])

print("\n" + "="*60)
print("CONCLUSION")
print("="*60)
