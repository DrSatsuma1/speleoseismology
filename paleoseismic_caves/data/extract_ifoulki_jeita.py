#!/usr/bin/env python3
"""
Extract Ifoulki and Jeita speleothem time series from SISAL v3 database.
Analyze for cross-validation of 1285 and 1394 CE anomalies detected in Basura Cave.

Target entities:
- Jeita-3 (entity 60): 1089-1582 CE - covers medieval period
- IFK1 (entity 118): 806-1956 CE - covers medieval period
- IFK2 (entity 787): 412-2030 CE - covers medieval period
"""

import csv
import os
from collections import defaultdict
import statistics

# Configuration
SISAL_DIR = "/Users/catherine/projects/quake/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv"
TARGET_ENTITIES = {
    60: "Jeita-3",
    118: "IFK1",
    787: "IFK2"
}

# Target event windows (CE years)
EVENTS = {
    "1285": (1280, 1290),  # Basura #1 anomaly
    "1394": (1389, 1399),  # Basura #3 anomaly
    "536_LALIA": (530, 545),  # Late Antique Little Ice Age
}


def load_csv(filename):
    """Load a CSV file and return list of dicts."""
    filepath = os.path.join(SISAL_DIR, filename)
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)


def bp_to_ce(bp_age):
    """Convert BP (Before Present, 1950) to CE year."""
    return 1950 - bp_age


def extract_entity_data():
    """Extract sample data for target entities."""
    print("Loading SISAL v3 data...")

    # Load samples for target entities
    samples = load_csv("sample.csv")
    entity_samples = {}
    sample_to_entity = {}

    for row in samples:
        eid = int(row['entity_id'])
        if eid in TARGET_ENTITIES:
            sid = row['sample_id']
            sample_to_entity[sid] = eid
            if eid not in entity_samples:
                entity_samples[eid] = []
            entity_samples[eid].append(sid)

    print(f"Found {sum(len(v) for v in entity_samples.values())} samples for target entities")

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
    for eid, name in TARGET_ENTITIES.items():
        entity_data[eid] = {
            'name': name,
            'samples': []
        }

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


def calculate_statistics(entity_data):
    """Calculate mean, std, and other statistics for each entity."""
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

        # Calculate resolution (average sample spacing)
        if len(samples) > 1:
            ages = sorted([s['age_ce'] for s in samples])
            gaps = [ages[i+1] - ages[i] for i in range(len(ages)-1)]
            data['stats']['avg_resolution_yr'] = statistics.mean(gaps)
            data['stats']['max_gap_yr'] = max(gaps)

    return entity_data


def analyze_event_windows(entity_data):
    """Analyze specific event windows and calculate Z-scores."""
    results = {}

    for event_name, (start_ce, end_ce) in EVENTS.items():
        results[event_name] = {}

        for eid, data in entity_data.items():
            name = data['name']
            stats = data['stats']

            # Find samples in window
            window_samples = [
                s for s in data['samples']
                if start_ce <= s['age_ce'] <= end_ce
            ]

            if not window_samples:
                results[event_name][name] = {
                    'in_range': False,
                    'reason': f"No samples in {start_ce}-{end_ce} CE window"
                }
                # Check if window is within entity's range at all
                if stats['min_ce'] and stats['max_ce']:
                    if start_ce < stats['min_ce'] or end_ce > stats['max_ce']:
                        results[event_name][name]['reason'] = f"Entity spans {stats['min_ce']:.0f}-{stats['max_ce']:.0f} CE, event outside range"
                continue

            # Calculate window averages
            d18o_window = [s['d18O'] for s in window_samples if s['d18O'] is not None]
            d13c_window = [s['d13C'] for s in window_samples if s['d13C'] is not None]

            result = {
                'in_range': True,
                'n_samples': len(window_samples),
                'samples_in_window': len(d18o_window),
            }

            # Calculate Z-scores for d18O
            if d18o_window and stats['d18O_mean'] and stats['d18O_std']:
                window_mean = statistics.mean(d18o_window)
                z_score = (window_mean - stats['d18O_mean']) / stats['d18O_std']
                result['d18O_window_mean'] = window_mean
                result['d18O_z_score'] = z_score
                result['d18O_overall_mean'] = stats['d18O_mean']
                result['d18O_overall_std'] = stats['d18O_std']

            # Calculate Z-scores for d13C
            if d13c_window and stats['d13C_mean'] and stats['d13C_std']:
                window_mean = statistics.mean(d13c_window)
                z_score = (window_mean - stats['d13C_mean']) / stats['d13C_std']
                result['d13C_window_mean'] = window_mean
                result['d13C_z_score'] = z_score
                result['d13C_overall_mean'] = stats['d13C_mean']
                result['d13C_overall_std'] = stats['d13C_std']

            results[event_name][name] = result

    return results


