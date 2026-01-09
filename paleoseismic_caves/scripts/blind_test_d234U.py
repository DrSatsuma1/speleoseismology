#!/usr/bin/env python3
"""
Blind test of δ234U hypothesis for seismic vs climatic discrimination.

Hypothesis:
- SEISMIC (deep water): HIGH δ234U + HIGH Mg/Ca (SAME direction)
- CLIMATIC (dilution): LOW δ234U + LOW Mg/Ca (SAME direction)
- CLIMATIC (evaporation): HIGH δ234U + LOW Mg/Ca (OPPOSITE)

Test events:
- 1285 ± 85 yr: SEISMIC (known Mg/Ca +2.25σ)
- 1394 ± 13 yr: SEISMIC (known Mg/Ca +1.60σ)
- 1649 CE: CLIMATIC volcanic recovery (known Mg/Ca -0.57σ)
"""

import pandas as pd
import numpy as np

# Load SISAL data
dating = pd.read_csv('data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv/dating.csv')
mgca = pd.read_csv('data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv/Mg_Ca.csv')
entity = pd.read_csv('data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv/entity.csv')
sample = pd.read_csv('data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv/sample.csv')
chronology = pd.read_csv('data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv/sisal_chronology.csv')

# Find Bàsura entity
basura = entity[entity['entity_name'] == 'BA18-4']
print("=== Bàsura Entity ===")
print(basura[['entity_id', 'entity_name', 'site_id']])
print()

if len(basura) == 0:
    print("ERROR: Bàsura not found!")
    exit(1)

basura_id = basura.iloc[0]['entity_id']
print(f"Bàsura entity_id: {basura_id}\n")

# Get δ234U from dating table
basura_dating = dating[dating['entity_id'] == basura_id].copy()
basura_dating = basura_dating[basura_dating['234U_238U_activity'].notna()]

# Get sample ages from chronology table
basura_samples = sample[sample['entity_id'] == basura_id][['sample_id', 'depth_sample']]
basura_samples = basura_samples.merge(chronology[['sample_id', 'lin_interp_age']], on='sample_id', how='left')
basura_samples = basura_samples.rename(columns={'lin_interp_age': 'interp_age'})

print(f"=== δ234U Data ===")
print(f"Found {len(basura_dating)} U-Th dates with δ234U measurements")
print(f"Date range: {basura_dating['corr_age'].min():.0f} - {basura_dating['corr_age'].max():.0f} years BP")
print()

if len(basura_dating) == 0:
    print("ERROR: No δ234U data found for Bàsura!")
    exit(1)

# Convert years BP to CE
basura_dating['year_CE'] = 1950 - basura_dating['corr_age']
basura_dating = basura_dating.sort_values('year_CE')

print("=== Available δ234U measurements ===")
print(basura_dating[['depth_dating', 'year_CE', '234U_238U_activity', '234U_238U_activity_uncertainty']].to_string(index=False))
print()

# Get Mg/Ca data
basura_mgca = mgca[mgca['sample_id'].isin(basura_samples['sample_id'])].copy()

# Merge with sample ages
basura_mgca = basura_mgca.merge(basura_samples, on='sample_id')
basura_mgca = basura_mgca.sort_values('interp_age')

print(f"=== Mg/Ca Data ===")
print(f"Found {len(basura_mgca)} Mg/Ca measurements")
print()

# Calculate z-scores for Mg/Ca
mgca_mean = basura_mgca['Mg_Ca_measurement'].mean()
mgca_std = basura_mgca['Mg_Ca_measurement'].std()
basura_mgca['mgca_z'] = (basura_mgca['Mg_Ca_measurement'] - mgca_mean) / mgca_std

# Calculate z-scores for δ234U
d234_mean = basura_dating['234U_238U_activity'].mean()
d234_std = basura_dating['234U_238U_activity'].std()
basura_dating['d234_z'] = (basura_dating['234U_238U_activity'] - d234_mean) / d234_std

print(f"Mg/Ca: μ={mgca_mean:.6f}, σ={mgca_std:.6f}")
print(f"δ234U: μ={d234_mean:.3f}, σ={d234_std:.3f}")
print()

# Define test events (BLIND - don't look at actual classification yet)
test_events = [
    {"name": "Event A", "year": 1285, "window": 85, "label": "SEISMIC"},  # 1285 ± 85
    {"name": "Event B", "year": 1394, "window": 13, "label": "SEISMIC"},  # 1394 ± 13
    {"name": "Event C", "year": 1649, "window": 10, "label": "CLIMATIC"}, # 1649 volcanic
]

print("=== BLIND TEST ===")
print("Extracting data for anonymous events...\n")

results = []

for event in test_events:
    year_min = event['year'] - event['window']
    year_max = event['year'] + event['window']

    # Get closest δ234U measurement
    event_d234 = basura_dating[(basura_dating['year_CE'] >= year_min) &
                               (basura_dating['year_CE'] <= year_max)]

    # Get Mg/Ca in window (from sample ages)
    # Convert sample ages (years BP) to CE
    basura_mgca['year_CE'] = 1950 - basura_mgca['interp_age']
    event_mgca = basura_mgca[(basura_mgca['year_CE'] >= year_min) &
                             (basura_mgca['year_CE'] <= year_max)]

    if len(event_d234) > 0 and len(event_mgca) > 0:
        # Take peak/mean values
        d234_z = event_d234['d234_z'].iloc[0]  # Closest date
        mgca_z = event_mgca['mgca_z'].mean()    # Mean in window

        # MAKE PREDICTION (without looking at label)
        if d234_z > 0 and mgca_z > 0:
            prediction = "SEISMIC (both HIGH - deep water)"
        elif d234_z < 0 and mgca_z < 0:
            prediction = "CLIMATIC (both LOW - dilution)"
        elif d234_z > 0 and mgca_z < 0:
            prediction = "CLIMATIC (opposite - evaporation)"
        else:
            prediction = "SEISMIC? (HIGH Mg, LOW δ234U - unusual)"

        results.append({
            'event': event['name'],
            'year': event['year'],
            'd234_z': d234_z,
            'mgca_z': mgca_z,
            'prediction': prediction,
            'actual': event['label']
        })

        print(f"{event['name']} (~{event['year']} CE):")
        print(f"  δ234U: {d234_z:+.2f}σ")
        print(f"  Mg/Ca: {mgca_z:+.2f}σ")
        print(f"  PREDICTION: {prediction}")
        print()
    else:
        print(f"{event['name']} (~{event['year']} CE): NO DATA")
        print()

# REVEAL TRUTH
print("\n" + "="*60)
print("REVEALING ACTUAL CLASSIFICATIONS:")
print("="*60 + "\n")

correct = 0
total = 0

for r in results:
    correct_prediction = r['prediction'].startswith(r['actual'])
    status = "✓ CORRECT" if correct_prediction else "✗ WRONG"

    print(f"{r['event']}: Predicted {r['prediction']}")
    print(f"         Actual: {r['actual']}")
    print(f"         {status}\n")

    if correct_prediction:
        correct += 1
    total += 1

if total > 0:
    print(f"ACCURACY: {correct}/{total} = {100*correct/total:.0f}%")
else:
    print("No events with paired data - cannot calculate accuracy")
