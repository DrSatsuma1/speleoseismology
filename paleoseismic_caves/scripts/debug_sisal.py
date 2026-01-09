#!/usr/bin/env python3
"""Debug and find alternatives for caves without chronology."""
import csv
from pathlib import Path

SISAL_DIR = Path('/Users/catherine/projects/quake/paleoseismic_caves/data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv')

def load_csv(filename):
    with open(SISAL_DIR / filename, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

# Load all data
samples = load_csv('sample.csv')
entities = load_csv('entity.csv')
sites = load_csv('site.csv')
d18O = load_csv('d18O.csv')
chron = load_csv('sisal_chronology.csv')

d18O_sample_ids = set(int(r['sample_id']) for r in d18O)
chron_sample_ids = set(int(r['sample_id']) for r in chron)

# Build entity info
entity_info = {e['entity_id']: e for e in entities}
site_info = {s['site_id']: s for s in sites}

print("=== LOOKING FOR BRAZILIAN CAVES WITH CHRONOLOGY ===\n")

# Group samples by entity
entity_samples = {}
for s in samples:
    eid = s['entity_id']
    if eid not in entity_samples:
        entity_samples[eid] = []
    entity_samples[eid].append(int(s['sample_id']))

# Find Brazilian entities with chronology
brazilian_candidates = []
for eid, sample_ids in entity_samples.items():
    sample_set = set(sample_ids)
    both = sample_set & d18O_sample_ids & chron_sample_ids

    if len(both) > 50:  # At least 50 samples
        # Get entity and site info
        if eid in entity_info:
            e = entity_info[eid]
            site_id = e.get('site_id', '')
            if site_id and site_id in site_info:
                site = site_info[site_id]
                lat = site.get('latitude', '')
                lon = site.get('longitude', '')
                country = site.get('country', '')
                site_name = site.get('site_name', '')

                # Check if South American (latitude < 15 and longitude < -30)
                try:
                    lat_f = float(lat)
                    lon_f = float(lon)
                    if lat_f < 15 and lon_f < -30:  # South/Central America
                        brazilian_candidates.append({
                            'entity_id': eid,
                            'entity_name': e.get('entity_name', ''),
                            'site_name': site_name,
                            'country': country,
                            'lat': lat_f,
                            'lon': lon_f,
                            'samples_with_both': len(both)
                        })
                except:
                    pass

# Sort by sample count
brazilian_candidates.sort(key=lambda x: x['samples_with_both'], reverse=True)

print("South/Central American caves with d18O + chronology:\n")
for c in brazilian_candidates[:20]:
    print(f"Entity {c['entity_id']:>3} ({c['entity_name']:>15}): {c['samples_with_both']:>4} samples - {c['site_name']}, {c['country']} ({c['lat']:.2f}, {c['lon']:.2f})")

# Also check if any Yok Balum entities have chronology (we know this works)
print("\n=== CHECKING YOK BALUM ===")
yok_entities = ['209', '210']
for eid in yok_entities:
    if eid in entity_samples:
        sample_set = set(entity_samples[eid])
        both = sample_set & d18O_sample_ids & chron_sample_ids
        print(f"Entity {eid}: {len(both)} samples with both d18O + chronology")
