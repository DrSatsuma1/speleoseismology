#!/usr/bin/env python3
"""
Marble Fork Kaweah River - Pattern Analysis
Looking for cycles, correlations, and time-lagged relationships.
Let the data speak.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import glob
from scipy import signal
from scipy.stats import pearsonr, spearmanr
from scipy.fft import fft, fftfreq
import warnings
warnings.filterwarnings('ignore')

DATA_DIR = Path("/Users/catherine/projects/quake/Marble Fork")
OUTPUT_DIR = Path("/Users/catherine/projects/quake/paleoseismic_caves/data/california")

def load_and_pivot_data():
    """Load all data and create pivoted time series"""
    files = sorted(glob.glob(str(DATA_DIR / "fullphyschem*.csv")))
    print(f"Loading {len(files)} files...")

    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f, low_memory=False)
            dfs.append(df)
        except Exception as e:
            print(f"  Error: {e}")

    combined = pd.concat(dfs, ignore_index=True)

    # Extract key columns
    cols = ['Activity_StartDate', 'Result_Characteristic', 'Result_Measure']
    ts = combined[cols].copy()
    ts['Activity_StartDate'] = pd.to_datetime(ts['Activity_StartDate'], errors='coerce')
    ts['Result_Measure'] = pd.to_numeric(ts['Result_Measure'], errors='coerce')
    ts = ts.dropna()

    # Get most common parameters
    param_counts = ts['Result_Characteristic'].value_counts()
    top_params = param_counts[param_counts > 100].index.tolist()

    # Filter and pivot
    ts = ts[ts['Result_Characteristic'].isin(top_params)]

    # Group by date and parameter, take mean
    grouped = ts.groupby(['Activity_StartDate', 'Result_Characteristic'])['Result_Measure'].mean().reset_index()

    # Pivot to wide format
    pivoted = grouped.pivot(index='Activity_StartDate', columns='Result_Characteristic', values='Result_Measure')
    pivoted = pivoted.sort_index()

    print(f"Pivoted data: {len(pivoted)} dates, {len(pivoted.columns)} parameters")
    return pivoted

def analyze_cycles(series, name, min_periods=3):
    """Find dominant cycles using FFT"""
    # Remove NaN and detrend
    clean = series.dropna()
    if len(clean) < 20:
        return None

    # Resample to regular monthly intervals
    monthly = clean.resample('M').mean().dropna()
    if len(monthly) < 24:
        return None

    # Detrend
    detrended = signal.detrend(monthly.values)

    # FFT
    n = len(detrended)
    yf = fft(detrended)
    xf = fftfreq(n, 1)  # 1 month intervals

    # Get power spectrum (positive frequencies only)
    power = np.abs(yf[:n//2])**2
    freqs = xf[:n//2]

    # Convert to periods (in months)
    periods = np.zeros_like(freqs)
    periods[1:] = 1 / freqs[1:]  # Skip DC component

    # Find peaks
    peak_indices = signal.find_peaks(power[1:], height=np.median(power[1:]) * 2)[0] + 1

    if len(peak_indices) == 0:
        return None

    # Get top 3 peaks
    top_peaks = sorted(peak_indices, key=lambda i: power[i], reverse=True)[:3]

    cycles = []
    for idx in top_peaks:
        if periods[idx] > 2 and periods[idx] < len(monthly):  # Reasonable range
            cycles.append({
                'period_months': periods[idx],
                'power': power[idx],
                'relative_power': power[idx] / np.sum(power[1:])
            })

    return cycles if cycles else None

def cross_correlation_with_lag(series1, series2, max_lag=12):
    """Calculate cross-correlation at different lags"""
    # Align series
    df = pd.DataFrame({'s1': series1, 's2': series2}).dropna()
    if len(df) < 30:
        return None

    results = []
    for lag in range(-max_lag, max_lag + 1):
        if lag < 0:
            s1 = df['s1'].iloc[-lag:].values
            s2 = df['s2'].iloc[:lag].values
        elif lag > 0:
            s1 = df['s1'].iloc[:-lag].values
            s2 = df['s2'].iloc[lag:].values
        else:
            s1 = df['s1'].values
            s2 = df['s2'].values

        if len(s1) > 10:
            corr, pval = pearsonr(s1, s2)
            results.append({'lag': lag, 'correlation': corr, 'pvalue': pval})

    return pd.DataFrame(results)

def find_leading_indicators(pivoted):
    """Find parameters that lead/lag others"""
    # Resample to monthly
    monthly = pivoted.resample('M').mean()

    # Key parameters for seismic analysis
    key_params = [
        'Specific conductance',
        'Calcium',
        'Magnesium',
        'pH',
        'Alkalinity',
        'Sulfate',
        'Chloride',
        'Silica',
        'Sodium',
        'Potassium',
        'Total dissolved solids',
        'Temperature, water'
    ]

    # Find matching columns
    available = []
    for param in key_params:
        matches = [c for c in monthly.columns if param.lower() in c.lower()]
        if matches:
            available.append(matches[0])

    print(f"\nAnalyzing {len(available)} key parameters")

    # Calculate lagged correlations
    lag_results = []

    for i, param1 in enumerate(available):
        for param2 in available[i+1:]:
            xcorr = cross_correlation_with_lag(monthly[param1], monthly[param2], max_lag=6)
            if xcorr is not None:
                # Find best lag
                best_idx = xcorr['correlation'].abs().idxmax()
                best_lag = xcorr.loc[best_idx, 'lag']
                best_corr = xcorr.loc[best_idx, 'correlation']
                best_pval = xcorr.loc[best_idx, 'pvalue']

                # Zero-lag correlation for comparison
                zero_corr = xcorr[xcorr['lag'] == 0]['correlation'].values[0]

                lag_results.append({
                    'param1': param1[:40],
                    'param2': param2[:40],
                    'best_lag_months': best_lag,
                    'best_correlation': best_corr,
                    'zero_lag_correlation': zero_corr,
                    'pvalue': best_pval,
                    'lag_improves': abs(best_corr) > abs(zero_corr) + 0.1
                })

    return pd.DataFrame(lag_results)

def seasonal_decomposition(series, name):
    """Simple seasonal analysis"""
    clean = series.dropna()
    if len(clean) < 24:
        return None

    # Add month
    df = pd.DataFrame({'value': clean})
    df['month'] = df.index.month

    # Monthly averages
    monthly_avg = df.groupby('month')['value'].agg(['mean', 'std', 'count'])

    # Find peak and trough months
    peak_month = monthly_avg['mean'].idxmax()
    trough_month = monthly_avg['mean'].idxmin()

    # Seasonal amplitude (as fraction of mean)
    amplitude = (monthly_avg['mean'].max() - monthly_avg['mean'].min()) / monthly_avg['mean'].mean()

    return {
        'peak_month': peak_month,
        'trough_month': trough_month,
        'amplitude': amplitude,
        'monthly_stats': monthly_avg
    }

def main():
    print("=" * 70)
    print("MARBLE FORK KAWEAH RIVER - PATTERN ANALYSIS")
    print("Looking for cycles, correlations, and time-lagged relationships")
    print("=" * 70)

    # Load data
    pivoted = load_and_pivot_data()

    # 1. CYCLE ANALYSIS
    print("\n" + "=" * 70)
    print("1. DOMINANT CYCLES (FFT Analysis)")
    print("=" * 70)

    cycle_results = []
    for col in pivoted.columns:
        cycles = analyze_cycles(pivoted[col], col)
        if cycles:
            for c in cycles:
                cycle_results.append({
                    'parameter': col[:50],
                    'period_months': c['period_months'],
                    'relative_power': c['relative_power']
                })

    if cycle_results:
        cycle_df = pd.DataFrame(cycle_results)
        cycle_df = cycle_df.sort_values('relative_power', ascending=False)

        print("\nStrongest cycles found:")
        for _, row in cycle_df.head(20).iterrows():
            period = row['period_months']
            if period >= 12:
                period_str = f"{period/12:.1f} years"
            else:
                period_str = f"{period:.1f} months"
            print(f"  {row['parameter'][:45]:45} | {period_str:12} | power={row['relative_power']:.3f}")

    # 2. SEASONAL PATTERNS
    print("\n" + "=" * 70)
    print("2. SEASONAL PATTERNS")
    print("=" * 70)

    month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    seasonal_results = []
    for col in pivoted.columns:
        result = seasonal_decomposition(pivoted[col], col)
        if result and result['amplitude'] > 0.1:  # At least 10% seasonal variation
            seasonal_results.append({
                'parameter': col[:50],
                'peak_month': result['peak_month'],
                'trough_month': result['trough_month'],
                'amplitude': result['amplitude']
            })

    seasonal_df = pd.DataFrame(seasonal_results).sort_values('amplitude', ascending=False)

    print("\nParameters with strong seasonality (>10% amplitude):")
    for _, row in seasonal_df.iterrows():
        print(f"  {row['parameter'][:45]:45} | Peak: {month_names[row['peak_month']]:3} | Trough: {month_names[row['trough_month']]:3} | Amp: {row['amplitude']*100:.0f}%")

    # 3. CROSS-CORRELATIONS WITH LAGS
    print("\n" + "=" * 70)
    print("3. LEAD-LAG RELATIONSHIPS")
    print("(Which parameters predict others?)")
    print("=" * 70)

    lag_df = find_leading_indicators(pivoted)

    # Show relationships where lag matters
    significant_lags = lag_df[
        (lag_df['lag_improves'] == True) &
        (lag_df['pvalue'] < 0.05) &
        (lag_df['best_lag_months'] != 0)
    ].sort_values('best_correlation', key=abs, ascending=False)

    print("\nSignificant lead-lag relationships (lag improves correlation):")
    for _, row in significant_lags.head(15).iterrows():
        lag = row['best_lag_months']
        if lag > 0:
            leader = row['param1']
            follower = row['param2']
        else:
            leader = row['param2']
            follower = row['param1']
            lag = -lag

        print(f"  {leader[:35]:35} → {follower[:35]:35} | lag: {lag} mo | r={row['best_correlation']:+.3f}")

    # 4. SYNCHRONOUS PAIRS
    print("\n" + "=" * 70)
    print("4. SYNCHRONOUS PAIRS (move together)")
    print("=" * 70)

    sync_pairs = lag_df[
        (lag_df['best_lag_months'] == 0) &
        (abs(lag_df['zero_lag_correlation']) > 0.5) &
        (lag_df['pvalue'] < 0.01)
    ].sort_values('zero_lag_correlation', key=abs, ascending=False)

    print("\nStrongly correlated parameter pairs (|r| > 0.5):")
    for _, row in sync_pairs.head(20).iterrows():
        corr = row['zero_lag_correlation']
        direction = "+" if corr > 0 else "-"
        print(f"  {row['param1'][:35]:35} ↔ {row['param2'][:35]:35} | r={corr:+.3f}")

    # 5. ANTI-CORRELATED PAIRS
    print("\n" + "=" * 70)
    print("5. ANTI-CORRELATED PAIRS (move opposite)")
    print("=" * 70)

    anti_pairs = lag_df[
        (lag_df['zero_lag_correlation'] < -0.3) &
        (lag_df['pvalue'] < 0.05)
    ].sort_values('zero_lag_correlation')

    print("\nNegatively correlated pairs:")
    for _, row in anti_pairs.head(10).iterrows():
        print(f"  {row['param1'][:35]:35} ↔ {row['param2'][:35]:35} | r={row['zero_lag_correlation']:+.3f}")

    # 6. SUMMARY: Cluster Analysis
    print("\n" + "=" * 70)
    print("6. PARAMETER CLUSTERS (based on correlation structure)")
    print("=" * 70)

    # Build correlation matrix for key params
    monthly = pivoted.resample('M').mean()
    key_cols = [c for c in monthly.columns if any(k.lower() in c.lower()
                for k in ['calcium', 'magnesium', 'sodium', 'potassium',
                         'chloride', 'sulfate', 'silica', 'alkalinity',
                         'conductance', 'dissolved solids', 'temperature', 'ph'])]

    if len(key_cols) >= 5:
        corr_matrix = monthly[key_cols].corr()

        # Find clusters by correlation
        print("\nCorrelation clusters (parameters that move together):")

        # Simple clustering: group highly correlated params
        clustered = set()
        cluster_id = 1

        for col in corr_matrix.columns:
            if col in clustered:
                continue

            # Find all params correlated > 0.6 with this one
            related = corr_matrix[col][corr_matrix[col] > 0.6].index.tolist()
            if len(related) > 1:
                print(f"\n  Cluster {cluster_id} (move together):")
                for r in related:
                    if r not in clustered:
                        print(f"    - {r[:50]}")
                        clustered.add(r)
                cluster_id += 1

    # Save results
    lag_df.to_csv(OUTPUT_DIR / 'marble_fork_correlations.csv', index=False)
    print(f"\nCorrelation results saved to: {OUTPUT_DIR / 'marble_fork_correlations.csv'}")

    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)

    return pivoted, lag_df, cycle_df if cycle_results else None

if __name__ == "__main__":
    pivoted, lag_df, cycle_df = main()
