#!/usr/bin/env python3
"""
Gejkar Cave Multivariate Seismic Detection Algorithm
=====================================================

Implements the detection algorithm from CAVE_MULTIVARIATE_MODEL.md to:
1. Detect ALL anomalies in Gejkar's 2,400-year record (~400 BCE to 2013 CE)
2. Validate detection of known 1304 Tabriz M7.3 earthquake
3. Evaluate volcanic discrimination (1286 UE6)
4. Discover new events (e.g., 1284.88 CE signal)

Algorithm (from CAVE_MULTIVARIATE_MODEL.md):
- HIGH confidence: (|d18O_z| > 2 AND |Mg/Ca_z| > 1.5 AND |U/Ca_z| > 2) OR (|U/Ca_z| > 3)
- MEDIUM confidence: |d18O_z| > 2 AND coupled d13C response
- LOW confidence: single proxy only
"""

import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict

# Paths
DATA_DIR = Path("/Users/catherine/projects/quake/paleoseismic_caves/data/multivariate")
OUTPUT_DIR = Path("/Users/catherine/projects/quake/paleoseismic_caves/regions/turkey")

# Known events for validation
KNOWN_EVENTS = {
    "1304_Tabriz_M7.3": {
        "year": 1304,
        "window": (1303, 1318),
        "type": "SEISMIC",
        "expected_detection": True,
        "expected_confidence": "HIGH",
        "distance_km": 273,
        "notes": "Historical M7.3 earthquake, U/Ca z=+6.87σ expected"
    },
    "1286_UE6_eruption": {
        "year": 1286,
        "window": (1286, 1292),
        "type": "VOLCANIC",
        "expected_detection": False,
        "expected_confidence": None,
        "notes": "Should NOT be detected - volcanic signal has no U/Ca spike"
    },
    "1285_Italy_CVSE": {
        "year": 1285,
        "window": (1282, 1288),
        "type": "UNKNOWN",
        "expected_detection": None,
        "expected_confidence": None,
        "distance_km": 884,
        "notes": "Cross-continental test - U/Ca z=+2.80σ reported at 1284.88 CE"
    }
}

# Major volcanic eruptions from eVolv2k for false positive checking
VOLCANIC_EVENTS = [
    {"year": 1257, "name": "Samalas", "vssi": 59.42},
    {"year": 1286, "name": "UE6 (Unknown)", "vssi": 6.08},
    {"year": 1230, "name": "Unknown", "vssi": 23.78},
    {"year": 1108, "name": "Unknown", "vssi": 19.16},
    {"year": 939, "name": "Eldgjá", "vssi": 36.08},
    {"year": 853, "name": "Churchill", "vssi": 27.0},
    {"year": 536, "name": "Ilopango?", "vssi": 46.7},
    {"year": 540, "name": "Unknown", "vssi": 23.7},
    {"year": 79, "name": "Vesuvius", "vssi": 3.2},
]


def load_gejkar_data():
    """Load Gejkar multiproxy data and calculate z-scores."""
    df = pd.read_csv(DATA_DIR / "gejkar_multiproxy.csv")

    # Sort by year
    df = df.sort_values('year_CE').reset_index(drop=True)

    # Define proxy columns
    proxy_cols = ['d18O_measurement', 'd13C_measurement', 'Mg_Ca_measurement',
                  'Sr_Ca_measurement', 'U_Ca_measurement', 'P_Ca_measurement']

    # Calculate z-scores for each proxy
    stats = {}
    for col in proxy_cols:
        valid = df[col].dropna()
        if len(valid) >= 10:
            mean = valid.mean()
            std = valid.std()
            stats[col] = {'mean': mean, 'std': std, 'n': len(valid)}
            z_col = col.replace('_measurement', '_z')
            df[z_col] = (df[col] - mean) / std
        else:
            stats[col] = {'mean': np.nan, 'std': np.nan, 'n': len(valid)}

    print("=== Gejkar Cave Data Statistics ===")
    print(f"Total samples: {len(df)}")
    print(f"Time span: {df['year_CE'].min():.0f} to {df['year_CE'].max():.0f} CE")
    print(f"Average resolution: {(df['year_CE'].max() - df['year_CE'].min()) / len(df):.1f} years/sample")
    print()
    print("Proxy Statistics:")
    for col, s in stats.items():
        short_name = col.replace('_measurement', '')
        if not np.isnan(s['mean']):
            print(f"  {short_name}: n={s['n']}, μ={s['mean']:.4f}, σ={s['std']:.4f}")
    print()

    return df, stats


