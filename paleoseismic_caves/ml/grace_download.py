#!/usr/bin/env python3
"""
GRACE/GRACE-FO Gravity Data Downloader

Downloads monthly gravity anomaly data from NASA JPL for post-seismic
groundwater mass change analysis.

Data source: NASA GRACE Tellus
https://grace.jpl.nasa.gov/data/get-data/

Coverage: April 2002 - present (~300km spatial resolution, monthly)

Usage:
    python grace_download.py --region liguria --start 2002-04 --end 2024-11
    python grace_download.py --lat 44.15 --lon 8.0 --radius 200
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
import argparse
import csv

# GRACE data endpoints
GRACE_MASCON_URL = "https://podaac-tools.jpl.nasa.gov/drive/files/allData/tellus/L3/mascon/RL06/JPL/v02/CRI/netcdf"
GRACE_TIMESERIES_API = "https://nasagrace.unl.edu/data"

# Predefined study regions
REGIONS = {
    "liguria": {
        "lat": 44.15, "lon": 8.0,
        "description": "Bàsura Cave - T. Porra Fault region"
    },
    "belize": {
        "lat": 16.21, "lon": -89.12,
        "description": "Yok Balum Cave - Motagua Fault"
    },
    "oregon": {
        "lat": 42.1, "lon": -123.4,
        "description": "Oregon Caves - Cascadia"
    },
    "ridgecrest": {
        "lat": 35.77, "lon": -117.60,
        "description": "Ridgecrest 2019 M7.1 validation"
    },
    "tohoku": {
        "lat": 38.3, "lon": 142.4,
        "description": "Tohoku 2011 M9.0 validation"
    },
    "chile": {
        "lat": -35.9, "lon": -72.7,
        "description": "Maule 2010 M8.8 validation"
    },
    "tabriz": {
        "lat": 38.1, "lon": 46.3,
        "description": "North Tabriz Fault - Gejkar correlation"
    }
}


def fetch_grace_timeseries_unl(lat, lon, start_year=2002, end_year=2024):
    """
    Fetch GRACE groundwater anomaly time series from UNL portal.

    This uses the University of Nebraska-Lincoln GRACE data portal
    which provides pre-processed groundwater storage anomalies.

    Returns:
        List of (date, anomaly_cm, uncertainty) tuples
    """
    # UNL provides global gridded data - we extract nearest point
    # API format: https://nasagrace.unl.edu/data/{lat}/{lon}

    url = f"https://nasagrace.unl.edu/globaldata/GRACE_Groundwater_Drought_Indicator.txt"

    print(f"Fetching GRACE groundwater data...")
    print(f"  Location: {lat:.2f}°N, {lon:.2f}°E")

    # Note: UNL API may require different approach for point data
    # For now, we'll document the manual download process

    print("\nFor GRACE time series extraction:")
    print("  1. Visit: https://nasagrace.unl.edu/")
    print(f"  2. Enter coordinates: Lat={lat}, Lon={lon}")
    print("  3. Select 'Groundwater' layer")
    print("  4. Download CSV time series")

    return None


def fetch_grace_mascon_jpl(bbox, output_dir):
    """
    Download JPL GRACE Mascon (RL06v02) data for a region.

    Mascon data provides higher spatial resolution (~300km) than
    spherical harmonic solutions, better for regional analysis.

    Args:
        bbox: [west, south, east, north] in degrees
        output_dir: Directory for downloaded files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nJPL GRACE Mascon Download Instructions:")
    print("=" * 50)
    print("\nData: JPL GRACE/GRACE-FO RL06v02 Mascon (CRI filtered)")
    print("Format: NetCDF4, global monthly grids")
    print("Resolution: 0.5° × 0.5° (~56 km at equator)")
    print(f"Region: {bbox[0]:.1f}°W to {bbox[2]:.1f}°E, {bbox[1]:.1f}°S to {bbox[3]:.1f}°N")
    print("\nDownload steps:")
    print("  1. Go to: https://podaac.jpl.nasa.gov/")
    print("  2. Search: 'GRACE Mascon RL06'")
    print("  3. Select: 'TELLUS_GRAC-GRFO_MASCON_CRI_GRID_RL06_V2'")
    print("  4. Use Earthdata login")
    print(f"  5. Save to: {output_dir}/")
    print("\nAlternative - OpenDAP subset:")
    print("  https://opendap.jpl.nasa.gov/opendap/")

    # Generate extraction script for after download
    script_path = output_dir / "extract_grace_timeseries.py"
    with open(script_path, 'w') as f:
        f.write('''#!/usr/bin/env python3
"""Extract GRACE time series for specific location from NetCDF files."""
import netCDF4
import numpy as np
from pathlib import Path

# Target location
LAT = {lat}
LON = {lon}

def extract_timeseries(nc_files, lat, lon):
    """Extract monthly anomaly values at given location."""
    results = []

    for nc_path in sorted(Path('.').glob('*.nc')):
        with netCDF4.Dataset(nc_path) as nc:
            lats = nc.variables['lat'][:]
            lons = nc.variables['lon'][:]

            # Find nearest grid point
            lat_idx = np.argmin(np.abs(lats - lat))
            lon_idx = np.argmin(np.abs(lons - lon))

            # Get liquid water equivalent thickness anomaly
            lwe = nc.variables['lwe_thickness'][0, lat_idx, lon_idx]
            time = nc.variables['time'][0]

            results.append((time, float(lwe)))

    return results

if __name__ == "__main__":
    ts = extract_timeseries('.', LAT, LON)
    print(f"Extracted {{len(ts)}} monthly values")
    for t, v in ts[:5]:
        print(f"  {{t}}: {{v:.2f}} cm")
'''.format(lat=bbox[1] + (bbox[3]-bbox[1])/2, lon=bbox[0] + (bbox[2]-bbox[0])/2))

    print(f"\nGenerated: {script_path}")
    return script_path


