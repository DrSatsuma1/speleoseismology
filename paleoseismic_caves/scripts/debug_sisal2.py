#!/usr/bin/env python3
"""Debug Sofular matching and find historical Brazilian caves."""
import csv
from pathlib import Path

SISAL_DIR = Path('/Users/catherine/projects/quake/paleoseismic_caves/data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv')

def load_csv(filename):
    with open(SISAL_DIR / filename, 'r') as f:
        return list(csv.DictReader(f))

# Load data
samples = load_csv('sample.csv')
d18O = load_csv('d18O.csv')
chron = load_csv('sisal_chronology.csv')
entities = load_csv('entity.csv')
sites = load_csv('site.csv')

# Debug Sofular
print("=== DEBUGGING SOFULAR ===")
sofular_samples = [s['sample_id'] for s in samples if s['entity_id'] == '305']
print(f"Sofular sample IDs (first 5): {sofular_samples[:5]}")
print(f"Type: {type(sofular_samples[0])}")

# Check d18O
d18O_ids = set(r['sample_id'] for r in d18O)
print(f"\nd18O sample IDs (first 5): {list(d18O_ids)[:5]}")

# Check overlap
sofular_set = set(sofular_samples)
overlap = sofular_set & d18O_ids
print(f"Sofular samples in d18O: {len(overlap)}")
if overlap:
    print(f"  First matching ID: {list(overlap)[0]}")

# Check chronology
chron_ids = set(r['sample_id'] for r in chron)
chron_overlap = sofular_set & chron_ids
print(f"Sofular samples in chronology: {len(chron_overlap)}")

# Check for BOTH
both_overlap = sofular_set & d18O_ids & chron_ids
print(f"Sofular samples with BOTH: {len(both_overlap)}")

# Check a specific sample
if both_overlap:
    sample_id = list(both_overlap)[0]
    print(f"\nChecking sample {sample_id}:")
    d18O_record = [r for r in d18O if r['sample_id'] == sample_id]
    chron_record = [r for r in chron if r['sample_id'] == sample_id]
    print(f"  d18O: {d18O_record[0] if d18O_record else 'NOT FOUND'}")
    print(f"  Chron age: {chron_record[0].get('StalAge_age', 'NA') if chron_record else 'NOT FOUND'}")

# Now find Brazilian caves with HISTORICAL coverage
print("\n\n=== BRAZILIAN CAVES WITH HISTORICAL DATA ===")

entity_info = {e['entity_id']: e for e in entities}
site_info = {s['site_id']: s for s in sites}

# Group samples by entity
entity_samples = {}
for s in samples:
    eid = s['entity_id']
    if eid not in entity_samples:
        entity_samples[eid] = []
    entity_samples[eid].append(s['sample_id'])

# Build age lookup
def safe_float(val):
    if val in ('NA', '', None, 'nan', 'NaN'):
        return None
    try:
        return float(val)
    except:
        return None

age_map = {}
for r in chron:
    age = safe_float(r.get('StalAge_age')) or safe_float(r.get('lin_interp_age'))
    if age is not None:
        age_map[r['sample_id']] = age

# Find caves with historical data
historical_caves = []
for eid, sample_ids in entity_samples.items():
    sample_set = set(sample_ids)
    both = sample_set & d18O_ids & chron_ids

    if len(both) > 30:
        # Get ages for these samples
        ages_ce = []
        for sid in both:
            if sid in age_map:
                age_ce = 1950 - age_map[sid]
                ages_ce.append(age_ce)

        if ages_ce:
            min_age = min(ages_ce)
            max_age = max(ages_ce)

            # Check if recent end is historical (> 0 CE)
            if max_age > 0:
                # Get location
                if eid in entity_info:
                    e = entity_info[eid]
                    site_id = e.get('site_id', '')
                    if site_id in site_info:
                        site = site_info[site_id]
                        lat = safe_float(site.get('latitude', ''))
                        lon = safe_float(site.get('longitude', ''))

                        # South America
                        if lat is not None and lon is not None and lat < 15 and lon < -30:
                            historical_caves.append({
                                'entity_id': eid,
                                'entity_name': e.get('entity_name', ''),
                                'site_name': site.get('site_name', ''),
                                'lat': lat,
                                'lon': lon,
                                'samples': len(both),
                                'min_age': min_age,
                                'max_age': max_age
                            })

# Sort by most recent date
historical_caves.sort(key=lambda x: x['max_age'], reverse=True)

print("South American caves with data extending to historical period:\n")
for c in historical_caves[:15]:
    print(f"Entity {c['entity_id']:>3} ({c['entity_name']:>15}): {c['samples']:>4} samples, {c['min_age']:.0f} - {c['max_age']:.0f} CE - {c['site_name']} ({c['lat']:.2f}, {c['lon']:.2f})")
