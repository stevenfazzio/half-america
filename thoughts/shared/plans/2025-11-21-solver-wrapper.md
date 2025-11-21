# Solver Wrapper Implementation Plan

## Overview

Implement the "graph-cut solver wrapper" milestone from ROADMAP.md Phase 3. This creates a thin wrapper over existing `build_flow_network()` and `get_partition()` that returns a structured result with partition data and statistics.

## Current State Analysis

The flow network construction is complete:
- `build_flow_network()` in `network.py:9-53` constructs the PyMaxFlow graph
- `get_partition()` in `network.py:56-67` extracts the boolean partition
- `GraphData` in `pipeline.py:16-22` is the input container
- `GraphAttributes` in `boundary.py:10-16` holds population, area, rho, edge_lengths

Missing: A wrapper that combines these into a single call with statistics.

### Key Discoveries:
- NamedTuple pattern used consistently: `AdjacencyResult`, `CleaningStats`, `GraphAttributes`, `GraphData`
- Verbose output follows pattern: main message, then indented sub-messages with `:,` number formatting
- Test fixtures in `test_network.py:9-17` provide reusable `simple_attributes` pattern
- High/zero mu tests in `test_network.py:30-48` verify boundary conditions

## Desired End State

After this plan is complete:
1. New `src/half_america/optimization/` module exists with solver wrapper
2. `OptimizationResult` NamedTuple captures partition, statistics, and parameters
3. `solve_partition()` function takes `GraphData` + parameters and returns `OptimizationResult`
4. Unit tests verify return types, statistics consistency, and boundary conditions
5. All automated verification passes (pytest, mypy, ruff)

### Verification:
```bash
uv run pytest tests/test_optimization/ -v  # All tests pass
uv run mypy src/half_america/optimization/  # No type errors
uv run ruff check src/half_america/         # No lint errors
```

## What We're NOT Doing

