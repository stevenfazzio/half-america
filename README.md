# Half of America

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A topology optimization experiment visualizing US population distribution with smooth, organic shapes instead of dusty dots or blocky counties.

> Where does half of America *really* live?

## Background

There is a genre of viral maps that frequently circulates on the internet, typically titled "Half of the United States Lives In These Counties" ([example](https://www.businessinsider.com/half-of-the-united-states-lives-in-these-counties-2013-9)). These maps illustrate the extreme geographic concentration of the US population using a simple algorithm: rank counties by population and select the top N until exceeding 50% of the total.

## The Problem

Traditional "half of America lives here" maps have two issues:

1. **The San Bernardino Problem**: County boundaries include vast empty areas (San Bernardino County is larger than nine US states but mostly desert)
2. **The Dust Problem**: Using smaller units creates thousands of disconnected specks that fail as visualization

This project solves both using **Max-Flow Min-Cut optimization** with a user-controlled "surface tension" parameter.

## How It Works

A slider controls lambda:

- **lambda ~ 0**: Minimizes area, showing high-resolution "dusty" city centers
- **lambda ~ 1**: Minimizes perimeter, creating smooth, compact blobs

**Note**: Due to computational complexity, geometries for various lambda values are pre-calculated. The web app serves as a visualizer for these pre-computed states.

See [METHODOLOGY.md](METHODOLOGY.md) for the mathematical formulation.

## Installation

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone <repo-url>
cd half_america
uv sync
```

## Usage

```bash
# Run the CLI
uv run half-america

# Run tests
uv run pytest

# Format code
uv run black src/ tests/

# Lint
uv run ruff check src/ tests/

# Type check
uv run mypy src/
```

## Data Pipeline

The data pipeline downloads Census Tract geometries and population data for the contiguous United States.

### Setup

1. Get a Census API key from https://api.census.gov/data/key_signup.html
2. Copy `.env.example` to `.env` and add your key:
   ```bash
   cp .env.example .env
   # Edit .env and add your CENSUS_API_KEY
   ```

### Quick Start

```python
from half_america.data import load_state_tracts, get_pipeline_summary

# Load a single state (e.g., California)
gdf = load_state_tracts("06")
print(get_pipeline_summary(gdf))
# Output: {'tract_count': 9129, 'total_population': 39538223, ...}
```

### Load All US Data

```python
from half_america.data import load_all_tracts

# Load all ~73,000 tracts (downloads ~400MB on first run, cached thereafter)
gdf = load_all_tracts()
```

### Available Functions

| Function | Description |
|----------|-------------|
| `load_all_tracts()` | Load all US tracts with population (main entry point) |
| `load_state_tracts(fips)` | Load single state by FIPS code |
| `get_pipeline_summary(gdf)` | Get statistics for loaded data |
| `CONTIGUOUS_US_FIPS` | List of 49 state FIPS codes |
| `FIPS_TO_STATE` | FIPS code to state name mapping |

Data is cached in `data/cache/` after first download.

## Project Status

**Current Phase**: Data Pipeline Complete (Phase 1)

See [ROADMAP.md](ROADMAP.md) for the full implementation plan.

## Documentation

- [METHODOLOGY.md](METHODOLOGY.md) - Mathematical formulation and algorithm
- [ROADMAP.md](ROADMAP.md) - Implementation roadmap

## License

[MIT](LICENSE)

## Disclaimer

This is a personal experimental project exploring topology optimization and cartography. Not intended as a production tool.
