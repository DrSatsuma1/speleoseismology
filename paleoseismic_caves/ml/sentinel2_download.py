#!/usr/bin/env python3
"""
Sentinel-2 Optical Imagery Downloader for Fault Analysis

Downloads multispectral imagery for:
- Fault trace identification via vegetation stress
- Scarp degradation analysis
- Landslide mapping
- Change detection

Data source: Copernicus Open Access Hub / Sentinel Hub
Resolution: 10m (RGB, NIR), 20m (SWIR), 60m (coastal, water vapor)

Usage:
    python sentinel2_download.py --region liguria --start 2023-01-01 --end 2023-12-31
    python sentinel2_download.py --bbox 7.5,43.8,8.5,44.5 --cloud-cover 20
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
import argparse

# Copernicus Data Space Ecosystem (successor to Scihub)
CDSE_CATALOG = "https://catalogue.dataspace.copernicus.eu/odata/v1"
CDSE_TOKEN = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"

# Sentinel Hub (commercial, easier API)
SENTINEL_HUB_CATALOG = "https://services.sentinel-hub.com/api/v1/catalog/search"

# Study regions
REGIONS = {
    "liguria": {
        "bbox": [7.5, 43.8, 8.5, 44.5],
        "description": "Ligurian Alps - T. Porra Fault, Bàsura Cave region",
        "targets": [
            "T. Porra Fault surface expression",
            "N-S lineaments in Toirano Valley",
            "Vegetation stress along fault traces"
        ]
    },
    "motagua": {
        "bbox": [-90.5, 14.5, -88.5, 16.0],
        "description": "Motagua Fault Zone - surface rupture traces",
        "targets": [
            "Motagua Fault scarp",
            "2012 M7.4 rupture zone",
            "Offset rivers and ridges"
        ]
    },
    "cascadia": {
        "bbox": [-124.5, 42.0, -123.0, 43.5],
        "description": "Oregon coastal zone - paleoseismic features",
        "targets": [
            "Coastal subsidence zones",
            "Ghost forests",
            "Tsunami deposits"
        ]
    },
    "san_andreas": {
        "bbox": [-123.5, 38.0, -122.0, 39.5],
        "description": "Northern San Andreas - tree ring study area",
        "targets": [
            "Fort Ross/Gualala redwood groves",
            "SAF surface trace",
            "1906 rupture zone"
        ]
    }
}


def search_cdse(bbox, start_date, end_date, max_cloud_cover=30, max_results=50):
    """
    Search Copernicus Data Space Ecosystem for Sentinel-2 products.

    CDSE replaced the old Scihub in January 2023.
    """
    # OData filter construction
    filter_str = (
        f"Collection/Name eq 'SENTINEL-2' and "
        f"OData.CSC.Intersects(area=geography'SRID=4326;POLYGON(("
        f"{bbox[0]} {bbox[1]},{bbox[2]} {bbox[1]},{bbox[2]} {bbox[3]},"
        f"{bbox[0]} {bbox[3]},{bbox[0]} {bbox[1]}))') and "
        f"ContentDate/Start gt {start_date}T00:00:00.000Z and "
        f"ContentDate/Start lt {end_date}T23:59:59.999Z and "
        f"Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and "
        f"att/OData.CSC.DoubleAttribute/Value lt {max_cloud_cover})"
    )

    url = f"{CDSE_CATALOG}/Products"
    params = {
        "$filter": filter_str,
        "$orderby": "ContentDate/Start desc",
        "$top": max_results
    }

    print(f"Searching Copernicus Data Space...")
    print(f"  Region: {bbox}")
    print(f"  Period: {start_date} to {end_date}")
    print(f"  Max cloud cover: {max_cloud_cover}%")

    try:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        results = response.json()
        products = results.get("value", [])
        print(f"  Found: {len(products)} products")
        return products
    except requests.exceptions.RequestException as e:
        print(f"  Search failed: {e}")
        print("\nManual search: https://dataspace.copernicus.eu/browser/")
        return []


def analyze_products(products):
    """Analyze search results for optimal acquisitions."""
    if not products:
        return

    print(f"\nProduct Summary:")
    print("-" * 70)

    # Group by tile
    tiles = {}
    for p in products:
        name = p.get("Name", "")
        # Extract tile ID (e.g., T32TLP)
        parts = name.split("_")
        if len(parts) >= 6:
            tile = parts[5]
            if tile not in tiles:
                tiles[tile] = []
            tiles[tile].append(p)

    for tile, tile_products in tiles.items():
        print(f"\nTile {tile}: {len(tile_products)} acquisitions")
        for p in tile_products[:3]:
            name = p.get("Name", "")
            date = p.get("ContentDate", {}).get("Start", "")[:10]
            cloud = None
            for attr in p.get("Attributes", []):
                if attr.get("Name") == "cloudCover":
                    cloud = attr.get("Value")
            cloud_str = f"{cloud:.1f}%" if cloud is not None else "N/A"
            print(f"  {date} - {cloud_str} cloud - {name[:50]}...")


def generate_download_instructions(products, output_dir, bbox):
    """Generate download instructions for CDSE."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "search_bbox": bbox,
        "product_count": len(products),
        "products": [
            {
                "name": p.get("Name"),
                "id": p.get("Id"),
                "date": p.get("ContentDate", {}).get("Start"),
                "size_mb": p.get("ContentLength", 0) / 1e6
            }
            for p in products
        ]
    }

    manifest_path = output_dir / "sentinel2_manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"\n" + "=" * 60)
    print("SENTINEL-2 DOWNLOAD INSTRUCTIONS")
    print("=" * 60)
    print(f"\nManifest saved: {manifest_path}")
    print(f"Products found: {len(products)}")

    print("""
DOWNLOAD OPTIONS:

1. Copernicus Browser (Visual, recommended for small areas):
   https://dataspace.copernicus.eu/browser/
   - Draw AOI, filter by date and cloud cover
   - Download individual tiles or processed outputs

2. CDSE API (Scripted, for bulk download):
   a) Register at https://dataspace.copernicus.eu/
   b) Get access token:
      curl -X POST https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token \\
           -d "grant_type=password&username=YOUR_USER&password=YOUR_PASS&client_id=cdse-public"
   c) Download products by ID:
      curl -H "Authorization: Bearer $TOKEN" \\
           "https://zipper.dataspace.copernicus.eu/odata/v1/Products(PRODUCT_ID)/\\$value" \\
           -o product.zip

3. Sentinel Hub (Commercial, best for processed data):
   https://www.sentinel-hub.com/
   - Free trial with 30,000 processing units
   - Direct access to NDVI, RGB composites, custom scripts
   - API for automated workflows

RECOMMENDED PRODUCTS FOR FAULT ANALYSIS:
- True Color (B04, B03, B02): General visualization
- NDVI (B08, B04): Vegetation stress along faults
- SWIR Composite (B12, B11, B04): Geological discrimination
- Bare Soil Index: Expose fault traces under vegetation
""")

    return manifest_path


