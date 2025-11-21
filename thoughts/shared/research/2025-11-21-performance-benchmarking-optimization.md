---
date: 2025-11-21T00:00:00-08:00
researcher: Claude
git_commit: dcbaa85a478467f2245b6c4ed4f4542051408321
branch: master
repository: half_america
topic: "Performance Benchmarking and Optimization for Phase 3 Optimization Engine"
tags: [research, codebase, performance, benchmarking, optimization, pymaxflow, graph-cut]
status: complete
last_updated: 2025-11-21
last_updated_by: Claude
---

# Research: Performance Benchmarking and Optimization

**Date**: 2025-11-21
**Researcher**: Claude
**Git Commit**: dcbaa85a478467f2245b6c4ed4f4542051408321
**Branch**: master
**Repository**: half_america

## Research Question

What is the current state of performance benchmarking and optimization for the Phase 3 Optimization Engine? What approaches should be used to implement the `[ ] Performance benchmarking and optimization` roadmap item?

## Summary

The optimization engine (Phase 3) is functionally complete but lacks formal benchmarking infrastructure. The codebase already includes:
- **Timing instrumentation** in `sweep.py` using `time.perf_counter()`
- **Parallel execution** via `ThreadPoolExecutor` for lambda sweeps
- **Vectorized operations** in boundary calculations
- **Data caching** throughout the pipeline

Key findings:
1. **PyMaxFlow graphs are single-use** - cannot be reused or updated between binary search iterations
2. **Current performance expectations**: ~1s per maxflow solve, ~15-20s per lambda, ~3-4 minutes for full sweep
3. **Missing infrastructure**: Formal benchmark suite, memory profiling, systematic regression testing
4. **Primary bottleneck**: Binary search iterations (15-20 maxflow solves per lambda value)

## Detailed Findings

### Current Implementation Analysis

#### Timing Infrastructure (Already Implemented)

**File**: `src/half_america/optimization/sweep.py:42-54`

```python
def _run_single_lambda(...) -> LambdaResult:
    """Run optimization for a single λ value with timing."""
    start = time.perf_counter()
    search_result = find_optimal_mu(...)
    elapsed = time.perf_counter() - start
    return LambdaResult(
        lambda_param=lambda_param,
        search_result=search_result,
        elapsed_seconds=elapsed,
    )
```

**Data structures** capture timing at multiple levels:
- `LambdaResult.elapsed_seconds` - per-lambda timing
- `SweepResult.total_elapsed_seconds` - total wall-clock time
- `SearchResult.iterations` - binary search iteration counts

#### Parallel Execution (Already Implemented)

**File**: `src/half_america/optimization/sweep.py:100-111`

Uses `ThreadPoolExecutor` with `as_completed()` pattern. This is appropriate because:
- PyMaxFlow releases GIL during C++ `maxflow()` computation
- Each lambda optimization is independent
- Memory overhead acceptable (~8MB per graph × workers)

#### Vectorized Operations (Already Implemented)

**File**: `src/half_america/graph/boundary.py:59-65`

```python
# Prepare index arrays for vectorized operation
i_indices = np.array([e[0] for e in edges])
j_indices = np.array([e[1] for e in edges])

# Vectorized intersection and length calculation
shared_boundaries = intersection(boundaries[i_indices], boundaries[j_indices])
lengths = length(shared_boundaries)
```

### Performance Bottleneck Analysis

#### Flow Network Construction

**File**: `src/half_america/graph/network.py:40-51`

```python
# Terminal edges: O(n) loop - 73,000 iterations
for i in range(num_nodes):
    source_cap = mu * attributes.population[i]
    sink_cap = (1 - lambda_param) * attributes.area[i]
    g.add_tedge(i, source_cap, sink_cap)

# Neighborhood edges: O(m) loop - ~292,000 iterations
for i, j in edges:
    l_ij = attributes.edge_lengths[(i, j)]
    capacity = lambda_param * l_ij / rho
    g.add_edge(i, j, capacity, capacity)
```

**Concern**: Graph must be rebuilt for each binary search iteration because PyMaxFlow does not support capacity updates.

