#!/usr/bin/env python3
"""
Map INGV microseismicity against ITHACA known faults to identify missing faults.

Creates a static matplotlib map showing:
- Earthquakes colored by azimuth cluster
- ITHACA faults colored by kinematics
- Distance rings from Basura Cave
- Gap analysis highlighting orphan earthquake clusters

Output: dem_tiles/microseismicity_vs_faults.png
"""

import json
import math
import os

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

# Configuration
BASURA_LAT = 44.1275
BASURA_LON = 8.1108
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
QUAKE_ROOT = os.path.dirname(PROJECT_ROOT)
DEM_TILES_DIR = os.path.join(QUAKE_ROOT, "dem_tiles")
OUTPUT_FILE = os.path.join(DEM_TILES_DIR, "microseismicity_vs_faults.png")

# Cluster definitions (azimuth ranges)
CLUSTERS = {
    "NE": {"range": (30, 60), "color": "blue", "name": "NE Cluster (30-60°)"},
    "NNW": {"range": (330, 360), "color": "green", "name": "NNW Cluster (330-360°)"},
    "ESE": {"range": (90, 130), "color": "orange", "name": "ESE Cluster (90-130°, T.Porra)"},
}

# Fault kinematics colors
KINEMATICS_COLORS = {
    "Normal": "#0066cc",
    "Reverse": "#cc0000",
    "Strike Slip": "#00cc00",
    "Oblique Normal": "#6699cc",
    "ND": "#999999",
}


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two points."""
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def calculate_azimuth(lat1, lon1, lat2, lon2):
    """Calculate bearing from point 1 to point 2."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    azimuth = math.degrees(math.atan2(x, y))
    return (azimuth + 360) % 360


def get_cluster(azimuth):
    """Determine which cluster an earthquake belongs to based on azimuth."""
    for name, config in CLUSTERS.items():
        low, high = config["range"]
        if low <= azimuth <= high:
            return name, config["color"]
    return "Other", "#888888"


def get_fault_color(kinematics):
    """Get color based on fault kinematics."""
    if not kinematics:
        return KINEMATICS_COLORS["ND"]
    for key, color in KINEMATICS_COLORS.items():
        if key.lower() in kinematics.lower():
            return color
    return KINEMATICS_COLORS["ND"]


def load_earthquakes():
    """Load INGV earthquake catalog."""
    earthquakes = []
    data_file = os.path.join(PROJECT_ROOT, "data", "ingv_liguria_raw.txt")

    with open(data_file, 'r') as f:
        header = f.readline()
        for line in f:
            parts = line.strip().split('|')
            if len(parts) >= 11:
                try:
                    eq = {
                        'time': parts[1][:10],  # Just date
                        'lat': float(parts[2]),
                        'lon': float(parts[3]),
                        'depth': float(parts[4]) if parts[4] else 10.0,
                        'mag': float(parts[10]) if parts[10] else 0.5,
                        'location': parts[12] if len(parts) > 12 else '',
                        'event_type': parts[13] if len(parts) > 13 else 'earthquake'
                    }
                    # Filter out quarry blasts
                    if 'blast' in eq['event_type'].lower():
                        continue
                    eq['distance'] = haversine_distance(BASURA_LAT, BASURA_LON, eq['lat'], eq['lon'])
                    eq['azimuth'] = calculate_azimuth(BASURA_LAT, BASURA_LON, eq['lat'], eq['lon'])
                    eq['cluster'], eq['color'] = get_cluster(eq['azimuth'])
                    earthquakes.append(eq)
                except (ValueError, IndexError):
                    continue
    return earthquakes


