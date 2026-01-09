#!/usr/bin/env python3.11
"""
Quick regional lineament analysis script
Runs edge detection and drainage analysis on 35km × 35km regional DEM
"""

import sys
sys.path.append('/Users/catherine/projects/quake/paleoseismic_caves/scripts')

# Import the main analysis functions from the original script
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from scipy.ndimage import sobel, gaussian_filter
from skimage import feature
from skimage.morphology import skeletonize

print("REGIONAL LINEAMENT ANALYSIS (35km × 35km)")
print("=" * 80)

# Load regional DEM
DEM_FILE = '/Users/catherine/projects/quake/dem_tiles/regional_lineament_dem.tif'
print(f"\nLoading DEM: {DEM_FILE}")

with rasterio.open(DEM_FILE) as src:
    dem = src.read(1)
    dem_meta = src.meta.copy()
    transform = src.transform
    crs = src.crs

print(f"  Shape: {dem.shape}")
print(f"  CRS: {crs}")
print(f"  Resolution: {transform.a:.1f}m")

# Load earthquake data
print("\nLoading earthquake data...")
earthquakes = []
with open('/Users/catherine/projects/quake/paleoseismic_caves/data/ingv_liguria_raw.txt', 'r') as f:
    for line in f:
        if line.strip() and not line.startswith('#'):
            parts = line.strip().split('|')
            if len(parts) >= 11:
                try:
                    lat = float(parts[2])
                    lon = float(parts[3])
                    depth = float(parts[4])
                    mag = float(parts[10]) if parts[10] != '--' else 0.0
                    earthquakes.append({'lat': lat, 'lon': lon, 'depth': depth, 'mag': mag})
                except ValueError:
                    continue

print(f"  Loaded {len(earthquakes)} earthquakes")

# Compute Canny edges
print("\nComputing Canny edge detection...")
dem_smooth = gaussian_filter(dem.astype(float), sigma=2.0)
edges = feature.canny(dem_smooth, sigma=1.0, low_threshold=0.08, high_threshold=0.25)
print(f"  Edge pixels: {np.sum(edges)}")

# Compute flow accumulation (simplified)
print("\nComputing drainage analysis...")
sx = sobel(dem.astype(float), axis=0)
sy = sobel(dem.astype(float), axis=1)
gradient_mag = np.hypot(sx, sy)
gradient_inv = gradient_mag.max() - gradient_mag
flow_accum = gaussian_filter(gradient_inv, sigma=10)

# Create integrated visualization
print("\nCreating visualization...")
fig, axes = plt.subplots(2, 2, figsize=(16, 16), dpi=150)

# Panel 1: Canny edges
ax = axes[0, 0]
ax.imshow(edges, cmap='gray', interpolation='nearest')
ax.set_title('Canny Edge Detection (σ=2.0)', fontsize=14, fontweight='bold')
ax.set_xlabel('Pixel X (10m resolution)')
ax.set_ylabel('Pixel Y (10m resolution)')
ax.grid(True, alpha=0.2)

# Panel 2: Flow accumulation
ax = axes[0, 1]
im = ax.imshow(np.log10(flow_accum + 1), cmap='Blues', interpolation='bilinear', alpha=0.8)
ax.set_title('Flow Accumulation (log scale)', fontsize=14, fontweight='bold')
ax.set_xlabel('Pixel X (10m resolution)')
ax.set_ylabel('Pixel Y (10m resolution)')
plt.colorbar(im, ax=ax, label='Log10(Flow)')
ax.grid(True, alpha=0.2)

# Panel 3: Integrated - Edges + Earthquakes
ax = axes[1, 0]
# Background: hillshade
hillshade = dem.copy()
hillshade = (hillshade - hillshade.min()) / (hillshade.max() - hillshade.min())
ax.imshow(hillshade, cmap='gray', alpha=0.3)

# Overlay edges
edge_overlay = np.ma.masked_where(~edges, edges)
ax.imshow(edge_overlay, cmap='Reds', alpha=0.6, interpolation='nearest')

# Plot earthquakes
from pyproj import Transformer
transformer = Transformer.from_crs("EPSG:4326", "EPSG:32632", always_xy=True)

eq_pixels_x = []
eq_pixels_y = []
for eq in earthquakes:
    utm_x, utm_y = transformer.transform(eq['lon'], eq['lat'])
    pixel_x = (utm_x - transform.c) / transform.a
    pixel_y = (utm_y - transform.f) / transform.e

    if 0 <= pixel_x < dem.shape[1] and 0 <= pixel_y < dem.shape[0]:
        eq_pixels_x.append(pixel_x)
        eq_pixels_y.append(pixel_y)

ax.scatter(eq_pixels_x, eq_pixels_y, c='yellow', s=30, alpha=0.8,
           edgecolors='red', linewidths=1, marker='o', zorder=10,
           label=f'Earthquakes (n={len(eq_pixels_x)})')

# Mark Bàsura Cave
basura_lat, basura_lon = 44.1167, 8.2000
basura_utm_x, basura_utm_y = transformer.transform(basura_lon, basura_lat)
basura_pixel_x = (basura_utm_x - transform.c) / transform.a
basura_pixel_y = (basura_utm_y - transform.f) / transform.e
ax.scatter([basura_pixel_x], [basura_pixel_y], c='cyan', s=500, marker='*',
           edgecolors='black', linewidths=3, label='Bàsura Cave', zorder=15)

ax.set_title('Edges + Seismicity', fontsize=14, fontweight='bold')
ax.set_xlabel('Pixel X (10m resolution)')
ax.set_ylabel('Pixel Y (10m resolution)')
ax.legend(loc='upper right', fontsize=10)
ax.grid(True, alpha=0.2)

# Panel 4: Full integrated (edges + flow + earthquakes)
ax = axes[1, 1]
ax.imshow(hillshade, cmap='gray', alpha=0.3)
ax.imshow(np.log10(flow_accum + 1), cmap='Blues', alpha=0.4, interpolation='bilinear')
ax.imshow(edge_overlay, cmap='Reds', alpha=0.4, interpolation='nearest')

ax.scatter(eq_pixels_x, eq_pixels_y, c='yellow', s=30, alpha=0.9,
           edgecolors='red', linewidths=1, marker='o', zorder=10,
           label=f'Earthquakes (n={len(eq_pixels_x)})')
ax.scatter([basura_pixel_x], [basura_pixel_y], c='cyan', s=500, marker='*',
           edgecolors='black', linewidths=3, label='Bàsura Cave', zorder=15)

ax.set_title('Integrated Analysis (35km × 35km)', fontsize=14, fontweight='bold')
ax.set_xlabel('Pixel X (10m resolution)')
ax.set_ylabel('Pixel Y (10m resolution)')
ax.legend(loc='upper right', fontsize=10)
ax.grid(True, alpha=0.2)

# Add scale bar annotation
ax.text(0.05, 0.95, '35km × 35km\n10m resolution\n3500 × 3500 pixels',
        transform=ax.transAxes, fontsize=10, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()
output_path = '/Users/catherine/projects/quake/dem_tiles/publication_figures/fig6_regional_lineament_35km.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight')
print(f"✓ Saved: {output_path}")

plt.close()

print(f"\n✓ Regional analysis complete")
print(f"  Edge pixels: {np.sum(edges):,}")
print(f"  Earthquakes in view: {len(eq_pixels_x)}")
print(f"  DEM size: 35km × 35km (3500 × 3500 pixels)")