#### Partition Extraction

**File**: `src/half_america/graph/network.py:67`

```python
return np.array([g.get_segment(i) == 0 for i in range(num_nodes)])
```

**Optimization opportunity**: Could use `np.fromiter()` for potential speedup.

### PyMaxFlow Limitations

Critical finding from library research:

1. **Graphs are single-use**: After `maxflow()`, internal state cannot be reset
2. **No capacity updates**: Must rebuild entire graph to change mu
3. **No batch API**: Terminal edges added one-by-one
4. **Memory**: ~5-8MB per graph for 73k nodes, 292k edges

**Implication**: Cannot avoid O(binary_search_iterations) graph reconstructions per lambda value.

### Expected Performance Characteristics

From existing research documents and analysis:

| Metric | Expected Value | Notes |
|--------|----------------|-------|
| Single maxflow solve | ~1 second | 73k nodes, 292k edges |
| Binary search iterations | 15-20 | For 1% tolerance |
| Time per lambda | 15-20 seconds | Sequential within lambda |
| Full sweep (10 lambdas) | 3-4 minutes | With parallelism |
| Memory per graph | 5-8 MB | Float capacities |

### Missing Infrastructure

#### 1. Formal Benchmark Suite

No `tests/benchmarks/` directory or pytest-benchmark integration.

**Recommendation**: Create benchmark suite with:
```
tests/benchmarks/
├── conftest.py           # Fixtures, GC control
├── test_network_perf.py  # Graph construction benchmarks
├── test_solver_perf.py   # Maxflow solve benchmarks
└── test_sweep_perf.py    # Full sweep benchmarks
```

#### 2. Memory Profiling

No memory tracking code found.

**Recommendation**: Use Scalene (best for NumPy/C extension code):
```bash
scalene --cpu --memory src/half_america/cli.py optimize --lambda 0.5
```

#### 3. Regression Testing

Current timing tests verify fields exist, but no baseline comparisons.

**Recommendation**: Use pytest-benchmark's comparison features:
```bash
pytest tests/benchmarks/ --benchmark-save=baseline
# ... make changes ...
pytest tests/benchmarks/ --benchmark-compare=baseline
```

## Code References

### Implementation Files
- `src/half_america/optimization/sweep.py:42-54` - Timing instrumentation
- `src/half_america/optimization/sweep.py:100-111` - Parallel execution
- `src/half_america/optimization/search.py:27-119` - Binary search implementation
- `src/half_america/graph/network.py:9-53` - Flow network construction
- `src/half_america/graph/network.py:56-67` - Partition extraction

### Test Files
- `tests/test_optimization/test_sweep.py:74-85` - Timing field tests
- `tests/test_optimization/test_sweep.py:122-145` - Parallel vs sequential comparison

### Documentation
- `ROADMAP.md:60` - Performance benchmarking milestone
- `METHODOLOGY.md:43-72` - Algorithm description

## Recommended Implementation Plan

### Phase 1: Benchmark Infrastructure

1. **Add pytest-benchmark** to dev dependencies
2. **Create benchmark fixtures** with real graph data
3. **Implement baseline benchmarks** for:
   - `build_flow_network()` - graph construction
   - `maxflow()` - solver execution
   - `get_partition()` - result extraction
   - `find_optimal_mu()` - full binary search
   - `sweep_lambda()` - full sweep

### Phase 2: Profiling and Analysis

1. **Profile with Scalene** to identify actual bottlenecks
2. **Document baseline performance** with 73k-node graph
3. **Identify optimization targets** based on profiling results

### Phase 3: Targeted Optimizations

Based on profiling, consider:

1. **Vectorize partition extraction**:
```python
def get_partition(g: maxflow.Graph, num_nodes: int) -> np.ndarray:
    return np.fromiter(
        (g.get_segment(i) == 0 for i in range(num_nodes)),
        dtype=bool,
        count=num_nodes
    )
```

2. **Warm-start binary search bounds** (for sequential processing):
```python
# Use previous lambda's mu as starting estimate
# Narrows search bounds from [0, mu_max] to [0.5*prev_mu, 2*prev_mu]
```