def load_faults(max_distance_km=30):
    """Load ITHACA faults within max_distance of Basura."""
    geojson_path = os.path.join(DEM_TILES_DIR, "ithaca_liguria.geojson")

    with open(geojson_path, 'r') as f:
        data = json.load(f)

    nearby_faults = []
    for feature in data['features']:
        coords = []
        geom = feature['geometry']
        if geom['type'] == 'MultiLineString':
            for line in geom['coordinates']:
                coords.extend(line)
        elif geom['type'] == 'LineString':
            coords = geom['coordinates']

        if not coords:
            continue

        # Check if any point is within max_distance
        for lon, lat in coords:
            dist = haversine_distance(BASURA_LAT, BASURA_LON, lat, lon)
            if dist < max_distance_km:
                # Add color based on kinematics
                kinematics = feature['properties'].get('kinematics', 'ND')
                feature['properties']['_color'] = get_fault_color(kinematics)
                feature['properties']['_min_dist'] = min(
                    haversine_distance(BASURA_LAT, BASURA_LON, c[1], c[0])
                    for c in coords
                )
                nearby_faults.append(feature)
                break

    return nearby_faults


def find_nearest_fault(lat, lon, faults):
    """Find the nearest fault to a point."""
    min_dist = float('inf')
    nearest = None

    for fault in faults:
        geom = fault['geometry']
        coords = []
        if geom['type'] == 'MultiLineString':
            for line in geom['coordinates']:
                coords.extend(line)
        elif geom['type'] == 'LineString':
            coords = geom['coordinates']

        for flon, flat in coords:
            dist = haversine_distance(lat, lon, flat, flon)
            if dist < min_dist:
                min_dist = dist
                nearest = fault

    return nearest, min_dist


def analyze_gaps(earthquakes, faults, threshold_km=3):
    """Find earthquakes far from any mapped fault."""
    orphans = []
    for eq in earthquakes:
        nearest, dist = find_nearest_fault(eq['lat'], eq['lon'], faults)
        if dist > threshold_km:
            eq['nearest_fault_dist'] = dist
            eq['nearest_fault'] = nearest['properties'].get('name', 'Unknown') if nearest else None
            orphans.append(eq)
    return orphans


