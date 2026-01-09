#!/usr/bin/env python3
"""
Map INGV earthquake clusters and identify the active fault.
Focus on the 30-60° (NE) cluster from Bàsura.
"""
import math
import json

# Bàsura Cave location
BASURA_LAT = 44.1275
BASURA_LON = 8.1108

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def calculate_azimuth(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    azimuth = math.degrees(math.atan2(x, y))
    return (azimuth + 360) % 360

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
                eq['distance'] = haversine_distance(BASURA_LAT, BASURA_LON, eq['lat'], eq['lon'])
                eq['azimuth'] = calculate_azimuth(BASURA_LAT, BASURA_LON, eq['lat'], eq['lon'])
                earthquakes.append(eq)
            except (ValueError, IndexError):
                continue

print(f"Total earthquakes: {len(earthquakes)}")

# Focus on the 30-60° cluster (NE from Bàsura)
ne_cluster = [eq for eq in earthquakes if 30 <= eq['azimuth'] <= 60]
print(f"\n=== NE CLUSTER (azimuth 30-60°): {len(ne_cluster)} events ===")

# Find the geographic center of this cluster
if ne_cluster:
    avg_lat = sum(eq['lat'] for eq in ne_cluster) / len(ne_cluster)
    avg_lon = sum(eq['lon'] for eq in ne_cluster) / len(ne_cluster)
    avg_dist = sum(eq['distance'] for eq in ne_cluster) / len(ne_cluster)
    print(f"Cluster center: {avg_lat:.4f}°N, {avg_lon:.4f}°E")
    print(f"Average distance from Bàsura: {avg_dist:.1f} km")

    # Get the bounding box
    min_lat = min(eq['lat'] for eq in ne_cluster)
    max_lat = max(eq['lat'] for eq in ne_cluster)
    min_lon = min(eq['lon'] for eq in ne_cluster)
    max_lon = max(eq['lon'] for eq in ne_cluster)
    print(f"Lat range: {min_lat:.4f}° to {max_lat:.4f}°")
    print(f"Lon range: {min_lon:.4f}° to {max_lon:.4f}°")

# What are the most common locations?
print(f"\n=== MOST COMMON LOCATIONS IN NE CLUSTER ===")
locations = {}
for eq in ne_cluster:
    loc = eq['location'].split('(')[0].strip()  # Remove province code
    locations[loc] = locations.get(loc, 0) + 1

for loc, count in sorted(locations.items(), key=lambda x: -x[1])[:15]:
    print(f"  {count:3d}  {loc}")

# Now look at the secondary cluster (330-360°, NNW)
nnw_cluster = [eq for eq in earthquakes if 330 <= eq['azimuth'] <= 360]
print(f"\n=== NNW CLUSTER (azimuth 330-360°): {len(nnw_cluster)} events ===")

if nnw_cluster:
    avg_lat = sum(eq['lat'] for eq in nnw_cluster) / len(nnw_cluster)
    avg_lon = sum(eq['lon'] for eq in nnw_cluster) / len(nnw_cluster)
    avg_dist = sum(eq['distance'] for eq in nnw_cluster) / len(nnw_cluster)
    print(f"Cluster center: {avg_lat:.4f}°N, {avg_lon:.4f}°E")
    print(f"Average distance from Bàsura: {avg_dist:.1f} km")

locations = {}
for eq in nnw_cluster:
    loc = eq['location'].split('(')[0].strip()
    locations[loc] = locations.get(loc, 0) + 1

print("\nMost common locations:")
for loc, count in sorted(locations.items(), key=lambda x: -x[1])[:10]:
    print(f"  {count:3d}  {loc}")

# Also check the VERY CLOSE earthquakes (< 5 km)
print(f"\n=== CLOSEST EARTHQUAKES (< 5 km from Bàsura) ===")
close = [eq for eq in earthquakes if eq['distance'] < 5]
print(f"Total: {len(close)} events")
for eq in sorted(close, key=lambda x: x['distance'])[:20]:
    print(f"  {eq['distance']:.1f} km, az {eq['azimuth']:.0f}°, M{eq['mag']:.1f}: {eq['location']}")

# Calculate the dominant trend within 20 km
print(f"\n=== AZIMUTH DISTRIBUTION WITHIN 20 KM ===")
nearby = [eq for eq in earthquakes if eq['distance'] <= 20]
bins = {}
for eq in nearby:
    bin_idx = int(eq['azimuth'] // 30) * 30
    bins[bin_idx] = bins.get(bin_idx, 0) + 1

for az, count in sorted(bins.items(), key=lambda x: -x[1]):
    bar = '#' * (count // 3)
    print(f"  {az:3d}-{az+30:3d}°: {count:3d}  {bar}")

# Look for linear alignment - calculate the best-fit line through the earthquake cloud
print(f"\n=== LOOKING FOR LINEAR FAULT ALIGNMENT ===")

# Earthquakes within 25 km
analysis_set = [eq for eq in earthquakes if eq['distance'] <= 25]
print(f"Analyzing {len(analysis_set)} events within 25 km")

# Convert to local coordinates (km from Bàsura)
for eq in analysis_set:
    # Approximate x,y in km
    eq['x'] = (eq['lon'] - BASURA_LON) * 111.32 * math.cos(math.radians(BASURA_LAT))
    eq['y'] = (eq['lat'] - BASURA_LAT) * 110.57

# Fit a line through the earthquake cloud
if len(analysis_set) > 2:
    x_vals = [eq['x'] for eq in analysis_set]
    y_vals = [eq['y'] for eq in analysis_set]

    # Calculate covariance matrix
    x_mean = sum(x_vals) / len(x_vals)
    y_mean = sum(y_vals) / len(y_vals)

    cov_xx = sum((x - x_mean)**2 for x in x_vals) / len(x_vals)
    cov_yy = sum((y - y_mean)**2 for y in y_vals) / len(y_vals)
    cov_xy = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_vals, y_vals)) / len(x_vals)

    # Principal component direction
    import math
    theta = 0.5 * math.atan2(2 * cov_xy, cov_xx - cov_yy)
    azimuth = (90 - math.degrees(theta)) % 180  # Convert to compass bearing

    print(f"\nPrincipal axis of earthquake cloud: {azimuth:.1f}° (or {azimuth+180:.1f}°)")
    print(f"Cluster center: {x_mean:.1f} km E, {y_mean:.1f} km N of Bàsura")
    print(f"  = {BASURA_LAT + y_mean/110.57:.4f}°N, {BASURA_LON + x_mean/(111.32*math.cos(math.radians(BASURA_LAT))):.4f}°E")

# Compare with ITHACA faults
print(f"\n=== COMPARING WITH ITHACA FAULTS ===")
print(f"T. Porra Fault: 111.1° strike - MISMATCH with earthquake cloud")
print(f"BSM trend (NE-SW): ~20-40° strike - let's check...")
