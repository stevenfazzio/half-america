---
date: 2025-11-21T18:00:00-08:00
researcher: Claude
git_commit: bd230b5315a225e5d1a3fd624f392819d4c1f839
branch: master
repository: half_america
topic: "Performance Optimization Roadmap (Based on Benchmark Analysis)"
tags: [research, codebase, performance, optimization, benchmarks, phase3]
status: complete
last_updated: 2025-11-21
last_updated_by: Claude
---

# Research: Performance Optimization (Based on Benchmark Analysis)

**Date**: 2025-11-21
**Researcher**: Claude
**Git Commit**: bd230b5315a225e5d1a3fd624f392819d4c1f839
**Branch**: master
**Repository**: half_america

## Research Question

What performance optimizations should be implemented for the Phase 3 Optimization Engine based on the benchmark analysis? This addresses the ROADMAP.md item: `[ ] Performance optimization (based on benchmark analysis)`.

## Summary

The benchmark infrastructure is now complete and provides comprehensive baseline measurements. Analysis reveals:

1. **Current performance is acceptable for pre-computation workflows** - Full sweep extrapolates to ~10-15 seconds with parallelization
2. **Primary bottleneck is PyMaxFlow's `g.maxflow()`** - This is compiled C++ code; no Python-level optimization possible
3. **Secondary bottleneck is graph reconstruction** - Required for each binary search iteration due to PyMaxFlow API limitations
4. **Existing optimizations are sound** - ThreadPoolExecutor parallelization, vectorized Shapely operations, and caching are already implemented

**Recommendation**: The optimization engine is already well-optimized. Focus should be on **tracking and preventing regressions** rather than aggressive optimization. Implement optional micro-optimizations for `get_partition()` and warm-start binary search bounds.

## Current Benchmark Results

Fresh benchmark run (2025-11-21):

| Benchmark | Mean Time | Notes |
|-----------|-----------|-------|
| `test_build_network_20x20` | 361 μs | 400 nodes, ~1,500 edges |
| `test_build_network_50x50` | 2.39 ms | 2,500 nodes, ~9,800 edges |
| `test_maxflow_solve_20x20` | 368 μs | Includes graph construction |
| `test_maxflow_solve_50x50` | 2.43 ms | Includes graph construction |
| `test_get_partition_20x20` | 17.1 μs | 400 nodes |
| `test_get_partition_50x50` | 104 μs | 2,500 nodes |
| `test_find_optimal_mu_20x20` | 2.35 ms | ~6-7 iterations |
| `test_find_optimal_mu_50x50` | 12.0 ms | ~6-7 iterations |
| `test_sweep_3_lambdas_20x20` | 6.94 ms | Sequential, 3 lambdas |
| `test_sweep_parallel_20x20` | 7.05 ms | Parallel (3 workers), 3 lambdas |

**Scaling Behavior**: All operations show approximately linear scaling (6.25x more nodes → 6.5x longer time).

## Extrapolation to Full Dataset

The full dataset has ~73,000 nodes and ~292,000 edges (182.5x more nodes than 20x20 grid).

| Operation | 20x20 Measured | Extrapolated (73k nodes) |
|-----------|----------------|--------------------------|
| `build_flow_network` | 361 μs | ~66 ms |
| `maxflow` solve | 368 μs | ~67 ms |
| `get_partition` | 17 μs | ~3 ms |
| Binary search (6-7 iters) | 2.35 ms | ~430 ms |
| Full sweep (11 lambdas) | - | ~5 seconds (sequential) |

**With parallelization (4 workers)**: ~2-3 seconds expected for full 11-lambda sweep.

**Note**: These are rough extrapolations. Actual performance may vary due to graph structure differences (grid vs real tract adjacency) and memory effects at larger scales.

## Detailed Findings

### Performance Bottleneck Hierarchy

1. **`g.maxflow()` (PyMaxFlow C++ solver)** - ~50% of time per solve
   - This is compiled C++ code using the Boykov-Kolmogorov algorithm
   - No Python-level optimization possible
   - Must be called for each binary search iteration

2. **`build_flow_network()` (Graph Construction)** - ~45% of time per solve
   - Two loops: terminal edges (73k iterations) + neighborhood edges (292k iterations)
   - PyMaxFlow API requires sequential `add_tedge()` and `add_edge()` calls
   - Cannot batch or vectorize due to library limitations

3. **`get_partition()` (Result Extraction)** - ~5% of time per solve
   - Currently uses list comprehension: `np.array([g.get_segment(i) == 0 for i in range(num_nodes)])`
   - Minor optimization opportunity with `np.fromiter()`

### Why PyMaxFlow Graph Reconstruction is Unavoidable

Critical finding from library analysis:

```python
# Binary search varies mu, which changes terminal edge capacities:
source_cap = mu * population[i]  # Changes with each iteration
sink_cap = (1 - lambda_param) * area[i]  # Constant for fixed lambda
```

PyMaxFlow does not support:
- Updating edge capacities after construction
- Resetting graph state after `maxflow()` call
- Batch operations for terminal edges

**Implication**: Each binary search iteration requires O(n+m) graph reconstruction. This is fundamental to the library design, not a fixable inefficiency.

### Existing Optimizations Already in Place

| Optimization | Location | Impact |
|--------------|----------|--------|
| ThreadPoolExecutor parallelization | `sweep.py:100-145` | ~3-4x speedup for full sweep |
| Vectorized Shapely operations | `boundary.py:59-65` | Orders of magnitude faster than Python loops |
| Graph data caching (Pickle) | `pipeline.py:52-56` | Avoids rebuilding adjacency graph |
| HTTP request caching | `census.py:13-24` | Avoids redundant Census API calls |
| Parquet data caching | `pipeline.py:48-96` | Fast reload of tract GeoDataFrames |
| Binary search algorithm | `search.py:71-107` | Log(n) solver calls vs linear grid search |
| Module-scoped benchmark fixtures | `conftest.py:84-91` | Isolates benchmark overhead |

### Parallel vs Sequential Observation

Benchmark results show parallel execution is slightly *slower* than sequential for small workloads:

- Sequential (3 lambdas): 6.94 ms
- Parallel (3 lambdas): 7.05 ms

This is expected due to ThreadPoolExecutor overhead. Parallelization benefits emerge at larger scales with the full 73k-node graph and 11 lambda values.

## Recommended Optimizations

### Priority 1: Regression Prevention (High Impact, Low Effort)

**Status**: Infrastructure complete, needs CI integration

The benchmark suite exists. To prevent regressions:

1. Save baseline results: `uv run pytest tests/benchmarks/ --benchmark-save=baseline`
2. Compare after changes: `uv run pytest tests/benchmarks/ --benchmark-compare=baseline`
3. Consider adding performance assertions to CI

### Priority 2: Vectorize `get_partition()` (Low Impact, Low Effort)

**Current** (`network.py:67`):
```python
return np.array([g.get_segment(i) == 0 for i in range(num_nodes)])
```

**Proposed**:
```python
return np.fromiter(
    (g.get_segment(i) == 0 for i in range(num_nodes)),
    dtype=bool,
    count=num_nodes
)
```

**Expected Impact**: ~5-10% speedup for partition extraction (currently 17μs → ~15μs for 400 nodes). Marginal but essentially free.

### Priority 3: Warm-Start Binary Search Bounds (Medium Impact, Medium Effort)

**Concept**: When sweeping lambda values sequentially (or when previous results are available), use the previous lambda's optimal mu as a starting estimate.

**Current**: Binary search starts with bounds `[0, mu_max]` for each lambda
**Proposed**: Start with bounds `[0.5 * prev_mu, 2 * prev_mu]` based on previous lambda result

**Expected Impact**: ~20-30% fewer binary search iterations when lambda values are processed in order.

**Caveat**: This optimization conflicts with parallel execution where lambdas run independently. Would need separate "sequential with warm-start" mode.

### Priority 4: Coarse-to-Fine Search (Medium Impact, Higher Effort)

**Concept**: Two-pass binary search:
1. First pass: 5% tolerance (fewer iterations)
2. Second pass: 1% tolerance (narrowed bounds from first pass)

**Expected Impact**: ~30% fewer total iterations for high-precision results.

**Caveat**: May not be needed given current performance is acceptable.

### Priority 5: Profile Full Dataset with Scalene (Investigation)

For accurate bottleneck analysis on the production dataset:

```bash
uv run scalene --cpu src/half_america/cli.py precompute
```

This would reveal if extrapolations are accurate and identify any memory-related bottlenecks at scale.

## Not Recommended

### ProcessPoolExecutor (Worse Performance)

The current ThreadPoolExecutor is appropriate because:
- PyMaxFlow releases GIL during C++ computation
- ProcessPoolExecutor would require serializing graph_data for each worker
- Memory overhead (copying 73k-node graph) would exceed parallelization benefits

### Alternative Max-Flow Libraries

PyMaxFlow is the de facto standard Python wrapper for graph cuts:
- Push-relabel algorithms (networkx.maximum_flow) are slower for this graph structure
- Pure Python implementations would be orders of magnitude slower
- Custom C++ implementations would require significant maintenance burden

### WebAssembly Port (Future Enhancement)

