---
date: 2025-11-21T12:00:00-08:00
researcher: Claude
git_commit: 830e7dc48893ff34f8ae8d237fc594fb421ca9a2
branch: master
repository: half_america
topic: "Phase 3: Optimization Engine"
tags: [research, codebase, optimization, pymaxflow, graph-cuts, binary-search]
status: complete
last_updated: 2025-11-21
last_updated_by: Claude
---

# Research: Phase 3 Optimization Engine

**Date**: 2025-11-21T12:00:00-08:00
**Researcher**: Claude
**Git Commit**: 830e7dc48893ff34f8ae8d237fc594fb421ca9a2
**Branch**: master
**Repository**: half_america

## Research Question

What is required to implement Phase 3: Optimization Engine as defined in ROADMAP.md?

## Summary

Phase 3 builds on the completed Phase 2 graph construction infrastructure to implement the core Max-Flow Min-Cut optimization with Lagrangian constraint tuning. The key deliverables are:

1. **Graph-cut solver wrapper** - Thin wrapper around existing `build_flow_network()` and `get_partition()`
2. **Binary search for μ** - Iteratively tune Lagrange multiplier to hit 50% population target
3. **λ parameter sweep** - Outer loop iterating surface tension from 0.0 to 1.0
4. **Pre-computation** - Cache results for discrete λ values (0.0, 0.1, ..., 1.0)
5. **Performance optimization** - Benchmarking and tuning for ~73,000 tract graph

The foundation is solid: `GraphData`, `GraphAttributes`, `build_flow_network()`, and `get_partition()` are fully implemented and tested.

## Detailed Findings

### Phase 3 Milestones (from ROADMAP.md:48-60)

```markdown
- [x] Add PyMaxFlow dependency (done in Phase 2)
- [ ] Implement graph-cut solver wrapper
- [ ] Implement binary search for Lagrange multiplier (μ) to hit 50% population target
- [ ] Build outer loop for λ parameter sweep (0.0 → 1.0)
- [ ] Pre-compute results for discrete λ values (e.g., 0.0, 0.1, 0.2, ..., 1.0)
- [ ] Performance benchmarking and optimization
- [ ] Unit tests for optimization correctness
```

### Existing Infrastructure (Phase 2 Complete)

#### Core Data Structures

| Structure | Location | Purpose |
|-----------|----------|---------|
| `GraphData` | `src/half_america/graph/pipeline.py:16-22` | Complete graph input (edges, attributes, counts) |
| `GraphAttributes` | `src/half_america/graph/boundary.py:10-16` | population[], area[], rho, edge_lengths |
| `AdjacencyResult` | `src/half_america/graph/adjacency.py:10-17` | Spatial adjacency (edges, weights, island count) |

#### GraphAttributes Fields

```python
class GraphAttributes(NamedTuple):
    population: np.ndarray      # p_i for each tract (int64)
    area: np.ndarray            # a_i for each tract in sq meters (float64)
    rho: float                  # Characteristic length scale = median(√a_i)
    edge_lengths: dict[tuple[int, int], float]  # l_ij in meters (both directions)
```

#### Implemented Functions

| Function | Location | Description |
|----------|----------|-------------|
| `build_flow_network()` | `network.py:9-53` | Constructs PyMaxFlow graph with capacities |
| `get_partition()` | `network.py:56-67` | Extracts boolean partition after maxflow |
| `load_graph_data()` | `pipeline.py:30-80` | Loads/builds cached graph data |
| `get_graph_summary()` | `pipeline.py:83-101` | Returns summary including total population |

### Mathematical Formulation (from METHODOLOGY.md)

#### Energy Function

```
E(X) = λ Σ(l_ij/ρ)|x_i - x_j| + (1-λ) Σ a_i x_i - μ Σ p_i x_i
       ─────────────────────   ──────────────────   ────────────
       Boundary Cost            Area Cost            Population Reward
```

Where:
- **λ ∈ [0, 1]**: Surface tension (user-controlled slider)
- **μ**: Lagrange multiplier (binary search target)
- **x_i ∈ {0, 1}**: Binary selection variable

#### Edge Capacities (already implemented in network.py)

**Terminal Edges (t-links):**
- Source capacity: `μ × p_i` (population reward)
- Sink capacity: `(1-λ) × a_i` (area cost)

**Neighborhood Edges (n-links):**
- Capacity: `λ × l_ij / ρ` (boundary cost, normalized)

### Binary Search Algorithm (from METHODOLOGY.md:59-72)

```
Target: P_target = 0.5 × P_total

1. Set bounds [μ_min, μ_max]
2. Construct graph with current μ
3. Solve Max-Flow
4. Check resulting population sum:
   - If P_selected < P_target → increase μ (reward too low)
   - If P_selected > P_target → decrease μ (reward too high)
5. Repeat until |P_selected - P_target| < ε
```

