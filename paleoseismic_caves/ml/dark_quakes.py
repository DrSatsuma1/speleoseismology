"""
Dark Earthquake Classifier

Analyzes ML-detected anomalies that don't match known volcanic or earthquake events.
Applies seismological criteria to identify the most promising "dark earthquake" candidates.

Classification criteria (based on Bàsura/Yok Balum methodology):
1. Recovery time >10 years (seismic signature vs 1-3 year climatic)
2. Proximity to known active faults
3. Temporal clustering (multiple caves show anomaly at same time)
4. Shift magnitude (stronger = higher confidence)
5. Regional seismicity context

Output: Ranked list of dark earthquake candidates with confidence scores
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from math import radians, sin, cos, sqrt, atan2
import requests

OUTPUT_DIR = Path(__file__).parent / "outputs"


@dataclass
class DarkQuakeCandidate:
    """A potential dark earthquake event."""
    year_ce: float
    latitude: float
    longitude: float
    shift_magnitude: float
    recovery_years: float
    site_name: str
    entity_name: str
    confidence_score: float
    evidence_summary: str
    nearby_caves: int = 0
    nearest_fault_km: Optional[float] = None
    fault_name: Optional[str] = None


# =============================================================================
# Known Seismic Zones and Faults
# =============================================================================

# Major seismic zones with approximate bounding boxes
# (min_lat, max_lat, min_lon, max_lon, zone_name, typical_magnitude_range)
SEISMIC_ZONES = [
    # Pacific Ring of Fire
    (-60, 60, 120, 180, "Western Pacific Subduction", "M6-M9"),
    (-60, 60, -180, -60, "Eastern Pacific/Americas", "M6-M9"),

    # Mediterranean-Himalayan Belt
    (30, 45, -10, 40, "Mediterranean", "M5-M7"),
    (25, 45, 40, 100, "Middle East-Himalaya", "M6-M8"),

    # Intraplate zones
    (30, 40, -125, -115, "California/SAF", "M6-M8"),
    (35, 50, -5, 15, "Central Europe/Alps", "M4-M6"),
    (-45, -30, 165, 180, "New Zealand", "M6-M8"),
    (30, 45, 125, 145, "Japan", "M6-M9"),

    # Central America
    (10, 25, -105, -80, "Central America/Caribbean", "M6-M8"),
]

# Notable fault systems (lat, lon, name, typical_magnitude)
MAJOR_FAULTS = [
    # San Andreas System
    (35.0, -119.0, "San Andreas Fault", 7.8),
    (37.5, -122.0, "Hayward Fault", 7.0),
    (34.0, -117.5, "San Jacinto Fault", 7.1),

    # Cascadia
    (45.0, -124.0, "Cascadia Subduction Zone", 9.0),

    # Mediterranean
    (43.5, 7.5, "Ligurian Alps Faults", 6.5),
    (42.0, 13.0, "Central Apennines", 6.5),
    (38.0, 22.0, "Hellenic Arc", 7.5),
    (40.0, 30.0, "North Anatolian Fault", 7.5),

    # Central America
    (15.0, -89.0, "Motagua Fault", 7.5),
    (14.0, -90.5, "Chixoy-Polochic Fault", 7.0),

    # Asia
    (35.0, 105.0, "Longmenshan Fault", 7.9),
    (28.0, 85.0, "Main Himalayan Thrust", 8.5),

    # Oceania
    (-42.0, 173.0, "Alpine Fault NZ", 8.0),
]


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in km."""
    R = 6371  # Earth radius in km

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return R * c


def get_nearest_fault(lat: float, lon: float) -> Tuple[Optional[str], Optional[float]]:
    """Find the nearest major fault to a location."""
    min_dist = float('inf')
    nearest_fault = None

    for fault_lat, fault_lon, fault_name, _ in MAJOR_FAULTS:
        dist = haversine_distance(lat, lon, fault_lat, fault_lon)
        if dist < min_dist:
            min_dist = dist
            nearest_fault = fault_name

    return nearest_fault, min_dist


def get_seismic_zone(lat: float, lon: float) -> Optional[str]:
    """Determine which seismic zone a location is in."""
    for min_lat, max_lat, min_lon, max_lon, zone_name, _ in SEISMIC_ZONES:
        if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
            return zone_name
    return None


# =============================================================================
# GEM Global Active Faults Database
# =============================================================================

# Cache for loaded GEM faults
_GEM_FAULTS_CACHE = None
_GEM_TREE_CACHE = None

GEM_FAULTS_PATH = Path(__file__).parent.parent / "data" / "gem_active_faults.geojson"


