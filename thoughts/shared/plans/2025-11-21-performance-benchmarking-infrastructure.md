# Performance Benchmarking Infrastructure Implementation Plan

## Overview

Add pytest-benchmark infrastructure to the optimization engine to enable systematic performance tracking and regression detection. This plan focuses on establishing the benchmark suite and running initial baselines - optimization work will be planned separately based on benchmark results.

## Current State Analysis

The optimization engine (Phase 3) is functionally complete with timing instrumentation already in place:
- `sweep.py:42-54` uses `time.perf_counter()` for timing
- `LambdaResult.elapsed_seconds` and `SweepResult.total_elapsed_seconds` capture timing data
- `test_sweep.py:122-145` has a basic parallel vs sequential comparison

**What's Missing:**
- No pytest-benchmark dependency
- No formal benchmark suite in `tests/benchmarks/`
- No baseline performance data documented
- No way to compare performance across code changes

### Key Discoveries:
- `pyproject.toml:48-55` - Dev dependencies need pytest-benchmark added
- `tests/test_optimization/conftest.py:27-52` - Has `complex_graph_data` fixture (5-node graph) but it's too small for meaningful benchmarks
- `tests/test_graph/conftest.py:16-42` - Has `grid_3x3_gdf` fixture that could be expanded

## Desired End State

After this plan is complete:
1. `pytest-benchmark` is available as a dev dependency
2. A `tests/benchmarks/` directory exists with benchmark tests for key operations
3. Benchmarks can be run with `uv run pytest tests/benchmarks/ --benchmark-only`
4. Baseline performance numbers are documented
5. `ROADMAP.md` is updated to reflect the phased approach (infrastructure vs optimization)

### Verification:
- `uv run pytest tests/benchmarks/ --benchmark-only` runs successfully
- Benchmark output shows timing statistics for each operation
- ROADMAP.md shows "Performance benchmarking infrastructure" as complete

## What We're NOT Doing

- CI/CD integration for benchmark regression tracking (deferred)
- Performance optimizations (will be planned after benchmarks establish baselines)
- Memory profiling (Scalene profiling is a one-time investigation, not part of this infrastructure)
- Fine-grained lambda values (0.01 step) - deferred per ROADMAP.md

## Implementation Approach

1. Add pytest-benchmark dependency
2. Create benchmark fixtures with appropriately-sized test data
3. Implement benchmarks for key operations (graph construction, maxflow solve, binary search, sweep)
4. Run benchmarks and document baseline performance
5. Update ROADMAP.md to reflect completed infrastructure and future optimization work

---

## Phase 1: Add pytest-benchmark Dependency

### Overview
Add pytest-benchmark to dev dependencies.

### Changes Required:

#### 1. Update pyproject.toml
**File**: `pyproject.toml`
**Changes**: Add pytest-benchmark to dev dependency group

```toml
[dependency-groups]
dev = [
    "black>=25.11.0",
    "mypy>=1.18.2",
    "pandas-stubs>=2.0",
    "pytest>=9.0.1",
    "pytest-benchmark>=4.0",
    "pytest-cov>=4.0",
    "ruff>=0.14.5",
]
```

### Success Criteria:

#### Automated Verification:
- [ ] `uv sync` completes successfully
- [ ] `uv run python -c "import pytest_benchmark"` succeeds

#### Manual Verification:
- [ ] None required

---

## Phase 2: Create Benchmark Fixtures

### Overview
Create fixtures that provide appropriately-sized test data for meaningful benchmarks. The existing test fixtures (3-5 nodes) are too small - we need larger graphs that better represent real workloads.

### Changes Required:

#### 1. Create benchmark conftest.py
**File**: `tests/benchmarks/conftest.py`
**Changes**: Create new file with benchmark-specific fixtures

