#!/usr/bin/env python3
"""
Crystal Cave Single-Proxy Detection Algorithm Test

Crystal Cave has δ18O only - requires external validation.
Known events to validate:
- 1896 Independence M6.3 (48 km, z=-3.54σ expected)
- 1741 Kern Canyon pre-Spanish event

Algorithm for Single-Proxy caves:
- IF (|δ18O_z| > 3): CONFIDENCE = HIGH (strong signal)
- ELIF (|δ18O_z| > 2): CONFIDENCE = MEDIUM
- Single-proxy requires external validation (paleoseismic, historical)
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Load data
data_path = Path(__file__).parent.parent / "data" / "multivariate" / "crystal_cave_multiproxy.csv"
df = pd.read_csv(data_path)

print("=" * 70)
print("CRYSTAL CAVE SINGLE-PROXY DETECTION ALGORITHM VALIDATION")
print("=" * 70)
print(f"\nData range: {df['year_CE'].min():.0f} - {df['year_CE'].max():.0f} CE")
print(f"Total samples: {len(df)}")

# Calculate z-scores
mean_d18o = df['d18O_measurement'].mean()
std_d18o = df['d18O_measurement'].std()

df['d18O_z'] = (df['d18O_measurement'] - mean_d18o) / std_d18o

print(f"\nδ18O statistics:")
print(f"  Mean: {mean_d18o:.3f}‰")
print(f"  Std: {std_d18o:.3f}‰")
print(f"  2σ threshold: ±{2*std_d18o:.3f}‰")
print(f"  3σ threshold: ±{3*std_d18o:.3f}‰")

# Detection parameters
D18O_HIGH_THRESHOLD = 3.0
D18O_MEDIUM_THRESHOLD = 2.0

# Classify each sample
def classify_sample(row):
    d18o_z = abs(row['d18O_z']) if pd.notna(row['d18O_z']) else 0

    if d18o_z >= D18O_HIGH_THRESHOLD:
        return "HIGH", "SINGLE_PROXY"
    elif d18o_z >= D18O_MEDIUM_THRESHOLD:
        return "MEDIUM", "SINGLE_PROXY"
    else:
        return None, None

results = df.apply(classify_sample, axis=1, result_type='expand')
df['confidence'] = results[0]
df['classification'] = results[1]

# Filter to detected events
detected = df[df['confidence'].notna()].copy()
detected = detected.sort_values('year_CE')

print(f"\n{'='*70}")
print("DETECTED EVENTS")
print("="*70)

# Group consecutive samples into events (within 15 years)
events = []
current_event = None

for idx, row in detected.iterrows():
    if current_event is None:
        current_event = {
            'start_year': row['year_CE'],
            'end_year': row['year_CE'],
            'peak_d18o_z': row['d18O_z'],
            'peak_d18o_raw': row['d18O_measurement'],
            'samples': [row],
            'confidence': row['confidence'],
            'classification': row['classification']
        }
    elif row['year_CE'] - current_event['end_year'] <= 15:
        current_event['end_year'] = row['year_CE']
        current_event['samples'].append(row)
        if abs(row['d18O_z']) > abs(current_event['peak_d18o_z']):
            current_event['peak_d18o_z'] = row['d18O_z']
            current_event['peak_d18o_raw'] = row['d18O_measurement']
        if row['confidence'] == 'HIGH':
            current_event['confidence'] = 'HIGH'
    else:
        events.append(current_event)
        current_event = {
            'start_year': row['year_CE'],
            'end_year': row['year_CE'],
            'peak_d18o_z': row['d18O_z'],
            'peak_d18o_raw': row['d18O_measurement'],
            'samples': [row],
            'confidence': row['confidence'],
            'classification': row['classification']
        }

if current_event:
    events.append(current_event)

# Sort by absolute z-score
events.sort(key=lambda x: abs(x['peak_d18o_z']), reverse=True)

print(f"\nTotal events detected: {len(events)}")
print(f"\nConfidence distribution:")
conf_counts = {'HIGH': 0, 'MEDIUM': 0}
for e in events:
    conf_counts[e['confidence']] += 1
for c, n in conf_counts.items():
    print(f"  {c}: {n}")

print(f"\n{'='*70}")
print("TOP 20 EVENTS BY Z-SCORE")
print("="*70)
print(f"\n| # | Year (CE) | Duration | Confidence | δ18O Z | δ18O Raw |")
print(f"|---|-----------|----------|------------|--------|----------|")

for i, e in enumerate(events[:20], 1):
    duration = int(e['end_year'] - e['start_year'])
    dur_str = f"{duration} yr" if duration > 0 else "point"
    year_str = f"{e['start_year']:.0f}-{e['end_year']:.0f}" if duration > 0 else f"{e['start_year']:.0f}"
    print(f"| {i} | {year_str} | {dur_str} | {e['confidence']} | {e['peak_d18o_z']:+.2f}σ | {e['peak_d18o_raw']:.2f}‰ |")

# Known event validation
print(f"\n{'='*70}")
print("KNOWN EVENT VALIDATION")
print("="*70)

known_events = [
    {"name": "1896 Independence M6.3 (48 km)", "window": (1890, 1905), "expected": "DETECT"},
    {"name": "1741 Kern Canyon pre-Spanish", "window": (1730, 1755), "expected": "DETECT"},
    {"name": "1952 Kern County M7.3 (178 km)", "window": (1948, 1960), "expected": "REJECT (too far)"},
]

print(f"\n| Event | Expected | Detected | δ18O Z | Year | Status |")
print(f"|-------|----------|----------|--------|------|--------|")

for ke in known_events:
    # Find events in window
    matching = [e for e in events if
                not (e['end_year'] < ke['window'][0] or e['start_year'] > ke['window'][1])]

    if matching:
        best = max(matching, key=lambda x: abs(x['peak_d18o_z']))
        year_str = f"{best['start_year']:.0f}"
        detected = "YES"
        status = "✅ PASS" if "DETECT" in ke['expected'] else "⚠️ FALSE POSITIVE"
    else:
        year_str = "-"
        detected = "NO"
        best = {"peak_d18o_z": 0}
        status = "✅ PASS" if "REJECT" in ke['expected'] else "❌ MISS"

    print(f"| {ke['name'][:35]} | {ke['expected'][:8]} | {detected} | {best['peak_d18o_z']:+.2f}σ | {year_str} | {status} |")

# Look specifically at 1896 and 1741 windows
print(f"\n{'='*70}")
print("DETAILED ANALYSIS: KEY TIME WINDOWS")
print("="*70)

for window_name, (start, end) in [("1896 Independence", (1890, 1905)), ("1741 Kern Canyon", (1730, 1755))]:
    window_data = df[(df['year_CE'] >= start) & (df['year_CE'] <= end)].copy()
    if len(window_data) > 0:
        min_idx = window_data['d18O_z'].idxmin()
        max_idx = window_data['d18O_z'].idxmax()
        print(f"\n### {window_name} ({start}-{end} CE)")
        print(f"- Samples in window: {len(window_data)}")
        print(f"- Min δ18O z-score: {window_data.loc[min_idx, 'd18O_z']:.2f}σ at {window_data.loc[min_idx, 'year_CE']:.1f} CE")
        print(f"- Max δ18O z-score: {window_data.loc[max_idx, 'd18O_z']:.2f}σ at {window_data.loc[max_idx, 'year_CE']:.1f} CE")
        print(f"- Detection: {'YES' if abs(window_data['d18O_z']).max() >= 2 else 'NO'}")

# β coefficient estimation
print(f"\n{'='*70}")
print("β COEFFICIENT ESTIMATION")
print("="*70)

high_events = [e for e in events if e['confidence'] == 'HIGH']
if high_events:
    avg_d18o = np.mean([abs(e['peak_d18o_z']) for e in high_events])
    print(f"\n  HIGH confidence events: {len(high_events)}")
    print(f"  Average |δ18O_z| at HIGH confidence: {avg_d18o:.2f}σ")
    print(f"\n  Estimated β₁(δ18O): **HIGH** (primary and ONLY detection proxy)")
    print(f"  Noise: σ = {std_d18o:.3f}‰ (LOW - good sensitivity)")
    print(f"\n  ⚠️ WARNING: Single-proxy cave requires external validation")
    print(f"  - Must cross-reference with paleoseismic trenching")
    print(f"  - Must check historical earthquake catalogs")
    print(f"  - Cannot discriminate seismic from climatic without Mg/Ca or δ13C")

print(f"\n{'='*70}")
print("CONCLUSIONS")
print("="*70)
print(f"""
**Algorithm validation**: Tested on Crystal Cave single-proxy data

**Detection statistics**:
- Time span: {df['year_CE'].max() - df['year_CE'].min():.0f} years
- Events detected: {len(events)}
- HIGH confidence (|z|>3): {conf_counts['HIGH']}
- MEDIUM confidence (|z|>2): {conf_counts['MEDIUM']}

**β coefficients for Crystal Cave**:
- β₁(δ18O) = HIGH (only proxy available)
- Noise: σ = {std_d18o:.3f}‰
- Detection threshold 2σ: ±{2*std_d18o:.3f}‰

**Critical limitation**: Single-proxy detection CANNOT discriminate:
- Seismic events from climate anomalies
- Local hydrological changes from regional forcing
- Must rely on EXTERNAL validation (paleoseismic, historical records)
""")
