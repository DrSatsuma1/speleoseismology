#!/usr/bin/env python3
"""
Blind test of U/Ca hypothesis for seismic vs climatic discrimination.

Hypothesis:
- SEISMIC (deep water): HIGH U/Ca + HIGH Mg/Ca (old water, uranium accumulation)
- CLIMATIC (fresh water): LOW U/Ca + LOW Mg/Ca (fresh meteoric)

U/Ca should behave similarly to δ234U (water residence time proxy) but may have
better coverage if measured as continuous trace element proxy rather than just
at dating points.
"""

import pandas as pd
import numpy as np

# Load SISAL data
uca = pd.read_csv('data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv/U_Ca.csv')
mgca = pd.read_csv('data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv/Mg_Ca.csv')
entity = pd.read_csv('data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv/entity.csv')
sample = pd.read_csv('data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv/sample.csv')
chronology = pd.read_csv('data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv/sisal_chronology.csv')

# Find Bàsura entity
basura = entity[entity['entity_name'] == 'BA18-4']
print("=== Bàsura Entity ===")
print(basura[['entity_id', 'entity_name', 'site_id']])
print()

basura_id = basura.iloc[0]['entity_id']
print(f"Bàsura entity_id: {basura_id}\n")

# Get sample ages from chronology table
basura_samples = sample[sample['entity_id'] == basura_id][['sample_id', 'depth_sample']]
basura_samples = basura_samples.merge(chronology[['sample_id', 'lin_interp_age']], on='sample_id', how='left')
basura_samples = basura_samples.rename(columns={'lin_interp_age': 'interp_age'})
basura_samples['year_CE'] = 1950 - basura_samples['interp_age']

# Get U/Ca data
basura_uca = uca[uca['sample_id'].isin(basura_samples['sample_id'])].copy()
basura_uca = basura_uca.merge(basura_samples[['sample_id', 'year_CE']], on='sample_id')
basura_uca = basura_uca.sort_values('year_CE')

print(f"=== U/Ca Data ===")
print(f"Found {len(basura_uca)} U/Ca measurements")
if len(basura_uca) > 0:
    print(f"Year range: {basura_uca['year_CE'].min():.0f} - {basura_uca['year_CE'].max():.0f} CE")
    print()

    # Calculate z-scores for U/Ca
    uca_mean = basura_uca['U_Ca_measurement'].mean()
    uca_std = basura_uca['U_Ca_measurement'].std()
    basura_uca['uca_z'] = (basura_uca['U_Ca_measurement'] - uca_mean) / uca_std

    print(f"U/Ca: μ={uca_mean:.6f}, σ={uca_std:.6f}")
else:
    print("NO U/Ca DATA AVAILABLE for Bàsura")
    exit(0)

# Get Mg/Ca data
basura_mgca = mgca[mgca['sample_id'].isin(basura_samples['sample_id'])].copy()
basura_mgca = basura_mgca.merge(basura_samples[['sample_id', 'year_CE']], on='sample_id')
basura_mgca = basura_mgca.sort_values('year_CE')

mgca_mean = basura_mgca['Mg_Ca_measurement'].mean()
mgca_std = basura_mgca['Mg_Ca_measurement'].std()
basura_mgca['mgca_z'] = (basura_mgca['Mg_Ca_measurement'] - mgca_mean) / mgca_std

print(f"Mg/Ca: μ={mgca_mean:.6f}, σ={mgca_std:.6f}")
print()

# Define test events (BLIND)
test_events = [
    {"name": "Event A", "year": 1285, "window": 85, "label": "SEISMIC"},
    {"name": "Event B", "year": 1394, "window": 13, "label": "SEISMIC"},
    {"name": "Event C", "year": 1649, "window": 10, "label": "CLIMATIC"},
]

print("=== BLIND TEST ===")
print("Extracting data for anonymous events...\n")

results = []

for event in test_events:
    year_min = event['year'] - event['window']
    year_max = event['year'] + event['window']

    # Get U/Ca in window
    event_uca = basura_uca[(basura_uca['year_CE'] >= year_min) &
                           (basura_uca['year_CE'] <= year_max)]

    # Get Mg/Ca in window
    event_mgca = basura_mgca[(basura_mgca['year_CE'] >= year_min) &
                             (basura_mgca['year_CE'] <= year_max)]

    if len(event_uca) > 0 and len(event_mgca) > 0:
        # Take mean values in window
        uca_z = event_uca['uca_z'].mean()
        mgca_z = event_mgca['mgca_z'].mean()

        # MAKE PREDICTION
        if uca_z > 0 and mgca_z > 0:
            prediction = "SEISMIC (both HIGH - deep water)"
        elif uca_z < 0 and mgca_z < 0:
            prediction = "CLIMATIC (both LOW - dilution)"
        elif uca_z > 0 and mgca_z < 0:
            prediction = "CLIMATIC (opposite - evaporation)"
        else:
            prediction = "SEISMIC? (HIGH Mg, LOW U - unusual)"

        results.append({
            'event': event['name'],
            'year': event['year'],
            'uca_z': uca_z,
            'mgca_z': mgca_z,
            'prediction': prediction,
            'actual': event['label'],
            'n_uca': len(event_uca),
            'n_mgca': len(event_mgca)
        })

        print(f"{event['name']} (~{event['year']} CE):")
        print(f"  U/Ca: {uca_z:+.2f}σ (n={len(event_uca)})")
        print(f"  Mg/Ca: {mgca_z:+.2f}σ (n={len(event_mgca)})")
        print(f"  PREDICTION: {prediction}")
        print()
    else:
        print(f"{event['name']} (~{event['year']} CE): NO DATA")
        print(f"  (U/Ca: {len(event_uca)} samples, Mg/Ca: {len(event_mgca)} samples)")
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
    print(f"         {status}")
    print(f"         (Coverage: {r['n_uca']} U/Ca, {r['n_mgca']} Mg/Ca samples)\n")

    if correct_prediction:
        correct += 1
    total += 1

if total > 0:
    print(f"ACCURACY: {correct}/{total} = {100*correct/total:.0f}%")
    print(f"\nU/Ca COVERAGE: {len(basura_uca)} samples vs δ234U: 18 samples")
    print(f"U/Ca testable events: {total}/3 = {100*total/3:.0f}%")
else:
    print("No events with paired data - cannot calculate accuracy")
