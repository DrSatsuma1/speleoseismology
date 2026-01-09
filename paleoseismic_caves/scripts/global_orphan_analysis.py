#!/usr/bin/env python3
"""
Global Orphan Earthquake Analysis Pipeline

Systematically analyzes microseismicity near SISAL caves to identify
"orphan clusters" - earthquakes far from mapped faults that indicate
unmapped active structures. These structures existed historically and
may be sources of "dark earthquakes" detectable in speleothem records.

Methodology validated in Italy: 80% orphan rate revealed unmapped fault
now the primary candidate for 1285/1394 dark earthquakes.

Usage:
    python global_orphan_analysis.py --cave sofular
    python global_orphan_analysis.py --lat 41.42 --lon 31.93 --name "Custom Cave"
    python global_orphan_analysis.py --all  # Run all SISAL priority caves
"""

import argparse
import json
import math
import csv
import os
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

# Project paths
PROJECT_ROOT = '/Users/catherine/projects/quake/paleoseismic_caves'
GEM_FAULTS_PATH = os.path.join(PROJECT_ROOT, 'data/gem_active_faults.geojson')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'data')

# Priority caves from SISAL with significant sample counts near seismic zones
PRIORITY_CAVES = {
    'sofular': {'lat': 41.4167, 'lon': 31.9333, 'entity_id': 305, 'region': 'turkey',
                'name': 'Sofular Cave', 'context': 'North Anatolian Fault Zone'},
    'jeita': {'lat': 33.95, 'lon': 35.65, 'entity_id': 58, 'region': 'lebanon',
              'name': 'Jeita Cave', 'context': 'Dead Sea Transform'},
    'closani': {'lat': 45.1, 'lon': 22.8, 'entity_id': 390, 'region': 'romania',
                'name': 'Closani Cave', 'context': 'Vrancea Seismic Zone'},
    'basura': {'lat': 44.1275, 'lon': 8.1108, 'entity_id': None, 'region': 'italy',
               'name': 'Bàsura Cave', 'context': 'Ligurian Alps'},
    'larga': {'lat': 18.3, 'lon': -66.8, 'entity_id': 812, 'region': 'puerto_rico',
              'name': 'Larga Cave', 'context': 'Puerto Rico Trench'},
    'chen_ha': {'lat': 16.7, 'lon': -89.1, 'entity_id': 404, 'region': 'belize',
                'name': 'Chen Ha Cave', 'context': 'Motagua/Caribbean'},
    'corchia': {'lat': 44.0, 'lon': 10.2, 'entity_id': 669, 'region': 'italy',
                'name': 'Antro del Corchia', 'context': 'Northern Apennines'},
    'pozzo_cucu': {'lat': 40.9, 'lon': 17.2, 'entity_id': 838, 'region': 'italy',
                   'name': 'Pozzo Cucù', 'context': 'Apulia/Adriatic'},
    'sahiya': {'lat': 30.6, 'lon': 77.9, 'entity_id': 132, 'region': 'india',
               'name': 'Sahiya Cave', 'context': 'Himalayan Front'},
    'dandak': {'lat': 19.0, 'lon': 82.0, 'entity_id': 278, 'region': 'india',
               'name': 'Dandak Cave', 'context': 'Central India'},
    'shatuca': {'lat': -5.7, 'lon': -77.9, 'entity_id': 434, 'region': 'peru',
                'name': 'Shatuca Cave', 'context': 'Andes subduction'},
    'yok_balum': {'lat': 16.2, 'lon': -89.1, 'entity_id': 393, 'region': 'belize',
                  'name': 'Yok Balum Cave', 'context': 'Maya Mountains/Motagua'},
    'oregon_caves': {'lat': 42.1, 'lon': -123.4, 'entity_id': None, 'region': 'usa',
                     'name': 'Oregon Caves', 'context': 'Cascadia Subduction Zone'},
}


@dataclass
class Earthquake:
    """Earthquake event with calculated distances."""
    id: str
    time: str
    lat: float
    lon: float
    depth_km: float
    magnitude: float
    place: str
    dist_to_cave_km: float = 0.0
    azimuth: float = 0.0
    dist_to_fault_km: float = float('inf')
    nearest_fault: str = ''
    is_orphan: bool = False