def load_gem_faults(geojson_path: Optional[Path] = None) -> Tuple[List[dict], any]:
    """
    Load GEM Global Active Faults database with spatial index.

    Returns:
        Tuple of (faults list, STRtree spatial index)
    """
    global _GEM_FAULTS_CACHE, _GEM_TREE_CACHE

    if _GEM_FAULTS_CACHE is not None:
        return _GEM_FAULTS_CACHE, _GEM_TREE_CACHE

    if geojson_path is None:
        geojson_path = GEM_FAULTS_PATH

    if not geojson_path.exists():
        print(f"WARNING: GEM faults file not found at {geojson_path}")
        return [], None

    try:
        import json
        from shapely.geometry import shape
        from shapely.strtree import STRtree

        print(f"Loading GEM Global Active Faults from {geojson_path}...")
        with open(geojson_path) as f:
            data = json.load(f)

        faults = []
        geometries = []

        for feature in data['features']:
            try:
                geom = shape(feature['geometry'])
                props = feature['properties']

                # Parse slip rate tuple if present
                slip_rate = None
                if props.get('net_slip_rate'):
                    try:
                        sr_str = props['net_slip_rate'].strip('()')
                        parts = sr_str.split(',')
                        if parts[0]:
                            slip_rate = float(parts[0])
                    except:
                        pass

                faults.append({
                    'geometry': geom,
                    'name': props.get('name', 'Unknown'),
                    'slip_type': props.get('slip_type', None),
                    'slip_rate': slip_rate,
                    'catalog': props.get('catalog_name', None)
                })
                geometries.append(geom)
            except Exception as e:
                continue

        # Build spatial index
        tree = STRtree(geometries)

        print(f"Loaded {len(faults)} faults from GEM database")

        _GEM_FAULTS_CACHE = faults
        _GEM_TREE_CACHE = tree

        return faults, tree

    except ImportError:
        print("WARNING: shapely not installed. Run: pip install shapely")
        return [], None
    except Exception as e:
        print(f"ERROR loading GEM faults: {e}")
        return [], None


def get_nearest_gem_fault(lat: float, lon: float,
                          faults: Optional[List[dict]] = None,
                          tree: Optional[any] = None) -> Tuple[Optional[str], Optional[float]]:
    """
    Find the nearest fault from the GEM database using spatial index.

    Args:
        lat, lon: Location coordinates
        faults, tree: Pre-loaded fault data (optional, will load if not provided)

    Returns:
        Tuple of (fault_name, distance_km)
    """
    if faults is None or tree is None:
        faults, tree = load_gem_faults()

    if not faults or tree is None:
        return None, None

    try:
        from shapely.geometry import Point

        point = Point(lon, lat)

        # Query nearby faults within ~5 degrees
        nearby_indices = list(tree.query(point.buffer(5)))

        if not nearby_indices:
            # No faults within 5 degrees (~550km), expand search
            nearby_indices = list(tree.query(point.buffer(10)))

        if not nearby_indices:
            return None, None

        min_dist = float('inf')
        nearest_name = None

        for idx in nearby_indices:
            fault = faults[idx]
            dist_deg = point.distance(fault['geometry'])
            # Convert degrees to km (approximate, varies with latitude)
            dist_km = dist_deg * 111 * np.cos(np.radians(lat))

            if dist_km < min_dist:
                min_dist = dist_km
                nearest_name = fault['name']

        return nearest_name, min_dist

    except Exception as e:
        print(f"Error querying GEM faults: {e}")
        return None, None


def check_fault_coverage(lat: float, lon: float, radius_km: float = 500,
                         faults: Optional[List[dict]] = None,
                         tree: Optional[any] = None) -> str:
    """
    Check if a location is within mapped fault coverage.

    Returns:
        "COVERED" if faults exist within radius_km
        "NO_COVERAGE" if no faults mapped (potential unknown fault region)
    """
    if faults is None or tree is None:
        faults, tree = load_gem_faults()

    if not faults or tree is None:
        return "UNKNOWN"

    try:
        from shapely.geometry import Point

        point = Point(lon, lat)
        radius_deg = radius_km / (111 * np.cos(np.radians(lat)))

        nearby = list(tree.query(point.buffer(radius_deg)))

        if len(nearby) == 0:
            return "NO_COVERAGE"
        else:
            return "COVERED"

    except Exception as e:
        return "UNKNOWN"


# =============================================================================
# USGS Fault Database Query
# =============================================================================

