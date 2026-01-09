#!/usr/bin/env python3
"""
Marble Fork Kaweah River - Forward-Looking Earthquake Prediction
USGS-11206820 - Downstream of Crystal Cave, Sequoia National Park

CRITICAL CONSTRAINT: Only past data used to predict - NO look-ahead bias.
- Data from Jan 2025 cannot predict events in 2024
- At each time t, only data from times < t is used

Two resolutions tested:
1. DAILY: Raw sample dates (~2-4 week gaps) - catches short-term precursors
2. MONTHLY: Aggregated means - more robust statistics

Target: M5.0+ earthquakes within 250km of Marble Fork (36.58°N, 118.82°W)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import glob
from datetime import datetime, timedelta
from scipy import stats
from sklearn.ensemble import IsolationForest, RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import roc_auc_score, precision_score, recall_score, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

# Configuration
DATA_DIR = Path("/Users/catherine/projects/quake/Marble Fork")
OUTPUT_DIR = Path("/Users/catherine/projects/quake/paleoseismic_caves/data/california")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MARBLE_FORK_LAT = 36.58
MARBLE_FORK_LON = -118.82

# M5.0+ earthquakes within 250km (from USGS search)
EARTHQUAKES = [
    {"date": "2012-10-20", "mag": 5.29, "place": "San Lucas, CA", "distance_km": 180},
    {"date": "2013-02-12", "mag": 5.1, "place": "Dyer, Nevada", "distance_km": 195},
    {"date": "2016-12-28", "mag": 5.6, "place": "Hawthorne, Nevada", "distance_km": 210},
    {"date": "2019-07-04", "mag": 6.4, "place": "Ridgecrest foreshock", "distance_km": 142},
    {"date": "2019-07-05", "mag": 7.1, "place": "Ridgecrest mainshock", "distance_km": 142},
    {"date": "2019-07-05", "mag": 5.5, "place": "Ridgecrest aftershock", "distance_km": 145},
    {"date": "2019-07-05", "mag": 5.44, "place": "Little Lake", "distance_km": 140},
    {"date": "2019-07-05", "mag": 5.37, "place": "Searles Valley", "distance_km": 145},
    {"date": "2020-04-11", "mag": 5.24, "place": "Bodie, CA", "distance_km": 175},
    {"date": "2020-05-15", "mag": 6.5, "place": "Monte Cristo Range", "distance_km": 196},
    {"date": "2020-05-15", "mag": 5.1, "place": "Mina, Nevada", "distance_km": 195},
    {"date": "2020-05-20", "mag": 5.0, "place": "Mina, Nevada", "distance_km": 200},
    {"date": "2020-05-21", "mag": 5.1, "place": "Mina, Nevada", "distance_km": 198},
    {"date": "2020-06-03", "mag": 5.51, "place": "Searles Valley", "distance_km": 150},
    {"date": "2020-06-24", "mag": 5.8, "place": "Lone Pine", "distance_km": 95},
    {"date": "2020-06-30", "mag": 5.0, "place": "Mina, Nevada", "distance_km": 200},
    {"date": "2020-11-13", "mag": 5.3, "place": "Mina, Nevada", "distance_km": 200},
    {"date": "2020-12-01", "mag": 5.1, "place": "Mina, Nevada", "distance_km": 195},
    {"date": "2021-07-08", "mag": 6.0, "place": "Antelope Valley", "distance_km": 223},
    {"date": "2021-07-08", "mag": 5.03, "place": "Markleeville", "distance_km": 225},
    {"date": "2023-08-20", "mag": 5.08, "place": "Ojai, CA", "distance_km": 240},
    {"date": "2024-08-06", "mag": 5.22, "place": "Lamont, CA", "distance_km": 170},
]

# Key seismic proxy parameters (based on Chiodini hydrogeochemical model)
SEISMIC_PARAMS = [
    'Calcium', 'Magnesium', 'Sodium', 'Potassium', 'Chloride', 'Sulfate',
    'Silica', 'Alkalinity', 'Specific conductance', 'Total dissolved solids',
    'pH', 'Temperature, water'
]


def load_raw_data():
    """Load all CSV files and extract time series"""
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

    # Extract relevant columns
    cols = ['Activity_StartDate', 'Result_Characteristic', 'Result_Measure']
    ts = combined[cols].copy()
    ts['Activity_StartDate'] = pd.to_datetime(ts['Activity_StartDate'], errors='coerce')
    ts['Result_Measure'] = pd.to_numeric(ts['Result_Measure'], errors='coerce')
    ts = ts.dropna()
    ts = ts.rename(columns={'Activity_StartDate': 'date',
                            'Result_Characteristic': 'parameter',
                            'Result_Measure': 'value'})

    return ts


def prepare_daily_data(ts):
    """Prepare daily resolution data (raw sample dates)"""
    # Pivot: one row per date, columns = parameters
    # Take mean if multiple samples same day

    # Filter to seismic-relevant parameters
    seismic_ts = ts[ts['parameter'].apply(lambda x: any(p.lower() in x.lower() for p in SEISMIC_PARAMS))]

    # Simplify parameter names
    def simplify_param(p):
        for sp in SEISMIC_PARAMS:
            if sp.lower() in p.lower():
                return sp
        return p

    seismic_ts = seismic_ts.copy()
    seismic_ts['param_simple'] = seismic_ts['parameter'].apply(simplify_param)

    # Pivot
    daily = seismic_ts.groupby(['date', 'param_simple'])['value'].mean().unstack()
    daily = daily.sort_index()

    print(f"\nDaily data: {len(daily)} sample dates, {len(daily.columns)} parameters")
    print(f"Date range: {daily.index.min().strftime('%Y-%m-%d')} to {daily.index.max().strftime('%Y-%m-%d')}")
    print(f"Parameters: {list(daily.columns)}")

    return daily


def prepare_monthly_data(daily):
    """Aggregate to monthly means"""
    monthly = daily.resample('M').mean()
    monthly = monthly.dropna(how='all')

    print(f"\nMonthly data: {len(monthly)} months")

    return monthly


def forward_looking_zscore(data, min_history=12):
    """
    Calculate Z-scores using ONLY past data (expanding window).

    At each time t, Z-score is calculated from data[0:t-1] statistics.
    First min_history points get NaN (not enough history).
    """
    result = pd.DataFrame(index=data.index, columns=data.columns, dtype=float)

    for i in range(len(data)):
        if i < min_history:
            continue

        # Use only past data
        historical = data.iloc[:i]
        current = data.iloc[i]

        for col in data.columns:
            hist_vals = historical[col].dropna()
            if len(hist_vals) >= min_history:
                mean = hist_vals.mean()
                std = hist_vals.std()
                if std > 0:
                    result.iloc[i][col] = (current[col] - mean) / std

    return result


def forward_looking_anomaly_score(data, min_history=12):
    """
    Calculate composite anomaly score using forward-looking Z-scores.
    Positive = more anomalous.
    """
    zscores = forward_looking_zscore(data, min_history)

    # Composite: mean of absolute Z-scores across parameters
    anomaly_score = zscores.abs().mean(axis=1)

    # Also track max Z-score
    max_z = zscores.abs().max(axis=1)

    # Count of parameters with |Z| > 2
    n_anomalous = (zscores.abs() > 2).sum(axis=1)

    return pd.DataFrame({
        'anomaly_score': anomaly_score,
        'max_z': max_z,
        'n_anomalous_params': n_anomalous
    }, index=data.index)


def create_earthquake_labels(data_index, earthquakes, windows_days=[7, 14, 30, 90, 180]):
    """
    Create binary labels: 1 if earthquake within next N days.

    FORWARD-LOOKING: At time t, label indicates if earthquake happens in [t, t+window].
    """
    eq_dates = pd.to_datetime([eq['date'] for eq in earthquakes])

    labels = pd.DataFrame(index=data_index)

    for window in windows_days:
        col_name = f'eq_within_{window}d'
        labels[col_name] = 0

        for date in data_index:
            # Check if any earthquake in [date, date + window]
            future_window_end = date + timedelta(days=window)
            hits = eq_dates[(eq_dates >= date) & (eq_dates <= future_window_end)]
            if len(hits) > 0:
                labels.loc[date, col_name] = 1

    return labels


def precursor_analysis(anomaly_scores, earthquakes, pre_windows_days=[7, 14, 30, 60, 90]):
    """
    Compare anomaly scores in pre-earthquake windows vs baseline periods.

    FORWARD-LOOKING: We're asking "given these anomaly scores, did an earthquake follow?"
    """
    print("\n" + "=" * 70)
    print("PRECURSOR ANALYSIS")
    print("Comparing anomaly scores BEFORE earthquakes vs. baseline periods")
    print("=" * 70)

    results = []

    for window_days in pre_windows_days:
        pre_eq_scores = []
        baseline_scores = []

        eq_dates = pd.to_datetime([eq['date'] for eq in earthquakes])

        for date, row in anomaly_scores.iterrows():
            if pd.isna(row['anomaly_score']):
                continue

            score = row['anomaly_score']

            # Check if this date is in pre-earthquake window
            days_until_eq = [(eq_date - date).days for eq_date in eq_dates]
            days_until_eq = [d for d in days_until_eq if 0 < d <= window_days]

            if len(days_until_eq) > 0:
                pre_eq_scores.append(score)
            else:
                # Check if far from any earthquake (baseline)
                min_days_to_eq = min([abs((eq_date - date).days) for eq_date in eq_dates])
                if min_days_to_eq > window_days * 2:  # Far from earthquakes
                    baseline_scores.append(score)

        if len(pre_eq_scores) > 3 and len(baseline_scores) > 10:
            # Statistical test
            statistic, pvalue = stats.mannwhitneyu(pre_eq_scores, baseline_scores, alternative='greater')

            result = {
                'window_days': window_days,
                'n_pre_eq': len(pre_eq_scores),
                'n_baseline': len(baseline_scores),
                'pre_eq_mean': np.mean(pre_eq_scores),
                'baseline_mean': np.mean(baseline_scores),
                'ratio': np.mean(pre_eq_scores) / np.mean(baseline_scores) if np.mean(baseline_scores) > 0 else np.nan,
                'pvalue': pvalue,
                'significant': pvalue < 0.05
            }
            results.append(result)

            sig = "**SIGNIFICANT**" if pvalue < 0.05 else ""
            print(f"\n{window_days}-day window:")
            print(f"  Pre-earthquake samples: {len(pre_eq_scores)}, mean score: {np.mean(pre_eq_scores):.3f}")
            print(f"  Baseline samples: {len(baseline_scores)}, mean score: {np.mean(baseline_scores):.3f}")
            print(f"  Ratio (pre-eq/baseline): {result['ratio']:.2f}x")
            print(f"  Mann-Whitney U p-value: {pvalue:.4f} {sig}")

    return pd.DataFrame(results)


def monte_carlo_test(anomaly_scores, earthquakes, n_permutations=10000, window_days=30):
    """
    Monte Carlo significance test: shuffle earthquake dates and compare.

    Null hypothesis: Anomaly scores are random with respect to earthquake timing.
    """
    print("\n" + "=" * 70)
    print(f"MONTE CARLO SIGNIFICANCE TEST (n={n_permutations})")
    print(f"Window: {window_days} days before earthquake")
    print("=" * 70)

    eq_dates = pd.to_datetime([eq['date'] for eq in earthquakes])

    # Calculate observed statistic: mean anomaly score before earthquakes
    def calc_pre_eq_mean(eq_dates_list, scores_df):
        pre_eq_scores = []
        for date, row in scores_df.iterrows():
            if pd.isna(row['anomaly_score']):
                continue
            days_until_eq = [(eq_date - date).days for eq_date in eq_dates_list]
            days_until_eq = [d for d in days_until_eq if 0 < d <= window_days]
            if len(days_until_eq) > 0:
                pre_eq_scores.append(row['anomaly_score'])
        return np.mean(pre_eq_scores) if pre_eq_scores else 0

    observed = calc_pre_eq_mean(eq_dates, anomaly_scores)
    print(f"Observed pre-earthquake mean anomaly score: {observed:.4f}")

    # Permutation test: shuffle earthquake dates within data range
    data_start = anomaly_scores.index.min()
    data_end = anomaly_scores.index.max()
    date_range_days = (data_end - data_start).days

    null_distribution = []

    for i in range(n_permutations):
        # Generate random earthquake dates
        random_offsets = np.random.randint(0, date_range_days, size=len(eq_dates))
        random_eq_dates = [data_start + timedelta(days=int(offset)) for offset in random_offsets]

        null_stat = calc_pre_eq_mean(random_eq_dates, anomaly_scores)
        null_distribution.append(null_stat)

    null_distribution = np.array(null_distribution)

    # P-value: proportion of null >= observed
    pvalue = np.mean(null_distribution >= observed)

    print(f"Null distribution: mean={np.mean(null_distribution):.4f}, std={np.std(null_distribution):.4f}")
    print(f"P-value (one-tailed): {pvalue:.4f}")

    if pvalue < 0.05:
        print(">>> SIGNIFICANT at p<0.05: Anomalies are elevated before earthquakes!")
    elif pvalue < 0.10:
        print(">>> Marginally significant (p<0.10)")
    else:
        print(">>> Not significant: Cannot reject null hypothesis")

    return {
        'observed': observed,
        'null_mean': np.mean(null_distribution),
        'null_std': np.std(null_distribution),
        'pvalue': pvalue,
        'percentile': stats.percentileofscore(null_distribution, observed)
    }


def ml_prediction(data, earthquakes, target_window_days=30, min_train_months=24):
    """
    ML prediction with strict temporal cross-validation.

    Train on past data only, predict future earthquakes.
    """
    print("\n" + "=" * 70)
    print("MACHINE LEARNING PREDICTION (Temporal Cross-Validation)")
    print(f"Target: Earthquake within {target_window_days} days")
    print("=" * 70)

    # Create features
    features = data.copy()

    # Add lagged features
    for lag in [1, 2, 3]:
        for col in data.columns:
            features[f'{col}_lag{lag}'] = data[col].shift(lag)

    # Add rolling features
    for col in data.columns:
        features[f'{col}_roll3_mean'] = data[col].rolling(3, min_periods=1).mean().shift(1)
        features[f'{col}_roll3_std'] = data[col].rolling(3, min_periods=1).std().shift(1)

    # Add rate of change
    for col in data.columns:
        features[f'{col}_diff'] = data[col].diff().shift(1)

    # Create labels
    labels = create_earthquake_labels(data.index, earthquakes, [target_window_days])
    target_col = f'eq_within_{target_window_days}d'

    # Merge and drop NaN
    combined = features.join(labels[[target_col]])
    combined = combined.dropna()

    X = combined.drop(columns=[target_col])
    y = combined[target_col]

    print(f"Samples: {len(y)}, Positive (pre-earthquake): {y.sum()} ({100*y.mean():.1f}%)")

    if y.sum() < 5:
        print(">>> Too few positive samples for reliable ML prediction")
        return None

    # Temporal split: train on first 70%, test on last 30%
    split_idx = int(len(X) * 0.7)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    print(f"Train: {len(y_train)} samples ({y_train.sum()} positive)")
    print(f"Test: {len(y_test)} samples ({y_test.sum()} positive)")

    if y_train.sum() < 3 or y_test.sum() < 2:
        print(">>> Not enough positive samples in train/test splits")
        return None

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Try multiple models
    models = [
        ('Random Forest', RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42, class_weight='balanced')),
        ('Gradient Boosting', GradientBoostingClassifier(n_estimators=100, max_depth=3, random_state=42)),
    ]

    results = []
    for name, model in models:
        model.fit(X_train_scaled, y_train)
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        y_pred = model.predict(X_test_scaled)

        try:
            auc = roc_auc_score(y_test, y_pred_proba)
        except:
            auc = np.nan

        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)

        print(f"\n{name}:")
        print(f"  ROC-AUC: {auc:.3f}")
        print(f"  Precision: {precision:.3f}")
        print(f"  Recall: {recall:.3f}")

        results.append({
            'model': name,
            'auc': auc,
            'precision': precision,
            'recall': recall
        })

        # Feature importance
        if hasattr(model, 'feature_importances_'):
            importances = pd.Series(model.feature_importances_, index=X.columns)
            top_features = importances.nlargest(10)
            print(f"  Top features:")
            for feat, imp in top_features.items():
                print(f"    {feat}: {imp:.3f}")

    return pd.DataFrame(results)


def ridgecrest_case_study(anomaly_scores, daily_zscores):
    """
    Detailed analysis of the Ridgecrest M7.1 sequence (July 4-5, 2019).

    The big question: Were there precursory signals?
    """
    print("\n" + "=" * 70)
    print("RIDGECREST M7.1 CASE STUDY")
    print("Mainshock: 2019-07-05, Distance: 142 km")
    print("=" * 70)

    ridgecrest_date = pd.Timestamp('2019-07-05')

    # Look at 6 months before
    window_start = ridgecrest_date - timedelta(days=180)

    # Filter to pre-Ridgecrest window
    pre_rc = anomaly_scores[(anomaly_scores.index >= window_start) &
                            (anomaly_scores.index < ridgecrest_date)]

    if len(pre_rc) == 0:
        print("No data in pre-Ridgecrest window")
        return

    print(f"\nAnomaly scores in 6 months before Ridgecrest:")
    print(f"Samples: {len(pre_rc)}")

    # Find peaks
    high_anomaly = pre_rc[pre_rc['anomaly_score'] > pre_rc['anomaly_score'].quantile(0.75)]

    print(f"\nHigh anomaly dates (top 25%):")
    for date, row in high_anomaly.iterrows():
        days_before = (ridgecrest_date - date).days
        print(f"  {date.strftime('%Y-%m-%d')} ({days_before} days before): score={row['anomaly_score']:.2f}, max_z={row['max_z']:.2f}")

    # Look at individual parameter Z-scores
    if daily_zscores is not None:
        pre_rc_z = daily_zscores[(daily_zscores.index >= window_start) &
                                  (daily_zscores.index < ridgecrest_date)]

        # Find any |Z| > 2 anomalies
        print(f"\nParameter-level anomalies (|Z| > 2) before Ridgecrest:")
        for date, row in pre_rc_z.iterrows():
            anomalous = row[row.abs() > 2].dropna()
            if len(anomalous) > 0:
                days_before = (ridgecrest_date - date).days
                params = ", ".join([f"{p}={v:+.2f}" for p, v in anomalous.items()])
                print(f"  {date.strftime('%Y-%m-%d')} ({days_before}d before): {params}")


def flag_fire_periods(data):
    """Flag periods likely affected by wildfires (KNP Complex, etc.)"""
    fire_periods = [
        ('2021-09-01', '2022-06-01', 'KNP Complex Fire aftermath'),
    ]

    data['fire_flag'] = ''
    for start, end, name in fire_periods:
        mask = (data.index >= start) & (data.index <= end)
        data.loc[mask, 'fire_flag'] = name

    return data


def main():
    print("=" * 80)
    print("MARBLE FORK - FORWARD-LOOKING EARTHQUAKE PREDICTION")
    print("Can water quality anomalies predict earthquakes?")
    print("CONSTRAINT: Only past data used - NO look-ahead bias")
    print("=" * 80)

    # Load data
    ts = load_raw_data()

    # Prepare both resolutions
    daily = prepare_daily_data(ts)
    monthly = prepare_monthly_data(daily)

    # Calculate forward-looking anomaly scores
    print("\n" + "=" * 70)
    print("CALCULATING FORWARD-LOOKING ANOMALY SCORES")
    print("(Using only historical data at each point)")
    print("=" * 70)

    print("\n--- DAILY RESOLUTION ---")
    daily_zscores = forward_looking_zscore(daily, min_history=20)
    daily_anomalies = forward_looking_anomaly_score(daily, min_history=20)
    daily_anomalies = flag_fire_periods(daily_anomalies)

    print(f"Daily anomaly scores computed: {daily_anomalies['anomaly_score'].notna().sum()} valid points")

    print("\n--- MONTHLY RESOLUTION ---")
    monthly_zscores = forward_looking_zscore(monthly, min_history=12)
    monthly_anomalies = forward_looking_anomaly_score(monthly, min_history=12)
    monthly_anomalies = flag_fire_periods(monthly_anomalies)

    print(f"Monthly anomaly scores computed: {monthly_anomalies['anomaly_score'].notna().sum()} valid points")

    # Precursor analysis
    print("\n\n########## DAILY RESOLUTION RESULTS ##########")
    daily_precursor = precursor_analysis(daily_anomalies, EARTHQUAKES,
                                         pre_windows_days=[7, 14, 30, 60, 90])

    print("\n\n########## MONTHLY RESOLUTION RESULTS ##########")
    monthly_precursor = precursor_analysis(monthly_anomalies, EARTHQUAKES,
                                           pre_windows_days=[30, 60, 90, 180])

    # Monte Carlo test
    print("\n\n########## MONTE CARLO TESTS ##########")

    print("\n--- DAILY (30-day window) ---")
    daily_mc_30 = monte_carlo_test(daily_anomalies, EARTHQUAKES, n_permutations=10000, window_days=30)

    print("\n--- DAILY (14-day window) ---")
    daily_mc_14 = monte_carlo_test(daily_anomalies, EARTHQUAKES, n_permutations=10000, window_days=14)

    print("\n--- MONTHLY (90-day window) ---")
    monthly_mc = monte_carlo_test(monthly_anomalies, EARTHQUAKES, n_permutations=10000, window_days=90)

    # ML prediction
    print("\n\n########## ML PREDICTION ##########")

    print("\n--- MONTHLY DATA, 30-DAY PREDICTION ---")
    ml_monthly_30 = ml_prediction(monthly, EARTHQUAKES, target_window_days=30)

    print("\n--- MONTHLY DATA, 90-DAY PREDICTION ---")
    ml_monthly_90 = ml_prediction(monthly, EARTHQUAKES, target_window_days=90)

    # Ridgecrest case study
    ridgecrest_case_study(daily_anomalies, daily_zscores)

    # Save results
    print("\n" + "=" * 70)
    print("SAVING RESULTS")
    print("=" * 70)

    # Save anomaly scores with fire flags
    daily_anomalies.to_csv(OUTPUT_DIR / 'marble_fork_daily_anomalies.csv')
    monthly_anomalies.to_csv(OUTPUT_DIR / 'marble_fork_monthly_anomalies.csv')
    daily_zscores.to_csv(OUTPUT_DIR / 'marble_fork_daily_zscores.csv')

    print(f"Saved: {OUTPUT_DIR / 'marble_fork_daily_anomalies.csv'}")
    print(f"Saved: {OUTPUT_DIR / 'marble_fork_monthly_anomalies.csv'}")
    print(f"Saved: {OUTPUT_DIR / 'marble_fork_daily_zscores.csv'}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print("\nPrecursor Analysis (Daily):")
    if len(daily_precursor) > 0:
        for _, row in daily_precursor.iterrows():
            sig = "***" if row['significant'] else ""
            print(f"  {row['window_days']:3d}-day: ratio={row['ratio']:.2f}x, p={row['pvalue']:.3f} {sig}")

    print("\nPrecursor Analysis (Monthly):")
    if len(monthly_precursor) > 0:
        for _, row in monthly_precursor.iterrows():
            sig = "***" if row['significant'] else ""
            print(f"  {row['window_days']:3d}-day: ratio={row['ratio']:.2f}x, p={row['pvalue']:.3f} {sig}")

    print("\nMonte Carlo Tests:")
    print(f"  Daily 14-day: p={daily_mc_14['pvalue']:.4f}, observed at {daily_mc_14['percentile']:.1f}th percentile")
    print(f"  Daily 30-day: p={daily_mc_30['pvalue']:.4f}, observed at {daily_mc_30['percentile']:.1f}th percentile")
    print(f"  Monthly 90-day: p={monthly_mc['pvalue']:.4f}, observed at {monthly_mc['percentile']:.1f}th percentile")

    return {
        'daily_anomalies': daily_anomalies,
        'monthly_anomalies': monthly_anomalies,
        'daily_precursor': daily_precursor,
        'monthly_precursor': monthly_precursor,
        'daily_mc': daily_mc_30,
        'monthly_mc': monthly_mc
    }


if __name__ == "__main__":
    results = main()
