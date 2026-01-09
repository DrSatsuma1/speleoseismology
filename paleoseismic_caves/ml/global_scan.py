"""
Global PELT Change Point Detection on SISAL δ18O Records

Runs unsupervised anomaly detection on ALL speleothem records in SISAL v3 database.
Uses ruptures library with PELT algorithm to find abrupt shifts in δ18O time series.

Output: Ranked list of all detected change points with:
- Entity/cave metadata
- Change point year (CE)
- Magnitude (z-score shift)
- Duration and recovery characteristics
"""

import numpy as np
import pandas as pd
import ruptures as rpt
from pathlib import Path
from typing import Dict, List, Tuple
import warnings

from sisal_loader import SISALLoader

warnings.filterwarnings('ignore')


class GlobalScanner:
    """Run PELT change point detection on all SISAL entities."""

    def __init__(self, penalty: float = 10.0, min_size: int = 3):
        """
        Initialize scanner.

        Args:
            penalty: PELT penalty parameter (higher = fewer change points)
            min_size: Minimum segment size between change points
        """
        self.penalty = penalty
        self.min_size = min_size

    def detect_change_points(self, signal: np.ndarray) -> List[int]:
        """
        Run PELT on a single time series.

        Args:
            signal: 1D array of δ18O z-scores

        Returns:
            List of change point indices
        """
        # Handle NaN values by interpolation
        signal = np.array(signal, dtype=float)
        nans = np.isnan(signal)
        if nans.all():
            return []
        if nans.any():
            # Linear interpolation for NaN values
            idx = np.arange(len(signal))
            signal[nans] = np.interp(idx[nans], idx[~nans], signal[~nans])

        # Need at least 2*min_size samples
        if len(signal) < 2 * self.min_size:
            return []

        # Run PELT with L2 cost (piecewise constant model)
        algo = rpt.Pelt(model="l2", min_size=self.min_size).fit(signal)
        try:
            change_points = algo.predict(pen=self.penalty)
            # Remove the last element (always equals signal length)
            return change_points[:-1]
        except Exception as e:
            return []

    def characterize_change_point(self, signal: np.ndarray, ages: np.ndarray,
                                   cp_idx: int, window: int = 10) -> dict:
        """
        Characterize a single change point.

        Args:
            signal: z-score time series
            ages: corresponding ages (CE)
            cp_idx: index of change point
            window: samples before/after to analyze

        Returns:
            Dict with change point characteristics
        """
        n = len(signal)

        # Get before/after windows
        before_start = max(0, cp_idx - window)
        after_end = min(n, cp_idx + window)

        before = signal[before_start:cp_idx]
        after = signal[cp_idx:after_end]

        # Calculate shift magnitude
        if len(before) > 0 and len(after) > 0:
            mean_before = np.nanmean(before)
            mean_after = np.nanmean(after)
            shift = mean_after - mean_before
        else:
            mean_before = mean_after = shift = np.nan

        # Get age at change point
        age_ce = ages[cp_idx] if cp_idx < len(ages) else np.nan

        # Estimate recovery time (how long until signal returns to baseline)
        recovery_samples = 0
        baseline = mean_before
        for i in range(cp_idx, min(n, cp_idx + 50)):
            if abs(signal[i] - baseline) < 0.5:  # Within 0.5 sigma
                break
            recovery_samples += 1

        # Convert samples to years (estimate)
        if cp_idx > 0 and cp_idx < len(ages) - 1:
            years_per_sample = abs(ages[cp_idx + 1] - ages[cp_idx - 1]) / 2
        else:
            years_per_sample = np.nan

        recovery_years = recovery_samples * years_per_sample if not np.isnan(years_per_sample) else np.nan

        return {
            'year_ce': age_ce,
            'shift_magnitude': shift,
            'mean_before': mean_before,
            'mean_after': mean_after,
            'recovery_samples': recovery_samples,
            'recovery_years': recovery_years,
            'years_per_sample': years_per_sample
        }

    def scan_entity(self, entity_data: dict) -> List[dict]:
        """
        Scan a single entity for change points.

        Args:
            entity_data: Dict with 'ages', 'd18O_z', 'metadata'

        Returns:
            List of detected anomalies with characteristics
        """
        signal = entity_data['d18O_z']
        ages = entity_data['ages']
        metadata = entity_data['metadata']

        # Detect change points
        change_points = self.detect_change_points(signal)

        # Characterize each
        anomalies = []
        for cp_idx in change_points:
            char = self.characterize_change_point(signal, ages, cp_idx)

            # Only keep significant shifts (>1 sigma)
            if abs(char['shift_magnitude']) < 1.0:
                continue

            anomaly = {
                'entity_id': metadata.get('entity_id', None),
                'site_name': metadata['site_name'],
                'entity_name': metadata['entity_name'],
                'lat': metadata['lat'],
                'lon': metadata['lon'],
                **char
            }
            anomalies.append(anomaly)

        return anomalies

    def scan_entity_proxy(self, entity_data: dict, proxy_name: str,
                          min_shift: float = 1.0) -> List[dict]:
        """
        Scan a single entity for change points in a specific proxy.

        Args:
            entity_data: Dict with 'ages', '{proxy}_z', 'metadata'
            proxy_name: Name of proxy to scan (e.g., 'Ba_Ca', 'U_Ca', 'Mg_Ca')
            min_shift: Minimum shift magnitude to report (in sigma)

        Returns:
            List of detected anomalies with characteristics
        """
        z_col = f'{proxy_name}_z'
        if z_col not in entity_data:
            return []

        signal = entity_data[z_col]
        ages = entity_data['ages']
        metadata = entity_data['metadata']

        # Skip if too many NaN values
        valid_mask = ~np.isnan(signal)
        if valid_mask.sum() < 2 * self.min_size:
            return []

        # Detect change points
        change_points = self.detect_change_points(signal)

        # Characterize each
        anomalies = []
        for cp_idx in change_points:
            char = self.characterize_change_point(signal, ages, cp_idx)

            # Only keep significant shifts
            if abs(char['shift_magnitude']) < min_shift:
                continue

            anomaly = {
                'entity_id': metadata.get('entity_id', None),
                'site_name': metadata['site_name'],
                'entity_name': metadata['entity_name'],
                'lat': metadata['lat'],
                'lon': metadata['lon'],
                'proxy': proxy_name,
                **char
            }
            anomalies.append(anomaly)

        return anomalies

    def scan_all_proxies(self, entities: Dict[int, dict],
                         proxies: List[str] = None,
                         min_year: int = None,
                         max_year: int = None,
                         min_shift: float = 1.0) -> pd.DataFrame:
        """
        Scan all entities for change points across multiple proxies.

        Args:
            entities: Dict from SISALLoader.get_entity_trace_timeseries()
            proxies: List of proxy names to scan (e.g., ['Ba_Ca', 'U_Ca'])
            min_year: Optional filter for minimum year
            max_year: Optional filter for maximum year
            min_shift: Minimum shift magnitude to report (in sigma)

        Returns:
            DataFrame of all detected anomalies across all proxies
        """
        if proxies is None:
            proxies = ['Ba_Ca', 'U_Ca', 'Mg_Ca', 'Sr_Ca']

        print(f"Scanning {len(entities)} entities for change points in {proxies}...")
        print(f"  PELT penalty: {self.penalty}, min_size: {self.min_size}")

        all_anomalies = []
        proxy_counts = {p: 0 for p in proxies}

        for entity_id, data in entities.items():
            # Add entity_id to metadata
            data['metadata']['entity_id'] = entity_id

            # Filter by year range if specified
            if min_year is not None or max_year is not None:
                ages = data['ages']
                mask = np.ones(len(ages), dtype=bool)
                if min_year is not None:
                    mask &= ages >= min_year
                if max_year is not None:
                    mask &= ages <= max_year

                if mask.sum() < 2 * self.min_size:
                    continue

                # Filter all arrays
                filtered_data = {'ages': ages[mask], 'metadata': data['metadata']}
                for proxy in proxies:
                    if proxy in data:
                        filtered_data[proxy] = data[proxy][mask]
                    z_col = f'{proxy}_z'
                    if z_col in data:
                        filtered_data[z_col] = data[z_col][mask]
            else:
                filtered_data = data

            # Scan each proxy
            for proxy in proxies:
                anomalies = self.scan_entity_proxy(filtered_data, proxy, min_shift)
                if anomalies:
                    all_anomalies.extend(anomalies)
                    proxy_counts[proxy] += len(anomalies)

        print(f"  Total anomalies: {len(all_anomalies)}")
        for proxy, count in proxy_counts.items():
            print(f"    {proxy}: {count}")

        if not all_anomalies:
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(all_anomalies)

        # Sort by absolute magnitude
        df['abs_magnitude'] = df['shift_magnitude'].abs()
        df = df.sort_values('abs_magnitude', ascending=False)

        return df

    def scan_all(self, entities: Dict[int, dict],
                 min_year: int = None, max_year: int = None) -> pd.DataFrame:
        """
        Scan all entities for change points.

        Args:
            entities: Dict from SISALLoader.get_entity_timeseries()
            min_year: Optional filter for minimum year
            max_year: Optional filter for maximum year

        Returns:
            DataFrame of all detected anomalies, sorted by magnitude
        """
        print(f"Scanning {len(entities)} entities for change points...")
        print(f"  PELT penalty: {self.penalty}, min_size: {self.min_size}")

        all_anomalies = []
        entities_with_anomalies = 0

        for entity_id, data in entities.items():
            # Add entity_id to metadata
            data['metadata']['entity_id'] = entity_id

            # Optionally filter by year range
            if min_year is not None or max_year is not None:
                ages = data['ages']
                mask = np.ones(len(ages), dtype=bool)
                if min_year is not None:
                    mask &= ages >= min_year
                if max_year is not None:
                    mask &= ages <= max_year

                if mask.sum() < 10:
                    continue

                filtered_data = {
                    'ages': ages[mask],
                    'd18O_z': data['d18O_z'][mask],
                    'd18O': data['d18O'][mask],
                    'metadata': data['metadata']
                }
            else:
                filtered_data = data

            # Scan this entity
            anomalies = self.scan_entity(filtered_data)
            if anomalies:
                all_anomalies.extend(anomalies)
                entities_with_anomalies += 1

        print(f"  Found {len(all_anomalies)} change points in {entities_with_anomalies} entities")

        if not all_anomalies:
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(all_anomalies)

        # Sort by absolute magnitude
        df['abs_magnitude'] = df['shift_magnitude'].abs()
        df = df.sort_values('abs_magnitude', ascending=False)

        return df


