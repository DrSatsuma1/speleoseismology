#!/usr/bin/env python3
"""
Analyze Central American caves for 617-663 CE anomalies matching Yok Balum.
Focus on caves near the Motagua fault.
"""

import csv
import statistics
from collections import defaultdict

# Target entities with 617-663 CE coverage (excluding Yok Balum 209)
TARGET_ENTITIES = {
    109: "Cueva del Diablo (Mexico)",
    147: "Tzabnah cave (Yucatan)",
    167: "Chilibrillo cave (Panama)",
    178: "Macal Chasm (Belize)",
    286: "Juxtlahuaca cave (Mexico)",
    684: "Palco cave (Puerto Rico)",
    841: "Rey Marcos (Guatemala)"
}

# Load sample IDs for each entity
entity_samples = defaultdict(list)
with open('sample.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        eid = int(row['entity_id']) if row['entity_id'].isdigit() else 0
        if eid in TARGET_ENTITIES:
            entity_samples[eid].append(row['sample_id'])

print("Samples per entity:")
for eid, samples in entity_samples.items():
    print(f"  Entity {eid} ({TARGET_ENTITIES[eid]}): {len(samples)} samples")

# Load chronology (sample_id -> age BP)
sample_ages = {}
with open('sisal_chronology.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['lin_interp_age'] and row['lin_interp_age'] != 'NA':
            try:
                sample_ages[row['sample_id']] = float(row['lin_interp_age'])
            except:
                pass

# Load d18O data
sample_d18o = {}
with open('d18O.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['d18O_measurement'] and row['d18O_measurement'] != 'NA':
            try:
                sample_d18o[row['sample_id']] = float(row['d18O_measurement'])
            except:
                pass

# Load d13C data
sample_d13c = {}
with open('d13C.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['d13C_measurement'] and row['d13C_measurement'] != 'NA':
            try:
                sample_d13c[row['sample_id']] = float(row['d13C_measurement'])
            except:
                pass

print("\n" + "="*80)
print("ANALYSIS: 617-663 CE ANOMALIES IN REGIONAL CAVES")
print("="*80)

# Analyze each entity
results = []
for eid, name in TARGET_ENTITIES.items():
    print(f"\n{'='*60}")
    print(f"Entity {eid}: {name}")
    print("="*60)

    # Build time series
    timeseries = []
    for sid in entity_samples[eid]:
        if sid in sample_ages and sid in sample_d18o:
            age_bp = sample_ages[sid]
            year_ce = 1950 - age_bp
            d18o = sample_d18o[sid]
            d13c = sample_d13c.get(sid)
            timeseries.append({
                'sample_id': sid,
                'year_ce': year_ce,
                'age_bp': age_bp,
                'd18O': d18o,
                'd13C': d13c
            })

    if not timeseries:
        print("  No data with chronology")
        continue

    # Sort by age
    timeseries.sort(key=lambda x: x['year_ce'])

    # Calculate overall statistics
    d18o_vals = [t['d18O'] for t in timeseries if t['d18O'] is not None]
    d13c_vals = [t['d13C'] for t in timeseries if t['d13C'] is not None]

    if len(d18o_vals) < 10:
        print(f"  Insufficient data: {len(d18o_vals)} δ18O values")
        continue

    d18o_mean = statistics.mean(d18o_vals)
    d18o_std = statistics.stdev(d18o_vals)

    print(f"  Total samples: {len(timeseries)}")
    print(f"  Time range: {timeseries[0]['year_ce']:.0f} to {timeseries[-1]['year_ce']:.0f} CE")
    print(f"  δ18O mean: {d18o_mean:.3f}‰, std: {d18o_std:.3f}‰")

    # Check 617-663 CE period
    eq_period = [t for t in timeseries if 550 <= t['year_ce'] <= 730]
    eq_samples = [t for t in timeseries if 617 <= t['year_ce'] <= 663]

    print(f"\n  550-730 CE (context): {len(eq_period)} samples")
    print(f"  617-663 CE (earthquake period): {len(eq_samples)} samples")

    if eq_samples:
        # Calculate z-scores
        eq_d18o = [t['d18O'] for t in eq_samples if t['d18O'] is not None]
        eq_z_scores = [(v - d18o_mean) / d18o_std for v in eq_d18o]

        mean_z = statistics.mean(eq_z_scores)
        min_z = min(eq_z_scores)
        max_z = max(eq_z_scores)

        print(f"\n  617-663 CE δ18O z-scores:")
        print(f"    Mean: {mean_z:.2f}σ")
        print(f"    Min:  {min_z:.2f}σ (most negative)")
        print(f"    Max:  {max_z:.2f}σ (most positive)")

        # Count anomalies
        neg_anomalies = sum(1 for z in eq_z_scores if z < -1.5)
        pos_anomalies = sum(1 for z in eq_z_scores if z > 1.5)

        print(f"\n  Anomalies (|z| > 1.5):")
        print(f"    Negative: {neg_anomalies}")
        print(f"    Positive: {pos_anomalies}")

        # Check if matches Yok Balum pattern (negative anomalies)
        if mean_z < -1.0 or neg_anomalies >= 2:
            print(f"\n  *** POTENTIAL MATCH: Shows negative anomalies like Yok Balum ***")
            results.append((name, eid, mean_z, min_z, len(eq_samples), "MATCH"))
        elif mean_z > 1.0 or pos_anomalies >= 2:
            print(f"\n  Shows OPPOSITE pattern (positive anomalies)")
            results.append((name, eid, mean_z, max_z, len(eq_samples), "OPPOSITE"))
        else:
            print(f"\n  No significant anomaly detected")
            results.append((name, eid, mean_z, min_z, len(eq_samples), "NEUTRAL"))

        # Show detailed data
        print(f"\n  Detailed 617-663 CE data:")
        for t in eq_samples[:10]:  # Show first 10
            z = (t['d18O'] - d18o_mean) / d18o_std
            marker = "**" if abs(z) > 1.5 else ""
            print(f"    {t['year_ce']:.1f} CE: δ18O = {t['d18O']:.2f}‰ (z = {z:.2f}) {marker}")
        if len(eq_samples) > 10:
            print(f"    ... and {len(eq_samples) - 10} more samples")

# Summary
print("\n" + "="*80)
print("SUMMARY: REGIONAL CAVE COMPARISON")
print("="*80)
print(f"\n{'Cave':<35} {'Entity':<8} {'Mean Z':<10} {'Peak Z':<10} {'Samples':<10} {'Pattern'}")
print("-" * 90)
for name, eid, mean_z, peak_z, n_samples, pattern in results:
    print(f"{name:<35} {eid:<8} {mean_z:<10.2f} {peak_z:<10.2f} {n_samples:<10} {pattern}")

# Compare with Yok Balum
print("\n" + "="*80)
print("YOK BALUM REFERENCE (from Kennett data analysis):")
print("  617-663 CE: Mean z = -1.88σ, Peak z = -3.63σ")
print("  Pattern: Strong NEGATIVE anomalies (depleted δ18O)")
print("="*80)
