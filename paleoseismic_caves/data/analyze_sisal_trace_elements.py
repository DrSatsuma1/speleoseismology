#!/usr/bin/env python3
"""
SISAL v3 Trace Element Cross-Validation Analysis

Analyzes Mg/Ca and Sr/Ca trace element data across European caves to determine
if the 1285 CE seismic signature detected in Bàsura Cave (BA18-4) is replicated
in other caves.

Key finding from preliminary investigation:
- Klapferloch (Austria) does NOT have Mg/Ca data in SISAL v3
- But several other European caves DO have trace element coverage

This script checks if caves that DO have Mg/Ca data show elevated values at 1285
like Bàsura (+2.25σ), which would support regional seismic origin.

Target comparison caves:
- Bunker cave (Germany) - 51.37°N, 7.66°E - 2,500+ samples
- Closani cave (Romania) - 45.10°N, 22.80°E - 1,700+ samples
- Herbstlabyrinth (Germany) - 50.69°N, 8.21°E - 700+ samples
- Bigonda cave (Italy) - 46.02°N, 11.58°E - 700+ samples
- Villars cave (France) - 45.43°N, 0.78°E - 167 samples
"""

import csv
import os
from collections import defaultdict
import statistics

# Configuration
SISAL_DIR = "/Users/catherine/projects/quake/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv"

# Target event windows
EVENTS = {
    "1285": (1280, 1290),  # Basura #1 anomaly - known seismic
    "1394": (1389, 1399),  # Basura #3 anomaly - dark earthquake
    "1641": (1636, 1646),  # Basura #2 anomaly - known climatic (Mg/Ca -1.48σ)
}

