---
date: 2025-11-21
researcher: Claude
git_commit: 09f5e2197065aebf76b07f029334843e1afc8fb8
branch: master
topic: "Performance Benchmark Baselines"
tags: [research, performance, benchmarks, baseline]
status: complete
---

# Benchmark Baselines

**Date**: 2025-11-21
**Hardware**: Apple M3, 24 GB RAM, macOS 15.4.1
**Python**: 3.11.12
**PyMaxFlow**: 1.3.2

## Summary

Initial performance baselines for the optimization engine using pytest-benchmark. These baselines establish reference points for tracking performance over time and detecting regressions.

## Results

### Graph Construction (build_flow_network)

| Grid Size | Nodes | Edges | Mean | Std Dev | Min | Max |
|-----------|-------|-------|------|---------|-----|-----|
| 20x20 | 400 | ~1,482 | 358 us | 11.9 us | 330 us | 540 us |
| 50x50 | 2,500 | ~9,702 | 2.34 ms | 51.4 us | 2.19 ms | 2.71 ms |

**Scaling**: 6.5x increase for 6.25x more nodes (linear scaling)

### Maxflow Solve

| Grid Size | Mean | Std Dev | Min | Max | Notes |
|-----------|------|---------|-----|-----|-------|
| 20x20 | 366 us | 55.6 us | 333 us | 2.98 ms | Includes graph construction |
| 50x50 | 2.38 ms | 37.9 us | 2.23 ms | 2.54 ms | Includes graph construction |

**Scaling**: 6.5x increase for 6.25x more nodes (linear scaling)

### Partition Extraction (get_partition)

| Grid Size | Mean | Std Dev | Min | Max |
|-----------|------|---------|-----|-----|
| 20x20 | 16.4 us | 0.47 us | 15.0 us | 32.8 us |
| 50x50 | 101 us | 7.3 us | 92.7 us | 385 us |

**Scaling**: 6.2x increase for 6.25x more nodes (linear scaling)

### Binary Search (find_optimal_mu)

| Grid Size | Mean | Std Dev | Iterations (typical) | Notes |
|-----------|------|---------|---------------------|-------|
| 20x20 | 2.32 ms | 35.1 us | ~6-7 | lambda=0.5, tolerance=1% |
| 50x50 | 11.8 ms | 134 us | ~6-7 | lambda=0.5, tolerance=1% |

**Scaling**: 5.1x increase for 6.25x more nodes (sub-linear due to similar iteration counts)

### Full Sweep (sweep_lambda)

| Grid Size | Lambda Values | Sequential | Parallel (3 workers) |
|-----------|---------------|------------|---------------------|
| 20x20 | 3 | 6.94 ms | 7.29 ms |

**Note**: Parallel execution shows similar timing to sequential for small workloads due to thread pool overhead. Parallelization benefits are expected to be more significant with larger graphs and more lambda values.

## Extrapolation to Full Dataset

The full dataset has ~73,000 nodes and ~292,000 edges.

Based on observed linear scaling:

| Operation | 20x20 (400 nodes) | Extrapolated (73k nodes) |
|-----------|-------------------|--------------------------|
| build_flow_network | 358 us | ~65 ms |
| maxflow solve | 366 us | ~67 ms |
| get_partition | 16.4 us | ~3 ms |
| Single binary search | 2.32 ms | ~420 ms |

**Expected full sweep timing** (11 lambda values, sequential):
- Per-lambda: ~6-7 binary search iterations x ~420 ms = ~2.5-3 seconds
- Full sweep: 11 lambdas x ~2.8 s = ~31 seconds

With parallelization (4 workers): ~10-15 seconds expected.

**Note**: These are rough extrapolations. Actual performance may vary due to:
- Graph structure differences (grid vs real tract adjacency)
- Memory effects at larger scales
- Binary search iteration counts varying by lambda

## Recommendations

Based on these baselines:

1. **Current performance is acceptable** - Full sweep is expected to complete in under a minute, which is suitable for pre-computation workflows.

2. **Parallelization ROI** - For small graphs, parallelization overhead may not provide benefits. Focus parallel execution on production workloads with the full 73k-node dataset.

3. **Optimization priorities** - If optimization becomes necessary, focus on:
   - Binary search warm-starting (reduce iterations per lambda)
   - Graph construction vectorization (largest single operation)
   - Partition extraction already very fast (~16 us for 400 nodes)

4. **Regression tracking** - These baselines can be used to detect performance regressions:
   - Alert if any operation exceeds 2x baseline mean
   - Run benchmarks after significant algorithm changes

## Test Commands

```bash
# Run all benchmarks
uv run pytest tests/benchmarks/ --benchmark-only

# Run with detailed statistics
uv run pytest tests/benchmarks/ --benchmark-only --benchmark-sort=name

# Compare against saved baseline (future)
uv run pytest tests/benchmarks/ --benchmark-compare=baseline
```
