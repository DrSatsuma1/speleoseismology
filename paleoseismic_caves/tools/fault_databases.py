#!/usr/bin/env python3
"""
Fault Database Query Module for Paleoseismic Research.

Provides unified access to multiple fault databases for verifying
whether earthquakes occur on mapped vs unmapped faults ("dark earthquakes").

Supported databases:
- USGS Quaternary Fault and Fold Database (API)
- GEM Global Active Faults (local GeoJSON)
- DISS v3.3.1 (Italy seismogenic sources)

Usage:
    from fault_databases import check_fault_proximity, search_usgs_faults

    # Quick check - queries all databases
    result = check_fault_proximity(lat=44.125, lon=8.208, radius_km=50)

    # Individual database queries
    usgs_faults = search_usgs_faults(lat=32.7, lon=-117.1, radius_km=30)
"""

import json
import math
import os
import urllib.request
import urllib.parse
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class Fault:
    """Represents a fault from any database."""
    name: str
    database: str  # 'usgs', 'gem', 'diss'
    distance_km: float
    slip_rate_mm_yr: Optional[float] = None
    slip_sense: Optional[str] = None  # 'Normal', 'Reverse', 'Strike-slip', etc.
    age: Optional[str] = None  # 'Holocene', 'Late Quaternary', etc.
    last_movement: Optional[str] = None
    fault_id: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    length_km: Optional[float] = None
    dip: Optional[float] = None
    rake: Optional[float] = None
    max_magnitude: Optional[float] = None
    recurrence_yr: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FaultProximityResult:
    """Result of checking all fault databases for nearby faults."""
    has_mapped_fault: bool
    nearest_fault: Optional[Fault]
    distance_km: Optional[float]
    faults_within_radius: List[Fault]
    databases_checked: List[str]
    is_dark_candidate: bool  # True if NO mapped fault found
    confidence: str  # 'HIGH', 'MODERATE', 'LOW'
    notes: List[str]


