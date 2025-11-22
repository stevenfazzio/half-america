# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Half of America is a topology optimization experiment that creates an interactive visualization of US population distribution. Instead of simple county-level "half of America lives here" maps, this project uses Census Tract data (~73,000 tracts) with Max-Flow Min-Cut optimization to generate smooth, organic shapes controlled by a "surface tension" parameter (λ).

**Naming Convention:**
- Repository/PyPI: `half-america` (hyphenated)
- Python module: `half_america` (underscored)
- CLI command: `half-america`

## Commands

Common commands (see [README.md#usage](README.md#usage) for full list):

```bash
uv sync                              # Install dependencies
uv run pytest                        # Run tests
uv run pytest path/to/test.py -v     # Run single test
uv run pytest -m "not integration"   # Skip network-dependent tests
uv run pytest -k "dissolve"          # Run tests matching pattern
uv run ruff format src/ tests/       # Format code
uv run ruff check src/ tests/        # Lint
uv run mypy src/                     # Type check
uv run half-america                  # Run CLI
uv run half-america precompute       # Pre-compute optimization results
uv run half-america export           # Export TopoJSON files
```

## Cache Management

The `data/` directory (gitignored) contains cached data at multiple levels:

| Cache | Location | When to Clear |
|-------|----------|---------------|
| HTTP requests | `data/cache/requests_cache.sqlite` | API issues |
| TIGER shapefiles | `data/cache/raw/tiger/` | Year config change |
| Census data | `data/cache/raw/census/` | Year config change |
| Processed tracts | `data/cache/processed/*.parquet` | Source data change |
| Graph/sweep | `data/cache/processed/*.pkl` | Algorithm change |

```bash
rm -rf data/cache/                   # Clear all caches
rm -rf data/cache/processed/         # Clear processed only (keeps downloads)
```

**Force rebuild:** Use `--force` flag with CLI commands, or `force_rebuild=True` in Python API.

## Data Files

```
data/                          # Gitignored
├── cache/
│   ├── raw/
│   │   ├── tiger/             # TIGER shapefiles (*.parquet)
│   │   └── census/            # Census population (*.parquet)
│   ├── processed/             # Merged data, graphs, sweeps
│   └── requests_cache.sqlite  # HTTP cache
└── output/
    └── topojson/              # Exported results
```

Cache filenames include year keys: `{name}_{TIGER_YEAR}_{ACS_YEAR}.ext`
Year constants in `src/half_america/config.py`: `TIGER_YEAR=2024`, `ACS_YEAR=2022`

## Architecture

**Implementation Stack (from METHODOLOGY.md):**
- **Data Ingestion:** pandas, cenpy (Census API) - *implemented*
- **Spatial Logic:** geopandas, libpysal (adjacency graph building) - *implemented*
- **Optimization:** PyMaxFlow (C++ graph cuts wrapper) - *implemented*
- **Geometry Operations:** shapely, topojson - *implemented*
- **Web Frontend:** React, Mapbox GL JS - *Phase 5*

**Core Algorithm:** The optimization uses Lagrangian relaxation with binary search to find the Lagrange multiplier (μ) that satisfies the 50% population constraint. The graph construction uses s-t cut with neighborhood edges (n-links) for boundary costs and terminal edges (t-links) for area costs and population rewards.

**Key Parameters:**
- λ (lambda): User-controlled surface tension [0,1). λ≈0 minimizes area (dusty map), λ≈0.9 minimizes perimeter (smooth blobs). λ=1.0 is excluded (causes convergence failure).
- μ (mu): Lagrange multiplier tuned via binary search to hit 50% population target

## Common Gotchas

**Parameter naming:** Use `lambda_param` not `lambda` in Python code (reserved word). Use `mu` for Lagrange multiplier.

**Lambda range:** λ must be in [0, 1). λ=1.0 raises `ValueError` because it causes zero area cost and convergence failure.

**Stale caches:** If you change `TIGER_YEAR`/`ACS_YEAR` in config.py, old caches remain orphaned. Clear with `rm -rf data/cache/`.

**Imports:** Use absolute imports only: `from half_america.data import load_all_tracts`

## Documentation

- [README.md](README.md) - Project overview, installation, and usage
- [docs/API.md](docs/API.md) - Python API reference
- [METHODOLOGY.md](METHODOLOGY.md) - Mathematical formulation and algorithm details
- [ROADMAP.md](ROADMAP.md) - Implementation phases and roadmap
