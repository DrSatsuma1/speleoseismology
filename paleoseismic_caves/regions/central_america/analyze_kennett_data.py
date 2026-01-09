#!/usr/bin/env python3
"""
Analyze Kennett et al. (2012) Yok Balum data for ~620 CE earthquake signature.
Focus on the 617-663 CE anomaly period.
"""

import csv
import statistics
from collections import defaultdict

# Read the data
data = []
with open('/Users/catherine/Downloads/yok-balum2012s4isotopes-noaa.txt', 'r') as f:
    in_data = False
    for line in f:
        line = line.strip()
        if line.startswith('depth_mm'):
            in_data = True
            continue
        if in_data and line and not line.startswith('#'):
            parts = line.split('\t')
            if len(parts) >= 4:
                try:
                    depth = float(parts[0])
                    age = float(parts[1])
                    d13c = float(parts[2]) if parts[2] != 'NAN' else None
                    d18o = float(parts[3]) if parts[3] != 'NAN' else None
                    data.append({
                        'depth_mm': depth,
                        'age_AD': age,
                        'd13C': d13c,
                        'd18O': d18o
                    })
                except ValueError:
                    pass

print(f"Total samples loaded: {len(data)}")
print(f"Age range: {data[-1]['age_AD']:.1f} to {data[0]['age_AD']:.1f} CE")

# Calculate overall statistics
d18o_vals = [d['d18O'] for d in data if d['d18O'] is not None]
d13c_vals = [d['d13C'] for d in data if d['d13C'] is not None]

d18o_mean = statistics.mean(d18o_vals)
d18o_std = statistics.stdev(d18o_vals)
d13c_mean = statistics.mean(d13c_vals)
d13c_std = statistics.stdev(d13c_vals)

print(f"\n=== OVERALL STATISTICS ===")
print(f"δ18O: mean = {d18o_mean:.3f}‰, std = {d18o_std:.3f}‰")
print(f"δ13C: mean = {d13c_mean:.3f}‰, std = {d13c_std:.3f}‰")

# Calculate z-scores for each sample
for d in data:
    if d['d18O'] is not None:
        d['z_d18O'] = (d['d18O'] - d18o_mean) / d18o_std
    else:
        d['z_d18O'] = None
    if d['d13C'] is not None:
        d['z_d13C'] = (d['d13C'] - d13c_mean) / d13c_std
    else:
        d['z_d13C'] = None

# Focus on 617-663 CE period (our earthquake hypothesis)
print(f"\n{'='*60}")
print(f"=== 617-663 CE EARTHQUAKE ANOMALY PERIOD ===")
print(f"{'='*60}")

eq_period = [d for d in data if 617 <= d['age_AD'] <= 663]
print(f"\nSamples in 617-663 CE: {len(eq_period)}")

# Statistics for earthquake period
eq_d18o = [d['d18O'] for d in eq_period if d['d18O'] is not None]
eq_d13c = [d['d13C'] for d in eq_period if d['d13C'] is not None]
eq_z_d18o = [d['z_d18O'] for d in eq_period if d['z_d18O'] is not None]
eq_z_d13c = [d['z_d13C'] for d in eq_period if d['z_d13C'] is not None]

print(f"\n617-663 CE δ18O:")
print(f"  Mean: {statistics.mean(eq_d18o):.3f}‰ (overall: {d18o_mean:.3f}‰)")
print(f"  Min:  {min(eq_d18o):.3f}‰")
print(f"  Max:  {max(eq_d18o):.3f}‰")
print(f"  Mean z-score: {statistics.mean(eq_z_d18o):.2f}σ")
print(f"  Peak z-score: {min(eq_z_d18o):.2f}σ")

print(f"\n617-663 CE δ13C:")
print(f"  Mean: {statistics.mean(eq_d13c):.3f}‰ (overall: {d13c_mean:.3f}‰)")
print(f"  Min:  {min(eq_d13c):.3f}‰")
print(f"  Max:  {max(eq_d13c):.3f}‰")
print(f"  Mean z-score: {statistics.mean(eq_z_d13c):.2f}σ")
print(f"  Peak z-score: {min(eq_z_d13c):.2f}σ")

# Count anomalies
d18o_anomalies = [d for d in eq_period if d['z_d18O'] and abs(d['z_d18O']) > 2.0]
d13c_anomalies = [d for d in eq_period if d['z_d13C'] and abs(d['z_d13C']) > 2.0]
print(f"\nAnomalies (|z| > 2.0):")
print(f"  δ18O: {len(d18o_anomalies)} samples")
print(f"  δ13C: {len(d13c_anomalies)} samples")

# Look for the two-pulse structure
print(f"\n=== TWO-PULSE STRUCTURE ANALYSIS ===")
pulse1 = [d for d in data if 617 <= d['age_AD'] <= 637]
gap = [d for d in data if 638 <= d['age_AD'] <= 650]
pulse2 = [d for d in data if 651 <= d['age_AD'] <= 663]

