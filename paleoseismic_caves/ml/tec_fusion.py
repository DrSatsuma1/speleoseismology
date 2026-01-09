"""
Seismo-Ionospheric Fusion Engine

Correlates GPS-TEC (Total Electron Content) anomalies with earthquake timing.
Uses:
- USGS Earthquake API (direct REST calls, no libcomcat needed)
- MadrigalWeb for GPS-TEC data from MIT Haystack

Test case: Ridgecrest M7.1 (2019-07-06, 20:19 UTC)
Expected: Positive TEC anomaly ~6 days before mainshock (June 29-30, 2019)

Reference: Xie et al. (2021) - Ionospheric precursors to the 2019 Ridgecrest earthquakes
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple, List
import warnings

try:
    from madrigalWeb.madrigalWeb import MadrigalData
    HAS_MADRIGAL = True
except ImportError:
    HAS_MADRIGAL = False
    MadrigalData = None
    warnings.warn("madrigalWeb not installed - TEC data fetching disabled")

OUTPUT_DIR = Path(__file__).parent / "outputs"


# =============================================================================
# USGS Earthquake API (replaces libcomcat)
# =============================================================================

USGS_API_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"


def fetch_earthquake(event_id: Optional[str] = None,
                     min_magnitude: float = 6.0,
                     start_time: Optional[str] = None,
                     end_time: Optional[str] = None,
                     latitude: Optional[float] = None,
                     longitude: Optional[float] = None,
                     max_radius_km: float = 100) -> pd.DataFrame:
    """
    Fetch earthquake(s) from USGS API.

    Args:
        event_id: Specific USGS event ID (e.g., 'ci38457511' for Ridgecrest)
        min_magnitude: Minimum magnitude filter
        start_time: ISO format start time
        end_time: ISO format end time
        latitude, longitude: Center point for radial search
        max_radius_km: Radius in km for geographic search

    Returns:
        DataFrame with earthquake details
    """
    params = {
        'format': 'geojson',
        'minmagnitude': min_magnitude,
    }

    if event_id:
        params['eventid'] = event_id
    if start_time:
        params['starttime'] = start_time
    if end_time:
        params['endtime'] = end_time
    if latitude and longitude:
        params['latitude'] = latitude
        params['longitude'] = longitude
        params['maxradiuskm'] = max_radius_km

    response = requests.get(USGS_API_URL, params=params)
    response.raise_for_status()
    data = response.json()

    events = []
    for feature in data.get('features', []):
        props = feature['properties']
        coords = feature['geometry']['coordinates']
        events.append({
            'event_id': feature['id'],
            'time': datetime.utcfromtimestamp(props['time'] / 1000),
            'magnitude': props['mag'],
            'mag_type': props['magType'],
            'longitude': coords[0],
            'latitude': coords[1],
            'depth_km': coords[2],
            'place': props['place'],
            'type': props['type'],
            'status': props['status']
        })

    return pd.DataFrame(events)


def get_ridgecrest_events() -> pd.DataFrame:
    """Get the 2019 Ridgecrest earthquake sequence (M6.4 foreshock + M7.1 mainshock)."""
    # Ridgecrest M7.1 mainshock
    mainshock = fetch_earthquake(event_id='ci38457511')

    # Ridgecrest M6.4 foreshock (2019-07-04)
    foreshock = fetch_earthquake(event_id='ci38443183')

    return pd.concat([mainshock, foreshock], ignore_index=True)


# =============================================================================
# TEC Data Sources
# =============================================================================

# MIT Haystack Madrigal server (primary)
MADRIGAL_URL = "http://cedar.openmadrigal.org"
TEC_EXPERIMENT_CODE = 8000  # Global GPS TEC

# NASA CDDIS (alternative - faster for bulk downloads)
# https://cddis.nasa.gov/archive/gnss/products/ionex/
CDDIS_URL = "https://cddis.nasa.gov/archive/gnss/products/ionex"


def fetch_tec_data(latitude: float, longitude: float,
                   start_date: datetime, end_date: datetime,
                   user_email: str = "research@example.edu",
                   user_name: str = "Researcher",
                   user_affiliation: str = "University") -> Optional[pd.DataFrame]:
    """
    Fetch GPS-TEC data from Madrigal database for a specific location.

    Args:
        latitude, longitude: Location of interest
        start_date, end_date: Time range
        user_email, user_name, user_affiliation: Required for Madrigal access

    Returns:
        DataFrame with TEC time series, or None if fetch fails
    """
    if not HAS_MADRIGAL:
        raise RuntimeError(
            "FATAL: madrigalWeb not installed. Install with: pip install madrigalWeb\n"
            "No simulated data allowed - real data only."
        )

    try:
        # Initialize Madrigal connection
        mad = MadrigalData(MADRIGAL_URL)

        # Get experiments in date range
        # TEC_EXPERIMENT_CODE = 8000 for GPS TEC
        experiments = mad.getExperiments(
            TEC_EXPERIMENT_CODE,
            start_date.year, start_date.month, start_date.day,
            0, 0, 0,  # start time
            end_date.year, end_date.month, end_date.day,
            23, 59, 59,  # end time
            local=0  # Search all sites
        )

        if not experiments:
            raise RuntimeError(
                f"FATAL: No TEC experiments found for {start_date} to {end_date}\n"
                "Check Madrigal server availability or try different date range."
            )

        print(f"Found {len(experiments)} TEC experiments")

        all_data = []
        for exp in experiments[:5]:  # Limit to first 5 for speed
            # Get files for this experiment
            files = mad.getExperimentFiles(exp.id)

            for f in files:
                if 'tec' in f.name.lower() or f.category == 1:  # Default file
                    try:
                        # Use isprint to get ASCII data
                        result = mad.isprint(
                            f.name,
                            'gdlat,glon,tec,dtec',  # Parameters to retrieve
                            f'gdlat>={latitude-5} gdlat<={latitude+5} glon>={longitude-5} glon<={longitude+5}',
                            user_name, user_email, user_affiliation
                        )
                        if result:
                            # Parse isprint output
                            lines = result.strip().split('\n')
                            for line in lines[1:]:  # Skip header
                                parts = line.split()
                                if len(parts) >= 4:
                                    all_data.append({
                                        'latitude': float(parts[0]),
                                        'longitude': float(parts[1]),
                                        'tec': float(parts[2]),
                                        'dtec': float(parts[3])
                                    })
                    except Exception as file_error:
                        continue

        if all_data:
            df = pd.DataFrame(all_data)
            return df

        raise RuntimeError(
            "FATAL: No TEC data retrieved from Madrigal.\n"
            "Check location coordinates and date range."
        )

    except RuntimeError:
        raise  # Re-raise our own errors
    except Exception as e:
        raise RuntimeError(f"FATAL: Error fetching Madrigal data: {e}")


# NOTE: Simulated data function removed - real data only policy


# =============================================================================
# TEC Anomaly Detection
# =============================================================================

def compute_tec_anomaly(tec_df: pd.DataFrame,
                         background_days: int = 15) -> pd.DataFrame:
    """
    Compute TEC anomaly as deviation from rolling background.

    Args:
        tec_df: DataFrame with 'timestamp' and 'tec' columns
        background_days: Days for rolling average background

    Returns:
        DataFrame with added 'background', 'anomaly', 'anomaly_sigma' columns
    """
    df = tec_df.copy()
    df = df.sort_values('timestamp')

    # Rolling background (centered, using hours)
    window_hours = background_days * 24
    df['background'] = df['tec'].rolling(window=window_hours, center=True, min_periods=24).mean()
    df['background_std'] = df['tec'].rolling(window=window_hours, center=True, min_periods=24).std()

    # Anomaly = deviation from background
    df['anomaly'] = df['tec'] - df['background']

    # Normalized anomaly (sigma units)
    df['anomaly_sigma'] = df['anomaly'] / df['background_std']

    return df


def detect_significant_anomalies(tec_df: pd.DataFrame,
                                  threshold_sigma: float = 2.0) -> pd.DataFrame:
    """
    Find timestamps with significant TEC anomalies.

    Args:
        tec_df: DataFrame with 'anomaly_sigma' column
        threshold_sigma: Significance threshold in standard deviations

    Returns:
        DataFrame of significant anomaly events
    """
    sig = tec_df[abs(tec_df['anomaly_sigma']) >= threshold_sigma].copy()
    sig['sign'] = np.sign(sig['anomaly_sigma'])
    sig['direction'] = sig['sign'].map({1: 'POSITIVE', -1: 'NEGATIVE'})

    return sig[['timestamp', 'tec', 'background', 'anomaly', 'anomaly_sigma', 'direction']]


# =============================================================================
# Fusion Analysis
# =============================================================================

def analyze_earthquake_precursors(eq_lat: float, eq_lon: float,
                                   eq_time: datetime,
                                   days_before: int = 30,
                                   days_after: int = 5) -> dict:
    """
    Full fusion analysis: fetch TEC data and correlate with earthquake timing.

    Args:
        eq_lat, eq_lon: Earthquake epicenter
        eq_time: Earthquake origin time
        days_before, days_after: Analysis window

    Returns:
        Dict with analysis results
    """
    start = eq_time - timedelta(days=days_before)
    end = eq_time + timedelta(days=days_after)

    print(f"Analyzing TEC for earthquake at ({eq_lat:.2f}, {eq_lon:.2f})")
    print(f"  Time: {eq_time}")
    print(f"  Window: {start.date()} to {end.date()}")

    # Fetch TEC data
    tec_df = fetch_tec_data(eq_lat, eq_lon, start, end)

    if tec_df is None or len(tec_df) == 0:
        return {'error': 'No TEC data available'}

    # Compute anomalies
    tec_df = compute_tec_anomaly(tec_df, background_days=15)

    # Find significant anomalies
    anomalies = detect_significant_anomalies(tec_df, threshold_sigma=2.0)

    # Calculate days before earthquake for each anomaly
    anomalies['days_before_eq'] = (eq_time - anomalies['timestamp']).dt.total_seconds() / 86400

    # Filter to pre-earthquake anomalies
    precursors = anomalies[anomalies['days_before_eq'] > 0].copy()

    # Summary statistics
    result = {
        'earthquake': {
            'latitude': eq_lat,
            'longitude': eq_lon,
            'time': eq_time
        },
        'tec_data': {
            'n_observations': len(tec_df),
            'start': tec_df['timestamp'].min(),
            'end': tec_df['timestamp'].max(),
            'mean_tec': tec_df['tec'].mean(),
            'std_tec': tec_df['tec'].std()
        },
        'anomalies': {
            'total': len(anomalies),
            'precursors': len(precursors),
            'positive_precursors': len(precursors[precursors['direction'] == 'POSITIVE']),
            'negative_precursors': len(precursors[precursors['direction'] == 'NEGATIVE'])
        },
        'precursor_details': precursors.to_dict('records') if len(precursors) > 0 else [],
        'tec_timeseries': tec_df
    }

    return result


def ridgecrest_test():
    """
    Run the Ridgecrest M7.1 test case.
    Expected: Positive TEC anomaly approximately 6 days before mainshock.
    """
    print("=" * 60)
    print("RIDGECREST M7.1 SEISMO-IONOSPHERIC FUSION TEST")
    print("=" * 60)

    # Ridgecrest M7.1 parameters
    eq_lat = 35.77
    eq_lon = -117.60
    eq_time = datetime(2019, 7, 6, 20, 19, 0)  # 20:19 UTC

    print(f"\nMainshock: M7.1 Ridgecrest")
    print(f"  Location: {eq_lat}°N, {eq_lon}°W")
    print(f"  Time: {eq_time} UTC")

    # Run analysis
    result = analyze_earthquake_precursors(eq_lat, eq_lon, eq_time,
                                            days_before=30, days_after=3)

    if 'error' in result:
        print(f"\nError: {result['error']}")
        return result

    # Report results
    print(f"\n--- TEC DATA SUMMARY ---")
    print(f"  Observations: {result['tec_data']['n_observations']}")
    print(f"  Mean TEC: {result['tec_data']['mean_tec']:.1f} TECU")
    print(f"  Std TEC: {result['tec_data']['std_tec']:.1f} TECU")
    print("  ✓ REAL DATA from Madrigal")

    print(f"\n--- ANOMALY DETECTION ---")
    print(f"  Total anomalies (|z| > 2): {result['anomalies']['total']}")
    print(f"  Pre-earthquake precursors: {result['anomalies']['precursors']}")
    print(f"    Positive: {result['anomalies']['positive_precursors']}")
    print(f"    Negative: {result['anomalies']['negative_precursors']}")

    if result['precursor_details']:
        print(f"\n--- TOP PRECURSOR SIGNALS ---")
        precursors = pd.DataFrame(result['precursor_details'])
        precursors = precursors.sort_values('anomaly_sigma', ascending=False)

        for _, row in precursors.head(10).iterrows():
            print(f"  {row['timestamp']}: {row['direction']} z={row['anomaly_sigma']:.2f} "
                  f"({row['days_before_eq']:.1f} days before)")

    # Save results
    OUTPUT_DIR.mkdir(exist_ok=True)
    result['tec_timeseries'].to_csv(OUTPUT_DIR / 'ridgecrest_tec.csv', index=False)
    print(f"\nSaved TEC timeseries to {OUTPUT_DIR / 'ridgecrest_tec.csv'}")

    return result


if __name__ == '__main__':
    result = ridgecrest_test()
