#!/usr/bin/env python3
"""
Analyze Mg/Ca temporal shape for 1285 and 1394 Italy events.
Tests "shark fin" vs "hump" discrimination for seismic vs climatic signals.
"""

import csv
import sys
from pathlib import Path

def load_basura_data(file_path):
    """Load Bàsura trace element data."""
    data = []
    with open(file_path, 'r') as f:
        # Find data start
        for line in f:
            if line.startswith('depth_sample'):
                header = line.strip().split('\t')
                break

        # Read data
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            values = line.strip().split('\t')
            if len(values) == len(header):
                row = dict(zip(header, values))
                try:
                    row['depth_sample'] = float(row['depth_sample'])
                    row['interp_age'] = float(row['interp_age'])
                    row['Mg_Ca_measurement'] = float(row['Mg_Ca_measurement']) if row['Mg_Ca_measurement'] != 'NA' else None
                    if row['Mg_Ca_measurement'] is not None:
                        data.append(row)
                except (ValueError, KeyError):
                    continue

    return data

def calculate_zscore(value, mean, std):
    """Calculate z-score."""
    return (value - mean) / std

def calculate_rate_of_change(data, index, window=2):
    """Calculate rate of change (dMg/dt) around a point."""
    if index < window:
        return None

    # Calculate slope over window samples before peak
    depths = [data[i]['depth_sample'] for i in range(index-window, index+1)]
    mgca_values = [data[i]['Mg_Ca_measurement'] for i in range(index-window, index+1)]

    # Simple linear regression
    n = len(depths)
    mean_depth = sum(depths) / n
    mean_mgca = sum(mgca_values) / n

    numerator = sum((depths[i] - mean_depth) * (mgca_values[i] - mean_mgca) for i in range(n))
    denominator = sum((depths[i] - mean_depth) ** 2 for i in range(n))

    if denominator == 0:
        return None

    slope = numerator / denominator  # mmol/mol per mm
    return slope

def classify_shape(onset_rate, recovery_rate, threshold=1.0):
    """
    Classify temporal shape as "shark fin" or "hump".

    Shark fin: Rapid onset (high rate), slower recovery
    Hump: Gradual onset and recovery (both slow)
    """
    if abs(onset_rate) > threshold:
        return "SHARK FIN (seismic)"
    else:
        return "HUMP (climatic)"

def analyze_event(data, event_name, target_depth, search_window=2.0):
    """Analyze Mg/Ca shape around a specific event."""
    print(f"\n{'='*60}")
    print(f"Event: {event_name}")
    print(f"{'='*60}")

    # Calculate statistics
    mgca_values = [d['Mg_Ca_measurement'] for d in data]
    mean_mgca = sum(mgca_values) / len(mgca_values)
    std_mgca = (sum((x - mean_mgca) ** 2 for x in mgca_values) / len(mgca_values)) ** 0.5

    # Find samples around target depth
    samples = []
    for i, d in enumerate(data):
        if abs(d['depth_sample'] - target_depth) <= search_window:
            zscore = calculate_zscore(d['Mg_Ca_measurement'], mean_mgca, std_mgca)
            samples.append({
                'index': i,
                'depth': d['depth_sample'],
                'age': d['interp_age'],
                'mgca': d['Mg_Ca_measurement'],
                'zscore': zscore
            })

    if not samples:
        print(f"No samples found near depth {target_depth} mm")
        return

    # Sort by depth
    samples.sort(key=lambda x: x['depth'])

    # Find peak
    peak_sample = max(samples, key=lambda x: x['mgca'])
    peak_index = peak_sample['index']

    print(f"\nTarget depth: {target_depth} mm")
    print(f"Peak found at depth: {peak_sample['depth']} mm (index {peak_index})")
    print(f"Peak age: {peak_sample['age']:.1f} cal BP ({1950 - peak_sample['age']:.0f} CE)")
    print(f"Peak Mg/Ca: {peak_sample['mgca']:.4f} mmol/mol")
    print(f"Peak z-score: {peak_sample['zscore']:+.2f}σ")

    # Calculate rate of change at onset
    onset_rate = calculate_rate_of_change(data, peak_index, window=3)

    if onset_rate is not None:
        print(f"\nOnset rate (dMg/dt): {onset_rate:+.4f} mmol/mol per mm")

    # Show surrounding samples
    print(f"\nSurrounding samples (±{search_window} mm):")
    print(f"{'Depth (mm)':<12} {'Age (BP)':<12} {'Age (CE)':<10} {'Mg/Ca':<12} {'Z-score':<10}")
    print("-" * 60)
    for s in samples:
        age_ce = 1950 - s['age']
        print(f"{s['depth']:<12.2f} {s['age']:<12.1f} {age_ce:<10.0f} {s['mgca']:<12.4f} {s['zscore']:+8.2f}σ")

    # Classify shape
    if onset_rate is not None:
        shape = classify_shape(onset_rate, None, threshold=0.5)
        print(f"\nShape classification: {shape}")

        if "SHARK FIN" in shape:
            print("✓ Consistent with seismic signal (rapid onset)")
        else:
            print("✗ Suggests climatic signal (gradual onset)")

    return peak_sample

def main():
    # File path
    data_dir = Path(__file__).parent.parent / 'data' / 'papers'
    file_path = data_dir / 'Hu2022-BA18-4.txt'

    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return 1

    print("Loading Bàsura Cave trace element data...")
    data = load_basura_data(file_path)

    print(f"Loaded {len(data)} samples with Mg/Ca measurements")
    print(f"Depth range: {data[0]['depth_sample']:.2f} - {data[-1]['depth_sample']:.2f} mm")
    print(f"Age range: {data[-1]['interp_age']:.1f} - {data[0]['interp_age']:.1f} cal BP")

    # Analyze 1285 event (depth ~32.5 mm)
    analyze_event(data, "1285 ± 85 yr (TITAN I)", target_depth=32.5, search_window=3.0)

    # Analyze 1394 event (depth ~27.67 mm)
    analyze_event(data, "1394 ± 13 yr (Dark Earthquake)", target_depth=27.67, search_window=3.0)

    print("\n" + "="*60)
    print("Analysis complete")
    print("="*60)

    return 0

if __name__ == '__main__':
    sys.exit(main())
