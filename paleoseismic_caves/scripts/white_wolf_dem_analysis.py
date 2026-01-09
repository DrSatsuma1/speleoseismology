#!/usr/bin/env python3
"""
White Wolf Fault DEM Lineament Analysis

Analyzes USGS 1/3 arc-second DEMs to identify lineaments related to the
White Wolf fault system - potential source of Crystal Cave ~1745 CE anomaly.

Coverage:
- n35w119, n35w120: White Wolf fault zone (~35°N)
- n36w119: Kern Canyon area
- n37w119: Crystal Cave area (~36.59°N)

Author: Claude Code
Date: 2026-01-03
"""

import os
from pathlib import Path
import numpy as np
import rasterio
from rasterio.merge import merge
from rasterio.warp import calculate_default_transform, reproject, Resampling
from scipy.ndimage import sobel, gaussian_filter, uniform_filter
from skimage import feature
from skimage.morphology import skeletonize
import matplotlib.pyplot as plt

# Configuration
CRYSTAL_CAVE_LAT = 36.59
CRYSTAL_CAVE_LON = -118.82

# White Wolf fault approximate endpoints (from SCEC CFM)
WHITE_WOLF_WEST = (35.03, -119.10)  # Near Wheeler Ridge
WHITE_WOLF_EAST = (35.35, -118.60)  # Near Arvin

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
QUAKE_ROOT = PROJECT_ROOT.parent
DEM_DIR = QUAKE_ROOT / "dem_tiles" / "white_wolf"
OUTPUT_DIR = DEM_DIR / "analysis"

# Input DEM tiles
DEM_TILES = [
    DEM_DIR / "USGS_13_n35w119.tif",
    DEM_DIR / "USGS_13_n35w120.tif",
    DEM_DIR / "USGS_13_n36w119.tif",
    DEM_DIR / "USGS_13_n37w119.tif",
]

def mosaic_dems():
    """Mosaic all DEM tiles into single raster."""
    print("Mosaicking DEM tiles...")

    src_files = []
    for tile in DEM_TILES:
        if tile.exists():
            src_files.append(rasterio.open(tile))
            print(f"  Opened: {tile.name}")
        else:
            print(f"  WARNING: Missing {tile.name}")

    if not src_files:
        raise FileNotFoundError("No DEM tiles found")

    mosaic, out_transform = merge(src_files)
    out_meta = src_files[0].meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_transform,
        "compress": "lzw"
    })

    # Close source files
    for src in src_files:
        src.close()

    print(f"  Mosaic shape: {mosaic.shape}")
    return mosaic[0], out_meta, out_transform


def extract_white_wolf_region(dem, transform, meta, buffer_km=30):
    """Extract region around White Wolf fault with buffer."""
    print(f"Extracting White Wolf region ({buffer_km}km buffer)...")

    # Calculate bounding box
    lat_min = WHITE_WOLF_WEST[0] - buffer_km/111
    lat_max = WHITE_WOLF_EAST[0] + buffer_km/111
    lon_min = WHITE_WOLF_WEST[1] - buffer_km/(111*np.cos(np.radians(35)))
    lon_max = WHITE_WOLF_EAST[1] + buffer_km/(111*np.cos(np.radians(35)))

    print(f"  Bounds: {lat_min:.3f}-{lat_max:.3f}N, {lon_min:.3f}-{lon_max:.3f}W")

    # Convert to pixel coordinates
    # transform: (a=scale_x, b=0, c=x_origin, d=0, e=scale_y, f=y_origin)
    col_min = int((lon_min - transform.c) / transform.a)
    col_max = int((lon_max - transform.c) / transform.a)
    row_min = int((lat_max - transform.f) / transform.e)  # Note: lat_max for row_min (north up)
    row_max = int((lat_min - transform.f) / transform.e)

    # Clamp to array bounds
    row_min = max(0, row_min)
    row_max = min(dem.shape[0], row_max)
    col_min = max(0, col_min)
    col_max = min(dem.shape[1], col_max)

    print(f"  Pixels: rows {row_min}-{row_max}, cols {col_min}-{col_max}")

    subset = dem[row_min:row_max, col_min:col_max]

    # Update transform for subset
    new_transform = rasterio.transform.from_bounds(
        lon_min, lat_min, lon_max, lat_max,
        col_max - col_min, row_max - row_min
    )

    new_meta = meta.copy()
    new_meta.update({
        "height": subset.shape[0],
        "width": subset.shape[1],
        "transform": new_transform
    })

    print(f"  Subset shape: {subset.shape}")
    return subset, new_meta, new_transform


