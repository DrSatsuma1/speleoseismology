#!/usr/bin/env python3
"""
Puerto Rico Speleothem Paleoseismic Analysis
Analyzes Perdida Cave and Larga Cave data for seismic anomalies
near the Puerto Rico Trench subduction zone.
"""

import csv
import math

def load_timeseries(filepath):
    """Load timeseries data from CSV."""
    data = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                age_field = row.get('age_BP', row.get('age', 'NA'))
                age = float(age_field) if age_field and age_field != 'NA' else None
                d18O_field = row.get('d18O', 'NA')
                d18O = float(d18O_field) if d18O_field and d18O_field != 'NA' else None

                if age is not None and d18O is not None:
                    entry = {
                        'sample_id': row.get('sample_id'),
                        'age_BP': age,
                        'd18O': d18O,
                    }

                    d13C_field = row.get('d13C', 'NA')
                    if d13C_field and d13C_field != 'NA':
                        try:
                            entry['d13C'] = float(d13C_field)
                        except:
                            entry['d13C'] = None
                    else:
                        entry['d13C'] = None

                    MgCa_field = row.get('Mg_Ca', 'NA')
                    if MgCa_field and MgCa_field != 'NA':
                        try:
                            entry['Mg_Ca'] = float(MgCa_field)
                        except:
                            entry['Mg_Ca'] = None
                    else:
                        entry['Mg_Ca'] = None

                    data.append(entry)
            except (ValueError, TypeError) as e:
                continue
    return sorted(data, key=lambda x: x['age_BP'])

def mean(values):
    """Calculate mean."""
    return sum(values) / len(values) if values else 0

def std(values, m=None):
    """Calculate standard deviation."""
    if not values or len(values) < 2:
        return 0
    if m is None:
        m = mean(values)
    variance = sum((x - m) ** 2 for x in values) / len(values)
    return math.sqrt(variance)

def calculate_zscore_anomalies(data, proxy='d18O', threshold=2.0):
    """Detect anomalies using z-score method."""
    values = [d[proxy] for d in data if d.get(proxy) is not None]
    if not values:
        return [], 0, 0

    m = mean(values)
    s = std(values, m)

    anomalies = []
    for d in data:
        val = d.get(proxy)
        if val is not None:
            z = (val - m) / s if s > 0 else 0
            if abs(z) >= threshold:
                anomalies.append({
                    'age_BP': d['age_BP'],
                    'value': val,
                    'z_score': z,
                    'proxy': proxy
                })
    return anomalies, m, s