def classify_confidence(row):
    """
    Apply detection algorithm from CAVE_MULTIVARIATE_MODEL.md

    Returns: (confidence_level, classification, reasons)
    """
    d18O_z = row.get('d18O_z', np.nan)
    d13C_z = row.get('d13C_z', np.nan)
    Mg_Ca_z = row.get('Mg_Ca_z', np.nan)
    U_Ca_z = row.get('U_Ca_z', np.nan)
    Sr_Ca_z = row.get('Sr_Ca_z', np.nan)

    reasons = []

    # Check for NaN values in critical proxies
    has_isotopes = not (pd.isna(d18O_z) or pd.isna(d13C_z))
    has_trace = not pd.isna(U_Ca_z)
    has_mgca = not pd.isna(Mg_Ca_z)

    # Rule 1: Multi-proxy confirmed (HIGH)
    if has_isotopes and has_trace and has_mgca:
        if abs(d18O_z) > 2 and abs(Mg_Ca_z) > 1.5 and abs(U_Ca_z) > 2:
            reasons.append(f"Multi-proxy: δ18O z={d18O_z:+.2f}, Mg/Ca z={Mg_Ca_z:+.2f}, U/Ca z={U_Ca_z:+.2f}")
            return ("HIGH", "SEISMIC_CONFIRMED", reasons)

    # Rule 2: U/Ca alone diagnostic in arid settings (HIGH)
    if has_trace and abs(U_Ca_z) > 3:
        reasons.append(f"U/Ca diagnostic: z={U_Ca_z:+.2f} (>3σ)")
        return ("HIGH", "SEISMIC_UCA", reasons)

    # Rule 3: Isotope-confirmed (MEDIUM)
    if has_isotopes:
        # Coupled response = both isotopes anomalous in same direction
        if abs(d18O_z) > 2:
            if abs(d13C_z) > 1.5 and np.sign(d18O_z) == np.sign(d13C_z):
                reasons.append(f"Coupled isotopes: δ18O z={d18O_z:+.2f}, δ13C z={d13C_z:+.2f}")
                return ("MEDIUM", "ISOTOPE_COUPLED", reasons)
            elif abs(d13C_z) < 1:
                # Decoupled - may be hydrological
                reasons.append(f"Decoupled: δ18O z={d18O_z:+.2f}, δ13C z={d13C_z:+.2f}")
                return ("LOW", "HYDROLOGICAL", reasons)

    # Rule 4: Single proxy only (LOW)
    max_z = 0
    max_proxy = None
    for proxy, z_val in [('d18O', d18O_z), ('d13C', d13C_z), ('Mg_Ca', Mg_Ca_z),
                          ('U_Ca', U_Ca_z), ('Sr_Ca', Sr_Ca_z)]:
        if not pd.isna(z_val) and abs(z_val) > abs(max_z):
            max_z = z_val
            max_proxy = proxy

    if max_proxy and abs(max_z) > 2:
        reasons.append(f"Single proxy: {max_proxy} z={max_z:+.2f}")
        return ("LOW", "SINGLE_PROXY", reasons)

    return (None, None, [])


def detect_anomalies(df, min_z=2.0):
    """
    Scan full timeseries for anomalies meeting detection criteria.
    Returns list of detected events.
    """
    detections = []

    for idx, row in df.iterrows():
        confidence, classification, reasons = classify_confidence(row)

        if confidence is not None:
            detections.append({
                'year_CE': row['year_CE'],
                'depth': row['depth_sample'],
                'confidence': confidence,
                'classification': classification,
                'reasons': '; '.join(reasons),
                'd18O_z': row.get('d18O_z', np.nan),
                'd13C_z': row.get('d13C_z', np.nan),
                'Mg_Ca_z': row.get('Mg_Ca_z', np.nan),
                'U_Ca_z': row.get('U_Ca_z', np.nan),
                'Sr_Ca_z': row.get('Sr_Ca_z', np.nan),
            })

    return pd.DataFrame(detections)