def compute_hillshade(dem, azimuth=315, altitude=45):
    """Compute hillshade from DEM."""
    print(f"Computing hillshade (az={azimuth}, alt={altitude})...")

    # Compute gradients
    dx = sobel(dem.astype(float), axis=1)
    dy = sobel(dem.astype(float), axis=0)

    # Convert to slope and aspect
    slope = np.arctan(np.sqrt(dx**2 + dy**2))
    aspect = np.arctan2(-dx, dy)

    # Hillshade formula
    az_rad = np.radians(azimuth)
    alt_rad = np.radians(altitude)

    hillshade = (np.cos(alt_rad) * np.cos(slope) +
                 np.sin(alt_rad) * np.sin(slope) * np.cos(az_rad - aspect))

    # Normalize to 0-255
    hillshade = ((hillshade + 1) / 2 * 255).astype(np.uint8)

    return hillshade


def compute_edge_detection(dem):
    """Run edge detection suite."""
    print("Computing edge detection...")

    results = {}

    # Sobel magnitude (omnidirectional)
    print("  Sobel magnitude...")
    sx = sobel(dem.astype(float), axis=0)
    sy = sobel(dem.astype(float), axis=1)
    magnitude = np.hypot(sx, sy)
    results['sobel_mag'] = ((magnitude - magnitude.min()) /
                            (magnitude.max() - magnitude.min()) * 255).astype(np.uint8)

    # Canny edges
    print("  Canny edges...")
    dem_smooth = gaussian_filter(dem.astype(float), sigma=1.5)
    edges = feature.canny(dem_smooth, sigma=1.0,
                         low_threshold=0.1, high_threshold=0.3)
    results['canny'] = (edges * 255).astype(np.uint8)
    print(f"    Edge pixels: {edges.sum():,}")

    # Directional Sobel for NE-SW lineaments (White Wolf trend ~N55E)
    print("  Directional Sobel (NE-SW, ~55 deg)...")
    # NE-SW lineaments show up in E-W Sobel
    # Keep as float32 for better visualization
    results['sobel_ew'] = sy.astype(np.float32)
    results['sobel_ew_norm'] = ((sy - sy.min()) / (sy.max() - sy.min()) * 255).astype(np.uint8)

    return results


def compute_drainage_analysis(dem):
    """Compute drainage patterns."""
    print("Computing drainage analysis...")

    results = {}

    # Better flow accumulation using curvature (valleys have negative curvature)
    print("  Flow accumulation (curvature-based)...")
    dem_smooth = gaussian_filter(dem.astype(float), sigma=3)

    # Compute second derivatives (curvature)
    dx2 = sobel(sobel(dem_smooth, axis=1), axis=1)
    dy2 = sobel(sobel(dem_smooth, axis=0), axis=0)
    curvature = dx2 + dy2  # Laplacian - valleys are positive

    # Valleys have positive curvature (concave up)
    valley_enhance = np.clip(curvature, 0, None)
    flow_accum = gaussian_filter(valley_enhance, sigma=5)
    flow_log = np.log10(flow_accum + 1)
    results['flow_accum'] = flow_log.astype(np.float32)

    # Stream network extraction - use lower threshold
    print("  Stream network...")
    valid_pixels = flow_log[flow_log > 0]
    if len(valid_pixels) > 0:
        threshold = np.percentile(valid_pixels, 85)  # Lower threshold
        streams = flow_log > threshold
        # Clean up with morphological operations
        from scipy.ndimage import binary_opening, binary_closing
        streams = binary_opening(streams, iterations=1)
        streams = binary_closing(streams, iterations=1)
        stream_skeleton = skeletonize(streams)
        results['streams'] = (stream_skeleton * 255).astype(np.uint8)
        print(f"    Stream pixels: {stream_skeleton.sum():,}")
    else:
        print("    WARNING: No valid flow accumulation values")
        results['streams'] = np.zeros(dem.shape, dtype=np.uint8)

    # Drainage density
    print("  Drainage density...")
    stream_array = results['streams'] / 255.0  # Convert back to binary
    density = uniform_filter(stream_array, size=50)
    results['drainage_density'] = density.astype(np.float32)

    return results


def save_raster(data, path, meta):
    """Save raster to GeoTIFF."""
    out_meta = meta.copy()
    out_meta.update({
        'dtype': data.dtype,
        'count': 1,
        'compress': 'lzw'
    })
    if data.dtype == np.uint8:
        out_meta['nodata'] = None

    with rasterio.open(path, 'w', **out_meta) as dst:
        dst.write(data, 1)
    print(f"  Saved: {path.name}")


