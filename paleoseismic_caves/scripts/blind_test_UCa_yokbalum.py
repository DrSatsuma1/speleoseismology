#!/usr/bin/env python3
"""
Blind test of U/Ca on Yok Balum Cave (YB-F1).

Test events (from previous analyses):
- ~495 CE: SEISMIC (z=-4.41σ δ13C, COUPLED)
- ~620 CE: SEISMIC (z=-3.6σ δ18O, COUPLED)
- ~700 CE: SEISMIC (z=-2.5σ, COUPLED)
- 1108 CE: VOLCANIC (1108 eruption, DECOUPLED δ18O/δ13C)
- ~1159 CE: TITAN (seismic + 1171 eruption)
"""

import pandas as pd
import numpy as np

# Load SISAL data
uca = pd.read_csv('data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv/U_Ca.csv')
d18o = pd.read_csv('data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv/d18O.csv')
d13c = pd.read_csv('data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv/d13C.csv')
entity = pd.read_csv('data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv/entity.csv')
sample = pd.read_csv('data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv/sample.csv')
chronology = pd.read_csv('data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv/sisal_chronology.csv')

# Find Yok Balum entity
yb = entity[entity['entity_name'] == 'YB-F1']
print("=== Yok Balum Entity ===")
print(yb[['entity_id', 'entity_name', 'site_id']])
print()

yb_id = yb.iloc[0]['entity_id']
print(f"Yok Balum entity_id: {yb_id}\n")

# Get sample ages
yb_samples = sample[sample['entity_id'] == yb_id][['sample_id', 'depth_sample']]
yb_samples = yb_samples.merge(chronology[['sample_id', 'lin_interp_age']], on='sample_id', how='left')
yb_samples = yb_samples.rename(columns={'lin_interp_age': 'interp_age'})
yb_samples['year_CE'] = 1950 - yb_samples['interp_age']

# Get U/Ca data
yb_uca = uca[uca['sample_id'].isin(yb_samples['sample_id'])].copy()
yb_uca = yb_uca.merge(yb_samples[['sample_id', 'year_CE']], on='sample_id')
yb_uca = yb_uca.sort_values('year_CE')

print(f"=== U/Ca Data ===")
print(f"Found {len(yb_uca)} U/Ca measurements")
if len(yb_uca) > 0:
    print(f"Year range: {yb_uca['year_CE'].min():.0f} - {yb_uca['year_CE'].max():.0f} CE")
    print()

    # Calculate z-scores
    uca_mean = yb_uca['U_Ca_measurement'].mean()
    uca_std = yb_uca['U_Ca_measurement'].std()
    yb_uca['uca_z'] = (yb_uca['U_Ca_measurement'] - uca_mean) / uca_std

    print(f"U/Ca: μ={uca_mean:.6f}, σ={uca_std:.6f}")
else:
    print("NO U/Ca DATA")
    exit(0)

# Get δ13C data for coupling check
yb_d13c = d13c[d13c['sample_id'].isin(yb_samples['sample_id'])].copy()
yb_d13c = yb_d13c.merge(yb_samples[['sample_id', 'year_CE']], on='sample_id')

d13c_mean = yb_d13c['d13C_measurement'].mean()
d13c_std = yb_d13c['d13C_measurement'].std()
yb_d13c['d13c_z'] = (yb_d13c['d13C_measurement'] - d13c_mean) / d13c_std

print(f"δ13C: μ={d13c_mean:.2f}‰, σ={d13c_std:.2f}‰")
print()

# Get δ18O data
yb_d18o = d18o[d18o['sample_id'].isin(yb_samples['sample_id'])].copy()
yb_d18o = yb_d18o.merge(yb_samples[['sample_id', 'year_CE']], on='sample_id')

d18o_mean = yb_d18o['d18O_measurement'].mean()
d18o_std = yb_d18o['d18O_measurement'].std()
yb_d18o['d18o_z'] = (yb_d18o['d18O_measurement'] - d18o_mean) / d18o_std

print(f"δ18O: μ={d18o_mean:.2f}‰, σ={d18o_std:.2f}‰")
print()

# Test events
test_events = [
    {"name": "Event A", "year": 495, "window": 20, "label": "SEISMIC"},
    {"name": "Event B", "year": 620, "window": 25, "label": "SEISMIC"},
    {"name": "Event C", "year": 700, "window": 10, "label": "SEISMIC"},
    {"name": "Event D", "year": 1108, "window": 10, "label": "VOLCANIC"},
    {"name": "Event E", "year": 1159, "window": 10, "label": "TITAN"},
]

print("=== BLIND TEST ===\n")

results = []

for event in test_events:
    year_min = event['year'] - event['window']
    year_max = event['year'] + event['window']

    event_uca = yb_uca[(yb_uca['year_CE'] >= year_min) & (yb_uca['year_CE'] <= year_max)]
    event_d13c = yb_d13c[(yb_d13c['year_CE'] >= year_min) & (yb_d13c['year_CE'] <= year_max)]
    event_d18o = yb_d18o[(yb_d18o['year_CE'] >= year_min) & (yb_d18o['year_CE'] <= year_max)]

    if len(event_uca) > 0 and len(event_d13c) > 0:
        uca_z = event_uca['uca_z'].mean()
        d13c_z = event_d13c['d13c_z'].mean()
        d18o_z = event_d18o['d18o_z'].mean() if len(event_d18o) > 0 else 0

        # Predict based on U/Ca + δ13C coupling
        if uca_z < -1.0 and d13c_z < -1.0:
            prediction = "SEISMIC (both LOW - COUPLED response)"
        elif uca_z < -1.0 and abs(d13c_z) < 1.0:
            prediction = "VOLCANIC (U/Ca LOW but δ13C normal - DECOUPLED)"
        elif abs(uca_z) < 1.0 and abs(d13c_z) < 1.0:
            prediction = "NORMAL (no anomaly)"
        else:
            prediction = "AMBIGUOUS"

        results.append({
            'event': event['name'],
            'year': event['year'],
            'uca_z': uca_z,
            'd13c_z': d13c_z,
            'd18o_z': d18o_z,
            'prediction': prediction,
            'actual': event['label']
        })

        print(f"{event['name']} (~{event['year']} CE):")
        print(f"  U/Ca:  {uca_z:+.2f}σ")
        print(f"  δ13C:  {d13c_z:+.2f}σ")
        print(f"  δ18O:  {d18o_z:+.2f}σ")
        print(f"  PREDICTION: {prediction}")
        print()
    else:
        print(f"{event['name']} (~{event['year']} CE): NO DATA")
        print()

# REVEAL
print("\n" + "="*60)
print("REVEALING CLASSIFICATIONS:")
print("="*60 + "\n")

correct = 0
total = 0

for r in results:
    # Check if prediction matches
    if r['actual'] == 'SEISMIC' and 'SEISMIC' in r['prediction']:
        status = "✓ CORRECT"
        correct += 1
    elif r['actual'] == 'VOLCANIC' and 'VOLCANIC' in r['prediction']:
        status = "✓ CORRECT"
        correct += 1
    elif r['actual'] == 'TITAN':
        status = "- SPECIAL (compound event)"
    else:
        status = "✗ WRONG"

    print(f"{r['event']}: {r['prediction']}")
    print(f"         Actual: {r['actual']}")
    print(f"         {status}\n")

    total += 1

print(f"ACCURACY: {correct}/{total} (excluding TITAN)")
