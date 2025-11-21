# API Reference

This document provides the Python API reference for programmatic use of Half of America. Each module includes a Quick Start example and full function reference.

For installation and CLI usage, see [README.md](../README.md).

---

## Data Pipeline

The data pipeline downloads Census Tract geometries and population data for the contiguous United States.

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

### Function Reference

| Function | Description |
|----------|-------------|
| `load_all_tracts()` | Load all US tracts with population (main entry point) |
| `load_state_tracts(fips)` | Load single state by FIPS code |
| `get_pipeline_summary(gdf)` | Get statistics for loaded data |
| `CONTIGUOUS_US_FIPS` | List of 49 state FIPS codes |
| `FIPS_TO_STATE` | FIPS code to state name mapping |

Data is cached in `data/cache/` after first download.

---

## Graph Construction

The graph module builds spatial adjacency graphs from Census Tract data for Max-Flow Min-Cut optimization.

### Quick Start

```python
from half_america.data import load_all_tracts
from half_america.graph import load_graph_data, get_graph_summary

# Load tract data (from Phase 1)
gdf = load_all_tracts()

# Build or load graph (cached after first run)
graph_data = load_graph_data(gdf)
print(get_graph_summary(graph_data))
# {'num_nodes': 73000, 'num_edges': 450000, 'rho_km': 2.5, ...}
```

### Building Flow Networks

```python
from half_america.graph import build_flow_network, get_partition

# Build flow network for specific λ and μ
g = build_flow_network(graph_data.attributes, graph_data.edges, lambda_param=0.5, mu=0.001)
g.maxflow()

# Extract selected tracts
selected = get_partition(g, graph_data.num_nodes)
print(f"Selected {selected.sum()} tracts")
```

### Function Reference

| Function | Description |
|----------|-------------|
| `load_graph_data(gdf)` | Main entry point - builds or loads cached graph data |
| `get_graph_summary(graph_data)` | Get statistics for loaded graph |
| `build_flow_network(attrs, edges, λ, μ)` | Construct PyMaxFlow graph for optimization |
| `get_partition(g, num_nodes)` | Extract selected tracts after maxflow |

### Data Types

| Type | Description |
|------|-------------|
| `GraphData` | Complete graph data (edges, attributes, statistics) |
| `GraphAttributes` | Node/edge attributes (population, area, rho, edge_lengths) |

Graph data is cached in `data/cache/` after first computation.

---

## Optimization

The optimization module runs Max-Flow Min-Cut optimization across lambda values to find population partitions.

### CLI Usage

```bash
# Pre-compute optimization results for all lambda values (recommended)
uv run half-america precompute

# Options
uv run half-america precompute --force           # Rebuild cache
uv run half-america precompute --lambda-step 0.05  # Finer granularity
uv run half-america precompute --skip-failures   # Continue on convergence errors
```

Results are cached in `data/cache/processed/` after computation.

### Quick Start

```python
from half_america.data import load_all_tracts
from half_america.graph import load_graph_data
from half_america.optimization import sweep_lambda, save_sweep_result

# Load data and graph
gdf = load_all_tracts()
graph_data = load_graph_data(gdf)

# Run optimization across all lambda values
result = sweep_lambda(graph_data)

# Check results
for lambda_val, lambda_result in result.results.items():
    opt = lambda_result.search_result.result
    print(f"lambda={lambda_val:.1f}: {opt.population_fraction:.2%} selected")

# Persist for post-processing
save_sweep_result(result, Path("data/cache/processed/sweep.pkl"))
```

### Function Reference

| Function | Description |
|----------|-------------|
| `sweep_lambda(graph_data)` | Run optimization across all lambda values (main entry point) |
| `find_optimal_mu(graph_data, lambda_val)` | Find mu that achieves 50% population for given lambda |
| `solve_partition(graph_data, lambda_val, mu)` | Solve single graph-cut for specific parameters |
| `save_sweep_result(result, path)` | Persist sweep results to disk |
| `load_sweep_result(path)` | Load persisted sweep results |

### Data Types

| Type | Description |
|------|-------------|
| `SweepResult` | Full sweep results (dict of lambda to result, timing, convergence) |
| `SearchResult` | Binary search result (final result, iterations, mu history) |
| `OptimizationResult` | Single solve result (partition, statistics, energy) |

See [METHODOLOGY.md](../METHODOLOGY.md) for mathematical details on the optimization algorithm.
