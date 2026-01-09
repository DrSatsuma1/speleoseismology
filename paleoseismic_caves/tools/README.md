# Paleoseismic Research Tools

Tools for automating paleoseismic cave research workflows.

## Setup

```bash
cd tools
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Available Tools

### 1. Calculators (`calculators.py`)

Domain-specific calculations:

```bash
# PGA attenuation
.venv/bin/python calculators.py pga --mag 6.5 --dist 50 --depth 10

# Chiodini CO2 flux model
.venv/bin/python calculators.py chiodini --mag 6.0 --dist 30

# Distance between coordinates
.venv/bin/python calculators.py haversine --lat1 44.125 --lon1 8.208 --lat2 43.7 --lon2 7.26

# Recurrence interval
.venv/bin/python calculators.py recurrence --events "1285,1394,1580,1825,1906"

# Rupture parameters
.venv/bin/python calculators.py rupture --mag 7.0
```

### 2. RAG System (`rag.py`)

Search your papers and documentation:

```bash
# Index files
.venv/bin/python rag.py index ../methodology/ --recursive
.venv/bin/python rag.py index /path/to/paper.pdf

# Search
.venv/bin/python rag.py search "Chiodini CO2 flux earthquake"

# Stats
.venv/bin/python rag.py stats
```

Currently indexed: 46 documents, 1,621 chunks.

### 3. MCP Server (`mcp_server.py`)

Provides Claude with direct tool access. To enable:

1. Copy `claude_mcp_config.json` contents to your Claude Code settings
2. Or run: `claude mcp add paleoseismic /path/to/mcp_server.py`

**Available MCP Tools:**
- `sisal_search_caves` - Search SISAL database for caves
- `sisal_get_samples` - Get measurements for a cave
- `earthquake_search` - Query USGS earthquake catalog
- `calc_pga` - PGA attenuation calculation
- `calc_chiodini` - CO2 flux perturbation
- `calc_distance` - Great-circle distance
- `calc_recurrence` - Recurrence interval stats
- `rag_search` - Search project documentation
- `rag_index` - Index new documents

## Directory Structure

```
tools/
├── .venv/              # Python 3.12 virtual environment
├── calculators.py      # Domain calculators
├── rag.py              # RAG system
├── mcp_server.py       # MCP server for Claude
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Data Locations

- **RAG Database**: `../data/rag_db/`
- **SISAL Database**: `../data/SISAL3/sisalv3_database_mysql_csv/sisalv3_csv/`
