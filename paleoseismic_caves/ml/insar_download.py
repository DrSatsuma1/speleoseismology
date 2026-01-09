#!/usr/bin/env python3
"""
InSAR Data Downloader for Paleoseismic Analysis

Downloads Sentinel-1 InSAR products from ASF DAAC for fault deformation analysis.
Focus: Liguria region (T. Porra Fault, potential 1285 source)

Requires: ASF Earthdata account (free registration at https://urs.earthdata.nasa.gov/)

Usage:
    python insar_download.py --region liguria --start 2014-10-01 --end 2024-12-01
    python insar_download.py --bbox 7.5,43.8,8.5,44.5 --product SLC
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
import argparse

# ASF DAAC API endpoint
ASF_SEARCH_URL = "https://api.daac.asf.alaska.edu/services/search/param"

# Predefined regions of interest
REGIONS = {
    "liguria": {
        "bbox": [7.5, 43.8, 8.5, 44.5],  # W, S, E, N
        "center": [8.0, 44.15],
        "description": "Ligurian Alps - Bàsura Cave, T. Porra Fault"
    },
    "motagua": {
        "bbox": [-90.5, 14.5, -88.5, 16.0],
        "center": [-89.5, 15.25],
        "description": "Motagua Fault Zone - Yok Balum Cave"
    },
    "cascadia": {
        "bbox": [-124.5, 42.0, -123.0, 43.5],
        "center": [-123.75, 42.75],
        "description": "Oregon Caves - Cascadia Subduction Zone"
    },
    "tabriz": {
        "bbox": [45.0, 35.5, 46.5, 38.5],
        "center": [45.75, 37.0],
        "description": "North Tabriz Fault - Gejkar Cave correlation"
    }
}

# Sentinel-1 product types
PRODUCT_TYPES = {
    "SLC": "Single Look Complex - full phase information for InSAR",
    "GRD": "Ground Range Detected - amplitude only, easier to process",
    "OCN": "Ocean products",
    "RAW": "Raw data"
}


def search_asf(bbox, start_date, end_date, product_type="SLC", platform="S1",
               max_results=250):
    """
    Search ASF DAAC for Sentinel-1 products.

    Args:
        bbox: [west, south, east, north] in degrees
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        product_type: SLC, GRD, OCN, or RAW
        platform: S1 (Sentinel-1), S1A, S1B
        max_results: Maximum number of results

    Returns:
        List of product metadata dictionaries
    """
    params = {
        "bbox": f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}",
        "start": start_date,
        "end": end_date,
        "platform": platform,
        "processingLevel": product_type,
        "output": "json",
        "maxResults": max_results
    }

    print(f"Searching ASF DAAC...")
    print(f"  Region: {bbox}")
    print(f"  Period: {start_date} to {end_date}")
    print(f"  Product: {product_type}")

    try:
        response = requests.get(ASF_SEARCH_URL, params=params, timeout=60)
        response.raise_for_status()
        results = response.json()

        if isinstance(results, list):
            products = results
        else:
            products = results.get("results", [])

        print(f"  Found: {len(products)} products")
        return products

    except requests.exceptions.RequestException as e:
        print(f"  Error: {e}")
        return []


def analyze_coverage(products):
    """Analyze temporal and spatial coverage of search results."""
    if not products:
        return None

    dates = []
    orbits = {"ASCENDING": 0, "DESCENDING": 0}

    for p in products:
        # Handle different response formats
        if isinstance(p, dict):
            date_str = p.get("startTime", p.get("acquisitionDate", ""))
            orbit = p.get("flightDirection", p.get("orbitDirection", "UNKNOWN"))
        else:
            continue

        if date_str:
            try:
                # Parse various date formats
                for fmt in ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"]:
                    try:
                        dates.append(datetime.strptime(date_str[:26], fmt))
                        break
                    except ValueError:
                        continue
            except:
                pass

        if orbit in orbits:
            orbits[orbit] += 1

    if not dates:
        return None

    dates.sort()

    # Calculate revisit statistics
    intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]

    return {
        "total_products": len(products),
        "date_range": (dates[0].strftime("%Y-%m-%d"), dates[-1].strftime("%Y-%m-%d")),
        "ascending": orbits["ASCENDING"],
        "descending": orbits["DESCENDING"],
        "mean_revisit_days": sum(intervals) / len(intervals) if intervals else 0,
        "min_revisit_days": min(intervals) if intervals else 0,
        "max_revisit_days": max(intervals) if intervals else 0
    }


def generate_download_script(products, output_dir, credentials_file=None):
    """
    Generate wget/curl download script for ASF products.

    Note: Actual download requires Earthdata authentication.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    script_path = output_dir / "download_insar.sh"
    manifest_path = output_dir / "insar_manifest.json"

    # Save manifest
    with open(manifest_path, 'w') as f:
        json.dump(products, f, indent=2, default=str)

    # Generate download script
    with open(script_path, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# InSAR Download Script - Generated by insar_download.py\n")
        f.write("# Requires: .netrc file with Earthdata credentials\n")
        f.write("# See: https://urs.earthdata.nasa.gov/\n\n")
        f.write(f"cd {output_dir}\n\n")

        for p in products[:50]:  # Limit to first 50 for script
            # Handle nested list structure from API
            if isinstance(p, list):
                p = p[0] if p else {}
            if not isinstance(p, dict):
                continue
            url = p.get("downloadUrl", p.get("url", ""))
            filename = p.get("fileName", p.get("granuleName", "unknown"))
            if url:
                f.write(f'echo "Downloading {filename}..."\n')
                f.write(f'wget --auth-no-challenge --content-disposition -c "{url}"\n\n')

    os.chmod(script_path, 0o755)

    print(f"\nGenerated:")
    print(f"  Manifest: {manifest_path}")
    print(f"  Download script: {script_path}")
    print(f"\nTo download, set up Earthdata credentials:")
    print("  1. Register at https://urs.earthdata.nasa.gov/")
    print("  2. Create ~/.netrc with:")
    print("     machine urs.earthdata.nasa.gov login YOUR_USER password YOUR_PASS")
    print(f"  3. Run: bash {script_path}")

    return script_path, manifest_path


def get_interferogram_pairs(products, max_temporal_baseline=48, max_pairs=20):
    """
    Identify optimal InSAR pairs for interferogram generation.

    Args:
        products: List of SLC products
        max_temporal_baseline: Maximum days between acquisitions
        max_pairs: Maximum number of pairs to return

    Returns:
        List of (primary, secondary) product pairs
    """
    # Sort by date
    dated_products = []
    for p in products:
        # Handle nested list structure from API
        if isinstance(p, list) and len(p) > 0:
            p = p[0] if isinstance(p[0], dict) else {}
        if not isinstance(p, dict):
            continue
        date_str = p.get("startTime", p.get("acquisitionDate", ""))
        orbit = p.get("flightDirection", "")
        if date_str and orbit:
            try:
                for fmt in ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"]:
                    try:
                        date = datetime.strptime(date_str[:26], fmt)
                        dated_products.append((date, orbit, p))
                        break
                    except ValueError:
                        continue
            except:
                pass

    dated_products.sort(key=lambda x: x[0])

    # Find pairs with same orbit direction and reasonable temporal baseline
    pairs = []
    for i, (date1, orbit1, p1) in enumerate(dated_products):
        for date2, orbit2, p2 in dated_products[i+1:]:
            if orbit1 != orbit2:
                continue
            baseline = (date2 - date1).days
            if baseline <= max_temporal_baseline:
                pairs.append({
                    "primary": p1.get("granuleName", p1.get("fileName", "")),
                    "secondary": p2.get("granuleName", p2.get("fileName", "")),
                    "primary_date": date1.strftime("%Y-%m-%d"),
                    "secondary_date": date2.strftime("%Y-%m-%d"),
                    "temporal_baseline_days": baseline,
                    "orbit_direction": orbit1
                })
                if len(pairs) >= max_pairs:
                    break
        if len(pairs) >= max_pairs:
            break

    return pairs


def main():
    parser = argparse.ArgumentParser(
        description="Search and download Sentinel-1 InSAR data from ASF DAAC"
    )
    parser.add_argument("--region", choices=list(REGIONS.keys()),
                        help="Predefined region of interest")
    parser.add_argument("--bbox", type=str,
                        help="Custom bounding box: west,south,east,north")
    parser.add_argument("--start", type=str, default="2020-01-01",
                        help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, default="2024-12-01",
                        help="End date (YYYY-MM-DD)")
    parser.add_argument("--product", type=str, default="SLC",
                        choices=list(PRODUCT_TYPES.keys()),
                        help="Product type")
    parser.add_argument("--output", type=str, default="insar_data",
                        help="Output directory")
    parser.add_argument("--pairs", action="store_true",
                        help="Identify interferogram pairs")

    args = parser.parse_args()

    # Determine bounding box
    if args.region:
        bbox = REGIONS[args.region]["bbox"]
        print(f"\nRegion: {args.region}")
        print(f"Description: {REGIONS[args.region]['description']}")
    elif args.bbox:
        bbox = [float(x) for x in args.bbox.split(",")]
    else:
        print("Error: Specify --region or --bbox")
        return

    # Search ASF
    products = search_asf(
        bbox=bbox,
        start_date=args.start,
        end_date=args.end,
        product_type=args.product
    )

    if not products:
        print("\nNo products found. Try adjusting search parameters.")
        return

    # Analyze coverage
    coverage = analyze_coverage(products)
    if coverage:
        print(f"\nCoverage Analysis:")
        print(f"  Total products: {coverage['total_products']}")
        print(f"  Date range: {coverage['date_range'][0]} to {coverage['date_range'][1]}")
        print(f"  Ascending orbits: {coverage['ascending']}")
        print(f"  Descending orbits: {coverage['descending']}")
        print(f"  Mean revisit: {coverage['mean_revisit_days']:.1f} days")

    # Identify interferogram pairs
    if args.pairs and args.product == "SLC":
        pairs = get_interferogram_pairs(products)
        print(f"\nOptimal Interferogram Pairs ({len(pairs)} found):")
        for pair in pairs[:10]:
            print(f"  {pair['primary_date']} → {pair['secondary_date']} "
                  f"({pair['temporal_baseline_days']}d, {pair['orbit_direction']})")

    # Generate download script
    output_dir = Path(args.output)
    if args.region:
        output_dir = output_dir / args.region
    generate_download_script(products, output_dir)


if __name__ == "__main__":
    main()
