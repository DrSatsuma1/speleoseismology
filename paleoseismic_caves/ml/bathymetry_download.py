#!/usr/bin/env python3
"""
Bathymetric Data Downloader for Offshore Fault Analysis

Downloads seafloor topography data to identify potential offshore
earthquake sources in the Ligurian Sea.

Data sources:
- GEBCO (General Bathymetric Chart of the Oceans) - Global 15 arc-second
- EMODnet (European Marine Observation and Data Network) - Higher res for Europe
- NOAA NCEI - US waters

Focus: Ligurian Sea offshore faults as potential 1285 earthquake sources

Usage:
    python bathymetry_download.py --region ligurian_sea
    python bathymetry_download.py --bbox 7.5,43.0,10.0,44.5 --source gebco
"""

import os
import json
import requests
from pathlib import Path
import argparse

# Data source URLs
GEBCO_WCS = "https://www.gebco.net/data_and_products/gebco_web_services/web_map_service/mapserv"
EMODNET_WCS = "https://ows.emodnet-bathymetry.eu/wcs"
EMODNET_WMS = "https://ows.emodnet-bathymetry.eu/wms"

# Predefined offshore regions
REGIONS = {
    "ligurian_sea": {
        "bbox": [7.5, 43.0, 10.0, 44.5],
        "description": "Ligurian Sea - offshore faults near Bàsura Cave",
        "known_structures": [
            "North Ligurian Fault System",
            "Ligurian Trough",
            "Monaco-Sanremo offshore segment",
            "Imperia offshore lineaments"
        ]
    },
    "gulf_honduras": {
        "bbox": [-89.5, 15.5, -87.5, 17.0],
        "description": "Gulf of Honduras - offshore Motagua continuation",
        "known_structures": [
            "Swan Islands Transform",
            "Motagua-Polochic offshore"
        ]
    },
    "cascadia_offshore": {
        "bbox": [-126.0, 42.0, -124.0, 46.0],
        "description": "Cascadia subduction zone offshore Oregon",
        "known_structures": [
            "Cascadia Subduction Zone",
            "Blanco Fracture Zone",
            "Gorda Plate"
        ]
    }
}


def download_gebco_subset(bbox, output_dir, resolution="15_arc_second"):
    """
    Download GEBCO bathymetry subset via their grid download interface.

    GEBCO 2023 Grid: 15 arc-second (~450m) global coverage
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nGEBCO Bathymetry Download")
    print("=" * 50)
    print(f"Region: {bbox[0]:.2f}°W to {bbox[2]:.2f}°E, {bbox[1]:.2f}°S to {bbox[3]:.2f}°N")
    print(f"Resolution: {resolution} (~450m)")

    # GEBCO requires interactive download or API access
    print("\nDownload options:")
    print("\n1. GEBCO Grid Download Tool (recommended):")
    print("   https://download.gebco.net/")
    print(f"   - Select region: N={bbox[3]}, S={bbox[1]}, W={bbox[0]}, E={bbox[2]}")
    print("   - Format: GeoTIFF or NetCDF")
    print("   - Grid: GEBCO_2023 Grid")

    print("\n2. OpenTopography (for high-res in specific areas):")
    print("   https://opentopography.org/")
    print("   - May have multibeam surveys for coastal areas")

    # Generate GDAL command for processing
    gdal_script = output_dir / "process_bathymetry.sh"
    with open(gdal_script, 'w') as f:
        f.write('''#!/bin/bash
# Process GEBCO bathymetry data
# Run after downloading GeoTIFF from GEBCO

INPUT_FILE="gebco_2023_subset.tif"
OUTPUT_DIR="processed"

mkdir -p $OUTPUT_DIR

# Create hillshade for visualization
echo "Creating hillshade..."
gdaldem hillshade $INPUT_FILE $OUTPUT_DIR/bathymetry_hillshade.tif -z 5 -az 315 -alt 45

# Create slope map to highlight fault scarps
echo "Creating slope map..."
gdaldem slope $INPUT_FILE $OUTPUT_DIR/bathymetry_slope.tif

# Create color relief
echo "Creating color relief..."
cat > depth_colors.txt << 'EOF'
-5000 0 0 128
-4000 0 0 255
-3000 0 128 255
-2000 0 255 255
-1000 128 255 128
-500 255 255 0
-200 255 200 100
-100 255 230 150
0 200 200 200
EOF
gdaldem color-relief $INPUT_FILE depth_colors.txt $OUTPUT_DIR/bathymetry_color.tif

echo "Processing complete!"
echo "Files in $OUTPUT_DIR/:"
ls -la $OUTPUT_DIR/
''')
    os.chmod(gdal_script, 0o755)
    print(f"\nGenerated processing script: {gdal_script}")

    return gdal_script


def download_emodnet(bbox, output_dir):
    """
    Download EMODnet bathymetry for European waters.

    EMODnet provides higher resolution (~115m) for European waters
    by combining multiple surveys.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nEMODnet Bathymetry (European waters)")
    print("=" * 50)
    print(f"Region: {bbox[0]:.2f}°E to {bbox[2]:.2f}°E, {bbox[1]:.2f}°N to {bbox[3]:.2f}°N")
    print("Resolution: ~115m (1/16 arc-minute)")

    # EMODnet WCS GetCoverage request
    wcs_url = (
        f"{EMODNET_WCS}?service=WCS&version=2.0.1&request=GetCoverage"
        f"&CoverageId=emodnet:mean"
        f"&format=image/tiff"
        f"&subset=Long({bbox[0]},{bbox[2]})"
        f"&subset=Lat({bbox[1]},{bbox[3]})"
    )

    print("\nDirect download URL:")
    print(f"  {wcs_url}")

    output_file = output_dir / "emodnet_bathymetry.tif"
    print(f"\nDownloading to: {output_file}")

    try:
        response = requests.get(wcs_url, stream=True, timeout=120)
        response.raise_for_status()

        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        file_size = output_file.stat().st_size / (1024 * 1024)
        print(f"Downloaded: {file_size:.1f} MB")
        return output_file

    except requests.exceptions.RequestException as e:
        print(f"Download failed: {e}")
        print("\nManual download:")
        print("  1. Visit: https://www.emodnet-bathymetry.eu/")
        print("  2. Use the 'Download' tool to select region")
        print("  3. Export as GeoTIFF")
        return None


