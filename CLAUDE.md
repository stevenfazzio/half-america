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
uv run black src/ tests/             # Format code
uv run ruff check src/ tests/        # Lint
uv run mypy src/                     # Type check
uv run half-america                  # Run CLI
uv run half-america precompute       # Pre-compute optimization results
```

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

## Documentation

- [README.md](README.md) - Project overview, installation, and usage
- [docs/API.md](docs/API.md) - Python API reference
- [METHODOLOGY.md](METHODOLOGY.md) - Mathematical formulation and algorithm details
- [ROADMAP.md](ROADMAP.md) - Implementation phases and roadmap