def create_map(earthquakes, faults, orphans):
    """Create matplotlib map."""
    fig, ax = plt.subplots(figsize=(14, 12))

    # Set extent to show the region
    all_lats = [eq['lat'] for eq in earthquakes] + [BASURA_LAT]
    all_lons = [eq['lon'] for eq in earthquakes] + [BASURA_LON]
    margin = 0.05
    ax.set_xlim(min(all_lons) - margin, max(all_lons) + margin)
    ax.set_ylim(min(all_lats) - margin, max(all_lats) + margin)

    # Plot faults first (background)
    for fault in faults:
        color = fault['properties'].get('_color', '#999999')
        geom = fault['geometry']
        if geom['type'] == 'MultiLineString':
            for line in geom['coordinates']:
                lons = [c[0] for c in line]
                lats = [c[1] for c in line]
                ax.plot(lons, lats, color=color, linewidth=2, alpha=0.8, zorder=2)
        elif geom['type'] == 'LineString':
            lons = [c[0] for c in geom['coordinates']]
            lats = [c[1] for c in geom['coordinates']]
            ax.plot(lons, lats, color=color, linewidth=2, alpha=0.8, zorder=2)

    # Plot earthquakes by cluster
    for cluster_name, config in CLUSTERS.items():
        cluster_eqs = [eq for eq in earthquakes if eq['cluster'] == cluster_name]
        if cluster_eqs:
            lons = [eq['lon'] for eq in cluster_eqs]
            lats = [eq['lat'] for eq in cluster_eqs]
            sizes = [max(10, eq['mag'] * 15) for eq in cluster_eqs]
            ax.scatter(lons, lats, s=sizes, c=config['color'], alpha=0.6,
                      edgecolors='white', linewidths=0.5, label=config['name'],
                      zorder=3)

    # Plot "Other" cluster
    other_eqs = [eq for eq in earthquakes if eq['cluster'] == 'Other']
    if other_eqs:
        lons = [eq['lon'] for eq in other_eqs]
        lats = [eq['lat'] for eq in other_eqs]
        sizes = [max(10, eq['mag'] * 15) for eq in other_eqs]
        ax.scatter(lons, lats, s=sizes, c='#888888', alpha=0.4,
                  edgecolors='white', linewidths=0.5, label=f'Other ({len(other_eqs)})',
                  zorder=3)

    # Highlight orphan earthquakes
    if orphans:
        orphan_lons = [eq['lon'] for eq in orphans]
        orphan_lats = [eq['lat'] for eq in orphans]
        ax.scatter(orphan_lons, orphan_lats, s=100, c='yellow',
                  edgecolors='red', linewidths=2, marker='o', alpha=0.8,
                  label=f'Orphan (>3km from fault): {len(orphans)}', zorder=5)

    # Plot Basura Cave
    ax.scatter([BASURA_LON], [BASURA_LAT], s=300, c='cyan', marker='*',
              edgecolors='black', linewidths=2, label='Basura Cave', zorder=10)
    ax.annotate('Basura Cave', (BASURA_LON, BASURA_LAT), xytext=(5, 5),
               textcoords='offset points', fontsize=10, fontweight='bold')

    # Add distance rings
    km_per_deg_lon = 80  # At 44°N
    km_per_deg_lat = 111
    for dist_km in [5, 10, 20]:
        theta = [i * 2 * math.pi / 100 for i in range(101)]
        r_lon = dist_km / km_per_deg_lon
        r_lat = dist_km / km_per_deg_lat
        x = [BASURA_LON + r_lon * math.cos(t) for t in theta]
        y = [BASURA_LAT + r_lat * math.sin(t) for t in theta]
        ax.plot(x, y, 'k--', linewidth=1, alpha=0.5)
        # Label at 45 degrees
        label_x = BASURA_LON + r_lon * 0.707
        label_y = BASURA_LAT + r_lat * 0.707
        ax.annotate(f'{dist_km} km', (label_x, label_y), fontsize=8, alpha=0.7)

    # Legend
    legend_elements = [
        Line2D([0], [0], color='blue', marker='o', linestyle='None',
               markersize=8, label='NE Cluster (30-60°)'),
        Line2D([0], [0], color='green', marker='o', linestyle='None',
               markersize=8, label='NNW Cluster (330-360°)'),
        Line2D([0], [0], color='orange', marker='o', linestyle='None',
               markersize=8, label='ESE Cluster (90-130°)'),
        Line2D([0], [0], color='#888', marker='o', linestyle='None',
               markersize=8, label='Other'),
        Line2D([0], [0], color='yellow', marker='o', linestyle='None',
               markeredgecolor='red', markeredgewidth=2, markersize=10,
               label=f'Orphan EQ (>3km): {len(orphans)}'),
        Line2D([0], [0], color='#0066cc', linewidth=2, label='Normal fault'),
        Line2D([0], [0], color='#cc0000', linewidth=2, label='Reverse fault'),
        Line2D([0], [0], color='#00cc00', linewidth=2, label='Strike-slip fault'),
        Line2D([0], [0], color='cyan', marker='*', linestyle='None',
               markersize=15, markeredgecolor='black', label='Basura Cave'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=9)

    # Labels
    ax.set_xlabel('Longitude (°E)', fontsize=12)
    ax.set_ylabel('Latitude (°N)', fontsize=12)
    ax.set_title('INGV Microseismicity (2003-2024) vs ITHACA Faults\n'
                 f'{len(earthquakes)} earthquakes, {len(faults)} faults, {len(orphans)} orphans',
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)

    # Summary text box
    textstr = '\n'.join([
        'Orphan EQ = >3km from any ITHACA fault',
        '',
        f'NE cluster: {sum(1 for eq in orphans if eq["cluster"]=="NE")} orphans',
        f'NNW cluster: {sum(1 for eq in orphans if eq["cluster"]=="NNW")} orphans',
        f'ESE cluster: {sum(1 for eq in orphans if eq["cluster"]=="ESE")} orphans',
        f'Other: {sum(1 for eq in orphans if eq["cluster"]=="Other")} orphans',
    ])
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)
    ax.text(0.02, 0.02, textstr, transform=ax.transAxes, fontsize=9,
            verticalalignment='bottom', bbox=props)

    plt.tight_layout()
    return fig


