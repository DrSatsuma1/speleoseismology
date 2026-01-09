#!/usr/bin/env python3
"""
Reverse validation: Start with known earthquakes → find nearby caves → test for signals.
This is faster than searching ML candidates because we know the earthquakes are real.
"""

import sys
sys.path.append('paleoseismic_caves/tools')

# Will use MCP tools for SISAL searches
print("Earthquake → Cave Validation Pipeline")
print("=" * 80)
print()

# Top 50 well-documented historical earthquakes for validation
VALIDATION_TARGETS = [
    # MEDITERRANEAN (1000+ years of records)
    (1755, 36.0, -9.0, 8.5, 'Lisbon', 'Portugal'),
    (1908, 38.25, 15.58, 7.1, 'Messina', 'Italy/Sicily'),
    (1693, 37.1, 15.1, 7.4, 'Sicily', 'Italy'),
    (1783, 38.3, 16.0, 7.0, 'Calabria', 'Italy'),
    (1456, 41.3, 14.4, 7.2, 'Naples', 'Italy'),
    (1349, 41.9, 13.5, 6.5, 'L\'Aquila', 'Italy'),
    (1348, 45.5, 11.0, 6.5, 'Friuli', 'Italy'),
    (1117, 45.2, 11.5, 6.5, 'Verona', 'Italy'),
    (365, 35.0, 25.0, 8.5, 'Crete', 'Greece'),
    (1303, 40.7, 30.0, 7.0, 'Izmit region', 'Turkey'),
    (1668, 38.5, 39.5, 8.0, 'Anatolia', 'Turkey'),
    (1138, 36.2, 37.2, 8.5, 'Aleppo', 'Syria - 230k deaths'),
    (1170, 35.5, 36.0, 7.5, 'Syria', 'Middle East'),

    # CHINA (continuous records back to 780 BCE!)
    (1920, 36.5, 105.7, 8.5, 'Haiyuan', 'China - 237k deaths'),
    (1679, 39.9, 118.0, 8.0, 'Sanhe-Pinggu', 'China'),
    (1556, 34.5, 109.0, 8.0, 'Shaanxi', 'China - 830k deaths'),
    (1303, 36.0, 111.0, 8.0, 'Hongdong', 'China'),
    (1290, 33.0, 120.0, 7.0, 'Jiangsu', 'China'),
    (1057, 39.0, 114.5, 7.0, 'Daming', 'China'),
    (1038, 23.0, 113.0, 7.0, 'Guangdong', 'China'),
    (1036, 36.5, 105.0, 7.5, 'Gansu', 'China'),
    (1033, 26.5, 103.0, 7.0, 'Sichuan', 'China'),
    (780, 33.0, 105.0, 7.0, 'Gansu', 'China - earliest record'),
    (-780, 34.5, 109.0, 7.0, 'Shaanxi', 'China - 780 BCE'),

    # JAPAN (excellent temple/shrine records)
    (1923, 35.3, 139.5, 7.9, 'Kanto', 'Japan'),
    (1891, 35.6, 136.6, 8.0, 'Nobi', 'Japan'),
    (1854, 33.0, 135.0, 8.4, 'Ansei-Nankai', 'Japan'),
    (1707, 33.2, 135.9, 8.6, 'Hoei', 'Japan - Mt. Fuji eruption'),
    (1703, 34.7, 139.8, 8.2, 'Genroku', 'Japan'),
    (1596, 33.8, 135.8, 7.5, 'Keicho-Fushimi', 'Japan'),
    (1498, 34.0, 137.0, 8.6, 'Meio Nankai', 'Japan'),
    (1361, 33.0, 135.0, 8.4, 'Shohei Nankai', 'Japan'),
    (1293, 35.3, 139.5, 7.1, 'Kamakura', 'Japan'),
    (869, 38.0, 142.0, 8.3, 'Jogan', 'Japan - tsunami'),
    (684, 33.0, 135.0, 8.4, 'Hakuho Nankai', 'Japan'),

    # NORTH AMERICA
    (1906, 37.75, -122.5, 7.9, 'San Francisco', 'California'),
    (1857, 35.7, -120.5, 7.9, 'Fort Tejon', 'California'),
    (1812, 36.6, -89.6, 7.7, 'New Madrid #1', 'Missouri'),
    (1811, 36.6, -89.6, 7.5, 'New Madrid #2', 'Missouri'),
    (1700, 45.0, -125.0, 9.0, 'Cascadia', 'Pacific Northwest'),

    # SOUTH AMERICA
    (1868, -18.5, -71.0, 8.5, 'Arica', 'Peru/Chile'),
    (1755, -36.8, -73.0, 8.5, 'Concepcion', 'Chile'),
    (1730, -33.0, -71.6, 8.7, 'Valparaiso', 'Chile'),
    (1575, -39.8, -73.2, 8.5, 'Valdivia', 'Chile'),

    # MIDDLE EAST/INDIA
    (1999, 40.7, 30.0, 7.6, 'Izmit', 'Turkey'),
    (1939, 39.8, 39.5, 7.8, 'Erzincan', 'Turkey'),
    (1905, 33.0, 76.0, 7.8, 'Kangra', 'India'),
    (1819, 23.6, 68.5, 8.0, 'Rann of Kutch', 'India'),
]

print(f"Validation target earthquakes: {len(VALIDATION_TARGETS)}")
print()
print("Strategy:")
print("1. For each earthquake, search SISAL for caves within 100 km")
print("2. Check if cave record covers earthquake date")
print("3. Download cave data using sisal_get_samples")
print("4. Test for z>2.0 signal within ±20 years of earthquake")
print()
print("=" * 80)
print()

# Print formatted list for manual processing
print("PRIORITY EARTHQUAKES FOR CAVE SEARCH:")
print()

for year, lat, lon, mag, name, region in VALIDATION_TARGETS[:30]:  # Top 30
    print(f"Year: {year:5d}  |  M{mag:.1f}  |  {name:25s} ({region})")
    print(f"  Coordinates: {lat:7.2f}, {lon:8.2f}")
    print(f"  → Search SISAL for caves near {lat:.2f}, {lon:.2f}")
    print()

print()
print("=" * 80)
print("NEXT STEPS:")
print("1. Use sisal_search_caves MCP tool for each earthquake location")
print("2. For matches, use sisal_get_samples to download data")
print("3. Run z-score analysis on earthquake date ± 20 years")
print("4. Document all matches (including negatives) for statistics")
print("=" * 80)
