#!/usr/bin/env python3
"""
Extract Sofular and Tamboril data for blind prediction test.
Uses only standard library - no pandas required.
"""

import csv
from pathlib import Path
import statistics

# Paths
SISAL_DIR = Path('/Users/catherine/projects/quake/paleoseismic_caves/data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv')
OUTPUT_DIR = Path('/Users/catherine/projects/quake/paleoseismic_caves/data')

# Target entities
SOFULAR_ENTITY = '305'   # SO-1 (Turkey, NAF)
TAMBORIL_ENTITY = '97'   # TM0 (Brazil, 489-1948 CE) - historical coverage!

def safe_float(val):
    """Convert to float, return None for NA/empty."""
    if val in ('NA', '', None, 'nan', 'NaN'):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None

def load_csv(filename):
    """Load CSV file as list of dicts."""
    with open(SISAL_DIR / filename, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

def main():
    print("Loading SISAL data...")

    samples = load_csv('sample.csv')
    print(f"  Loaded {len(samples)} samples")

    # Get sample IDs for target entities
    sofular_samples = set(s['sample_id'] for s in samples if s['entity_id'] == SOFULAR_ENTITY)
    tamboril_samples = set(s['sample_id'] for s in samples if s['entity_id'] == TAMBORIL_ENTITY)

    print(f"  Sofular (Entity {SOFULAR_ENTITY}) samples: {len(sofular_samples)}")
    print(f"  Tamboril (Entity {TAMBORIL_ENTITY}) samples: {len(tamboril_samples)}")

    # Load d18O data
    d18O_data = load_csv('d18O.csv')
    d18O_map = {r['sample_id']: safe_float(r['d18O_measurement']) for r in d18O_data}
    print(f"  Loaded {len(d18O_data)} d18O records")

    # Load d13C data
    d13C_data = load_csv('d13C.csv')
    d13C_map = {r['sample_id']: safe_float(r['d13C_measurement']) for r in d13C_data}
    print(f"  Loaded {len(d13C_data)} d13C records")

    # Load chronology - try multiple age columns in order of preference
    # Bchron_age is most common for modern caves like Sofular
    chron_data = load_csv('sisal_chronology.csv')
    chron_map = {}
    for r in chron_data:
        sample_id = r['sample_id']
        # Try age columns in order: Bchron, Bacon, lin_interp, StalAge
        age = (safe_float(r.get('Bchron_age')) or
               safe_float(r.get('Bacon_age')) or
               safe_float(r.get('lin_interp_age')) or
               safe_float(r.get('StalAge_age')))
        if age is not None:
            chron_map[sample_id] = age
    print(f"  Loaded {len(chron_map)} chronology records")

    # Process each cave
    for entity_id, entity_samples, name, time_filter in [
        (SOFULAR_ENTITY, sofular_samples, "Sofular", (-1000, 1900)),
        (TAMBORIL_ENTITY, tamboril_samples, "Tamboril", (None, None))  # No filter for Tamboril
    ]:
        print(f"\n=== {name} (Entity {entity_id}) ===")

        # Build dataset
        data = []
        for sample_id in entity_samples:
            d18O = d18O_map.get(sample_id)
            age_bp = chron_map.get(sample_id)

            if d18O is None or age_bp is None:
                continue

            age_ce = 1950 - age_bp
            d13C = d13C_map.get(sample_id)

            data.append({
                'sample_id': sample_id,
                'age_bp': age_bp,
                'age_ce': age_ce,
                'd18O': d18O,
                'd13C': d13C
            })

        print(f"  Records with d18O + age: {len(data)}")

        if len(data) == 0:
            print("  ⚠️ No data found!")
            continue

        # Sort by age
        data.sort(key=lambda x: x['age_ce'])

        # Time filter if specified
        min_t, max_t = time_filter
        if min_t is not None:
            data = [d for d in data if d['age_ce'] >= min_t]
        if max_t is not None:
            data = [d for d in data if d['age_ce'] <= max_t]

        if time_filter != (None, None):
            print(f"  After time filter ({min_t} - {max_t} CE): {len(data)}")

        if len(data) == 0:
            print("  ⚠️ No data after filter!")
            continue

        # Calculate z-scores
        d18O_values = [d['d18O'] for d in data]
        mean_d18O = statistics.mean(d18O_values)
        std_d18O = statistics.stdev(d18O_values) if len(d18O_values) > 1 else 1

        print(f"  d18O mean: {mean_d18O:.2f}, std: {std_d18O:.2f}")
        print(f"  Age range: {data[0]['age_ce']:.0f} - {data[-1]['age_ce']:.0f} CE")

        # Calculate d13C stats if available
        d13C_values = [d['d13C'] for d in data if d['d13C'] is not None]
        mean_d13C = statistics.mean(d13C_values) if len(d13C_values) > 1 else None
        std_d13C = statistics.stdev(d13C_values) if len(d13C_values) > 1 else None

        if mean_d13C:
            print(f"  d13C mean: {mean_d13C:.2f}, std: {std_d13C:.2f}")
            print(f"  d13C coverage: {len(d13C_values)}/{len(data)} ({100*len(d13C_values)/len(data):.0f}%)")

        for d in data:
            d['d18O_z'] = (d['d18O'] - mean_d18O) / std_d18O
            if d['d13C'] is not None and std_d13C:
                d['d13C_z'] = (d['d13C'] - mean_d13C) / std_d13C
            else:
                d['d13C_z'] = None

        # Save to CSV
        if name == "Sofular":
            output_path = OUTPUT_DIR / 'sofular' / 'sofular_raw_1000bce_1900ce.csv'
        else:
            output_path = OUTPUT_DIR / 'brazil' / 'tamboril_raw.csv'

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['sample_id', 'age_bp', 'age_ce', 'd18O', 'd18O_z', 'd13C', 'd13C_z'])
            for d in data:
                writer.writerow([
                    d['sample_id'],
                    f"{d['age_bp']:.2f}",
                    f"{d['age_ce']:.2f}",
                    f"{d['d18O']:.3f}",
                    f"{d['d18O_z']:.3f}",
                    f"{d['d13C']:.3f}" if d['d13C'] else '',
                    f"{d['d13C_z']:.3f}" if d.get('d13C_z') else ''
                ])

        print(f"  Saved to: {output_path}")

        # Detect anomalies
        anomalies = [d for d in data if abs(d['d18O_z']) > 2.0]
        print(f"\n  Anomalies (|z| > 2.0): {len(anomalies)}")

        # Show top 20 by |z|
        anomalies.sort(key=lambda x: abs(x['d18O_z']), reverse=True)
        print("  Top 20 by |z|:")
        for d in anomalies[:20]:
            d13c_str = f", d13C_z={d['d13C_z']:.2f}" if d.get('d13C_z') else ""
            print(f"    {d['age_ce']:.0f} CE: d18O={d['d18O']:.2f}, z={d['d18O_z']:.2f}{d13c_str}")

    print("\n=== EXTRACTION COMPLETE ===")

if __name__ == '__main__':
    main()
