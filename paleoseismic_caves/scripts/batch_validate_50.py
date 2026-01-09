#!/usr/bin/env python3
"""
GOAL: Get 50+ validations FAST by systematically processing existing data.

Strategy:
1. Take all known caves from ML candidates
2. For each cave, search earthquake catalog (1900-2025) within 100 km
3. For modern earthquakes M>5.0, check if we have cave data covering that period
4. Test for z>2 signal within ±10 years
5. Document ALL tests (positives AND negatives) for statistics
"""

import pandas as pd
import sys

# Known caves from your dataset (from ML CSV)
ml_df = pd.read_csv('paleoseismic_caves/ml/outputs/dark_quake_candidates.csv')

caves = ml_df[['site_name', 'entity_name', 'latitude', 'longitude']].drop_duplicates()

print(f"SYSTEMATIC VALIDATION PIPELINE")
print(f"=" * 80)
print(f"Found {len(caves)} unique cave sites in ML dataset")
print()

# Group by location to avoid duplicates
cave_locations = {}
for idx, row in caves.iterrows():
    key = f"{row['latitude']:.2f},{row['longitude']:.2f}"
    if key not in cave_locations:
        cave_locations[key] = row

print(f"Unique geographic locations: {len(cave_locations)}")
print()

# Generate MCP tool commands for systematic validation
print("="*80)
print("STEP 1: EARTHQUAKE CATALOG SEARCHES")
print("="*80)
print()
print("Run these MCP tool calls to find modern earthquakes near each cave:")
print()

validation_commands = []

for idx, (key, cave) in enumerate(cave_locations.items(), 1):
    lat, lon = cave['latitude'], cave['longitude']
    site_name = cave['site_name']

    print(f"# Cave {idx}: {site_name} ({lat:.3f}, {lon:.3f})")
    print(f"earthquake_search(lat={lat:.3f}, lon={lon:.3f}, radius_km=100, min_magnitude=5.0, start_date='1900-01-01', end_date='2025-01-01')")
    print()

    validation_commands.append({
        'cave': site_name,
        'lat': lat,
        'lon': lon,
        'entity': cave['entity_name']
    })

# Save commands for reference
commands_df = pd.DataFrame(validation_commands)
commands_df.to_csv('paleoseismic_caves/ml/outputs/validation_commands.csv', index=False)

print()
print("="*80)
print(f"Generated {len(validation_commands)} earthquake search commands")
print("Saved to: paleoseismic_caves/ml/outputs/validation_commands.csv")
print()
print("NEXT: Run these searches using MCP tools and document:")
print("  - Total earthquakes found: ___")
print("  - Cave records covering earthquake: ___")
print("  - Signals detected (z>2): ___")
print("  - Non-detections: ___")
print()
print("Detection rate = signals / earthquakes covered")
print("This gives you a robust validation statistic!")
print("="*80)
