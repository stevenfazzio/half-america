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

---

## Post-Processing

The post-processing module transforms optimization results into web-ready formats through dissolve, simplify, and export operations.

### Quick Start

```python
from half_america.data import load_all_tracts
from half_america.optimization.sweep import load_sweep_result
from half_america.postprocess import (
    dissolve_all_lambdas,
    simplify_all_lambdas,
    export_all_lambdas,
)

# Load data
gdf = load_all_tracts()
sweep_result = load_sweep_result(Path("data/cache/processed/sweep_2024_2022_0.1.pkl"))

# Run post-processing pipeline
dissolve_results = dissolve_all_lambdas(gdf, sweep_result)
simplify_results = simplify_all_lambdas(dissolve_results)
export_results = export_all_lambdas(simplify_results, dissolve_results)
```

### Dissolve Module

Merge selected tracts into unified geometries.

| Function | Description |
|----------|-------------|
| `dissolve_partition(gdf, partition)` | Dissolve selected tracts into unified geometry |
| `dissolve_all_lambdas(gdf, sweep_result)` | Batch dissolve for all lambda values |

| Type | Description |
|------|-------------|
| `DissolveResult` | Dissolved geometry with num_parts, total_area_sqm, num_tracts |

### Simplify Module

Reduce geometry complexity for web performance.

| Function | Description |
|----------|-------------|
| `simplify_geometry(geometry, tolerance)` | Simplify geometry using Douglas-Peucker |
| `simplify_all_lambdas(dissolve_results)` | Batch simplify for all lambda values |

| Type | Description |
|------|-------------|
| `SimplifyResult` | Simplified geometry with vertex counts and reduction percent |

| Constant | Description |
|----------|-------------|
| `DEFAULT_TOLERANCE` | 500m - provides ~98% vertex reduction |

### Export Module

Export simplified geometries to TopoJSON format for web delivery.

#### Functions

##### `export_to_topojson(geometry, output_path, metadata, object_name="selected_region", quantization=1e5)`

Export a single geometry to TopoJSON format.

**Parameters:**
- `geometry`: Shapely Polygon or MultiPolygon in EPSG:5070
- `output_path`: Path for output .json file
- `metadata`: ExportMetadata with lambda_value, population_selected, area_sqm, num_parts
- `object_name`: Name for geometry object in TopoJSON (default: "selected_region")
- `quantization`: Quantization factor (default: 1e5)

**Returns:** `ExportResult` with path, file_size_bytes, lambda_value, object_name

##### `export_all_lambdas(simplify_results, dissolve_results, output_dir=None, verbose=True)`

Export all lambda values to individual TopoJSON files.

**Parameters:**
- `simplify_results`: dict[float, SimplifyResult] from simplify_all_lambdas()
- `dissolve_results`: dict[float, DissolveResult] from dissolve_all_lambdas()
- `output_dir`: Output directory (default: data/output/topojson)
- `verbose`: Print progress messages

**Returns:** dict[float, ExportResult]

##### `export_combined_topojson(simplify_results, dissolve_results, output_path=None, quantization=1e5, verbose=True)`

Export all lambda values to a single multi-object TopoJSON file.

**Parameters:**
- `simplify_results`: dict[float, SimplifyResult]
- `dissolve_results`: dict[float, DissolveResult]
- `output_path`: Output file path (default: data/output/topojson/combined.json)
- `quantization`: Quantization factor
- `verbose`: Print progress messages

**Returns:** Path to combined file

#### Types

| Type | Description |
|------|-------------|
| `ExportResult` | Export result with path, file_size_bytes, lambda_value, object_name |
| `ExportMetadata` | Metadata with lambda_value, population_selected, area_sqm, num_parts |

#### Constants

| Constant | Description |
|----------|-------------|
| `DEFAULT_QUANTIZATION` | 1e5 - good balance of precision vs file size |
