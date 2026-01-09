#!/usr/bin/env python3
"""
Dos Anas Cave (Cuba) Dual-Isotope Detection Algorithm Test

Dos Anas has δ18O and δ13C with WEAK correlation (r=0.15).
Known event: 1766 Cuba M7.6 (z=-2.74σ expected)

Algorithm for Weak-Correlation Dual-Isotope caves:
- δ18O tracks water source (primary detection)
- δ13C tracks CO2 source independently (use to REJECT volcanic)
- Weak correlation means decoupled signals - use δ13C for discrimination only
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Load data
data_path = Path(__file__).parent.parent / "data" / "multivariate" / "dos_anas_cg_multiproxy.csv"
df = pd.read_csv(data_path)

print("=" * 70)
print("DOS ANAS CAVE DUAL-ISOTOPE DETECTION ALGORITHM VALIDATION")
print("=" * 70)
print(f"\nData range: {df['year_CE'].min():.0f} - {df['year_CE'].max():.0f} CE")
print(f"Total samples: {len(df)}")

# Calculate z-scores
mean_d18o = df['d18O_measurement'].mean()
std_d18o = df['d18O_measurement'].std()
mean_d13c = df['d13C_measurement'].mean()
std_d13c = df['d13C_measurement'].std()

df['d18O_z'] = (df['d18O_measurement'] - mean_d18o) / std_d18o
df['d13C_z'] = (df['d13C_measurement'] - mean_d13c) / std_d13c

# Calculate correlation
corr = df[['d18O_measurement', 'd13C_measurement']].corr().iloc[0,1]

print(f"\nδ18O statistics:")
print(f"  Mean: {mean_d18o:.3f}‰, Std: {std_d18o:.3f}‰")
print(f"  2σ threshold: ±{2*std_d18o:.3f}‰")

print(f"\nδ13C statistics:")
print(f"  Mean: {mean_d13c:.3f}‰, Std: {std_d13c:.3f}‰")
print(f"  2σ threshold: ±{2*std_d13c:.3f}‰")

print(f"\nInter-proxy correlation: r = {corr:.2f} (WEAK - decoupled signals)")

# Detection parameters
D18O_THRESHOLD = 2.0
D13C_COUPLING_THRESHOLD = 1.5

# Classify each sample
def classify_sample(row):
    d18o_z = row['d18O_z'] if pd.notna(row['d18O_z']) else 0
    d13c_z = row['d13C_z'] if pd.notna(row['d13C_z']) else None

    if abs(d18o_z) < D18O_THRESHOLD:
        return None, None

    # δ18O passes threshold
    if d13c_z is not None:
        # With weak correlation (r=0.15), check if responses are COUPLED or DECOUPLED
        same_sign = (d18o_z > 0 and d13c_z > 0) or (d18o_z < 0 and d13c_z < 0)

        if same_sign and abs(d13c_z) >= D13C_COUPLING_THRESHOLD:
            # Coupled response - could be volcanic OR seismic
            return "MEDIUM", "COUPLED"
        elif abs(d13c_z) < 1.0:
            # Decoupled - δ18O anomaly without δ13C response
            # In weak-correlation cave, this is the EXPECTED seismic signature
            return "HIGH", "DECOUPLED_SEISMIC"
        else:
            return "MEDIUM", "PARTIAL_COUPLING"
    else:
        return "LOW", "SINGLE_PROXY"

results = df.apply(classify_sample, axis=1, result_type='expand')
df['confidence'] = results[0]
df['classification'] = results[1]

# Filter to detected events
detected = df[df['confidence'].notna()].copy()
detected = detected.sort_values('year_CE')

print(f"\n{'='*70}")
print("DETECTED EVENTS")
print("="*70)

# Group consecutive samples into events
events = []
current_event = None

for idx, row in detected.iterrows():
    if current_event is None:
        current_event = {
            'start_year': row['year_CE'],
            'end_year': row['year_CE'],
            'peak_d18o_z': row['d18O_z'],
            'peak_d13c_z': row['d13C_z'] if pd.notna(row['d13C_z']) else None,
            'samples': [row],
            'confidence': row['confidence'],
            'classification': row['classification']
        }
    elif row['year_CE'] - current_event['end_year'] <= 20:
        current_event['end_year'] = row['year_CE']
        current_event['samples'].append(row)
        if abs(row['d18O_z']) > abs(current_event['peak_d18o_z']):
            current_event['peak_d18o_z'] = row['d18O_z']
        if pd.notna(row['d13C_z']) and (current_event['peak_d13c_z'] is None or
                                         abs(row['d13C_z']) > abs(current_event['peak_d13c_z'])):
            current_event['peak_d13c_z'] = row['d13C_z']
        # Upgrade confidence if needed
        if row['confidence'] == 'HIGH':
            current_event['confidence'] = 'HIGH'
            current_event['classification'] = row['classification']
    else:
        events.append(current_event)
        current_event = {
            'start_year': row['year_CE'],
            'end_year': row['year_CE'],
            'peak_d18o_z': row['d18O_z'],
            'peak_d13c_z': row['d13C_z'] if pd.notna(row['d13C_z']) else None,
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
conf_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
for e in events:
    conf_counts[e['confidence']] += 1
for c, n in conf_counts.items():
    print(f"  {c}: {n}")

print(f"\n{'='*70}")
print("TOP 15 EVENTS BY Z-SCORE")
print("="*70)
print(f"\n| # | Year (CE) | Duration | Confidence | Classification | δ18O Z | δ13C Z |")
print(f"|---|-----------|----------|------------|----------------|--------|--------|")

for i, e in enumerate(events[:15], 1):
    duration = int(e['end_year'] - e['start_year'])
    dur_str = f"{duration} yr" if duration > 0 else "point"
    year_str = f"{e['start_year']:.0f}-{e['end_year']:.0f}" if duration > 0 else f"{e['start_year']:.0f}"
    d13c_str = f"{e['peak_d13c_z']:+.2f}σ" if e['peak_d13c_z'] is not None else "N/A"
    print(f"| {i} | {year_str} | {dur_str} | {e['confidence']} | {e['classification']} | {e['peak_d18o_z']:+.2f}σ | {d13c_str} |")

# Known event validation
print(f"\n{'='*70}")
print("KNOWN EVENT VALIDATION")
print("="*70)

known_events = [
    {"name": "1766 Cuba M7.6", "window": (1760, 1780), "expected": "DETECT"},
    {"name": "1775 Lisbon M8.5 (remote)", "window": (1770, 1785), "expected": "REJECT (too far)"},
]

print(f"\n| Event | Expected | Detected | δ18O Z | δ13C Z | Status |")
print(f"|-------|----------|----------|--------|--------|--------|")

for ke in known_events:
    matching = [e for e in events if
                not (e['end_year'] < ke['window'][0] or e['start_year'] > ke['window'][1])]

    if matching:
        best = max(matching, key=lambda x: abs(x['peak_d18o_z']))
        detected = "YES"
        d13c_str = f"{best['peak_d13c_z']:+.2f}σ" if best['peak_d13c_z'] else "N/A"
        status = "✅ PASS" if "DETECT" in ke['expected'] else "⚠️ FALSE POSITIVE"
    else:
        detected = "NO"
        best = {"peak_d18o_z": 0, "peak_d13c_z": None}
        d13c_str = "-"
        status = "✅ PASS" if "REJECT" in ke['expected'] else "❌ MISS"

    print(f"| {ke['name'][:30]} | {ke['expected'][:8]} | {detected} | {best['peak_d18o_z']:+.2f}σ | {d13c_str} | {status} |")

# β coefficient estimation
print(f"\n{'='*70}")
print("β COEFFICIENT ESTIMATION")
print("="*70)

high_events = [e for e in events if e['confidence'] == 'HIGH']
if high_events:
    avg_d18o = np.mean([abs(e['peak_d18o_z']) for e in high_events])
    print(f"\n  HIGH confidence events: {len(high_events)}")
    print(f"  Average |δ18O_z| at HIGH confidence: {avg_d18o:.2f}σ")

print(f"""
  Estimated β₁(δ18O): **HIGH** (primary detection proxy)
  Estimated β₂(δ13C): **LOW** (discrimination only, not detection)
  Inter-proxy correlation: r = {corr:.2f} (WEAK)
  Noise (δ18O): σ = {std_d18o:.3f}‰
  Noise (δ13C): σ = {std_d13c:.3f}‰

  **Key insight**: Weak correlation means δ18O and δ13C are INDEPENDENT.
  - For seismic events: Expect δ18O anomaly WITHOUT corresponding δ13C change
  - For volcanic events: Expect COUPLED δ18O-δ13C response
  - Use δ13C to REJECT volcanic false positives, not to detect seismic
""")

print(f"\n{'='*70}")
print("CONCLUSIONS")
print("="*70)
print(f"""
**Algorithm validation**: Tested on Dos Anas dual-isotope data

**Detection statistics**:
- Time span: {df['year_CE'].max() - df['year_CE'].min():.0f} years
- Events detected: {len(events)}
- HIGH confidence: {conf_counts['HIGH']}
- MEDIUM confidence: {conf_counts['MEDIUM']}
- LOW confidence: {conf_counts['LOW']}

**β coefficients for Dos Anas**:
- β₁(δ18O) = HIGH (primary detection)
- β₂(δ13C) = LOW (discrimination only)
- Correlation: r = {corr:.2f} (weak = independent signals)

**Discrimination strategy for weak-correlation caves**:
- Seismic = δ18O anomaly WITH LOW δ13C (water disruption without CO2 change)
- Volcanic = COUPLED δ18O + δ13C response (both affected by climate/sulfate)
""")
