# Half of America

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An exploration of max-flow min-cut optimization applied to cartographic data visualization. This project introduces an interactive "surface tension" parameter (λ) that controls the tradeoff between area minimization and perimeter smoothness when selecting census tracts, producing smooth organic boundaries for population concentration maps.

**[View the Live Demo →](https://stevenfazzio.github.io/half-america)**

> Half of America lives in a surprisingly small area. The slider lets you explore how balancing precision vs. visual clarity affects the result.

## Background

There is a genre of viral maps that frequently circulates on the internet, typically titled "Half of the United States Lives In These Counties" ([example](https://www.businessinsider.com/half-of-the-united-states-lives-in-these-counties-2013-9)). These maps show how concentrated the US population is by selecting the most populous counties until reaching 50% of the total population.

This project evolved through several iterations:

1. **The San Bernardino Problem**: County-level maps include vast empty areas (San Bernardino County is larger than nine US states but mostly desert). Solution: use Census Tracts (~73,000 units) instead of counties (~3,100).

2. **The Dust Problem**: Census tracts created thousands of tiny disconnected regions. While technically accurate, humans struggle to visually reason about thousands of tiny specks. The map was accurate but not *compelling*.

3. **The Bridge Problem**: Minimizing region *count* (to reduce dust) created oddly-shaped regions with narrow "bridges" connecting dense areas.

4. **The Solution**: Minimize *perimeter* instead. This produces smooth, organic shapes that are easier to visually interpret while remaining accurate. Implemented via **Max-Flow Min-Cut optimization** with a user-controlled "surface tension" parameter.

## How It Works

This project treats census tract selection as a graph optimization problem. Given ~73,000 census tracts and their spatial adjacencies, we use **max-flow min-cut** to find the optimal 50% population subset while balancing two competing objectives:

1. **Minimize area** (precision): Select the smallest possible land area
2. **Minimize perimeter** (smoothness): Create smooth, organic boundaries

The interactive slider controls lambda (λ), the "surface tension" parameter (0 to <1):

- **λ ≈ 0**: Prioritizes area minimization. Produces high-resolution "dusty" city centers—accurate but hard to visually process.
- **λ ≈ 0.9**: Prioritizes perimeter minimization. Creates smooth, compact regions that are easier to reason about while remaining accurate.

The result reveals surprising population concentration: **50% of Americans live in a very small fraction of the country's land area**. The exact percentage depends on your parameter choice—prioritizing precision produces smaller areas, while prioritizing smoothness creates larger, more cohesive regions.

**Technical Note**: λ=1.0 is mathematically degenerate and excluded. Due to computational complexity, geometries for various lambda values are pre-calculated offline; the web app visualizes these pre-computed states.

See [METHODOLOGY.md](METHODOLOGY.md) for the mathematical formulation and algorithm details.

## Installation

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone <repo-url>
cd half_america
uv sync
```

### Census API Key

The data pipeline requires a Census API key:

1. Get a free key from https://api.census.gov/data/key_signup.html
2. Create your environment file:
   ```bash
   cp .env.example .env
   # Add your CENSUS_API_KEY to .env
   ```

## Usage

```bash
# Pre-compute optimization results for all lambda values
uv run half-america precompute

# Precompute options
uv run half-america precompute --force          # Rebuild cache
uv run half-america precompute --lambda-step 0.05  # Finer granularity

# Export TopoJSON files
uv run half-america export

# Export options
uv run half-america export --combined      # Include combined.json
uv run half-america export --force         # Overwrite existing
```

## Development

```bash
# Run tests
uv run pytest

# Skip network-dependent tests
uv run pytest -m "not integration"

# Run tests matching pattern
uv run pytest -k "dissolve"

# Format code
uv run ruff format src/ tests/

# Lint
uv run ruff check src/ tests/

# Type check
uv run mypy src/
```

### Cache Management

Data is cached in `data/cache/`. Clear with `rm -rf data/cache/` if you encounter stale data or change year configurations in `src/half_america/config.py`.

### Frontend

```bash
cd web
npm install        # Install dependencies
npm run dev        # Start dev server (localhost:5173)
npm run build      # Production build
npm run preview    # Preview production build
```

The frontend is built with React + Vite + MapLibre GL JS + deck.gl. No API keys required.

## API Reference

For complete API documentation, see [docs/API.md](docs/API.md).

### Quick Start

```python
from half_america.data import load_all_tracts
from half_america.graph import load_graph_data
from half_america.optimization import sweep_lambda

# Load Census Tract data (~73,000 tracts)
gdf = load_all_tracts()

# Build spatial adjacency graph
graph_data = load_graph_data(gdf)

# Run optimization across lambda values
result = sweep_lambda(graph_data)

# Check results
for lambda_val, lambda_result in result.results.items():
    opt = lambda_result.search_result.result
    print(f"lambda={lambda_val:.1f}: {opt.population_fraction:.2%} selected")
```

See [docs/API.md](docs/API.md) for post-processing (dissolve, simplify, export) and the full API reference.

## Project Status

**Current Phase**: Web Frontend Complete (Phase 5)

The interactive visualization is live at https://stevenfazzio.github.io/half-america

For more information:
- [ROADMAP.md](ROADMAP.md) - Implementation plan and future enhancements
- [METHODOLOGY.md](METHODOLOGY.md) - Mathematical details

## License

MIT License. See [LICENSE](LICENSE).

*This is a personal experimental project exploring topology optimization and cartography. Not intended as a production tool.*
