"""
Multi-Proxy Correlation Analysis

Finds where Ba/Ca, U/Ca, Mg/Ca, Sr/Ca, and δ18O anomalies co-occur.
Cross-correlates with earthquake and volcanic catalogs to discover patterns.

This is a pure ML/data-driven approach - we don't pre-define what anomalies mean,
we discover patterns through correlation with known events.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class ProxyCorrelator:
    """Find co-occurring anomalies and correlate with known events."""

    def __init__(self, window_years: int = 10):
        """
        Initialize correlator.

        Args:
            window_years: Time window for considering anomalies coincident
        """
        self.window_years = window_years

    def find_coincident_anomalies(self, anomalies_df: pd.DataFrame) -> pd.DataFrame:
        """
        Group anomalies that occur within the time window at the same cave.

        Args:
            anomalies_df: DataFrame with columns: entity_id, year_ce, proxy, shift_magnitude

        Returns:
            DataFrame of anomaly clusters with columns:
            - entity_id, site_name, year_ce (center)
            - proxies (list of proxies that spiked)
            - n_proxies (count)
            - total_magnitude (sum of |shift|)
        """
        if len(anomalies_df) == 0:
            return pd.DataFrame()

        print(f"Finding coincident anomalies (window: ±{self.window_years} years)...")

        clusters = []
        processed = set()

        # Group by entity first
        for entity_id, entity_group in anomalies_df.groupby('entity_id'):
            entity_group = entity_group.sort_values('year_ce')

            for idx, row in entity_group.iterrows():
                if idx in processed:
                    continue

                # Find all anomalies within window
                year = row['year_ce']
                window_mask = (
                    (entity_group['year_ce'] >= year - self.window_years) &
                    (entity_group['year_ce'] <= year + self.window_years)
                )
                cluster = entity_group[window_mask]

                # Mark as processed
                processed.update(cluster.index.tolist())

                # Build cluster record
                proxies = cluster['proxy'].unique().tolist()
                cluster_record = {
                    'entity_id': entity_id,
                    'site_name': row['site_name'],
                    'entity_name': row['entity_name'],
                    'lat': row['lat'],
                    'lon': row['lon'],
                    'year_ce': cluster['year_ce'].mean(),
                    'year_min': cluster['year_ce'].min(),
                    'year_max': cluster['year_ce'].max(),
                    'proxies': ','.join(sorted(proxies)),
                    'n_proxies': len(proxies),
                    'n_anomalies': len(cluster),
                    'total_magnitude': cluster['shift_magnitude'].abs().sum(),
                    'max_magnitude': cluster['shift_magnitude'].abs().max(),
                }

                # Add per-proxy magnitudes
                for proxy in ['Ba_Ca', 'U_Ca', 'Mg_Ca', 'Sr_Ca', 'd18O']:
                    proxy_data = cluster[cluster['proxy'] == proxy]
                    if len(proxy_data) > 0:
                        cluster_record[f'{proxy}_shift'] = proxy_data['shift_magnitude'].iloc[0]
                    else:
                        cluster_record[f'{proxy}_shift'] = np.nan

                clusters.append(cluster_record)

        result = pd.DataFrame(clusters)
        if len(result) > 0:
            result = result.sort_values('n_proxies', ascending=False)

        print(f"  Found {len(result)} anomaly clusters")
        print(f"  Multi-proxy clusters (n>=2): {(result['n_proxies'] >= 2).sum()}")

        return result

    def load_earthquake_catalog(self, catalog_path: str = None) -> pd.DataFrame:
        """
        Load earthquake catalog for correlation.

        Expected columns: year, lat, lon, magnitude, region
        """
        if catalog_path is None:
            # Try to find CFTI5Med or similar
            default_paths = [
                Path(__file__).parent.parent / "data" / "earthquakes.csv",
                Path(__file__).parent.parent / "data" / "cfti5med.csv",
            ]
            for path in default_paths:
                if path.exists():
                    catalog_path = path
                    break

        if catalog_path is None or not Path(catalog_path).exists():
            print("  Warning: No earthquake catalog found")
            return pd.DataFrame()

        return pd.read_csv(catalog_path)

    def load_volcanic_catalog(self, catalog_path: str = None) -> pd.DataFrame:
        """
        Load volcanic eruption catalog for correlation.

        Expected columns: year, sulfate_tg, eruption_name
        """
        if catalog_path is None:
            default_paths = [
                Path(__file__).parent.parent / "data" / "evolv2k.csv",
                Path(__file__).parent.parent / "data" / "volcanic_events.csv",
            ]
            for path in default_paths:
                if path.exists():
                    catalog_path = path
                    break

        if catalog_path is None or not Path(catalog_path).exists():
            print("  Warning: No volcanic catalog found")
            return pd.DataFrame()

        return pd.read_csv(catalog_path)

    def correlate_with_earthquakes(self, clusters: pd.DataFrame,
                                    earthquakes: pd.DataFrame,
                                    distance_km: float = 500,
                                    time_window: int = 5) -> pd.DataFrame:
        """
        Match anomaly clusters with nearby earthquakes.

        Args:
            clusters: DataFrame from find_coincident_anomalies
            earthquakes: Earthquake catalog with year, lat, lon, magnitude
            distance_km: Maximum distance to consider a match
            time_window: Years before/after anomaly to search

        Returns:
            DataFrame with earthquake matches added
        """
        if len(earthquakes) == 0 or len(clusters) == 0:
            return clusters

        print(f"Correlating with earthquakes (dist<{distance_km}km, window±{time_window}yr)...")

        matches = []
        for idx, cluster in clusters.iterrows():
            # Time filter
            eq_in_window = earthquakes[
                (earthquakes['year'] >= cluster['year_ce'] - time_window) &
                (earthquakes['year'] <= cluster['year_ce'] + time_window)
            ]

            if len(eq_in_window) == 0:
                matches.append({'eq_match': False})
                continue

            # Distance filter (simple haversine approximation)
            lat1, lon1 = cluster['lat'], cluster['lon']
            distances = np.sqrt(
                (eq_in_window['lat'] - lat1)**2 +
                (eq_in_window['lon'] - lon1)**2
            ) * 111  # Approximate km

            nearby = eq_in_window[distances < distance_km]

            if len(nearby) == 0:
                matches.append({'eq_match': False})
                continue

            # Get closest earthquake
            closest_idx = distances[distances < distance_km].idxmin()
            eq = earthquakes.loc[closest_idx]

            matches.append({
                'eq_match': True,
                'eq_year': eq.get('year', np.nan),
                'eq_magnitude': eq.get('magnitude', np.nan),
                'eq_distance_km': distances[closest_idx],
                'eq_region': eq.get('region', ''),
            })

        match_df = pd.DataFrame(matches)
        result = pd.concat([clusters.reset_index(drop=True), match_df], axis=1)

        n_matched = result['eq_match'].sum()
        print(f"  Matched {n_matched}/{len(clusters)} clusters to earthquakes ({100*n_matched/len(clusters):.1f}%)")

        return result

    def correlate_with_volcanoes(self, clusters: pd.DataFrame,
                                  volcanoes: pd.DataFrame,
                                  time_window: int = 5) -> pd.DataFrame:
        """
        Match anomaly clusters with volcanic eruptions.

        Args:
            clusters: DataFrame from find_coincident_anomalies
            volcanoes: Volcanic catalog with year, sulfate_tg
            time_window: Years before/after anomaly to search (volcanic effects delayed 1-3 years)

        Returns:
            DataFrame with volcanic matches added
        """
        if len(volcanoes) == 0 or len(clusters) == 0:
            return clusters

        print(f"Correlating with volcanic events (window±{time_window}yr)...")

        matches = []
        for idx, cluster in clusters.iterrows():
            # Time filter - look for eruptions 1-5 years BEFORE the anomaly
            volc_in_window = volcanoes[
                (volcanoes['year'] >= cluster['year_ce'] - time_window - 2) &
                (volcanoes['year'] <= cluster['year_ce'] + 2)
            ]

            if len(volc_in_window) == 0:
                matches.append({'volc_match': False})
                continue

            # Get largest eruption in window
            if 'sulfate_tg' in volc_in_window.columns:
                largest_idx = volc_in_window['sulfate_tg'].idxmax()
            else:
                largest_idx = volc_in_window.index[0]

            volc = volcanoes.loc[largest_idx]

            matches.append({
                'volc_match': True,
                'volc_year': volc.get('year', np.nan),
                'volc_sulfate': volc.get('sulfate_tg', np.nan),
                'volc_name': volc.get('eruption_name', ''),
            })

        match_df = pd.DataFrame(matches)
        result = pd.concat([clusters.reset_index(drop=True), match_df], axis=1)

        n_matched = result['volc_match'].sum()
        print(f"  Matched {n_matched}/{len(clusters)} clusters to volcanoes ({100*n_matched/len(clusters):.1f}%)")

        return result

    def generate_signature_matrix(self, clusters: pd.DataFrame) -> pd.DataFrame:
        """
        Create a matrix showing which proxies spike for each event type.

        Analyzes patterns like:
        - Earthquakes: High Ba_Ca + High Mg_Ca + negative δ18O?
        - Volcanoes: negative δ18O + low Mg_Ca?

        Returns:
            DataFrame summarizing proxy patterns by event type
        """
        if len(clusters) == 0:
            return pd.DataFrame()

        print("Generating proxy signature matrix...")

        signatures = []

        # Define event categories
        categories = []
        if 'eq_match' in clusters.columns:
            clusters['category'] = 'unknown'
            clusters.loc[clusters['eq_match'] == True, 'category'] = 'earthquake'
        if 'volc_match' in clusters.columns:
            clusters.loc[clusters['volc_match'] == True, 'category'] = 'volcanic'
            # If both match, prefer earthquake (more localized signal)
            if 'eq_match' in clusters.columns:
                both_mask = (clusters['eq_match'] == True) & (clusters['volc_match'] == True)
                clusters.loc[both_mask, 'category'] = 'compound'

        # Analyze patterns by category
        proxies = ['Ba_Ca', 'U_Ca', 'Mg_Ca', 'Sr_Ca']
        shift_cols = [f'{p}_shift' for p in proxies]
        available_cols = [c for c in shift_cols if c in clusters.columns]

        if 'category' in clusters.columns:
            for category in clusters['category'].unique():
                cat_data = clusters[clusters['category'] == category]
                sig = {'category': category, 'n_events': len(cat_data)}

                for col in available_cols:
                    proxy = col.replace('_shift', '')
                    values = cat_data[col].dropna()
                    if len(values) > 0:
                        sig[f'{proxy}_mean'] = values.mean()
                        sig[f'{proxy}_pos_pct'] = (values > 0).sum() / len(values) * 100
                        sig[f'{proxy}_neg_pct'] = (values < 0).sum() / len(values) * 100

                signatures.append(sig)

        result = pd.DataFrame(signatures)
        if len(result) > 0:
            print(result.to_string(index=False))

        return result

    def analyze_all(self, anomalies_df: pd.DataFrame,
                    earthquake_catalog: str = None,
                    volcanic_catalog: str = None) -> Dict:
        """
        Run full correlation analysis pipeline.

        Args:
            anomalies_df: DataFrame of detected anomalies
            earthquake_catalog: Path to earthquake CSV (optional)
            volcanic_catalog: Path to volcanic CSV (optional)

        Returns:
            Dict with: clusters, signatures, statistics
        """
        print("\n=== Multi-Proxy Correlation Analysis ===")

        # Find coincident anomalies
        clusters = self.find_coincident_anomalies(anomalies_df)

        if len(clusters) == 0:
            return {'clusters': pd.DataFrame(), 'signatures': pd.DataFrame(), 'stats': {}}

        # Load catalogs
        earthquakes = self.load_earthquake_catalog(earthquake_catalog)
        volcanoes = self.load_volcanic_catalog(volcanic_catalog)

        # Correlate with events
        if len(earthquakes) > 0:
            clusters = self.correlate_with_earthquakes(clusters, earthquakes)
        if len(volcanoes) > 0:
            clusters = self.correlate_with_volcanoes(clusters, volcanoes)

        # Generate signature matrix
        signatures = self.generate_signature_matrix(clusters)

        # Summary statistics
        stats = {
            'total_clusters': len(clusters),
            'multi_proxy_clusters': int((clusters['n_proxies'] >= 2).sum()),
            'earthquake_matches': int(clusters.get('eq_match', pd.Series([False])).sum()),
            'volcanic_matches': int(clusters.get('volc_match', pd.Series([False])).sum()),
        }

        print(f"\n=== Summary ===")
        print(f"  Total anomaly clusters: {stats['total_clusters']}")
        print(f"  Multi-proxy clusters: {stats['multi_proxy_clusters']}")
        print(f"  Earthquake matches: {stats['earthquake_matches']}")
        print(f"  Volcanic matches: {stats['volcanic_matches']}")

        return {
            'clusters': clusters,
            'signatures': signatures,
            'stats': stats
        }


def main():
    """Test the correlator with sample data."""
    # Create sample anomalies
    sample_anomalies = pd.DataFrame([
        {'entity_id': 1, 'site_name': 'Test Cave', 'entity_name': 'TC1',
         'lat': 44.0, 'lon': 8.0, 'year_ce': 1285, 'proxy': 'Ba_Ca', 'shift_magnitude': 2.5},
        {'entity_id': 1, 'site_name': 'Test Cave', 'entity_name': 'TC1',
         'lat': 44.0, 'lon': 8.0, 'year_ce': 1287, 'proxy': 'Mg_Ca', 'shift_magnitude': 2.2},
        {'entity_id': 1, 'site_name': 'Test Cave', 'entity_name': 'TC1',
         'lat': 44.0, 'lon': 8.0, 'year_ce': 1285, 'proxy': 'U_Ca', 'shift_magnitude': 1.8},
        {'entity_id': 2, 'site_name': 'Other Cave', 'entity_name': 'OC1',
         'lat': 45.0, 'lon': 9.0, 'year_ce': 1650, 'proxy': 'Ba_Ca', 'shift_magnitude': -1.5},
    ])

    correlator = ProxyCorrelator(window_years=10)
    results = correlator.analyze_all(sample_anomalies)

    print("\n=== Clusters ===")
    print(results['clusters'].to_string())


if __name__ == '__main__':
    main()
