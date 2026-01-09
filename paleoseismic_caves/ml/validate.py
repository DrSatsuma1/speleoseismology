"""
Cross-Validation of ML-Detected Anomalies

Matches anomalies against:
1. Known earthquake catalogs (DBMI15, USGS)
2. Volcanic forcing database (eVolv2k v4)
3. Known climate events (LALIA, LIA, etc.)

Output: Classification of each anomaly as:
- MATCHED_EARTHQUAKE: Within ±10 years of known earthquake
- MATCHED_VOLCANIC: Within ±5 years of major eruption
- MATCHED_CLIMATE: Within known climate anomaly period
- DARK_CANDIDATE: Unexplained - potential dark earthquake
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List, Tuple

# Project paths
DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent / "outputs"


def load_volcanic_forcing() -> pd.DataFrame:
    """Load eVolv2k v4 volcanic stratospheric sulfur injection database."""
    evol_path = DATA_DIR / "SISAL3" / "eVolv2k_v4" / "Sigl-Toohey_2024_eVolv2k_v4.tab"

    if not evol_path.exists():
        print(f"Warning: eVolv2k file not found at {evol_path}")
        return pd.DataFrame(columns=['year_ce', 'vssi'])

    # Read the tab-delimited file - skip /* */ metadata block
    try:
        # Find where data starts (after */ line)
        with open(evol_path, 'r') as f:
            lines = f.readlines()

        skip_rows = 0
        for i, line in enumerate(lines):
            if line.strip().endswith('*/'):
                skip_rows = i + 1
                break

        # Read with correct skiprows
        df = pd.read_csv(evol_path, sep='\t', skiprows=skip_rows, header=0)

        # eVolv2k v4 columns (13 total):
        # 0: Eruption year (CE), 1: ISO year, 2: Month, 3: Day, 4: Latitude
        # 5: Greenland SO4, 6: Antarctic SO4, 7: VSSI (Tg), 8: VSSI std dev
        # 9: Asymmetry, 10: Location, 11: Tephra, 12: Reference

        # Extract relevant columns by position
        result = pd.DataFrame({
            'year_ce': pd.to_numeric(df.iloc[:, 0], errors='coerce'),
            'vssi': pd.to_numeric(df.iloc[:, 7], errors='coerce'),
            'uncertainty': pd.to_numeric(df.iloc[:, 8], errors='coerce'),
            'latitude': pd.to_numeric(df.iloc[:, 4], errors='coerce'),
            'location': df.iloc[:, 10] if df.shape[1] > 10 else None
        })

        result = result.dropna(subset=['year_ce', 'vssi'])
        print(f"Loaded {len(result)} volcanic events from eVolv2k v4")
        return result
    except Exception as e:
        print(f"Error loading volcanic data: {e}")
        return pd.DataFrame(columns=['year_ce', 'vssi'])


def load_earthquake_catalog() -> pd.DataFrame:
    """Load earthquake catalogs (DBMI15 for Italy, USGS for global)."""
    catalogs = []

    # Try DBMI15 files
    dbmi_files = list(DATA_DIR.glob("DBMI15*.csv"))
    for f in dbmi_files:
        try:
            df = pd.read_csv(f)
            # Look for year column
            year_col = None
            for col in df.columns:
                if 'year' in col.lower() or 'date' in col.lower() or 'anno' in col.lower():
                    year_col = col
                    break
            if year_col:
                df['year_ce'] = pd.to_numeric(df[year_col], errors='coerce')
                df['source'] = f.name
                catalogs.append(df[['year_ce', 'source']].dropna())
        except Exception as e:
            print(f"Error loading {f}: {e}")

    if catalogs:
        combined = pd.concat(catalogs, ignore_index=True)
        combined = combined.drop_duplicates(subset=['year_ce'])
        print(f"Loaded {len(combined)} earthquake events from catalogs")
        return combined

    print("Warning: No earthquake catalog files found")
    return pd.DataFrame(columns=['year_ce', 'source'])


# Known major climate anomaly periods (year_start, year_end, name)
CLIMATE_PERIODS = [
    (536, 660, 'Late Antique Little Ice Age'),
    (1250, 1300, 'Medieval Climate Anomaly transition'),
    (1600, 1700, 'Little Ice Age peak'),
    (1783, 1785, 'Laki eruption aftermath'),
    (1815, 1820, 'Tambora Year Without Summer'),
    (1257, 1260, 'Samalas eruption'),
    (1640, 1645, 'Mount Parker eruption'),
]


def match_to_volcanic(anomalies: pd.DataFrame, volcanoes: pd.DataFrame,
                      window_years: int = 5, min_vssi: float = 5.0) -> pd.DataFrame:
    """Match anomalies to volcanic events within time window."""
    if len(volcanoes) == 0:
        anomalies['volcanic_match'] = None
        anomalies['volcanic_vssi'] = None
        return anomalies

    # Filter to significant eruptions
    sig_volc = volcanoes[volcanoes['vssi'] >= min_vssi]

    matches = []
    for _, row in anomalies.iterrows():
        year = row['year_ce']
        # Find closest volcanic event within window
        in_window = sig_volc[(sig_volc['year_ce'] >= year - window_years) &
                             (sig_volc['year_ce'] <= year + window_years)]
        if len(in_window) > 0:
            # Take the largest eruption in window
            best = in_window.loc[in_window['vssi'].idxmax()]
            matches.append({'volcanic_match': best['year_ce'], 'volcanic_vssi': best['vssi']})
        else:
            matches.append({'volcanic_match': None, 'volcanic_vssi': None})

    match_df = pd.DataFrame(matches)
    return pd.concat([anomalies.reset_index(drop=True), match_df], axis=1)


def match_to_earthquakes(anomalies: pd.DataFrame, earthquakes: pd.DataFrame,
                          window_years: int = 10) -> pd.DataFrame:
    """Match anomalies to earthquake catalog within time window."""
    if len(earthquakes) == 0:
        anomalies['earthquake_match'] = None
        return anomalies

    matches = []
    for _, row in anomalies.iterrows():
        year = row['year_ce']
        in_window = earthquakes[(earthquakes['year_ce'] >= year - window_years) &
                                 (earthquakes['year_ce'] <= year + window_years)]
        if len(in_window) > 0:
            # Take closest
            closest_idx = (in_window['year_ce'] - year).abs().idxmin()
            matches.append({'earthquake_match': in_window.loc[closest_idx, 'year_ce']})
        else:
            matches.append({'earthquake_match': None})

    match_df = pd.DataFrame(matches)
    return pd.concat([anomalies.reset_index(drop=True), match_df], axis=1)


def match_to_climate_periods(anomalies: pd.DataFrame) -> pd.DataFrame:
    """Match anomalies to known climate anomaly periods."""
    matches = []
    for _, row in anomalies.iterrows():
        year = row['year_ce']
        matched_period = None
        for start, end, name in CLIMATE_PERIODS:
            if start <= year <= end:
                matched_period = name
                break
        matches.append({'climate_period': matched_period})

    match_df = pd.DataFrame(matches)
    return pd.concat([anomalies.reset_index(drop=True), match_df], axis=1)


def classify_anomalies(anomalies: pd.DataFrame) -> pd.DataFrame:
    """Classify each anomaly based on matches."""
    classifications = []

    for _, row in anomalies.iterrows():
        if pd.notna(row.get('volcanic_match')):
            if row.get('volcanic_vssi', 0) > 20:
                classification = 'MATCHED_VOLCANIC_MAJOR'
            else:
                classification = 'MATCHED_VOLCANIC'
        elif pd.notna(row.get('earthquake_match')):
            classification = 'MATCHED_EARTHQUAKE'
        elif pd.notna(row.get('climate_period')):
            classification = 'MATCHED_CLIMATE'
        else:
            # This is a dark candidate!
            if abs(row['shift_magnitude']) >= 2.0:
                classification = 'DARK_CANDIDATE_STRONG'
            else:
                classification = 'DARK_CANDIDATE'

        classifications.append(classification)

    anomalies['classification'] = classifications
    return anomalies


def main():
    """Run cross-validation pipeline."""
    print("=== Cross-Validation of ML-Detected Anomalies ===\n")

    # Load anomalies
    anomalies_path = OUTPUT_DIR / "anomalies.csv"
    if not anomalies_path.exists():
        print("Error: Run global_scan.py first to generate anomalies.csv")
        return

    anomalies = pd.read_csv(anomalies_path)
    print(f"Loaded {len(anomalies)} anomalies from ML scan\n")

    # Load reference catalogs
    volcanoes = load_volcanic_forcing()
    earthquakes = load_earthquake_catalog()

    # Match to each source
    print("\nMatching to volcanic events (±5 years, VSSI ≥ 5)...")
    anomalies = match_to_volcanic(anomalies, volcanoes)

    print("Matching to earthquake catalog (±10 years)...")
    anomalies = match_to_earthquakes(anomalies, earthquakes)

    print("Matching to known climate periods...")
    anomalies = match_to_climate_periods(anomalies)

    # Classify
    print("Classifying anomalies...")
    anomalies = classify_anomalies(anomalies)

    # Save results
    output_path = OUTPUT_DIR / "anomalies_validated.csv"
    anomalies.to_csv(output_path, index=False)
    print(f"\nSaved validated anomalies to {output_path}")

    # Summary statistics
    print("\n=== Classification Summary ===")
    class_counts = anomalies['classification'].value_counts()
    for cls, count in class_counts.items():
        print(f"  {cls}: {count}")

    # Show dark candidates
    dark = anomalies[anomalies['classification'].str.contains('DARK')]
    print(f"\n=== Top 20 Dark Earthquake Candidates ===")
    dark_sorted = dark.sort_values('shift_magnitude', key=abs, ascending=False)
    display_cols = ['site_name', 'entity_name', 'year_ce', 'shift_magnitude', 'lat', 'lon']
    print(dark_sorted[display_cols].head(20).to_string(index=False))

    # Geographic distribution of dark candidates
    print(f"\n=== Dark Candidates by Region ===")
    dark['region'] = pd.cut(dark['lat'],
                            bins=[-90, -30, 30, 90],
                            labels=['Southern Hemisphere', 'Tropics', 'Northern Hemisphere'])
    print(dark['region'].value_counts())

    return anomalies


if __name__ == '__main__':
    results = main()