def print_summary(earthquakes, faults, orphans):
    """Print analysis summary to terminal."""
    print("\n" + "="*60)
    print("MICROSEISMICITY vs FAULTS ANALYSIS")
    print("="*60)

    print(f"\nTotal earthquakes: {len(earthquakes)}")
    print(f"Total faults within 30km: {len(faults)}")
    print(f"Orphan earthquakes (>3km from any fault): {len(orphans)}")

    # Cluster statistics
    print("\n--- Cluster Statistics ---")
    for cluster_name, config in CLUSTERS.items():
        count = sum(1 for eq in earthquakes if eq['cluster'] == cluster_name)
        print(f"{config['name']}: {count} events")
    other_count = sum(1 for eq in earthquakes if eq['cluster'] == 'Other')
    print(f"Other: {other_count} events")

    # Orphan analysis by cluster
    print("\n--- Orphan Events by Cluster ---")
    orphan_clusters = {}
    for eq in orphans:
        cluster = eq['cluster']
        if cluster not in orphan_clusters:
            orphan_clusters[cluster] = []
        orphan_clusters[cluster].append(eq)

    for cluster, eqs in sorted(orphan_clusters.items(), key=lambda x: -len(x[1])):
        print(f"\n{cluster}: {len(eqs)} orphan events")
        # Find geographic center
        if eqs:
            avg_lat = sum(eq['lat'] for eq in eqs) / len(eqs)
            avg_lon = sum(eq['lon'] for eq in eqs) / len(eqs)
            avg_az = sum(eq['azimuth'] for eq in eqs) / len(eqs)
            avg_dist = sum(eq['distance'] for eq in eqs) / len(eqs)
            print(f"  Center: {avg_lat:.4f}°N, {avg_lon:.4f}°E")
            print(f"  Average azimuth: {avg_az:.0f}°, distance: {avg_dist:.1f} km")

            # Most common locations
            locs = {}
            for eq in eqs:
                loc = eq['location'].split('(')[0].strip()
                locs[loc] = locs.get(loc, 0) + 1
            top_locs = sorted(locs.items(), key=lambda x: -x[1])[:3]
            print(f"  Top locations: {', '.join(f'{loc} ({n})' for loc, n in top_locs)}")

    # Key findings
    print("\n" + "="*60)
    print("KEY FINDINGS - POTENTIAL MISSING FAULTS")
    print("="*60)

    if orphan_clusters:
        for cluster, eqs in sorted(orphan_clusters.items(), key=lambda x: -len(x[1])):
            if len(eqs) >= 5:  # Only report clusters with 5+ orphan events
                avg_lat = sum(eq['lat'] for eq in eqs) / len(eqs)
                avg_lon = sum(eq['lon'] for eq in eqs) / len(eqs)
                avg_az = sum(eq['azimuth'] for eq in eqs) / len(eqs)
                print(f"\n*** POTENTIAL UNMAPPED FAULT ***")
                print(f"  Cluster: {cluster}")
                print(f"  Events: {len(eqs)}")
                print(f"  Approximate center: {avg_lat:.4f}°N, {avg_lon:.4f}°E")
                print(f"  Implied strike: ~{avg_az:.0f}° or ~{(avg_az + 180) % 360:.0f}°")
    else:
        print("\nNo significant orphan clusters found.")


def main():
    print("Loading earthquake data...")
    earthquakes = load_earthquakes()
    print(f"  Loaded {len(earthquakes)} earthquakes")

    print("Loading ITHACA faults...")
    faults = load_faults(max_distance_km=30)
    print(f"  Loaded {len(faults)} faults within 30km")

    print("Analyzing gaps...")
    orphans = analyze_gaps(earthquakes, faults, threshold_km=3)
    print(f"  Found {len(orphans)} orphan earthquakes (>3km from any fault)")

    print_summary(earthquakes, faults, orphans)

    print(f"\nCreating map...")
    fig = create_map(earthquakes, faults, orphans)

    print(f"Saving to {OUTPUT_FILE}...")
    fig.savefig(OUTPUT_FILE, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"\nDone! Map saved to: {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
