#!/usr/bin/env python3
"""
USGS Quaternary Fault Database Gap Analysis
Newport-Inglewood-Rose Canyon Fault Zone

Identifies 85 km unmapped offshore segment between south LA Basin
and San Diego sections.

Author: Claude Code
Date: 2026-01-02
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import geopandas as gpd
import pandas as pd
from matplotlib.patches import Rectangle
from shapely.geometry import Point, LineString

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ANALYSIS_DIR = os.path.dirname(SCRIPT_DIR)
SAN_DIEGO_DIR = os.path.dirname(ANALYSIS_DIR)

USGS_DATABASE = os.path.join(SAN_DIEGO_DIR, "SHP", "Qfaults_US_Database.shp")
EARTHQUAKES = os.path.join(SAN_DIEGO_DIR, "usgs_sandiego_microseismicity_1980-2025.csv")

OUTPUT_DIR = os.path.join(ANALYSIS_DIR, "figures")
DATA_DIR = os.path.join(ANALYSIS_DIR, "data")


def load_nifz_rcfz():
    """Load all Newport-Inglewood-Rose Canyon fault sections."""
    faults = gpd.read_file(USGS_DATABASE)
    ni_rcf = faults[faults['fault_name'].str.contains(
        'Newport-Inglewood-Rose Canyon', case=False, na=False
    )]
    return ni_rcf


def analyze_sections(ni_rcf):
    """Analyze geographic distribution and gaps."""
    print("="*70)
    print("NEWPORT-INGLEWOOD-ROSE CANYON FAULT ZONE - USGS DATABASE ANALYSIS")
    print("="*70)

    sections = []
    for section_name in sorted(ni_rcf['section_na'].unique()):
        section_data = ni_rcf[ni_rcf['section_na'] == section_name]
        bounds = section_data.total_bounds

        section_info = {
            'name': section_name,
            'lat_min': bounds[1],
            'lat_max': bounds[3],
            'lon_min': bounds[0],
            'lon_max': bounds[2],
            'features': len(section_data)
        }
        sections.append(section_info)

        print(f"\n{section_name}:")
        print(f"  Latitude: {bounds[1]:.4f}°N to {bounds[3]:.4f}°N")
        print(f"  Longitude: {bounds[0]:.4f}°W to {bounds[2]:.4f}°W")
        print(f"  Features: {len(section_data)}")

    # Identify gaps
    print("\n" + "="*70)
    print("GAP ANALYSIS")
    print("="*70)

    # Sort by latitude
    sections_sorted = sorted(sections, key=lambda x: x['lat_min'])

    gaps = []
    for i in range(len(sections_sorted) - 1):
        current = sections_sorted[i]
        next_section = sections_sorted[i + 1]

        gap_size = next_section['lat_min'] - current['lat_max']

        if gap_size > 0.01:  # >1 km gap
            gap_km = gap_size * 111  # Approximate km per degree
            print(f"\nGAP DETECTED:")
            print(f"  Between: {current['name']} → {next_section['name']}")
            print(f"  Latitude range: {current['lat_max']:.4f}°N to {next_section['lat_min']:.4f}°N")
            print(f"  Size: ~{gap_km:.1f} km")

            gaps.append({
                'south_section': current['name'],
                'north_section': next_section['name'],
                'lat_south': current['lat_max'],
                'lat_north': next_section['lat_min'],
                'gap_km': gap_km
            })

    return sections, gaps


def analyze_earthquakes_in_gap(gaps):
    """Count earthquakes in unmapped gap zones."""
    eq_df = pd.read_csv(EARTHQUAKES)

    print("\n" + "="*70)
    print("MICROSEISMICITY IN GAP ZONES")
    print("="*70)

    for gap in gaps:
        in_gap = eq_df[
            (eq_df['lat'] >= gap['lat_south']) &
            (eq_df['lat'] <= gap['lat_north'])
        ]

        print(f"\n{gap['south_section']} → {gap['north_section']} gap:")
        print(f"  Earthquakes: {len(in_gap)} ({len(in_gap)/len(eq_df)*100:.1f}% of catalog)")
        if len(in_gap) > 0:
            print(f"  Magnitude range: {in_gap['magnitude'].min():.2f} - {in_gap['magnitude'].max():.2f}")
            print(f"  M≥3.0 events: {len(in_gap[in_gap['magnitude'] >= 3.0])}")
            print(f"  M≥4.0 events: {len(in_gap[in_gap['magnitude'] >= 4.0])}")

    return eq_df


def create_visualization(ni_rcf, eq_df, gaps):
    """Create publication-quality visualization of database gap."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 12))

    # Panel A: Full system map
    ax1.set_title('A) USGS Database Coverage: Newport-Inglewood-Rose Canyon Fault Zone',
                  fontweight='bold', fontsize=14)

    # Plot each section in different color
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    for i, section_name in enumerate(sorted(ni_rcf['section_na'].unique(), reverse=True)):
        section_data = ni_rcf[ni_rcf['section_na'] == section_name]
        section_data.plot(ax=ax1, color=colors[i], linewidth=2,
                         label=section_name, alpha=0.8)

    # Highlight gap zones
    for gap in gaps:
        ax1.axhspan(gap['lat_south'], gap['lat_north'],
                   color='red', alpha=0.2, zorder=0,
                   label=f"Gap: {gap['gap_km']:.0f} km" if gaps.index(gap) == 0 else "")

        # Add gap annotation
        mid_lat = (gap['lat_south'] + gap['lat_north']) / 2
        ax1.text(-118.5, mid_lat, f"GAP\n~{gap['gap_km']:.0f} km",
                ha='center', va='center', fontsize=12, fontweight='bold',
                bbox=dict(boxstyle='round', facecolor='red', alpha=0.3))

    ax1.set_xlabel('Longitude', fontsize=12)
    ax1.set_ylabel('Latitude', fontsize=12)
    ax1.legend(loc='upper left', fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(-118.6, -117.0)
    ax1.set_ylim(32.5, 34.3)

    # Panel B: Earthquakes in gap zone
    ax2.set_title('B) Microseismicity in Unmapped Zone (1980-2025)',
                  fontweight='bold', fontsize=14)

    # Plot fault sections
    for i, section_name in enumerate(sorted(ni_rcf['section_na'].unique(), reverse=True)):
        section_data = ni_rcf[ni_rcf['section_na'] == section_name]
        section_data.plot(ax=ax2, color=colors[i], linewidth=2, alpha=0.5)

    # Highlight main gap
    main_gap = max(gaps, key=lambda x: x['gap_km'])
    ax2.axhspan(main_gap['lat_south'], main_gap['lat_north'],
               color='red', alpha=0.15, zorder=0, label=f"Unmapped gap ({main_gap['gap_km']:.0f} km)")

    # Plot earthquakes
    gap_eq = eq_df[
        (eq_df['lat'] >= main_gap['lat_south']) &
        (eq_df['lat'] <= main_gap['lat_north'])
    ]
    mapped_eq = eq_df[
        (eq_df['lat'] < main_gap['lat_south']) |
        (eq_df['lat'] > main_gap['lat_north'])
    ]

    # Plot mapped zone earthquakes in gray
    ax2.scatter(mapped_eq['lon'], mapped_eq['lat'],
               c='gray', s=5, alpha=0.3, label=f'Mapped zones (n={len(mapped_eq)})')

    # Plot gap zone earthquakes colored by magnitude
    scatter = ax2.scatter(gap_eq['lon'], gap_eq['lat'],
                         c=gap_eq['magnitude'], s=gap_eq['magnitude']**2,
                         cmap='Reds', alpha=0.7, edgecolors='k', linewidth=0.3,
                         vmin=1, vmax=5, label=f'Gap zone (n={len(gap_eq)})')
    cbar = plt.colorbar(scatter, ax=ax2, label='Magnitude')

    ax2.set_xlabel('Longitude', fontsize=12)
    ax2.set_ylabel('Latitude', fontsize=12)
    ax2.legend(loc='upper left', fontsize=10)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(-118.6, -117.0)
    ax2.set_ylim(32.5, 34.3)

    plt.tight_layout()

    output_file = os.path.join(OUTPUT_DIR, 'usgs_database_gap_analysis.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nSaved: {output_file}")

    return output_file


def create_detailed_gap_map(ni_rcf, eq_df, gaps):
    """Create zoomed-in map of the main gap zone."""
    main_gap = max(gaps, key=lambda x: x['gap_km'])

    fig, ax = plt.subplots(figsize=(12, 14))
    fig.suptitle('USGS Database Gap: Offshore Newport-Inglewood-Rose Canyon Fault Zone',
                fontsize=16, fontweight='bold')

    # Get earthquakes in and around gap
    buffer = 0.3  # degrees
    gap_region_eq = eq_df[
        (eq_df['lat'] >= main_gap['lat_south'] - buffer) &
        (eq_df['lat'] <= main_gap['lat_north'] + buffer)
    ]

    gap_eq = eq_df[
        (eq_df['lat'] >= main_gap['lat_south']) &
        (eq_df['lat'] <= main_gap['lat_north'])
    ]

    # Highlight gap zone
    ax.axhspan(main_gap['lat_south'], main_gap['lat_north'],
              color='red', alpha=0.15, zorder=0)

    # Plot fault sections
    colors = {'south Los Angeles Basin section': '#ff7f0e',
              'San Diego section': '#2ca02c'}

    for section_name, color in colors.items():
        section_data = ni_rcf[ni_rcf['section_na'] == section_name]
        if len(section_data) > 0:
            section_data.plot(ax=ax, color=color, linewidth=3,
                            label=f'{section_name} (USGS)', alpha=0.8)

    # Plot all earthquakes in region
    ax.scatter(gap_region_eq['lon'], gap_region_eq['lat'],
              c='lightgray', s=10, alpha=0.4, label=f'All EQs (n={len(gap_region_eq)})')

    # Highlight gap zone earthquakes
    scatter = ax.scatter(gap_eq['lon'], gap_eq['lat'],
                        c=gap_eq['magnitude'], s=gap_eq['magnitude']**2 * 5,
                        cmap='hot_r', alpha=0.8, edgecolors='k', linewidth=0.5,
                        vmin=1, vmax=5, label=f'Gap zone EQs (n={len(gap_eq)})', zorder=5)
    cbar = plt.colorbar(scatter, ax=ax, label='Magnitude')

    # Add text annotations
    ax.text(-118.4, main_gap['lat_south'] - 0.05,
           f"{main_gap['south_section']}\n(ends {main_gap['lat_south']:.2f}°N)",
           ha='center', fontsize=11, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='orange', alpha=0.7))

    ax.text(-118.4, main_gap['lat_north'] + 0.05,
           f"{main_gap['north_section']}\n(starts {main_gap['lat_north']:.2f}°N)",
           ha='center', fontsize=11, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='green', alpha=0.7))

    mid_lat = (main_gap['lat_south'] + main_gap['lat_north']) / 2
    ax.text(-117.4, mid_lat,
           f"UNMAPPED GAP\n{main_gap['gap_km']:.0f} km\n{len(gap_eq)} earthquakes\n(1980-2025)",
           ha='center', va='center', fontsize=13, fontweight='bold',
           bbox=dict(boxstyle='round', facecolor='red', alpha=0.3))

    # Add coastline reference
    ax.axvline(-118.0, color='blue', linestyle='--', alpha=0.3, linewidth=1, label='~Coastline')

    ax.set_xlabel('Longitude', fontsize=12)
    ax.set_ylabel('Latitude', fontsize=12)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-118.6, -117.0)
    ax.set_ylim(main_gap['lat_south'] - buffer, main_gap['lat_north'] + buffer)

    plt.tight_layout()

    output_file = os.path.join(OUTPUT_DIR, 'usgs_gap_detailed.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_file}")

    return output_file


def export_gap_statistics(sections, gaps, eq_df):
    """Export detailed statistics to CSV."""
    main_gap = max(gaps, key=lambda x: x['gap_km'])

    gap_eq = eq_df[
        (eq_df['lat'] >= main_gap['lat_south']) &
        (eq_df['lat'] <= main_gap['lat_north'])
    ]

    stats = {
        'metric': [
            'Total NIFZ/RCFZ length (USGS sections)',
            'Mapped length',
            'Gap length',
            'Gap percentage',
            'Gap latitude range',
            'Total earthquakes (1980-2025)',
            'Earthquakes in gap',
            'Gap earthquake percentage',
            'M≥3.0 in gap',
            'M≥4.0 in gap',
            'Largest event in gap'
        ],
        'value': [
            '~209 km',
            f'{209 - main_gap["gap_km"]:.0f} km',
            f'{main_gap["gap_km"]:.0f} km',
            f'{main_gap["gap_km"]/209*100:.1f}%',
            f'{main_gap["lat_south"]:.2f}°N to {main_gap["lat_north"]:.2f}°N',
            len(eq_df),
            len(gap_eq),
            f'{len(gap_eq)/len(eq_df)*100:.1f}%',
            len(gap_eq[gap_eq['magnitude'] >= 3.0]),
            len(gap_eq[gap_eq['magnitude'] >= 4.0]),
            f'M{gap_eq["magnitude"].max():.2f}' if len(gap_eq) > 0 else 'N/A'
        ]
    }

    stats_df = pd.DataFrame(stats)
    stats_file = os.path.join(DATA_DIR, 'gap_statistics.csv')
    stats_df.to_csv(stats_file, index=False)
    print(f"\nSaved: {stats_file}")

    # Print summary table
    print("\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70)
    for _, row in stats_df.iterrows():
        print(f"{row['metric']}: {row['value']}")

    return stats_df


def main():
    """Main analysis pipeline."""
    # Load data
    print("Loading USGS Quaternary Fault Database...")
    ni_rcf = load_nifz_rcfz()

    # Analyze sections and gaps
    sections, gaps = analyze_sections(ni_rcf)

    # Load and analyze earthquakes
    eq_df = analyze_earthquakes_in_gap(gaps)

    # Create visualizations
    print("\nCreating visualizations...")
    create_visualization(ni_rcf, eq_df, gaps)
    create_detailed_gap_map(ni_rcf, eq_df, gaps)

    # Export statistics
    export_gap_statistics(sections, gaps, eq_df)

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print(f"Output directory: {ANALYSIS_DIR}")


if __name__ == '__main__':
    main()
