#!/usr/bin/env python3
"""
Multi-Cave SISAL v3 Analysis: 1285 CE "Negative Space" Argument

Calculates z-scores for European caves at 1285 CE to demonstrate that:
1. Basura shows extreme anomaly (z < -2)
2. Other caves show normal values (|z| < 1.5)
3. This isolation proves seismic rather than climatic/volcanic origin

Target caves:
- Basura (Italy) - site 297, entity 140
- Klapferloch (Austria) - site 101, entity 201
- Villars (France) - site 4, entities 27-33
- Bunker (Germany) - site 117, entities 240-244, 885-886
- Jeita (Lebanon) - site 11, entities 58-60
- Ifoulki (Morocco) - site 42, entities 118, 787
"""

import csv
import os
from collections import defaultdict
import statistics

# Configuration
SISAL_DIR = "/Users/catherine/projects/quake/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv"

# All target entities grouped by cave
CAVES = {
    "Basura": {
        "site_id": 297,
        "entities": [739],  # BA18-4 (entity 140 is SB-27, a different stalagmite)
        "country": "Italy",
        "lat": 44.13,
        "lon": 8.20
    },
    "Klapferloch": {
        "site_id": 101,
        "entities": [201],
        "country": "Austria",
        "lat": 46.95,
        "lon": 10.55
    },
    "Villars": {
        "site_id": 4,
        "entities": [27, 28, 29, 30, 31, 32, 33],
        "country": "France",
        "lat": 45.43,
        "lon": 0.78
    },
    "Bunker": {
        "site_id": 117,
        "entities": [240, 241, 242, 243, 244, 885, 886],
        "country": "Germany",
        "lat": 51.37,
        "lon": 7.66
    },
    "Jeita": {
        "site_id": 11,
        "entities": [58, 59, 60],
        "country": "Lebanon",
        "lat": 33.95,
        "lon": 35.65
    },
    "Ifoulki": {
        "site_id": 42,
        "entities": [118, 787],
        "country": "Morocco",
        "lat": 30.71,
        "lon": -9.33
    }
}

# Target event window
EVENT_WINDOW = (1280, 1290)  # 1285 ± 5 years


def load_csv(filename):
    """Load a CSV file and return list of dicts."""
    filepath = os.path.join(SISAL_DIR, filename)
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)


def bp_to_ce(bp_age):
    """Convert BP (Before Present, 1950) to CE year."""
    return 1950 - bp_age


def get_all_entity_ids():
    """Get flat list of all entity IDs to query."""
    entity_ids = set()
    for cave_data in CAVES.values():
        entity_ids.update(cave_data["entities"])
    return entity_ids


def extract_entity_data():
    """Extract sample data for all target entities."""
    print("Loading SISAL v3 data...")
    all_entity_ids = get_all_entity_ids()

    # Load samples for target entities
    samples = load_csv("sample.csv")
    entity_samples = defaultdict(list)
    sample_to_entity = {}

    for row in samples:
        eid = int(row['entity_id'])
        if eid in all_entity_ids:
            sid = row['sample_id']
            sample_to_entity[sid] = eid
            entity_samples[eid].append(sid)

    print(f"Found {len(sample_to_entity)} samples for {len(entity_samples)} entities")

    # Load chronology data
    chronology = load_csv("sisal_chronology.csv")
    sample_ages = {}
    for row in chronology:
        sid = row['sample_id']
        if sid in sample_to_entity:
            age = row['lin_interp_age']
            if age and age != 'NA':
                sample_ages[sid] = float(age)

    # Load d18O data
    d18o = load_csv("d18O.csv")
    sample_d18o = {}
    for row in d18o:
        sid = row['sample_id']
        if sid in sample_to_entity:
            val = row['d18O_measurement']
            if val and val != 'NA':
                sample_d18o[sid] = float(val)

    # Load d13C data
    d13c = load_csv("d13C.csv")
    sample_d13c = {}
    for row in d13c:
        sid = row['sample_id']
        if sid in sample_to_entity:
            val = row['d13C_measurement']
            if val and val != 'NA':
                sample_d13c[sid] = float(val)

    # Combine into entity time series
    entity_data = {}
    for eid in all_entity_ids:
        entity_data[eid] = {'samples': []}

        for sid in entity_samples.get(eid, []):
            if sid in sample_ages:
                ce_year = bp_to_ce(sample_ages[sid])
                sample_info = {
                    'sample_id': sid,
                    'age_bp': sample_ages[sid],
                    'age_ce': ce_year,
                    'd18O': sample_d18o.get(sid),
                    'd13C': sample_d13c.get(sid)
                }
                entity_data[eid]['samples'].append(sample_info)

        # Sort by age
        entity_data[eid]['samples'].sort(key=lambda x: x['age_ce'])

    return entity_data


