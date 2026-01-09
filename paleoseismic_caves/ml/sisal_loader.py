"""
SISAL v3 Data Loader for ML Anomaly Detection

Loads δ18O time series from SISAL database, joins with chronology and metadata,
and outputs standardized z-score time series per entity (cave speleothem).

Join path: site → entity → sample → d18O + chronology
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional
import warnings

# Suppress pandas warnings about mixed dtypes
warnings.filterwarnings('ignore', category=pd.errors.DtypeWarning)


class SISALLoader:
    """Load and process SISAL v3 database for anomaly detection."""

    def __init__(self, sisal_path: str = None):
        """Initialize with path to SISAL CSV directory."""
        if sisal_path is None:
            # Default path relative to this script
            self.sisal_path = Path(__file__).parent.parent / "data" / "SISAL3" / \
                             "sisalv3_database_mysql_csv" / "sisalv3_csv"
        else:
            self.sisal_path = Path(sisal_path)

        self._validate_path()

    def _validate_path(self):
        """Check that required files exist."""
        required = ['d18O.csv', 'sample.csv', 'sisal_chronology.csv',
                   'entity.csv', 'site.csv']
        for f in required:
            if not (self.sisal_path / f).exists():
                raise FileNotFoundError(f"Required file not found: {self.sisal_path / f}")

    def load_all(self) -> pd.DataFrame:
        """
        Load and join all SISAL tables into a single dataframe.

        Returns DataFrame with columns:
        - entity_id, site_id, entity_name, site_name
        - lat, lon, elevation
        - sample_id, d18O, d18O_precision
        - age_bp (best available chronology)
        - age_ce (converted to Common Era)
        """
        print("Loading SISAL v3 database...")

        # Load tables (handle NA values)
        d18o = pd.read_csv(self.sisal_path / 'd18O.csv', na_values=['NA', 'NaN', ''])
        d18o['d18O_measurement'] = pd.to_numeric(d18o['d18O_measurement'], errors='coerce')
        sample = pd.read_csv(self.sisal_path / 'sample.csv',
                            usecols=['entity_id', 'sample_id', 'mineralogy'])
        chronology = pd.read_csv(self.sisal_path / 'sisal_chronology.csv')
        entity = pd.read_csv(self.sisal_path / 'entity.csv',
                            usecols=['site_id', 'entity_id', 'entity_name',
                                    'speleothem_type', 'Mg_Ca', 'd13C'])  # exclude d18O flag
        site = pd.read_csv(self.sisal_path / 'site.csv',
                          usecols=['site_id', 'site_name', 'latitude',
                                  'longitude', 'elevation'])

        print(f"  d18O: {len(d18o):,} measurements")
        print(f"  samples: {len(sample):,}")
        print(f"  entities: {len(entity):,}")
        print(f"  sites: {len(site):,}")

        # Select best age model (priority: copRa > StalAge > lin_interp > lin_reg)
        chronology['age_bp'] = chronology['copRa_age'].fillna(
            chronology['StalAge_age'].fillna(
                chronology['lin_interp_age'].fillna(
                    chronology['lin_reg_age']
                )
            )
        )
        chronology = chronology[['sample_id', 'age_bp']].dropna()

        # Join: d18O → sample → chronology → entity → site
        df = d18o.merge(sample, on='sample_id', how='inner')
        df = df.merge(chronology, on='sample_id', how='inner')
        df = df.merge(entity, on='entity_id', how='inner')
        df = df.merge(site, on='site_id', how='inner')

        # Convert BP (before 1950) to CE
        df['age_ce'] = 1950 - df['age_bp']

        # Rename columns for clarity
        df = df.rename(columns={
            'latitude': 'lat',
            'longitude': 'lon'
        })
        # Ensure d18O column name is consistent
        if 'd18O_measurement' in df.columns:
            df = df.rename(columns={'d18O_measurement': 'd18O'})

        print(f"  After joins: {len(df):,} records with age + d18O")
        print(f"  Entities with data: {df['entity_id'].nunique()}")

        return df

    def get_entity_timeseries(self, df: pd.DataFrame = None,
                              min_samples: int = 20) -> Dict[int, dict]:
        """
        Extract time series per entity with z-score standardization.

        Args:
            df: Joined dataframe (will call load_all if None)
            min_samples: Minimum samples required for an entity

        Returns:
            Dict of {entity_id: {
                'ages': np.array (years CE),
                'd18O': np.array (raw values),
                'd18O_z': np.array (z-scores),
                'metadata': dict with site_name, lat, lon, etc.
            }}
        """
        if df is None:
            df = self.load_all()

        print(f"\nExtracting entity time series (min_samples={min_samples})...")

        entities = {}
        entity_groups = df.groupby('entity_id')

        for entity_id, group in entity_groups:
            if len(group) < min_samples:
                continue

            # Sort by age
            group = group.sort_values('age_ce')

            # Extract data (ensure numeric)
            ages = group['age_ce'].values.astype(float)
            d18o = pd.to_numeric(group['d18O'], errors='coerce').values

            # Calculate z-scores
            mean_d18o = np.nanmean(d18o)
            std_d18o = np.nanstd(d18o)
            if std_d18o > 0:
                d18o_z = (d18o - mean_d18o) / std_d18o
            else:
                d18o_z = np.zeros_like(d18o)

            # Metadata
            first_row = group.iloc[0]
            metadata = {
                'site_id': int(first_row['site_id']),
                'site_name': first_row['site_name'],
                'entity_name': first_row['entity_name'],
                'lat': first_row['lat'],
                'lon': first_row['lon'],
                'n_samples': len(group),
                'age_min': ages.min(),
                'age_max': ages.max(),
                'd18O_mean': mean_d18o,
                'd18O_std': std_d18o
            }

            entities[entity_id] = {
                'ages': ages,
                'd18O': d18o,
                'd18O_z': d18o_z,
                'metadata': metadata
            }

        print(f"  Extracted {len(entities)} entities with >= {min_samples} samples")

        return entities

    def filter_historical_era(self, entities: Dict,
                              min_year: int = 0, max_year: int = 2000) -> Dict:
        """
        Filter entities to only include those with data in historical era.

        Args:
            entities: Dict from get_entity_timeseries
            min_year: Start of time window (CE)
            max_year: End of time window (CE)

        Returns:
            Filtered dict with only relevant samples
        """
        print(f"\nFiltering to {min_year}-{max_year} CE...")

        filtered = {}
        for entity_id, data in entities.items():
            mask = (data['ages'] >= min_year) & (data['ages'] <= max_year)
            if mask.sum() >= 10:  # Need at least 10 samples in window
                filtered[entity_id] = {
                    'ages': data['ages'][mask],
                    'd18O': data['d18O'][mask],
                    'd18O_z': data['d18O_z'][mask],
                    'metadata': data['metadata']
                }

        print(f"  {len(filtered)} entities have >= 10 samples in range")

        return filtered

    def get_summary_stats(self, entities: Dict) -> pd.DataFrame:
        """Create summary dataframe of all entities."""
        rows = []
        for entity_id, data in entities.items():
            row = {'entity_id': entity_id}
            row.update(data['metadata'])
            row['age_range'] = data['ages'].max() - data['ages'].min()
            rows.append(row)

        return pd.DataFrame(rows).sort_values('n_samples', ascending=False)

    def load_trace_elements(self, proxies: list = None) -> pd.DataFrame:
        """
        Load trace element data (Ba/Ca, U/Ca, Mg/Ca, Sr/Ca) with chronology.

        Args:
            proxies: List of proxies to load. Default: ['Ba_Ca', 'U_Ca', 'Mg_Ca', 'Sr_Ca']

        Returns:
            DataFrame with columns:
            - entity_id, site_id, entity_name, site_name, lat, lon
            - sample_id, age_bp, age_ce
            - Ba_Ca, U_Ca, Mg_Ca, Sr_Ca (whichever are requested)
        """
        if proxies is None:
            proxies = ['Ba_Ca', 'U_Ca', 'Mg_Ca', 'Sr_Ca']

        print(f"Loading trace elements: {proxies}")

        # Load base tables
        sample = pd.read_csv(self.sisal_path / 'sample.csv',
                            usecols=['entity_id', 'sample_id'])
        chronology = pd.read_csv(self.sisal_path / 'sisal_chronology.csv')
        entity = pd.read_csv(self.sisal_path / 'entity.csv',
                            usecols=['site_id', 'entity_id', 'entity_name'])
        site = pd.read_csv(self.sisal_path / 'site.csv',
                          usecols=['site_id', 'site_name', 'latitude', 'longitude'])

        # Select best age model
        chronology['age_bp'] = chronology['copRa_age'].fillna(
            chronology['StalAge_age'].fillna(
                chronology['lin_interp_age'].fillna(
                    chronology['lin_reg_age']
                )
            )
        )
        chronology = chronology[['sample_id', 'age_bp']].dropna()

        # Load each trace element file
        trace_dfs = {}
        for proxy in proxies:
            filepath = self.sisal_path / f'{proxy}.csv'
            if filepath.exists():
                df = pd.read_csv(filepath, na_values=['NA', 'NaN', ''])
                col_name = f'{proxy}_measurement'
                df[proxy] = pd.to_numeric(df[col_name], errors='coerce')
                df = df[['sample_id', proxy]].dropna()
                trace_dfs[proxy] = df
                print(f"  {proxy}: {len(df):,} measurements")
            else:
                print(f"  {proxy}: file not found")

        if not trace_dfs:
            raise ValueError("No trace element files found")

        # Merge all trace elements on sample_id
        # Start with first proxy
        first_proxy = list(trace_dfs.keys())[0]
        result = trace_dfs[first_proxy]

        for proxy in list(trace_dfs.keys())[1:]:
            result = result.merge(trace_dfs[proxy], on='sample_id', how='outer')

        # Join with chronology and metadata
        result = result.merge(sample, on='sample_id', how='inner')
        result = result.merge(chronology, on='sample_id', how='inner')
        result = result.merge(entity, on='entity_id', how='inner')
        result = result.merge(site, on='site_id', how='inner')

        # Convert BP to CE
        result['age_ce'] = 1950 - result['age_bp']

        # Rename columns
        result = result.rename(columns={'latitude': 'lat', 'longitude': 'lon'})

        print(f"  After joins: {len(result):,} records with chronology")
        print(f"  Entities with trace data: {result['entity_id'].nunique()}")

        return result

    def get_entity_trace_timeseries(self, df: pd.DataFrame = None,
                                     proxies: list = None,
                                     min_samples: int = 10) -> Dict[int, dict]:
        """
        Extract trace element time series per entity with z-score standardization.

        Args:
            df: Trace element dataframe (will call load_trace_elements if None)
            proxies: List of proxies to include
            min_samples: Minimum samples required for an entity

        Returns:
            Dict of {entity_id: {
                'ages': np.array (years CE),
                'Ba_Ca': np.array (raw values),
                'Ba_Ca_z': np.array (z-scores),
                'U_Ca': np.array (raw values),
                'U_Ca_z': np.array (z-scores),
                ... (for each proxy)
                'metadata': dict with site_name, lat, lon, etc.
            }}
        """
        if proxies is None:
            proxies = ['Ba_Ca', 'U_Ca', 'Mg_Ca', 'Sr_Ca']

        if df is None:
            df = self.load_trace_elements(proxies)

        print(f"\nExtracting trace element time series (min_samples={min_samples})...")

        entities = {}
        entity_groups = df.groupby('entity_id')

        for entity_id, group in entity_groups:
            # Check if entity has enough samples for ANY proxy
            has_data = False
            for proxy in proxies:
                if proxy in group.columns:
                    valid_count = group[proxy].notna().sum()
                    if valid_count >= min_samples:
                        has_data = True
                        break

            if not has_data:
                continue

            # Sort by age
            group = group.sort_values('age_ce')
            ages = group['age_ce'].values.astype(float)

            # Build entity data dict
            entity_data = {'ages': ages, 'metadata': {}}

            # Extract each proxy with z-scores
            for proxy in proxies:
                if proxy in group.columns:
                    values = pd.to_numeric(group[proxy], errors='coerce').values

                    # Calculate z-scores (ignoring NaN)
                    valid_mask = ~np.isnan(values)
                    if valid_mask.sum() > 1:
                        mean_val = np.nanmean(values)
                        std_val = np.nanstd(values)
                        if std_val > 0:
                            z_scores = (values - mean_val) / std_val
                        else:
                            z_scores = np.zeros_like(values)

                        entity_data[proxy] = values
                        entity_data[f'{proxy}_z'] = z_scores
                        entity_data['metadata'][f'{proxy}_mean'] = mean_val
                        entity_data['metadata'][f'{proxy}_std'] = std_val
                        entity_data['metadata'][f'{proxy}_n'] = int(valid_mask.sum())

            # Add metadata
            first_row = group.iloc[0]
            entity_data['metadata'].update({
                'site_id': int(first_row['site_id']),
                'site_name': first_row['site_name'],
                'entity_name': first_row['entity_name'],
                'lat': first_row['lat'],
                'lon': first_row['lon'],
                'n_samples': len(group),
                'age_min': ages.min(),
                'age_max': ages.max()
            })

            entities[entity_id] = entity_data

        print(f"  Extracted {len(entities)} entities with trace element data")

        # Summary of proxy coverage
        for proxy in proxies:
            count = sum(1 for e in entities.values() if proxy in e)
            print(f"    {proxy}: {count} entities")

        return entities


def main():
    """Test the loader."""
    loader = SISALLoader()

    # Load all data
    df = loader.load_all()

    # Extract entity time series
    entities = loader.get_entity_timeseries(df, min_samples=20)

    # Filter to historical era
    historical = loader.filter_historical_era(entities, min_year=0, max_year=2000)

    # Summary
    summary = loader.get_summary_stats(historical)
    print("\n=== Top 10 entities by sample count (0-2000 CE) ===")
    print(summary[['entity_id', 'site_name', 'entity_name', 'lat', 'lon',
                   'n_samples', 'age_min', 'age_max']].head(10).to_string(index=False))

    return entities, historical


if __name__ == '__main__':
    main()
