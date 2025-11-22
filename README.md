# Half of America

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An experimental data visualization exploring US population concentration. Interactive map highlighting where 50% of Americans live, with a slider to balance area minimization vs. perimeter smoothness.

> Half of America lives in a *very* small area. See for yourself.

## Background

There is a genre of viral maps that frequently circulates on the internet, typically titled "Half of the United States Lives In These Counties" ([example](https://www.businessinsider.com/half-of-the-united-states-lives-in-these-counties-2013-9)). These maps show how concentrated the US population is by selecting the most populous counties until reaching 50% of the total population.

This project evolved through several iterations:

1. **The San Bernardino Problem**: County-level maps include vast empty areas (San Bernardino County is larger than nine US states but mostly desert). Solution: use Census Tracts (~73,000 units) instead of counties (~3,100).

2. **The Dust Problem**: Census tracts created thousands of tiny disconnected regions. While technically accurate, humans struggle to visually reason about thousands of tiny specks. The map was accurate but not *compelling*.

3. **The Bridge Problem**: Minimizing region *count* (to reduce dust) created oddly-shaped regions with narrow "bridges" connecting dense areas.

4. **The Solution**: Minimize *perimeter* instead. This produces smooth, organic shapes that are easier to visually interpret while remaining accurate. Implemented via **Max-Flow Min-Cut optimization** with a user-controlled "surface tension" parameter.

## How It Works

The visualization shows how concentrated the US population is—50% of Americans live in a surprisingly small area. The challenge is presenting this in a visually compelling way.

A slider controls lambda (0 to <1):

- **lambda ~ 0**: Minimizes total area. Shows high-resolution "dusty" city centers—accurate but hard to visually process.
- **lambda ~ 0.9**: Minimizes perimeter. Creates smooth, compact blobs that are easier to reason about while still being accurate.

The slider lets you explore the tradeoff between precision and visual clarity.

Note: lambda=1.0 is mathematically degenerate and excluded from valid values. Due to computational complexity, geometries for various lambda values are pre-calculated. The web app serves as a visualizer for these pre-computed states.

See [METHODOLOGY.md](METHODOLOGY.md) for the mathematical formulation.

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
# Run the CLI
uv run half-america

# Run tests
uv run pytest

# Format code
uv run ruff format src/ tests/

# Lint
uv run ruff check src/ tests/

# Type check
uv run mypy src/

# Export TopoJSON files
uv run half-america export

# Export with options
uv run half-america export --combined      # Include combined.json
uv run half-america export --force         # Overwrite existing
```

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

# Post-process for web delivery
from half_america.postprocess import (
    dissolve_all_lambdas,
    simplify_all_lambdas,
    export_all_lambdas,
)

# Transform optimization results to web-ready TopoJSON
dissolve_results = dissolve_all_lambdas(gdf, result)
simplify_results = simplify_all_lambdas(dissolve_results)
export_results = export_all_lambdas(simplify_results, dissolve_results)
# Output: data/output/topojson/lambda_0.0.json, lambda_0.1.json, ...
```

See [METHODOLOGY.md](METHODOLOGY.md) for algorithm details.

## Project Status

**Current Phase**: Post-Processing Complete (Phase 4)

For more information:
- [ROADMAP.md](ROADMAP.md) - Implementation plan
- [METHODOLOGY.md](METHODOLOGY.md) - Mathematical details

## License

MIT License. See [LICENSE](LICENSE).

*This is a personal experimental project exploring topology optimization and cartography. Not intended as a production tool.*