def fault_analysis_workflow(region_name, output_dir):
    """Generate fault analysis workflow using Sentinel-2."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║           SENTINEL-2 FAULT ANALYSIS WORKFLOW                      ║
╚══════════════════════════════════════════════════════════════════╝

OBJECTIVE: Identify surface expressions of potential 1285 source faults

STEP 1: ACQUIRE IMAGERY
────────────────────────
- Target season: Late summer (Aug-Sep) for minimal vegetation
- Cloud cover: <10% over fault zone
- Multiple years to assess seasonal vs. permanent features

STEP 2: GENERATE INDICES
────────────────────────
┌────────────────────┬──────────────────────────────────────────────┐
│ Index              │ Purpose                                       │
├────────────────────┼──────────────────────────────────────────────┤
│ NDVI               │ Vegetation stress along fault traces         │
│ Clay Minerals      │ Fault gouge exposure                         │
│ Iron Oxide         │ Hydrothermal alteration                      │
│ NDWI               │ Spring alignment (fault-controlled drainage) │
│ Bare Soil Index    │ Direct fault trace visibility                │
└────────────────────┴──────────────────────────────────────────────┘

STEP 3: MULTI-TEMPORAL ANALYSIS
───────────────────────────────
- Stack 5+ years of dry-season imagery
- Compute pixel-wise standard deviation
- Low variance = stable bare rock/fault outcrop
- High variance = vegetation/seasonal features

STEP 4: LINEAMENT EXTRACTION
────────────────────────────
- Apply Canny edge detection to SWIR bands
- Hough transform for linear feature extraction
- Filter by:
  - Length (>500m for regional faults)
  - Orientation (compare with known fault sets)
  - Persistence across multiple dates

STEP 5: INTEGRATION WITH OTHER DATA
───────────────────────────────────
- Overlay on DEM hillshade (TINITALY 10m)
- Cross-reference with ITHACA fault database
- Compare with InSAR deformation (if available)
- Ground-truth with field mapping

EXPECTED OUTPUTS:
─────────────────
1. sentinel2_ndvi_timeseries.tif - Vegetation stress map
2. sentinel2_bare_soil.tif - Exposed fault traces
3. lineaments_extracted.geojson - Automatically detected lineaments
4. fault_candidates_optical.csv - Ranked fault candidates
""")


def main():
    parser = argparse.ArgumentParser(
        description="Download Sentinel-2 imagery for fault analysis"
    )
    parser.add_argument("--region", choices=list(REGIONS.keys()),
                        help="Predefined region")
    parser.add_argument("--bbox", type=str,
                        help="Custom bounding box: west,south,east,north")
    parser.add_argument("--start", type=str, default="2023-01-01",
                        help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, default="2023-12-31",
                        help="End date (YYYY-MM-DD)")
    parser.add_argument("--cloud-cover", type=int, default=20,
                        help="Maximum cloud cover percentage")
    parser.add_argument("--output", type=str, default="sentinel2_data",
                        help="Output directory")
    parser.add_argument("--workflow", action="store_true",
                        help="Show fault analysis workflow")

    args = parser.parse_args()

    if args.workflow:
        fault_analysis_workflow(None, None)
        return

    # Determine region
    if args.region:
        region_info = REGIONS[args.region]
        bbox = region_info["bbox"]
        print(f"\nRegion: {args.region}")
        print(f"Description: {region_info['description']}")
        print("Analysis targets:")
        for target in region_info.get("targets", []):
            print(f"  - {target}")
    elif args.bbox:
        bbox = [float(x) for x in args.bbox.split(",")]
    else:
        print("Specify --region or --bbox")
        print("\nAvailable regions:")
        for name, info in REGIONS.items():
            print(f"  {name}: {info['description']}")
        return

    # Search for products
    products = search_cdse(
        bbox=bbox,
        start_date=args.start,
        end_date=args.end,
        max_cloud_cover=args.cloud_cover
    )

    if products:
        analyze_products(products)

    # Generate download instructions
    output_dir = Path(args.output)
    if args.region:
        output_dir = output_dir / args.region

    generate_download_instructions(products, output_dir, bbox)

    # Show workflow
    fault_analysis_workflow(args.region, output_dir)


if __name__ == "__main__":
    main()