def identify_offshore_faults(bbox, output_dir):
    """
    Protocol for identifying potential offshore fault sources.
    """
    print("\n" + "=" * 60)
    print("OFFSHORE FAULT IDENTIFICATION PROTOCOL")
    print("=" * 60)

    print("""
OBJECTIVE: Identify offshore fault candidates for 1285 Dark Earthquake

METHODOLOGY:
1. Download high-resolution bathymetry (EMODnet/GEBCO)
2. Generate slope and hillshade derivatives
3. Identify linear scarps and offsets
4. Cross-reference with:
   - ITHACA database (onshore faults with offshore continuations)
   - Published marine geology surveys
   - Seismic reflection profiles (if available)

LIGURIAN SEA TARGETS:
┌─────────────────────────────────────────────────────────────┐
│ Structure                  │ Kinematics  │ Distance to     │
│                            │             │ Bàsura (km)     │
├────────────────────────────┼─────────────┼─────────────────┤
│ North Ligurian Fault       │ Normal      │ ~40             │
│ Monaco offshore segment    │ Unknown     │ ~35             │
│ Imperia lineaments         │ Unknown     │ ~20             │
│ Ligurian Trough axis       │ Extension   │ ~50             │
└─────────────────────────────────────────────────────────────┘

KEY INDICATORS OF ACTIVE FAULTS:
- Sharp bathymetric scarps (>50m offset)
- Linear deeps parallel to coast
- Submarine canyon deflections
- Sediment ponding asymmetry
- Turbidite distribution patterns

EXPECTED PRODUCTS:
1. bathymetry_hillshade.tif - Visualization of seafloor morphology
2. bathymetry_slope.tif - Highlight steep scarps (faults?)
3. offshore_lineaments.geojson - Digitized potential faults
4. fault_candidates.csv - Attributes and rankings
""")


def main():
    parser = argparse.ArgumentParser(
        description="Download bathymetric data for offshore fault analysis"
    )
    parser.add_argument("--region", choices=list(REGIONS.keys()),
                        help="Predefined offshore region")
    parser.add_argument("--bbox", type=str,
                        help="Custom bounding box: west,south,east,north")
    parser.add_argument("--source", choices=["gebco", "emodnet", "both"],
                        default="both", help="Data source")
    parser.add_argument("--output", type=str, default="bathymetry_data",
                        help="Output directory")
    parser.add_argument("--protocol", action="store_true",
                        help="Show fault identification protocol")

    args = parser.parse_args()

    if args.protocol:
        identify_offshore_faults(None, None)
        return

    # Determine bounding box
    if args.region:
        region_info = REGIONS[args.region]
        bbox = region_info["bbox"]
        print(f"\nRegion: {args.region}")
        print(f"Description: {region_info['description']}")
        print(f"Known structures:")
        for struct in region_info.get("known_structures", []):
            print(f"  - {struct}")
    elif args.bbox:
        bbox = [float(x) for x in args.bbox.split(",")]
    else:
        print("Specify --region or --bbox")
        print("\nAvailable regions:")
        for name, info in REGIONS.items():
            print(f"  {name}: {info['description']}")
        return

    output_dir = Path(args.output)
    if args.region:
        output_dir = output_dir / args.region

    # Download data
    if args.source in ["gebco", "both"]:
        download_gebco_subset(bbox, output_dir)

    if args.source in ["emodnet", "both"]:
        download_emodnet(bbox, output_dir)

    # Show analysis protocol
    identify_offshore_faults(bbox, output_dir)


if __name__ == "__main__":
    main()