def cluster_events(detections_df, gap_years=10):
    """
    Cluster adjacent detections into discrete events.
    Events separated by > gap_years are considered distinct.
    """
    if len(detections_df) == 0:
        return []

    detections_df = detections_df.sort_values('year_CE').reset_index(drop=True)

    events = []
    current_event = {
        'start_year': detections_df.iloc[0]['year_CE'],
        'end_year': detections_df.iloc[0]['year_CE'],
        'peak_year': detections_df.iloc[0]['year_CE'],
        'max_confidence': detections_df.iloc[0]['confidence'],
        'samples': [detections_df.iloc[0].to_dict()],
        'classifications': [detections_df.iloc[0]['classification']],
    }

    # Find peak based on maximum absolute z-score
    max_z = 0
    for col in ['d18O_z', 'd13C_z', 'Mg_Ca_z', 'U_Ca_z']:
        z = detections_df.iloc[0].get(col, 0)
        if not pd.isna(z) and abs(z) > abs(max_z):
            max_z = z
    current_event['peak_z'] = max_z
    current_event['peak_proxy'] = 'U_Ca' if not pd.isna(detections_df.iloc[0].get('U_Ca_z')) else 'd18O'

    for i in range(1, len(detections_df)):
        row = detections_df.iloc[i]

        if row['year_CE'] - current_event['end_year'] <= gap_years:
            # Same event
            current_event['end_year'] = row['year_CE']
            current_event['samples'].append(row.to_dict())
            current_event['classifications'].append(row['classification'])

            # Update peak if this sample has higher z
            for col in ['d18O_z', 'd13C_z', 'Mg_Ca_z', 'U_Ca_z']:
                z = row.get(col, 0)
                if not pd.isna(z) and abs(z) > abs(current_event['peak_z']):
                    current_event['peak_z'] = z
                    current_event['peak_year'] = row['year_CE']
                    current_event['peak_proxy'] = col.replace('_z', '')

            # Update confidence (take highest)
            conf_order = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
            if conf_order.get(row['confidence'], 0) > conf_order.get(current_event['max_confidence'], 0):
                current_event['max_confidence'] = row['confidence']
        else:
            # New event
            events.append(current_event)
            current_event = {
                'start_year': row['year_CE'],
                'end_year': row['year_CE'],
                'peak_year': row['year_CE'],
                'max_confidence': row['confidence'],
                'samples': [row.to_dict()],
                'classifications': [row['classification']],
                'peak_z': 0,
                'peak_proxy': 'd18O',
            }
            for col in ['d18O_z', 'd13C_z', 'Mg_Ca_z', 'U_Ca_z']:
                z = row.get(col, 0)
                if not pd.isna(z) and abs(z) > abs(current_event['peak_z']):
                    current_event['peak_z'] = z
                    current_event['peak_proxy'] = col.replace('_z', '')

    events.append(current_event)

    # Add duration and dominant classification
    for event in events:
        event['duration'] = event['end_year'] - event['start_year']
        event['n_samples'] = len(event['samples'])
        # Dominant classification
        class_counts = defaultdict(int)
        for c in event['classifications']:
            class_counts[c] += 1
        event['dominant_classification'] = max(class_counts, key=class_counts.get)

    return events


def check_volcanic_association(year, window=5):
    """Check if a year falls within window of known volcanic event."""
    for vol in VOLCANIC_EVENTS:
        if abs(year - vol['year']) <= window:
            return vol
    return None


def validate_against_known(events):
    """Check if known events were correctly detected/rejected."""
    results = {}

    for event_name, expected in KNOWN_EVENTS.items():
        window_start, window_end = expected['window']

        # Find any detections in this window
        matches = [e for e in events
                   if (e['start_year'] <= window_end and e['end_year'] >= window_start)]

        detected = len(matches) > 0
        max_confidence = max([m['max_confidence'] for m in matches], default=None) if matches else None

        # Evaluate correctness
        if expected['expected_detection'] is True:
            correct = detected
            status = "PASS" if correct else "FAIL"
        elif expected['expected_detection'] is False:
            correct = not detected
            status = "PASS" if correct else "FAIL"
        else:
            correct = None
            status = "INFO"

        results[event_name] = {
            'expected_detection': expected['expected_detection'],
            'actual_detection': detected,
            'expected_confidence': expected['expected_confidence'],
            'actual_confidence': max_confidence,
            'correct': correct,
            'status': status,
            'matches': matches,
            'notes': expected.get('notes', ''),
        }

    return results


def calculate_statistics(events, df):
    """Calculate detection statistics."""
    time_span = df['year_CE'].max() - df['year_CE'].min()

    stats = {
        'total_events': len(events),
        'time_span_years': time_span,
        'events_per_century': len(events) / (time_span / 100) if time_span > 0 else 0,
        'high_confidence': len([e for e in events if e['max_confidence'] == 'HIGH']),
        'medium_confidence': len([e for e in events if e['max_confidence'] == 'MEDIUM']),
        'low_confidence': len([e for e in events if e['max_confidence'] == 'LOW']),
    }

    # Classification breakdown
    by_class = defaultdict(int)
    for e in events:
        by_class[e['dominant_classification']] += 1
    stats['by_classification'] = dict(by_class)

    return stats