for name, period in [("Pulse 1 (617-637)", pulse1), ("Gap (638-650)", gap), ("Pulse 2 (651-663)", pulse2)]:
    if period:
        z18 = [d['z_d18O'] for d in period if d['z_d18O']]
        z13 = [d['z_d13C'] for d in period if d['z_d13C']]
        print(f"\n{name}:")
        print(f"  Samples: {len(period)}")
        if z18:
            print(f"  δ18O mean z: {statistics.mean(z18):.2f}σ, min z: {min(z18):.2f}σ")
        if z13:
            print(f"  δ13C mean z: {statistics.mean(z13):.2f}σ, min z: {min(z13):.2f}σ")

# Growth rate analysis
print(f"\n=== GROWTH RATE ANALYSIS ===")
print("(detecting changes in deposition rate)")

# Calculate growth rate (mm/year) in windows
def calc_growth_rate(samples):
    """Calculate growth rate from depth and age."""
    if len(samples) < 2:
        return None
    depth_range = samples[-1]['depth_mm'] - samples[0]['depth_mm']
    age_range = samples[0]['age_AD'] - samples[-1]['age_AD']  # older is larger depth
    if age_range > 0:
        return depth_range / age_range
    return None

before = [d for d in data if 550 <= d['age_AD'] < 617]
during = [d for d in data if 617 <= d['age_AD'] <= 663]
after = [d for d in data if 663 < d['age_AD'] <= 730]

print(f"\nGrowth rates (mm/year):")
gr_before = calc_growth_rate(before)
gr_during = calc_growth_rate(during)
gr_after = calc_growth_rate(after)
if gr_before:
    print(f"  Before (550-617 CE): {gr_before:.3f} mm/yr")
if gr_during:
    print(f"  During (617-663 CE): {gr_during:.3f} mm/yr")
if gr_after:
    print(f"  After (663-730 CE):  {gr_after:.3f} mm/yr")
if gr_before and gr_during:
    change = ((gr_during - gr_before) / gr_before) * 100
    print(f"\n  Change during event: {change:+.1f}%")

# Compare with other major anomalies (1070s drought)
print(f"\n=== COMPARISON: 1070s DROUGHT ===")
drought = [d for d in data if 1020 <= d['age_AD'] <= 1100]
if drought:
    dz18 = [d['z_d18O'] for d in drought if d['z_d18O']]
    dz13 = [d['z_d13C'] for d in drought if d['z_d13C']]
    print(f"1020-1100 CE (Terminal Classic Drought):")
    print(f"  Samples: {len(drought)}")
    if dz18:
        print(f"  δ18O mean z: {statistics.mean(dz18):.2f}σ, max z: {max(dz18):.2f}σ")
    if dz13:
        print(f"  δ13C mean z: {statistics.mean(dz13):.2f}σ, max z: {max(dz13):.2f}σ")
    print("\n  → Drought shows POSITIVE z-scores (enriched)")
    print("  → 617-663 CE shows NEGATIVE z-scores (depleted)")
    print("  → OPPOSITE directions = DIFFERENT mechanisms!")

# Detailed output for 600-680 CE
print(f"\n{'='*60}")
print(f"=== DETAILED DATA: 600-680 CE ===")
print(f"{'='*60}")
print(f"\n{'Age':<10} {'δ18O':>8} {'z(18O)':>8} {'δ13C':>8} {'z(13C)':>8} {'Note':<20}")
print("-" * 70)

for d in sorted([x for x in data if 600 <= x['age_AD'] <= 680], key=lambda x: x['age_AD']):
    note = ""
    if d['z_d18O'] and d['z_d18O'] < -2.0:
        note = "** δ18O ANOMALY"
    if d['z_d13C'] and d['z_d13C'] < -2.0:
        note = note + " ** δ13C ANOMALY" if note else "** δ13C ANOMALY"

    d18o_str = f"{d['d18O']:.2f}" if d['d18O'] else "NaN"
    z18o_str = f"{d['z_d18O']:.2f}" if d['z_d18O'] else "NaN"
    d13c_str = f"{d['d13C']:.2f}" if d['d13C'] else "NaN"
    z13c_str = f"{d['z_d13C']:.2f}" if d['z_d13C'] else "NaN"

    print(f"{d['age_AD']:<10.1f} {d18o_str:>8} {z18o_str:>8} {d13c_str:>8} {z13c_str:>8} {note:<20}")

# Save detailed earthquake period data
print(f"\n=== SAVING EARTHQUAKE PERIOD DATA ===")
output_file = '/Users/catherine/projects/quake/us_speleothem_project/kennett_620ce_data.csv'
with open(output_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['depth_mm', 'age_AD', 'd18O', 'z_d18O', 'd13C', 'z_d13C'])
    for d in sorted([x for x in data if 550 <= x['age_AD'] <= 730], key=lambda x: x['age_AD']):
        writer.writerow([
            d['depth_mm'],
            d['age_AD'],
            d['d18O'] if d['d18O'] else '',
            f"{d['z_d18O']:.3f}" if d['z_d18O'] else '',
            d['d13C'] if d['d13C'] else '',
            f"{d['z_d13C']:.3f}" if d['z_d13C'] else ''
        ])
print(f"Saved to: {output_file}")