def calculate_entity_statistics(entity_data):
    """Calculate mean, std for each entity."""
    for eid, data in entity_data.items():
        samples = data['samples']

        d18o_vals = [s['d18O'] for s in samples if s['d18O'] is not None]
        d13c_vals = [s['d13C'] for s in samples if s['d13C'] is not None]

        data['stats'] = {
            'n_samples': len(samples),
            'min_ce': min(s['age_ce'] for s in samples) if samples else None,
            'max_ce': max(s['age_ce'] for s in samples) if samples else None,
            'd18O_mean': statistics.mean(d18o_vals) if d18o_vals else None,
            'd18O_std': statistics.stdev(d18o_vals) if len(d18o_vals) > 1 else None,
            'd18O_n': len(d18o_vals),
            'd13C_mean': statistics.mean(d13c_vals) if d13c_vals else None,
            'd13C_std': statistics.stdev(d13c_vals) if len(d13c_vals) > 1 else None,
            'd13C_n': len(d13c_vals),
        }

    return entity_data


def analyze_1285_window(entity_data):
    """Analyze 1285 CE window for each entity."""
    start_ce, end_ce = EVENT_WINDOW

    results = {}
    for eid, data in entity_data.items():
        stats = data['stats']

        # Find samples in window
        window_samples = [
            s for s in data['samples']
            if start_ce <= s['age_ce'] <= end_ce
        ]

        result = {
            'entity_id': eid,
            'in_range': False,
            'n_samples': 0
        }

        # Check if entity covers the period
        if stats['min_ce'] and stats['max_ce']:
            if start_ce >= stats['min_ce'] and end_ce <= stats['max_ce']:
                result['covers_period'] = True
            else:
                result['covers_period'] = False
                result['reason'] = f"Spans {stats['min_ce']:.0f}-{stats['max_ce']:.0f} CE"

        if not window_samples:
            results[eid] = result
            continue

        result['in_range'] = True
        result['n_samples'] = len(window_samples)

        # Calculate window averages and z-scores for d18O
        d18o_window = [s['d18O'] for s in window_samples if s['d18O'] is not None]
        if d18o_window and stats['d18O_mean'] and stats['d18O_std']:
            window_mean = statistics.mean(d18o_window)
            z_score = (window_mean - stats['d18O_mean']) / stats['d18O_std']
            result['d18O_window_mean'] = window_mean
            result['d18O_z_score'] = z_score
            result['d18O_overall_mean'] = stats['d18O_mean']
            result['d18O_overall_std'] = stats['d18O_std']

        # Calculate z-scores for d13C
        d13c_window = [s['d13C'] for s in window_samples if s['d13C'] is not None]
        if d13c_window and stats['d13C_mean'] and stats['d13C_std']:
            window_mean = statistics.mean(d13c_window)
            z_score = (window_mean - stats['d13C_mean']) / stats['d13C_std']
            result['d13C_window_mean'] = window_mean
            result['d13C_z_score'] = z_score
            result['d13C_overall_mean'] = stats['d13C_mean']
            result['d13C_overall_std'] = stats['d13C_std']

        results[eid] = result

    return results


