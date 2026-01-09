#!/usr/bin/env python3
"""
Extract and analyze Sofular Cave SO-1 speleothem data for NAF paleoseismology.

Reads SISAL v3 CSV files and outputs:
1. Processed data with ages, δ18O, δ13C
2. Anomaly catalog with coupling ratios
3. Summary statistics

Usage:
    python extract_sofular.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuration
SISAL_DIR = Path(__file__).parent.parent / "data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv"
OUTPUT_DIR = Path(__file__).parent.parent / "data/sofular"
ENTITY_ID = 305  # SO-1 speleothem

# Analysis parameters
WINDOW_SIZE = 50  # samples for rolling statistics (adjust based on resolution)
Z_THRESHOLD = 2.0  # minimum Z-score for anomaly
COUPLING_THRESHOLD = 2.0  # max ratio for seismic classification


def load_sisal_data():
    """Load and merge SISAL CSV files for entity 305 (SO-1)."""
    print(f"Loading SISAL data from {SISAL_DIR}")

    # Load sample table
    sample_df = pd.read_csv(SISAL_DIR / "sample.csv")
    sample_df = sample_df[sample_df['entity_id'] == ENTITY_ID].copy()
    print(f"  Samples: {len(sample_df)}")

    # Get sample IDs for this entity
    sample_ids = set(sample_df['sample_id'])

    # Load d18O
    d18o_df = pd.read_csv(SISAL_DIR / "d18O.csv")
    d18o_df = d18o_df[d18o_df['sample_id'].isin(sample_ids)].copy()
    print(f"  δ18O measurements: {len(d18o_df)}")

    # Load d13C
    d13c_df = pd.read_csv(SISAL_DIR / "d13C.csv")
    d13c_df = d13c_df[d13c_df['sample_id'].isin(sample_ids)].copy()
    print(f"  δ13C measurements: {len(d13c_df)}")

    # Load chronology (Bchron ages)
    chron_df = pd.read_csv(SISAL_DIR / "sisal_chronology.csv")
    chron_df = chron_df[chron_df['sample_id'].isin(sample_ids)].copy()
    # Use Bchron_age column (index 7)
    chron_df = chron_df[['sample_id', 'Bchron_age', 'Bchron_age_uncert_pos', 'Bchron_age_uncert_neg']]
    chron_df.columns = ['sample_id', 'age_bp', 'age_uncert_pos', 'age_uncert_neg']
    print(f"  Chronology records: {len(chron_df)}")

    # Merge all data
    merged = sample_df[['sample_id', 'depth_sample']].merge(
        d18o_df[['sample_id', 'd18O_measurement']], on='sample_id', how='left'
    ).merge(
        d13c_df[['sample_id', 'd13C_measurement']], on='sample_id', how='left'
    ).merge(
        chron_df, on='sample_id', how='left'
    )

    # Rename columns
    merged.columns = ['sample_id', 'depth_mm', 'd18O', 'd13C', 'age_bp', 'age_uncert_pos', 'age_uncert_neg']

    # Convert age to numeric, handling 'NA' strings
    merged['age_bp'] = pd.to_numeric(merged['age_bp'], errors='coerce')
    merged['d18O'] = pd.to_numeric(merged['d18O'], errors='coerce')
    merged['d13C'] = pd.to_numeric(merged['d13C'], errors='coerce')

    # Sort by age
    merged = merged.sort_values('age_bp').reset_index(drop=True)

    # Calculate age in CE/BCE
    merged['age_ce'] = 1950 - merged['age_bp']

    print(f"\nMerged dataset: {len(merged)} samples")
    print(f"  With valid ages: {merged['age_bp'].notna().sum()}")
    print(f"  With valid δ18O: {merged['d18O'].notna().sum()}")
    print(f"  With valid δ13C: {merged['d13C'].notna().sum()}")

    return merged


def calculate_anomalies(df):
    """Calculate Z-scores and coupling ratios for anomaly detection."""
    print("\nCalculating anomalies...")

    # Work with samples that have both isotopes and valid ages
    valid = df.dropna(subset=['d18O', 'd13C', 'age_bp']).copy()
    print(f"  Valid samples for analysis: {len(valid)}")

    if len(valid) < WINDOW_SIZE * 2:
        print(f"  Warning: Not enough samples for rolling window of {WINDOW_SIZE}")
        return valid

    # Calculate rolling statistics
    valid['d18O_mean'] = valid['d18O'].rolling(window=WINDOW_SIZE, center=True, min_periods=10).mean()
    valid['d18O_std'] = valid['d18O'].rolling(window=WINDOW_SIZE, center=True, min_periods=10).std()
    valid['d13C_mean'] = valid['d13C'].rolling(window=WINDOW_SIZE, center=True, min_periods=10).mean()
    valid['d13C_std'] = valid['d13C'].rolling(window=WINDOW_SIZE, center=True, min_periods=10).std()

    # Calculate Z-scores
    valid['d18O_z'] = (valid['d18O'] - valid['d18O_mean']) / valid['d18O_std']
    valid['d13C_z'] = (valid['d13C'] - valid['d13C_mean']) / valid['d13C_std']

    # Calculate coupling ratio (avoid division by zero)
    valid['coupling_ratio'] = np.abs(valid['d18O_z']) / np.abs(valid['d13C_z']).replace(0, np.nan)

    # Flag anomalies
    valid['is_anomaly'] = (
        (np.abs(valid['d18O_z']) > Z_THRESHOLD) &
        (valid['coupling_ratio'] < COUPLING_THRESHOLD) &
        (valid['coupling_ratio'].notna())
    )

    # Classify
    def classify(row):
        if pd.isna(row['coupling_ratio']) or pd.isna(row['d18O_z']):
            return 'INSUFFICIENT_DATA'
        if np.abs(row['d18O_z']) < Z_THRESHOLD:
            return 'NORMAL'
        if row['coupling_ratio'] < COUPLING_THRESHOLD:
            return 'SEISMIC_CANDIDATE'
        elif row['coupling_ratio'] > 3.0:
            return 'CLIMATIC'
        else:
            return 'UNCERTAIN'

    valid['classification'] = valid.apply(classify, axis=1)

    # Summary
    seismic = valid[valid['classification'] == 'SEISMIC_CANDIDATE']
    print(f"  Seismic candidates (|Z| > {Z_THRESHOLD}, ratio < {COUPLING_THRESHOLD}): {len(seismic)}")

    return valid


def find_top_anomalies(df, n=50):
    """Extract top N anomalies ranked by Z-score."""
    seismic = df[df['classification'] == 'SEISMIC_CANDIDATE'].copy()
    seismic['abs_z'] = np.abs(seismic['d18O_z'])
    seismic = seismic.sort_values('abs_z', ascending=False).head(n)

    cols = ['sample_id', 'age_bp', 'age_ce', 'd18O', 'd13C', 'd18O_z', 'd13C_z', 'coupling_ratio', 'classification']
    return seismic[cols]


def main():
    """Main processing pipeline."""
    print("=" * 60)
    print("SOFULAR CAVE SO-1 PALEOSEISMIC ANALYSIS")
    print("North Anatolian Fault - Prehistoric Earthquake Detection")
    print("=" * 60)

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load data
    df = load_sisal_data()

    # Save processed data
    output_file = OUTPUT_DIR / "SO1_processed.csv"
    df.to_csv(output_file, index=False)
    print(f"\nSaved processed data to {output_file}")

    # Calculate anomalies
    analyzed = calculate_anomalies(df)

    # Save analyzed data
    analyzed_file = OUTPUT_DIR / "SO1_analyzed.csv"
    analyzed.to_csv(analyzed_file, index=False)
    print(f"Saved analyzed data to {analyzed_file}")

    # Extract top anomalies
    top_anomalies = find_top_anomalies(analyzed, n=50)
    anomalies_file = OUTPUT_DIR / "SO1_anomalies.csv"
    top_anomalies.to_csv(anomalies_file, index=False)
    print(f"Saved top 50 anomalies to {anomalies_file}")

    # Print summary
    print("\n" + "=" * 60)
    print("TOP 20 SEISMIC CANDIDATES")
    print("=" * 60)
    if len(top_anomalies) > 0:
        print(top_anomalies.head(20).to_string(index=False))
    else:
        print("No seismic candidates found meeting criteria.")

    # Age distribution of anomalies
    print("\n" + "=" * 60)
    print("AGE DISTRIBUTION OF SEISMIC CANDIDATES")
    print("=" * 60)
    if len(top_anomalies) > 0:
        bins = [0, 2000, 5000, 10000, 20000, 30000, 50000]
        labels = ['0-2k', '2-5k', '5-10k', '10-20k', '20-30k', '30-50k']
        top_anomalies['age_bin'] = pd.cut(top_anomalies['age_bp'], bins=bins, labels=labels)
        print(top_anomalies['age_bin'].value_counts().sort_index())

    return analyzed, top_anomalies


if __name__ == "__main__":
    analyzed, anomalies = main()