def print_results(entity_data, event_results):
    """Print formatted results."""
    print("\n" + "="*80)
    print("SISAL v3 EXTRACTION: IFOULKI AND JEITA SPELEOTHEM ANALYSIS")
    print("="*80)

    # Entity summaries
    print("\n## Entity Summary\n")
    print(f"{'Entity':<12} {'Samples':<10} {'Time Span (CE)':<20} {'d18O n':<10} {'d13C n':<10} {'Resolution':<12}")
    print("-"*80)

    for eid, data in entity_data.items():
        stats = data['stats']
        name = data['name']
        time_span = f"{stats['min_ce']:.0f} - {stats['max_ce']:.0f}" if stats['min_ce'] else "N/A"
        res = f"{stats.get('avg_resolution_yr', 0):.1f} yr" if stats.get('avg_resolution_yr') else "N/A"
        print(f"{name:<12} {stats['n_samples']:<10} {time_span:<20} {stats['d18O_n']:<10} {stats['d13C_n']:<10} {res:<12}")

    # Statistics
    print("\n## Isotope Statistics\n")
    print(f"{'Entity':<12} {'d18O mean':<12} {'d18O std':<12} {'d13C mean':<12} {'d13C std':<12}")
    print("-"*60)

    for eid, data in entity_data.items():
        stats = data['stats']
        name = data['name']
        d18o_mean = f"{stats['d18O_mean']:.2f}" if stats['d18O_mean'] else "N/A"
        d18o_std = f"{stats['d18O_std']:.2f}" if stats['d18O_std'] else "N/A"
        d13c_mean = f"{stats['d13C_mean']:.2f}" if stats['d13C_mean'] else "N/A"
        d13c_std = f"{stats['d13C_std']:.2f}" if stats['d13C_std'] else "N/A"
        print(f"{name:<12} {d18o_mean:<12} {d18o_std:<12} {d13c_mean:<12} {d13c_std:<12}")

    # Event analysis
    print("\n## Event Window Analysis\n")

    for event_name, cave_results in event_results.items():
        start, end = EVENTS[event_name]
        print(f"\n### {event_name} ({start}-{end} CE)\n")

        for cave, result in cave_results.items():
            print(f"**{cave}**:")
            if not result['in_range']:
                print(f"  - {result['reason']}")
            else:
                print(f"  - Samples in window: {result['n_samples']}")
                if 'd18O_z_score' in result:
                    z = result['d18O_z_score']
                    sig = "SIGNIFICANT" if abs(z) >= 2 else "moderate" if abs(z) >= 1 else "weak"
                    print(f"  - d18O: {result['d18O_window_mean']:.2f} permil (Z = {z:+.2f} sigma) [{sig}]")
                if 'd13C_z_score' in result:
                    z = result['d13C_z_score']
                    sig = "SIGNIFICANT" if abs(z) >= 2 else "moderate" if abs(z) >= 1 else "weak"
                    print(f"  - d13C: {result['d13C_window_mean']:.2f} permil (Z = {z:+.2f} sigma) [{sig}]")
            print()

    # Summary table for cross-validation
    print("\n## Cross-Validation Summary Table\n")
    print("| Cave | Location | 1285 d18O | 1285 d13C | 1394 d18O | 1394 d13C |")
    print("|------|----------|-----------|-----------|-----------|-----------|")

    locations = {
        "Jeita-3": "Lebanon",
        "IFK1": "Morocco",
        "IFK2": "Morocco"
    }

    for cave in ["Jeita-3", "IFK1", "IFK2"]:
        loc = locations[cave]

        # 1285 results
        r1285 = event_results["1285"].get(cave, {})
        if r1285.get('in_range'):
            d18o_1285 = f"{r1285.get('d18O_z_score', 0):+.2f}σ" if 'd18O_z_score' in r1285 else "N/A"
            d13c_1285 = f"{r1285.get('d13C_z_score', 0):+.2f}σ" if 'd13C_z_score' in r1285 else "N/A"
        else:
            d18o_1285 = "out of range"
            d13c_1285 = "out of range"

        # 1394 results
        r1394 = event_results["1394"].get(cave, {})
        if r1394.get('in_range'):
            d18o_1394 = f"{r1394.get('d18O_z_score', 0):+.2f}σ" if 'd18O_z_score' in r1394 else "N/A"
            d13c_1394 = f"{r1394.get('d13C_z_score', 0):+.2f}σ" if 'd13C_z_score' in r1394 else "N/A"
        else:
            d18o_1394 = "out of range"
            d13c_1394 = "out of range"

        print(f"| {cave} | {loc} | {d18o_1285} | {d13c_1285} | {d18o_1394} | {d13c_1394} |")

    return


def main():
    # Extract data
    entity_data = extract_entity_data()

    # Calculate statistics
    entity_data = calculate_statistics(entity_data)

    # Analyze event windows
    event_results = analyze_event_windows(entity_data)

    # Print results
    print_results(entity_data, event_results)

    return entity_data, event_results


if __name__ == "__main__":
    main()
