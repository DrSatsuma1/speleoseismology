#!/usr/bin/env python3
"""
Extract California cave speleothem data from SISAL v3 for paleoseismic analysis.
Target caves: Lake Shasta, Moaning, White Moon, McLean's, Oregon Caves (for cross-validation)
"""

import pandas as pd
import numpy as np
from pathlib import Path

# SISAL v3 database path
SISAL_PATH = Path("/Users/catherine/projects/quake/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv")

# California cave entity IDs from US_CAVE_INVENTORY.md
CALIFORNIA_ENTITIES = {
    889: "Lake_Shasta_LSC2",
    890: "Lake_Shasta_LSC3",
    126: "Moaning_Cave_MC3",
    438: "White_Moon_Cave_WMC1",
    125: "McLeans_Cave_ML1",
    445: "McLeans_Cave_ML2",
    294: "Oregon_Caves_OCNM02-1"  # For Cascadia cross-validation
}

def load_sisal_data():
    """Load relevant SISAL v3 tables."""
    print("Loading SISAL v3 data...")

    sample = pd.read_csv(SISAL_PATH / "sample.csv")
    d18O = pd.read_csv(SISAL_PATH / "d18O.csv")
    d13C = pd.read_csv(SISAL_PATH / "d13C.csv")
    chronology = pd.read_csv(SISAL_PATH / "sisal_chronology.csv")
    mg_ca = pd.read_csv(SISAL_PATH / "Mg_Ca.csv")
    sr_ca = pd.read_csv(SISAL_PATH / "Sr_Ca.csv")

    print(f"  Samples: {len(sample):,}")
    print(f"  δ18O measurements: {len(d18O):,}")
    print(f"  δ13C measurements: {len(d13C):,}")
    print(f"  Chronology records: {len(chronology):,}")
    print(f"  Mg/Ca measurements: {len(mg_ca):,}")
    print(f"  Sr/Ca measurements: {len(sr_ca):,}")

    return sample, d18O, d13C, chronology, mg_ca, sr_ca

def extract_entity_data(entity_id, entity_name, sample_df, d18O_df, d13C_df, chron_df, mg_ca_df, sr_ca_df):
    """Extract all data for a single entity."""

    # Get samples for this entity
    entity_samples = sample_df[sample_df['entity_id'] == entity_id].copy()

    if len(entity_samples) == 0:
        print(f"  ⚠️  No samples found for entity {entity_id}")
        return None

    # Merge with chronology
    data = entity_samples.merge(chron_df, on='sample_id', how='left')

    # Merge with isotopes
    data = data.merge(d18O_df, on='sample_id', how='left')
    data = data.merge(d13C_df, on='sample_id', how='left')

    # Merge with trace elements
    data = data.merge(mg_ca_df, on='sample_id', how='left')
    data = data.merge(sr_ca_df, on='sample_id', how='left')

    # Convert age to year CE (BP = 1950 - CE)
    data['year_CE'] = 1950 - data['lin_interp_age']

    # Summary stats
    n_samples = len(data)
    n_d18O = data['d18O_measurement'].notna().sum()
    n_d13C = data['d13C_measurement'].notna().sum() if 'd13C_measurement' in data.columns else 0
    n_mg_ca = data['Mg_Ca'].notna().sum() if 'Mg_Ca' in data.columns else 0

    # Time range
    valid_years = data[data['year_CE'].notna()]['year_CE']
    if len(valid_years) > 0:
        min_year = valid_years.min()
        max_year = valid_years.max()
    else:
        min_year = max_year = np.nan

    print(f"\n  {entity_name} (Entity {entity_id}):")
    print(f"    Samples: {n_samples}")
    print(f"    δ18O: {n_d18O}")
    print(f"    δ13C: {n_d13C}")
    print(f"    Mg/Ca: {n_mg_ca}")
    print(f"    Time range: {min_year:.0f} to {max_year:.0f} CE")

    # Check for 1800s coverage
    historical_data = data[(data['year_CE'] >= 1800) & (data['year_CE'] <= 1910)]
    n_historical = len(historical_data[historical_data['d18O_measurement'].notna()])
    print(f"    1800-1910 samples: {n_historical}")

    return {
        'entity_id': entity_id,
        'entity_name': entity_name,
        'data': data,
        'n_samples': n_samples,
        'n_d18O': n_d18O,
        'n_d13C': n_d13C,
        'n_mg_ca': n_mg_ca,
        'min_year': min_year,
        'max_year': max_year,
        'n_historical': n_historical
    }

def calculate_anomalies(data, column='d18O_measurement'):
    """Calculate Z-scores for anomaly detection."""
    values = data[column].dropna()
    if len(values) < 10:
        return None

    mean = values.mean()
    std = values.std()

    data['z_score'] = (data[column] - mean) / std
    data['is_anomaly'] = abs(data['z_score']) > 1.5

    return mean, std