3. **Coarse-to-fine search** (reduces iterations):
```python
# First pass: 5% tolerance (fewer iterations)
# Second pass: 1% tolerance (starting from coarse result)
```

4. **Consider joblib.Parallel** for better memory handling:
```python
from joblib import Parallel, delayed
results = Parallel(n_jobs=-1, backend="threading")(
    delayed(_run_single_lambda)(graph_data, lam, ...)
    for lam in lambda_values
)
```

### Phase 4: Regression Prevention

1. **Save benchmark baselines** in CI
2. **Add performance assertions** to CI pipeline
3. **Document acceptable performance ranges**

## Historical Context (from thoughts/)

### Existing Research Documents

| Document | Key Insights |
|----------|--------------|
| `2025-11-21-phase3-optimization-engine.md` | PyMaxFlow integration, ~500-1500ms per solve |
| `2025-11-21-binary-search-lagrange-multiplier.md` | 15-20 iterations typical, warm-start suggestions |
| `2025-11-21-lambda-parameter-sweep.md` | Parallel sweep design rationale |
| `2025-11-21-precompute-lambda-values.md` | Caching strategy for discrete lambda values |

### Performance Estimates from Research

From `2025-11-21-binary-search-lagrange-multiplier.md`:
- Single maxflow solve: ~1 second
- Binary search (15-20 iterations): 15-20 seconds per lambda
- Full sweep (11 lambdas): ~3-4 minutes sequential

**Optimization opportunities identified**:
1. Warm-start mu from previous lambda
2. Coarse-to-fine tolerance
3. Parallel lambda sweep (already implemented)

## Architecture Insights

### Why Graph Reconstruction is Unavoidable

The binary search varies mu, which changes terminal edge capacities:
```
source_cap = mu * population[i]  # Changes with mu
sink_cap = (1-lambda) * area[i]  # Constant for fixed lambda
```

PyMaxFlow does not support updating edge capacities after construction. This is a fundamental limitation of the library, not a design flaw in the implementation.

### Parallelization Trade-offs

**Thread-based** (current): Lower overhead, works because PyMaxFlow releases GIL
**Process-based**: Better isolation, but higher memory (each process copies graph_data)

The current `ThreadPoolExecutor` approach is appropriate for this workload.

### Caching Strategy

Current caching layers:
1. **Data pipeline**: TIGER/Census data cached as Parquet
2. **Graph data**: Adjacency/attributes cached as Pickle
3. **Sweep results**: Full results cached as Pickle

This is sound architecture - optimization results are expensive to compute and stable for given inputs.

## Open Questions

1. **Fine-grained lambda values**: If 0.01 step (101 values) is needed for smooth animations, total time increases to ~30-40 minutes. Is this acceptable for pre-computation?
RESPONSE: It's probably fine eventually. I want to hold off on going more fine-grained until we have everything else in the project completed (to keep velocity high during initial development). We have "- **Fine λ granularity**: Support 0.01 increments (101 values) for smooth animations" in ROADMAP.md

2. **WebAssembly port**: Future enhancement mentions client-side optimization. Would require replacing PyMaxFlow with JS-compatible solver.
RESPONSE: I don't think we're actually going to end up doing this, so you can disregard for now.

3. **Alternative algorithms**: For real-time computation, could approximate solutions (greedy region growing, simulated annealing) provide acceptable quality with better performance?
RESPONSE: Maybe, but I don't think we're going to end up doign real-time computation, so we can hold off on this for now.

## Recommendations Summary

| Priority | Action | Impact |
|----------|--------|--------|
| High | Add pytest-benchmark infrastructure | Enables regression tracking |
| High | Profile with Scalene | Identifies actual bottlenecks |
| Medium | Vectorize `get_partition()` | Minor speedup (~5%) |
| Medium | Warm-start binary search bounds | ~20-30% fewer iterations |
| Low | Switch to joblib.Parallel | Better memory management |
| Low | Coarse-to-fine search | ~30% fewer iterations |

The current implementation is already well-optimized. Focus should be on **benchmarking infrastructure** to track performance over time and prevent regressions, rather than aggressive optimization.
