#!/usr/bin/env python3
"""
Generate GIS overlay of T. Porra Fault on hillshade for Bàsura Cave region.

This script creates a publication-quality figure showing:
- TINITALY DEM hillshade as base layer
- ITHACA capable faults within 50km of Bàsura Cave
- T. Porra Fault highlighted as primary 1285 candidate
- Bàsura Cave location
- Distance rings (10km, 25km, 50km)
"""

import json
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches

# Try to import rasterio, fall back to PIL if not available
try:
    import rasterio
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False
    from PIL import Image

# Configuration
BASURA_LAT = 44.1275
BASURA_LON = 8.1108

# Get the script directory for relative path resolution
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)  # paleoseismic_caves
QUAKE_ROOT = os.path.dirname(PROJECT_ROOT)  # quake
DEM_TILES_DIR = os.path.join(QUAKE_ROOT, "dem_tiles")
OUTPUT_FILE = os.path.join(DEM_TILES_DIR, "tporra_overlay.png")

# Key faults to highlight
KEY_FAULTS = {
    94207: {"name": "T. Porra Fault", "color": "red", "linewidth": 3, "priority": 1},
    94050: {"name": "Saorge-Taggia", "color": "orange", "linewidth": 2, "priority": 2},
}

def load_ithaca_faults(geojson_path):
    """Load ITHACA fault data from GeoJSON."""
    with open(geojson_path, 'r') as f:
        data = json.load(f)
    return data['features']

