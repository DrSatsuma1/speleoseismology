#!/usr/bin/env python3
"""Debug Sofular chronology specifically."""
import csv
from pathlib import Path

SISAL_DIR = Path('/Users/catherine/projects/quake/paleoseismic_caves/data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv')

def load_csv(filename):
    with open(SISAL_DIR / filename, 'r') as f:
        return list(csv.DictReader(f))

def safe_float(val):
    if val in ('NA', '', None, 'nan', 'NaN'):
        return None
    try:
        return float(val)
    except:
        return None

# Load samples
samples = load_csv('sample.csv')
sofular_samples = set(s['sample_id'] for s in samples if s['entity_id'] == '305')
print(f"Sofular samples: {len(sofular_samples)}")

# Load chronology and check Sofular
chron = load_csv('sisal_chronology.csv')

# Find Sofular samples in chronology
sofular_chron = [r for r in chron if r['sample_id'] in sofular_samples]
print(f"Sofular chronology records: {len(sofular_chron)}")

if sofular_chron:
    # Check first few records
    print("\nFirst 5 Sofular chronology records:")
    for r in sofular_chron[:5]:
        print(f"  sample_id={r['sample_id']}")
        print(f"    lin_interp_age: '{r.get('lin_interp_age', 'MISSING')}'")
        print(f"    StalAge_age: '{r.get('StalAge_age', 'MISSING')}'")
        print(f"    Bchron_age: '{r.get('Bchron_age', 'MISSING')}'")
        print()

    # Count how many have valid ages
    with_lin = sum(1 for r in sofular_chron if safe_float(r.get('lin_interp_age')) is not None)
    with_stal = sum(1 for r in sofular_chron if safe_float(r.get('StalAge_age')) is not None)
    with_bchron = sum(1 for r in sofular_chron if safe_float(r.get('Bchron_age')) is not None)

    print(f"With valid lin_interp_age: {with_lin}")
    print(f"With valid StalAge_age: {with_stal}")
    print(f"With valid Bchron_age: {with_bchron}")

    # Check if ANY age column has data
    for col in ['lin_interp_age', 'StalAge_age', 'Bchron_age', 'Bacon_age', 'OxCal_age', 'copRa_age', 'lin_reg_age']:
        count = sum(1 for r in sofular_chron if safe_float(r.get(col)) is not None)
        if count > 0:
            print(f"  {col}: {count} valid")
