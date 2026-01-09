#!/usr/bin/env python3
"""
Quick analysis: Do INGV earthquakes cluster along T. Porra Fault azimuth?

T. Porra Fault: Strike 111.1° (ESE-WNW), ~14 km from Bàsura Cave
Bàsura Cave: 44.1275°N, 8.1108°E
"""
import math
from collections import Counter

# Bàsura Cave location
BASURA_LAT = 44.1275
BASURA_LON = 8.1108

# T. Porra Fault azimuth (ESE-WNW)
TPORRA_AZIMUTH = 111.1

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two points."""
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def calculate_azimuth(lat1, lon1, lat2, lon2):
    """Calculate azimuth from point 1 to point 2 (degrees from North)."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    azimuth = math.degrees(math.atan2(x, y))
    return (azimuth + 360) % 360

def azimuth_diff(az1, az2):
    """Calculate minimum angular difference between two azimuths."""
    diff = abs(az1 - az2)
    if diff > 180:
        diff = 360 - diff
    return diff

# Parse earthquake data
earthquakes = []
with open('/Users/catherine/projects/quake/paleoseismic_caves/data/ingv_liguria_raw.txt', 'r') as f:
    header = f.readline()
    for line in f:
        parts = line.strip().split('|')
        if len(parts) >= 11:
            try:
                eq = {
                    'time': parts[1],
                    'lat': float(parts[2]),
                    'lon': float(parts[3]),
                    'depth': float(parts[4]) if parts[4] else 10.0,
                    'mag': float(parts[10]) if parts[10] else 0.5,
                    'location': parts[12] if len(parts) > 12 else ''
                }
                earthquakes.append(eq)
            except (ValueError, IndexError):
                continue

print(f"Parsed {len(earthquakes)} earthquakes")
print()

# Calculate azimuth and distance for each earthquake
results = []
for eq in earthquakes:
    dist = haversine_distance(BASURA_LAT, BASURA_LON, eq['lat'], eq['lon'])
    az = calculate_azimuth(BASURA_LAT, BASURA_LON, eq['lat'], eq['lon'])
    eq['distance_km'] = dist
    eq['azimuth'] = az
    eq['az_diff_from_tporra'] = azimuth_diff(az, TPORRA_AZIMUTH)
    results.append(eq)

# Sort by distance
results.sort(key=lambda x: x['distance_km'])

print("=== CLOSEST 20 EARTHQUAKES TO BÀSURA CAVE ===")
print(f"{'Dist(km)':<10} {'Azimuth':<10} {'Δ from T.Porra':<15} {'Mag':<6} {'Location'}")
print("-" * 80)
for eq in results[:20]:
    print(f"{eq['distance_km']:<10.1f} {eq['azimuth']:<10.1f} {eq['az_diff_from_tporra']:<15.1f} {eq['mag']:<6.1f} {eq['location'][:40]}")

print()
print("=== AZIMUTH DISTRIBUTION (from Bàsura to earthquakes) ===")

# Bin azimuths into 30° sectors
bins = {f"{i*30}-{(i+1)*30}°": 0 for i in range(12)}
for eq in results:
    bin_idx = int(eq['azimuth'] // 30)
    bin_name = f"{bin_idx*30}-{(bin_idx+1)*30}°"
    bins[bin_name] += 1

for bin_name, count in sorted(bins.items(), key=lambda x: -x[1]):
    bar = '#' * (count // 5)
    print(f"{bin_name:<12} {count:>4}  {bar}")

print()
print("=== T. PORRA ALIGNMENT TEST ===")
print(f"T. Porra Fault azimuth: {TPORRA_AZIMUTH}°")
print()

# Count earthquakes within different angular windows of T. Porra azimuth
for window in [15, 30, 45]:
    aligned = sum(1 for eq in results if eq['az_diff_from_tporra'] <= window)
    pct = 100 * aligned / len(results)
    # Expected if uniform: window*2/360 * total
    expected_pct = 100 * (window * 2) / 360
    enrichment = pct / expected_pct if expected_pct > 0 else 0
    print(f"Within ±{window}° of T. Porra: {aligned}/{len(results)} ({pct:.1f}%) - Expected if uniform: {expected_pct:.1f}% - Enrichment: {enrichment:.2f}x")

# Also test the anti-azimuth (291°) since faults are bidirectional
print()
print("=== BIDIRECTIONAL TEST (111° OR 291°) ===")
for window in [15, 30]:
    aligned = sum(1 for eq in results
                  if eq['az_diff_from_tporra'] <= window or
                  azimuth_diff(eq['azimuth'], (TPORRA_AZIMUTH + 180) % 360) <= window)
    pct = 100 * aligned / len(results)
    expected_pct = 100 * (window * 4) / 360  # Both directions
    enrichment = pct / expected_pct if expected_pct > 0 else 0
    print(f"Within ±{window}° of T. Porra axis: {aligned}/{len(results)} ({pct:.1f}%) - Expected: {expected_pct:.1f}% - Enrichment: {enrichment:.2f}x")

print()
print("=== EARTHQUAKES WITHIN 20 KM OF BÀSURA ===")
nearby = [eq for eq in results if eq['distance_km'] <= 20]
print(f"Total within 20 km: {len(nearby)}")
if nearby:
    print(f"\nAzimuth distribution of nearby events:")
    for window in [15, 30]:
        aligned = sum(1 for eq in nearby if eq['az_diff_from_tporra'] <= window)
        pct = 100 * aligned / len(nearby) if nearby else 0
        expected_pct = 100 * (window * 2) / 360
        enrichment = pct / expected_pct if expected_pct > 0 else 0
        print(f"  Within ±{window}° of T. Porra: {aligned}/{len(nearby)} ({pct:.1f}%) - Enrichment: {enrichment:.2f}x")

print()
print("=== EARTHQUAKES DIRECTLY ALONG T. PORRA LINE ===")
# T. Porra is at azimuth 111° from Bàsura, distance ~14 km
# Check for earthquakes in that direction
tporra_aligned = [eq for eq in results
                  if eq['az_diff_from_tporra'] <= 20 and 10 <= eq['distance_km'] <= 25]
print(f"Events in T. Porra direction (az 91-131°) at 10-25 km: {len(tporra_aligned)}")
for eq in tporra_aligned[:10]:
    print(f"  {eq['distance_km']:.1f} km, az {eq['azimuth']:.1f}°, M{eq['mag']:.1f}: {eq['location'][:40]}")
