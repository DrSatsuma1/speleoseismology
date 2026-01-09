#!/usr/bin/env python3
"""
MCP Server for Paleoseismic Research Tools.

This server provides Claude with direct access to:
- SISAL database queries
- Earthquake catalog searches (USGS)
- Domain calculators (PGA, Chiodini, etc.)
- RAG search over project documents

To use with Claude Code, add to settings:
{
  "mcpServers": {
    "paleoseismic": {
      "command": "python3",
      "args": ["/path/to/tools/mcp_server.py"],
      "env": {}
    }
  }
}
"""

import json
import os
import sys
from pathlib import Path
from typing import Any
import csv
from datetime import datetime

# Add tools directory to path
TOOLS_DIR = Path(__file__).parent
sys.path.insert(0, str(TOOLS_DIR))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import our modules
import calculators
from rag import RAGDatabase
import fault_databases
import volcanic_databases

# =============================================================================
# SISAL DATABASE
# =============================================================================

SISAL_PATH = Path(__file__).parent.parent / "data" / "SISAL3" / "sisalv3_database_mysql_csv" / "sisalv3_csv"


def query_sisal_entities(region: str = None, min_samples: int = 100) -> list[dict]:
    """Query SISAL entities (caves) with optional filtering."""
    entity_file = SISAL_PATH / "entity.csv"
    site_file = SISAL_PATH / "site.csv"
    sample_file = SISAL_PATH / "sample.csv"

    if not entity_file.exists():
        return [{"error": f"SISAL not found at {SISAL_PATH}"}]

    # Load sites for location data
    sites = {}
    with open(site_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sites[row['site_id']] = {
                'name': row['site_name'],
                'lat': float(row['latitude']) if row['latitude'] else None,
                'lon': float(row['longitude']) if row['longitude'] else None,
                'country': row.get('country', '')
            }

    # Count samples per entity
    sample_counts = {}
    with open(sample_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            eid = row['entity_id']
            sample_counts[eid] = sample_counts.get(eid, 0) + 1

    # Load entities
    results = []
    with open(entity_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            site = sites.get(row['site_id'], {})
            count = sample_counts.get(row['entity_id'], 0)

            if count < min_samples:
                continue

            if region:
                country = site.get('country', '').lower()
                name = site.get('name', '').lower()
                if region.lower() not in country and region.lower() not in name:
                    continue

            results.append({
                'entity_id': row['entity_id'],
                'entity_name': row['entity_name'],
                'site_name': site.get('name', ''),
                'country': site.get('country', ''),
                'lat': site.get('lat'),
                'lon': site.get('lon'),
                'sample_count': count
            })

    return sorted(results, key=lambda x: -x['sample_count'])[:50]


def query_sisal_samples(entity_id: str, proxy: str = 'd18O_measurement') -> list[dict]:
    """Get samples for a specific entity."""
    sample_file = SISAL_PATH / "sample.csv"
    d18o_file = SISAL_PATH / "d18o.csv"

    if not sample_file.exists():
        return [{"error": "SISAL not found"}]

    # Load d18O data
    d18o_data = {}
    if d18o_file.exists():
        with open(d18o_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                sid = row['sample_id']
                d18o_data[sid] = float(row['d18O_measurement']) if row['d18O_measurement'] else None

    # Load samples
    results = []
    with open(sample_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['entity_id'] != entity_id:
                continue

            sample_id = row['sample_id']
            results.append({
                'sample_id': sample_id,
                'depth_mm': float(row['depth_sample']) if row.get('depth_sample') else None,
                'age_bp': float(row['interp_age']) if row.get('interp_age') else None,
                'd18O': d18o_data.get(sample_id)
            })

    return sorted(results, key=lambda x: x.get('age_bp') or 0)


# =============================================================================
# EARTHQUAKE CATALOG (USGS)
# =============================================================================

def query_usgs_earthquakes(
    lat: float, lon: float, radius_km: float = 100,
    start_date: str = "2000-01-01", end_date: str = None,
    min_magnitude: float = 4.0
) -> list[dict]:
    """Query USGS earthquake catalog."""
    import urllib.request
    import urllib.parse

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    params = {
        'format': 'geojson',
        'latitude': lat,
        'longitude': lon,
        'maxradiuskm': radius_km,
        'starttime': start_date,
        'endtime': end_date,
        'minmagnitude': min_magnitude,
        'eventtype': 'earthquake',  # Filter out explosions, quarry blasts, etc.
        'orderby': 'time'
    }

    url = "https://earthquake.usgs.gov/fdsnws/event/1/query?" + urllib.parse.urlencode(params)

    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode())
    except Exception as e:
        return [{"error": str(e)}]

    results = []
    for feature in data.get('features', []):
        props = feature['properties']
        coords = feature['geometry']['coordinates']

        results.append({
            'id': feature['id'],
            'time': datetime.fromtimestamp(props['time']/1000).isoformat(),
            'magnitude': props['mag'],
            'mag_type': props['magType'],
            'place': props['place'],
            'depth_km': coords[2],
            'lat': coords[1],
            'lon': coords[0]
        })

    return results


# =============================================================================
# MCP SERVER
# =============================================================================

# Initialize server
server = Server("paleoseismic-tools")

# Initialize RAG (lazily)
_rag_db = None

def get_rag():
    global _rag_db
    if _rag_db is None:
        _rag_db = RAGDatabase()
    return _rag_db


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="sisal_search_caves",
            description="Search SISAL database for caves/speleothems. Filter by region (country/name) and minimum sample count.",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {"type": "string", "description": "Filter by region/country name (e.g., 'Italy', 'Belize')"},
                    "min_samples": {"type": "integer", "description": "Minimum number of samples (default 100)", "default": 100}
                }
            }
        ),
        Tool(
            name="sisal_get_samples",
            description="Get all samples (measurements) for a specific SISAL entity (cave/stalagmite). Returns depth, age, and d18O values.",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "SISAL entity ID"}
                },
                "required": ["entity_id"]
            }
        ),
        Tool(
            name="earthquake_search",
            description="Search USGS earthquake catalog for events near a location.",
            inputSchema={
                "type": "object",
                "properties": {
                    "lat": {"type": "number", "description": "Latitude"},
                    "lon": {"type": "number", "description": "Longitude"},
                    "radius_km": {"type": "number", "description": "Search radius in km (default 100)", "default": 100},
                    "start_date": {"type": "string", "description": "Start date YYYY-MM-DD (default 2000-01-01)"},
                    "end_date": {"type": "string", "description": "End date YYYY-MM-DD (default today)"},
                    "min_magnitude": {"type": "number", "description": "Minimum magnitude (default 4.0)", "default": 4.0}
                },
                "required": ["lat", "lon"]
            }
        ),
        Tool(
            name="calc_pga",
            description="Calculate Peak Ground Acceleration using attenuation model.",
            inputSchema={
                "type": "object",
                "properties": {
                    "magnitude": {"type": "number", "description": "Earthquake magnitude"},
                    "distance_km": {"type": "number", "description": "Distance from epicenter in km"},
                    "depth_km": {"type": "number", "description": "Focal depth in km (default 10)", "default": 10},
                    "model": {"type": "string", "enum": ["bindi2011", "boore2014", "akkar2014", "simple"], "default": "bindi2011"}
                },
                "required": ["magnitude", "distance_km"]
            }
        ),
        Tool(
            name="calc_chiodini",
            description="Calculate CO2 flux perturbation from earthquake using Chiodini model.",
            inputSchema={
                "type": "object",
                "properties": {
                    "magnitude": {"type": "number", "description": "Earthquake magnitude"},
                    "distance_km": {"type": "number", "description": "Distance to cave in km"}
                },
                "required": ["magnitude", "distance_km"]
            }
        ),
        Tool(
            name="calc_distance",
            description="Calculate great-circle distance between two coordinates.",
            inputSchema={
                "type": "object",
                "properties": {
                    "lat1": {"type": "number"},
                    "lon1": {"type": "number"},
                    "lat2": {"type": "number"},
                    "lon2": {"type": "number"}
                },
                "required": ["lat1", "lon1", "lat2", "lon2"]
            }
        ),
        Tool(
            name="calc_recurrence",
            description="Calculate earthquake recurrence interval from event dates.",
            inputSchema={
                "type": "object",
                "properties": {
                    "events": {"type": "array", "items": {"type": "number"}, "description": "List of event years (CE)"}
                },
                "required": ["events"]
            }
        ),
        Tool(
            name="calc_energy",
            description="Calculate seismic energy density using Wang & Manga (2010) formula. Used to predict groundwater responses.",
            inputSchema={
                "type": "object",
                "properties": {
                    "magnitude": {"type": "number", "description": "Earthquake magnitude"},
                    "distance_km": {"type": "number", "description": "Distance from epicenter in km"},
                    "connectivity": {"type": "number", "description": "Aquifer connectivity coefficient (0-1, default 1.0)", "default": 1.0}
                },
                "required": ["magnitude", "distance_km"]
            }
        ),
        Tool(
            name="calc_connectivity",
            description="Estimate aquifer connectivity coefficient based on fault type, geology, and distance. Developed to explain the Yok Balum Ridley Paradox.",
            inputSchema={
                "type": "object",
                "properties": {
                    "fault_type": {
                        "type": "string",
                        "enum": ["offshore_subduction", "offshore_transform", "onland_strike_slip", "onland_normal", "onland_thrust", "local_karst"],
                        "description": "Type of fault mechanism"
                    },
                    "geology": {
                        "type": "string",
                        "enum": ["sedimentary_basin", "crystalline", "fractured", "karst", "same_aquifer"],
                        "description": "Rock type between fault and cave"
                    },
                    "distance_km": {"type": "number", "description": "Distance from fault to cave in km"},
                    "fault_intersects_aquifer": {"type": "boolean", "description": "Does fault directly cut through the aquifer?", "default": False}
                },
                "required": ["fault_type", "geology", "distance_km"]
            }
        ),
        Tool(
            name="calc_pore_pressure",
            description="Calculate pore pressure perturbation from earthquake using Skempton model.",
            inputSchema={
                "type": "object",
                "properties": {
                    "magnitude": {"type": "number", "description": "Earthquake magnitude"},
                    "distance_km": {"type": "number", "description": "Distance from fault in km"},
                    "skempton_b": {"type": "number", "description": "Skempton B coefficient (0.5-1.0, default 0.7)", "default": 0.7}
                },
                "required": ["magnitude", "distance_km"]
            }
        ),
        Tool(
            name="rag_search",
            description="Search project documentation and papers for relevant information.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "top_k": {"type": "integer", "description": "Number of results (default 5)", "default": 5}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="rag_index",
            description="Index a new document (PDF or markdown) into the RAG database.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to file to index"}
                },
                "required": ["file_path"]
            }
        ),
        # Fault Database Tools
        Tool(
            name="search_usgs_faults",
            description="Search USGS Quaternary Fault Database for mapped faults near a location. Note: USGS has 9-27 year lag.",
            inputSchema={
                "type": "object",
                "properties": {
                    "lat": {"type": "number", "description": "Latitude"},
                    "lon": {"type": "number", "description": "Longitude"},
                    "radius_km": {"type": "number", "description": "Search radius in km (default 50)", "default": 50}
                },
                "required": ["lat", "lon"]
            }
        ),
        Tool(
            name="search_gem_faults",
            description="Search GEM Global Active Faults Database. Requires local GeoJSON data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "lat": {"type": "number", "description": "Latitude"},
                    "lon": {"type": "number", "description": "Longitude"},
                    "radius_km": {"type": "number", "description": "Search radius in km (default 50)", "default": 50}
                },
                "required": ["lat", "lon"]
            }
        ),
        Tool(
            name="search_diss_sources",
            description="Search DISS v3.3.1 (Italy) for seismogenic sources near a location.",
            inputSchema={
                "type": "object",
                "properties": {
                    "lat": {"type": "number", "description": "Latitude (should be in Italy: 35-47°N)"},
                    "lon": {"type": "number", "description": "Longitude (should be in Italy: 6-19°E)"},
                    "radius_km": {"type": "number", "description": "Search radius in km (default 50)", "default": 50}
                },
                "required": ["lat", "lon"]
            }
        ),
        Tool(
            name="check_fault_proximity",
            description="Check ALL fault databases for mapped faults near a location. Use this to verify dark earthquake candidates. Returns whether location has mapped faults and confidence assessment.",
            inputSchema={
                "type": "object",
                "properties": {
                    "lat": {"type": "number", "description": "Latitude"},
                    "lon": {"type": "number", "description": "Longitude"},
                    "radius_km": {"type": "number", "description": "Search radius in km (default 50)", "default": 50}
                },
                "required": ["lat", "lon"]
            }
        ),
        # Volcanic Database Tools
        Tool(
            name="search_gvp_eruptions",
            description="Search Smithsonian Global Volcanism Program for eruptions in time window.",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_year": {"type": "integer", "description": "Start year (CE, negative for BCE)"},
                    "end_year": {"type": "integer", "description": "End year (CE)"},
                    "vei_min": {"type": "integer", "description": "Minimum VEI (default 4)", "default": 4}
                },
                "required": ["start_year", "end_year"]
            }
        ),
        Tool(
            name="search_evolv2k",
            description="Search eVolv2k volcanic forcing database (Toohey & Sigl 2017) for sulfur injection events.",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_year": {"type": "integer", "description": "Start year (CE, negative for BCE)"},
                    "end_year": {"type": "integer", "description": "End year (CE)"},
                    "vssi_min": {"type": "number", "description": "Minimum VSSI in Tg S (default 5.0)", "default": 5.0}
                },
                "required": ["start_year", "end_year"]
            }
        ),
        Tool(
            name="check_volcanic_activity",
            description="Check for volcanic activity that could cause false positives in speleothem anomalies. Use before attributing anomaly to earthquake.",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_year": {"type": "integer", "description": "Start year (CE)"},
                    "end_year": {"type": "integer", "description": "End year (CE)"},
                    "cave_lat": {"type": "number", "description": "Cave latitude (optional)"},
                    "cave_lon": {"type": "number", "description": "Cave longitude (optional)"}
                },
                "required": ["start_year", "end_year"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""

    if name == "sisal_search_caves":
        results = query_sisal_entities(
            region=arguments.get("region"),
            min_samples=arguments.get("min_samples", 100)
        )
        return [TextContent(type="text", text=json.dumps(results, indent=2))]

    elif name == "sisal_get_samples":
        results = query_sisal_samples(arguments["entity_id"])
        return [TextContent(type="text", text=json.dumps(results[:100], indent=2))]  # Limit output

    elif name == "earthquake_search":
        results = query_usgs_earthquakes(
            lat=arguments["lat"],
            lon=arguments["lon"],
            radius_km=arguments.get("radius_km", 100),
            start_date=arguments.get("start_date", "2000-01-01"),
            end_date=arguments.get("end_date"),
            min_magnitude=arguments.get("min_magnitude", 4.0)
        )
        return [TextContent(type="text", text=json.dumps(results, indent=2))]

    elif name == "calc_pga":
        result = calculators.pga_attenuation(
            magnitude=arguments["magnitude"],
            distance_km=arguments["distance_km"],
            depth_km=arguments.get("depth_km", 10),
            model=arguments.get("model", "bindi2011")
        )
        output = {
            "pga_g": round(result.pga_g, 4),
            "pga_cm_s2": round(result.pga_cm_s2, 1),
            "mmi": result.mmi,
            "model": result.model,
            "sigma": result.sigma
        }
        return [TextContent(type="text", text=json.dumps(output, indent=2))]

    elif name == "calc_chiodini":
        result = calculators.chiodini_co2_flux(
            magnitude=arguments["magnitude"],
            distance_km=arguments["distance_km"]
        )
        output = {
            "flux_ratio": round(result.flux_ratio, 2),
            "perturbation_pct": round(result.perturbation_pct, 1),
            "duration_years": round(result.duration_years, 1),
            "detectable": result.detectable
        }
        return [TextContent(type="text", text=json.dumps(output, indent=2))]

    elif name == "calc_distance":
        dist = calculators.haversine(
            arguments["lat1"], arguments["lon1"],
            arguments["lat2"], arguments["lon2"]
        )
        bearing = calculators.bearing(
            arguments["lat1"], arguments["lon1"],
            arguments["lat2"], arguments["lon2"]
        )
        output = {
            "distance_km": round(dist, 1),
            "bearing_deg": round(bearing, 1)
        }
        return [TextContent(type="text", text=json.dumps(output, indent=2))]

    elif name == "calc_recurrence":
        mean_int, std_int, intervals = calculators.recurrence_interval(arguments["events"])
        last_event = max(arguments["events"])
        years_since = 2025 - last_event
        output = {
            "events": sorted(arguments["events"]),
            "intervals": intervals,
            "mean_recurrence": round(mean_int, 1),
            "std_recurrence": round(std_int, 1),
            "years_since_last": years_since,
            "percent_of_cycle": round(100 * years_since / mean_int, 0) if mean_int > 0 else None
        }
        return [TextContent(type="text", text=json.dumps(output, indent=2))]

    elif name == "calc_energy":
        result = calculators.seismic_energy_density(
            magnitude=arguments["magnitude"],
            distance_km=arguments["distance_km"],
            connectivity=arguments.get("connectivity", 1.0)
        )
        max_dist = calculators.detection_distance_limit(
            arguments["magnitude"],
            arguments.get("connectivity", 1.0)
        )
        output = {
            "raw_energy_jm3": result.raw_energy_jm3,
            "effective_energy_jm3": result.effective_energy_jm3,
            "connectivity": result.connectivity,
            "threshold_jm3": result.threshold_jm3,
            "threshold_exceeded": result.threshold_exceeded,
            "ratio_to_threshold": round(result.ratio_to_threshold, 1),
            "max_detection_distance_km": round(max_dist, 0)
        }
        return [TextContent(type="text", text=json.dumps(output, indent=2))]

    elif name == "calc_connectivity":
        result = calculators.aquifer_connectivity(
            fault_type=arguments["fault_type"],
            geology=arguments["geology"],
            distance_km=arguments["distance_km"],
            fault_intersects_aquifer=arguments.get("fault_intersects_aquifer", False)
        )
        output = {
            "connectivity": round(result.connectivity, 2),
            "fault_factor": round(result.fault_factor, 2),
            "geology_factor": round(result.geology_factor, 2),
            "distance_factor": round(result.distance_factor, 2),
            "confidence": result.confidence,
            "explanation": result.explanation
        }
        return [TextContent(type="text", text=json.dumps(output, indent=2))]

    elif name == "calc_pore_pressure":
        result = calculators.pore_pressure_perturbation(
            magnitude=arguments["magnitude"],
            distance_km=arguments["distance_km"],
            skempton_b=arguments.get("skempton_b", 0.7)
        )
        output = {
            "delta_p_kpa": round(result.delta_p_kpa, 3),
            "delta_p_bar": round(result.delta_p_bar, 4),
            "static_stress_pa": result.static_stress_pa,
            "skempton_b": result.skempton_b,
            "detectable": result.detectable
        }
        return [TextContent(type="text", text=json.dumps(output, indent=2))]

    elif name == "rag_search":
        rag = get_rag()
        results = rag.search(
            query=arguments["query"],
            top_k=arguments.get("top_k", 5)
        )
        output = []
        for r in results:
            output.append({
                "source": r["source"],
                "page": r["page"],
                "similarity": round(r["similarity"], 2),
                "text": r["text"][:500] + "..." if len(r["text"]) > 500 else r["text"]
            })
        return [TextContent(type="text", text=json.dumps(output, indent=2))]

    elif name == "rag_index":
        rag = get_rag()
        try:
            chunks = rag.index_document(Path(arguments["file_path"]))
            return [TextContent(type="text", text=f"Indexed {chunks} chunks from {arguments['file_path']}")]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {e}")]

    # Fault Database Tools
    elif name == "search_usgs_faults":
        faults = fault_databases.search_usgs_faults(
            lat=arguments["lat"],
            lon=arguments["lon"],
            radius_km=arguments.get("radius_km", 50)
        )
        output = [{
            "name": f.name,
            "database": f.database,
            "distance_km": f.distance_km,
            "slip_rate_mm_yr": f.slip_rate_mm_yr,
            "slip_sense": f.slip_sense,
            "age": f.age
        } for f in faults]
        return [TextContent(type="text", text=json.dumps(output, indent=2))]

    elif name == "search_gem_faults":
        faults = fault_databases.search_gem_faults(
            lat=arguments["lat"],
            lon=arguments["lon"],
            radius_km=arguments.get("radius_km", 50)
        )
        output = [{
            "name": f.name,
            "database": f.database,
            "distance_km": f.distance_km,
            "slip_rate_mm_yr": f.slip_rate_mm_yr,
            "slip_sense": f.slip_sense,
            "length_km": f.length_km
        } for f in faults]
        return [TextContent(type="text", text=json.dumps(output, indent=2))]

    elif name == "search_diss_sources":
        faults = fault_databases.search_diss_sources(
            lat=arguments["lat"],
            lon=arguments["lon"],
            radius_km=arguments.get("radius_km", 50)
        )
        output = [{
            "name": f.name,
            "database": f.database,
            "distance_km": f.distance_km,
            "max_magnitude": f.max_magnitude,
            "slip_sense": f.slip_sense,
            "recurrence_yr": f.recurrence_yr,
            "dip": f.dip,
            "rake": f.rake
        } for f in faults]
        return [TextContent(type="text", text=json.dumps(output, indent=2))]

    elif name == "check_fault_proximity":
        result = fault_databases.check_fault_proximity(
            lat=arguments["lat"],
            lon=arguments["lon"],
            radius_km=arguments.get("radius_km", 50)
        )
        output = {
            "has_mapped_fault": result.has_mapped_fault,
            "is_dark_candidate": result.is_dark_candidate,
            "confidence": result.confidence,
            "databases_checked": result.databases_checked,
            "distance_km": result.distance_km,
            "nearest_fault": {
                "name": result.nearest_fault.name,
                "database": result.nearest_fault.database,
                "distance_km": result.nearest_fault.distance_km,
                "slip_sense": result.nearest_fault.slip_sense
            } if result.nearest_fault else None,
            "faults_count": len(result.faults_within_radius),
            "notes": result.notes
        }
        return [TextContent(type="text", text=json.dumps(output, indent=2))]

    # Volcanic Database Tools
    elif name == "search_gvp_eruptions":
        eruptions = volcanic_databases.search_gvp_eruptions(
            start_year=arguments["start_year"],
            end_year=arguments["end_year"],
            vei_min=arguments.get("vei_min", 4)
        )
        output = [{
            "volcano_name": e.volcano_name,
            "year": e.start_year,
            "vei": e.vei,
            "country": e.country,
            "lat": e.lat,
            "lon": e.lon
        } for e in eruptions]
        return [TextContent(type="text", text=json.dumps(output, indent=2))]

    elif name == "search_evolv2k":
        events = volcanic_databases.search_evolv2k(
            start_year=arguments["start_year"],
            end_year=arguments["end_year"],
            vssi_min=arguments.get("vssi_min", 5.0)
        )
        output = [{
            "year": e.year,
            "vssi_tg_s": e.vssi,
            "eruption_name": e.eruption_name,
            "hemisphere": e.hemisphere,
            "rank": e.rank,
            "lat": e.lat
        } for e in events]
        return [TextContent(type="text", text=json.dumps(output, indent=2))]

    elif name == "check_volcanic_activity":
        result = volcanic_databases.check_volcanic_activity(
            start_year=arguments["start_year"],
            end_year=arguments["end_year"],
            cave_lat=arguments.get("cave_lat"),
            cave_lon=arguments.get("cave_lon")
        )
        output = {
            "has_major_eruption": result.has_major_eruption,
            "is_volcanic_false_positive_likely": result.is_volcanic_false_positive_likely,
            "confidence": result.confidence,
            "max_vei": result.max_vei,
            "max_vssi_tg_s": result.max_vssi,
            "eruptions_count": len(result.eruptions),
            "forcing_events_count": len(result.forcing_events),
            "forcing_events": [{
                "year": f.year,
                "vssi": f.vssi,
                "name": f.eruption_name,
                "rank": f.rank
            } for f in result.forcing_events[:5]],  # Top 5
            "notes": result.notes
        }
        return [TextContent(type="text", text=json.dumps(output, indent=2))]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