@dataclass
class OrphanCluster:
    """Cluster of orphan earthquakes."""
    azimuth_bin: str
    count: int
    avg_distance_km: float
    avg_depth_km: float
    mag_range: Tuple[float, float]
    m4_plus_count: int
    m5_plus_count: int


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance in km between two points."""
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def calculate_azimuth(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate azimuth from point 1 to point 2 (degrees from North)."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    azimuth = math.degrees(math.atan2(x, y))
    return (azimuth + 360) % 360


def point_to_line_distance(eq_lat: float, eq_lon: float, fault_coords: List) -> float:
    """
    Calculate minimum distance from earthquake to fault line (series of coordinates).
    Returns distance in km.
    """
    min_dist = float('inf')
    for i in range(len(fault_coords) - 1):
        # Handle both 2D and 3D coordinates
        lon1, lat1 = fault_coords[i][0], fault_coords[i][1]
        lon2, lat2 = fault_coords[i+1][0], fault_coords[i+1][1]

        # Distance to segment endpoints and midpoint
        d1 = haversine_distance(eq_lat, eq_lon, lat1, lon1)
        d2 = haversine_distance(eq_lat, eq_lon, lat2, lon2)
        mid_lat = (lat1 + lat2) / 2
        mid_lon = (lon1 + lon2) / 2
        d_mid = haversine_distance(eq_lat, eq_lon, mid_lat, mid_lon)

        min_dist = min(min_dist, d1, d2, d_mid)

    return min_dist


def load_gem_faults(geojson_path: str, lat: float, lon: float, radius_km: float = 200) -> List[Dict]:
    """Load GEM faults within radius of cave location."""
    # Approximate bounding box
    lat_range = radius_km / 111  # ~111 km per degree latitude
    lon_range = radius_km / (111 * math.cos(math.radians(lat)))

    lat_min, lat_max = lat - lat_range, lat + lat_range
    lon_min, lon_max = lon - lon_range, lon + lon_range

    with open(geojson_path, 'r') as f:
        data = json.load(f)

    faults = []
    for feature in data['features']:
        if feature['geometry']['type'] != 'LineString':
            continue

        coords = feature['geometry']['coordinates']

        # Check if any point is within bounding box
        in_box = False
        for coord in coords:
            c_lon, c_lat = coord[0], coord[1]
            if lat_min <= c_lat <= lat_max and lon_min <= c_lon <= lon_max:
                in_box = True
                break

        if in_box:
            faults.append({
                'name': feature['properties'].get('name', 'Unknown'),
                'slip_type': feature['properties'].get('slip_type', 'Unknown'),
                'coords': coords
            })

    return faults


def load_earthquakes_from_json(json_path: str) -> List[Dict]:
    """Load earthquakes from USGS JSON output."""
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Handle MCP tool wrapped format
    if isinstance(data, list) and len(data) > 0 and 'text' in data[0]:
        earthquakes = json.loads(data[0]['text'])
    else:
        earthquakes = data

    return earthquakes


def analyze_orphan_clusters(earthquakes: List[Earthquake], min_cluster_size: int = 5) -> List[OrphanCluster]:
    """Identify and characterize orphan clusters by azimuth."""
    orphans = [eq for eq in earthquakes if eq.is_orphan]

    # Bin by 30° azimuth sectors
    bins = defaultdict(list)
    for eq in orphans:
        bin_idx = int(eq.azimuth // 30) * 30
        bin_name = f"{bin_idx:03d}-{bin_idx+30:03d}°"
        bins[bin_name].append(eq)

    clusters = []
    for bin_name, eqs in sorted(bins.items(), key=lambda x: -len(x[1])):
        if len(eqs) >= min_cluster_size:
            mags = [eq.magnitude for eq in eqs]
            clusters.append(OrphanCluster(
                azimuth_bin=bin_name,
                count=len(eqs),
                avg_distance_km=sum(eq.dist_to_cave_km for eq in eqs) / len(eqs),
                avg_depth_km=sum(eq.depth_km for eq in eqs) / len(eqs),
                mag_range=(min(mags), max(mags)),
                m4_plus_count=sum(1 for m in mags if m >= 4),
                m5_plus_count=sum(1 for m in mags if m >= 5)
            ))

    return clusters


def analyze_cave_region(
    cave_lat: float,
    cave_lon: float,
    cave_name: str,
    earthquakes: List[Dict],
    orphan_threshold_km: float = 5.0,
    search_radius_km: float = 200.0
) -> Dict:
    """
    Main analysis function for a cave region.

    Args:
        cave_lat, cave_lon: Cave location
        cave_name: Name for output files
        earthquakes: List of earthquake dicts from USGS query
        orphan_threshold_km: Distance from fault to be considered "orphan"
        search_radius_km: Radius for fault loading

    Returns:
        Dictionary with analysis results
    """
    # Load faults
    if os.path.exists(GEM_FAULTS_PATH):
        faults = load_gem_faults(GEM_FAULTS_PATH, cave_lat, cave_lon, search_radius_km)
    else:
        print(f"Warning: GEM faults file not found at {GEM_FAULTS_PATH}")
        faults = []

    # Process earthquakes
    processed = []
    for eq in earthquakes:
        earthquake = Earthquake(
            id=eq.get('id', ''),
            time=eq.get('time', ''),
            lat=eq['lat'],
            lon=eq['lon'],
            depth_km=eq.get('depth_km', 10.0),
            magnitude=eq.get('magnitude', 0.0),
            place=eq.get('place', '')
        )

        # Distance and azimuth from cave
        earthquake.dist_to_cave_km = haversine_distance(cave_lat, cave_lon, earthquake.lat, earthquake.lon)
        earthquake.azimuth = calculate_azimuth(cave_lat, cave_lon, earthquake.lat, earthquake.lon)

        # Distance to nearest fault
        min_fault_dist = float('inf')
        nearest_fault = "None"
        for fault in faults:
            d = point_to_line_distance(earthquake.lat, earthquake.lon, fault['coords'])
            if d < min_fault_dist:
                min_fault_dist = d
                nearest_fault = fault['name']

        earthquake.dist_to_fault_km = min_fault_dist
        earthquake.nearest_fault = nearest_fault
        earthquake.is_orphan = min_fault_dist > orphan_threshold_km

        processed.append(earthquake)

    # Sort by distance to cave
    processed.sort(key=lambda x: x.dist_to_cave_km)

    # Statistics
    orphans = [eq for eq in processed if eq.is_orphan]
    orphan_rate = len(orphans) / len(processed) * 100 if processed else 0
    m5_plus = [eq for eq in processed if eq.magnitude >= 5]
    m5_orphans = [eq for eq in m5_plus if eq.is_orphan]

    # Cluster analysis
    clusters = analyze_orphan_clusters(processed)

    return {
        'cave_name': cave_name,
        'cave_lat': cave_lat,
        'cave_lon': cave_lon,
        'total_earthquakes': len(processed),
        'orphan_count': len(orphans),
        'orphan_rate': orphan_rate,
        'fault_count': len(faults),
        'm5_plus_total': len(m5_plus),
        'm5_plus_orphans': len(m5_orphans),
        'clusters': clusters,
        'earthquakes': processed
    }


def print_results(results: Dict):
    """Print analysis results to terminal."""
    print(f"\n{'='*80}")
    print(f"ORPHAN EARTHQUAKE ANALYSIS: {results['cave_name']}")
    print(f"{'='*80}")
    print(f"Location: {results['cave_lat']:.4f}°N, {results['cave_lon']:.4f}°E")
    print(f"Total earthquakes: {results['total_earthquakes']}")
    print(f"GEM faults in region: {results['fault_count']}")
    print(f"Orphan earthquakes (>5km from fault): {results['orphan_count']} ({results['orphan_rate']:.1f}%)")
    print(f"M5+ events: {results['m5_plus_total']} ({results['m5_plus_orphans']} orphans)")

    if results['clusters']:
        print(f"\n{'='*80}")
        print("SIGNIFICANT ORPHAN CLUSTERS (≥5 events)")
        print(f"{'='*80}")
        print(f"{'Azimuth':<15} {'Count':<8} {'Avg Dist':<10} {'Avg Depth':<10} {'M4+':<6} {'M5+':<6}")
        print("-" * 60)
        for c in results['clusters']:
            print(f"{c.azimuth_bin:<15} {c.count:<8} {c.avg_distance_km:<10.1f} {c.avg_depth_km:<10.1f} {c.m4_plus_count:<6} {c.m5_plus_count:<6}")

    # Top 10 closest earthquakes
    print(f"\n{'='*80}")
    print("CLOSEST 10 EARTHQUAKES")
    print(f"{'='*80}")
    print(f"{'Dist':<8} {'Azimuth':<10} {'FltDist':<8} {'Mag':<6} {'Depth':<7} {'Orphan':<8} Place")
    print("-" * 90)
    for eq in results['earthquakes'][:10]:
        orphan_str = "YES" if eq.is_orphan else ""
        print(f"{eq.dist_to_cave_km:<8.1f} {eq.azimuth:<10.1f} {eq.dist_to_fault_km:<8.1f} {eq.magnitude:<6.1f} {eq.depth_km:<7.1f} {orphan_str:<8} {eq.place[:30]}")


def save_results_csv(results: Dict, output_path: str):
    """Save earthquake results to CSV."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'time', 'lat', 'lon', 'depth_km', 'magnitude', 'place',
                        'dist_to_cave_km', 'azimuth', 'dist_to_fault_km', 'nearest_fault', 'is_orphan'])
        for eq in results['earthquakes']:
            writer.writerow([eq.id, eq.time, eq.lat, eq.lon, eq.depth_km, eq.magnitude, eq.place,
                           eq.dist_to_cave_km, eq.azimuth, eq.dist_to_fault_km, eq.nearest_fault, eq.is_orphan])

    print(f"\nResults saved to: {output_path}")