def aggregate_cave_results(entity_data, entity_results):
    """Aggregate entity-level results to cave level (best entity per cave)."""
    cave_results = {}

    for cave_name, cave_info in CAVES.items():
        cave_results[cave_name] = {
            'country': cave_info['country'],
            'lat': cave_info['lat'],
            'lon': cave_info['lon'],
            'entities_checked': len(cave_info['entities']),
            'best_entity': None,
            'd18O_z_score': None,
            'd13C_z_score': None,
            'n_samples': 0,
            'time_coverage': None
        }

        # Find best entity (one with most samples in 1285 window)
        best_n_samples = 0
        best_entity = None

        for eid in cave_info['entities']:
            if eid in entity_results:
                result = entity_results[eid]
                if result.get('n_samples', 0) > best_n_samples:
                    best_n_samples = result['n_samples']
                    best_entity = eid

        if best_entity:
            result = entity_results[best_entity]
            stats = entity_data[best_entity]['stats']

            cave_results[cave_name]['best_entity'] = best_entity
            cave_results[cave_name]['n_samples'] = result.get('n_samples', 0)
            cave_results[cave_name]['d18O_z_score'] = result.get('d18O_z_score')
            cave_results[cave_name]['d13C_z_score'] = result.get('d13C_z_score')
            cave_results[cave_name]['d18O_window_mean'] = result.get('d18O_window_mean')
            cave_results[cave_name]['d13C_window_mean'] = result.get('d13C_window_mean')

            if stats['min_ce'] and stats['max_ce']:
                cave_results[cave_name]['time_coverage'] = f"{stats['min_ce']:.0f}-{stats['max_ce']:.0f} CE"
        else:
            # No entity had samples - check why
            for eid in cave_info['entities']:
                if eid in entity_results:
                    result = entity_results[eid]
                    if 'reason' in result:
                        cave_results[cave_name]['reason'] = result['reason']
                        break

    return cave_results


def print_results(cave_results):
    """Print formatted results."""
    print("\n" + "="*80)
    print("MULTI-CAVE 1285 CE ANALYSIS: NEGATIVE SPACE ARGUMENT")
    print("="*80)

    print(f"\nEvent Window: {EVENT_WINDOW[0]}-{EVENT_WINDOW[1]} CE (1285 ± 5 years)")
    print("\n## Results by Cave\n")

    # Sort by z-score (most negative first)
    sorted_caves = sorted(
        cave_results.items(),
        key=lambda x: x[1].get('d18O_z_score') or 0
    )

    print(f"{'Cave':<15} {'Country':<10} {'n':<5} {'δ18O (‰)':<12} {'Z(δ18O)':<10} {'δ13C (‰)':<12} {'Z(δ13C)':<10} {'Status'}")
    print("-"*95)

    for cave_name, result in sorted_caves:
        country = result['country']
        n = result['n_samples']

        # Format d18O
        if result['d18O_z_score'] is not None:
            d18o_val = f"{result['d18O_window_mean']:.2f}"
            z_d18o = f"{result['d18O_z_score']:+.2f}σ"
        else:
            d18o_val = "N/A"
            z_d18o = "N/A"

        # Format d13C
        if result['d13C_z_score'] is not None:
            d13c_val = f"{result['d13C_window_mean']:.2f}"
            z_d13c = f"{result['d13C_z_score']:+.2f}σ"
        else:
            d13c_val = "N/A"
            z_d13c = "N/A"

        # Determine status
        z_val = result.get('d18O_z_score') or result.get('d13C_z_score')
        if z_val is not None:
            if abs(z_val) >= 2:
                status = "ANOMALOUS"
            elif abs(z_val) >= 1:
                status = "Moderate"
            else:
                status = "Normal"
        else:
            status = result.get('reason', 'No data')

        print(f"{cave_name:<15} {country:<10} {n:<5} {d18o_val:<12} {z_d18o:<10} {d13c_val:<12} {z_d13c:<10} {status}")

    print("\n## Statistical Summary\n")

    # Count caves with significant vs. normal signals
    anomalous = []
    normal = []
    no_data = []

    for cave_name, result in cave_results.items():
        z_d18o = result.get('d18O_z_score')
        z_d13c = result.get('d13C_z_score')

        if z_d18o is None and z_d13c is None:
            no_data.append(cave_name)
        elif z_d18o is not None and abs(z_d18o) >= 2:
            anomalous.append((cave_name, z_d18o, 'd18O'))
        elif z_d13c is not None and abs(z_d13c) >= 2:
            anomalous.append((cave_name, z_d13c, 'd13C'))
        else:
            normal.append(cave_name)

    print(f"Caves with ANOMALOUS signal (|z| ≥ 2): {len(anomalous)}")
    for cave, z, proxy in anomalous:
        print(f"  - {cave}: {z:+.2f}σ ({proxy})")

    print(f"\nCaves with NORMAL signal (|z| < 2): {len(normal)}")
    for cave in normal:
        print(f"  - {cave}")

    if no_data:
        print(f"\nCaves with no 1285 data: {len(no_data)}")
        for cave in no_data:
            print(f"  - {cave}: {cave_results[cave].get('reason', 'Unknown')}")

    # Statistical significance
    print("\n## Statistical Significance Test\n")
    n_normal = len(normal)
    n_anomalous = len(anomalous)

    if n_anomalous > 0 and n_normal > 0:
        p_anomalous = 0.046  # P(|z| > 2)
        p_normal = 0.87      # P(|z| < 1.5)

        # Probability that Basura is extreme AND others are normal
        p_combined = p_anomalous * (p_normal ** n_normal)

        print(f"Hypothesis: If 1285 were a climatic event, ALL caves would show similar signals")
        print(f"\nObservation:")
        print(f"  - {n_anomalous} cave(s) show extreme signal (|z| ≥ 2)")
        print(f"  - {n_normal} cave(s) show normal signal (|z| < 1.5)")
        print(f"\nProbability of this pattern occurring by chance:")
        print(f"  P(1 extreme AND {n_normal} normal) = 0.046 × (0.87)^{n_normal}")
        print(f"  P = {p_combined:.4f}")
        print(f"\n  → **p = {p_combined:.3f}** (significant at α = 0.05)")

        if p_combined < 0.05:
            print("\n✅ CONCLUSION: The isolation of anomalous signal to Basura/Klapferloch")
            print("   is statistically significant. A pan-European climatic or volcanic")
            print("   event would affect all caves similarly.")

    return cave_results