def generate_report(df, events, validation_results, stats):
    """Generate markdown report."""

    report = []
    report.append("# Gejkar Cave Multivariate Detection Algorithm Validation")
    report.append("")
    report.append(f"**Date**: {pd.Timestamp.now().strftime('%Y-%m-%d')}")
    report.append(f"**Algorithm**: CAVE_MULTIVARIATE_MODEL.md detection criteria")
    report.append("")

    # Summary
    report.append("## Summary")
    report.append("")
    report.append(f"- **Time span analyzed**: {df['year_CE'].min():.0f} to {df['year_CE'].max():.0f} CE ({stats['time_span_years']:.0f} years)")
    report.append(f"- **Total samples**: {len(df)}")
    report.append(f"- **Events detected**: {stats['total_events']}")
    report.append(f"- **Detection rate**: {stats['events_per_century']:.1f} events/century")
    report.append("")

    # Confidence breakdown
    report.append("### Confidence Distribution")
    report.append("")
    report.append(f"- HIGH: {stats['high_confidence']} events")
    report.append(f"- MEDIUM: {stats['medium_confidence']} events")
    report.append(f"- LOW: {stats['low_confidence']} events")
    report.append("")

    # Classification breakdown
    report.append("### Classification Distribution")
    report.append("")
    for cls, count in stats['by_classification'].items():
        report.append(f"- {cls}: {count} events")
    report.append("")

    # Validation results
    report.append("## Known Event Validation")
    report.append("")
    report.append("| Event | Expected | Detected | Confidence | Status |")
    report.append("|-------|----------|----------|------------|--------|")

    for event_name, result in validation_results.items():
        expected = "YES" if result['expected_detection'] else "NO" if result['expected_detection'] is False else "?"
        detected = "YES" if result['actual_detection'] else "NO"
        confidence = result['actual_confidence'] or "-"
        status = result['status']
        report.append(f"| {event_name} | {expected} | {detected} | {confidence} | {status} |")
    report.append("")

    # Detailed validation notes
    report.append("### Validation Details")
    report.append("")
    for event_name, result in validation_results.items():
        report.append(f"**{event_name}**:")
        report.append(f"- Expected: {'Detect' if result['expected_detection'] else 'Reject' if result['expected_detection'] is False else 'Unknown'}")
        report.append(f"- Result: {'Detected' if result['actual_detection'] else 'Not detected'}")
        if result['matches']:
            for m in result['matches']:
                report.append(f"  - Window: {m['start_year']:.0f}-{m['end_year']:.0f} CE, Peak z={m['peak_z']:+.2f} ({m['peak_proxy']})")
        report.append(f"- Notes: {result['notes']}")
        report.append("")

    # Full event catalog
    report.append("## Full Event Catalog")
    report.append("")
    report.append("All detected events sorted by confidence and peak z-score:")
    report.append("")
    report.append("| # | Year (CE) | Duration | Confidence | Classification | Peak Z | Peak Proxy | Volcanic? |")
    report.append("|---|-----------|----------|------------|----------------|--------|------------|-----------|")

    # Sort by confidence (HIGH first), then by absolute peak z
    conf_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    sorted_events = sorted(events, key=lambda e: (conf_order.get(e['max_confidence'], 3), -abs(e['peak_z'])))

    for i, event in enumerate(sorted_events, 1):
        year_str = f"{event['start_year']:.0f}" if event['duration'] == 0 else f"{event['start_year']:.0f}-{event['end_year']:.0f}"
        duration = f"{event['duration']:.0f} yr" if event['duration'] > 0 else "point"
        volcanic = check_volcanic_association(event['peak_year'])
        vol_str = volcanic['name'] if volcanic else "-"

        report.append(f"| {i} | {year_str} | {duration} | {event['max_confidence']} | {event['dominant_classification']} | {event['peak_z']:+.2f}σ | {event['peak_proxy']} | {vol_str} |")

    report.append("")

    # HIGH confidence events detail
    high_events = [e for e in events if e['max_confidence'] == 'HIGH']
    if high_events:
        report.append("## HIGH Confidence Events (Detailed)")
        report.append("")
        for event in sorted(high_events, key=lambda e: e['peak_year']):
            report.append(f"### ~{event['peak_year']:.0f} CE")
            report.append("")
            report.append(f"- **Window**: {event['start_year']:.0f} - {event['end_year']:.0f} CE ({event['duration']:.0f} years)")
            report.append(f"- **Peak**: {event['peak_z']:+.2f}σ in {event['peak_proxy']}")
            report.append(f"- **Classification**: {event['dominant_classification']}")
            report.append(f"- **Samples**: {event['n_samples']}")

            # Show all proxy values at peak
            peak_sample = [s for s in event['samples'] if s['year_CE'] == event['peak_year']]
            if peak_sample:
                ps = peak_sample[0]
                report.append(f"- **Proxy values at peak**:")
                for proxy in ['d18O_z', 'd13C_z', 'Mg_Ca_z', 'U_Ca_z', 'Sr_Ca_z']:
                    val = ps.get(proxy, np.nan)
                    if not pd.isna(val):
                        report.append(f"  - {proxy.replace('_z', '')}: {val:+.2f}σ")

            # Check volcanic association
            volcanic = check_volcanic_association(event['peak_year'])
            if volcanic:
                report.append(f"- **Volcanic association**: {volcanic['name']} ({volcanic['year']} CE, VSSI={volcanic['vssi']} Tg S)")
            else:
                report.append("- **Volcanic association**: None within ±5 years")

            report.append("")

    # Conclusions
    report.append("## Conclusions")
    report.append("")

    # Check validation pass/fail
    passes = sum(1 for r in validation_results.values() if r['correct'] is True)
    fails = sum(1 for r in validation_results.values() if r['correct'] is False)

    if fails == 0:
        report.append(f"**Algorithm validated**: {passes}/{passes + fails} known event tests passed.")
    else:
        report.append(f"**Validation issues**: {fails} test(s) failed. Review algorithm criteria.")

    report.append("")
    report.append(f"- Detection rate ({stats['events_per_century']:.1f}/century) is {'reasonable' if stats['events_per_century'] < 5 else 'high - may indicate false positives'}")
    report.append(f"- HIGH confidence events: {stats['high_confidence']} (should be rare, significant)")

    return "\n".join(report)