```python
"""Fixtures for performance benchmarks.

These fixtures provide larger test data than unit test fixtures
to produce meaningful performance measurements.
"""

import gc

import numpy as np
import pytest
from shapely import box

import geopandas as gpd

from half_america.graph.pipeline import build_graph_data, GraphData


@pytest.fixture
def benchmark_setup(benchmark):
    """Configure benchmark to disable GC during measurement."""
    benchmark.extra_info["gc_disabled"] = True
    gc.collect()
    gc.disable()
    yield
    gc.enable()


@pytest.fixture(scope="module")
def grid_20x20_gdf() -> gpd.GeoDataFrame:
    """Create a 20×20 grid of adjacent squares for benchmarking.

    This creates 400 tracts with ~1,500 edges (Queen contiguity),
    which is ~0.5% of the real dataset size but sufficient for
    meaningful benchmarks without excessive test time.

    Returns:
        GeoDataFrame with 400 square polygons in EPSG:5070
    """
    rows, cols = 20, 20
    cell_size = 1000  # 1km cells

    geometries = []
    populations = []

    for row in range(rows):
        for col in range(cols):
            x0 = col * cell_size
            y0 = row * cell_size
            geom = box(x0, y0, x0 + cell_size, y0 + cell_size)
            geometries.append(geom)
            # Vary population to create interesting optimization landscape
            populations.append(1000 * (1 + row) * (1 + col))

    gdf = gpd.GeoDataFrame(
        {"population": populations, "geometry": geometries},
        crs="EPSG:5070",
    )
    return gdf


@pytest.fixture(scope="module")
def benchmark_graph_data(grid_20x20_gdf) -> GraphData:
    """Build GraphData from 20×20 grid for benchmarking.

    This fixture is module-scoped to avoid rebuilding the graph
    for each benchmark iteration.
    """
    return build_graph_data(grid_20x20_gdf)


@pytest.fixture(scope="module")
def grid_50x50_gdf() -> gpd.GeoDataFrame:
    """Create a 50×50 grid for larger-scale benchmarks.

    This creates 2,500 tracts with ~9,800 edges, which is ~3.4%
    of the real dataset size. Use for benchmarks where you need
    to measure scaling behavior.

    Returns:
        GeoDataFrame with 2,500 square polygons in EPSG:5070
    """
    rows, cols = 50, 50
    cell_size = 1000

    geometries = []
    populations = []

    for row in range(rows):
        for col in range(cols):
            x0 = col * cell_size
            y0 = row * cell_size
            geom = box(x0, y0, x0 + cell_size, y0 + cell_size)
            geometries.append(geom)
            populations.append(1000 * (1 + row) * (1 + col))

    gdf = gpd.GeoDataFrame(
        {"population": populations, "geometry": geometries},
        crs="EPSG:5070",
    )
    return gdf


@pytest.fixture(scope="module")
def large_graph_data(grid_50x50_gdf) -> GraphData:
    """Build GraphData from 50×50 grid for scaling benchmarks."""
    return build_graph_data(grid_50x50_gdf)
```

#### 2. Create benchmark __init__.py
**File**: `tests/benchmarks/__init__.py`
**Changes**: Create new file

```python
"""Performance benchmarks for optimization engine."""
```

### Success Criteria:

#### Automated Verification:
- [ ] `uv run pytest tests/benchmarks/conftest.py --collect-only` succeeds
- [ ] Fixtures are discoverable

#### Manual Verification:
- [ ] None required

---

## Phase 3: Implement Benchmark Tests

### Overview
Create benchmark tests for the key operations identified in the research document:
1. Graph construction (`build_flow_network`)
2. Maxflow solve
3. Partition extraction (`get_partition`)
4. Binary search (`find_optimal_mu`)
5. Full sweep (`sweep_lambda`)

### Changes Required:

#### 1. Create network benchmarks
**File**: `tests/benchmarks/test_network_bench.py`
**Changes**: Create new file

