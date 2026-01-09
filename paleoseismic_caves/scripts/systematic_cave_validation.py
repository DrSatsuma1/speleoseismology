#!/usr/bin/env python3
"""
Systematic validation: Test ALL caves in SISAL for modern earthquake detection.

Goal: Build database of which caves WORK vs FAIL to identify geological factors.

Known results:
- Crystal Cave (CRC-3): 9/9 detections (100%) ✓✓✓
- Yok Balum (YOKI): 0/6 detections (0%) ✗

Testing all other caves with:
1. Coverage extending into modern era (1900+)
2. Known earthquakes within 100 km
"""

import pandas as pd
import numpy as np
import os

# Set up paths
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
sisal_path = os.path.join(project_dir, 'data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv')

# Load SISAL data
print("Loading SISAL database...")
entity = pd.read_csv(os.path.join(sisal_path, 'entity.csv'))
site = pd.read_csv(os.path.join(sisal_path, 'site.csv'))
sample = pd.read_csv(os.path.join(sisal_path, 'sample.csv'))
chronology = pd.read_csv(os.path.join(sisal_path, 'sisal_chronology.csv'))
d18o = pd.read_csv(os.path.join(sisal_path, 'd18O.csv'))

print(f"Found {len(entity)} entities in SISAL\n")

# Target caves from validation matrix
target_caves = {
    'YOKI': {'name': 'Yok Balum', 'country': 'Belize/Guatemala', 'tested': True, 'result': '0/6 (0%)'},
    'CRC-3': {'name': 'Crystal Cave', 'country': 'USA', 'tested': True, 'result': '9/9 (100%)'},
    'SQ1': {'name': 'Shenqi Cave', 'country': 'China', 'tested': False},
    'Ko-1': {'name': 'Kocain Cave', 'country': 'Turkey', 'tested': False},
    'LG3': {'name': 'Lapa Grande', 'country': 'Brazil', 'tested': False},
    'ORE1': {'name': 'Oregon Caves', 'country': 'USA', 'tested': False},
}

# Get data coverage for all entities with δ18O data
print("="*100)
print("Scanning all SISAL caves for modern coverage (1900-2025 CE)...")
print("="*100 + "\n")

modern_caves = []

for idx, entity_row in entity.iterrows():
    entity_id = entity_row['entity_id']
    entity_name = entity_row['entity_name']
    site_id = entity_row['site_id']

    # Get site info
    site_row = site[site['site_id'] == site_id]
    if len(site_row) == 0:
        continue

    site_name = site_row.iloc[0]['site_name']

    # Get samples for this entity
    entity_samples = sample[sample['entity_id'] == entity_id][['sample_id']]
    if len(entity_samples) == 0:
        continue

    # Check if has δ18O data
    entity_d18o = d18o[d18o['sample_id'].isin(entity_samples['sample_id'])]
    if len(entity_d18o) == 0:
        continue

    # Get age range
    entity_samples_ages = entity_samples.merge(
        chronology[['sample_id', 'lin_interp_age']],
        on='sample_id',
        how='left'
    )
    entity_samples_ages = entity_samples_ages.dropna(subset=['lin_interp_age'])

    if len(entity_samples_ages) == 0:
        continue

    # Convert to CE
    min_age = entity_samples_ages['lin_interp_age'].min()
    max_age = entity_samples_ages['lin_interp_age'].max()
    min_year = 1950 - max_age  # max age = earliest year
    max_year = 1950 - min_age  # min age = latest year

    # Check if extends into modern era (1900+)
    if max_year >= 1900:
        modern_caves.append({
            'entity_id': entity_id,
            'entity_name': entity_name,
            'site_name': site_name,
            'min_year': min_year,
            'max_year': max_year,
            'n_d18o': len(entity_d18o),
            'tested': entity_name in target_caves and target_caves[entity_name].get('tested', False),
            'result': target_caves.get(entity_name, {}).get('result', 'Not tested')
        })

# Sort by max year
modern_caves = sorted(modern_caves, key=lambda x: x['max_year'], reverse=True)

print(f"Found {len(modern_caves)} caves with data extending to 1900 CE or later:\n")
print(f"{'Entity':<10} {'Site Name':<30} {'Coverage':<25} {'δ18O':<8} {'Status':<20}")
print("="*100)

for cave in modern_caves:
    coverage = f"{cave['min_year']:.0f} - {cave['max_year']:.0f} CE"
    status = f"✓ {cave['result']}" if cave['tested'] else "⬜ Not tested"
    print(f"{cave['entity_name']:<10} {cave['site_name']:<30} {coverage:<25} {cave['n_d18o']:<8} {status:<20}")

print("="*100)

# Identify priority caves for testing
print("\n" + "="*100)
print("PRIORITY CAVES FOR IMMEDIATE TESTING")
print("="*100 + "\n")

priority = [c for c in modern_caves if not c['tested'] and c['max_year'] >= 1950]
print(f"Found {len(priority)} caves with data ≥1950 CE (likely modern earthquake coverage):\n")

for i, cave in enumerate(priority[:20], 1):  # Show top 20
    print(f"{i:2d}. {cave['entity_name']:<10} {cave['site_name']:<30} → {cave['max_year']:.0f} CE")

print("\n" + "="*100)
print("NEXT STEPS")
print("="*100 + "\n")
print("1. For each priority cave:")
print("   - Search for earthquakes within 100 km (1900-2025)")
print("   - Test detection using δ18O z-scores")
print("   - Record: WORKS (>50% detection) vs FAILS (<50% detection)")
print("")
print("2. Build comparison database:")
print("   - WORKING caves: Geology, climate, fault type, depth")
print("   - FAILING caves: Same parameters")
print("   - Identify discriminating factors")
print("")
print("3. Develop predictive model:")
print("   - Which cave characteristics predict success?")
print("   - Can we screen caves before full analysis?")
print("")

# Save results
output_file = os.path.join(project_dir, 'CAVE_VALIDATION_DATABASE.csv')
df = pd.DataFrame(modern_caves)
df.to_csv(output_file, index=False)
print(f"Saved cave database to: CAVE_VALIDATION_DATABASE.csv")
print(f"Total caves with modern coverage: {len(modern_caves)}")
print()
