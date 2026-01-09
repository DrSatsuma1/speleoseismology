#!/usr/bin/env python3
"""
Marble Fork Kaweah River Water Quality Anomaly Analysis
USGS-11206820 - Downstream of Crystal Cave, Sequoia National Park

Approach: Let the data speak. No earthquake matching - pure anomaly detection.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import glob
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Configuration
DATA_DIR = Path("/Users/catherine/projects/quake/Marble Fork")
OUTPUT_DIR = Path("/Users/catherine/projects/quake/paleoseismic_caves/data/california")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_all_data():
    """Load and merge all CSV files"""
    files = sorted(glob.glob(str(DATA_DIR / "fullphyschem*.csv")))
    print(f"Loading {len(files)} files...")

    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f, low_memory=False)
            dfs.append(df)
        except Exception as e:
            print(f"  Error loading {f}: {e}")

    combined = pd.concat(dfs, ignore_index=True)
    print(f"Total records: {len(combined):,}")
    return combined

def extract_timeseries(df):
    """Extract clean time series for each parameter"""
    # Key columns
    cols = ['Activity_StartDate', 'Result_Characteristic', 'Result_Measure',
            'Result_MeasureUnit', 'Result_SampleFraction']

    # Filter to valid data
    ts = df[cols].copy()
    ts['Activity_StartDate'] = pd.to_datetime(ts['Activity_StartDate'], errors='coerce')
    ts['Result_Measure'] = pd.to_numeric(ts['Result_Measure'], errors='coerce')
    ts = ts.dropna(subset=['Activity_StartDate', 'Result_Characteristic', 'Result_Measure'])

    # Summarize available parameters
    print("\n=== AVAILABLE PARAMETERS ===")
    param_counts = ts.groupby('Result_Characteristic').agg({
        'Result_Measure': ['count', 'min', 'max', 'mean'],
        'Activity_StartDate': ['min', 'max']
    })
    param_counts.columns = ['count', 'min_val', 'max_val', 'mean_val', 'first_date', 'last_date']
    param_counts = param_counts.sort_values('count', ascending=False)

    print("\nTop 30 parameters by count:")
    for idx, row in param_counts.head(30).iterrows():
        print(f"  {idx[:50]:50} n={int(row['count']):4}  {row['first_date'].strftime('%Y-%m-%d')} to {row['last_date'].strftime('%Y-%m-%d')}")

    return ts, param_counts

def analyze_parameter(ts, param_name, min_samples=20):
    """Analyze a single parameter for anomalies"""
    # Filter to parameter
    data = ts[ts['Result_Characteristic'] == param_name].copy()
    if len(data) < min_samples:
        return None

    # Group by date (take mean if multiple samples same day)
    daily = data.groupby('Activity_StartDate')['Result_Measure'].mean().reset_index()
    daily = daily.sort_values('Activity_StartDate')
    daily.columns = ['date', 'value']

    # Z-score analysis
    mean_val = daily['value'].mean()
    std_val = daily['value'].std()
    if std_val == 0:
        return None

    daily['z_score'] = (daily['value'] - mean_val) / std_val
    daily['anomaly_zscore'] = abs(daily['z_score']) > 2.0

    # Isolation Forest
    scaler = StandardScaler()
    X = scaler.fit_transform(daily[['value']])
    iso = IsolationForest(contamination=0.1, random_state=42)
    daily['anomaly_iforest'] = iso.fit_predict(X) == -1

    # Combined anomaly score
    daily['is_anomaly'] = daily['anomaly_zscore'] | daily['anomaly_iforest']

    return {
        'param': param_name,
        'n_samples': len(daily),
        'date_range': (daily['date'].min(), daily['date'].max()),
        'mean': mean_val,
        'std': std_val,
        'data': daily,
        'n_anomalies_zscore': daily['anomaly_zscore'].sum(),
        'n_anomalies_iforest': daily['anomaly_iforest'].sum(),
        'n_anomalies_combined': daily['is_anomaly'].sum()
    }

def predictive_analysis(daily_data, window_months=12):
    """Analyze with rolling average to find departures from expected behavior"""
    df = daily_data.copy()
    df = df.set_index('date').sort_index()

    # Resample to monthly means
    monthly = df['value'].resample('M').mean().dropna()
    if len(monthly) < window_months + 1:
        return None

    # Rolling mean (past window_months)
    monthly_df = pd.DataFrame({'value': monthly})
    monthly_df['rolling_mean'] = monthly_df['value'].rolling(window=window_months, min_periods=window_months).mean()
    monthly_df['rolling_std'] = monthly_df['value'].rolling(window=window_months, min_periods=window_months).std()

    # Residual from rolling mean
    monthly_df['residual'] = monthly_df['value'] - monthly_df['rolling_mean']
    monthly_df['z_residual'] = monthly_df['residual'] / monthly_df['rolling_std']

    # Flag departures
    monthly_df['departure'] = abs(monthly_df['z_residual']) > 2.0

    return monthly_df.dropna()

def main():
    print("=" * 70)
    print("MARBLE FORK KAWEAH RIVER - WATER QUALITY ANOMALY ANALYSIS")
    print("USGS-11206820 | Downstream of Crystal Cave, Sequoia NP")
    print("=" * 70)

    # Load data
    df = load_all_data()

    # Extract time series
    ts, param_counts = extract_timeseries(df)

    # Parameters of interest for seismic signal detection
    # (based on Chiodini hydrogeochemical model)
    seismic_params = [
        'Specific conductance',
        'Turbidity',
        'Calcium',
        'Magnesium',
        'pH',
        'Dissolved oxygen (DO)',
        'Temperature, water',
        'Sodium',
        'Potassium',
        'Chloride',
        'Sulfate',
        'Silica',
        'Alkalinity',
        'Total dissolved solids'
    ]

    print("\n" + "=" * 70)
    print("ANOMALY DETECTION RESULTS")
    print("=" * 70)

    results = []
    all_anomalies = []

    for param in seismic_params:
        # Find matching parameter (may have additional text)
        matches = [p for p in param_counts.index if param.lower() in p.lower()]

        for match in matches:
            result = analyze_parameter(ts, match)
            if result:
                results.append(result)
                print(f"\n{match}")
                print(f"  Samples: {result['n_samples']}")
                print(f"  Period: {result['date_range'][0].strftime('%Y-%m-%d')} to {result['date_range'][1].strftime('%Y-%m-%d')}")
                print(f"  Mean: {result['mean']:.4f} ± {result['std']:.4f}")
                print(f"  Anomalies (|Z|>2): {result['n_anomalies_zscore']}")
                print(f"  Anomalies (IForest): {result['n_anomalies_iforest']}")

                # Get anomaly dates
                anomalies = result['data'][result['data']['is_anomaly']].copy()
                anomalies['parameter'] = match
                all_anomalies.append(anomalies)

    # Combine all anomalies
    if all_anomalies:
        anomaly_df = pd.concat(all_anomalies, ignore_index=True)
        anomaly_df = anomaly_df.sort_values('date')

        print("\n" + "=" * 70)
        print("ALL DETECTED ANOMALIES (sorted by date)")
        print("=" * 70)

        for _, row in anomaly_df.iterrows():
            direction = "HIGH" if row['z_score'] > 0 else "LOW"
            print(f"  {row['date'].strftime('%Y-%m-%d')} | {row['parameter'][:40]:40} | Z={row['z_score']:+.2f} ({direction})")

        # Look for multi-parameter anomalies (same date, multiple params)
        print("\n" + "=" * 70)
        print("MULTI-PARAMETER ANOMALY CLUSTERS")
        print("(Multiple parameters anomalous on same date - potential seismic signal)")
        print("=" * 70)

        # Group anomalies by year-month to find clusters
        anomaly_df['year_month'] = anomaly_df['date'].dt.to_period('M')
        monthly_clusters = anomaly_df.groupby('year_month').agg({
            'parameter': lambda x: list(x),
            'z_score': list,
            'date': 'first'
        })

        for ym, row in monthly_clusters.iterrows():
            if len(row['parameter']) >= 2:  # Multiple params anomalous
                print(f"\n{ym}:")
                for p, z in zip(row['parameter'], row['z_score']):
                    print(f"    {p[:50]:50} Z={z:+.2f}")

        # Save anomalies
        anomaly_df.to_csv(OUTPUT_DIR / 'marble_fork_anomalies.csv', index=False)
        print(f"\nSaved anomalies to: {OUTPUT_DIR / 'marble_fork_anomalies.csv'}")

    # Predictive Analysis
    print("\n" + "=" * 70)
    print("PREDICTIVE ANALYSIS (12-month rolling baseline)")
    print("Identifies departures from expected seasonal/trend behavior")
    print("=" * 70)

    for result in results:
        pred = predictive_analysis(result['data'])
        if pred is not None and len(pred) > 0:
            departures = pred[pred['departure']]
            if len(departures) > 0:
                print(f"\n{result['param'][:60]}")
                print(f"  Months analyzed: {len(pred)}")
                print(f"  Departures from 12-mo baseline: {len(departures)}")
                for idx, row in departures.iterrows():
                    direction = "ABOVE" if row['z_residual'] > 0 else "BELOW"
                    print(f"    {idx.strftime('%Y-%m')} | Z_residual={row['z_residual']:+.2f} ({direction} expected)")

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)

    return results, anomaly_df if all_anomalies else None

if __name__ == "__main__":
    results, anomalies = main()
