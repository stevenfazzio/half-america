# Half of America

A topology optimization experiment that visualizes US population concentration using Max-Flow Min-Cut algorithms to produce smooth, organic shapes.

## The Problem

You've seen those viral maps titled "Half of the United States Lives In These Counties." They sort counties by population and highlight the top N until reaching 50% of Americans. While effective at shock value, this approach has fundamental flaws:

1. **The San Bernardino Problem**: San Bernardino County (larger than nine US states) always appears—implying its vast desert is densely populated.

2. **The "Dust" Problem**: Using finer-grained Census Tracts produces thousands of disconnected specks—mathematically accurate but visually useless.

3. **The "Bridge" Problem**: Minimizing region count creates degenerate shapes with narrow connections between population centers.

## The Solution

This project minimizes *perimeter* instead of region count, producing smooth, topologically coherent shapes. A user-controlled "surface tension" parameter (λ) balances area minimization against boundary smoothness:

- **λ ≈ 0**: Minimizes area → high-resolution "dusty" map of dense urban cores
- **λ ≈ 0.9**: Minimizes perimeter → smooth "blobs" showing megaregions

The slider lets you visualize how distinct cities merge into megaregions and eventually into continental blocks.

## How It Works

The algorithm treats Census Tracts (~73,000 across the US) as nodes in a graph:

1. **Graph Construction**: Build spatial adjacency graph with edge weights proportional to shared boundary length
2. **Max-Flow Min-Cut**: Use Lagrangian relaxation to solve the constrained optimization
3. **Binary Search**: Find the Lagrange multiplier (μ) that achieves exactly 50% population
4. **Post-Processing**: Dissolve selected tracts, simplify geometry, export as TopoJSON

The math involves minimizing:

```
E(X) = λ·(boundary cost) + (1-λ)·(area cost) - μ·(population reward)
```

See [METHODOLOGY.md](METHODOLOGY.md) for the full mathematical formulation.

## Installation

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/stevenfazzio/half-america.git
cd half-america
uv sync
```

### Census API Key (Optional)

For faster data downloads, get a free API key from [census.gov](https://api.census.gov/data/key_signup.html):

```bash
cp .env.example .env
# Edit .env and add your CENSUS_API_KEY
```

## Usage

### Pre-compute Optimization Results

Generate optimized partitions for all λ values:

```bash
uv run half-america precompute
```

Options:
- `--force`: Rebuild cache even if it exists
- `--lambda-step 0.05`: Finer granularity (default: 0.1)
- `--skip-failures`: Continue on convergence errors

### Export TopoJSON

Export web-ready geometry files:

```bash
uv run half-america export
```

Output goes to `data/output/topojson/`.

### Python API

```python
from half_america.data import load_all_tracts
from half_america.graph import load_graph_data
from half_america.optimization import sweep_lambda

# Load ~73,000 Census Tracts (cached after first download)
gdf = load_all_tracts()

# Build spatial adjacency graph
graph_data = load_graph_data(gdf)

# Run optimization across lambda values
result = sweep_lambda(graph_data)

for lambda_val, lambda_result in result.results.items():
    opt = lambda_result.search_result.result
    print(f"λ={lambda_val:.1f}: {opt.population_fraction:.2%} of population")
```

See [docs/API.md](docs/API.md) for the complete API reference.

## Project Structure

```
half-america/
├── src/half_america/       # Python package
│   ├── data/               # Census data pipeline
│   ├── graph/              # Spatial graph construction
│   ├── optimization/       # Max-Flow Min-Cut solver
│   └── postprocess/        # Dissolve, simplify, export
├── data/                   # Cached data (gitignored)
│   ├── cache/              # Downloaded & processed data
│   └── output/             # Exported TopoJSON files
├── tests/                  # Test suite
├── METHODOLOGY.md          # Mathematical formulation
└── ROADMAP.md              # Implementation phases
```

## Development

```bash
# Run tests
uv run pytest

# Skip network-dependent tests
uv run pytest -m "not integration"

# Format and lint
uv run ruff format src/ tests/
uv run ruff check src/ tests/

# Type check
uv run mypy src/
```

### Cache Management

Data is cached at multiple levels in `data/cache/`:

| Cache | Location | Clear When |
|-------|----------|------------|
| HTTP requests | `requests_cache.sqlite` | API issues |
| TIGER shapefiles | `raw/tiger/*.parquet` | Year config change |
| Census data | `raw/census/*.parquet` | Year config change |
| Processed tracts | `processed/*.parquet` | Source data change |
| Graph/sweep | `processed/*.pkl` | Algorithm change |

```bash
# Clear all caches
rm -rf data/cache/

# Clear processed only (keep downloads)
rm -rf data/cache/processed/
```

## Technology Stack

- **Data Ingestion**: pandas, cenpy (Census API)
- **Spatial Operations**: geopandas, libpysal, shapely
- **Optimization**: PyMaxFlow (C++ wrapper)
- **Export**: topojson
- **Web Frontend**: React, Mapbox GL JS (Phase 5)

## Current Status

Phase 4 (Post-Processing) is complete. The Python backend can:

- Download and cache Census Tract data
- Build spatial adjacency graphs
- Run Max-Flow Min-Cut optimization
- Export simplified TopoJSON geometry

Phase 5 (Web Frontend) is next—building the interactive map visualization.

See [ROADMAP.md](ROADMAP.md) for full implementation details.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

Steven Fazzio ([@stevenfazzio](https://github.com/stevenfazzio))
