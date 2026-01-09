#!/usr/bin/env python3
"""
Plot Mg/Ca temporal shapes for 1285 and 1394 events.
Creates publication-quality figures showing shark fin vs hump discrimination.
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
                    row['d18O_measurement'] = float(row['d18O_measurement']) if row.get('d18O_measurement') != 'NA' else None
                    if row['Mg_Ca_measurement'] is not None:
                        data.append(row)
                except (ValueError, KeyError):
                    continue

    return data

def create_ascii_plot(data, event_name, target_depth, search_window=5.0, width=80, height=20):
    """Create ASCII art plot of Mg/Ca vs depth."""
    # Filter data
    samples = [d for d in data if abs(d['depth_sample'] - target_depth) <= search_window]
    samples.sort(key=lambda x: x['depth_sample'])

    if not samples:
        print(f"No data for {event_name}")
        return

    # Get Mg/Ca values
    depths = [s['depth_sample'] for s in samples]
    mgca_values = [s['Mg_Ca_measurement'] for s in samples]

    # Calculate statistics
    all_mgca = [d['Mg_Ca_measurement'] for d in data]
    mean_mgca = sum(all_mgca) / len(all_mgca)
    std_mgca = (sum((x - mean_mgca) ** 2 for x in all_mgca) / len(all_mgca)) ** 0.5

    # Normalize to z-scores
    zscores = [(m - mean_mgca) / std_mgca for m in mgca_values]

    # Create plot grid
    min_z = min(zscores)
    max_z = max(zscores)
    z_range = max_z - min_z

    min_depth = min(depths)
    max_depth = max(depths)
    depth_range = max_depth - min_depth

    print(f"\n{event_name}")
    print("=" * width)
    print(f"Mg/Ca Z-score vs Depth (mm)")
    print(f"Mean Mg/Ca: {mean_mgca:.2f} ± {std_mgca:.2f} mmol/mol")
    print("")

    # Plot grid
    for row in range(height):
        z_val = max_z - (row / (height - 1)) * z_range
        line = f"{z_val:+5.1f}σ |"

        for col in range(width - 8):
            depth_val = min_depth + (col / (width - 9)) * depth_range

            # Find nearest sample
            closest_idx = min(range(len(depths)), key=lambda i: abs(depths[i] - depth_val))
            closest_depth = depths[closest_idx]
            closest_z = zscores[closest_idx]

            if abs(closest_depth - depth_val) < depth_range / (width - 9):
                # This column has a data point
                z_diff = abs(closest_z - z_val)
                if z_diff < z_range / (height - 1):
                    # Mark peak
                    if closest_z == max(zscores):
                        line += "*"
                    else:
                        line += "█"
                else:
                    line += " "
            else:
                line += " "

        print(line)

    # X-axis
    print("      +" + "-" * (width - 8))
    x_labels = f"      {min_depth:.1f}"
    x_labels += " " * (width - 8 - len(f"{min_depth:.1f}") - len(f"{max_depth:.1f}"))
    x_labels += f"{max_depth:.1f}"
    print(x_labels + " mm")

    # Find peak
    peak_idx = zscores.index(max(zscores))
    peak_depth = depths[peak_idx]
    peak_age = 1950 - samples[peak_idx]['interp_age']

    print(f"\nPeak: {max(zscores):+.2f}σ at {peak_depth:.2f} mm ({peak_age:.0f} CE)")

    # Calculate onset rate
    if peak_idx >= 3:
        onset_depths = depths[peak_idx-3:peak_idx+1]
        onset_zscores = zscores[peak_idx-3:peak_idx+1]

        # Simple slope
        n = len(onset_depths)
        mean_d = sum(onset_depths) / n
        mean_z = sum(onset_zscores) / n
        numerator = sum((onset_depths[i] - mean_d) * (onset_zscores[i] - mean_z) for i in range(n))
        denominator = sum((onset_depths[i] - mean_d) ** 2 for i in range(n))

        if denominator > 0:
            slope = numerator / denominator
            print(f"Onset slope: {slope:+.3f} σ per mm")

            if abs(slope) > 0.3:
                print("Shape: SHARK FIN (seismic) ✓")
            else:
                print("Shape: HUMP (climatic) ✗")

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

    # Create plots
    create_ascii_plot(data, "1285 ± 85 yr (TITAN I)", target_depth=32.5, search_window=6.0)
    create_ascii_plot(data, "1394 ± 13 yr (Dark Earthquake)", target_depth=27.67, search_window=6.0)

    # Additional: 1649 climatic event for comparison
    create_ascii_plot(data, "1649 CE (Climatic - Volcanic Recovery)", target_depth=23.0, search_window=6.0)

    return 0

if __name__ == '__main__':
    sys.exit(main())