def analyze_cave(name, filepath, has_d13C=False, has_MgCa=False):
    """Analyze a single cave record."""
    print(f"\n{'='*60}")
    print(f"{name} ANALYSIS")
    print(f"{'='*60}")

    try:
        data = load_timeseries(filepath)
    except Exception as e:
        print(f"  Error loading {filepath}: {e}")
        return []

    if not data:
        print(f"  No valid data loaded from {filepath}")
        return []

    print(f"\nRecord Overview:")
    print(f"  Samples with valid data: {len(data)}")
    ages = [d['age_BP'] for d in data]
    print(f"  Age range: {min(ages):.0f} - {max(ages):.0f} BP")
    print(f"  Resolution: ~{(max(ages) - min(ages)) / len(ages):.1f} years/sample")

    # d18O analysis
    print(f"\nδ18O Analysis:")
    d18O_anomalies, d18O_mean, d18O_std = calculate_zscore_anomalies(data, 'd18O', threshold=2.0)
    print(f"  Mean: {d18O_mean:.2f}‰, Std: {d18O_std:.2f}‰")
    print(f"  Anomalies (|z| > 2): {len(d18O_anomalies)}")

    if d18O_anomalies:
        print(f"\n  Top 10 δ18O Anomalies:")
        sorted_anom = sorted(d18O_anomalies, key=lambda x: abs(x['z_score']), reverse=True)[:10]
        for a in sorted_anom:
            sign = '+' if a['z_score'] > 0 else ''
            print(f"    {a['age_BP']:.0f} BP: δ18O = {a['value']:.2f}‰ (z = {sign}{a['z_score']:.2f})")

    # d13C analysis if available
    if has_d13C:
        d13C_data = [d for d in data if d.get('d13C') is not None]
        if d13C_data:
            print(f"\nδ13C Analysis ({len(d13C_data)} samples):")
            d13C_anomalies, d13C_mean, d13C_std = calculate_zscore_anomalies(data, 'd13C', threshold=2.0)
            print(f"  Mean: {d13C_mean:.2f}‰, Std: {d13C_std:.2f}‰")
            print(f"  Anomalies (|z| > 2): {len(d13C_anomalies)}")

    # Mg/Ca analysis if available
    MgCa_mean, MgCa_std = 0, 0
    if has_MgCa:
        MgCa_data = [d for d in data if d.get('Mg_Ca') is not None]
        if MgCa_data:
            print(f"\nMg/Ca Analysis ({len(MgCa_data)} samples):")
            MgCa_anomalies, MgCa_mean, MgCa_std = calculate_zscore_anomalies(data, 'Mg_Ca', threshold=2.0)
            print(f"  Mean: {MgCa_mean:.2f}, Std: {MgCa_std:.2f}")
            print(f"  Anomalies (|z| > 2): {len(MgCa_anomalies)}")

            if MgCa_anomalies:
                print(f"\n  Top 10 Mg/Ca Anomalies:")
                sorted_mgca = sorted(MgCa_anomalies, key=lambda x: abs(x['z_score']), reverse=True)[:10]
                for a in sorted_mgca:
                    sign = '+' if a['z_score'] > 0 else ''
                    print(f"    {a['age_BP']:.0f} BP: Mg/Ca = {a['value']:.2f} (z = {sign}{a['z_score']:.2f})")

    # Multi-proxy coincidence check
    if has_MgCa and MgCa_std > 0 and d18O_std > 0:
        print(f"\nMulti-Proxy Coincidence Check (seismic signature):")
        print(f"  Looking for -δ18O + +Mg/Ca events (deep water influx)...")

        coincident = []
        for d in data:
            d18O_val = d.get('d18O')
            MgCa_val = d.get('Mg_Ca')
            if d18O_val is not None and MgCa_val is not None:
                d18O_z = (d18O_val - d18O_mean) / d18O_std
                MgCa_z = (MgCa_val - MgCa_mean) / MgCa_std
                # Seismic signature: negative d18O AND positive Mg/Ca
                if d18O_z < -1.5 and MgCa_z > 1.5:
                    coincident.append({
                        'age_BP': d['age_BP'],
                        'd18O': d18O_val,
                        'd18O_z': d18O_z,
                        'Mg_Ca': MgCa_val,
                        'Mg_Ca_z': MgCa_z
                    })

        print(f"  Found {len(coincident)} potential seismic events")
        if coincident:
            print(f"\n  Potential Seismic Events (δ18O<-1.5σ AND Mg/Ca>+1.5σ):")
            for e in sorted(coincident, key=lambda x: x['age_BP']):
                print(f"    {e['age_BP']:.0f} BP: δ18O={e['d18O']:.2f}‰ (z={e['d18O_z']:.2f}), Mg/Ca={e['Mg_Ca']:.2f} (z=+{e['Mg_Ca_z']:.2f})")

    return d18O_anomalies

def main():
    print("="*60)
    print("PUERTO RICO SPELEOTHEM PALEOSEISMIC ANALYSIS")
    print("Caves near Puerto Rico Trench Subduction Zone")
    print("="*60)

    print("\n** TECTONIC CONTEXT **")
    print("Puerto Rico Trench: World's deepest trench in Atlantic (8,380m)")
    print("Oblique subduction of North American plate beneath Caribbean plate")
    print("Historical earthquakes: 1787 M8.1, 1867 M7.3, 1918 M7.1")
    print("Recurrence interval: ~200 years for M7+ events")

    # Analyze Perdida Cave (prehistoric)
    analyze_cave(
        "PERDIDA CAVE (entity 81, stm2)",
        "/Users/catherine/projects/quake/paleoseismic_caves/regions/caribbean/perdida_timeseries.csv",
        has_d13C=True,
        has_MgCa=False
    )

    # Analyze Larga Cave entity 812 (prehistoric with Mg/Ca)
    analyze_cave(
        "LARGA CAVE (entity 812, PR-LA-1)",
        "/Users/catherine/projects/quake/paleoseismic_caves/regions/caribbean/larga_812_complete.csv",
        has_d13C=False,
        has_MgCa=True
    )

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("""
Key Findings:
1. Both Puerto Rico caves contain PREHISTORIC records only
   - Perdida: 83,000 - 128,000 BP (Late Pleistocene)
   - Larga 812: 15,320 - 46,398 BP (Deglacial to Late Pleistocene)

2. Larga Cave has dual-proxy capability (δ18O + Mg/Ca)
   - Can apply Chiodini discrimination model
   - 2,049 δ18O measurements, 2,024 Mg/Ca measurements

3. These records could validate paleoseismic trench studies
   - Prentice et al. (2003) identified ~5,000 BP event in Septentrional Fault
   - Could cross-reference with prehistoric Puerto Rico Trench events

4. LIMITATION: No historical coverage
   - Cannot validate against known 1787, 1867, 1918 earthquakes
""")

if __name__ == "__main__":
    main()
