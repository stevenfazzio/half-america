# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Half of America is a portfolio project exploring the application of max-flow min-cut optimization to cartographic data visualization. It produces an interactive map where users control a "surface tension" parameter (λ) to balance area minimization vs. perimeter smoothness when selecting census tracts, revealing surprising population concentration across the United States.

**Portfolio Value:**
This project showcases:
- Graph optimization applied to spatial problems (operations research)
- Interactive parameter exploration (computational cartography)
- Full-stack implementation from data pipeline to web visualization

**Project Goals:**
- Demonstrate methodological exploration: applying optimization techniques to geographic data
- Create compelling, interactive visualization (not just static analysis)
- Showcase end-to-end data science skills for portfolio purposes

The implementation uses Census Tract data (~73,000 tracts) with Max-Flow Min-Cut optimization to generate smooth, organic shapes controlled by a "surface tension" parameter (λ).

**Project Evolution:**
The approach evolved through iteration:
1. County maps had the "San Bernardino Problem" (empty areas included)
2. Census tracts created "dust" (too many tiny regions to reason about)
3. Minimizing region count created "bridges" (narrow connections)
4. Minimizing perimeter produces smooth, compelling shapes

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

## Frontend Development

```bash
cd web
npm install                          # Install dependencies
npm run dev                          # Start dev server (localhost:5173)
npm run build                        # Production build
npm run preview                      # Preview production build
```

**Stack**: React + Vite + MapLibre GL JS + deck.gl + KaTeX. No API keys required.

**Live Site**: https://stevenfazzio.github.io/half-america

**Navigation**: The app uses hash-based routing (`#map`, `#story`, `#method`) with three tabs. The Map tab uses a KeepMounted pattern to preserve WebGL state when switching tabs.

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
- **Web Frontend:** React, MapLibre GL JS (basemap), deck.gl (data visualization) - *implemented*

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
- [METHODOLOGY.md](METHODOLOGY.md) - Mathematical formulation and algorithm details (also rendered in web app's Method tab via react-markdown)
- [ROADMAP.md](ROADMAP.md) - Implementation phases and roadmap
- [docs/archive/tab_strategy.md](docs/archive/tab_strategy.md) - Tab structure design rationale (archived)