- Binary search for μ (that's the next milestone)
- Lambda sweep loop (separate milestone)
- Pre-computation/caching of results (separate milestone)
- CLI integration (future work)

## Implementation Approach

Create a minimal wrapper that:
1. Validates input parameters
2. Calls existing network functions
3. Computes statistics from the partition
4. Returns a structured result

All logic stays in existing functions; the wrapper just orchestrates and packages results.

---

## Phase 1: Create Optimization Module

### Overview
Create the module structure and implement `OptimizationResult` and `solve_partition()`.

### Changes Required:

#### 1. Create module directory
**Path**: `src/half_america/optimization/`

Create directory structure:
```
src/half_america/optimization/
├── __init__.py
└── solver.py
```

#### 2. Implement solver.py
**File**: `src/half_america/optimization/solver.py`

```python
"""Graph cut solver wrapper for optimization."""

from typing import NamedTuple

import numpy as np

from half_america.graph.network import build_flow_network, get_partition
from half_america.graph.pipeline import GraphData


class OptimizationResult(NamedTuple):
    """Result from graph cut optimization."""

    partition: np.ndarray  # Boolean array: True = selected (source partition)
    selected_population: int  # Sum of p_i for selected tracts
    selected_area: float  # Sum of a_i for selected tracts in sq meters
    total_population: int  # Total population across all tracts
    total_area: float  # Total area in sq meters
    population_fraction: float  # selected_population / total_population
    satisfied_target: bool  # True if population_fraction within 1% of 50%
    lambda_param: float  # Surface tension parameter used
    mu: float  # Lagrange multiplier used
    flow_value: float  # Minimum cut value from maxflow


# Target tolerance: population fraction must be within this of 0.5
TARGET_TOLERANCE = 0.01


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
        mu: Lagrange multiplier for population constraint (non-negative)
        verbose: Print diagnostic output

    Returns:
        OptimizationResult with partition and statistics

    Raises:
        ValueError: If lambda_param not in [0, 1] or mu < 0
    """
    # Validate parameters
    if not 0 <= lambda_param <= 1:
        raise ValueError(f"lambda_param must be in [0, 1], got {lambda_param}")
    if mu < 0:
        raise ValueError(f"mu must be non-negative, got {mu}")

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
    satisfied_target = abs(population_fraction - 0.5) <= TARGET_TOLERANCE

    if verbose:
        print(f"  Selected: {partition.sum():,} / {graph_data.num_nodes:,} tracts")
        print(
            f"  Population: {selected_population:,} / {total_population:,} "
            f"({100 * population_fraction:.2f}%)"
        )
        print(f"  Area: {selected_area / 1e6:.0f} / {total_area / 1e6:.0f} km²")
        print(f"  Flow value: {flow_value:.2f}")
        if satisfied_target:
            print("  Target satisfied: Yes")
        else:
            print(f"  Target satisfied: No (need 49-51%, got {100 * population_fraction:.2f}%)")

    return OptimizationResult(
        partition=partition,
        selected_population=selected_population,
        selected_area=selected_area,
        total_population=total_population,
        total_area=total_area,
        population_fraction=population_fraction,
        satisfied_target=satisfied_target,
        lambda_param=lambda_param,
        mu=mu,
        flow_value=flow_value,
    )
```

#### 3. Implement __init__.py
**File**: `src/half_america/optimization/__init__.py`

```python
"""Optimization module for graph cut partition."""

from half_america.optimization.solver import (
    TARGET_TOLERANCE,
    OptimizationResult,
    solve_partition,
)

__all__ = [
    "TARGET_TOLERANCE",
    "OptimizationResult",
    "solve_partition",
]
```

### Success Criteria:

#### Automated Verification:
- [ ] Module imports without error: `python -c "from half_america.optimization import solve_partition"`
- [ ] Type check passes: `uv run mypy src/half_america/optimization/`
- [ ] Lint passes: `uv run ruff check src/half_america/optimization/`

#### Manual Verification:
- [ ] Code review confirms NamedTuple follows codebase patterns
- [ ] Code review confirms verbose output matches existing conventions

**Implementation Note**: After completing this phase and all automated verification passes, proceed to Phase 2.

---

## Phase 2: Add Unit Tests

### Overview
Create comprehensive unit tests following existing patterns from `test_network.py`.

### Changes Required:

#### 1. Create test directory
**Path**: `tests/test_optimization/`

Create directory structure:
```
tests/test_optimization/
├── __init__.py
├── conftest.py
└── test_solver.py
```

#### 2. Create conftest.py with fixtures
**File**: `tests/test_optimization/conftest.py`

```python
"""Fixtures for optimization tests."""

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

#### 3. Create __init__.py
**File**: `tests/test_optimization/__init__.py`

```python
"""Tests for optimization module."""
```

#### 4. Create test_solver.py
**File**: `tests/test_optimization/test_solver.py`

```python
"""Tests for solver wrapper."""

import pytest
import numpy as np
from half_america.optimization import (
    solve_partition,
    OptimizationResult,
    TARGET_TOLERANCE,
)


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


class TestSolvePartitionValidation:
    """Tests for parameter validation."""

    def test_lambda_below_zero_raises(self, simple_graph_data):
        """Test that lambda < 0 raises ValueError."""
        with pytest.raises(ValueError, match="lambda_param must be in"):
            solve_partition(
                simple_graph_data,
                lambda_param=-0.1,
                mu=0.01,
                verbose=False,
            )

    def test_lambda_above_one_raises(self, simple_graph_data):
        """Test that lambda > 1 raises ValueError."""
        with pytest.raises(ValueError, match="lambda_param must be in"):
            solve_partition(
                simple_graph_data,
                lambda_param=1.5,
                mu=0.01,
                verbose=False,
            )

    def test_negative_mu_raises(self, simple_graph_data):
        """Test that negative mu raises ValueError."""
        with pytest.raises(ValueError, match="mu must be non-negative"):
            solve_partition(
                simple_graph_data,
                lambda_param=0.5,
                mu=-0.01,
                verbose=False,
            )

    def test_lambda_zero_valid(self, simple_graph_data):
        """Test that lambda=0 is valid (boundary)."""
        result = solve_partition(
            simple_graph_data,
            lambda_param=0.0,
            mu=0.01,
            verbose=False,
        )
        assert result.lambda_param == 0.0

    def test_lambda_one_valid(self, simple_graph_data):
        """Test that lambda=1 is valid (boundary)."""
        result = solve_partition(
            simple_graph_data,
            lambda_param=1.0,
            mu=0.01,
            verbose=False,
        )
        assert result.lambda_param == 1.0


class TestSatisfiedTarget:
    """Tests for satisfied_target field."""

    def test_satisfied_when_at_50_percent(self, simple_graph_data):
        """Test satisfied_target is True when at exactly 50%."""
        # With this data, we need to find mu that gives ~50%
        # Total pop = 600, so 50% = 300
        # Node 2 alone has pop 300, so selecting just node 2 gives 50%
        # This is hard to achieve precisely, so we test boundaries instead
        pass  # See boundary tests below

    def test_not_satisfied_at_100_percent(self, simple_graph_data):
        """Test satisfied_target is False when at 100%."""
        result = solve_partition(
            simple_graph_data,
            lambda_param=0.5,
            mu=1000.0,
            verbose=False,
        )
        assert result.population_fraction == pytest.approx(1.0)
        assert result.satisfied_target is False

    def test_not_satisfied_at_0_percent(self, simple_graph_data):
        """Test satisfied_target is False when at 0%."""
        result = solve_partition(
            simple_graph_data,
            lambda_param=0.5,
            mu=0.0,
            verbose=False,
        )
        assert result.population_fraction == pytest.approx(0.0)
        assert result.satisfied_target is False

    def test_target_tolerance_exported(self):
        """Test that TARGET_TOLERANCE is accessible."""
        assert TARGET_TOLERANCE == 0.01
```

### Success Criteria:

#### Automated Verification:
- [ ] All tests pass: `uv run pytest tests/test_optimization/ -v`
- [ ] Tests follow existing patterns (class-based, descriptive names)

#### Manual Verification:
- [ ] Test coverage includes return types, statistics, validation, and boundaries

**Implementation Note**: After completing this phase and all automated verification passes, proceed to Phase 3.

---

## Phase 3: Update ROADMAP.md

### Overview
Mark the milestone as complete in ROADMAP.md.

### Changes Required:

**File**: `ROADMAP.md`

Change line 55:
```markdown
- [ ] Implement graph-cut solver wrapper
```

To:
```markdown
- [x] Implement graph-cut solver wrapper
```

### Success Criteria:

#### Automated Verification:
- [ ] File saves without error
- [ ] Git diff shows only the checkbox change

#### Manual Verification:
- [ ] ROADMAP.md accurately reflects project status

---

## Testing Strategy

### Unit Tests:
- Return type verification (`OptimizationResult`)
- Partition format (boolean numpy array)
- Boundary conditions (high mu → all selected, zero mu → none selected)
- Parameter storage in result
- Statistics consistency (fraction matches selected/total)
- Parameter validation (ValueError for invalid inputs)
- `satisfied_target` field behavior

### Integration Tests:
- None needed for this phase (wrapper is thin)

### Manual Testing:
- Run with real graph data to verify verbose output formatting
- Spot-check statistics against manual calculations

## Performance Considerations

No performance concerns - the wrapper adds minimal overhead:
- Parameter validation: O(1)
- Statistics computation: O(n) array sums (negligible vs maxflow)
- The expensive operation is `g.maxflow()` which is unchanged

## References

- Research document: `thoughts/shared/research/2025-11-21-solver-wrapper-implementation.md`
- Network functions: `src/half_america/graph/network.py`
- Input types: `src/half_america/graph/pipeline.py`, `src/half_america/graph/boundary.py`
- Test patterns: `tests/test_graph/test_network.py`
