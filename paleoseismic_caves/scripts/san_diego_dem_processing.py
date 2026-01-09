#!/usr/bin/env python3
"""
San Diego Rose Canyon Fault DEM Processing
Mosaic USGS 3DEP tiles and crop to Rose Canyon extent

Input: 2 USGS tiles (different resolutions)
- n34w118 (33-34°N): 1/3 arc-second (~10m)
- n33w118 (32-33°N): 13 arc-second (~400m)

Output:
- rose_canyon_dem_20x70km.tif (mosaicked, cropped, UTM 11N)
- rose_canyon_hillshade.tif

Author: Claude Code
Date: 2026-01-02
"""

import os
from pathlib import Path
import rasterio
from rasterio.merge import merge
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.mask import mask
from shapely.geometry import box
import numpy as np

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
QUAKE_ROOT = os.path.dirname(PROJECT_ROOT)
DEM_DIR = os.path.join(QUAKE_ROOT, "dem_tiles", "san_diego")

# Input files
TILE_HIGH_RES = os.path.join(DEM_DIR, "USGS_13_n34w118_20250826.tif")  # 10m, northern
TILE_LOW_RES = os.path.join(DEM_DIR, "USGS_13_n33w118_20180313.tif")   # 400m, southern

# Output files
MOSAIC_WGS84 = os.path.join(DEM_DIR, "rose_canyon_mosaic_wgs84.tif")
MOSAIC_UTM = os.path.join(DEM_DIR, "rose_canyon_mosaic_utm11n.tif")
CROPPED_DEM = os.path.join(DEM_DIR, "rose_canyon_dem_20x70km.tif")
HILLSHADE = os.path.join(DEM_DIR, "rose_canyon_hillshade.tif")

# Rose Canyon Fault extent (from plan)
RCF_BOUNDS = {
    'west': -117.3,
    'east': -117.1,
    'south': 32.6,
    'north': 33.2
}

# UTM Zone 11N (EPSG:26911) - for California
TARGET_CRS = "EPSG:26911"
TARGET_RESOLUTION = 10  # meters (match high-res tile)


def resample_to_target_resolution(input_file, output_file, target_res_arcsec=1/3):
    """
    Resample low-res tile to match high-res tile resolution.

    Target: 1/3 arc-second ≈ 10m at this latitude
    """
    print(f"\nResampling {os.path.basename(input_file)} to {target_res_arcsec} arc-second...")

    with rasterio.open(input_file) as src:
        # Calculate new transform with target resolution
        # 1/3 arc-second = 1/10800 degrees
        new_res = target_res_arcsec / 3600  # Convert arc-seconds to degrees

        # Get current bounds
        bounds = src.bounds

        # Calculate new dimensions
        new_width = int((bounds.right - bounds.left) / new_res)
        new_height = int((bounds.top - bounds.bottom) / new_res)

        # Create new transform
        from rasterio.transform import from_bounds
        new_transform = from_bounds(
            bounds.left, bounds.bottom, bounds.right, bounds.top,
            new_width, new_height
        )

        # Prepare output array
        data = src.read(1)
        resampled = np.empty((new_height, new_width), dtype=data.dtype)

        # Resample
        reproject(
            source=data,
            destination=resampled,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=new_transform,
            dst_crs=src.crs,
            resampling=Resampling.bilinear
        )

        # Write output
        profile = src.profile.copy()
        profile.update({
            'height': new_height,
            'width': new_width,
            'transform': new_transform
        })

        with rasterio.open(output_file, 'w', **profile) as dst:
            dst.write(resampled, 1)

    print(f"  Resampled: {new_width} x {new_height} pixels")
    return output_file


def mosaic_tiles(tile_files, output_file):
    """Mosaic multiple DEM tiles into single raster."""
    print(f"\nMosaicking {len(tile_files)} tiles...")

    # Open all tiles
    src_files = [rasterio.open(f) for f in tile_files]

    # Merge
    mosaic, out_transform = merge(src_files)

    # Get metadata from first tile
    out_meta = src_files[0].meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_transform,
        "compress": "lzw"
    })

    # Write mosaic
    with rasterio.open(output_file, "w", **out_meta) as dest:
        dest.write(mosaic)

    # Close source files
    for src in src_files:
        src.close()

    print(f"  Mosaic size: {mosaic.shape[2]} x {mosaic.shape[1]} pixels")
    print(f"  Saved: {output_file}")
    return output_file


def reproject_to_utm(input_file, output_file, target_crs=TARGET_CRS, resolution=TARGET_RESOLUTION):
    """Reproject from WGS84 to UTM Zone 11N."""
    print(f"\nReprojecting to {target_crs} at {resolution}m resolution...")

    with rasterio.open(input_file) as src:
        # Calculate transform for target CRS
        transform, width, height = calculate_default_transform(
            src.crs, target_crs, src.width, src.height, *src.bounds,
            resolution=resolution
        )

        # Prepare output
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': target_crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        with rasterio.open(output_file, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=target_crs,
                    resampling=Resampling.bilinear
                )

    print(f"  Reprojected size: {width} x {height} pixels")
    print(f"  Saved: {output_file}")
    return output_file


