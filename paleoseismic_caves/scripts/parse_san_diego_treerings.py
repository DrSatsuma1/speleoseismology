#!/usr/bin/env python3
"""Parse San Diego County tree ring chronologies."""

def parse_simple(filepath):
    """Parse ITRDB .crn format."""
    data = []
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    for line in lines[3:]:
        if len(line) < 20:
            continue
        try:
            decade = int(line[6:10])
        except:
            continue
        
        rest = line[10:60]
        for i in range(10):
            try:
                chunk = rest[i*5:(i+1)*5].strip()
                if not chunk or '9990' in chunk or chunk == '0':
                    continue
                if len(chunk) >= 4:
                    val = int(chunk[-4:]) / 1000.0 if int(chunk[-4:]) < 3000 else int(chunk[-3:]) / 1000.0
                    if 0.1 < val < 3.0:
                        data.append((decade + i, val))
            except:
                continue
    return data

mt_laguna = parse_simple('data/tree_rings/ca610_mt_laguna.crn')
palomar = parse_simple('data/tree_rings/ca611_palomar.crn')

print("=" * 70)
print("SAN DIEGO COUNTY TREE RING ANALYSIS")
print("=" * 70)

for name, data in [("Mt. Laguna (Jeffrey Pine, 32.52N 116.25W)", mt_laguna), 
                   ("Palomar Mt. (Bigcone Douglas-fir, 33.21N 116.51W)", palomar)]:
    if not data:
        continue
    indices = [d[1] for d in data]
    mean = sum(indices) / len(indices)
    std = (sum((x - mean)**2 for x in indices) / len(indices)) ** 0.5
    
    print(f"\n{name}")
    years = [d[0] for d in data]
    print(f"Period: {min(years)}-{max(years)} ({len(data)} years)")
    print(f"Mean: {mean:.3f}, Std: {std:.3f}")
    
    print("\n  ROCKWELL DATE WINDOWS:")
    for window, label in [
        ((1740, 1760), "~1745-1755 (Rose Canyon mid-1700s / SJF ~1750)"),
        ((1795, 1810), "1800 SJF Mw 7.3 (Nov 22, 1800)"),
        ((1855, 1870), "1862 Rose Canyon ~M6"),
        ((1900, 1915), "1906 SF M7.9 (validation)")
    ]:
        print(f"\n  {label}:")
        window_data = [(y, idx) for y, idx in data if window[0] <= y <= window[1]]
        for year, idx in sorted(window_data):
            z = (idx - mean) / std
            flag = " ** ANOMALY" if abs(z) > 1.5 else ""
            print(f"    {year}: {idx:.3f} (z={z:+.2f}){flag}")

print("\n" + "=" * 70)
print("TOP 10 EXTREME YEARS (potential earthquake signals)")
print("=" * 70)

for name, data in [("Mt. Laguna", mt_laguna), ("Palomar", palomar)]:
    if not data:
        continue
    indices = [d[1] for d in data]
    mean = sum(indices) / len(indices)
    std = (sum((x - mean)**2 for x in indices) / len(indices)) ** 0.5
    
    extremes = [(y, idx, (idx - mean) / std) for y, idx in data]
    extremes.sort(key=lambda x: x[2])
    
    print(f"\n{name} - STRONGEST SUPPRESSIONS (possible damage):")
    for y, idx, z in extremes[:5]:
        print(f"  {y}: index={idx:.3f}, z={z:+.2f}")
    
    print(f"\n{name} - STRONGEST ENHANCEMENTS (possible release effect):")
    for y, idx, z in extremes[-5:]:
        print(f"  {y}: index={idx:.3f}, z={z:+.2f}")

