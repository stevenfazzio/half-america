# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Half of America is a topology optimization experiment that creates an interactive visualization of US population distribution. Instead of simple county-level "half of America lives here" maps, this project uses Census Tract data (~73,000 tracts) with Max-Flow Min-Cut optimization to generate smooth, organic shapes controlled by a "surface tension" parameter (λ).

## Commands

```bash
# Install dependencies (uses uv)
uv sync

# Run tests
uv run pytest

# Run single test
uv run pytest tests/test_sanity.py::test_sanity -v

# Format code
uv run black src/ tests/

# Lint
uv run ruff check src/ tests/

# Type check
uv run mypy src/

# Run the CLI
uv run half-america
```

## Architecture

**Planned Implementation Stack (from METHODOLOGY.md):**
- **Data Ingestion:** pandas, cenpy (Census API)
- **Spatial Logic:** geopandas, libpysal (adjacency graph building)
- **Optimization:** PyMaxFlow (C++ graph cuts wrapper)
- **Geometry Operations:** shapely, topojson
- **Web Frontend:** React, Mapbox GL JS

**Core Algorithm:** The optimization uses Lagrangian relaxation with binary search to find the Lagrange multiplier (μ) that satisfies the 50% population constraint. The graph construction uses s-t cut with neighborhood edges (n-links) for boundary costs and terminal edges (t-links) for area costs and population rewards.

**Key Parameters:**
- λ (lambda): User-controlled surface tension [0,1]. λ≈0 minimizes area (dusty map), λ≈1 minimizes perimeter (smooth blobs)
- μ (mu): Lagrange multiplier tuned via binary search to hit 50% population target

## Documentation

- [README.md](README.md) - Project overview, installation, and usage
- [METHODOLOGY.md](METHODOLOGY.md) - Mathematical formulation and algorithm details
- [ROADMAP.md](ROADMAP.md) - Implementation phases and roadmap