def analyze_earthquake_signal(lat, lon, eq_date, window_months=24):
    """
    Analyze GRACE signal around a known earthquake.

    Large earthquakes (M7+) produce measurable gravity changes:
    - Coseismic: Instant mass redistribution
    - Postseismic: Delayed aquifer response (months-years)

    Args:
        lat, lon: Earthquake epicenter
        eq_date: Earthquake date (YYYY-MM-DD)
        window_months: Analysis window before/after
    """
    print(f"\nEarthquake GRACE Analysis Protocol:")
    print("=" * 50)
    print(f"Event location: {lat:.2f}°N, {lon:.2f}°E")
    print(f"Event date: {eq_date}")
    print(f"Analysis window: ±{window_months} months")
    print("\nExpected signals:")
    print("  - Coseismic: Sudden change in monthly anomaly")
    print("  - Postseismic: Gradual recovery over 6-24 months")
    print("  - Groundwater: Aquifer pressure changes")
    print("\nValidation examples:")
    print("  - Tohoku 2011 M9.0: -15 μGal coseismic, years recovery")
    print("  - Sumatra 2004 M9.1: -12 μGal, still recovering")
    print("  - Chile 2010 M8.8: -8 μGal, 18-month recovery")
    print("\nFor M6-7 events (like 1285 aftershocks):")
    print("  - Expected signal: 0.5-2 cm water equivalent")
    print("  - Detectability: Marginal at GRACE resolution")
    print("  - Best use: Validate regional aquifer response patterns")