```python
"""Benchmarks for flow network construction."""

import maxflow

from half_america.graph.network import build_flow_network, get_partition


class TestBuildFlowNetworkBench:
    """Benchmarks for build_flow_network()."""

    def test_build_network_20x20(self, benchmark, benchmark_graph_data):
        """Benchmark network construction on 20×20 grid (400 nodes)."""
        result = benchmark(
            build_flow_network,
            benchmark_graph_data.attributes,
            benchmark_graph_data.edges,
            lambda_param=0.5,
            mu=0.001,
        )
        assert isinstance(result, maxflow.Graph)

    def test_build_network_50x50(self, benchmark, large_graph_data):
        """Benchmark network construction on 50×50 grid (2500 nodes)."""
        result = benchmark(
            build_flow_network,
            large_graph_data.attributes,
            large_graph_data.edges,
            lambda_param=0.5,
            mu=0.001,
        )
        assert isinstance(result, maxflow.Graph)


class TestMaxflowSolveBench:
    """Benchmarks for maxflow computation."""

    def test_maxflow_solve_20x20(self, benchmark, benchmark_graph_data):
        """Benchmark maxflow solve on 20×20 grid."""
        # Build graph outside benchmark
        g = build_flow_network(
            benchmark_graph_data.attributes,
            benchmark_graph_data.edges,
            lambda_param=0.5,
            mu=0.001,
        )

        def solve():
            # Must rebuild graph each time - PyMaxFlow graphs are single-use
            g_new = build_flow_network(
                benchmark_graph_data.attributes,
                benchmark_graph_data.edges,
                lambda_param=0.5,
                mu=0.001,
            )
            return g_new.maxflow()

        result = benchmark(solve)
        assert result >= 0

    def test_maxflow_solve_50x50(self, benchmark, large_graph_data):
        """Benchmark maxflow solve on 50×50 grid."""
        def solve():
            g = build_flow_network(
                large_graph_data.attributes,
                large_graph_data.edges,
                lambda_param=0.5,
                mu=0.001,
            )
            return g.maxflow()

        result = benchmark(solve)
        assert result >= 0


class TestGetPartitionBench:
    """Benchmarks for partition extraction."""

    def test_get_partition_20x20(self, benchmark, benchmark_graph_data):
        """Benchmark partition extraction on 20×20 grid."""
        g = build_flow_network(
            benchmark_graph_data.attributes,
            benchmark_graph_data.edges,
            lambda_param=0.5,
            mu=0.001,
        )
        g.maxflow()
        num_nodes = len(benchmark_graph_data.attributes.population)

        result = benchmark(get_partition, g, num_nodes)
        assert len(result) == num_nodes

    def test_get_partition_50x50(self, benchmark, large_graph_data):
        """Benchmark partition extraction on 50×50 grid."""
        g = build_flow_network(
            large_graph_data.attributes,
            large_graph_data.edges,
            lambda_param=0.5,
            mu=0.001,
        )
        g.maxflow()
        num_nodes = len(large_graph_data.attributes.population)

        result = benchmark(get_partition, g, num_nodes)
        assert len(result) == num_nodes
```

#### 2. Create solver benchmarks
**File**: `tests/benchmarks/test_solver_bench.py`
**Changes**: Create new file

```python
"""Benchmarks for optimization solver."""

from half_america.optimization.search import find_optimal_mu
from half_america.optimization.sweep import sweep_lambda


class TestFindOptimalMuBench:
    """Benchmarks for binary search optimization."""

    def test_find_optimal_mu_20x20(self, benchmark, benchmark_graph_data):
        """Benchmark binary search on 20×20 grid."""
        result = benchmark(
            find_optimal_mu,
            benchmark_graph_data,
            lambda_param=0.5,
            target_fraction=0.5,
            tolerance=0.01,
            verbose=False,
        )
        assert result.converged
        assert 0.49 <= result.result.population_fraction <= 0.51

    def test_find_optimal_mu_50x50(self, benchmark, large_graph_data):
        """Benchmark binary search on 50×50 grid."""
        result = benchmark(
            find_optimal_mu,
            large_graph_data,
            lambda_param=0.5,
            target_fraction=0.5,
            tolerance=0.01,
            verbose=False,
        )
        assert result.converged


class TestSweepLambdaBench:
    """Benchmarks for full lambda sweep."""

    def test_sweep_3_lambdas_20x20(self, benchmark, benchmark_graph_data):
        """Benchmark sweep with 3 lambda values on 20×20 grid."""
        result = benchmark(
            sweep_lambda,
            benchmark_graph_data,
            lambda_values=[0.0, 0.5, 0.9],
            tolerance=0.01,
            max_workers=1,  # Sequential for reproducible timing
            verbose=False,
        )
        assert result.all_converged
        assert len(result.results) == 3

    def test_sweep_parallel_20x20(self, benchmark, benchmark_graph_data):
        """Benchmark parallel sweep on 20×20 grid."""
        result = benchmark(
            sweep_lambda,
            benchmark_graph_data,
            lambda_values=[0.0, 0.5, 0.9],
            tolerance=0.01,
            max_workers=3,  # Parallel
            verbose=False,
        )
        assert result.all_converged
```

### Success Criteria:

#### Automated Verification:
- [ ] `uv run pytest tests/benchmarks/ --benchmark-only` runs all benchmarks
- [ ] All benchmarks pass (assertions hold)
- [ ] Benchmark output shows timing statistics

#### Manual Verification:
- [ ] Review benchmark output for reasonable timing values
- [ ] Verify 50×50 benchmarks take noticeably longer than 20×20 (confirms scaling)

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation that the benchmark output looks reasonable before proceeding to Phase 4.

---

## Phase 4: Run Benchmarks and Document Baselines

### Overview
Run the complete benchmark suite and document baseline performance in a new research document.

### Changes Required:

#### 1. Run benchmarks with statistics
Execute:
```bash
uv run pytest tests/benchmarks/ --benchmark-only --benchmark-sort=name
```