def create_overview_figure(hillshade, edges, streams, meta, transform):
    """Create publication figure showing key results."""
    print("Creating overview figure...")

    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    fig.suptitle('White Wolf Fault DEM Lineament Analysis\n'
                 'Potential Source of Crystal Cave ~1745 CE Anomaly',
                 fontsize=16, fontweight='bold')

    # Panel A: Hillshade
    ax = axes[0, 0]
    ax.imshow(hillshade, cmap='gray', interpolation='nearest')
    ax.set_title('A) Hillshade (NW illumination)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Longitude (pixels)')
    ax.set_ylabel('Latitude (pixels)')

    # Add White Wolf fault line (approximate)
    # Convert fault endpoints to pixel coordinates
    ww_west_col = int((WHITE_WOLF_WEST[1] - transform.c) / transform.a)
    ww_west_row = int((WHITE_WOLF_WEST[0] - transform.f) / transform.e)
    ww_east_col = int((WHITE_WOLF_EAST[1] - transform.c) / transform.a)
    ww_east_row = int((WHITE_WOLF_EAST[0] - transform.f) / transform.e)

    # Check if fault is in view
    if (0 <= ww_west_col < hillshade.shape[1] and
        0 <= ww_east_col < hillshade.shape[1]):
        ax.plot([ww_west_col, ww_east_col], [ww_west_row, ww_east_row],
               'r-', linewidth=3, label='White Wolf Fault (approx)')
        ax.legend(loc='upper right')

    # Panel B: Canny edges
    ax = axes[0, 1]
    ax.imshow(edges['canny'], cmap='gray_r', interpolation='nearest')
    ax.set_title('B) Canny Edge Detection', fontsize=12, fontweight='bold')
    ax.set_xlabel('Longitude (pixels)')
    ax.set_ylabel('Latitude (pixels)')

    # Panel C: Sobel E-W (NE-SW lineaments)
    ax = axes[1, 0]
    # Use raw float values with seismic colormap centered on zero
    sobel_ew = edges['sobel_ew']
    vmax = np.percentile(np.abs(sobel_ew), 98)  # Symmetric around zero
    ax.imshow(sobel_ew, cmap='seismic', vmin=-vmax, vmax=vmax, interpolation='nearest')
    ax.set_title('C) Sobel E-W Gradient (NE-SW Lineaments)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Longitude (pixels)')
    ax.set_ylabel('Latitude (pixels)')

    # Panel D: Stream network overlaid on hillshade
    ax = axes[1, 1]
    # Show hillshade as background
    ax.imshow(hillshade, cmap='gray', alpha=0.7, interpolation='nearest')
    # Overlay stream network in blue
    stream_mask = np.ma.masked_where(streams['streams'] == 0, streams['streams'])
    ax.imshow(stream_mask, cmap='Blues', interpolation='nearest', alpha=0.8)
    ax.set_title('D) Stream Network on Hillshade', fontsize=12, fontweight='bold')
    ax.set_xlabel('Longitude (pixels)')
    ax.set_ylabel('Latitude (pixels)')

    plt.tight_layout()

    output_path = OUTPUT_DIR / "fig1_white_wolf_overview.png"
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {output_path.name}")


def main():
    """Main analysis pipeline."""
    print("=" * 60)
    print("WHITE WOLF FAULT DEM LINEAMENT ANALYSIS")
    print("=" * 60)
    print()

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Step 1: Mosaic DEMs
    dem, meta, transform = mosaic_dems()

    # Step 2: Extract White Wolf region
    ww_dem, ww_meta, ww_transform = extract_white_wolf_region(dem, transform, meta)

    # Save subset DEM
    save_raster(ww_dem, OUTPUT_DIR / "white_wolf_dem_subset.tif", ww_meta)

    # Step 3: Hillshade
    hillshade = compute_hillshade(ww_dem)
    save_raster(hillshade, OUTPUT_DIR / "white_wolf_hillshade.tif", ww_meta)

    # Step 4: Edge detection
    edges = compute_edge_detection(ww_dem)
    save_raster(edges['sobel_mag'], OUTPUT_DIR / "white_wolf_sobel_mag.tif", ww_meta)
    save_raster(edges['canny'], OUTPUT_DIR / "white_wolf_canny.tif", ww_meta)
    save_raster(edges['sobel_ew_norm'], OUTPUT_DIR / "white_wolf_sobel_ew.tif", ww_meta)

    # Step 5: Drainage analysis
    streams = compute_drainage_analysis(ww_dem)
    save_raster(streams['flow_accum'], OUTPUT_DIR / "white_wolf_flow_accum.tif", ww_meta)
    save_raster(streams['streams'], OUTPUT_DIR / "white_wolf_streams.tif", ww_meta)

    # Step 6: Create figure
    create_overview_figure(hillshade, edges, streams, ww_meta, ww_transform)

    print()
    print("=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print("\nGenerated files:")
    for f in sorted(OUTPUT_DIR.glob("*")):
        print(f"  {f.name}")

    print("\nKey findings to check:")
    print("1. Does White Wolf fault scarp show in hillshade?")
    print("2. Are there parallel lineaments suggesting unmapped splays?")
    print("3. Do drainage patterns show fault-controlled deflections?")
    print("4. Any NE-SW lineaments between White Wolf and Crystal Cave?")


if __name__ == '__main__':
    main()
