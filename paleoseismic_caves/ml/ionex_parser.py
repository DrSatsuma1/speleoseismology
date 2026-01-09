"""
IONEX File Parser for GPS-TEC Data

Parses IONEX (IONosphere EXchange) format files from CDDIS/IGS.
Extracts TEC values for specific locations and times.

NO SIMULATED DATA - real observations only.
"""

import gzip
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
import re


def decompress_ionex(filepath: Path) -> str:
    """Decompress .Z file and return contents as string."""
    if str(filepath).endswith('.Z'):
        import subprocess
        # Use gunzip to decompress
        result = subprocess.run(['gunzip', '-c', str(filepath)],
                              capture_output=True, check=True)
        return result.stdout.decode('utf-8')
    else:
        with open(filepath, 'r') as f:
            return f.read()


def parse_ionex_header(content: str) -> dict:
    """Parse IONEX header to get grid parameters."""
    header = {}

    for line in content.split('\n'):
        if 'END OF HEADER' in line:
            break
        if 'EPOCH OF FIRST MAP' in line:
            parts = line[:60].split()
            header['first_epoch'] = datetime(int(parts[0]), int(parts[1]), int(parts[2]),
                                            int(parts[3]), int(parts[4]), int(parts[5]))
        elif 'EPOCH OF LAST MAP' in line:
            parts = line[:60].split()
            header['last_epoch'] = datetime(int(parts[0]), int(parts[1]), int(parts[2]),
                                           int(parts[3]), int(parts[4]), int(parts[5]))
        elif 'INTERVAL' in line:
            header['interval'] = int(line[:60].strip())
        elif '# OF MAPS IN FILE' in line:
            header['n_maps'] = int(line[:60].strip())
        elif 'EXPONENT' in line:
            header['exponent'] = int(line[:60].strip())
        elif 'LAT1 / LAT2 / DLAT' in line:
            parts = line[:60].split()
            header['lat1'] = float(parts[0])
            header['lat2'] = float(parts[1])
            header['dlat'] = float(parts[2])
        elif 'LON1 / LON2 / DLON' in line:
            parts = line[:60].split()
            header['lon1'] = float(parts[0])
            header['lon2'] = float(parts[1])
            header['dlon'] = float(parts[2])

    # Calculate grid dimensions
    header['n_lat'] = int((header['lat1'] - header['lat2']) / abs(header['dlat'])) + 1
    header['n_lon'] = int((header['lon2'] - header['lon1']) / header['dlon']) + 1

    return header


def parse_tec_maps(content: str, header: dict) -> List[Tuple[datetime, np.ndarray]]:
    """Parse all TEC maps from IONEX content."""
    maps = []
    lines = content.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i]

        if 'START OF TEC MAP' in line:
            map_num = int(line[:6].strip())
            i += 1

            # Parse epoch
            epoch_line = lines[i]
            parts = epoch_line[:60].split()
            epoch = datetime(int(parts[0]), int(parts[1]), int(parts[2]),
                           int(parts[3]), int(parts[4]), int(parts[5]))
            i += 1

            # Parse TEC grid
            tec_grid = np.zeros((header['n_lat'], header['n_lon']))
            lat_idx = 0

            while i < len(lines) and 'END OF TEC MAP' not in lines[i]:
                if 'LAT/LON1/LON2/DLON/H' in lines[i]:
                    # Start of new latitude row
                    lat_val = float(lines[i][:8].strip())
                    i += 1

                    # Read TEC values for this latitude (5 lines of data)
                    lon_values = []
                    while i < len(lines) and 'LAT/LON1/LON2/DLON/H' not in lines[i] and 'END OF TEC MAP' not in lines[i]:
                        # Each line has up to 16 values, 5 chars each
                        for j in range(0, min(80, len(lines[i])), 5):
                            val_str = lines[i][j:j+5].strip()
                            if val_str:
                                lon_values.append(int(val_str))
                        i += 1

                    # Store in grid
                    if lat_idx < header['n_lat']:
                        tec_grid[lat_idx, :len(lon_values)] = lon_values
                        lat_idx += 1
                else:
                    i += 1

            # Apply exponent
            tec_grid = tec_grid * (10 ** header['exponent'])

            # Replace 9999 with NaN
            tec_grid[tec_grid > 900] = np.nan

            maps.append((epoch, tec_grid))

        i += 1

    return maps