def crop_to_extent(input_file, output_file, bounds):
    """Crop raster to Rose Canyon extent."""
    print(f"\nCropping to Rose Canyon extent...")
    print(f"  Bounds: {bounds}")

    with rasterio.open(input_file) as src:
        # Create bounding box geometry
        bbox = box(bounds['west'], bounds['south'], bounds['east'], bounds['north'])

        # Crop
        out_image, out_transform = mask(src, [bbox], crop=True)
        out_meta = src.meta.copy()

        out_meta.update({
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform
        })

        with rasterio.open(output_file, "w", **out_meta) as dest:
            dest.write(out_image)

    print(f"  Cropped size: {out_image.shape[2]} x {out_image.shape[1]} pixels")
    print(f"  Saved: {output_file}")
    return output_file


def create_hillshade(dem_file, output_file, azimuth=315, altitude=45):
    """Create hillshade from DEM for visualization."""
    print(f"\nCreating hillshade (azimuth={azimuth}°, altitude={altitude}°)...")

    with rasterio.open(dem_file) as src:
        dem = src.read(1)

        # Get pixel size in meters (for UTM)
        pixel_size = src.transform.a  # assumes square pixels

        # Calculate slope and aspect
        from scipy.ndimage import sobel

        # Gradients
        dx = sobel(dem, axis=1) / (8 * pixel_size)
        dy = sobel(dem, axis=0) / (8 * pixel_size)

        # Slope and aspect
        slope = np.arctan(np.sqrt(dx**2 + dy**2))
        aspect = np.arctan2(-dy, dx)

        # Convert azimuth and altitude to radians
        azimuth_rad = np.radians(azimuth)
        altitude_rad = np.radians(altitude)

        # Calculate hillshade
        hillshade = np.sin(altitude_rad) * np.sin(slope) + \
                    np.cos(altitude_rad) * np.cos(slope) * \
                    np.cos(azimuth_rad - aspect)

        # Normalize to 0-255
        hillshade = ((hillshade + 1) * 127.5).astype(np.uint8)

        # Write output
        profile = src.profile.copy()
        profile.update(dtype=rasterio.uint8, count=1, nodata=None)

        with rasterio.open(output_file, 'w', **profile) as dst:
            dst.write(hillshade, 1)

    print(f"  Saved: {output_file}")
    return output_file


def main():
    """Main processing pipeline."""
    print("="*70)
    print("SAN DIEGO ROSE CANYON FAULT DEM PROCESSING")
    print("="*70)

    # Check input files
    print("\nInput files:")
    print(f"  High-res (10m): {os.path.basename(TILE_HIGH_RES)}")
    print(f"  Low-res (400m): {os.path.basename(TILE_LOW_RES)}")

    if not os.path.exists(TILE_HIGH_RES) or not os.path.exists(TILE_LOW_RES):
        print("\n❌ ERROR: Input tiles not found!")
        return

    # Step 1: Resample low-res tile to match high-res
    print("\n" + "="*70)
    print("STEP 1: RESAMPLE LOW-RES TILE")
    print("="*70)
    resampled_low = os.path.join(DEM_DIR, "n33w118_resampled.tif")
    resample_to_target_resolution(TILE_LOW_RES, resampled_low, target_res_arcsec=1/3)

    # Step 2: Mosaic tiles
    print("\n" + "="*70)
    print("STEP 2: MOSAIC TILES")
    print("="*70)
    mosaic_tiles([TILE_HIGH_RES, resampled_low], MOSAIC_WGS84)

    # Step 3: Crop to Rose Canyon extent (before reprojection for accuracy)
    print("\n" + "="*70)
    print("STEP 3: CROP TO ROSE CANYON EXTENT")
    print("="*70)
    cropped_wgs84 = os.path.join(DEM_DIR, "rose_canyon_wgs84.tif")
    crop_to_extent(MOSAIC_WGS84, cropped_wgs84, RCF_BOUNDS)

    # Step 4: Reproject to UTM 11N
    print("\n" + "="*70)
    print("STEP 4: REPROJECT TO UTM 11N")
    print("="*70)
    reproject_to_utm(cropped_wgs84, CROPPED_DEM, TARGET_CRS, TARGET_RESOLUTION)

    # Step 5: Create hillshade
    print("\n" + "="*70)
    print("STEP 5: CREATE HILLSHADE")
    print("="*70)
    create_hillshade(CROPPED_DEM, HILLSHADE)

    # Summary
    print("\n" + "="*70)
    print("PROCESSING COMPLETE")
    print("="*70)
    print("\nOutput files:")
    print(f"  DEM (UTM 11N, 10m): {os.path.basename(CROPPED_DEM)}")
    print(f"  Hillshade: {os.path.basename(HILLSHADE)}")
    print(f"\nLocation: {DEM_DIR}/")
    print("\nNext steps:")
    print("  1. Run san_diego_lineament_analysis.py for edge detection")
    print("  2. Download microseismicity data")
    print("  3. Overlay faults and earthquakes")


if __name__ == '__main__':
    main()
