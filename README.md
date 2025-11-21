# Half of America

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A topology optimization experiment that treats the 'Half of America' map as a fluid, replacing dusty dots with smooth, organic population blobs.

> Where does half of America *really* live?

## The Problem

There is a genre of viral maps that frequently circulates on the internet, typically titled "Half of the United States Lives In These Counties" ([example](https://www.businessinsider.com/half-of-the-united-states-lives-in-these-counties-2013-9)). These maps illustrate the extreme geographic concentration of the US population using a simple algorithm: rank counties by population and select the top N until exceeding 50% of the total.

Traditional approaches have two issues:

1. **The San Bernardino Problem**: County boundaries include vast empty areas (San Bernardino County is larger than nine US states but mostly desert)
2. **The Dust Problem**: Using smaller units creates thousands of disconnected specks that fail as visualization

This project solves both using **Max-Flow Min-Cut optimization** with a user-controlled "surface tension" parameter.

## How It Works

A slider controls lambda (0 to <1):

- **lambda ~ 0**: Minimizes area, showing high-resolution "dusty" city centers
- **lambda ~ 0.9**: Minimizes perimeter, creating smooth, compact blobs

Note: lambda=1.0 is mathematically degenerate and excluded from valid values.

**Note**: Due to computational complexity, geometries for various lambda values are pre-calculated. The web app serves as a visualizer for these pre-computed states.

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
```

See [METHODOLOGY.md](METHODOLOGY.md) for algorithm details.

## Project Status

**Current Phase**: Optimization Engine Complete (Phase 3)

For more information:
- [ROADMAP.md](ROADMAP.md) - Implementation plan
- [METHODOLOGY.md](METHODOLOGY.md) - Mathematical details

## License

MIT License. See [LICENSE](LICENSE).

*This is a personal experimental project exploring topology optimization and cartography. Not intended as a production tool.*
