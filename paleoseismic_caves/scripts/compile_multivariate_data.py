#!/usr/bin/env python3
"""
Compile all proxy data for multivariate cave detection model.
Calculates baseline noise, detection thresholds, and correlation matrices.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Paths
SISAL_DIR = Path("/Users/catherine/projects/quake/paleoseismic_caves/data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv")
DATA_DIR = Path("/Users/catherine/projects/quake/paleoseismic_caves/data")
REGION_DIR = Path("/Users/catherine/projects/quake/paleoseismic_caves/regions")

# Cave entity IDs from SISAL
CAVE_ENTITIES = {
    "Yok Balum YOKI": 209,
    "Yok Balum YOKG": 210,
    "Crystal Cave": 577,
    "Dos Anas CP": 395,
    "Dos Anas CG": 443,
    "Oregon Caves": 294,
    "Gejkar": 573,
}

def load_sisal_data():
    """Load SISAL sample and proxy data."""
    print("Loading SISAL database...")

    # Load sample mappings
    samples = pd.read_csv(SISAL_DIR / "sample.csv")
    chronology = pd.read_csv(SISAL_DIR / "sisal_chronology.csv")

    # Load all proxy files
    proxies = {}
    for proxy in ['d18O', 'd13C', 'Mg_Ca', 'Sr_Ca', 'U_Ca', 'P_Ca', 'Ba_Ca']:
        try:
            df = pd.read_csv(SISAL_DIR / f"{proxy}.csv")
            # Convert NA strings to NaN
            for col in df.columns:
                if df[col].dtype == object:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            proxies[proxy] = df
            print(f"  Loaded {proxy}: {len(df)} measurements")
        except Exception as e:
            print(f"  Failed to load {proxy}: {e}")

    return samples, chronology, proxies

def extract_cave_data(entity_id, samples, chronology, proxies):
    """Extract all proxy data for a specific cave entity."""
    # Get sample IDs for this entity
    entity_samples = samples[samples['entity_id'] == entity_id]['sample_id'].tolist()

    # Get chronology (ages) for these samples - use lin_interp_age
    chron = chronology[chronology['sample_id'].isin(entity_samples)][['sample_id', 'lin_interp_age']].copy()
    chron = chron.rename(columns={'lin_interp_age': 'age_BP'})
    chron['age_BP'] = pd.to_numeric(chron['age_BP'], errors='coerce')

    # Merge with each proxy
    result = chron.copy()

    for proxy_name, proxy_df in proxies.items():
        col_name = f"{proxy_name}_measurement"
        if col_name in proxy_df.columns:
            proxy_subset = proxy_df[proxy_df['sample_id'].isin(entity_samples)][['sample_id', col_name]]
            result = result.merge(proxy_subset, on='sample_id', how='left')

    # Convert age_BP to year_CE
    result['year_CE'] = 1950 - result['age_BP']

    return result.sort_values('year_CE')

def calculate_z_scores(series):
    """Calculate z-scores, handling NaN values."""
    valid = series.dropna()
    if len(valid) < 10:
        return pd.Series(np.nan, index=series.index)
    mean = valid.mean()
    std = valid.std()
    if std == 0:
        return pd.Series(0, index=series.index)
    return (series - mean) / std

def calculate_noise_stats(df, proxy_cols):
    """Calculate noise statistics for each proxy."""
    stats = {}
    for col in proxy_cols:
        if col in df.columns:
            valid = df[col].dropna()
            if len(valid) >= 10:
                stats[col] = {
                    'n': len(valid),
                    'mean': valid.mean(),
                    'std': valid.std(),
                    'median': valid.median(),
                    'iqr': valid.quantile(0.75) - valid.quantile(0.25),
                    'mad': np.median(np.abs(valid - valid.median())),  # Median absolute deviation
                    'min': valid.min(),
                    'max': valid.max(),
                }
    return stats

def calculate_correlations(df, proxy_cols):
    """Calculate correlation matrix between proxies."""
    available_cols = [c for c in proxy_cols if c in df.columns]
    if len(available_cols) < 2:
        return None

    # Subset to available columns and drop rows with all NaN
    subset = df[available_cols].dropna(how='all')

    # Calculate pairwise correlations
    corr_matrix = subset.corr()
    return corr_matrix

def load_basura_data():
    """Load Bàsura Cave data from local file."""
    basura_file = REGION_DIR / "italy" / "basura_d18O_complete.csv"
    if basura_file.exists():
        df = pd.read_csv(basura_file)
        return df
    return None

def load_gejkar_full():
    """Load full Gejkar data from NOAA file."""
    gejkar_file = DATA_DIR / "Flohr2017-Gej-1.txt"
    if gejkar_file.exists():
        # Read tab-separated data, skipping header lines
        df = pd.read_csv(gejkar_file, sep='\t', comment='#',
                        names=['depth_sample', 'interp_age', 'sample_thickness',
                               'd18O_measurement', 'd13C_measurement', 'Mg_Ca_measurement',
                               'P_Ca_measurement', 'Sr_Ca_measurement', 'U_Ca_measurement'],
                        na_values=['NA', 'na', ''])

        # Convert all numeric columns
        numeric_cols = ['depth_sample', 'interp_age', 'sample_thickness',
                       'd18O_measurement', 'd13C_measurement', 'Mg_Ca_measurement',
                       'P_Ca_measurement', 'Sr_Ca_measurement', 'U_Ca_measurement']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Skip the header row if it got included
        df = df[df['depth_sample'].notna()]

        df['year_CE'] = 1950 - df['interp_age']
        return df
    return None

def main():
    print("=" * 80)
    print("MULTIVARIATE CAVE DETECTION MODEL - PROXY DATA COMPILATION")
    print("=" * 80)
    print()

    # Load SISAL data
    samples, chronology, proxies = load_sisal_data()

    proxy_cols = ['d18O_measurement', 'd13C_measurement', 'Mg_Ca_measurement',
                  'Sr_Ca_measurement', 'U_Ca_measurement', 'P_Ca_measurement']

    results = {}

    print()
    print("=" * 80)
    print("CAVE-BY-CAVE ANALYSIS")
    print("=" * 80)

    # 1. Bàsura Cave (from local file)
    print("\n### BÀSURA CAVE (Italy) ###")
    basura = load_basura_data()
    if basura is not None:
        print(f"Loaded {len(basura)} samples")
        print(f"Time span: {basura['year_CE'].min():.0f} - {basura['year_CE'].max():.0f} CE")

        # Available proxies
        basura_proxies = ['d18O_measurement', 'Mg_Ca_measurement']
        stats = calculate_noise_stats(basura, basura_proxies)

        print("\nProxy Statistics:")
        for proxy, s in stats.items():
            print(f"  {proxy}: n={s['n']}, mean={s['mean']:.3f}, std={s['std']:.3f}")

        # Correlation
        if 'Mg_Ca_measurement' in basura.columns:
            valid = basura[['d18O_measurement', 'Mg_Ca_measurement']].dropna()
            if len(valid) > 10:
                corr = valid.corr().iloc[0, 1]
                print(f"\nδ18O vs Mg/Ca correlation: r = {corr:.3f}")

        results['Basura'] = {'data': basura, 'stats': stats}

    # 2. Gejkar (full multi-proxy from NOAA file)
    print("\n### GEJKAR CAVE (Iraq) ###")
    gejkar = load_gejkar_full()
    if gejkar is not None:
        print(f"Loaded {len(gejkar)} samples")
        print(f"Time span: {gejkar['year_CE'].min():.0f} - {gejkar['year_CE'].max():.0f} CE")

        stats = calculate_noise_stats(gejkar, proxy_cols)

        print("\nProxy Statistics:")
        for proxy, s in stats.items():
            print(f"  {proxy}: n={s['n']}, mean={s['mean']:.4f}, std={s['std']:.4f}")

        # Correlation matrix
        corr = calculate_correlations(gejkar, proxy_cols)
        if corr is not None:
            print("\nCorrelation Matrix:")
            print(corr.round(3).to_string())

        results['Gejkar'] = {'data': gejkar, 'stats': stats, 'correlations': corr}

    # 3-7. SISAL caves
    for cave_name, entity_id in CAVE_ENTITIES.items():
        if 'Gejkar' in cave_name:
            continue  # Already handled

        print(f"\n### {cave_name.upper()} ###")

        data = extract_cave_data(entity_id, samples, chronology, proxies)

        if len(data) == 0:
            print("  No data found")
            continue

        print(f"Loaded {len(data)} samples")

        # Filter for valid year_CE
        data = data[data['year_CE'].notna()]
        if len(data) == 0:
            print("  No chronology data")
            continue

        print(f"Time span: {data['year_CE'].min():.0f} - {data['year_CE'].max():.0f} CE")

        stats = calculate_noise_stats(data, proxy_cols)

        if stats:
            print("\nProxy Statistics:")
            for proxy, s in stats.items():
                print(f"  {proxy}: n={s['n']}, mean={s['mean']:.3f}, std={s['std']:.3f}")

            # Correlation if multiple proxies
            available = [p for p in proxy_cols if p in stats]
            if len(available) >= 2:
                corr = calculate_correlations(data, available)
                if corr is not None:
                    print("\nCorrelation Matrix:")
                    print(corr.round(3).to_string())
                    results[cave_name] = {'data': data, 'stats': stats, 'correlations': corr}
                else:
                    results[cave_name] = {'data': data, 'stats': stats}
            else:
                results[cave_name] = {'data': data, 'stats': stats}
        else:
            print("  Insufficient data for statistics")

    # Summary table
    print()
    print("=" * 80)
    print("SUMMARY: PROXY AVAILABILITY AND NOISE LEVELS")
    print("=" * 80)
    print()

    summary_rows = []
    for cave, res in results.items():
        stats = res.get('stats', {})
        row = {'Cave': cave}
        for proxy in ['d18O_measurement', 'd13C_measurement', 'Mg_Ca_measurement',
                      'Sr_Ca_measurement', 'U_Ca_measurement']:
            short_name = proxy.replace('_measurement', '')
            if proxy in stats:
                row[f'{short_name}_n'] = stats[proxy]['n']
                row[f'{short_name}_std'] = stats[proxy]['std']
            else:
                row[f'{short_name}_n'] = 0
                row[f'{short_name}_std'] = None
        summary_rows.append(row)

    summary_df = pd.DataFrame(summary_rows)
    print(summary_df.to_string(index=False))

    # Detection threshold recommendations
    print()
    print("=" * 80)
    print("DETECTION THRESHOLD RECOMMENDATIONS")
    print("=" * 80)
    print()
    print("Based on 2σ (95%) and 3σ (99.7%) thresholds:\n")

    for cave, res in results.items():
        stats = res.get('stats', {})
        print(f"{cave}:")
        for proxy, s in stats.items():
            short_name = proxy.replace('_measurement', '')
            threshold_2s = s['mean'] + 2 * s['std']
            threshold_3s = s['mean'] + 3 * s['std']
            print(f"  {short_name}: mean={s['mean']:.3f}, 2σ threshold=±{2*s['std']:.3f}, 3σ=±{3*s['std']:.3f}")
        print()

    # Save compiled data
    print("=" * 80)
    print("SAVING COMPILED DATA")
    print("=" * 80)

    output_dir = Path("/Users/catherine/projects/quake/paleoseismic_caves/data/multivariate")
    output_dir.mkdir(exist_ok=True)

    for cave, res in results.items():
        if 'data' in res:
            filename = cave.replace(' ', '_').lower() + '_multiproxy.csv'
            res['data'].to_csv(output_dir / filename, index=False)
            print(f"  Saved: {filename}")

    print()
    print("Done!")

if __name__ == "__main__":
    main()