def run_sensitivity_analysis(entities: Dict, penalties: List[float] = [5, 10, 20, 50]):
    """Run scan with different penalty values to assess sensitivity."""
    print("\n=== PELT Sensitivity Analysis ===")

    results = {}
    for pen in penalties:
        scanner = GlobalScanner(penalty=pen)
        df = scanner.scan_all(entities, min_year=0, max_year=2000)
        results[pen] = {
            'n_anomalies': len(df),
            'top_5_years': df['year_ce'].head(5).tolist() if len(df) > 0 else []
        }
        print(f"  penalty={pen}: {len(df)} change points")

    return results


def main():
    """Run global scan on SISAL database."""

    # Load SISAL data
    loader = SISALLoader()
    df = loader.load_all()
    entities = loader.get_entity_timeseries(df, min_samples=20)

    print(f"\n=== Running Global Change Point Detection ===")
    print(f"Entities: {len(entities)}")

    # Run with default penalty
    scanner = GlobalScanner(penalty=10.0, min_size=3)
    anomalies = scanner.scan_all(entities, min_year=0, max_year=2000)

    if len(anomalies) == 0:
        print("No significant change points detected!")
        return

    # Save results
    output_path = Path(__file__).parent / "outputs" / "anomalies.csv"
    output_path.parent.mkdir(exist_ok=True)
    anomalies.to_csv(output_path, index=False)
    print(f"\nSaved {len(anomalies)} anomalies to {output_path}")

    # Display top 20 anomalies
    print("\n=== Top 20 Anomalies by Magnitude ===")
    display_cols = ['site_name', 'entity_name', 'year_ce', 'shift_magnitude',
                   'recovery_years', 'lat', 'lon']
    available_cols = [c for c in display_cols if c in anomalies.columns]
    print(anomalies[available_cols].head(20).to_string(index=False))

    # Summary by region
    print("\n=== Anomalies by Latitude Band ===")
    anomalies['lat_band'] = pd.cut(anomalies['lat'],
                                   bins=[-90, -30, 0, 30, 60, 90],
                                   labels=['S Polar', 'S Temperate', 'Tropics', 'N Temperate', 'N Polar'])
    print(anomalies.groupby('lat_band').size())

    # Time distribution
    print("\n=== Anomalies by Century ===")
    anomalies['century'] = (anomalies['year_ce'] // 100) * 100
    century_counts = anomalies.groupby('century').size().sort_values(ascending=False)
    print(century_counts.head(10))

    return anomalies


if __name__ == '__main__':
    results = main()
