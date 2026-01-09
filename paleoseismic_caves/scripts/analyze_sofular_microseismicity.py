#!/usr/bin/env python3
"""
Sofular Cave (Turkey) Microseismicity Analysis

Goal: Identify orphan earthquake clusters (far from mapped faults) that could
be sources of historical "dark earthquakes" detectable in the speleothem record.

Location: 41.4167°N, 31.9333°E (North Anatolian Fault Zone)
"""
import json
import math
from collections import defaultdict
import csv

# Sofular Cave location
SOFULAR_LAT = 41.4167
SOFULAR_LON = 31.9333

# North Anatolian Fault approximate azimuth (E-W trending)
NAF_AZIMUTH = 90  # East-West

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two points."""
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def calculate_azimuth(lat1, lon1, lat2, lon2):
    """Calculate azimuth from point 1 to point 2 (degrees from North)."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    azimuth = math.degrees(math.atan2(x, y))
    return (azimuth + 360) % 360

def azimuth_diff(az1, az2):
    """Calculate minimum angular difference between two azimuths."""
    diff = abs(az1 - az2)
    if diff > 180:
        diff = 360 - diff
    return diff

def point_to_line_distance(eq_lat, eq_lon, fault_coords):
    """
    Calculate minimum distance from earthquake to fault line (series of coordinates).
    Returns distance in km.
    """
    min_dist = float('inf')
    for i in range(len(fault_coords) - 1):
        # Segment from fault_coords[i] to fault_coords[i+1]
        lon1, lat1 = fault_coords[i][0], fault_coords[i][1]
        lon2, lat2 = fault_coords[i+1][0], fault_coords[i+1][1]

        # Simple approximation: distance to segment midpoint and endpoints
        d1 = haversine_distance(eq_lat, eq_lon, lat1, lon1)
        d2 = haversine_distance(eq_lat, eq_lon, lat2, lon2)
        mid_lat = (lat1 + lat2) / 2
        mid_lon = (lon1 + lon2) / 2
        d_mid = haversine_distance(eq_lat, eq_lon, mid_lat, mid_lon)

        min_dist = min(min_dist, d1, d2, d_mid)

    return min_dist

def load_gem_faults(geojson_path, lat_min, lat_max, lon_min, lon_max):
    """Load GEM faults within bounding box."""
    with open(geojson_path, 'r') as f:
        data = json.load(f)

    faults = []
    for feature in data['features']:
        coords = feature['geometry']['coordinates']
        if feature['geometry']['type'] != 'LineString':
            continue

        # Check if any point is within bounding box
        in_box = False
        for coord in coords:
            lon, lat = coord[0], coord[1]  # Handle 2D or 3D coordinates
            if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                in_box = True
                break

        if in_box:
            faults.append({
                'name': feature['properties'].get('name', 'Unknown'),
                'slip_type': feature['properties'].get('slip_type', 'Unknown'),
                'coords': coords
            })

    return faults

def load_earthquakes(json_path):
    """Load earthquakes from USGS JSON output."""
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Handle wrapped format
    if isinstance(data, list) and len(data) > 0 and 'text' in data[0]:
        earthquakes = json.loads(data[0]['text'])
    else:
        earthquakes = data

    return earthquakes

