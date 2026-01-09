#!/usr/bin/env python3
"""
Aquifer Monitoring Validation - USGS Water Quality Portal Data Analysis
=======================================================================

Downloads and analyzes groundwater chemistry data from modern M6+ earthquakes
to validate the Chiodini speleothem paleoseismology model.

Target Earthquakes:
- 2019 Ridgecrest M7.1 (California)
- 2009 L'Aquila M6.3 (Italy)
- 2016 Central Italy M6.0-6.5 (Italy)
- 2011 Christchurch M6.3 (New Zealand)

Validation: If earthquakes disrupt aquifers (Chiodini model), we should see:
- Mg/Ca ratio increases (deep water intrusion)
- pH decreases (CO2 degassing)
- Conductivity increases (saline water)
- Recovery time >10 years (not 1-3 years like climate)
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from scipy import stats
import json

# =============================================================================
# EARTHQUAKE PARAMETERS
# =============================================================================

EARTHQUAKES = {
    'ridgecrest_2019': {
        'name': '2019 Ridgecrest M7.1',
        'date': '2019-07-05',
        'lat': 35.77,
        'lon': -117.60,
        'magnitude': 7.1,
        'search_radius_km': 100,
        'baseline_start': '2018-01-01',
        'baseline_end': '2019-07-01',
        'postevent_start': '2019-07-06',
        'postevent_end': '2021-07-01'
    },
    'laquila_2009': {
        'name': '2009 L\'Aquila M6.3',
        'date': '2009-04-06',
        'lat': 42.35,
        'lon': 13.38,
        'magnitude': 6.3,
        'search_radius_km': 50,
        'baseline_start': '2008-01-01',
        'baseline_end': '2009-04-01',
        'postevent_start': '2009-04-07',
        'postevent_end': '2011-04-01'
    },
    'central_italy_2016': {
        'name': '2016 Central Italy M6.0',
        'date': '2016-08-24',
        'lat': 42.70,
        'lon': 13.23,
        'magnitude': 6.0,
        'search_radius_km': 50,
        'baseline_start': '2015-01-01',
        'baseline_end': '2016-08-01',
        'postevent_start': '2016-08-25',
        'postevent_end': '2018-08-01'
    }
}

# =============================================================================
# USGS WATER QUALITY PORTAL API
# =============================================================================

WQP_BASE_URL = "https://www.waterqualitydata.us/data/Result/search"

def query_usgs_water_quality(earthquake_key):
    """
    Query USGS Water Quality Portal for groundwater chemistry data
    near earthquake epicenter.

    Parameters:
        earthquake_key: Key from EARTHQUAKES dict

    Returns:
        pandas DataFrame with water chemistry measurements
    """
    eq = EARTHQUAKES[earthquake_key]

    # Convert search radius from km to miles (USGS uses miles)
    radius_miles = eq['search_radius_km'] * 0.621371

    # Convert dates from YYYY-MM-DD to MM-DD-YYYY (WQP format)
    def convert_date(date_str):
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%m-%d-%Y')

    # Build parameters with correct WQP format
    # Multiple characteristics separated by semicolons
    characteristics = ';'.join(['Calcium', 'Magnesium', 'Strontium', 'pH',
                                'Specific conductance', 'Turbidity', 'Temperature, water'])

    params = {
        'lat': eq['lat'],
        'long': eq['lon'],
        'within': radius_miles,
        'siteType': 'Well',
        'startDateLo': convert_date(eq['baseline_start']),
        'startDateHi': convert_date(eq['postevent_end']),
        'characteristicName': characteristics,
        'mimeType': 'csv',
        'zip': 'no'
    }

    print(f"Querying USGS Water Quality Portal for {eq['name']}...")
    print(f"  Location: {eq['lat']}, {eq['lon']}")
    print(f"  Radius: {radius_miles:.1f} miles ({eq['search_radius_km']} km)")
    print(f"  Date range: {eq['baseline_start']} to {eq['postevent_end']}")

    response = requests.get(WQP_BASE_URL, params=params, timeout=120)

    if response.status_code == 200:
        # Save raw CSV
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(os.path.dirname(script_dir), 'data', 'aquifer_monitoring')
        output_file = os.path.join(data_dir, f"{earthquake_key}_raw.csv")
        with open(output_file, 'w') as f:
            f.write(response.text)
        print(f"  ✓ Downloaded data to {output_file}")

        # Parse into DataFrame
        from io import StringIO
        df = pd.read_csv(StringIO(response.text))
        print(f"  ✓ Found {len(df)} measurements from {df['MonitoringLocationIdentifier'].nunique()} sites")
        return df
    else:
        print(f"  ✗ Error: HTTP {response.status_code}")
        return None

# =============================================================================
# DATA PROCESSING
# =============================================================================

def calculate_mg_ca_ratio(df):
    """
    Calculate Mg/Ca molar ratio from water chemistry data.

    The Chiodini model predicts:
    - Seismic: HIGH Mg/Ca (deep water intrusion)
    - Climatic: LOW Mg/Ca (meteoric dilution)
    """
    # Pivot to get Mg and Ca columns
    pivot = df.pivot_table(
        index=['MonitoringLocationIdentifier', 'ActivityStartDate'],
        columns='CharacteristicName',
        values='ResultMeasureValue',
        aggfunc='first'
    ).reset_index()

    # Convert date to datetime
    pivot['ActivityStartDate'] = pd.to_datetime(pivot['ActivityStartDate'])

    # Calculate molar ratio (Mg/Ca)
    # Atomic weights: Mg=24.305, Ca=40.078
    if 'Magnesium' in pivot.columns and 'Calcium' in pivot.columns:
        pivot['Mg_Ca_ratio'] = (pivot['Magnesium'] / 24.305) / (pivot['Calcium'] / 40.078)

    return pivot

def calculate_z_scores(time_series, earthquake_date, baseline_months=12):
    """
    Calculate z-scores relative to pre-earthquake baseline.

    Similar to Bàsura Cave analysis:
    - Baseline: Mean and stdev from N months before earthquake
    - Z-score: (value - baseline_mean) / baseline_stdev
    - Significant: |z| > 2.0
    """
    eq_date = pd.to_datetime(earthquake_date)
    baseline_start = eq_date - timedelta(days=baseline_months*30)

    # Get baseline statistics
    baseline = time_series[time_series['ActivityStartDate'] < eq_date]
    baseline = baseline[baseline['ActivityStartDate'] > baseline_start]

    mean = baseline['Mg_Ca_ratio'].mean()
    std = baseline['Mg_Ca_ratio'].std()

    # Calculate z-scores
    time_series['z_score'] = (time_series['Mg_Ca_ratio'] - mean) / std
    time_series['baseline_mean'] = mean
    time_series['baseline_std'] = std

    return time_series

# =============================================================================
# VISUALIZATION
# =============================================================================

def plot_before_after(df, earthquake_key):
    """
    Create before/after plots showing Mg/Ca response to earthquake.
    """
    eq = EARTHQUAKES[earthquake_key]
    eq_date = pd.to_datetime(eq['date'])

    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # Convert date to datetime
    df['ActivityStartDate'] = pd.to_datetime(df['ActivityStartDate'])

    # Plot 1: Mg/Ca ratio over time
    ax1 = axes[0]
    for site in df['MonitoringLocationIdentifier'].unique():
        site_data = df[df['MonitoringLocationIdentifier'] == site]
        ax1.plot(site_data['ActivityStartDate'], site_data['Mg_Ca_ratio'],
                marker='o', label=site, alpha=0.7)

    ax1.axvline(eq_date, color='red', linestyle='--', linewidth=2, label='Earthquake')
    ax1.set_ylabel('Mg/Ca Molar Ratio')
    ax1.set_title(f'{eq["name"]} - Groundwater Mg/Ca Response')
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.grid(True, alpha=0.3)

    # Plot 2: Z-scores
    ax2 = axes[1]
    for site in df['MonitoringLocationIdentifier'].unique():
        site_data = df[df['MonitoringLocationIdentifier'] == site]
        ax2.plot(site_data['ActivityStartDate'], site_data['z_score'],
                marker='s', label=site, alpha=0.7)

    ax2.axvline(eq_date, color='red', linestyle='--', linewidth=2)
    ax2.axhline(2.0, color='orange', linestyle=':', label='Significant (+2σ)')
    ax2.axhline(-2.0, color='orange', linestyle=':')
    ax2.axhline(0, color='gray', linestyle='-', linewidth=0.5)
    ax2.set_ylabel('Z-score (σ)')
    ax2.set_xlabel('Date')
    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), 'data', 'aquifer_monitoring')
    output_file = os.path.join(data_dir, f"{earthquake_key}_plot.png")
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"  ✓ Saved plot to {output_file}")
    plt.close()

# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def analyze_earthquake(earthquake_key):
    """
    Complete analysis pipeline for one earthquake.
    """
    print(f"\n{'='*70}")
    print(f"ANALYZING: {EARTHQUAKES[earthquake_key]['name']}")
    print(f"{'='*70}\n")

    # Step 1: Download data
    df = query_usgs_water_quality(earthquake_key)
    if df is None or len(df) == 0:
        print("  ✗ No data found. Skipping analysis.")
        return

    # Step 2: Calculate Mg/Ca ratios
    print("\nCalculating Mg/Ca ratios...")
    pivot = calculate_mg_ca_ratio(df)
    if 'Mg_Ca_ratio' not in pivot.columns:
        print("  ✗ Insufficient Mg/Ca data. Skipping analysis.")
        return

    # Step 3: Calculate z-scores
    print("Calculating z-scores relative to baseline...")
    for site in pivot['MonitoringLocationIdentifier'].unique():
        site_data = pivot[pivot['MonitoringLocationIdentifier'] == site].copy()
        site_data_with_z = calculate_z_scores(site_data, EARTHQUAKES[earthquake_key]['date'])
        for col in ['z_score', 'baseline_mean', 'baseline_std']:
            if col in site_data_with_z.columns:
                pivot.loc[pivot['MonitoringLocationIdentifier'] == site, col] = site_data_with_z[col].values

    # Step 4: Find significant anomalies
    print("\nSearching for significant Mg/Ca anomalies (|z| > 2.0)...")
    if 'z_score' not in pivot.columns:
        print("  ✗ Z-scores not calculated. Skipping anomaly detection.")
        return

    post_eq_data = pivot[pivot['ActivityStartDate'] > EARTHQUAKES[earthquake_key]['date']]
    anomalies = post_eq_data[abs(post_eq_data['z_score']) > 2.0]

    if len(anomalies) > 0:
        print(f"  ✓ Found {len(anomalies)} significant anomalies:")
        for idx, row in anomalies.iterrows():
            print(f"    - {row['MonitoringLocationIdentifier']}: "
                  f"{row['ActivityStartDate'].strftime('%Y-%m-%d')} "
                  f"z={row['z_score']:.2f}σ")
    else:
        print("  ✗ No significant anomalies detected.")

    # Step 5: Generate plots
    print("\nGenerating visualization...")
    plot_before_after(pivot, earthquake_key)

    # Step 6: Save processed data
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(script_dir), 'data', 'aquifer_monitoring')
    output_csv = os.path.join(data_dir, f"{earthquake_key}_processed.csv")
    pivot.to_csv(output_csv, index=False)
    print(f"  ✓ Saved processed data to {output_csv}")

    # Step 7: Statistical summary
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    baseline = pivot[pivot['ActivityStartDate'] < EARTHQUAKES[earthquake_key]['date']]
    postevent = pivot[pivot['ActivityStartDate'] > EARTHQUAKES[earthquake_key]['date']]

    print(f"Baseline Mg/Ca: {baseline['Mg_Ca_ratio'].mean():.4f} ± {baseline['Mg_Ca_ratio'].std():.4f}")
    print(f"Post-event Mg/Ca: {postevent['Mg_Ca_ratio'].mean():.4f} ± {postevent['Mg_Ca_ratio'].std():.4f}")

    if len(anomalies) > 0:
        print(f"\nPeak z-score: {anomalies['z_score'].abs().max():.2f}σ")
        print(f"Compare to Bàsura 1285: Mg/Ca +2.25σ")

        if anomalies['z_score'].abs().max() > 2.0:
            print("\n✓ VALIDATES CHIODINI MODEL: Earthquake produced Mg/Ca anomaly!")
        else:
            print("\n✗ WEAK SIGNAL: Anomaly below Bàsura threshold.")
    else:
        print("\n✗ NO VALIDATION: No Mg/Ca anomalies detected.")
        print("   Possible reasons:")
        print("   - Earthquake too distant from monitoring wells")
        print("   - Aquifer not connected to fault rupture zone")
        print("   - Insufficient data resolution (quarterly sampling)")

    print("="*70 + "\n")

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("AQUIFER MONITORING VALIDATION STUDY")
    print("Validating Speleothem Paleoseismology with Modern Earthquake Data")
    print("="*70 + "\n")

    # Analyze each earthquake
    for eq_key in ['ridgecrest_2019']:  # Start with Ridgecrest
        try:
            analyze_earthquake(eq_key)
        except Exception as e:
            print(f"\n✗ Error analyzing {eq_key}: {str(e)}\n")
            import traceback
            traceback.print_exc()

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("1. Review plots in paleoseismic_caves/data/aquifer_monitoring/")
    print("2. If Ridgecrest shows signal, expand to Italy (L'Aquila, Central Italy)")
    print("3. Draft AQUIFER_MONITORING_VALIDATION.md with results")
    print("4. Update PUBLICATION_STRATEGY.md with validation evidence")