def generate_summary_table(all_results: List[Dict]) -> str:
    """Generate markdown summary table of all analyzed caves."""
    lines = [
        "# Global Orphan Earthquake Analysis Summary",
        "",
        "| Cave | Location | Total EQs | Orphan Rate | M5+ (Orphans) | Top Cluster |",
        "|------|----------|-----------|-------------|---------------|-------------|"
    ]

    for r in sorted(all_results, key=lambda x: -x['orphan_rate']):
        top_cluster = r['clusters'][0].azimuth_bin if r['clusters'] else "None"
        lines.append(
            f"| {r['cave_name']} | {r['cave_lat']:.1f}°N, {r['cave_lon']:.1f}°E | "
            f"{r['total_earthquakes']} | {r['orphan_rate']:.1f}% | "
            f"{r['m5_plus_total']} ({r['m5_plus_orphans']}) | {top_cluster} |"
        )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Global orphan earthquake analysis')
    parser.add_argument('--cave', type=str, help='Cave name from PRIORITY_CAVES dict')
    parser.add_argument('--lat', type=float, help='Custom cave latitude')
    parser.add_argument('--lon', type=float, help='Custom cave longitude')
    parser.add_argument('--name', type=str, default='Custom Cave', help='Custom cave name')
    parser.add_argument('--earthquakes', type=str, help='Path to earthquakes JSON file')
    parser.add_argument('--all', action='store_true', help='Run analysis for all priority caves')
    parser.add_argument('--output', type=str, help='Output CSV path')

    args = parser.parse_args()

    if args.all:
        print("Running analysis for all priority caves requires earthquake data for each.")
        print("Use individual --cave runs or provide earthquake data via MCP tools.")
        for cave_key, cave_info in PRIORITY_CAVES.items():
            print(f"  {cave_key}: {cave_info['name']} ({cave_info['context']})")
        return

    # Determine cave location
    if args.cave:
        if args.cave not in PRIORITY_CAVES:
            print(f"Unknown cave: {args.cave}")
            print(f"Available: {', '.join(PRIORITY_CAVES.keys())}")
            return
        cave_info = PRIORITY_CAVES[args.cave]
        cave_lat = cave_info['lat']
        cave_lon = cave_info['lon']
        cave_name = cave_info['name']
        region = cave_info['region']
    elif args.lat and args.lon:
        cave_lat = args.lat
        cave_lon = args.lon
        cave_name = args.name
        region = 'custom'
    else:
        print("Specify --cave or --lat/--lon")
        return

    # Load earthquakes
    if args.earthquakes:
        earthquakes = load_earthquakes_from_json(args.earthquakes)
    else:
        print("No earthquake data provided. Use --earthquakes or call via MCP tools.")
        print(f"\nExample MCP usage:")
        print(f"  earthquake_search(lat={cave_lat}, lon={cave_lon}, radius_km=200, min_magnitude=2)")
        return

    # Run analysis
    results = analyze_cave_region(cave_lat, cave_lon, cave_name, earthquakes)

    # Print results
    print_results(results)

    # Save CSV
    output_path = args.output or os.path.join(OUTPUT_DIR, region, f'{args.cave or "custom"}_microseismicity.csv')
    save_results_csv(results, output_path)


if __name__ == '__main__':
    main()