# =============================================================================
# GEOGRAPHIC UTILITIES
# =============================================================================

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance in km."""
    R = 6371.0
    lat1_rad, lat2_rad = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def point_to_line_distance(
    point_lat: float, point_lon: float,
    line_coords: List[List[float]]
) -> float:
    """
    Calculate minimum distance from point to a line (fault trace).

    Args:
        point_lat, point_lon: Query point
        line_coords: List of [lon, lat] coordinate pairs

    Returns:
        Minimum distance in km
    """
    min_dist = float('inf')

    for i in range(len(line_coords) - 1):
        # Get segment endpoints
        lon1, lat1 = line_coords[i]
        lon2, lat2 = line_coords[i + 1]

        # Distance to each endpoint
        d1 = haversine(point_lat, point_lon, lat1, lon1)
        d2 = haversine(point_lat, point_lon, lat2, lon2)

        # Simple approximation: use minimum of endpoint distances
        # For more accuracy, would project point onto segment
        min_dist = min(min_dist, d1, d2)

    # Also check single point if only one coordinate
    if len(line_coords) == 1:
        lon, lat = line_coords[0]
        min_dist = haversine(point_lat, point_lon, lat, lon)

    return min_dist


# =============================================================================
# USGS QUATERNARY FAULT DATABASE
# =============================================================================

def search_usgs_faults(
    lat: float,
    lon: float,
    radius_km: float = 50,
    timeout: int = 30
) -> List[Fault]:
    """
    Query USGS Quaternary Fault and Fold Database.

    Note: USGS database has 9-27 year lag and incomplete offshore coverage.
    Always cross-reference with state surveys and published studies.

    API: https://earthquake.usgs.gov/cfusion/qfault/

    Args:
        lat, lon: Search center coordinates
        radius_km: Search radius in km
        timeout: Request timeout in seconds

    Returns:
        List of Fault objects within radius
    """
    # USGS QFaults doesn't have a proper REST API, but we can scrape
    # the KML/JSON export. Using the hazards query endpoint.

    # Convert radius to degrees (approximate)
    radius_deg = radius_km / 111.0

    # Bounding box
    min_lat = lat - radius_deg
    max_lat = lat + radius_deg
    min_lon = lon - radius_deg
    max_lon = lon + radius_deg

    # USGS Quaternary Faults GeoJSON endpoint
    # This is the official USGS Hazards endpoint
    url = (
        f"https://earthquake.usgs.gov/ws/geoserve/regions.json?"
        f"latitude={lat}&longitude={lon}&type=fe"
    )

    faults = []

    # Try the USGS fault query - note this endpoint may change
    # Fallback: check if we have local USGS data
    local_usgs = Path(__file__).parent.parent / "data" / "fault_databases" / "usgs_qfaults.geojson"

    if local_usgs.exists():
        faults = _query_local_geojson(local_usgs, lat, lon, radius_km, "usgs")
    else:
        # Try API query
        try:
            # Alternative: use the Hazard Fault Search
            search_url = (
                "https://earthquake.usgs.gov/arcgis/rest/services/"
                "haz/hazfaults2014/MapServer/0/query?"
                f"geometry={min_lon},{min_lat},{max_lon},{max_lat}&"
                "geometryType=esriGeometryEnvelope&"
                "spatialRel=esriSpatialRelIntersects&"
                "outFields=*&f=geojson"
            )

            req = urllib.request.Request(
                search_url,
                headers={'User-Agent': 'PaleoseismicResearch/1.0'}
            )

            with urllib.request.urlopen(req, timeout=timeout) as response:
                data = json.loads(response.read().decode())

            for feature in data.get('features', []):
                props = feature.get('properties', {})
                geom = feature.get('geometry', {})

                # Calculate distance to fault trace
                if geom.get('type') == 'MultiLineString':
                    coords = geom.get('coordinates', [[]])[0]
                elif geom.get('type') == 'LineString':
                    coords = geom.get('coordinates', [])
                else:
                    coords = []

                if coords:
                    dist = point_to_line_distance(lat, lon, coords)
                else:
                    dist = radius_km  # Unknown distance

                if dist <= radius_km:
                    faults.append(Fault(
                        name=props.get('fault_name', props.get('NAME', 'Unknown')),
                        database='usgs',
                        distance_km=round(dist, 1),
                        slip_rate_mm_yr=_parse_slip_rate(props.get('slip_rate')),
                        slip_sense=props.get('slip_sense', props.get('SLIPSENSE')),
                        age=props.get('age', props.get('AGE')),
                        fault_id=props.get('fault_id', props.get('OBJECTID')),
                        metadata=props
                    ))

        except Exception as e:
            # API failed, return empty with note
            return []

    return sorted(faults, key=lambda f: f.distance_km)


def _parse_slip_rate(rate_str: Optional[str]) -> Optional[float]:
    """Parse slip rate string to float."""
    if not rate_str:
        return None
    try:
        # Handle ranges like "0.2-1.0"
        if '-' in str(rate_str):
            parts = str(rate_str).split('-')
            return (float(parts[0]) + float(parts[1])) / 2
        return float(rate_str)
    except (ValueError, IndexError):
        return None


# =============================================================================
# GEM GLOBAL ACTIVE FAULTS
# =============================================================================

def search_gem_faults(
    lat: float,
    lon: float,
    radius_km: float = 50
) -> List[Fault]:
    """
    Query GEM Global Active Faults Database.

    Data source: https://github.com/GEMScienceTools/gem-global-active-faults

    Requires local GeoJSON file at:
    data/fault_databases/gem_active_faults.geojson

    Args:
        lat, lon: Search center coordinates
        radius_km: Search radius in km

    Returns:
        List of Fault objects within radius
    """
    gem_path = Path(__file__).parent.parent / "data" / "fault_databases" / "gem_active_faults.geojson"

    if not gem_path.exists():
        # Try alternative paths
        alt_paths = [
            Path(__file__).parent.parent / "data" / "gem_active_faults.geojson",
            Path(__file__).parent.parent.parent / "data" / "fault_databases" / "gem_active_faults.geojson",
        ]
        for p in alt_paths:
            if p.exists():
                gem_path = p
                break
        else:
            return []  # No GEM data available

    return _query_local_geojson(gem_path, lat, lon, radius_km, "gem")


def _query_local_geojson(
    filepath: Path,
    lat: float,
    lon: float,
    radius_km: float,
    database: str
) -> List[Fault]:
    """Query a local GeoJSON fault file."""
    faults = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

    for feature in data.get('features', []):
        props = feature.get('properties', {})
        geom = feature.get('geometry', {})

        # Get coordinates based on geometry type
        if geom.get('type') == 'MultiLineString':
            all_coords = []
            for line in geom.get('coordinates', []):
                all_coords.extend(line)
            coords = all_coords
        elif geom.get('type') == 'LineString':
            coords = geom.get('coordinates', [])
        elif geom.get('type') == 'Point':
            coords = [geom.get('coordinates', [])]
        else:
            coords = []

        if not coords:
            continue

        # Calculate distance
        dist = point_to_line_distance(lat, lon, coords)

        if dist <= radius_km:
            # Extract properties based on database format
            if database == 'gem':
                name = props.get('name', props.get('fault_name', 'Unknown'))
                slip_rate = props.get('slip_rate', props.get('average_slip_rate'))
                slip_sense = props.get('slip_type', props.get('slip_sense'))
            else:
                name = props.get('fault_name', props.get('NAME', 'Unknown'))
                slip_rate = props.get('slip_rate')
                slip_sense = props.get('slip_sense')

            faults.append(Fault(
                name=name,
                database=database,
                distance_km=round(dist, 1),
                slip_rate_mm_yr=_parse_slip_rate(slip_rate),
                slip_sense=slip_sense,
                fault_id=props.get('ogc_fid', props.get('fault_id')),
                length_km=props.get('length_km'),
                metadata=props
            ))

    return sorted(faults, key=lambda f: f.distance_km)


# =============================================================================
# DISS v3.3.1 (ITALY)
# =============================================================================

def search_diss_sources(
    lat: float,
    lon: float,
    radius_km: float = 50
) -> List[Fault]:
    """
    Query DISS v3.3.1 (Database of Individual Seismogenic Sources) for Italy.

    Data source: https://diss.ingv.it

    Requires local data at:
    data/fault_databases/diss331/

    Args:
        lat, lon: Search center coordinates (should be in Italy region)
        radius_km: Search radius in km

    Returns:
        List of Fault objects (seismogenic sources) within radius
    """
    diss_dir = Path(__file__).parent.parent / "data" / "fault_databases" / "diss331"

    # Try individual source files
    iss_file = diss_dir / "individual_seismogenic_sources.geojson"
    css_file = diss_dir / "composite_seismogenic_sources.geojson"

    faults = []

    # Query Individual Seismogenic Sources (better constrained)
    if iss_file.exists():
        faults.extend(_query_diss_file(iss_file, lat, lon, radius_km, "ISS"))

    # Query Composite Seismogenic Sources
    if css_file.exists():
        faults.extend(_query_diss_file(css_file, lat, lon, radius_km, "CSS"))

    # Fallback: check for combined file
    combined = diss_dir / "diss331.geojson"
    if not faults and combined.exists():
        faults = _query_diss_file(combined, lat, lon, radius_km, "DISS")

    return sorted(faults, key=lambda f: f.distance_km)


def _query_diss_file(
    filepath: Path,
    lat: float,
    lon: float,
    radius_km: float,
    source_type: str
) -> List[Fault]:
    """Query a DISS GeoJSON file."""
    faults = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

    for feature in data.get('features', []):
        props = feature.get('properties', {})
        geom = feature.get('geometry', {})

        # DISS uses various geometry types
        if geom.get('type') == 'Polygon':
            # Use centroid approximation
            coords = geom.get('coordinates', [[]])[0]
            if coords:
                center_lon = sum(c[0] for c in coords) / len(coords)
                center_lat = sum(c[1] for c in coords) / len(coords)
                dist = haversine(lat, lon, center_lat, center_lon)
            else:
                continue
        elif geom.get('type') in ('LineString', 'MultiLineString'):
            if geom.get('type') == 'MultiLineString':
                coords = [c for line in geom.get('coordinates', []) for c in line]
            else:
                coords = geom.get('coordinates', [])
            dist = point_to_line_distance(lat, lon, coords)
        elif geom.get('type') == 'Point':
            coords = geom.get('coordinates', [])
            if len(coords) >= 2:
                dist = haversine(lat, lon, coords[1], coords[0])
            else:
                continue
        else:
            continue

        if dist <= radius_km:
            # Extract DISS-specific properties
            faults.append(Fault(
                name=props.get('name', props.get('Name', f'DISS {source_type}')),
                database='diss',
                distance_km=round(dist, 1),
                slip_rate_mm_yr=props.get('slip_rate_min'),  # DISS has min/max
                slip_sense=props.get('rake_class', props.get('mechanism')),
                fault_id=props.get('iss_id', props.get('css_id', props.get('id'))),
                dip=props.get('dip'),
                rake=props.get('rake'),
                max_magnitude=props.get('max_mag', props.get('Mmax')),
                recurrence_yr=props.get('rec_int_min'),  # Recurrence interval
                length_km=props.get('length'),
                metadata={
                    'source_type': source_type,
                    'min_depth': props.get('min_depth'),
                    'max_depth': props.get('max_depth'),
                    **props
                }
            ))

    return faults


# =============================================================================
# SCEC COMMUNITY FAULT MODEL (CALIFORNIA)
# =============================================================================

def search_scec_faults(
    lat: float,
    lon: float,
    radius_km: float = 50
) -> List[Fault]:
    """
    Query SCEC Community Fault Model v7.0 for California.

    This is the most up-to-date California fault database.

    Data source: https://www.scec.org/research/cfm

    Args:
        lat, lon: Search center (should be in California)
        radius_km: Search radius in km

    Returns:
        List of Fault objects within radius
    """
    scec_path = Path(__file__).parent.parent / "data" / "fault_databases" / "scec_cfm7.geojson"

    if not scec_path.exists():
        return []

    return _query_local_geojson(scec_path, lat, lon, radius_km, "scec")


# =============================================================================
# UNIFIED FAULT PROXIMITY CHECK
# =============================================================================

def check_fault_proximity(
    lat: float,
    lon: float,
    radius_km: float = 50,
    include_databases: Optional[List[str]] = None
) -> FaultProximityResult:
    """
    Check all fault databases for mapped faults near a location.

    This is the main function for verifying "dark earthquake" candidates.
    A true dark earthquake has NO mapped fault within the search radius
    in ANY database.

    Args:
        lat, lon: Location to check
        radius_km: Search radius in km (default 50 km for M6-7 events)
        include_databases: List of databases to check. Default: all available.
            Options: 'usgs', 'gem', 'diss', 'scec'

    Returns:
        FaultProximityResult with:
        - has_mapped_fault: True if ANY fault found
        - is_dark_candidate: True if NO fault found (potential dark earthquake)
        - nearest_fault: Closest fault if any
        - faults_within_radius: All faults found
        - confidence: Assessment confidence

    Example:
        >>> result = check_fault_proximity(44.125, 8.208, radius_km=50)
        >>> if result.is_dark_candidate:
        ...     print("No mapped fault - potential dark earthquake!")
        >>> else:
        ...     print(f"Nearest fault: {result.nearest_fault.name} at {result.distance_km} km")
    """
    if include_databases is None:
        include_databases = ['usgs', 'gem', 'diss', 'scec']

    all_faults = []
    databases_checked = []
    notes = []

    # Determine which databases are relevant based on location
    # Italy region: 35-47°N, 6-19°E
    is_italy = 35 <= lat <= 47 and 6 <= lon <= 19
    # California region: 32-42°N, 114-125°W
    is_california = 32 <= lat <= 42 and -125 <= lon <= -114

    # Query each database
    if 'usgs' in include_databases:
        try:
            usgs_faults = search_usgs_faults(lat, lon, radius_km)
            all_faults.extend(usgs_faults)
            databases_checked.append('usgs')
            if not usgs_faults:
                notes.append("USGS: No faults found (note: 9-27yr database lag)")
        except Exception as e:
            notes.append(f"USGS query failed: {e}")

    if 'gem' in include_databases:
        try:
            gem_faults = search_gem_faults(lat, lon, radius_km)
            all_faults.extend(gem_faults)
            databases_checked.append('gem')
            if not gem_faults:
                notes.append("GEM: No faults found")
        except Exception as e:
            notes.append(f"GEM query failed: {e}")

    if 'diss' in include_databases and is_italy:
        try:
            diss_faults = search_diss_sources(lat, lon, radius_km)
            all_faults.extend(diss_faults)
            databases_checked.append('diss')
            if not diss_faults:
                notes.append("DISS: No seismogenic sources found")
        except Exception as e:
            notes.append(f"DISS query failed: {e}")

    if 'scec' in include_databases and is_california:
        try:
            scec_faults = search_scec_faults(lat, lon, radius_km)
            all_faults.extend(scec_faults)
            databases_checked.append('scec')
            if not scec_faults:
                notes.append("SCEC CFM: No faults found")
        except Exception as e:
            notes.append(f"SCEC query failed: {e}")

    # Sort by distance and deduplicate by name
    all_faults.sort(key=lambda f: f.distance_km)
    seen_names = set()
    unique_faults = []
    for f in all_faults:
        if f.name.lower() not in seen_names:
            unique_faults.append(f)
            seen_names.add(f.name.lower())

    # Determine result
    has_mapped_fault = len(unique_faults) > 0
    nearest = unique_faults[0] if unique_faults else None
    distance = nearest.distance_km if nearest else None

    # Confidence assessment
    if len(databases_checked) >= 3:
        confidence = "HIGH"
    elif len(databases_checked) >= 2:
        confidence = "MODERATE"
    else:
        confidence = "LOW"
        notes.append("Limited database coverage - verify with additional sources")

    # Add region-specific warnings
    if not is_italy and not is_california:
        notes.append("Location outside well-mapped regions (Italy/California)")
        if confidence == "HIGH":
            confidence = "MODERATE"

    return FaultProximityResult(
        has_mapped_fault=has_mapped_fault,
        nearest_fault=nearest,
        distance_km=distance,
        faults_within_radius=unique_faults,
        databases_checked=databases_checked,
        is_dark_candidate=not has_mapped_fault,
        confidence=confidence,
        notes=notes
    )


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """Command-line interface for fault database queries."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Query fault databases for paleoseismic research"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Check proximity command
    check_parser = subparsers.add_parser("check", help="Check fault proximity")
    check_parser.add_argument("--lat", type=float, required=True)
    check_parser.add_argument("--lon", type=float, required=True)
    check_parser.add_argument("--radius", type=float, default=50, help="Radius in km")

    # USGS query
    usgs_parser = subparsers.add_parser("usgs", help="Query USGS faults")
    usgs_parser.add_argument("--lat", type=float, required=True)
    usgs_parser.add_argument("--lon", type=float, required=True)
    usgs_parser.add_argument("--radius", type=float, default=50)

    # GEM query
    gem_parser = subparsers.add_parser("gem", help="Query GEM faults")
    gem_parser.add_argument("--lat", type=float, required=True)
    gem_parser.add_argument("--lon", type=float, required=True)
    gem_parser.add_argument("--radius", type=float, default=50)

    # DISS query
    diss_parser = subparsers.add_parser("diss", help="Query DISS (Italy)")
    diss_parser.add_argument("--lat", type=float, required=True)
    diss_parser.add_argument("--lon", type=float, required=True)
    diss_parser.add_argument("--radius", type=float, default=50)

    args = parser.parse_args()

    if args.command == "check":
        result = check_fault_proximity(args.lat, args.lon, args.radius)
        print(f"\nFault Proximity Check")
        print(f"  Location: {args.lat:.3f}°N, {args.lon:.3f}°E")
        print(f"  Radius: {args.radius} km")
        print(f"  Databases: {', '.join(result.databases_checked)}")
        print(f"  ---")
        print(f"  Mapped fault found: {'YES' if result.has_mapped_fault else 'NO'}")
        print(f"  Dark candidate: {'YES' if result.is_dark_candidate else 'NO'}")
        print(f"  Confidence: {result.confidence}")

        if result.nearest_fault:
            f = result.nearest_fault
            print(f"\n  Nearest fault:")
            print(f"    Name: {f.name}")
            print(f"    Database: {f.database}")
            print(f"    Distance: {f.distance_km} km")
            if f.slip_rate_mm_yr:
                print(f"    Slip rate: {f.slip_rate_mm_yr} mm/yr")
            if f.slip_sense:
                print(f"    Mechanism: {f.slip_sense}")

        if result.notes:
            print(f"\n  Notes:")
            for note in result.notes:
                print(f"    - {note}")

        if len(result.faults_within_radius) > 1:
            print(f"\n  All faults within {args.radius} km ({len(result.faults_within_radius)}):")
            for f in result.faults_within_radius[:10]:
                print(f"    - {f.name} ({f.database}): {f.distance_km} km")

    elif args.command == "usgs":
        faults = search_usgs_faults(args.lat, args.lon, args.radius)
        print(f"\nUSGS Quaternary Faults within {args.radius} km:")
        if faults:
            for f in faults:
                print(f"  {f.name}: {f.distance_km} km")
        else:
            print("  No faults found")

    elif args.command == "gem":
        faults = search_gem_faults(args.lat, args.lon, args.radius)
        print(f"\nGEM Active Faults within {args.radius} km:")
        if faults:
            for f in faults:
                print(f"  {f.name}: {f.distance_km} km")
        else:
            print("  No faults found (check if GEM data is downloaded)")

    elif args.command == "diss":
        faults = search_diss_sources(args.lat, args.lon, args.radius)
        print(f"\nDISS Seismogenic Sources within {args.radius} km:")
        if faults:
            for f in faults:
                print(f"  {f.name}: {f.distance_km} km (Mmax: {f.max_magnitude})")
        else:
            print("  No sources found (check if DISS data is downloaded)")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