def main():
    # Paths
    eq_path = '/Users/catherine/.claude/projects/-Users-catherine-projects-quake/ad8b3ac4-e797-4f35-97f8-c025161b0580/tool-results/mcp-paleoseismic-earthquake_search-1767367979796.txt'
    gem_path = '/Users/catherine/projects/quake/paleoseismic_caves/data/gem_active_faults.geojson'

    # Load earthquakes
    print("Loading earthquakes...")
    earthquakes = load_earthquakes(eq_path)
    print(f"  Loaded {len(earthquakes)} earthquakes")

    # Load GEM faults for Turkey region (expanded box around Sofular)
    print("\nLoading GEM faults...")
    faults = load_gem_faults(gem_path,
                              lat_min=39, lat_max=43,
                              lon_min=28, lon_max=36)
    print(f"  Loaded {len(faults)} faults in region")

    # Calculate distance from each earthquake to Sofular and nearest fault
    print("\nCalculating distances...")
    results = []
    for eq in earthquakes:
        eq_lat = eq['lat']
        eq_lon = eq['lon']

        # Distance to Sofular
        dist_to_cave = haversine_distance(SOFULAR_LAT, SOFULAR_LON, eq_lat, eq_lon)

        # Azimuth from Sofular
        azimuth = calculate_azimuth(SOFULAR_LAT, SOFULAR_LON, eq_lat, eq_lon)

        # Distance to nearest fault
        min_fault_dist = float('inf')
        nearest_fault = "None"
        for fault in faults:
            d = point_to_line_distance(eq_lat, eq_lon, fault['coords'])
            if d < min_fault_dist:
                min_fault_dist = d
                nearest_fault = fault['name']

        results.append({
            'id': eq['id'],
            'time': eq['time'],
            'lat': eq_lat,
            'lon': eq_lon,
            'depth_km': eq['depth_km'],
            'magnitude': eq['magnitude'],
            'place': eq.get('place', ''),
            'dist_to_cave_km': dist_to_cave,
            'azimuth': azimuth,
            'dist_to_fault_km': min_fault_dist,
            'nearest_fault': nearest_fault,
            'is_orphan': min_fault_dist > 5  # >5km from any mapped fault
        })

    # Sort by distance to cave
    results.sort(key=lambda x: x['dist_to_cave_km'])

    # Summary statistics
    orphans = [r for r in results if r['is_orphan']]
    orphan_rate = len(orphans) / len(results) * 100 if results else 0

    print(f"\n{'='*80}")
    print(f"SOFULAR CAVE MICROSEISMICITY ANALYSIS")
    print(f"{'='*80}")
    print(f"Total earthquakes: {len(results)}")
    print(f"Orphan earthquakes (>5km from mapped fault): {len(orphans)} ({orphan_rate:.1f}%)")
    print(f"Magnitude range: {min(r['magnitude'] for r in results):.1f} - {max(r['magnitude'] for r in results):.1f}")

    # Azimuth distribution
    print(f"\n{'='*80}")
    print("AZIMUTH DISTRIBUTION (from Sofular)")
    print(f"{'='*80}")
    bins = defaultdict(int)
    for r in results:
        bin_idx = int(r['azimuth'] // 30) * 30
        bins[f"{bin_idx:03d}-{bin_idx+30:03d}°"] += 1

    for bin_name in sorted(bins.keys()):
        count = bins[bin_name]
        bar = '#' * (count // 2)
        print(f"  {bin_name}: {count:3d} {bar}")

    # Orphan clusters by azimuth
    print(f"\n{'='*80}")
    print("ORPHAN CLUSTERS (potential unmapped faults)")
    print(f"{'='*80}")
    orphan_bins = defaultdict(list)
    for r in orphans:
        bin_idx = int(r['azimuth'] // 30) * 30
        orphan_bins[f"{bin_idx:03d}-{bin_idx+30:03d}°"].append(r)

    for bin_name in sorted(orphan_bins.keys(), key=lambda x: -len(orphan_bins[x])):
        cluster = orphan_bins[bin_name]
        if len(cluster) >= 5:  # Only show significant clusters
            avg_dist = sum(r['dist_to_cave_km'] for r in cluster) / len(cluster)
            avg_depth = sum(r['depth_km'] for r in cluster) / len(cluster)
            mags = [r['magnitude'] for r in cluster]
            print(f"\n  {bin_name}: {len(cluster)} orphans")
            print(f"    Avg distance from Sofular: {avg_dist:.1f} km")
            print(f"    Avg depth: {avg_depth:.1f} km")
            print(f"    Magnitude range: {min(mags):.1f} - {max(mags):.1f}")
            print(f"    M4+ events: {sum(1 for m in mags if m >= 4)}")

    # Closest earthquakes
    print(f"\n{'='*80}")
    print("CLOSEST 20 EARTHQUAKES TO SOFULAR")
    print(f"{'='*80}")
    print(f"{'Dist':<8} {'Azimuth':<8} {'FltDist':<8} {'Mag':<6} {'Depth':<6} {'Orphan':<7} Place")
    print("-" * 100)
    for r in results[:20]:
        orphan_str = "YES" if r['is_orphan'] else "no"
        print(f"{r['dist_to_cave_km']:<8.1f} {r['azimuth']:<8.1f} {r['dist_to_fault_km']:<8.1f} {r['magnitude']:<6.1f} {r['depth_km']:<6.1f} {orphan_str:<7} {r['place'][:40]}")

    # M5+ earthquakes
    print(f"\n{'='*80}")
    print("M5+ EARTHQUAKES")
    print(f"{'='*80}")
    m5_plus = [r for r in results if r['magnitude'] >= 5]
    print(f"Total M5+: {len(m5_plus)}")
    for r in sorted(m5_plus, key=lambda x: -x['magnitude']):
        orphan_str = "ORPHAN" if r['is_orphan'] else ""
        print(f"  M{r['magnitude']:.1f} at {r['dist_to_cave_km']:.1f} km, depth {r['depth_km']:.1f} km: {r['place'][:50]} {orphan_str}")

    # Save results to CSV
    output_path = '/Users/catherine/projects/quake/paleoseismic_caves/data/turkey/sofular_microseismicity.csv'
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'time', 'lat', 'lon', 'depth_km', 'magnitude', 'place',
                                                'dist_to_cave_km', 'azimuth', 'dist_to_fault_km', 'nearest_fault', 'is_orphan'])
        writer.writeheader()
        writer.writerows(results)
    print(f"\nResults saved to: {output_path}")

    # Summary for documentation
    print(f"\n{'='*80}")
    print("SUMMARY FOR DOCUMENTATION")
    print(f"{'='*80}")
    print(f"- Total earthquakes within 200 km: {len(results)}")
    print(f"- Orphan rate: {orphan_rate:.1f}%")
    print(f"- Significant orphan clusters: {sum(1 for b, c in orphan_bins.items() if len(c) >= 5)}")
    print(f"- M5+ events: {len(m5_plus)} (orphans: {sum(1 for r in m5_plus if r['is_orphan'])})")

if __name__ == '__main__':
    main()