def find_historical_anomalies(entity_results):
    """Find anomalies in the 1800-1910 period."""

    print("\n" + "="*60)
    print("HISTORICAL PERIOD ANOMALY SEARCH (1800-1910 CE)")
    print("="*60)

    historical_anomalies = []

    for result in entity_results:
        if result is None:
            continue

        data = result['data'].copy()
        entity_name = result['entity_name']

        # Only analyze if we have δ18O data
        if result['n_d18O'] < 10:
            continue

        # Calculate Z-scores
        stats = calculate_anomalies(data)
        if stats is None:
            continue

        mean, std = stats

        # Filter to historical period
        historical = data[(data['year_CE'] >= 1800) & (data['year_CE'] <= 1910)]
        historical = historical[historical['d18O_measurement'].notna()]

        if len(historical) == 0:
            print(f"\n  {entity_name}: No 1800s data available")
            continue

        # Find anomalies
        anomalies = historical[abs(historical['z_score']) > 1.5].copy()

        print(f"\n  {entity_name}:")
        print(f"    Mean δ18O: {mean:.2f}‰, Std: {std:.2f}‰")
        print(f"    Historical samples: {len(historical)}")
        print(f"    Anomalies found: {len(anomalies)}")

        if len(anomalies) > 0:
            for _, row in anomalies.iterrows():
                year = row['year_CE']
                d18O = row['d18O_measurement']
                z = row['z_score']
                d13C = row.get('d13C_measurement', np.nan)
                mg_ca = row.get('Mg_Ca', np.nan)

                print(f"      Year {year:.0f}: δ18O={d18O:.2f}‰ (z={z:+.2f})", end="")
                if not np.isnan(d13C):
                    print(f", δ13C={d13C:.2f}‰", end="")
                if not np.isnan(mg_ca):
                    print(f", Mg/Ca={mg_ca:.2f}", end="")
                print()

                historical_anomalies.append({
                    'entity': entity_name,
                    'year_CE': year,
                    'd18O': d18O,
                    'z_score': z,
                    'd13C': d13C if not np.isnan(d13C) else None,
                    'mg_ca': mg_ca if not np.isnan(mg_ca) else None
                })

    return historical_anomalies

def main():
    print("="*60)
    print("CALIFORNIA SPELEOTHEM PALEOSEISMIC ANALYSIS")
    print("="*60)

    # Load data
    sample, d18O, d13C, chronology, mg_ca, sr_ca = load_sisal_data()

    # Extract data for each California entity
    print("\n" + "="*60)
    print("EXTRACTING CALIFORNIA CAVE DATA")
    print("="*60)

    results = []
    for entity_id, entity_name in CALIFORNIA_ENTITIES.items():
        result = extract_entity_data(
            entity_id, entity_name,
            sample, d18O, d13C, chronology, mg_ca, sr_ca
        )
        results.append(result)

    # Summary table
    print("\n" + "="*60)
    print("SUMMARY: TEMPORAL COVERAGE")
    print("="*60)
    print(f"{'Cave':<30} {'Samples':>8} {'δ18O':>6} {'δ13C':>6} {'Mg/Ca':>6} {'Min Year':>10} {'Max Year':>10} {'1800s':>6}")
    print("-"*90)

    for result in results:
        if result is None:
            continue
        print(f"{result['entity_name']:<30} {result['n_samples']:>8} {result['n_d18O']:>6} {result['n_d13C']:>6} {result['n_mg_ca']:>6} {result['min_year']:>10.0f} {result['max_year']:>10.0f} {result['n_historical']:>6}")

    # Find historical anomalies
    historical_anomalies = find_historical_anomalies(results)

    # Save results
    print("\n" + "="*60)
    print("SAVING RESULTS")
    print("="*60)

    output_path = Path("/Users/catherine/projects/quake/us_speleothem_project")

    # Save each entity's data
    for result in results:
        if result is None or result['n_d18O'] == 0:
            continue

        filename = f"california_{result['entity_name'].lower()}.csv"
        result['data'].to_csv(output_path / filename, index=False)
        print(f"  Saved: {filename}")

    # Save historical anomalies
    if historical_anomalies:
        anomaly_df = pd.DataFrame(historical_anomalies)
        anomaly_df.to_csv(output_path / "california_historical_anomalies.csv", index=False)
        print(f"  Saved: california_historical_anomalies.csv ({len(anomaly_df)} anomalies)")

    print("\n" + "="*60)
    print("DONE")
    print("="*60)

    return results, historical_anomalies

if __name__ == "__main__":
    results, anomalies = main()
