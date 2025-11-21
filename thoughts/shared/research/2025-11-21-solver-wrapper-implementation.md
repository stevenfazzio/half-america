---
date: 2025-11-21T13:00:00-08:00
researcher: Claude
git_commit: 0410a86742732f24d5cedfa857e3ac4d96acba23
branch: master
repository: half_america
topic: "Implement graph-cut solver wrapper"
tags: [research, codebase, optimization, solver, implementation]
status: complete
last_updated: 2025-11-21
last_updated_by: Claude
---

# Research: Implement Graph-Cut Solver Wrapper

**Date**: 2025-11-21T13:00:00-08:00
**Researcher**: Claude
**Git Commit**: 0410a86742732f24d5cedfa857e3ac4d96acba23
**Branch**: master
**Repository**: half_america

## Research Question

How to implement the "graph-cut solver wrapper" milestone from ROADMAP.md Phase 3?

## Summary

The solver wrapper is a thin layer over existing `build_flow_network()` and `get_partition()` that:
1. Takes `GraphData` + parameters (λ, μ) as input
2. Runs the max-flow optimization
3. Returns an `OptimizationResult` with partition, statistics, and parameters

**Key deliverables:**
- `OptimizationResult` NamedTuple following codebase patterns
- `solve_partition()` function with verbose output
- Unit tests following `test_network.py` patterns
- Module structure in `src/half_america/optimization/`

## Detailed Findings

### Existing Infrastructure

The solver wrapper builds directly on these implemented functions:

| Function | Location | What It Does |
|----------|----------|--------------|
| `build_flow_network()` | `network.py:9-53` | Constructs PyMaxFlow graph with t-links and n-links |
| `get_partition()` | `network.py:56-67` | Extracts boolean partition after maxflow |
| `GraphData` | `pipeline.py:16-22` | Input container with edges and attributes |
| `GraphAttributes` | `boundary.py:10-16` | population[], area[], rho, edge_lengths |

### Implementation Specification

#### 1. File Structure

Create new module: `src/half_america/optimization/`

```
src/half_america/optimization/
├── __init__.py           # Public exports
└── solver.py             # OptimizationResult + solve_partition()
```

#### 2. OptimizationResult Definition

Following codebase NamedTuple patterns (see `AdjacencyResult`, `CleaningStats`, `GraphAttributes`):

```python
# src/half_america/optimization/solver.py

from typing import NamedTuple
import numpy as np

class OptimizationResult(NamedTuple):
    """Result from graph cut optimization."""

    partition: np.ndarray       # Boolean array: True = selected (source partition)
    selected_population: int    # Sum of p_i for selected tracts
    selected_area: float        # Sum of a_i for selected tracts in sq meters
    total_population: int       # Total population across all tracts
    total_area: float           # Total area in sq meters
    population_fraction: float  # selected_population / total_population
    lambda_param: float         # Surface tension parameter used
    mu: float                   # Lagrange multiplier used
    flow_value: float           # Minimum cut value from maxflow
```

**Design decisions:**
- All statistics pre-computed (no downstream recalculation needed)
- Both selected and total values stored (enables fraction verification)
- Parameters stored for reproducibility
- Flow value stored for debugging/analysis

#### 3. solve_partition() Function