**Key Property**: Selected population is monotonic with respect to μ, guaranteeing binary search convergence.

### PyMaxFlow API Reference

#### Graph Creation
```python
import maxflow
g = maxflow.Graph[float](num_nodes, num_edges)
g.add_nodes(num_nodes)
```

#### Edge Addition
```python
# Terminal edges (t-links)
g.add_tedge(node_id, source_cap, sink_cap)

# Neighborhood edges (n-links)
g.add_edge(i, j, cap_ij, cap_ji)  # Symmetric: cap_ij == cap_ji
```

#### Solving and Partition
```python
min_cut_value = g.maxflow()
segment = g.get_segment(node_id)  # 0 = source (selected), 1 = sink (unselected)
```

#### Performance Characteristics
- Runtime: ~500-1500ms for 73,000 nodes with ~292,000 edges
- Memory: ~5-6 MB for typical tract graph
- Use `Graph[float]` for continuous capacities

### Proposed Module Structure

```
src/half_america/optimization/
├── __init__.py           # Public API exports
├── solver.py             # Graph-cut solver wrapper
├── search.py             # Binary search for μ
├── sweep.py              # λ parameter sweep + pre-computation
└── cache.py              # Result caching for pre-computed λ values
```

### Implementation Plan

#### 1. Solver Wrapper (`solver.py`)

```python
@dataclass
class OptimizationResult:
    partition: np.ndarray      # Boolean array (True = selected)
    selected_population: int   # Sum of p_i for selected tracts
    selected_area: float       # Sum of a_i for selected tracts
    lambda_param: float        # Surface tension used
    mu: float                  # Lagrange multiplier used
    iterations: int            # Binary search iterations (if applicable)

def solve_partition(
    graph_data: GraphData,
    lambda_param: float,
    mu: float,
) -> OptimizationResult:
    """Single graph-cut solve for given parameters."""
    g = build_flow_network(graph_data.attributes, graph_data.edges, lambda_param, mu)
    g.maxflow()
    partition = get_partition(g, graph_data.num_nodes)
    # ... compute statistics and return result
```

#### 2. Binary Search (`search.py`)

```python
def find_optimal_mu(
    graph_data: GraphData,
    lambda_param: float,
    target_fraction: float = 0.5,
    tolerance: float = 0.001,  # 0.1% of total population
    max_iterations: int = 50,
    mu_min: float = 0.0,
    mu_max: float = 1.0,
) -> OptimizationResult:
    """Binary search for μ that achieves target population fraction."""
    total_population = graph_data.attributes.population.sum()
    target_population = target_fraction * total_population

    while iterations < max_iterations:
        mu = (mu_min + mu_max) / 2
        result = solve_partition(graph_data, lambda_param, mu)

        if abs(result.selected_population - target_population) < tolerance * total_population:
            return result

        if result.selected_population < target_population:
            mu_min = mu  # Need more selection → increase reward
        else:
            mu_max = mu  # Need less selection → decrease reward
```

#### 3. Parameter Sweep (`sweep.py`)

```python
def sweep_lambda(
    graph_data: GraphData,
    lambda_values: list[float] = None,  # Default: [0.0, 0.1, ..., 1.0]
    target_fraction: float = 0.5,
) -> dict[float, OptimizationResult]:
    """Pre-compute optimal partitions for all λ values."""
    if lambda_values is None:
        lambda_values = [i / 10 for i in range(11)]  # 0.0 to 1.0

    results = {}
    for lambda_param in lambda_values:
        results[lambda_param] = find_optimal_mu(graph_data, lambda_param, target_fraction)

    return results
```

#### 4. Caching (`cache.py`)

```python
def get_results_cache_path(lambda_param: float) -> Path:
    """Return cache path for pre-computed result."""
    return PROCESSED_DIR / f"result_lambda_{lambda_param:.2f}.pkl"

def save_sweep_results(results: dict[float, OptimizationResult]) -> None:
    """Cache all sweep results to disk."""

def load_sweep_results() -> dict[float, OptimizationResult] | None:
    """Load cached sweep results if available."""
```

### Test Strategy

#### Unit Tests (`tests/test_optimization/`)

**test_solver.py:**
- `test_solve_partition_returns_result()` - Basic structure validation
- `test_high_mu_selects_all()` - Boundary condition (μ → ∞)
- `test_zero_mu_selects_none()` - Boundary condition (μ = 0)
- `test_lambda_affects_shape()` - Different λ produces different partitions

**test_search.py:**
- `test_binary_search_converges()` - Reaches target within tolerance
- `test_search_monotonicity()` - Higher μ → more selection
- `test_search_respects_max_iterations()` - Terminates correctly
- `test_search_finds_exact_half()` - Achieves 50% ± tolerance

**test_sweep.py:**
- `test_sweep_covers_all_lambda()` - Results for all values
- `test_sweep_all_reach_target()` - All results meet constraint
- `test_lambda_zero_is_dusty()` - Low λ → many disconnected tracts
- `test_lambda_one_is_smooth()` - High λ → compact blobs

