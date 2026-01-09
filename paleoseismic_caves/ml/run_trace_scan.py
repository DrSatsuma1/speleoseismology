#!/usr/bin/env python3
"""
Run Global Trace Element Anomaly Scan

Executes the full ML pipeline for Ba/Ca and U/Ca analysis:
1. Load all trace element data from SISAL v3
2. Run PELT change point detection on each proxy
3. Find coincident multi-proxy anomalies
4. Correlate with earthquake and volcanic catalogs
5. Output results and discovered patterns

Usage:
    python run_trace_scan.py [--min-year 0] [--max-year 2000] [--penalty 10]
"""

import argparse
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

from sisal_loader import SISALLoader
from global_scan import GlobalScanner
from proxy_correlation import ProxyCorrelator


def run_trace_element_scan(min_year: int = None,
                            max_year: int = None,
                            penalty: float = 10.0,
                            min_samples: int = 10,
                            output_dir: str = None) -> dict:
    """
    Run complete trace element anomaly detection pipeline.

    Args:
        min_year: Filter anomalies to this minimum year (CE)
        max_year: Filter anomalies to this maximum year (CE)
        penalty: PELT penalty parameter (higher = fewer change points)
        min_samples: Minimum samples per entity to analyze
        output_dir: Directory for output files

    Returns:
        Dict with all results
    """
    if output_dir is None:
        output_dir = Path(__file__).parent / "outputs"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    print("=" * 70)
    print("GLOBAL TRACE ELEMENT ANOMALY SCAN")
    print("=" * 70)
    print(f"Time range: {min_year or 'all'} - {max_year or 'all'} CE")
    print(f"PELT penalty: {penalty}")
    print(f"Min samples: {min_samples}")
    print()

    # Step 1: Load trace element data
    print("=" * 70)
    print("STEP 1: Loading trace element data from SISAL v3")
    print("=" * 70)

    loader = SISALLoader()
    proxies = ['Ba_Ca', 'U_Ca', 'Mg_Ca', 'Sr_Ca']

    df = loader.load_trace_elements(proxies)
    entities = loader.get_entity_trace_timeseries(df, proxies, min_samples=min_samples)

    print(f"\nLoaded {len(entities)} entities with trace element data")

    # Step 2: Run PELT change point detection
    print("\n" + "=" * 70)
    print("STEP 2: Running PELT change point detection")
    print("=" * 70)

    scanner = GlobalScanner(penalty=penalty, min_size=3)
    anomalies = scanner.scan_all_proxies(
        entities,
        proxies=proxies,
        min_year=min_year,
        max_year=max_year,
        min_shift=1.0  # Minimum 1 sigma shift
    )

    if len(anomalies) == 0:
        print("No anomalies detected!")
        return {'anomalies': pd.DataFrame(), 'clusters': pd.DataFrame(), 'stats': {}}

    # Save raw anomalies
    anomaly_path = output_dir / "trace_element_anomalies.csv"
    anomalies.to_csv(anomaly_path, index=False)
    print(f"\nSaved {len(anomalies)} anomalies to {anomaly_path}")

    # Step 3: Find coincident anomalies and correlate
    print("\n" + "=" * 70)
    print("STEP 3: Multi-proxy correlation analysis")
    print("=" * 70)

    correlator = ProxyCorrelator(window_years=10)
    correlation_results = correlator.analyze_all(anomalies)

    clusters = correlation_results['clusters']
    if len(clusters) > 0:
        cluster_path = output_dir / "trace_element_clusters.csv"
        clusters.to_csv(cluster_path, index=False)
        print(f"\nSaved {len(clusters)} clusters to {cluster_path}")

    # Step 4: Summary report
    print("\n" + "=" * 70)
    print("STEP 4: Results Summary")
    print("=" * 70)

    # Proxy-level statistics
    print("\n### Anomalies by Proxy ###")
    proxy_counts = anomalies.groupby('proxy').size().sort_values(ascending=False)
    for proxy, count in proxy_counts.items():
        print(f"  {proxy}: {count} change points")

    # Multi-proxy events
    if len(clusters) > 0:
        print("\n### Multi-Proxy Events (n_proxies >= 2) ###")
        multi = clusters[clusters['n_proxies'] >= 2].copy()
        if len(multi) > 0:
            print(multi[['site_name', 'year_ce', 'proxies', 'n_proxies', 'max_magnitude']].head(20).to_string(index=False))
        else:
            print("  None found")

    # Top anomalies by magnitude
    print("\n### Top 20 Anomalies by Magnitude ###")
    top_cols = ['site_name', 'entity_name', 'proxy', 'year_ce', 'shift_magnitude']
    available = [c for c in top_cols if c in anomalies.columns]
    print(anomalies[available].head(20).to_string(index=False))

    # Time distribution
    print("\n### Anomalies by Century ###")
    anomalies['century'] = (anomalies['year_ce'] // 100).astype(int) * 100
    century_counts = anomalies.groupby('century').size().sort_values(ascending=False)
    print(century_counts.head(10))

    # Geographic distribution
    print("\n### Anomalies by Region ###")
    anomalies['region'] = pd.cut(
        anomalies['lat'],
        bins=[-90, -30, 0, 30, 60, 90],
        labels=['S Polar', 'S Temperate', 'Tropics', 'N Temperate', 'N Polar']
    )
    print(anomalies.groupby('region').size())

    # Generate final statistics
    stats = {
        'total_anomalies': len(anomalies),
        'entities_with_anomalies': anomalies['entity_id'].nunique(),
        'total_clusters': len(clusters) if len(clusters) > 0 else 0,
        'multi_proxy_clusters': int((clusters['n_proxies'] >= 2).sum()) if len(clusters) > 0 else 0,
        'by_proxy': proxy_counts.to_dict(),
        'run_timestamp': datetime.now().isoformat(),
        'parameters': {
            'min_year': min_year,
            'max_year': max_year,
            'penalty': penalty,
            'min_samples': min_samples
        }
    }

    # Save stats
    stats_path = output_dir / "trace_scan_stats.txt"
    with open(stats_path, 'w') as f:
        f.write("TRACE ELEMENT SCAN STATISTICS\n")
        f.write("=" * 50 + "\n\n")
        for key, value in stats.items():
            f.write(f"{key}: {value}\n")

    print(f"\nSaved statistics to {stats_path}")

    print("\n" + "=" * 70)
    print("SCAN COMPLETE")
    print("=" * 70)
    print(f"  Total anomalies: {stats['total_anomalies']}")
    print(f"  Entities analyzed: {len(entities)}")
    print(f"  Multi-proxy clusters: {stats['multi_proxy_clusters']}")

    return {
        'anomalies': anomalies,
        'clusters': clusters,
        'signatures': correlation_results.get('signatures', pd.DataFrame()),
        'stats': stats
    }


def main():
    parser = argparse.ArgumentParser(description='Run global trace element anomaly scan')
    parser.add_argument('--min-year', type=int, default=None,
                       help='Minimum year CE to analyze')
    parser.add_argument('--max-year', type=int, default=None,
                       help='Maximum year CE to analyze')
    parser.add_argument('--penalty', type=float, default=10.0,
                       help='PELT penalty parameter (default: 10)')
    parser.add_argument('--min-samples', type=int, default=10,
                       help='Minimum samples per entity (default: 10)')
    parser.add_argument('--output', type=str, default=None,
                       help='Output directory')

    args = parser.parse_args()

    results = run_trace_element_scan(
        min_year=args.min_year,
        max_year=args.max_year,
        penalty=args.penalty,
        min_samples=args.min_samples,
        output_dir=args.output
    )

    return results


if __name__ == '__main__':
    main()
