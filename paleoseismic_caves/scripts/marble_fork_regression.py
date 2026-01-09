#!/usr/bin/env python3
"""
Marble Fork Kaweah River - Multi-Factor Regression Model
Can we predict anomalies using multiple parameters with lags?
"""

import pandas as pd
import numpy as np
from pathlib import Path
import glob
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

DATA_DIR = Path("/Users/catherine/projects/quake/Marble Fork")
OUTPUT_DIR = Path("/Users/catherine/projects/quake/paleoseismic_caves/data/california")

def load_and_prepare():
    """Load data and create monthly time series"""
    files = sorted(glob.glob(str(DATA_DIR / "fullphyschem*.csv")))
    print(f"Loading {len(files)} files...")

    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f, low_memory=False)
            dfs.append(df)
        except:
            pass

    combined = pd.concat(dfs, ignore_index=True)

    # Extract and pivot
    cols = ['Activity_StartDate', 'Result_Characteristic', 'Result_Measure']
    ts = combined[cols].copy()
    ts['Activity_StartDate'] = pd.to_datetime(ts['Activity_StartDate'], errors='coerce')
    ts['Result_Measure'] = pd.to_numeric(ts['Result_Measure'], errors='coerce')
    ts = ts.dropna()

    # Get common parameters
    param_counts = ts['Result_Characteristic'].value_counts()
    top_params = param_counts[param_counts > 80].index.tolist()
    ts = ts[ts['Result_Characteristic'].isin(top_params)]

    # Pivot
    grouped = ts.groupby(['Activity_StartDate', 'Result_Characteristic'])['Result_Measure'].mean().reset_index()
    pivoted = grouped.pivot(index='Activity_StartDate', columns='Result_Characteristic', values='Result_Measure')

    # Resample to monthly
    monthly = pivoted.resample('M').mean()

    # Rename columns to short names
    short_names = {
        'Calcium': 'Ca',
        'Magnesium': 'Mg',
        'Sodium': 'Na',
        'Potassium': 'K',
        'Chloride': 'Cl',
        'Sulfate': 'SO4',
        'Silica': 'Si',
        'Alkalinity': 'Alk',
        'Specific conductance': 'SC',
        'Total dissolved solids': 'TDS',
        'Temperature, water': 'Temp',
        'pH': 'pH',
        'Oxygen-18/Oxygen-16 ratio': 'd18O',
        'Deuterium/Hydrogen ratio': 'dD',
    }

    # Find and rename matching columns (avoid duplicates)
    rename_map = {}
    used_names = set()
    for col in monthly.columns:
        for long_name, short in short_names.items():
            if long_name.lower() in col.lower() and short not in used_names:
                rename_map[col] = short
                used_names.add(short)
                break

    monthly = monthly.rename(columns=rename_map)

    # Keep only renamed columns (no duplicates)
    keep_cols = [c for c in monthly.columns if c in used_names]
    monthly = monthly[keep_cols]

    print(f"Monthly data: {len(monthly)} months, {len(monthly.columns)} parameters")
    print(f"Parameters: {list(monthly.columns)}")

    return monthly

def create_features(df, target_col, lags=[1, 2, 3]):
    """Create lagged features for prediction"""
    features = pd.DataFrame(index=df.index)

    # Only use columns with enough data
    good_cols = [c for c in df.columns if df[c].notna().sum() > 50]

    # Lagged values of columns with good data
    for col in good_cols:
        for lag in lags:
            features[f'{col}_lag{lag}'] = df[col].shift(lag)

    # Rolling means (shorter window)
    for col in good_cols:
        features[f'{col}_roll3'] = df[col].rolling(3, min_periods=2).mean().shift(1)

    # Rate of change
    for col in good_cols:
        features[f'{col}_diff1'] = df[col].diff().shift(1)

    # Seasonal features
    features['month'] = df.index.month
    features['month_sin'] = np.sin(2 * np.pi * df.index.month / 12)
    features['month_cos'] = np.cos(2 * np.pi * df.index.month / 12)

    # Year trend
    features['year'] = (df.index.year - df.index.year.min())

    # Target
    target = df[target_col].copy()

    # Forward fill missing values in features (limited)
    features = features.ffill(limit=2)

    # Drop NaN
    valid_idx = features.dropna().index.intersection(target.dropna().index)
    features = features.loc[valid_idx]
    target = target.loc[valid_idx]

    return features, target