```python
# src/half_america/optimization/solver.py

import numpy as np
import maxflow

from half_america.graph.network import build_flow_network, get_partition
from half_america.graph.pipeline import GraphData


def solve_partition(
    graph_data: GraphData,
    lambda_param: float,
    mu: float,
    verbose: bool = True,
) -> OptimizationResult:
    """
    Solve graph cut optimization for given parameters.

    Args:
        graph_data: GraphData from load_graph_data()
        lambda_param: Surface tension parameter [0, 1]
        mu: Lagrange multiplier for population constraint
        verbose: Print diagnostic output

    Returns:
        OptimizationResult with partition and statistics
    """
    if verbose:
        print(f"Solving partition for λ={lambda_param:.2f}, μ={mu:.6f}...")

    # Build and solve flow network
    g = build_flow_network(
        graph_data.attributes,
        graph_data.edges,
        lambda_param,
        mu,
    )
    flow_value = g.maxflow()
    partition = get_partition(g, graph_data.num_nodes)

    # Compute statistics
    attrs = graph_data.attributes
    selected_population = int(attrs.population[partition].sum())
    selected_area = float(attrs.area[partition].sum())
    total_population = int(attrs.population.sum())
    total_area = float(attrs.area.sum())
    population_fraction = selected_population / total_population

    if verbose:
        print(f"  Selected: {partition.sum():,} / {graph_data.num_nodes:,} tracts")
        print(f"  Population: {selected_population:,} / {total_population:,} ({100*population_fraction:.2f}%)")
        print(f"  Area: {selected_area/1e6:.0f} / {total_area/1e6:.0f} km²")
        print(f"  Flow value: {flow_value:.2f}")

    return OptimizationResult(
        partition=partition,
        selected_population=selected_population,
        selected_area=selected_area,
        total_population=total_population,
        total_area=total_area,
        population_fraction=population_fraction,
        lambda_param=lambda_param,
        mu=mu,
        flow_value=flow_value,
    )
```

#### 4. Module Exports

```python
# src/half_america/optimization/__init__.py

"""Optimization module for graph cut partition."""

from half_america.optimization.solver import OptimizationResult, solve_partition

__all__ = [
    "OptimizationResult",
    "solve_partition",
]
```

### Test Specification

#### Test File Structure

```
tests/test_optimization/
├── __init__.py
├── conftest.py          # Fixtures
└── test_solver.py       # Unit tests
```

#### Test Fixtures

```python
# tests/test_optimization/conftest.py

import pytest
import numpy as np
from half_america.graph.boundary import GraphAttributes
from half_america.graph.pipeline import GraphData


@pytest.fixture
def simple_graph_data():
    """Create minimal 3-node GraphData for testing."""
    attributes = GraphAttributes(
        population=np.array([100, 200, 300]),
        area=np.array([1000.0, 1000.0, 1000.0]),
        rho=100.0,
        edge_lengths={(0, 1): 50.0, (1, 0): 50.0, (1, 2): 50.0, (2, 1): 50.0},
    )
    return GraphData(
        edges=[(0, 1), (1, 2)],
        attributes=attributes,
        num_nodes=3,
        num_edges=2,
    )
```

#### Unit Tests

```python
# tests/test_optimization/test_solver.py

import pytest
import numpy as np
from half_america.optimization import solve_partition, OptimizationResult


class TestSolvePartition:
    """Tests for solve_partition function."""

    def test_returns_optimization_result(self, simple_graph_data):
        """Test that function returns OptimizationResult."""
        result = solve_partition(
            simple_graph_data,
            lambda_param=0.5,
            mu=0.01,
            verbose=False,
        )
        assert isinstance(result, OptimizationResult)

    def test_partition_is_boolean_array(self, simple_graph_data):
        """Test partition format."""
        result = solve_partition(
            simple_graph_data,
            lambda_param=0.5,
            mu=0.01,
            verbose=False,
        )
        assert result.partition.dtype == bool
        assert len(result.partition) == 3

    def test_high_mu_selects_all(self, simple_graph_data):
        """Test that high mu selects all nodes."""
        result = solve_partition(
            simple_graph_data,
            lambda_param=0.5,
            mu=1000.0,
            verbose=False,
        )
        assert result.partition.all()
        assert result.selected_population == 600  # 100 + 200 + 300
        assert result.population_fraction == pytest.approx(1.0)

    def test_zero_mu_selects_none(self, simple_graph_data):
        """Test that zero mu selects no nodes."""
        result = solve_partition(
            simple_graph_data,
            lambda_param=0.5,
            mu=0.0,
            verbose=False,
        )
        assert not result.partition.any()
        assert result.selected_population == 0
        assert result.population_fraction == pytest.approx(0.0)

    def test_stores_parameters(self, simple_graph_data):
        """Test that parameters are stored in result."""
        result = solve_partition(
            simple_graph_data,
            lambda_param=0.7,
            mu=0.05,
            verbose=False,
        )
        assert result.lambda_param == 0.7
        assert result.mu == 0.05

    def test_statistics_are_consistent(self, simple_graph_data):
        """Test that statistics are internally consistent."""
        result = solve_partition(
            simple_graph_data,
            lambda_param=0.5,
            mu=0.01,
            verbose=False,
        )
        # Population fraction should match selected/total
        expected_fraction = result.selected_population / result.total_population
        assert result.population_fraction == pytest.approx(expected_fraction)

        # Total population should match input
        assert result.total_population == 600  # 100 + 200 + 300

    def test_flow_value_non_negative(self, simple_graph_data):
        """Test that flow value is non-negative."""
        result = solve_partition(
            simple_graph_data,
            lambda_param=0.5,
            mu=0.01,
            verbose=False,
        )
        assert result.flow_value >= 0
```

