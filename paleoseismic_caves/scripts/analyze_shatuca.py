#!/usr/bin/env python3
"""
Analyze Shatuca Cave (Peru) speleothem data for seismic anomalies.
Entity IDs: 432 (Sha-2), 433 (Sha-3), 434 (Sha-composite)
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Paths
SISAL_DIR = Path(__file__).parent.parent / "data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv"

# Shatuca entity IDs
SHATUCA_ENTITIES = [432, 433, 434]

def load_sisal_data():
    """Load and join SISAL tables for Shatuca."""
    # Load tables
    samples = pd.read_csv(SISAL_DIR / "sample.csv")
    d18O = pd.read_csv(SISAL_DIR / "d18O.csv")
    d13C = pd.read_csv(SISAL_DIR / "d13C.csv")
    chronology = pd.read_csv(SISAL_DIR / "sisal_chronology.csv")

    # Filter to Shatuca entities
    shatuca_samples = samples[samples['entity_id'].isin(SHATUCA_ENTITIES)].copy()
    print(f"Shatuca samples: {len(shatuca_samples)}")

    # Join with d18O
    data = shatuca_samples.merge(d18O, on='sample_id', how='left')
    print(f"After d18O join: {len(data)} ({data['d18O_measurement'].notna().sum()} with d18O)")

    # Join with d13C
    data = data.merge(d13C, on='sample_id', how='left')
    print(f"After d13C join: {len(data)} ({data['d13C_measurement'].notna().sum()} with d13C)")

    # Join with chronology - use lin_interp_age as primary
    chron = chronology[['sample_id', 'lin_interp_age', 'lin_interp_age_uncert_pos', 'StalAge_age']]
    data = data.merge(chron, on='sample_id', how='left')

    # Use lin_interp_age, fallback to StalAge_age
    data['age_bp'] = data['lin_interp_age'].fillna(data['StalAge_age'])
    data['age_ce'] = 1950 - data['age_bp']

    valid_data = data.dropna(subset=['d18O_measurement', 'age_bp'])
    print(f"Valid samples with d18O + age: {len(valid_data)}")

    return valid_data.sort_values('age_bp')

def calculate_zscores(data):
    """Calculate z-scores for d18O and d13C."""
    data = data.copy()

    # d18O z-scores
    mean_d18O = data['d18O_measurement'].mean()
    std_d18O = data['d18O_measurement'].std()
    data['d18O_z'] = (data['d18O_measurement'] - mean_d18O) / std_d18O

    # d13C z-scores (if available)
    if data['d13C_measurement'].notna().any():
        mean_d13C = data['d13C_measurement'].mean()
        std_d13C = data['d13C_measurement'].std()
        data['d13C_z'] = (data['d13C_measurement'] - mean_d13C) / std_d13C
    else:
        data['d13C_z'] = np.nan

    print(f"\nd18O stats: mean={mean_d18O:.2f}‰, std={std_d18O:.2f}‰")
    if data['d13C_measurement'].notna().any():
        print(f"d13C stats: mean={mean_d13C:.2f}‰, std={std_d13C:.2f}‰")

    return data

def find_anomalies(data, z_threshold=2.0):
    """Find samples with z-scores exceeding threshold."""
    anomalies = data[
        (data['d18O_z'].abs() >= z_threshold) |
        (data['d13C_z'].abs() >= z_threshold)
    ].copy()

    print(f"\n=== ANOMALIES (|z| >= {z_threshold}) ===")
    print(f"Total: {len(anomalies)}")

    return anomalies

def identify_clusters(data, anomalies, max_gap_years=50):
    """Group anomalies into clusters (potential earthquake events)."""
    if len(anomalies) == 0:
        return []

    anomalies = anomalies.sort_values('age_ce')
    clusters = []
    current_cluster = [anomalies.iloc[0]]

    for i in range(1, len(anomalies)):
        prev_age = anomalies.iloc[i-1]['age_ce']
        curr_age = anomalies.iloc[i]['age_ce']

        if abs(curr_age - prev_age) <= max_gap_years:
            current_cluster.append(anomalies.iloc[i])
        else:
            clusters.append(pd.DataFrame(current_cluster))
            current_cluster = [anomalies.iloc[i]]

    clusters.append(pd.DataFrame(current_cluster))

    return clusters

def calculate_recovery_time(data, cluster):
    """Estimate recovery time for a cluster."""
    if len(cluster) == 0:
        return None

    start_age = cluster['age_ce'].min()
    end_age = cluster['age_ce'].max()

    # Look for return to baseline (z < 1.0)
    post_cluster = data[data['age_ce'] > end_age].sort_values('age_ce')

    for _, row in post_cluster.iterrows():
        if abs(row['d18O_z']) < 1.0:
            return row['age_ce'] - start_age

    return end_age - start_age  # If no clear return, use cluster duration

def main():
    print("=" * 60)
    print("SHATUCA CAVE (PERU) SPELEOTHEM ANALYSIS")
    print("Location: 5.7°S, 77.9°W (Andes subduction zone)")
    print("=" * 60)

    # Load data
    data = load_sisal_data()

    # Get age range
    min_age = data['age_ce'].min()
    max_age = data['age_ce'].max()
    print(f"\nRecord spans: {min_age:.0f} CE to {max_age:.0f} CE ({max_age - min_age:.0f} years)")

    # Calculate z-scores
    data = calculate_zscores(data)

    # Find anomalies
    anomalies = find_anomalies(data)

    if len(anomalies) == 0:
        print("\nNo significant anomalies found.")
        return

    # Group into clusters
    clusters = identify_clusters(data, anomalies)

    print(f"\n=== ANOMALY CLUSTERS ({len(clusters)} detected) ===")
    print("-" * 80)

    results = []
    for i, cluster in enumerate(clusters):
        start_ce = cluster['age_ce'].min()
        end_ce = cluster['age_ce'].max()
        duration = end_ce - start_ce
        peak_d18O_z = cluster['d18O_z'].abs().max()
        peak_d13C_z = cluster['d13C_z'].abs().max() if cluster['d13C_z'].notna().any() else np.nan
        recovery = calculate_recovery_time(data, cluster)

        # Check if d18O and d13C are coupled (both significant)
        has_d13C = cluster['d13C_z'].notna().any()
        coupled = (peak_d18O_z >= 2.0) and has_d13C and (peak_d13C_z >= 1.5)

        # Seismic discrimination
        seismic_score = 0
        reasons = []

        if recovery and recovery > 10:
            seismic_score += 2
            reasons.append(f"long recovery ({recovery:.0f} yr)")

        if duration > 20:
            seismic_score += 1
            reasons.append(f"extended duration ({duration:.0f} yr)")

        if coupled:
            seismic_score += 2
            reasons.append("coupled δ18O/δ13C")

        if peak_d18O_z >= 3.0:
            seismic_score += 1
            reasons.append(f"extreme d18O (z={peak_d18O_z:.2f})")

        classification = "SEISMIC CANDIDATE" if seismic_score >= 2 else "POSSIBLE" if seismic_score >= 1 else "UNCERTAIN"

        result = {
            'cluster': i + 1,
            'start_ce': start_ce,
            'end_ce': end_ce,
            'duration': duration,
            'n_samples': len(cluster),
            'peak_d18O_z': peak_d18O_z,
            'peak_d13C_z': peak_d13C_z,
            'recovery_yr': recovery,
            'coupled': coupled,
            'seismic_score': seismic_score,
            'classification': classification,
            'reasons': reasons
        }
        results.append(result)

        print(f"\nCluster {i+1}: ~{start_ce:.0f} CE")
        print(f"  Duration: {duration:.0f} years ({start_ce:.0f}-{end_ce:.0f} CE)")
        print(f"  Samples: {len(cluster)}")
        print(f"  Peak d18O z-score: {peak_d18O_z:.2f}σ")
        if has_d13C:
            print(f"  Peak d13C z-score: {peak_d13C_z:.2f}σ")
            print(f"  Coupled: {'YES' if coupled else 'NO'}")
        if recovery:
            print(f"  Recovery time: {recovery:.0f} years")
        print(f"  Classification: {classification}")
        if reasons:
            print(f"  Evidence: {', '.join(reasons)}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY: DARK EARTHQUAKE CANDIDATES")
    print("=" * 60)

    seismic_candidates = [r for r in results if r['classification'] == "SEISMIC CANDIDATE"]
    possible = [r for r in results if r['classification'] == "POSSIBLE"]

    print(f"\nSeismic candidates: {len(seismic_candidates)}")
    for r in seismic_candidates:
        print(f"  ~{r['start_ce']:.0f} CE: d18O z={r['peak_d18O_z']:.2f}, recovery={r['recovery_yr']:.0f} yr")

    print(f"\nPossible events: {len(possible)}")
    for r in possible:
        print(f"  ~{r['start_ce']:.0f} CE: d18O z={r['peak_d18O_z']:.2f}")

    # Save detailed data
    output_dir = Path(__file__).parent.parent / "data/peru"
    output_dir.mkdir(parents=True, exist_ok=True)

    anomalies.to_csv(output_dir / "shatuca_anomalies.csv", index=False)
    print(f"\nAnomalies saved to: {output_dir / 'shatuca_anomalies.csv'}")

    # Return results for further analysis
    return results, data

if __name__ == "__main__":
    main()