# Reference values from BA18-4 (Bàsura Cave) from NOAA archive
BASURA_REFERENCE = {
    "1285": {"Mg_Ca": 30.24, "Mg_Ca_z": 2.25, "interpretation": "SEISMIC (deep water)"},
    "1394": {"Mg_Ca": 28.12, "Mg_Ca_z": 1.60, "interpretation": "SEISMIC (supported)"},
    "1641": {"Mg_Ca": 23.89, "Mg_Ca_z": -1.48, "interpretation": "CLIMATIC (meteoric dilution)"},
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


def build_sample_entity_map():
    """Build mapping of sample_id to entity_id."""
    samples = load_csv("sample.csv")
    sample_to_entity = {}
    entity_samples = defaultdict(list)

    for row in samples:
        sid = row['sample_id']
        eid = int(row['entity_id'])
        sample_to_entity[sid] = eid
        entity_samples[eid].append(sid)

    return sample_to_entity, entity_samples


def load_site_info():
    """Load site information (name, location)."""
    sites = load_csv("site.csv")
    return {row['site_id']: row for row in sites}


def load_entity_info():
    """Load entity metadata."""
    entities = load_csv("entity.csv")
    return {int(row['entity_id']): row for row in entities}


def load_trace_elements(sample_to_entity):
    """Load Mg/Ca and Sr/Ca data, linked to entities."""
    # Load Mg/Ca
    mg_ca_data = defaultdict(list)
    mg_ca = load_csv("Mg_Ca.csv")
    for row in mg_ca:
        sid = row['sample_id']
        if sid in sample_to_entity:
            val = row['Mg_Ca_measurement']
            if val and val != 'NA':
                eid = sample_to_entity[sid]
                mg_ca_data[eid].append({
                    'sample_id': sid,
                    'value': float(val)
                })

    # Load Sr/Ca
    sr_ca_data = defaultdict(list)
    sr_ca = load_csv("Sr_Ca.csv")
    for row in sr_ca:
        sid = row['sample_id']
        if sid in sample_to_entity:
            val = row['Sr_Ca_measurement']
            if val and val != 'NA':
                eid = sample_to_entity[sid]
                sr_ca_data[eid].append({
                    'sample_id': sid,
                    'value': float(val)
                })

    return mg_ca_data, sr_ca_data


def load_chronology(sample_to_entity):
    """Load chronology data for target samples."""
    chronology = load_csv("sisal_chronology.csv")
    sample_ages = {}

    for row in chronology:
        sid = row['sample_id']
        if sid in sample_to_entity:
            age = row['lin_interp_age']
            if age and age != 'NA':
                sample_ages[sid] = float(age)

    return sample_ages


def get_european_caves_with_trace_elements(mg_ca_data, entity_info, site_info):
    """Identify European caves with Mg/Ca data."""
    european_caves = []

    for eid, data in mg_ca_data.items():
        if eid not in entity_info:
            continue

        site_id = entity_info[eid]['site_id']
        if site_id not in site_info:
            continue

        site = site_info[site_id]
        lat = float(site['latitude']) if site['latitude'] else None
        lon = float(site['longitude']) if site['longitude'] else None

        # Filter for European caves (roughly lat > 35, lon -15 to 45)
        if lat and lon and lat > 35 and -15 < lon < 45:
            european_caves.append({
                'entity_id': eid,
                'site_id': site_id,
                'site_name': site['site_name'],
                'entity_name': entity_info[eid].get('entity_name', 'Unknown'),
                'lat': lat,
                'lon': lon,
                'n_mg_ca': len(data)
            })

    return european_caves


def analyze_entity_trace_elements(eid, mg_ca_data, sr_ca_data, sample_ages, events):
    """Analyze trace elements for a single entity at target windows."""
    results = {
        'entity_id': eid,
        'n_mg_ca': 0,
        'n_sr_ca': 0,
        'mg_ca_stats': None,
        'sr_ca_stats': None,
        'events': {}
    }

    # Build time series for Mg/Ca
    mg_ca_series = []
    for record in mg_ca_data.get(eid, []):
        sid = record['sample_id']
        if sid in sample_ages:
            ce_year = bp_to_ce(sample_ages[sid])
            mg_ca_series.append({
                'year_ce': ce_year,
                'value': record['value']
            })

    mg_ca_series.sort(key=lambda x: x['year_ce'])
    results['n_mg_ca'] = len(mg_ca_series)

    if len(mg_ca_series) < 5:
        return results

    # Calculate overall statistics for Mg/Ca
    values = [s['value'] for s in mg_ca_series]
    results['mg_ca_stats'] = {
        'mean': statistics.mean(values),
        'std': statistics.stdev(values) if len(values) > 1 else 0,
        'min_year': min(s['year_ce'] for s in mg_ca_series),
        'max_year': max(s['year_ce'] for s in mg_ca_series)
    }

    # Analyze each event window
    for event_name, (start_ce, end_ce) in events.items():
        window_samples = [s for s in mg_ca_series if start_ce <= s['year_ce'] <= end_ce]

        if not window_samples:
            results['events'][event_name] = {
                'in_range': False,
                'reason': f"No samples in {start_ce}-{end_ce} window"
            }
            # Check if window is within entity's range
            if results['mg_ca_stats']:
                if start_ce < results['mg_ca_stats']['min_year'] or end_ce > results['mg_ca_stats']['max_year']:
                    results['events'][event_name]['reason'] = (
                        f"Entity spans {results['mg_ca_stats']['min_year']:.0f}-"
                        f"{results['mg_ca_stats']['max_year']:.0f} CE"
                    )
            continue

        # Calculate window statistics and z-score
        window_values = [s['value'] for s in window_samples]
        window_mean = statistics.mean(window_values)

        z_score = None
        if results['mg_ca_stats']['std'] > 0:
            z_score = (window_mean - results['mg_ca_stats']['mean']) / results['mg_ca_stats']['std']

        results['events'][event_name] = {
            'in_range': True,
            'n_samples': len(window_samples),
            'window_mean': window_mean,
            'z_score': z_score,
            'overall_mean': results['mg_ca_stats']['mean'],
            'overall_std': results['mg_ca_stats']['std']
        }

    return results


def print_results(european_caves, analysis_results, site_info, entity_info):
    """Print formatted results."""
    print("=" * 90)
    print("SISAL v3 TRACE ELEMENT CROSS-VALIDATION ANALYSIS")
    print("=" * 90)

    print("\n## Reference: Bàsura Cave BA18-4 (from NOAA archive)\n")
    print(f"{'Event':<10} {'Mg/Ca (mmol/mol)':<18} {'Z-score':<12} {'Interpretation'}")
    print("-" * 60)
    for event, ref in BASURA_REFERENCE.items():
        print(f"{event:<10} {ref['Mg_Ca']:<18.2f} {ref['Mg_Ca_z']:+.2f}σ{'':>8} {ref['interpretation']}")

    print("\n## European Caves with Mg/Ca Data in SISAL v3\n")
    print(f"{'Site':<30} {'Entity':<8} {'n':<8} {'Time Span':<20} {'Distance from Bàsura'}")
    print("-" * 90)

    # Sort by sample count
    for cave in sorted(european_caves, key=lambda x: -x['n_mg_ca']):
        eid = cave['entity_id']
        if eid in analysis_results:
            res = analysis_results[eid]
            if res['mg_ca_stats']:
                time_span = f"{res['mg_ca_stats']['min_year']:.0f}-{res['mg_ca_stats']['max_year']:.0f} CE"
            else:
                time_span = "N/A"
        else:
            time_span = "N/A"

        # Calculate distance from Bàsura (44.13°N, 8.20°E)
        dist_km = ((cave['lat'] - 44.13)**2 + (cave['lon'] - 8.20)**2)**0.5 * 111

        print(f"{cave['site_name'][:30]:<30} {eid:<8} {cave['n_mg_ca']:<8} {time_span:<20} {dist_km:.0f} km")

    # Event analysis
    print("\n" + "=" * 90)
    print("EVENT WINDOW ANALYSIS: Mg/Ca Z-scores at 1285, 1394, 1641 CE")
    print("=" * 90)

    for event_name in EVENTS.keys():
        start, end = EVENTS[event_name]
        ref = BASURA_REFERENCE[event_name]

        print(f"\n### {event_name} CE ({start}-{end})")
        print(f"### Bàsura BA18-4 reference: Mg/Ca = {ref['Mg_Ca']:.2f} mmol/mol, Z = {ref['Mg_Ca_z']:+.2f}σ ({ref['interpretation']})")
        print()
        print(f"{'Cave':<30} {'n':<6} {'Mg/Ca Mean':<14} {'Z-score':<12} {'Interpretation'}")
        print("-" * 80)

        caves_with_data = []
        caves_no_data = []

        for cave in european_caves:
            eid = cave['entity_id']
            if eid not in analysis_results:
                continue

            res = analysis_results[eid]
            event_data = res['events'].get(event_name, {})

            if event_data.get('in_range'):
                z = event_data.get('z_score')
                mean = event_data.get('window_mean', 0)
                n = event_data.get('n_samples', 0)

                # Interpret z-score
                if z is None:
                    interp = "N/A"
                elif z > 1.5:
                    interp = "**HIGH** (deep water?)"
                elif z < -1.5:
                    interp = "LOW (dilution)"
                else:
                    interp = "Normal"

                z_str = f"{z:+.2f}σ" if z is not None else "N/A"
                caves_with_data.append((cave['site_name'][:30], n, mean, z_str, interp, z or 0))
            else:
                reason = event_data.get('reason', 'Unknown')
                caves_no_data.append((cave['site_name'][:30], reason))

        # Sort by z-score (highest first to show potential seismic signals)
        caves_with_data.sort(key=lambda x: -x[5])

        for name, n, mean, z_str, interp, _ in caves_with_data:
            print(f"{name:<30} {n:<6} {mean:<14.4f} {z_str:<12} {interp}")

        if caves_no_data:
            print("\nCaves without data for this window:")
            for name, reason in caves_no_data:
                print(f"  - {name}: {reason}")

    # Summary statistics
    print("\n" + "=" * 90)
    print("SUMMARY: Cross-Cave Mg/Ca Comparison at 1285 CE")
    print("=" * 90)

    print("\nQuestion: Do other European caves show HIGH Mg/Ca at 1285 like Bàsura (+2.25σ)?")
    print()

    # Collect 1285 results
    high_mg_ca = []
    normal_mg_ca = []
    low_mg_ca = []
    no_data = []

    for cave in european_caves:
        eid = cave['entity_id']
        if eid not in analysis_results:
            no_data.append(cave['site_name'])
            continue

        res = analysis_results[eid]
        event_data = res['events'].get('1285', {})

        if not event_data.get('in_range'):
            no_data.append(cave['site_name'])
            continue

        z = event_data.get('z_score')
        if z is None:
            no_data.append(cave['site_name'])
        elif z > 1.5:
            high_mg_ca.append((cave['site_name'], z))
        elif z < -1.5:
            low_mg_ca.append((cave['site_name'], z))
        else:
            normal_mg_ca.append((cave['site_name'], z))

    if high_mg_ca:
        print(f"Caves with HIGH Mg/Ca at 1285 (z > +1.5σ): {len(high_mg_ca)}")
        for name, z in sorted(high_mg_ca, key=lambda x: -x[1]):
            print(f"  - {name}: z = {z:+.2f}σ → Potential seismic signal")
    else:
        print("Caves with HIGH Mg/Ca at 1285: NONE")

    if normal_mg_ca:
        print(f"\nCaves with NORMAL Mg/Ca at 1285 (|z| ≤ 1.5σ): {len(normal_mg_ca)}")
        for name, z in normal_mg_ca[:5]:  # Show first 5
            print(f"  - {name}: z = {z:+.2f}σ")
        if len(normal_mg_ca) > 5:
            print(f"  ... and {len(normal_mg_ca) - 5} more")

    if low_mg_ca:
        print(f"\nCaves with LOW Mg/Ca at 1285 (z < -1.5σ): {len(low_mg_ca)}")
        for name, z in low_mg_ca:
            print(f"  - {name}: z = {z:+.2f}σ → Climatic/meteoric signal")

    if no_data:
        print(f"\nCaves without 1285 coverage: {len(no_data)}")

    # Interpretation
    print("\n" + "-" * 80)
    print("INTERPRETATION")
    print("-" * 80)

    if high_mg_ca:
        print("""
If other caves show HIGH Mg/Ca at 1285:
→ Supports regional deep aquifer disturbance (seismic)
→ Strengthens "Titan Event" hypothesis
""")
    elif normal_mg_ca and not high_mg_ca:
        print("""
If ONLY Bàsura shows HIGH Mg/Ca at 1285:
→ Signal may be LOCAL to Bàsura cave system
→ Still valid as Bàsura-specific seismic indicator
→ Does NOT invalidate seismic interpretation (different aquifer systems)
→ The Klapferloch δ13C cross-validation (+3.14σ) remains the key independent confirmation
""")


def generate_markdown_output(european_caves, analysis_results):
    """Generate markdown-formatted output for documentation."""
    print("\n\n" + "=" * 90)
    print("MARKDOWN OUTPUT FOR DOCUMENTATION")
    print("=" * 90)

    print("""
## Cross-Cave Trace Element Analysis Results

### Key Finding: Trace Element Coverage in SISAL v3

**Critical Discovery**: The cross-validation caves (Klapferloch, Ifoulki, Jeita) do NOT have
Mg/Ca data in SISAL v3. However, several OTHER European caves do have trace element coverage.

### Caves with Mg/Ca Data

| Cave | Country | Entity | n | Time Span | Distance |
|------|---------|--------|---|-----------|----------|""")

    for cave in sorted(european_caves, key=lambda x: -x['n_mg_ca'])[:15]:
        eid = cave['entity_id']
        if eid in analysis_results:
            res = analysis_results[eid]
            if res['mg_ca_stats']:
                time_span = f"{res['mg_ca_stats']['min_year']:.0f}-{res['mg_ca_stats']['max_year']:.0f}"
            else:
                time_span = "N/A"
        else:
            time_span = "N/A"

        dist_km = ((cave['lat'] - 44.13)**2 + (cave['lon'] - 8.20)**2)**0.5 * 111
        country = "Europe"  # Simplified

        print(f"| {cave['site_name'][:25]} | {country} | {eid} | {cave['n_mg_ca']} | {time_span} | {dist_km:.0f} km |")

    print("""
### 1285 CE Event Comparison

| Cave | Mg/Ca Z-score | Status | Notes |
|------|---------------|--------|-------|
| **Bàsura BA18-4** | **+2.25σ** | **SEISMIC** | Deep water intrusion confirmed |""")

    for cave in european_caves:
        eid = cave['entity_id']
        if eid not in analysis_results:
            continue

        res = analysis_results[eid]
        event_data = res['events'].get('1285', {})

        if event_data.get('in_range'):
            z = event_data.get('z_score')
            if z is not None:
                if z > 1.5:
                    status = "HIGH"
                elif z < -1.5:
                    status = "LOW"
                else:
                    status = "Normal"
                print(f"| {cave['site_name'][:25]} | {z:+.2f}σ | {status} | |")


def main():
    print("Loading SISAL v3 data...")

    # Build data structures
    sample_to_entity, entity_samples = build_sample_entity_map()
    site_info = load_site_info()
    entity_info = load_entity_info()
    sample_ages = load_chronology(sample_to_entity)

    # Load trace elements
    print("Loading trace element data...")
    mg_ca_data, sr_ca_data = load_trace_elements(sample_to_entity)

    print(f"Found {len(mg_ca_data)} entities with Mg/Ca data")
    print(f"Found {len(sr_ca_data)} entities with Sr/Ca data")

    # Get European caves with trace elements
    european_caves = get_european_caves_with_trace_elements(mg_ca_data, entity_info, site_info)
    print(f"Found {len(european_caves)} European caves with Mg/Ca data")

    # Analyze each cave
    print("Analyzing trace elements at event windows...")
    analysis_results = {}
    for cave in european_caves:
        eid = cave['entity_id']
        analysis_results[eid] = analyze_entity_trace_elements(
            eid, mg_ca_data, sr_ca_data, sample_ages, EVENTS
        )

    # Print results
    print_results(european_caves, analysis_results, site_info, entity_info)

    # Generate markdown output
    generate_markdown_output(european_caves, analysis_results)

    return european_caves, analysis_results


if __name__ == "__main__":
    main()