def main():
    print("=" * 80)
    print("GEJKAR CAVE MULTIVARIATE DETECTION ALGORITHM TEST")
    print("=" * 80)
    print()

    # Step 1: Load data
    df, stats = load_gejkar_data()

    # Step 2: Detect anomalies
    print("=== Running Detection Algorithm ===")
    detections = detect_anomalies(df)
    print(f"Raw detections: {len(detections)} samples flagged")
    print()

    # Step 3: Cluster into events
    print("=== Clustering Detections into Events ===")
    events = cluster_events(detections)
    print(f"Distinct events: {len(events)}")
    print()

    # Step 4: Validate against known events
    print("=== Validating Against Known Events ===")
    validation_results = validate_against_known(events)

    for event_name, result in validation_results.items():
        status_symbol = "✓" if result['correct'] else "✗" if result['correct'] is False else "?"
        print(f"{status_symbol} {event_name}: {result['status']}")
        if result['matches']:
            for m in result['matches']:
                print(f"    → Detected {m['start_year']:.0f}-{m['end_year']:.0f} CE, peak z={m['peak_z']:+.2f} ({m['peak_proxy']})")
    print()

    # Step 5: Calculate statistics
    calc_stats = calculate_statistics(events, df)
    print("=== Detection Statistics ===")
    print(f"Total events: {calc_stats['total_events']}")
    print(f"Events per century: {calc_stats['events_per_century']:.1f}")
    print(f"By confidence: HIGH={calc_stats['high_confidence']}, MEDIUM={calc_stats['medium_confidence']}, LOW={calc_stats['low_confidence']}")
    print()

    # Step 6: Generate and save report
    report = generate_report(df, events, validation_results, calc_stats)

    output_file = OUTPUT_DIR / "GEJKAR_MULTIPROXY_VALIDATION.md"
    with open(output_file, 'w') as f:
        f.write(report)
    print(f"Report saved to: {output_file}")
    print()

    # Print HIGH confidence events
    high_events = [e for e in events if e['max_confidence'] == 'HIGH']
    if high_events:
        print("=== HIGH CONFIDENCE EVENTS ===")
        for e in sorted(high_events, key=lambda x: x['peak_year']):
            volcanic = check_volcanic_association(e['peak_year'])
            vol_note = f" [VOLCANIC: {volcanic['name']}]" if volcanic else ""
            print(f"~{e['peak_year']:.0f} CE: z={e['peak_z']:+.2f} ({e['peak_proxy']}), {e['dominant_classification']}{vol_note}")

    return events, validation_results


if __name__ == "__main__":
    events, validation = main()