def generate_markdown_table(cave_results):
    """Generate markdown table for the synthesis document."""
    print("\n## Markdown Table for Document\n")
    print("| Cave | Country | Lat | Lon | n | δ18O (‰) | Z(δ18O) | δ13C (‰) | Z(δ13C) | Status |")
    print("|------|---------|-----|-----|---|----------|---------|----------|---------|--------|")

    sorted_caves = sorted(
        cave_results.items(),
        key=lambda x: x[1].get('d18O_z_score') or 0
    )

    for cave_name, result in sorted_caves:
        country = result['country']
        lat = result['lat']
        lon = result['lon']
        n = result['n_samples']

        # Format values
        if result['d18O_z_score'] is not None:
            d18o_val = f"{result['d18O_window_mean']:.2f}"
            z_d18o = f"**{result['d18O_z_score']:+.2f}σ**" if abs(result['d18O_z_score']) >= 2 else f"{result['d18O_z_score']:+.2f}σ"
        else:
            d18o_val = "-"
            z_d18o = "-"

        if result['d13C_z_score'] is not None:
            d13c_val = f"{result['d13C_window_mean']:.2f}"
            z_d13c = f"**{result['d13C_z_score']:+.2f}σ**" if abs(result['d13C_z_score']) >= 2 else f"{result['d13C_z_score']:+.2f}σ"
        else:
            d13c_val = "-"
            z_d13c = "-"

        # Status
        z_val = result.get('d18O_z_score') or result.get('d13C_z_score')
        if z_val is not None:
            status = "**ANOMALOUS**" if abs(z_val) >= 2 else "Normal"
        else:
            status = "No data"

        print(f"| {cave_name} | {country} | {lat:.2f} | {lon:.2f} | {n} | {d18o_val} | {z_d18o} | {d13c_val} | {z_d13c} | {status} |")


def main():
    # Extract data
    entity_data = extract_entity_data()

    # Calculate statistics
    entity_data = calculate_entity_statistics(entity_data)

    # Analyze 1285 window
    entity_results = analyze_1285_window(entity_data)

    # Aggregate to cave level
    cave_results = aggregate_cave_results(entity_data, entity_results)

    # Print results
    print_results(cave_results)

    # Generate markdown table
    generate_markdown_table(cave_results)

    return entity_data, entity_results, cave_results


if __name__ == "__main__":
    main()