#### 2. Create baseline documentation
**File**: `thoughts/shared/research/2025-11-21-benchmark-baselines.md`
**Changes**: Create new file documenting baseline performance

The file should follow this template:
```markdown
---
date: 2025-11-21
researcher: [Name]
git_commit: [commit hash]
branch: master
topic: "Performance Benchmark Baselines"
tags: [research, performance, benchmarks, baseline]
status: complete
---

# Benchmark Baselines

**Date**: 2025-11-21
**Hardware**: [CPU model, RAM, OS]
**Python**: [version]
**PyMaxFlow**: [version]

## Summary

Initial performance baselines for the optimization engine using pytest-benchmark.

## Results

### Graph Construction (build_flow_network)

| Grid Size | Nodes | Edges | Mean | Std Dev | Min | Max |
|-----------|-------|-------|------|---------|-----|-----|
| 20×20 | 400 | ~1,500 | X.XXms | X.XXms | X.XXms | X.XXms |
| 50×50 | 2,500 | ~9,800 | X.XXms | X.XXms | X.XXms | X.XXms |

### Maxflow Solve

| Grid Size | Mean | Std Dev | Notes |
|-----------|------|---------|-------|
| 20×20 | X.XXms | X.XXms | Includes graph construction |
| 50×50 | X.XXms | X.XXms | Includes graph construction |

### Binary Search (find_optimal_mu)

| Grid Size | Mean | Iterations (typical) | Notes |
|-----------|------|---------------------|-------|
| 20×20 | X.XXs | ~15-20 | λ=0.5, tolerance=1% |
| 50×50 | X.XXs | ~15-20 | λ=0.5, tolerance=1% |

### Full Sweep (sweep_lambda)

| Grid Size | Lambda Values | Sequential | Parallel (3 workers) |
|-----------|---------------|------------|---------------------|
| 20×20 | 3 | X.XXs | X.XXs |

## Extrapolation to Full Dataset

The full dataset has ~73,000 nodes and ~292,000 edges.

Based on observed scaling:
- [Analysis of expected performance on full dataset]

## Recommendations

Based on these baselines:
1. [Recommendation 1]
2. [Recommendation 2]
```

### Success Criteria:

#### Automated Verification:
- [ ] Benchmark command completes without errors
- [ ] All benchmarks pass

#### Manual Verification:
- [ ] Baseline document created with actual benchmark values
- [ ] Scaling behavior is reasonable (50×50 takes longer than 20×20)
- [ ] Results match expected order of magnitude from research document

---

## Phase 5: Update ROADMAP.md

### Overview
Update ROADMAP.md to mark benchmark infrastructure as complete and add a new item for performance optimization based on benchmark results.

### Changes Required:

#### 1. Update Phase 3 milestones
**File**: `ROADMAP.md`
**Changes**: Update the performance benchmarking milestone

Replace:
```markdown
- [ ] Performance benchmarking and optimization
```

With:
```markdown
- [x] Performance benchmarking infrastructure (pytest-benchmark suite)
- [ ] Performance optimization (based on benchmark analysis)
```

### Success Criteria:

#### Automated Verification:
- [ ] `cat ROADMAP.md | grep -A2 "Performance"` shows updated milestones

#### Manual Verification:
- [ ] ROADMAP accurately reflects current state

---

## Testing Strategy

### Benchmark Tests:
- All benchmarks should pass assertions
- 50×50 grid benchmarks should take measurably longer than 20×20
- Parallel sweep should not be significantly slower than sequential (may be faster)

### Unit Tests:
- Existing unit tests in `tests/test_optimization/` should continue to pass
- New benchmark fixtures should not interfere with existing tests

### Manual Testing Steps:
1. Run `uv run pytest tests/benchmarks/ --benchmark-only` and verify output
2. Run `uv run pytest tests/` to ensure no regressions in existing tests
3. Review benchmark statistics for reasonable values

## Performance Considerations

The benchmark fixtures create grids of 400 and 2,500 nodes. These are intentionally smaller than the real dataset (73,000 nodes) to keep benchmark runtime reasonable while still producing meaningful measurements.

For occasional profiling of the full dataset, use:
```bash
uv run scalene --cpu src/half_america/cli.py optimize --lambda 0.5
```

## References

- Research document: `thoughts/shared/research/2025-11-21-performance-benchmarking-optimization.md`
- pytest-benchmark docs: https://pytest-benchmark.readthedocs.io/
- Existing timing code: `src/half_america/optimization/sweep.py:42-54`
