#!/usr/bin/env python3
"""Analyze Sahiya Cave (India) for Himalayan Front dark earthquakes."""

import pandas as pd
import numpy as np
from pathlib import Path

SISAL_DIR = Path(__file__).parent.parent / "data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv"

def main():
    # Load data
    samples = pd.read_csv(SISAL_DIR / "sample.csv")
    d18O = pd.read_csv(SISAL_DIR / "d18O.csv")
    chron = pd.read_csv(SISAL_DIR / "original_chronology.csv")

    # Filter for entity 902 (Sahiya SAH-AB_2023)
    entity_samples = samples[samples['entity_id'] == 902]
    sample_ids = set(entity_samples['sample_id'])

    # Get d18O for these samples
    d18O_entity = d18O[d18O['sample_id'].isin(sample_ids)].copy()

    # Get ages
    chron_entity = chron[chron['sample_id'].isin(sample_ids)][['sample_id', 'interp_age']].copy()
    chron_entity.columns = ['sample_id', 'age_bp']

    # Merge
    data = d18O_entity.merge(chron_entity, on='sample_id')
    data = data.sort_values('age_bp')

    # Convert age to CE
    data['age_ce'] = 1950 - data['age_bp']

    print(f"Sahiya Cave Analysis (Entity 902)")
    print(f"="*50)
    print(f"Total samples with d18O and age: {len(data)}")
    print(f"Age range: {data['age_ce'].min():.0f} to {data['age_ce'].max():.0f} CE")
    print(f"d18O range: {data['d18O_measurement'].min():.2f} to {data['d18O_measurement'].max():.2f}")

    # Calculate z-scores using rolling baseline
    window = 50  # samples
    data['d18O_rolling_mean'] = data['d18O_measurement'].rolling(window, center=True, min_periods=10).mean()
    data['d18O_rolling_std'] = data['d18O_measurement'].rolling(window, center=True, min_periods=10).std()
    data['z_score'] = (data['d18O_measurement'] - data['d18O_rolling_mean']) / data['d18O_rolling_std']

    # Find anomalies
    anomalies = data[abs(data['z_score']) >= 2.0].copy()

    print(f"\nAnomalies (|z| >= 2.0): {len(anomalies)}")
    print(f"  Negative (wet/seismic): {len(anomalies[anomalies['z_score'] < -2])}")
    print(f"  Positive (dry): {len(anomalies[anomalies['z_score'] > 2])}")

    # Top anomalies by z-score magnitude
    print(f"\n{'='*60}")
    print(f"TOP 20 ANOMALIES (sorted by |z|)")
    print(f"{'='*60}")
    top = anomalies.nlargest(20, 'z_score', keep='first') if len(anomalies) > 0 else pd.DataFrame()
    top_neg = anomalies.nsmallest(20, 'z_score', keep='first') if len(anomalies) > 0 else pd.DataFrame()
    all_top = pd.concat([top, top_neg]).drop_duplicates().sort_values('z_score')

    for _, row in all_top.iterrows():
        print(f"  {row['age_ce']:.0f} CE: z = {row['z_score']:+.2f}, d18O = {row['d18O_measurement']:.2f}")

    # Historical Himalayan earthquakes to check
    print(f"\n{'='*60}")
    print(f"MAJOR HISTORICAL HIMALAYAN EARTHQUAKES")
    print(f"{'='*60}")

    hist_eq = [
        (1950, "Assam M8.6", 500),  # km from cave
        (1934, "Bihar-Nepal M8.0", 400),
        (1905, "Kangra M7.8", 200),
        (1803, "Garhwal M7.5-8.0", 100),
        (1555, "Kashmir M7.6", 300),
        (1505, "Lo Mustang M8.2", 400),
    ]

    for year, name, dist in hist_eq:
        # Find samples near this year
        window_yrs = 20
        near = data[(data['age_ce'] >= year - window_yrs) & (data['age_ce'] <= year + window_yrs)]
        if len(near) > 0:
            max_z = near['z_score'].max()
            min_z = near['z_score'].min()
            best_z = max_z if abs(max_z) > abs(min_z) else min_z
            print(f"  {year} {name} ({dist} km): max |z| = {best_z:+.2f}")
        else:
            print(f"  {year} {name} ({dist} km): NO DATA")

    # Save output
    output_file = Path(__file__).parent.parent / "data/sahiya_analysis.csv"
    data.to_csv(output_file, index=False)
    print(f"\nData saved to: {output_file}")

if __name__ == "__main__":
    main()