### Verbose Output Pattern

Following codebase conventions from `cleaning.py`, `adjacency.py`, `boundary.py`:

```python
if verbose:
    print(f"Solving partition for λ={lambda_param:.2f}, μ={mu:.6f}...")
    # ... operation ...
    print(f"  Selected: {partition.sum():,} / {graph_data.num_nodes:,} tracts")
    print(f"  Population: {selected_population:,} / {total_population:,} ({100*population_fraction:.2f}%)")
```

**Conventions:**
- Main operation message starts immediately
- Sub-messages indented with 2 spaces
- Numbers with thousands separators (`:,`)
- Percentages with 2 decimal places (`:.2f%`)
- Scientific values with 6 decimal places for μ (`:.6f`)

## Code References

- `src/half_america/graph/network.py:9-53` - `build_flow_network()` to wrap
- `src/half_america/graph/network.py:56-67` - `get_partition()` to wrap
- `src/half_america/graph/pipeline.py:16-22` - `GraphData` input type
- `src/half_america/graph/boundary.py:10-16` - `GraphAttributes` for statistics
- `src/half_america/graph/adjacency.py:10-17` - `AdjacencyResult` pattern to follow
- `src/half_america/data/cleaning.py:10-17` - `CleaningStats` pattern to follow
- `tests/test_graph/test_network.py:9-17` - Test fixture pattern
- `tests/test_graph/test_network.py:30-48` - High/zero mu test patterns

## Architecture Insights

### Design Patterns Applied

1. **NamedTuple for results** - Immutable, hashable, consistent with codebase
2. **Pre-computed statistics** - All derived values calculated once
3. **Verbose parameter** - Follows `verbose: bool = True` convention
4. **Thin wrapper** - Minimal logic, delegates to existing functions

### Module Boundaries

```
graph.pipeline.GraphData
        │
        ▼
optimization.solver.solve_partition()
        │
        ├── graph.network.build_flow_network()
        ├── maxflow.Graph.maxflow()
        └── graph.network.get_partition()
        │
        ▼
optimization.solver.OptimizationResult
```

### Future Extensions

The `solve_partition()` function will be called by:
- `search.py:find_optimal_mu()` - Binary search loop
- `sweep.py:sweep_lambda()` - Parameter sweep
- CLI for single-run testing

## Historical Context (from thoughts/)

- `thoughts/shared/research/2025-11-21-phase3-optimization-engine.md` - Overall Phase 3 research

## Related Research

- [Phase 3 Optimization Engine](2025-11-21-phase3-optimization-engine.md) - Parent research document

## Open Questions

1. **Population fraction tolerance**: Should `OptimizationResult` include a `satisfied_target` boolean field?
2. **Error handling**: Should invalid parameters (λ < 0 or > 1) raise ValueError?
3. **Caching**: Should solved partitions be cached, or defer to sweep module?

## Implementation Checklist

- [ ] Create `src/half_america/optimization/` directory
- [ ] Create `src/half_america/optimization/__init__.py`
- [ ] Create `src/half_america/optimization/solver.py` with:
  - [ ] `OptimizationResult` NamedTuple
  - [ ] `solve_partition()` function
- [ ] Create `tests/test_optimization/` directory
- [ ] Create `tests/test_optimization/__init__.py`
- [ ] Create `tests/test_optimization/conftest.py` with fixtures
- [ ] Create `tests/test_optimization/test_solver.py` with unit tests
- [ ] Run tests: `uv run pytest tests/test_optimization/ -v`
- [ ] Run type check: `uv run mypy src/half_america/optimization/`
- [ ] Update ROADMAP.md to mark milestone complete