def query_usgs_faults(lat: float, lon: float, radius_km: float = 200) -> List[dict]:
    """
    Query USGS Quaternary Fault Database for nearby faults.

    Note: This queries the US faults only. For global coverage,
    use GEM Global Active Faults database.
    """
    # USGS Quaternary Fault API
    url = "https://earthquake.usgs.gov/ws/geoserve/faults.json"

    params = {
        'latitude': lat,
        'longitude': lon,
        'maxradiuskm': radius_km
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            faults = data.get('faults', {}).get('features', [])
            return [
                {
                    'name': f['properties'].get('fault_name', 'Unknown'),
                    'slip_rate': f['properties'].get('slip_rate', None),
                    'age': f['properties'].get('age', None)
                }
                for f in faults
            ]
    except Exception as e:
        pass

    return []


# =============================================================================
# Temporal Clustering Analysis
# =============================================================================

def find_temporal_clusters(anomalies: pd.DataFrame,
                           time_window_years: float = 10,
                           distance_threshold_km: float = 1000) -> Dict[float, List[dict]]:
    """
    Find anomalies that cluster in time across multiple caves.
    This suggests a real event affecting a regional aquifer system.
    """
    clusters = {}

    # Sort by year
    sorted_anomalies = anomalies.sort_values('year_ce')

    for idx, row in sorted_anomalies.iterrows():
        year = row['year_ce']

        # Find other anomalies within time window
        time_matches = sorted_anomalies[
            (abs(sorted_anomalies['year_ce'] - year) <= time_window_years) &
            (sorted_anomalies.index != idx)
        ]

        if len(time_matches) > 0:
            # Check geographic proximity
            nearby = []
            for _, match in time_matches.iterrows():
                dist = haversine_distance(row['lat'], row['lon'],
                                         match['lat'], match['lon'])
                if dist <= distance_threshold_km:
                    nearby.append({
                        'site': match['site_name'],
                        'entity': match['entity_name'],
                        'year': match['year_ce'],
                        'distance_km': dist,
                        'magnitude': match['shift_magnitude']
                    })

            if nearby:
                # Round to nearest 5 years for clustering
                cluster_year = round(year / 5) * 5
                if cluster_year not in clusters:
                    clusters[cluster_year] = []
                clusters[cluster_year].extend(nearby)

    # Deduplicate and count
    for year in clusters:
        seen = set()
        unique = []
        for item in clusters[year]:
            key = (item['site'], item['entity'])
            if key not in seen:
                seen.add(key)
                unique.append(item)
        clusters[year] = unique

    return {k: v for k, v in clusters.items() if len(v) >= 2}


# =============================================================================
# Confidence Scoring
# =============================================================================

def calculate_confidence_score(row: pd.Series,
                                nearby_caves: int = 0,
                                nearest_fault_km: Optional[float] = None) -> Tuple[float, str]:
    """
    Calculate confidence score for a dark earthquake candidate.

    Scoring:
    - Shift magnitude: |z| > 2 = base, higher = more points
    - Recovery time: >10 years = seismic signature
    - Fault proximity: closer = higher score
    - Temporal clustering: more caves = higher score

    Returns: (score 0-100, evidence summary string)
    """
    score = 0
    evidence = []

    # 1. Shift magnitude (0-25 points)
    mag = abs(row['shift_magnitude'])
    if mag >= 3.0:
        score += 25
        evidence.append(f"Very strong shift (z={mag:.2f})")
    elif mag >= 2.5:
        score += 20
        evidence.append(f"Strong shift (z={mag:.2f})")
    elif mag >= 2.0:
        score += 15
        evidence.append(f"Significant shift (z={mag:.2f})")
    else:
        score += 10
        evidence.append(f"Moderate shift (z={mag:.2f})")

    # 2. Recovery time (0-25 points)
    recovery = row.get('recovery_years', 0)
    if pd.notna(recovery) and recovery > 0:
        if recovery >= 20:
            score += 25
            evidence.append(f"Long recovery ({recovery:.0f} years) - SEISMIC SIGNATURE")
        elif recovery >= 10:
            score += 20
            evidence.append(f"Extended recovery ({recovery:.0f} years)")
        elif recovery >= 5:
            score += 10
            evidence.append(f"Moderate recovery ({recovery:.0f} years)")
        else:
            score += 5
            evidence.append(f"Short recovery ({recovery:.1f} years) - possibly climatic")

    # 3. Fault proximity (0-25 points)
    if nearest_fault_km is not None:
        if nearest_fault_km <= 100:
            score += 25
            evidence.append(f"Near major fault ({nearest_fault_km:.0f} km)")
        elif nearest_fault_km <= 300:
            score += 20
            evidence.append(f"Moderate fault distance ({nearest_fault_km:.0f} km)")
        elif nearest_fault_km <= 500:
            score += 15
            evidence.append(f"Regional fault context ({nearest_fault_km:.0f} km)")
        else:
            score += 5
            evidence.append(f"Distant from known faults ({nearest_fault_km:.0f} km)")

    # 4. Temporal clustering (0-25 points)
    if nearby_caves >= 3:
        score += 25
        evidence.append(f"Strong temporal cluster ({nearby_caves} caves)")
    elif nearby_caves >= 2:
        score += 20
        evidence.append(f"Temporal cluster ({nearby_caves} caves)")
    elif nearby_caves >= 1:
        score += 10
        evidence.append(f"Possible cluster ({nearby_caves} other cave)")
    else:
        score += 0
        evidence.append("Single-cave detection")

    return score, "; ".join(evidence)


def calculate_confidence_score_inverted(row: pd.Series,
                                        nearby_caves: int = 0,
                                        nearest_fault_km: Optional[float] = None) -> Tuple[float, str]:
    """
    INVERTED scoring: rewards candidates FAR from known faults.

    Rationale: Dark earthquakes may occur on unknown/unmapped faults.
    Being distant from known faults could indicate a discovery opportunity.
    """
    score = 0
    evidence = []

    # 1. Shift magnitude (0-25 points) - same as original
    mag = abs(row['shift_magnitude'])
    if mag >= 3.0:
        score += 25
        evidence.append(f"Very strong shift (z={mag:.2f})")
    elif mag >= 2.5:
        score += 20
        evidence.append(f"Strong shift (z={mag:.2f})")
    elif mag >= 2.0:
        score += 15
        evidence.append(f"Significant shift (z={mag:.2f})")
    else:
        score += 10
        evidence.append(f"Moderate shift (z={mag:.2f})")

    # 2. Recovery time (0-25 points) - same as original
    recovery = row.get('recovery_years', 0)
    if pd.notna(recovery) and recovery > 0:
        if recovery >= 20:
            score += 25
            evidence.append(f"Long recovery ({recovery:.0f} years) - SEISMIC SIGNATURE")
        elif recovery >= 10:
            score += 20
            evidence.append(f"Extended recovery ({recovery:.0f} years)")
        elif recovery >= 5:
            score += 10
            evidence.append(f"Moderate recovery ({recovery:.0f} years)")
        else:
            score += 5
            evidence.append(f"Short recovery ({recovery:.1f} years) - possibly climatic")

    # 3. Fault proximity - INVERTED (0-25 points)
    # Far from known faults = potential unknown fault discovery
    if nearest_fault_km is not None:
        if nearest_fault_km > 500:
            score += 20
            evidence.append(f"POTENTIAL UNKNOWN FAULT - distant from known faults ({nearest_fault_km:.0f} km)")
        elif nearest_fault_km > 300:
            score += 15
            evidence.append(f"Possible unknown fault ({nearest_fault_km:.0f} km from known)")
        elif nearest_fault_km > 100:
            score += 10
            evidence.append(f"Moderate distance from known faults ({nearest_fault_km:.0f} km)")
        else:
            score += 25
            evidence.append(f"Near known active fault ({nearest_fault_km:.0f} km)")

    # 4. Temporal clustering (0-25 points) - same as original
    if nearby_caves >= 3:
        score += 25
        evidence.append(f"Strong temporal cluster ({nearby_caves} caves)")
    elif nearby_caves >= 2:
        score += 20
        evidence.append(f"Temporal cluster ({nearby_caves} caves)")
    elif nearby_caves >= 1:
        score += 10
        evidence.append(f"Possible cluster ({nearby_caves} other cave)")
    else:
        score += 0
        evidence.append("Single-cave detection")

    return score, "; ".join(evidence)


def calculate_confidence_score_no_proximity(row: pd.Series,
                                            nearby_caves: int = 0,
                                            nearest_fault_km: Optional[float] = None) -> Tuple[float, str]:
    """
    NO PROXIMITY scoring: removes fault proximity factor entirely.

    Rationale: Fault proximity introduces circular logic. This variant
    evaluates candidates purely on signal quality (magnitude + recovery + clustering).
    Maximum score is 75 instead of 100.
    """
    score = 0
    evidence = []

    # 1. Shift magnitude (0-25 points)
    mag = abs(row['shift_magnitude'])
    if mag >= 3.0:
        score += 25
        evidence.append(f"Very strong shift (z={mag:.2f})")
    elif mag >= 2.5:
        score += 20
        evidence.append(f"Strong shift (z={mag:.2f})")
    elif mag >= 2.0:
        score += 15
        evidence.append(f"Significant shift (z={mag:.2f})")
    else:
        score += 10
        evidence.append(f"Moderate shift (z={mag:.2f})")

    # 2. Recovery time (0-25 points)
    recovery = row.get('recovery_years', 0)
    if pd.notna(recovery) and recovery > 0:
        if recovery >= 20:
            score += 25
            evidence.append(f"Long recovery ({recovery:.0f} years) - SEISMIC SIGNATURE")
        elif recovery >= 10:
            score += 20
            evidence.append(f"Extended recovery ({recovery:.0f} years)")
        elif recovery >= 5:
            score += 10
            evidence.append(f"Moderate recovery ({recovery:.0f} years)")
        else:
            score += 5
            evidence.append(f"Short recovery ({recovery:.1f} years) - possibly climatic")

    # 3. Fault proximity - REMOVED
    # Just note the distance for context, no scoring
    if nearest_fault_km is not None:
        evidence.append(f"[{nearest_fault_km:.0f} km from known fault - not scored]")

    # 4. Temporal clustering (0-25 points)
    if nearby_caves >= 3:
        score += 25
        evidence.append(f"Strong temporal cluster ({nearby_caves} caves)")
    elif nearby_caves >= 2:
        score += 20
        evidence.append(f"Temporal cluster ({nearby_caves} caves)")
    elif nearby_caves >= 1:
        score += 10
        evidence.append(f"Possible cluster ({nearby_caves} other cave)")
    else:
        score += 0
        evidence.append("Single-cave detection")

    return score, "; ".join(evidence)


def calculate_confidence_score_gem(row: pd.Series,
                                   nearby_caves: int = 0,
                                   gem_fault_name: Optional[str] = None,
                                   gem_fault_km: Optional[float] = None,
                                   fault_coverage: str = "UNKNOWN") -> Tuple[float, str]:
    """
    GEM DATABASE scoring: uses 16,195 global faults + coverage awareness.

    Key insight: If in a region with NO fault coverage in GEM database,
    the candidate gets a bonus (potential unknown fault discovery).
    """
    score = 0
    evidence = []

    # 1. Shift magnitude (0-25 points)
    mag = abs(row['shift_magnitude'])
    if mag >= 3.0:
        score += 25
        evidence.append(f"Very strong shift (z={mag:.2f})")
    elif mag >= 2.5:
        score += 20
        evidence.append(f"Strong shift (z={mag:.2f})")
    elif mag >= 2.0:
        score += 15
        evidence.append(f"Significant shift (z={mag:.2f})")
    else:
        score += 10
        evidence.append(f"Moderate shift (z={mag:.2f})")

    # 2. Recovery time (0-25 points)
    recovery = row.get('recovery_years', 0)
    if pd.notna(recovery) and recovery > 0:
        if recovery >= 20:
            score += 25
            evidence.append(f"Long recovery ({recovery:.0f} years) - SEISMIC SIGNATURE")
        elif recovery >= 10:
            score += 20
            evidence.append(f"Extended recovery ({recovery:.0f} years)")
        elif recovery >= 5:
            score += 10
            evidence.append(f"Moderate recovery ({recovery:.0f} years)")
        else:
            score += 5
            evidence.append(f"Short recovery ({recovery:.1f} years) - possibly climatic")

    # 3. Fault proximity with coverage awareness (0-25 points)
    if fault_coverage == "NO_COVERAGE":
        # No mapped faults in region - potential unknown fault discovery!
        score += 20
        evidence.append("UNMAPPED REGION - potential unknown fault discovery")
    elif gem_fault_km is not None:
        if gem_fault_km <= 50:
            score += 25
            evidence.append(f"Near GEM fault: {gem_fault_name} ({gem_fault_km:.0f} km)")
        elif gem_fault_km <= 150:
            score += 20
            evidence.append(f"Moderate distance to {gem_fault_name} ({gem_fault_km:.0f} km)")
        elif gem_fault_km <= 300:
            score += 15
            evidence.append(f"Regional fault: {gem_fault_name} ({gem_fault_km:.0f} km)")
        else:
            score += 10
            evidence.append(f"Distant from mapped faults ({gem_fault_km:.0f} km)")
    else:
        score += 5
        evidence.append("GEM query failed")

    # 4. Temporal clustering (0-25 points)
    if nearby_caves >= 3:
        score += 25
        evidence.append(f"Strong temporal cluster ({nearby_caves} caves)")
    elif nearby_caves >= 2:
        score += 20
        evidence.append(f"Temporal cluster ({nearby_caves} caves)")
    elif nearby_caves >= 1:
        score += 10
        evidence.append(f"Possible cluster ({nearby_caves} other cave)")
    else:
        score += 0
        evidence.append("Single-cave detection")

    return score, "; ".join(evidence)


def count_sisal_caves_in_region(lat: float, lon: float, radius_km: float = 500,
                                 all_sites: Optional[pd.DataFrame] = None) -> int:
    """
    Count how many SISAL caves exist within a radius of the given location.

    Used to determine if a region is well-sampled or sparse.
    """
    if all_sites is None:
        # Try to load from anomalies file
        try:
            anomalies_path = OUTPUT_DIR / "anomalies_validated.csv"
            if anomalies_path.exists():
                df = pd.read_csv(anomalies_path)
                all_sites = df[['site_name', 'lat', 'lon']].drop_duplicates()
            else:
                return 0
        except:
            return 0

    count = 0
    for _, site in all_sites.iterrows():
        dist = haversine_distance(lat, lon, site['lat'], site['lon'])
        if dist <= radius_km:
            count += 1

    return count


def calculate_coverage_adjusted_clustering(lat: float, lon: float,
                                           nearby_caves: int,
                                           all_sites: Optional[pd.DataFrame] = None) -> Tuple[int, str]:
    """
    Adjust clustering score based on regional cave density.

    Fixes the circular logic flaw: don't penalize isolation in sparse regions.

    If region has few studied caves, we can't evaluate clustering - give neutral score.
    If region has many caves and only 1 detected, that's meaningful (possibly suspicious).
    """
    caves_in_region = count_sisal_caves_in_region(lat, lon, radius_km=500, all_sites=all_sites)

    if caves_in_region <= 2:
        # Sparse coverage - cannot meaningfully evaluate clustering
        return 15, f"Sparse regional coverage ({caves_in_region} caves within 500km - clustering N/A)"
    elif caves_in_region <= 5:
        # Moderate coverage
        if nearby_caves >= 2:
            return 25, f"Strong cluster ({nearby_caves} caves in moderately-sampled region)"
        elif nearby_caves >= 1:
            return 15, f"Weak cluster ({nearby_caves} cave in moderately-sampled region)"
        else:
            return 10, f"Isolated in moderately-sampled region ({caves_in_region} caves)"
    else:
        # Well-sampled region (>5 caves within 500km)
        if nearby_caves >= 3:
            return 25, f"Strong cluster ({nearby_caves} caves in well-sampled region)"
        elif nearby_caves >= 2:
            return 20, f"Temporal cluster ({nearby_caves} caves in well-sampled region)"
        elif nearby_caves >= 1:
            return 10, f"Weak cluster ({nearby_caves} cave in well-sampled region)"
        else:
            # Isolated detection in well-sampled region = suspicious
            return 5, f"Isolated detection in well-sampled region ({caves_in_region} caves) - suspicious"


# =============================================================================
# Comparative Analysis Runner
# =============================================================================

def run_comparative_analysis(anomalies_path: Optional[Path] = None) -> Dict[str, pd.DataFrame]:
    """
    Run all 4 scoring variants and compare results.

    Variants:
    1. Original - current scoring (near known faults = bonus)
    2. Inverted - far from known faults = potential discovery
    3. No proximity - removes fault factor entirely
    4. GEM - uses global fault database with coverage awareness

    Returns dict of DataFrames, one per variant.
    """
    if anomalies_path is None:
        anomalies_path = OUTPUT_DIR / "anomalies_validated.csv"

    print("=" * 70)
    print("COMPARATIVE DARK EARTHQUAKE SCORING ANALYSIS")
    print("=" * 70)

    # Load anomalies
    df = pd.read_csv(anomalies_path)
    dark = df[df['classification'].str.contains('DARK', na=False)].copy()
    print(f"\nAnalyzing {len(dark)} dark candidates with 4 scoring methods...")

    # Get all sites for coverage calculation
    all_sites = dark[['site_name', 'lat', 'lon']].drop_duplicates()

    # Find temporal clusters (same for all variants)
    clusters = find_temporal_clusters(dark)
    cluster_counts = {}
    for year, members in clusters.items():
        for m in members:
            key = (m['site'], m['entity'])
            cluster_counts[key] = cluster_counts.get(key, 0) + len(members)

    # Load GEM faults once
    gem_faults, gem_tree = load_gem_faults()

    results = {}

    for variant in ['original', 'inverted', 'no_proximity', 'gem']:
        print(f"\n--- Running {variant.upper()} scoring ---")
        candidates = []

        for idx, row in dark.iterrows():
            # Get hardcoded fault proximity (for original/inverted/no_proximity)
            fault_name, fault_dist = get_nearest_fault(row['lat'], row['lon'])

            # Get cluster count
            key = (row['site_name'], row['entity_name'])
            nearby_caves = cluster_counts.get(key, 0)

            # Get GEM fault data (for gem variant)
            gem_fault_name, gem_fault_dist = get_nearest_gem_fault(
                row['lat'], row['lon'], gem_faults, gem_tree
            )
            fault_coverage = check_fault_coverage(
                row['lat'], row['lon'], 500, gem_faults, gem_tree
            )

            # Calculate score based on variant
            if variant == 'original':
                score, evidence = calculate_confidence_score(row, nearby_caves, fault_dist)
            elif variant == 'inverted':
                score, evidence = calculate_confidence_score_inverted(row, nearby_caves, fault_dist)
            elif variant == 'no_proximity':
                score, evidence = calculate_confidence_score_no_proximity(row, nearby_caves, fault_dist)
            elif variant == 'gem':
                # Also use coverage-adjusted clustering
                cluster_score, cluster_evidence = calculate_coverage_adjusted_clustering(
                    row['lat'], row['lon'], nearby_caves, all_sites
                )

                # Custom scoring for GEM variant with adjusted clustering
                mag = abs(row['shift_magnitude'])
                recovery = row.get('recovery_years', 0)

                score = 0
                evidence_parts = []

                # Magnitude
                if mag >= 3.0:
                    score += 25
                    evidence_parts.append(f"Very strong shift (z={mag:.2f})")
                elif mag >= 2.5:
                    score += 20
                    evidence_parts.append(f"Strong shift (z={mag:.2f})")
                elif mag >= 2.0:
                    score += 15
                    evidence_parts.append(f"Significant shift (z={mag:.2f})")
                else:
                    score += 10
                    evidence_parts.append(f"Moderate shift (z={mag:.2f})")

                # Recovery
                if pd.notna(recovery) and recovery > 0:
                    if recovery >= 20:
                        score += 25
                        evidence_parts.append(f"Long recovery ({recovery:.0f} years) - SEISMIC SIGNATURE")
                    elif recovery >= 10:
                        score += 20
                        evidence_parts.append(f"Extended recovery ({recovery:.0f} years)")
                    elif recovery >= 5:
                        score += 10
                        evidence_parts.append(f"Moderate recovery ({recovery:.0f} years)")
                    else:
                        score += 5
                        evidence_parts.append(f"Short recovery ({recovery:.1f} years)")

                # GEM fault proximity with coverage awareness
                if fault_coverage == "NO_COVERAGE":
                    score += 20
                    evidence_parts.append("UNMAPPED REGION - potential unknown fault")
                elif gem_fault_dist is not None:
                    if gem_fault_dist <= 50:
                        score += 25
                        evidence_parts.append(f"Near GEM fault: {gem_fault_name} ({gem_fault_dist:.0f} km)")
                    elif gem_fault_dist <= 150:
                        score += 20
                        evidence_parts.append(f"GEM fault: {gem_fault_name} ({gem_fault_dist:.0f} km)")
                    elif gem_fault_dist <= 300:
                        score += 15
                        evidence_parts.append(f"Regional: {gem_fault_name} ({gem_fault_dist:.0f} km)")
                    else:
                        score += 10
                        evidence_parts.append(f"Distant ({gem_fault_dist:.0f} km)")
                else:
                    score += 5
                    evidence_parts.append("GEM query failed")

                # Coverage-adjusted clustering
                score += cluster_score
                evidence_parts.append(cluster_evidence)

                evidence = "; ".join(evidence_parts)

            # Get seismic zone
            zone = get_seismic_zone(row['lat'], row['lon'])
            if zone:
                evidence += f"; Zone: {zone}"

            candidates.append({
                'year_ce': row['year_ce'],
                'site_name': row['site_name'],
                'entity_name': row['entity_name'],
                'latitude': row['lat'],
                'longitude': row['lon'],
                'shift_magnitude': row['shift_magnitude'],
                'recovery_years': row.get('recovery_years', np.nan),
                'confidence_score': score,
                'evidence': evidence,
                'nearest_fault': fault_name if variant != 'gem' else gem_fault_name,
                'fault_distance_km': fault_dist if variant != 'gem' else gem_fault_dist,
                'fault_coverage': fault_coverage if variant == 'gem' else None,
                'seismic_zone': zone,
                'cluster_caves': nearby_caves,
                'scoring_method': variant
            })

        result_df = pd.DataFrame(candidates)
        result_df = result_df.sort_values('confidence_score', ascending=False)
        results[variant] = result_df

        # Save to file
        output_path = OUTPUT_DIR / f"dark_quake_candidates_{variant}.csv"
        result_df.to_csv(output_path, index=False)
        print(f"Saved {len(result_df)} candidates to {output_path}")

    return results


def generate_comparison_report(results: Dict[str, pd.DataFrame]) -> str:
    """Generate a comparison report showing score deltas between variants."""
    lines = []
    lines.append("=" * 80)
    lines.append("COMPARATIVE SCORING ANALYSIS REPORT")
    lines.append("Addressing circular logic flaws in fault proximity and clustering scoring")
    lines.append("=" * 80)
    lines.append("")

    # Summary by variant
    lines.append("SUMMARY BY SCORING METHOD")
    lines.append("-" * 40)
    for variant, df in results.items():
        high = len(df[df['confidence_score'] >= 70])
        med = len(df[(df['confidence_score'] >= 50) & (df['confidence_score'] < 70)])
        low = len(df[df['confidence_score'] < 50])
        lines.append(f"  {variant.upper():15} | High: {high:3} | Med: {med:3} | Low: {low:3}")
    lines.append("")

    # Compare rankings
    original = results['original'].set_index(['site_name', 'entity_name', 'year_ce'])
    lines.append("TOP SCORE CHANGES (candidates that moved up with alternative scoring)")
    lines.append("-" * 80)

    for variant in ['inverted', 'no_proximity', 'gem']:
        lines.append(f"\n{variant.upper()} vs ORIGINAL:")

        variant_df = results[variant].set_index(['site_name', 'entity_name', 'year_ce'])

        # Calculate deltas
        deltas = []
        for idx in variant_df.index:
            if idx in original.index:
                orig_score = original.loc[idx, 'confidence_score']
                new_score = variant_df.loc[idx, 'confidence_score']
                delta = new_score - orig_score
                if abs(delta) > 0:
                    deltas.append({
                        'site': idx[0],
                        'entity': idx[1],
                        'year': idx[2],
                        'original': orig_score,
                        'new': new_score,
                        'delta': delta
                    })

        deltas = sorted(deltas, key=lambda x: x['delta'], reverse=True)

        # Top gainers
        lines.append("  GAINERS (moved UP):")
        for d in deltas[:5]:
            if d['delta'] > 0:
                lines.append(f"    {d['site'][:20]:20} {d['year']:.0f} CE: {d['original']:.0f} → {d['new']:.0f} (+{d['delta']:.0f})")

        # Top losers
        lines.append("  LOSERS (moved DOWN):")
        for d in deltas[-5:]:
            if d['delta'] < 0:
                lines.append(f"    {d['site'][:20]:20} {d['year']:.0f} CE: {d['original']:.0f} → {d['new']:.0f} ({d['delta']:.0f})")

    # Identify potential unknown fault candidates
    lines.append("")
    lines.append("=" * 80)
    lines.append("POTENTIAL UNKNOWN FAULT DISCOVERIES")
    lines.append("(Candidates that scored higher with inverted/gem scoring)")
    lines.append("-" * 80)

    gem_df = results['gem']
    unmapped = gem_df[gem_df['fault_coverage'] == 'NO_COVERAGE']
    if len(unmapped) > 0:
        lines.append(f"\n{len(unmapped)} candidates in UNMAPPED REGIONS:")
        for _, row in unmapped.head(10).iterrows():
            lines.append(f"  {row['year_ce']:.0f} CE: {row['site_name']} (score: {row['confidence_score']})")
            lines.append(f"         {row['evidence'][:80]}")

    return "\n".join(lines)


# =============================================================================
# Main Classification Pipeline
# =============================================================================

def classify_dark_quakes(anomalies_path: Optional[Path] = None) -> pd.DataFrame:
    """
    Main classification pipeline for dark earthquake candidates.
    """
    if anomalies_path is None:
        anomalies_path = OUTPUT_DIR / "anomalies_validated.csv"

    print("=" * 60)
    print("DARK EARTHQUAKE CLASSIFIER")
    print("=" * 60)

    # Load validated anomalies
    df = pd.read_csv(anomalies_path)
    print(f"\nLoaded {len(df)} validated anomalies")

    # Filter to dark candidates only
    dark = df[df['classification'].str.contains('DARK', na=False)].copy()
    print(f"Dark candidates: {len(dark)}")

    if len(dark) == 0:
        print("No dark candidates found!")
        return pd.DataFrame()

    # Find temporal clusters
    print("\nAnalyzing temporal clusters...")
    clusters = find_temporal_clusters(dark)
    print(f"Found {len(clusters)} temporal clusters")

    # Create cluster lookup
    cluster_counts = {}
    for year, members in clusters.items():
        for m in members:
            key = (m['site'], m['entity'])
            cluster_counts[key] = cluster_counts.get(key, 0) + len(members)

    # Classify each candidate
    print("\nClassifying candidates...")
    candidates = []

    for idx, row in dark.iterrows():
        # Get fault proximity
        fault_name, fault_dist = get_nearest_fault(row['lat'], row['lon'])

        # Get cluster count
        key = (row['site_name'], row['entity_name'])
        nearby_caves = cluster_counts.get(key, 0)

        # Calculate confidence
        score, evidence = calculate_confidence_score(row, nearby_caves, fault_dist)

        # Get seismic zone
        zone = get_seismic_zone(row['lat'], row['lon'])
        if zone:
            evidence += f"; Zone: {zone}"

        candidates.append({
            'year_ce': row['year_ce'],
            'site_name': row['site_name'],
            'entity_name': row['entity_name'],
            'latitude': row['lat'],
            'longitude': row['lon'],
            'shift_magnitude': row['shift_magnitude'],
            'recovery_years': row.get('recovery_years', np.nan),
            'confidence_score': score,
            'evidence': evidence,
            'nearest_fault': fault_name,
            'fault_distance_km': fault_dist,
            'seismic_zone': zone,
            'cluster_caves': nearby_caves,
            'classification': row['classification']
        })

    result = pd.DataFrame(candidates)
    result = result.sort_values('confidence_score', ascending=False)

    return result


def generate_report(candidates: pd.DataFrame) -> str:
    """Generate a summary report of dark earthquake candidates."""
    lines = []
    lines.append("=" * 70)
    lines.append("DARK EARTHQUAKE CANDIDATES - RANKED BY CONFIDENCE")
    lines.append("=" * 70)
    lines.append("")

    # Summary stats
    lines.append(f"Total candidates: {len(candidates)}")
    lines.append(f"High confidence (score >= 70): {len(candidates[candidates['confidence_score'] >= 70])}")
    lines.append(f"Medium confidence (50-69): {len(candidates[(candidates['confidence_score'] >= 50) & (candidates['confidence_score'] < 70)])}")
    lines.append(f"Low confidence (<50): {len(candidates[candidates['confidence_score'] < 50])}")
    lines.append("")

    # Top candidates
    lines.append("-" * 70)
    lines.append("TOP 20 CANDIDATES")
    lines.append("-" * 70)

    for i, (_, row) in enumerate(candidates.head(20).iterrows(), 1):
        lines.append(f"\n{i}. {row['site_name']} ({row['entity_name']})")
        lines.append(f"   Year: {row['year_ce']:.0f} CE")
        lines.append(f"   Location: {row['latitude']:.2f}°, {row['longitude']:.2f}°")
        lines.append(f"   Confidence: {row['confidence_score']}/100")
        lines.append(f"   Evidence: {row['evidence']}")
        if row['nearest_fault']:
            lines.append(f"   Nearest fault: {row['nearest_fault']} ({row['fault_distance_km']:.0f} km)")
        if row['seismic_zone']:
            lines.append(f"   Seismic zone: {row['seismic_zone']}")

    # Regional breakdown
    lines.append("")
    lines.append("-" * 70)
    lines.append("CANDIDATES BY SEISMIC ZONE")
    lines.append("-" * 70)

    zone_counts = candidates.groupby('seismic_zone').size().sort_values(ascending=False)
    for zone, count in zone_counts.items():
        if pd.notna(zone):
            lines.append(f"  {zone}: {count}")

    # Temporal distribution
    lines.append("")
    lines.append("-" * 70)
    lines.append("CANDIDATES BY CENTURY")
    lines.append("-" * 70)

    candidates['century'] = (candidates['year_ce'] // 100).astype(int) * 100
    century_counts = candidates.groupby('century').size().sort_index()
    for century, count in century_counts.items():
        lines.append(f"  {century}s CE: {count}")

    return "\n".join(lines)


def main():
    """Run the dark earthquake classification pipeline."""

    # Classify candidates
    candidates = classify_dark_quakes()

    if len(candidates) == 0:
        return

    # Save results
    output_path = OUTPUT_DIR / "dark_quake_candidates.csv"
    candidates.to_csv(output_path, index=False)
    print(f"\nSaved {len(candidates)} candidates to {output_path}")

    # Generate and print report
    report = generate_report(candidates)
    print("\n" + report)

    # Save report
    report_path = OUTPUT_DIR / "dark_quake_report.txt"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"\nSaved report to {report_path}")

    # Highlight special cases
    print("\n" + "=" * 70)
    print("NOTABLE FINDINGS")
    print("=" * 70)

    # High confidence candidates
    high_conf = candidates[candidates['confidence_score'] >= 70]
    if len(high_conf) > 0:
        print(f"\n{len(high_conf)} HIGH CONFIDENCE candidates (score >= 70):")
        for _, row in high_conf.iterrows():
            print(f"  - {row['year_ce']:.0f} CE: {row['site_name']} (score={row['confidence_score']})")

    # Long recovery times (seismic signature)
    long_recovery = candidates[candidates['recovery_years'] >= 15]
    if len(long_recovery) > 0:
        print(f"\n{len(long_recovery)} candidates with LONG RECOVERY (>15 years) - seismic signature:")
        for _, row in long_recovery.head(10).iterrows():
            print(f"  - {row['year_ce']:.0f} CE: {row['site_name']} ({row['recovery_years']:.0f} year recovery)")

    # Clustered events
    clustered = candidates[candidates['cluster_caves'] >= 2]
    if len(clustered) > 0:
        print(f"\n{len(clustered)} candidates with TEMPORAL CLUSTERING (2+ caves):")
        for _, row in clustered.head(10).iterrows():
            print(f"  - {row['year_ce']:.0f} CE: {row['site_name']} ({row['cluster_caves']} caves)")

    return candidates


def main_comparative():
    """Run the comparative scoring analysis to fix circular logic flaws."""

    # Run all 4 scoring variants
    results = run_comparative_analysis()

    if not results:
        print("No results generated!")
        return

    # Generate comparison report
    report = generate_comparison_report(results)
    print("\n" + report)

    # Save comparison report
    report_path = OUTPUT_DIR / "scoring_comparison_report.txt"
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"\nSaved comparison report to {report_path}")

    return results


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--compare':
        # Run comparative analysis
        results = main_comparative()
    else:
        # Run original pipeline
        results = main()