def extract_fault_coords(feature):
    """Extract coordinates from a fault feature."""
    geom = feature['geometry']
    coords = []
    if geom['type'] == 'MultiLineString':
        for line in geom['coordinates']:
            coords.extend(line)
    elif geom['type'] == 'LineString':
        coords = geom['coordinates']
    return coords

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two points."""
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

def utm_to_latlon(easting, northing, zone=32, northern=True):
    """Convert UTM to lat/lon (approximate for zone 32N - Liguria)."""
    # Simplified conversion for zone 32N
    # More accurate would use pyproj, but this is close enough for visualization
    k0 = 0.9996
    a = 6378137.0  # WGS84 semi-major axis
    e = 0.0818192  # eccentricity
    e1 = (1 - np.sqrt(1 - e**2)) / (1 + np.sqrt(1 - e**2))

    x = easting - 500000  # Remove false easting
    y = northing

    M = y / k0
    mu = M / (a * (1 - e**2/4 - 3*e**4/64))

    phi1 = mu + (3*e1/2 - 27*e1**3/32) * np.sin(2*mu)
    phi1 += (21*e1**2/16 - 55*e1**4/32) * np.sin(4*mu)

    N1 = a / np.sqrt(1 - e**2 * np.sin(phi1)**2)
    T1 = np.tan(phi1)**2
    C1 = (e**2 / (1-e**2)) * np.cos(phi1)**2
    R1 = a * (1 - e**2) / (1 - e**2 * np.sin(phi1)**2)**1.5
    D = x / (N1 * k0)

    lat = phi1 - (N1 * np.tan(phi1) / R1) * (D**2/2)
    lon_rad = D / np.cos(phi1)

    lat_deg = np.degrees(lat)
    lon_deg = np.degrees(lon_rad) + (zone * 6 - 183)  # Central meridian

    return lat_deg, lon_deg

def load_hillshade(filepath):
    """Load hillshade raster and return array with extent in lat/lon."""
    if HAS_RASTERIO:
        with rasterio.open(filepath) as src:
            data = src.read(1)
            bounds = src.bounds
            # Check if coordinates are in UTM (large values)
            if bounds.left > 1000:
                # Convert UTM corners to lat/lon
                lat_ll, lon_ll = utm_to_latlon(bounds.left, bounds.bottom)
                lat_ur, lon_ur = utm_to_latlon(bounds.right, bounds.top)
                extent = [lon_ll, lon_ur, lat_ll, lat_ur]
            else:
                extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]
            return data, extent
    else:
        # Fallback: use PIL and estimate extent from filename
        img = Image.open(filepath)
        data = np.array(img)
        # Estimate extent for Toirano area (20km around Bàsura)
        extent = [BASURA_LON - 0.15, BASURA_LON + 0.15,
                  BASURA_LAT - 0.12, BASURA_LAT + 0.12]
        return data, extent

def main():
    print("Loading ITHACA fault data...")
    faults = load_ithaca_faults(f"{DEM_TILES_DIR}/ithaca_liguria.geojson")
    print(f"  Loaded {len(faults)} faults")

    # Filter faults within 50km of Bàsura
    nearby_faults = []
    for f in faults:
        coords = extract_fault_coords(f)
        if not coords:
            continue
        # Check if any point is within 50km
        for lon, lat in coords:
            dist = haversine_distance(BASURA_LAT, BASURA_LON, lat, lon)
            if dist < 50:
                nearby_faults.append(f)
                break
    print(f"  {len(nearby_faults)} faults within 50km of Bàsura")

    # Find T. Porra specifically
    tporra = None
    for f in faults:
        if f['properties'].get('faultcode') == 94207:
            tporra = f
            break

    if tporra:
        coords = extract_fault_coords(tporra)
        print(f"  T. Porra Fault: {len(coords)} vertices")
        if coords:
            center_lon = np.mean([c[0] for c in coords])
            center_lat = np.mean([c[1] for c in coords])
            print(f"  T. Porra center: {center_lat:.4f}°N, {center_lon:.4f}°E")
    else:
        print("  WARNING: T. Porra Fault not found!")

    # Load hillshade
    print("\nLoading hillshade...")
    hillshade_path = f"{DEM_TILES_DIR}/toirano_hillshade.tif"
    try:
        hillshade, extent = load_hillshade(hillshade_path)
        print(f"  Hillshade shape: {hillshade.shape}")
        print(f"  Extent: {extent}")
        has_hillshade = True
    except Exception as e:
        print(f"  Could not load hillshade: {e}")
        has_hillshade = False
        extent = [7.9, 8.35, 43.95, 44.25]  # Default extent

    # Create figure
    print("\nCreating figure...")
    fig, ax = plt.subplots(figsize=(14, 12))

    # Plot hillshade if available
    if has_hillshade:
        ax.imshow(hillshade, cmap='gray', extent=extent, origin='upper', alpha=0.8)

    # Set extent to focus on region of interest (include T. Porra at ~8.25, 44.22)
    ax.set_xlim(8.00, 8.32)
    ax.set_ylim(44.06, 44.26)

    # Plot all nearby faults (background)
    for f in nearby_faults:
        coords = extract_fault_coords(f)
        if not coords:
            continue
        faultcode = f['properties'].get('faultcode')
        kinematics = f['properties'].get('kinematics', 'ND')

        # Skip if this is a highlighted fault (plot separately)
        if faultcode in KEY_FAULTS:
            continue

        # Color by kinematics
        if 'Normal' in kinematics:
            color = '#4444aa'
        elif 'Reverse' in kinematics:
            color = '#aa4444'
        elif 'Strike' in kinematics:
            color = '#44aa44'
        else:
            color = '#666666'

        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        ax.plot(lons, lats, color=color, linewidth=0.8, alpha=0.6)

    # Plot key faults with emphasis
    for faultcode, style in KEY_FAULTS.items():
        for f in faults:
            if f['properties'].get('faultcode') == faultcode:
                coords = extract_fault_coords(f)
                if coords:
                    lons = [c[0] for c in coords]
                    lats = [c[1] for c in coords]
                    ax.plot(lons, lats, color=style['color'],
                           linewidth=style['linewidth'],
                           label=style['name'],
                           zorder=10)
                break

    # Plot Bàsura Cave
    ax.scatter([BASURA_LON], [BASURA_LAT], c='cyan', s=200, marker='*',
               edgecolors='black', linewidths=1.5, zorder=20, label='Bàsura Cave')
    ax.annotate('Bàsura Cave', (BASURA_LON, BASURA_LAT),
                xytext=(10, 10), textcoords='offset points',
                fontsize=11, fontweight='bold', color='white',
                bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))

    # Add distance rings (approximate - degrees to km varies with latitude)
    # At 44°N, 1° longitude ≈ 80 km, 1° latitude ≈ 111 km
    km_per_deg_lon = 80
    km_per_deg_lat = 111

    for dist_km, ls in [(10, '-'), (20, '--')]:
        # Approximate ellipse
        theta = np.linspace(0, 2*np.pi, 100)
        r_lon = dist_km / km_per_deg_lon
        r_lat = dist_km / km_per_deg_lat
        x = BASURA_LON + r_lon * np.cos(theta)
        y = BASURA_LAT + r_lat * np.sin(theta)
        ax.plot(x, y, 'white', linestyle=ls, linewidth=1.2, alpha=0.8)
        # Label at 45 degrees
        label_x = BASURA_LON + r_lon * 0.707
        label_y = BASURA_LAT + r_lat * 0.707
        if 8.00 < label_x < 8.32 and 44.06 < label_y < 44.26:
            ax.annotate(f'{dist_km} km', (label_x, label_y), fontsize=9, color='white',
                       fontweight='bold', bbox=dict(boxstyle='round', facecolor='black', alpha=0.5))

    # Legend
    legend_elements = [
        Line2D([0], [0], color='red', linewidth=3, label='T. Porra Fault (14.25 km)'),
        Line2D([0], [0], color='orange', linewidth=2, label='Saorge-Taggia Fault'),
        Line2D([0], [0], color='#4444aa', linewidth=1, label='Normal faults'),
        Line2D([0], [0], color='#aa4444', linewidth=1, label='Reverse faults'),
        Line2D([0], [0], color='#44aa44', linewidth=1, label='Strike-slip faults'),
        Line2D([0], [0], marker='*', color='w', markerfacecolor='cyan',
               markersize=15, label='Bàsura Cave'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

    # Labels and title
    ax.set_xlabel('Longitude (°E)', fontsize=12)
    ax.set_ylabel('Latitude (°N)', fontsize=12)
    ax.set_title('ITHACA Capable Faults near Bàsura Cave\n'
                 'T. Porra Fault: Candidate Source for 1285 "Dark Earthquake"',
                 fontsize=14, fontweight='bold')

    # Grid
    ax.grid(True, alpha=0.3)

    # Add text box with key info
    textstr = '\n'.join([
        'T. Porra Fault (ITHACA 94207)',
        '• Distance: 14.25 km from Bàsura',
        '• Strike: ESE-WNW (111.1°)',
        '• Length: 5.89 km mapped',
        '• Kinematics: Not Determined',
        '• Literature: NONE (unstudied)',
        '',
        'Candidate source for',
        '1285 CE "Dark Earthquake"'
    ])
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.9)
    ax.text(0.02, 0.02, textstr, transform=ax.transAxes, fontsize=9,
            verticalalignment='bottom', bbox=props)

    plt.tight_layout()

    # Save figure
    print(f"\nSaving to {OUTPUT_FILE}...")
    plt.savefig(OUTPUT_FILE, dpi=200, bbox_inches='tight')
    print("Done!")

    # Also save a high-res version
    hires_output = OUTPUT_FILE.replace('.png', '_hires.png')
    plt.savefig(hires_output, dpi=300, bbox_inches='tight')
    print(f"High-res version saved to {hires_output}")

if __name__ == '__main__':
    main()
