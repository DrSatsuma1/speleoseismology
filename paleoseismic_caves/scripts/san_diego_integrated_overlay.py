#!/usr/bin/env python3
"""
Rose Canyon Fault Integrated Analysis - Microseismicity + Faults + DEM
Overlay earthquakes and mapped faults on edge detection products

Author: Claude Code
Date: 2026-01-02
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import rasterio
import geopandas as gpd
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
QUAKE_ROOT = os.path.dirname(PROJECT_ROOT)
DEM_DIR = os.path.join(QUAKE_ROOT, "dem_tiles", "san_diego")

# Input files
HILLSHADE = os.path.join(DEM_DIR, "rose_canyon_hillshade.tif")
CANNY_EDGES = os.path.join(DEM_DIR, "edge_detection", "rcf_canny_edges.tif")
FAULTS = os.path.join(DEM_DIR, "usgs_faults_sandiego.geojson")
EARTHQUAKES = os.path.join(DEM_DIR, "usgs_sandiego_microseismicity_1980-2025.csv")

# Output directory
OUTPUT_DIR = os.path.join(DEM_DIR, "integrated_analysis")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Rose Canyon Fault approximate location (for reference)
RCF_LAT = 32.9
RCF_LON = -117.2


def load_raster(filepath):
    """Load raster and return data array + metadata."""
    with rasterio.open(filepath) as src:
        data = src.read(1)
        extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]
        crs = src.crs
    return data, extent, crs


def load_earthquakes(filepath):
    """Load earthquake CSV."""
    df = pd.read_csv(filepath)
    # Convert time to datetime (handle mixed formats)
    df['time'] = pd.to_datetime(df['time'], format='ISO8601')
    df['year'] = df['time'].dt.year
    return df


def find_orphan_earthquakes(eq_df, faults_gdf, distance_km=3.0):
    """
    Find earthquakes >distance_km from any mapped fault.

    Returns:
        GeoDataFrame of orphan earthquakes
    """
    from shapely.geometry import Point

    # Convert earthquakes to GeoDataFrame
    geometry = [Point(lon, lat) for lon, lat in zip(eq_df['lon'], eq_df['lat'])]
    eq_gdf = gpd.GeoDataFrame(eq_df, geometry=geometry, crs="EPSG:4326")

    # Reproject both to UTM 11N for distance calculation
    eq_utm = eq_gdf.to_crs("EPSG:26911")
    faults_utm = faults_gdf.to_crs("EPSG:26911")

    # Calculate minimum distance from each earthquake to any fault
    distances = eq_utm.geometry.apply(
        lambda pt: faults_utm.geometry.distance(pt).min()
    )

    # Convert to km
    distances_km = distances / 1000.0

    # Find orphans
    orphans = eq_gdf[distances_km > distance_km].copy()
    orphans['distance_to_fault_km'] = distances_km[distances_km > distance_km]

    return orphans


def create_integrated_figure():
    """
    Create publication-quality integrated analysis figure.

    4-panel layout:
    - Panel A: Hillshade + Faults
    - Panel B: Canny edges + Microseismicity
    - Panel C: Orphan earthquake analysis
    - Panel D: Integrated (all layers)
    """
    print("="*70)
    print("ROSE CANYON FAULT INTEGRATED ANALYSIS")
    print("="*70)

    # Load data
    print("\nLoading data...")
    hillshade, extent, crs = load_raster(HILLSHADE)
    canny, _, _ = load_raster(CANNY_EDGES)
    faults = gpd.read_file(FAULTS)
    earthquakes = load_earthquakes(EARTHQUAKES)

    print(f"  Faults: {len(faults)} features")
    print(f"  Earthquakes: {len(earthquakes)} events ({earthquakes['year'].min()}-{earthquakes['year'].max()})")
    print(f"  Magnitude range: {earthquakes['magnitude'].min():.2f} - {earthquakes['magnitude'].max():.2f}")

    # Find orphan earthquakes
    print("\nAnalyzing orphan earthquakes (>3 km from mapped faults)...")
    orphans = find_orphan_earthquakes(earthquakes, faults, distance_km=3.0)
    print(f"  Orphan earthquakes: {len(orphans)} ({len(orphans)/len(earthquakes)*100:.1f}%)")

    # Magnitude statistics for orphans
    if len(orphans) > 0:
        print(f"  Orphan magnitude range: {orphans['magnitude'].min():.2f} - {orphans['magnitude'].max():.2f}")
        print(f"  Orphans M≥3.0: {len(orphans[orphans['magnitude'] >= 3.0])}")

    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    fig.suptitle('Rose Canyon Fault - Integrated DEM, Fault, and Microseismicity Analysis',
                 fontsize=16, fontweight='bold')

    # Panel A: Hillshade + Faults
    ax = axes[0, 0]
    ax.imshow(hillshade, extent=extent, cmap='gray', origin='upper', alpha=0.8)
    faults.plot(ax=ax, color='red', linewidth=1.5, alpha=0.7, label='USGS Quaternary Faults')
    ax.set_title('A) Hillshade + Mapped Faults', fontweight='bold')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)

    # Panel B: Canny edges + All microseismicity
    ax = axes[0, 1]
    ax.imshow(canny, extent=extent, cmap='Greys', origin='upper', alpha=0.6)
    scatter = ax.scatter(earthquakes['lon'], earthquakes['lat'],
                        c=earthquakes['magnitude'], s=earthquakes['magnitude']**2,
                        cmap='YlOrRd', alpha=0.6, edgecolors='k', linewidth=0.3,
                        vmin=1, vmax=5)
    cbar = plt.colorbar(scatter, ax=ax, label='Magnitude')
    ax.set_title(f'B) Edge Detection + Microseismicity (n={len(earthquakes)})', fontweight='bold')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.grid(True, alpha=0.3)

    # Panel C: Orphan earthquake analysis
    ax = axes[1, 0]
    ax.imshow(hillshade, extent=extent, cmap='gray', origin='upper', alpha=0.5)
    faults.plot(ax=ax, color='blue', linewidth=1.0, alpha=0.5, label='Mapped faults')

    if len(orphans) > 0:
        scatter = ax.scatter(orphans['lon'], orphans['lat'],
                            c=orphans['magnitude'], s=orphans['magnitude']**2 * 3,
                            cmap='Reds', alpha=0.8, edgecolors='k', linewidth=0.5,
                            vmin=1, vmax=5)
        cbar = plt.colorbar(scatter, ax=ax, label='Magnitude')

    ax.set_title(f'C) Orphan Earthquakes (>3 km from faults, n={len(orphans)})', fontweight='bold')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)

    # Panel D: Integrated (all layers)
    ax = axes[1, 1]
    ax.imshow(canny, extent=extent, cmap='Greys', origin='upper', alpha=0.4)
    faults.plot(ax=ax, color='red', linewidth=1.5, alpha=0.7, label='USGS faults')

    # Plot all earthquakes in background
    ax.scatter(earthquakes['lon'], earthquakes['lat'],
              c='gray', s=5, alpha=0.3, label=f'All EQs (n={len(earthquakes)})')

    # Highlight larger earthquakes (M≥3.0)
    large_eq = earthquakes[earthquakes['magnitude'] >= 3.0]
    if len(large_eq) > 0:
        scatter = ax.scatter(large_eq['lon'], large_eq['lat'],
                            c=large_eq['magnitude'], s=large_eq['magnitude']**2 * 5,
                            cmap='hot_r', alpha=0.9, edgecolors='k', linewidth=0.5,
                            vmin=3, vmax=5, label=f'M≥3.0 (n={len(large_eq)})')
        cbar = plt.colorbar(scatter, ax=ax, label='Magnitude')

    ax.set_title('D) Integrated Analysis (Edges + Faults + M≥3.0)', fontweight='bold')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    # Save figure
    output_file = os.path.join(OUTPUT_DIR, 'fig_integrated_rcf_analysis.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nSaved: {output_file}")

    return orphans, large_eq


def analyze_orphan_clusters(orphans_gdf, min_cluster_size=5):
    """
    Identify spatial clusters of orphan earthquakes that might indicate
    unmapped fault segments.
    """
    if len(orphans_gdf) < min_cluster_size:
        print("\nNot enough orphan earthquakes for cluster analysis.")
        return

    from sklearn.cluster import DBSCAN
    from shapely.geometry import Point

    print(f"\n{'='*70}")
    print("ORPHAN EARTHQUAKE CLUSTER ANALYSIS")
    print(f"{'='*70}")

    # Convert to UTM for distance-based clustering
    orphans_utm = orphans_gdf.to_crs("EPSG:26911")

    # Extract coordinates
    coords = np.array([[pt.x, pt.y] for pt in orphans_utm.geometry])

    # DBSCAN clustering (eps=5000m, min_samples=5)
    clustering = DBSCAN(eps=5000, min_samples=min_cluster_size).fit(coords)
    labels = clustering.labels_

    # Number of clusters
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)

    print(f"\nClusters found: {n_clusters}")
    print(f"Noise points: {n_noise}")

    # Analyze each cluster
    for cluster_id in range(n_clusters):
        cluster_mask = labels == cluster_id
        cluster_eq = orphans_gdf[cluster_mask]

        print(f"\nCluster {cluster_id + 1}:")
        print(f"  Events: {len(cluster_eq)}")
        print(f"  Magnitude range: {cluster_eq['magnitude'].min():.2f} - {cluster_eq['magnitude'].max():.2f}")
        print(f"  Center: {cluster_eq['lat'].mean():.4f}°N, {cluster_eq['lon'].mean():.4f}°W")
        print(f"  Mean distance from faults: {cluster_eq['distance_to_fault_km'].mean():.1f} km")


def main():
    """Main analysis pipeline."""
    # Create integrated figure
    orphans, large_eq = create_integrated_figure()

    # Cluster analysis on orphans
    if len(orphans) > 0:
        analyze_orphan_clusters(orphans, min_cluster_size=5)

    # Summary statistics
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Total earthquakes (1980-2025): {len(pd.read_csv(EARTHQUAKES))}")
    print(f"Orphan earthquakes (>3 km): {len(orphans)} ({len(orphans)/len(pd.read_csv(EARTHQUAKES))*100:.1f}%)")
    print(f"M≥3.0 events: {len(large_eq)}")
    print(f"\nOutput: {OUTPUT_DIR}/")
    print("\nNext steps:")
    print("  1. Examine orphan clusters for linear patterns (unmapped faults?)")
    print("  2. Compare edge detection with microseismicity alignment")
    print("  3. Identify trenching targets where edges + faults + orphans align")
    print("  4. Write SAN_DIEGO_DEM_FINDINGS.md")


if __name__ == '__main__':
    main()