def get_tec_at_location(maps: List[Tuple[datetime, np.ndarray]],
                        header: dict,
                        lat: float, lon: float) -> pd.DataFrame:
    """Extract TEC time series for a specific location."""

    # Find nearest grid point
    lat_idx = int(round((header['lat1'] - lat) / abs(header['dlat'])))
    lon_idx = int(round((lon - header['lon1']) / header['dlon']))

    # Clamp to grid bounds
    lat_idx = max(0, min(lat_idx, header['n_lat'] - 1))
    lon_idx = max(0, min(lon_idx, header['n_lon'] - 1))

    # Actual grid coordinates
    actual_lat = header['lat1'] - lat_idx * abs(header['dlat'])
    actual_lon = header['lon1'] + lon_idx * header['dlon']

    print(f"Requested: ({lat:.2f}, {lon:.2f})")
    print(f"Grid point: ({actual_lat:.1f}, {actual_lon:.1f})")

    # Extract time series
    data = []
    for epoch, grid in maps:
        tec = grid[lat_idx, lon_idx]
        data.append({
            'timestamp': epoch,
            'tec': tec,
            'latitude': actual_lat,
            'longitude': actual_lon
        })

    return pd.DataFrame(data)


def load_ionex_file(filepath: Path, lat: float, lon: float) -> pd.DataFrame:
    """Load single IONEX file and extract TEC for location."""
    print(f"Loading {filepath.name}...")

    content = decompress_ionex(filepath)
    header = parse_ionex_header(content)
    maps = parse_tec_maps(content, header)

    print(f"  Found {len(maps)} TEC maps")
    print(f"  Grid: {header['n_lat']} x {header['n_lon']}")
    print(f"  Epoch range: {header['first_epoch']} to {header['last_epoch']}")

    df = get_tec_at_location(maps, header, lat, lon)
    return df


def load_ionex_directory(dirpath: Path, lat: float, lon: float,
                         prefix: str = 'jplg') -> pd.DataFrame:
    """Load all IONEX files from directory matching prefix."""

    files = sorted(dirpath.glob(f'{prefix}*.Z'))
    if not files:
        files = sorted(dirpath.glob(f'{prefix}*.19i'))

    if not files:
        raise RuntimeError(f"No IONEX files found matching {prefix}* in {dirpath}")

    print(f"Found {len(files)} IONEX files with prefix '{prefix}'")

    all_data = []
    for f in files:
        try:
            df = load_ionex_file(f, lat, lon)
            all_data.append(df)
        except Exception as e:
            print(f"  Error processing {f.name}: {e}")

    if not all_data:
        raise RuntimeError("No TEC data extracted from any file")

    result = pd.concat(all_data, ignore_index=True)
    result = result.sort_values('timestamp').drop_duplicates('timestamp')

    return result


def ridgecrest_test():
    """Test with Ridgecrest M7.1 earthquake data."""
    print("=" * 60)
    print("RIDGECREST M7.1 TEC ANALYSIS - REAL DATA")
    print("=" * 60)

    # Ridgecrest coordinates
    eq_lat = 35.77
    eq_lon = -117.60
    eq_time = datetime(2019, 7, 6, 3, 19, 0)  # 20:19 UTC = 03:19 UTC next day? Actually 2019-07-06 03:19:53 UTC

    print(f"\nEarthquake: M7.1 Ridgecrest")
    print(f"  Location: {eq_lat}°N, {eq_lon}°W")
    print(f"  Time: {eq_time} UTC")

    # Load IONEX data
    ionex_dir = Path(__file__).parent / "ionex_data"

    # Try JPL first (best quality)
    try:
        df = load_ionex_directory(ionex_dir, eq_lat, eq_lon, prefix='jplg')
    except RuntimeError:
        df = load_ionex_directory(ionex_dir, eq_lat, eq_lon, prefix='igsg')

    print(f"\n--- TEC DATA SUMMARY ---")
    print(f"  Observations: {len(df)}")
    print(f"  Time range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"  Mean TEC: {df['tec'].mean():.2f} TECU")
    print(f"  Std TEC: {df['tec'].std():.2f} TECU")
    print(f"  Min TEC: {df['tec'].min():.2f} TECU")
    print(f"  Max TEC: {df['tec'].max():.2f} TECU")

    # Save output
    output_dir = Path(__file__).parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "ridgecrest_tec_real.csv"
    df.to_csv(output_file, index=False)
    print(f"\nSaved to {output_file}")

    return df


if __name__ == '__main__':
    df = ridgecrest_test()
    print("\n--- TEC VALUES ---")
    print(df.to_string())