#### Integration Tests

**test_integration.py:**
- `test_full_optimization_dc()` - DC tracts (~200) end-to-end
- `test_precompute_and_cache()` - Full sweep with caching
- `test_cache_roundtrip()` - Save/load results correctly

#### Test Fixtures

```python
# In tests/test_optimization/conftest.py
@pytest.fixture
def small_graph_data():
    """3x3 grid for fast unit tests."""
    # Reuse grid_3x3_gdf from test_graph/conftest.py

@pytest.fixture
def dc_graph_data():
    """DC tracts for integration tests."""
    return load_graph_data(load_state_tracts("11"))
```

### Performance Considerations

1. **Binary search iterations**: ~15-20 iterations to converge with 0.1% tolerance
2. **Single maxflow solve**: ~1 second for 73k nodes
3. **Full sweep (11 λ values)**: ~15-20 × 11 = 165-220 solves → ~3-4 minutes
4. **Caching**: Store results to avoid re-computation

**Optimization opportunities:**
- Warm-start μ from previous λ value (nearby λ have similar μ)
- Parallel λ sweep (independent optimizations)
- Coarse-to-fine search (start with wider tolerance)

### Initial μ Bounds Estimation

The μ parameter must be scaled appropriately to the problem:

```python
# Heuristic for initial bounds
total_pop = attrs.population.sum()
total_area = attrs.area.sum()
avg_pop_density = total_pop / total_area

# μ should be on scale of area/population ratio
mu_scale = total_area / total_pop  # ~area per person
mu_min = 0.0
mu_max = mu_scale * 10  # Allow headroom
```

### CLI Integration

```python
# In src/half_america/__init__.py or new cli.py
@click.command()
@click.option('--lambda', 'lambda_param', type=float, default=0.5)
@click.option('--precompute', is_flag=True, help='Pre-compute all λ values')
def main(lambda_param: float, precompute: bool):
    graph_data = load_graph_data(load_all_tracts())

    if precompute:
        results = sweep_lambda(graph_data)
        save_sweep_results(results)
    else:
        result = find_optimal_mu(graph_data, lambda_param)
        print(f"Selected {result.selected_population:,} people ({result.selected_population/total*100:.1f}%)")
```

## Code References

- `src/half_america/graph/network.py:9-53` - `build_flow_network()` implementation
- `src/half_america/graph/network.py:56-67` - `get_partition()` implementation
- `src/half_america/graph/pipeline.py:16-22` - `GraphData` definition
- `src/half_america/graph/boundary.py:10-16` - `GraphAttributes` definition
- `src/half_america/graph/pipeline.py:83-101` - `get_graph_summary()` with total population
- `tests/test_graph/test_network.py:30-48` - Existing tests for high/zero μ behavior
- `tests/test_graph/conftest.py:16-42` - `grid_3x3_gdf` fixture pattern

## Architecture Insights

### Design Patterns to Follow

1. **NamedTuple for results** - Consistent with `GraphAttributes`, `AdjacencyResult`
2. **Verbose parameter** - All functions accept `verbose: bool` for diagnostic output
3. **Caching with pickle** - Matches `graph_data` caching pattern in `pipeline.py`
4. **Thin wrappers** - Build on existing `build_flow_network()` rather than reimplementing

### Module Dependencies

```
data.pipeline → graph.pipeline → optimization.solver
                                        ↓
                              optimization.search
                                        ↓
                              optimization.sweep
                                        ↓
                              optimization.cache
```

### Data Flow

```
load_all_tracts() → GeoDataFrame (73k rows)
        ↓
load_graph_data() → GraphData (edges, attributes)
        ↓
sweep_lambda() → For each λ:
        ↓
    find_optimal_mu() → Binary search:
        ↓
        solve_partition() → g = build_flow_network()
                           g.maxflow()
                           partition = get_partition()
        ↓
    OptimizationResult (partition, stats, params)
        ↓
save_sweep_results() → Cache to disk
```

## Historical Context (from thoughts/)

- `thoughts/shared/plans/2025-11-21-phase2-graph-construction.md` - Phase 2 implementation plan
- `thoughts/shared/research/2025-11-21-phase2-graph-construction.md` - Phase 2 research

## Related Research

- [Phase 2 Graph Construction](2025-11-21-phase2-graph-construction.md) - Foundation for Phase 3

## Open Questions

1. **μ scale**: What are appropriate initial bounds for μ given tract data characteristics?
2. **Tolerance**: Is 0.1% of total population (~160k people) an acceptable tolerance?
3. **Edge cases**: How to handle λ=0 where boundary cost is zero (potentially many disconnected regions)?
4. **Caching format**: Should results include full partition or just tract IDs?
5. **Performance target**: What's acceptable pre-computation time? (Current estimate: 3-4 minutes)
