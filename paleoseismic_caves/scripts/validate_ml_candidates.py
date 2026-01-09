#!/usr/bin/env python3
"""
Systematic validation of ML dark earthquake candidates against historical catalogs.
Goal: Get to 50+ validated events by cross-referencing with known earthquakes.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json

# Historical earthquake catalogs to check
CATALOGS = {
    'italy_cpti15': 'https://emidius.mi.ingv.it/CPTI15-DBMI15/query_eq/',
    'usgs_global': 'https://earthquake.usgs.gov/fdsnws/event/1/query',
    'china_historical': 'Available via ISC-GEM',
    'japan_historical': 'JMA catalog',
    'mediterranean': 'SHARE catalog'
}

def load_ml_candidates(csv_path):
    """Load ML candidate dark earthquakes"""
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} ML candidates")
    return df

def get_validation_targets():
    """
    High-confidence historical earthquakes for blind validation.
    These are well-documented events that should show up in nearby caves.
    """
    return [
        # MEDITERRANEAN (excellent historical records)
        {'year': 1755, 'lat': 36.0, 'lon': -9.0, 'mag': 8.5, 'name': 'Lisbon', 'region': 'Portugal'},
        {'year': 1908, 'lat': 38.25, 'lon': 15.58, 'mag': 7.1, 'name': 'Messina', 'region': 'Italy'},
        {'year': 1693, 'lat': 37.1, 'lon': 15.1, 'mag': 7.4, 'name': 'Sicily', 'region': 'Italy'},
        {'year': 1456, 'lat': 41.3, 'lon': 14.4, 'mag': 7.2, 'name': 'Naples', 'region': 'Italy'},
        {'year': 1349, 'lat': 41.9, 'lon': 13.5, 'mag': 6.5, 'name': 'L\'Aquila', 'region': 'Italy'},
        {'year': 1170, 'lat': 35.5, 'lon': 36.0, 'mag': 7.5, 'name': 'Syria', 'region': 'Middle East'},
        {'year': 1138, 'lat': 36.2, 'lon': 37.2, 'mag': 8.5, 'name': 'Aleppo', 'region': 'Syria'},

        # CHINA (continuous records back to 780 BCE)
        {'year': 1920, 'lat': 36.5, 'lon': 105.7, 'mag': 8.5, 'name': 'Haiyuan', 'region': 'China'},
        {'year': 1679, 'lat': 39.9, 'lon': 118.0, 'mag': 8.0, 'name': 'Sanhe-Pinggu', 'region': 'China'},
        {'year': 1556, 'lat': 34.5, 'lon': 109.0, 'mag': 8.0, 'name': 'Shaanxi', 'region': 'China'},
        {'year': 1303, 'lat': 36.0, 'lon': 111.0, 'mag': 8.0, 'name': 'Hongdong', 'region': 'China'},
        {'year': 1057, 'lat': 39.0, 'lon': 114.5, 'mag': 7.0, 'name': 'Daming', 'region': 'China'},
        {'year': 1038, 'lat': 23.0, 'lon': 113.0, 'mag': 7.0, 'name': 'Guangdong', 'region': 'China'},

        # JAPAN (excellent historical records)
        {'year': 1923, 'lat': 35.3, 'lon': 139.5, 'mag': 7.9, 'name': 'Kanto', 'region': 'Japan'},
        {'year': 1854, 'lat': 33.0, 'lon': 135.0, 'mag': 8.4, 'name': 'Ansei-Nankai', 'region': 'Japan'},
        {'year': 1707, 'lat': 33.2, 'lon': 135.9, 'mag': 8.6, 'name': 'Hoei', 'region': 'Japan'},
        {'year': 1596, 'lat': 33.8, 'lon': 135.8, 'mag': 7.5, 'name': 'Keicho-Fushimi', 'region': 'Japan'},

        # CALIFORNIA (tree rings + paleoseismic)
        {'year': 1906, 'lat': 37.75, 'lon': -122.5, 'mag': 7.9, 'name': 'San Francisco', 'region': 'California'},
        {'year': 1857, 'lat': 35.7, 'lon': -120.5, 'mag': 7.9, 'name': 'Fort Tejon', 'region': 'California'},

        # NEW MADRID (3 major events)
        {'year': 1811, 'lat': 36.6, 'lon': -89.6, 'mag': 7.7, 'name': 'New Madrid #1', 'region': 'Missouri'},
        {'year': 1812, 'lat': 36.6, 'lon': -89.6, 'mag': 7.5, 'name': 'New Madrid #2', 'region': 'Missouri'},

        # SOUTH AMERICA
        {'year': 1868, 'lat': -18.5, 'lon': -71.0, 'mag': 8.5, 'name': 'Arica', 'region': 'Peru/Chile'},
        {'year': 1755, 'lat': -36.8, 'lon': -73.0, 'mag': 8.5, 'name': 'Concepcion', 'region': 'Chile'},

        # MIDDLE EAST
        {'year': 1999, 'lat': 40.7, 'lon': 30.0, 'mag': 7.6, 'name': 'Izmit', 'region': 'Turkey'},
        {'year': 1939, 'lat': 39.8, 'lon': 39.5, 'mag': 7.8, 'name': 'Erzincan', 'region': 'Turkey'},
        {'year': 1668, 'lat': 38.5, 'lon': 39.5, 'mag': 8.0, 'name': 'Anatolia', 'region': 'Turkey'},
    ]

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points on Earth in km"""
    R = 6371  # Earth radius in km

    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))

    return R * c