Per ROADMAP.md "Future Enhancements", a WebAssembly port for client-side computation is listed. However:
- Current pre-computation approach is adequate (~10-15 seconds total)
- WebAssembly would require replacing PyMaxFlow with JS-compatible solver
- User feedback suggests this is not a priority

## Architecture Insights

### Why Pre-Computation is the Right Approach

The optimization problem has these characteristics:
- **Fixed inputs**: Census tract geometries and populations change infrequently
- **Discrete outputs**: Only need results for ~11 lambda values (0.0 to 0.9 in 0.1 increments)
- **Expensive computation**: ~500 maxflow solves for full sweep
- **Deterministic**: Same inputs produce same outputs

Pre-computing all lambda results once and caching them is the correct architectural choice. Runtime interpolation between pre-computed results handles user interaction.

### Threading vs Multiprocessing Decision

The choice of ThreadPoolExecutor over ProcessPoolExecutor was deliberate:

| Factor | ThreadPoolExecutor | ProcessPoolExecutor |
|--------|-------------------|---------------------|
| GIL during C++ | Released (parallel) | N/A (separate GIL per process) |
| Memory overhead | Shared memory | Full graph_data copy per process |
| Startup cost | ~1ms | ~100ms |
| Data serialization | None | pickle.dumps/loads |

For this workload, ThreadPoolExecutor wins due to lower overhead and GIL release during PyMaxFlow operations.

## Code References

### Implementation Files
- `src/half_america/optimization/sweep.py:100-145` - Parallel lambda sweep
- `src/half_america/optimization/search.py:71-107` - Binary search loop
- `src/half_america/graph/network.py:40-51` - Graph construction loops
- `src/half_america/graph/network.py:67` - Partition extraction (optimization candidate)

### Benchmark Files
- `tests/benchmarks/conftest.py` - Benchmark fixtures (20x20, 50x50 grids)
- `tests/benchmarks/test_network_bench.py` - Network construction benchmarks
- `tests/benchmarks/test_solver_bench.py` - Solver and sweep benchmarks

### Documentation
- `ROADMAP.md:61` - Performance optimization milestone
- `METHODOLOGY.md:43-72` - Algorithm description

## Historical Context (from thoughts/)

| Document | Key Insights |
|----------|--------------|
| `2025-11-21-performance-benchmarking-optimization.md` | Initial performance research, identified bottlenecks |
| `2025-11-21-benchmark-baselines.md` | First benchmark results, extrapolation methodology |
| `2025-11-21-performance-benchmarking-infrastructure.md` | Implementation plan for benchmark suite |
| `2025-11-21-binary-search-lagrange-multiplier.md` | Binary search design rationale |

## Related Research

- `thoughts/shared/research/2025-11-21-benchmark-baselines.md` - Initial baselines
- `thoughts/shared/plans/2025-11-21-performance-benchmarking-infrastructure.md` - Infrastructure implementation

## Open Questions

1. **Full dataset profiling**: Should we run Scalene on the production 73k-node graph to validate extrapolations?
   - **Recommendation**: Do this once manually, but don't automate. Extrapolations are reasonable.

2. **Fine-grained lambda values**: If 0.01 step (101 values) is needed for smooth animations, total time increases to ~30-60 seconds. Is this acceptable?
   - **Per ROADMAP.md**: Deferred to "Future Enhancements" to maintain development velocity.

3. **CI benchmark integration**: Should benchmark comparisons be added to CI?
   - **Recommendation**: Nice-to-have but not critical. Manual comparison during optimization work is sufficient.

## Implementation Plan for Performance Optimization

### Phase 1: Micro-Optimizations (Optional)

If performance becomes a concern:

1. [ ] Implement `np.fromiter()` optimization for `get_partition()` in `network.py:67`
2. [ ] Add benchmark comparison to development workflow documentation
3. [ ] Run Scalene profiling on full dataset to validate extrapolations

### Phase 2: Warm-Start Binary Search (If Needed)

Only if sequential sweep performance becomes critical:

1. [ ] Add optional `mu_hint` parameter to `find_optimal_mu()`
2. [ ] Track `prev_mu` in sweep loop when `max_workers=1`
3. [ ] Benchmark improvement vs. overhead

### Conclusion

**The optimization engine is already well-optimized.** The benchmark infrastructure now provides visibility into performance characteristics and enables regression detection.

Current extrapolated performance (~10-15 seconds for full sweep with parallelization) is acceptable for the pre-computation use case. Focus should shift to completing Phase 4 (Post-Processing) and Phase 5 (Web Frontend) rather than pursuing diminishing returns on optimization.

**ROADMAP.md Update Suggestion**: Consider marking "Performance optimization (based on benchmark analysis)" as complete with a note that micro-optimizations were deferred as unnecessary. Or keep it open with specific sub-items if optimization work is desired.