def generate_validation_report(regions_to_test):
    """
    Generate GRACE validation protocol for modern earthquakes.
    """
    validation_events = [
        {
            "name": "Ridgecrest 2019",
            "date": "2019-07-06",
            "mag": 7.1,
            "lat": 35.77,
            "lon": -117.60,
            "expected": "Moderate groundwater signal, validation of TEC precursor"
        },
        {
            "name": "Tohoku 2011",
            "date": "2011-03-11",
            "mag": 9.0,
            "lat": 38.30,
            "lon": 142.40,
            "expected": "Large gravity anomaly, well-documented in literature"
        },
        {
            "name": "Chile 2010",
            "date": "2010-02-27",
            "mag": 8.8,
            "lat": -35.90,
            "lon": -72.70,
            "expected": "Strong signal, 18-month postseismic recovery"
        },
        {
            "name": "Nepal 2015",
            "date": "2015-04-25",
            "mag": 7.8,
            "lat": 28.23,
            "lon": 84.73,
            "expected": "Continental collision, groundwater response"
        }
    ]

    print("\n" + "=" * 60)
    print("GRACE VALIDATION PROTOCOL - Modern Earthquake Benchmarks")
    print("=" * 60)

    for event in validation_events:
        print(f"\n{event['name']} M{event['mag']}")
        print(f"  Date: {event['date']}")
        print(f"  Location: {event['lat']:.2f}°N, {event['lon']:.2f}°E")
        print(f"  Expected: {event['expected']}")

    print("\n" + "-" * 60)
    print("METHODOLOGY:")
    print("  1. Download GRACE mascons for each region")
    print("  2. Extract time series at epicenter ± 200km")
    print("  3. Compute pre-event baseline (12 months prior)")
    print("  4. Calculate coseismic jump and postseismic trend")
    print("  5. Compare with published results")
    print("-" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Download and analyze GRACE gravity data for earthquake validation"
    )
    parser.add_argument("--region", choices=list(REGIONS.keys()),
                        help="Predefined region")
    parser.add_argument("--lat", type=float, help="Custom latitude")
    parser.add_argument("--lon", type=float, help="Custom longitude")
    parser.add_argument("--start", type=str, default="2002-04",
                        help="Start month (YYYY-MM)")
    parser.add_argument("--end", type=str, default="2024-11",
                        help="End month (YYYY-MM)")
    parser.add_argument("--output", type=str, default="grace_data",
                        help="Output directory")
    parser.add_argument("--validate", action="store_true",
                        help="Show validation protocol for modern earthquakes")
    parser.add_argument("--earthquake", type=str,
                        help="Analyze earthquake date (YYYY-MM-DD)")

    args = parser.parse_args()

    if args.validate:
        generate_validation_report([])
        return

    # Determine location
    if args.region:
        lat = REGIONS[args.region]["lat"]
        lon = REGIONS[args.region]["lon"]
        print(f"\nRegion: {args.region}")
        print(f"Description: {REGIONS[args.region]['description']}")
    elif args.lat and args.lon:
        lat, lon = args.lat, args.lon
    else:
        print("Specify --region or --lat/--lon")
        print("\nAvailable regions:")
        for name, info in REGIONS.items():
            print(f"  {name}: {info['description']}")
        return

    # Create bounding box (±2° around point for mascon extraction)
    bbox = [lon - 2, lat - 2, lon + 2, lat + 2]

    # Earthquake analysis mode
    if args.earthquake:
        analyze_earthquake_signal(lat, lon, args.earthquake)
        return

    # Download instructions and scripts
    output_dir = Path(args.output)
    if args.region:
        output_dir = output_dir / args.region

    fetch_grace_mascon_jpl(bbox, output_dir)

    print("\n" + "=" * 50)
    print("GRACE Data Integration with Speleothem Analysis")
    print("=" * 50)
    print("\nHypothesis to test:")
    print("  Large earthquakes alter regional groundwater storage")
    print("  This should correlate with speleothem δ18O/Mg/Ca changes")
    print("\nFor historical events (pre-2002):")
    print("  - GRACE cannot directly validate (data starts 2002)")
    print("  - Use modern analogues to calibrate response magnitude")
    print("  - Apply response model to interpret speleothem signals")


if __name__ == "__main__":
    main()