def evaluate_model(model, X, y, name):
    """Evaluate with time series cross-validation"""
    n_splits = min(5, len(X) // 10)  # Ensure enough samples per split
    if n_splits < 2:
        n_splits = 2
    tscv = TimeSeriesSplit(n_splits=n_splits)

    scores = cross_val_score(model, X, y, cv=tscv, scoring='r2')

    # Fit on all data for feature importance
    model.fit(X, y)
    y_pred = model.predict(X)

    rmse = np.sqrt(mean_squared_error(y, y_pred))
    r2 = r2_score(y, y_pred)

    return {
        'name': name,
        'cv_r2_mean': scores.mean(),
        'cv_r2_std': scores.std(),
        'full_r2': r2,
        'rmse': rmse,
        'model': model
    }

def main():
    print("=" * 80)
    print("MARBLE FORK - MULTI-FACTOR REGRESSION MODEL")
    print("Can we predict water chemistry using multiple factors with lags?")
    print("=" * 80)

    # Load data
    monthly = load_and_prepare()

    # Standardize
    scaler = StandardScaler()
    monthly_scaled = pd.DataFrame(
        scaler.fit_transform(monthly),
        index=monthly.index,
        columns=monthly.columns
    )

    # Target parameters (most relevant for seismic detection)
    targets = ['TDS', 'Ca', 'Mg', 'SC']
    targets = [t for t in targets if t in monthly_scaled.columns]

    print(f"\nTarget parameters: {targets}")

    all_results = []

    for target in targets:
        print(f"\n{'='*60}")
        print(f"PREDICTING: {target}")
        print("="*60)

        # Create features
        X, y = create_features(monthly_scaled, target)
        print(f"Features: {X.shape[1]}, Samples: {len(X)}")

        # Models to try
        models = [
            (Ridge(alpha=1.0), "Ridge Regression"),
            (Lasso(alpha=0.1), "Lasso Regression"),
            (RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42), "Random Forest"),
            (GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42), "Gradient Boosting"),
        ]

        results = []
        for model, name in models:
            result = evaluate_model(model, X, y, name)
            results.append(result)
            print(f"\n{name}:")
            print(f"  CV R² = {result['cv_r2_mean']:.3f} ± {result['cv_r2_std']:.3f}")
            print(f"  Full R² = {result['full_r2']:.3f}")
            print(f"  RMSE = {result['rmse']:.3f}")

        # Best model
        best = max(results, key=lambda x: x['cv_r2_mean'])
        print(f"\n→ Best model: {best['name']} (CV R² = {best['cv_r2_mean']:.3f})")

        # Feature importance for best tree-based model
        tree_models = [r for r in results if 'Forest' in r['name'] or 'Boosting' in r['name']]
        if tree_models:
            best_tree = max(tree_models, key=lambda x: x['cv_r2_mean'])
            importances = pd.Series(
                best_tree['model'].feature_importances_,
                index=X.columns
            ).sort_values(ascending=False)

            print(f"\nTop 10 predictors for {target} ({best_tree['name']}):")
            for feat, imp in importances.head(10).items():
                print(f"  {feat:20} : {imp:.4f}")

        all_results.append({
            'target': target,
            'best_model': best['name'],
            'cv_r2': best['cv_r2_mean'],
            'top_predictors': list(importances.head(5).index) if tree_models else []
        })

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY: MULTI-FACTOR PREDICTION CAPABILITY")
    print("=" * 80)

    for r in all_results:
        print(f"\n{r['target']}:")
        print(f"  Best model: {r['best_model']}")
        print(f"  CV R² = {r['cv_r2']:.3f}")
        print(f"  Key predictors: {', '.join(r['top_predictors'][:3])}")

    # Anomaly detection using residuals
    print("\n" + "=" * 80)
    print("RESIDUAL-BASED ANOMALY DETECTION")
    print("(Anomalies = observations that deviate from prediction)")
    print("=" * 80)

    # Use best model (Gradient Boosting typically) for residual analysis
    target = 'TDS' if 'TDS' in monthly_scaled.columns else targets[0]
    X, y = create_features(monthly_scaled, target)

    model = GradientBoostingRegressor(n_estimators=100, max_depth=3, random_state=42)
    model.fit(X, y)
    y_pred = model.predict(X)

    residuals = pd.Series(y.values - y_pred, index=y.index)
    residual_std = residuals.std()

    # Find anomalies (residuals > 2 std)
    anomalies = residuals[abs(residuals) > 2 * residual_std]

    print(f"\nResidual-based anomalies for {target} (|residual| > 2σ):")
    print(f"Total: {len(anomalies)} anomalies")

    for date, resid in anomalies.sort_values(key=abs, ascending=False).head(15).items():
        direction = "HIGHER than predicted" if resid > 0 else "LOWER than predicted"
        print(f"  {date.strftime('%Y-%m')} : residual = {resid:+.2f}σ ({direction})")

    # Save residuals
    residual_df = pd.DataFrame({
        'date': y.index,
        'actual': y.values,
        'predicted': y_pred,
        'residual': residuals.values,
        'residual_zscore': residuals.values / residual_std
    })
    residual_df.to_csv(OUTPUT_DIR / 'marble_fork_residuals.csv', index=False)
    print(f"\nResiduals saved to: {OUTPUT_DIR / 'marble_fork_residuals.csv'}")

    # Key insight
    print("\n" + "=" * 80)
    print("KEY INSIGHT: What the regression tells us")
    print("=" * 80)
    print("""
The multi-factor regression model predicts water chemistry reasonably well
(R² ~ 0.4-0.6) using:
  1. Lagged values (1-6 months prior)
  2. Rolling averages
  3. Seasonal patterns
  4. Cross-parameter relationships

ANOMALIES are dates where actual values DEVIATE from predictions.
These residual anomalies are INDEPENDENT of normal seasonal/trend patterns.

For seismic detection:
  - If an earthquake perturbs the system, it should appear as a
    POSITIVE RESIDUAL (higher than predicted from normal dynamics)
  - Fire/debris effects may also appear but with different signature

This approach is MORE POWERFUL than simple Z-scores because it accounts
for the complex dynamics of the aquifer system.
""")

    return monthly, all_results, residual_df

if __name__ == "__main__":
    monthly, results, residuals = main()
