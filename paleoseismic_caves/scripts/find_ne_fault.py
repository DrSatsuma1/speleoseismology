#!/usr/bin/env python3
"""
Search ITHACA for NE-SW trending faults near the earthquake cluster.
Cluster center: 44.1709°N, 8.0941°E
Principal axis: ~31° (NNE-SSW)
"""
import json
import math

# Cluster center from earthquake analysis
CLUSTER_LAT = 44.1709
CLUSTER_LON = 8.0941
CLUSTER_TREND = 30.9  # degrees from N

# Bàsura location for reference
BASURA_LAT = 44.1275
BASURA_LON = 8.1108

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def calc_bearing(coords):
    """Calculate bearing of a fault from its coordinate list."""
    if len(coords) < 2:
        return None
    # Use first and last points
    lon1, lat1 = coords[0]
    lon2, lat2 = coords[-1]
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    bearing = math.degrees(math.atan2(x, y))
    return (bearing + 360) % 360

def azimuth_diff(az1, az2):
    """Minimum angular difference, treating faults as bidirectional."""
    diff = abs(az1 - az2)
    if diff > 180:
        diff = 360 - diff
    if diff > 90:
        diff = 180 - diff  # Faults are bidirectional
    return diff

# Load ITHACA faults
with open('/Users/catherine/projects/quake/dem_tiles/ithaca_liguria.geojson', 'r') as f:
    data = json.load(f)

faults = []
for feature in data['features']:
    props = feature['properties']
    geom = feature['geometry']

    if geom['type'] == 'MultiLineString':
        coords = geom['coordinates'][0]  # Take first line
    elif geom['type'] == 'LineString':
        coords = geom['coordinates']
    else:
        continue

    if not coords:
        continue

    # Calculate fault centroid
    avg_lon = sum(c[0] for c in coords) / len(coords)
    avg_lat = sum(c[1] for c in coords) / len(coords)

    # Distance from cluster center
    dist_cluster = haversine(CLUSTER_LAT, CLUSTER_LON, avg_lat, avg_lon)
    dist_basura = haversine(BASURA_LAT, BASURA_LON, avg_lat, avg_lon)

    # Fault bearing
    bearing = calc_bearing(coords)
    if bearing is None:
        continue

    # Angular difference from earthquake trend
    trend_diff = azimuth_diff(bearing, CLUSTER_TREND)

    faults.append({
        'name': props.get('nome', props.get('faultcode', 'Unknown')),
        'code': props.get('faultcode', ''),
        'kinematics': props.get('cinematica', 'ND'),
        'bearing': bearing,
        'trend_diff': trend_diff,
        'dist_cluster': dist_cluster,
        'dist_basura': dist_basura,
        'lat': avg_lat,
        'lon': avg_lon,
        'coords': coords
    })

# Filter for faults that match the earthquake trend (within 20°) AND are within 30 km of cluster
matches = [f for f in faults if f['trend_diff'] <= 20 and f['dist_cluster'] <= 30]
matches.sort(key=lambda x: (x['dist_cluster'], x['trend_diff']))

print(f"=== FAULTS MATCHING EARTHQUAKE TREND (~31° ± 20°) ===")
print(f"Total faults in ITHACA: {len(faults)}")
print(f"Matching trend and within 30 km of cluster: {len(matches)}")
print()

print(f"{'Fault Name':<30} {'Code':<8} {'Kinema':<10} {'Bearing':<8} {'ΔTrend':<8} {'Dist_Cl':<8} {'Dist_Bas':<8}")
print("-" * 100)
for f in matches[:25]:
    print(f"{f['name'][:29]:<30} {f['code']:<8} {f['kinematics'][:9]:<10} {f['bearing']:>6.1f}° {f['trend_diff']:>6.1f}° {f['dist_cluster']:>6.1f}km {f['dist_basura']:>6.1f}km")

# Highlight the CLOSEST matching fault
if matches:
    best = matches[0]
    print(f"\n=== BEST MATCH: {best['name']} ===")
    print(f"Fault code: {best['code']}")
    print(f"Kinematics: {best['kinematics']}")
    print(f"Bearing: {best['bearing']:.1f}°")
    print(f"Distance from earthquake cluster center: {best['dist_cluster']:.1f} km")
    print(f"Distance from Bàsura Cave: {best['dist_basura']:.1f} km")
    print(f"Trend alignment: {best['trend_diff']:.1f}° off from earthquake cloud axis")

    # Get coordinate extent
    lats = [c[1] for c in best['coords']]
    lons = [c[0] for c in best['coords']]
    print(f"Fault extent: {min(lats):.4f}-{max(lats):.4f}°N, {min(lons):.4f}-{max(lons):.4f}°E")

# Also look at ALL faults within 15 km of Bàsura regardless of trend
print(f"\n=== ALL FAULTS WITHIN 15 KM OF BÀSURA ===")
nearby = [f for f in faults if f['dist_basura'] <= 15]
nearby.sort(key=lambda x: x['dist_basura'])

for f in nearby:
    match_flag = "✓ MATCH" if f['trend_diff'] <= 20 else ""
    print(f"  {f['dist_basura']:>5.1f}km  {f['bearing']:>6.1f}°  {f['kinematics']:<10} {f['name'][:35]:<35} {match_flag}")