def validate_candidate(candidate, historical_events, max_distance_km=100, max_time_offset_years=50):
    """
    Check if a cave anomaly matches a known historical earthquake.

    Returns:
        - match: dict with earthquake details if match found
        - None: if no match
    """
    candidate_year = candidate['year_ce']
    candidate_lat = candidate['latitude']
    candidate_lon = candidate['longitude']

    matches = []

    for eq in historical_events:
        # Check time window
        time_diff = abs(candidate_year - eq['year'])
        if time_diff > max_time_offset_years:
            continue

        # Check distance
        distance = haversine_distance(candidate_lat, candidate_lon, eq['lat'], eq['lon'])
        if distance > max_distance_km:
            continue

        # Found a match!
        matches.append({
            'earthquake': eq['name'],
            'eq_year': eq['year'],
            'eq_mag': eq['mag'],
            'eq_region': eq['region'],
            'cave_year': candidate_year,
            'time_offset': time_diff,
            'distance_km': distance,
            'cave_site': candidate['site_name'],
            'cave_entity': candidate['entity_name'],
            'z_score': candidate['shift_magnitude'],
            'recovery_years': candidate['recovery_years'],
            'confidence': candidate['confidence_score']
        })

    return matches if matches else None

def main():
    """Main validation pipeline"""

    # Load ML candidates
    candidates_df = load_ml_candidates('paleoseismic_caves/ml/outputs/dark_quake_candidates.csv')

    # Load historical earthquake targets
    historical_events = get_validation_targets()

    print(f"\nValidating {len(candidates_df)} ML candidates against {len(historical_events)} historical earthquakes...")
    print(f"Search criteria: ≤100 km distance, ≤50 years time offset\n")

    # Validate each candidate
    validations = []

    for idx, candidate in candidates_df.iterrows():
        matches = validate_candidate(candidate, historical_events)

        if matches:
            for match in matches:
                validations.append(match)
                print(f"✓ MATCH: {match['cave_site']} ({match['cave_year']:.0f} CE) → {match['earthquake']} ({match['eq_year']} M{match['eq_mag']})")
                print(f"  Offset: {match['time_offset']:.1f} years, {match['distance_km']:.0f} km, z={match['z_score']:.2f}σ")

    # Save results
    if validations:
        validations_df = pd.DataFrame(validations)
        validations_df.to_csv('paleoseismic_caves/ml/outputs/validated_candidates.csv', index=False)
        print(f"\n{'='*80}")
        print(f"VALIDATION COMPLETE: {len(validations)} matches found!")
        print(f"Results saved to: paleoseismic_caves/ml/outputs/validated_candidates.csv")
        print(f"{'='*80}\n")

        # Summary by region
        print("Validations by region:")
        region_counts = validations_df['eq_region'].value_counts()
        for region, count in region_counts.items():
            print(f"  {region}: {count}")
    else:
        print("\nNo matches found. Consider:")
        print("  1. Expanding distance threshold (currently 100 km)")
        print("  2. Expanding time window (currently 50 years)")
        print("  3. Adding more historical earthquakes to the target list")

if __name__ == '__main__':
    main()
