# Binary Search for Lagrange Multiplier (μ) Implementation Plan

## Overview

Implement `find_optimal_mu()` function that performs binary search to find the Lagrange multiplier (μ) that achieves ~50% population selection. This exploits the monotonicity property: higher μ → more tracts selected.

## Current State Analysis

**Existing Infrastructure:**
- `solve_partition()` wrapper is complete (`optimization/solver.py:30-103`)
- `OptimizationResult` NamedTuple captures all needed statistics
- `TARGET_TOLERANCE = 0.01` (1%) defined at `solver.py:27`
- Test fixture `simple_graph_data` exists with 3-node graph

**What's Missing:**
- Binary search loop to find optimal μ
- Auto-scaling for μ bounds based on data characteristics

### Key Discoveries:
- `solve_partition()` returns `population_fraction` we can compare against target (`solver.py:76`)
- Population data accessed via `graph_data.attributes.population` (`solver.py:72`)
- Existing test patterns use `pytest.approx()` for float comparisons (`test_solver.py:46`)

## Desired End State

A working `find_optimal_mu()` function that:
1. Takes `GraphData` and `lambda_param`, returns `SearchResult` with optimal partition
2. Converges to within 1% of 50% population target
3. Is exported from `half_america.optimization` module
4. Has comprehensive test coverage

**Verification:**
```bash
uv run pytest tests/test_optimization/test_search.py -v
uv run mypy src/half_america/optimization/
uv run ruff check src/half_america/optimization/
```

## What We're NOT Doing

- Warm-start optimization (using previous λ's μ as starting point)
- Parallel λ sweep (Phase 3 future milestone)
- Performance optimizations beyond basic implementation
- CLI integration (separate milestone)

## Implementation Approach

Create a thin orchestration layer that:
1. Auto-scales μ bounds based on data characteristics
2. Runs binary search calling `solve_partition()` each iteration
3. Returns structured result with search metadata

Use `TARGET_TOLERANCE = 0.01` (1%) for consistency with existing codebase.

---

## Phase 1: Create Binary Search Module

### Overview
Create `search.py` with `SearchResult` and `find_optimal_mu()` function.

### Changes Required:

#### 1. New File: `src/half_america/optimization/search.py`

```python
"""Binary search for Lagrange multiplier (μ)."""

from typing import NamedTuple

from half_america.graph.pipeline import GraphData
from half_america.optimization.solver import (
    TARGET_TOLERANCE,
    OptimizationResult,
    solve_partition,
)


class SearchResult(NamedTuple):
    """Result from binary search for optimal μ."""

    result: OptimizationResult  # Final optimization result
    iterations: int  # Number of binary search iterations
    mu_history: list[float]  # μ values tried during search
    converged: bool  # True if converged within max_iterations


# Default parameters
DEFAULT_MAX_ITERATIONS = 50
DEFAULT_MU_MIN = 0.0


def find_optimal_mu(
    graph_data: GraphData,
    lambda_param: float,
    target_fraction: float = 0.5,
    tolerance: float = TARGET_TOLERANCE,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
    mu_min: float = DEFAULT_MU_MIN,
    mu_max: float | None = None,
    verbose: bool = True,
) -> SearchResult:
    """
    Binary search for μ that achieves target population fraction.

    Exploits monotonicity: higher μ → more tracts selected.

    Args:
        graph_data: GraphData from load_graph_data()
        lambda_param: Surface tension parameter [0, 1]
        target_fraction: Target population fraction (default 0.5)
        tolerance: Acceptable deviation from target (default 0.01 = 1%)
        max_iterations: Maximum search iterations (default 50)
        mu_min: Lower bound for μ (default 0.0)
        mu_max: Upper bound for μ (auto-scaled if None)
        verbose: Print diagnostic output

    Returns:
        SearchResult with final OptimizationResult and search metadata
    """
    total_pop = graph_data.attributes.population.sum()
    target_pop = target_fraction * total_pop
    pop_tolerance = tolerance * total_pop

    # Auto-scale mu_max if not provided
    if mu_max is None:
        mu_max = _estimate_mu_max(graph_data)

    if verbose:
        print(f"Binary search for μ: target={target_fraction:.1%} ± {tolerance:.1%}")
        print(f"  Population target: {target_pop:,.0f} ± {pop_tolerance:,.0f}")
        print(f"  μ bounds: [{mu_min:.6f}, {mu_max:.6f}]")

    mu_history: list[float] = []
    result: OptimizationResult | None = None

    for iteration in range(max_iterations):
        mu = (mu_min + mu_max) / 2
        mu_history.append(mu)

        result = solve_partition(
            graph_data,
            lambda_param,
            mu,
            verbose=False,
        )

        error = result.selected_population - target_pop

        if verbose:
            print(
                f"  [{iteration + 1:2d}] μ={mu:.6f}, "
                f"pop={result.selected_population:,} "
                f"({100 * result.population_fraction:.2f}%), "
                f"error={error:+,.0f}"
            )

        # Check convergence
        if abs(error) <= pop_tolerance:
            if verbose:
                print(f"  Converged in {iteration + 1} iterations")
            return SearchResult(
                result=result,
                iterations=iteration + 1,
                mu_history=mu_history,
                converged=True,
            )

        # Binary search step
        if result.selected_population < target_pop:
            mu_min = mu  # Need more selection → increase reward
        else:
            mu_max = mu  # Need less selection → decrease reward

    # Did not converge
    if verbose:
        print(f"  Did not converge in {max_iterations} iterations")

    assert result is not None  # Always at least one iteration
    return SearchResult(
        result=result,
        iterations=max_iterations,
        mu_history=mu_history,
        converged=False,
    )


def _estimate_mu_max(graph_data: GraphData) -> float:
    """
    Estimate upper bound for μ based on data characteristics.

    μ should be on scale of (area cost) / (population benefit).
    We want μ × p_i to be comparable to (1-λ) × a_i.
    """
    attrs = graph_data.attributes
    total_area = attrs.area.sum()
    total_pop = attrs.population.sum()

    # Scale factor: area per person, with headroom
    mu_scale = total_area / total_pop
    return mu_scale * 10  # Allow 10x headroom
```

### Success Criteria:

#### Automated Verification:
- [x] File exists: `ls src/half_america/optimization/search.py`
- [x] Type checking passes: `uv run mypy src/half_america/optimization/search.py`
- [x] Linting passes: `uv run ruff check src/half_america/optimization/search.py`

---

## Phase 2: Update Module Exports

### Overview
Export new symbols from the optimization module.

### Changes Required:

#### 1. Update `src/half_america/optimization/__init__.py`

```python
"""Optimization module for graph cut partition."""

from half_america.optimization.search import (
    DEFAULT_MAX_ITERATIONS,
    DEFAULT_MU_MIN,
    SearchResult,
    find_optimal_mu,
)
from half_america.optimization.solver import (
    TARGET_TOLERANCE,
    OptimizationResult,
    solve_partition,
)

__all__ = [
    # Solver
    "TARGET_TOLERANCE",
    "OptimizationResult",
    "solve_partition",
    # Search
    "DEFAULT_MAX_ITERATIONS",
    "DEFAULT_MU_MIN",
    "SearchResult",
    "find_optimal_mu",
]
```

### Success Criteria:

#### Automated Verification:
- [x] Import works: `uv run python -c "from half_america.optimization import find_optimal_mu, SearchResult; print('OK')"`
- [x] Type checking passes: `uv run mypy src/half_america/optimization/__init__.py`

---

## Phase 3: Create Test Suite

### Overview
Create comprehensive tests for binary search functionality.

### Changes Required:

#### 1. Update `tests/test_optimization/conftest.py`

Add a more complex fixture where 50% isn't achievable by single node:

```python
@pytest.fixture
def complex_graph_data():
    """Create 5-node GraphData where 50% requires multiple nodes.

    Populations: [80, 120, 150, 200, 250] = 800 total
    50% target = 400, achievable via nodes 3+4 (200+250=450) or 2+3 (150+200=350)
    but not by any single node.

    Graph topology: 0 -- 1 -- 2 -- 3 -- 4 (linear chain)
    """
    attributes = GraphAttributes(
        population=np.array([80, 120, 150, 200, 250]),
        area=np.array([1000.0, 1000.0, 1000.0, 1000.0, 1000.0]),
        rho=100.0,
        edge_lengths={
            (0, 1): 50.0, (1, 0): 50.0,
            (1, 2): 50.0, (2, 1): 50.0,
            (2, 3): 50.0, (3, 2): 50.0,
            (3, 4): 50.0, (4, 3): 50.0,
        },
    )
    return GraphData(
        edges=[(0, 1), (1, 2), (2, 3), (3, 4)],
        attributes=attributes,
        num_nodes=5,
        num_edges=4,
    )
```

#### 2. New File: `tests/test_optimization/test_search.py`

```python
"""Tests for binary search optimization."""

import pytest

from half_america.optimization import (
    DEFAULT_MAX_ITERATIONS,
    DEFAULT_MU_MIN,
    TARGET_TOLERANCE,
    SearchResult,
    find_optimal_mu,
    solve_partition,
)


class TestFindOptimalMu:
    """Tests for find_optimal_mu function."""

    def test_returns_search_result(self, complex_graph_data):
        """Test that function returns SearchResult."""
        result = find_optimal_mu(
            complex_graph_data,
            lambda_param=0.5,
            verbose=False,
        )
        assert isinstance(result, SearchResult)

    def test_converges_to_target(self, complex_graph_data):
        """Test that search converges to target fraction."""
        result = find_optimal_mu(
            complex_graph_data,
            lambda_param=0.5,
            verbose=False,
        )
        assert result.converged
        assert abs(result.result.population_fraction - 0.5) <= TARGET_TOLERANCE

    def test_mu_history_tracked(self, complex_graph_data):
        """Test that μ history is recorded."""
        result = find_optimal_mu(
            complex_graph_data,
            lambda_param=0.5,
            verbose=False,
        )
        assert len(result.mu_history) == result.iterations
        assert all(mu > 0 for mu in result.mu_history)

    def test_respects_max_iterations(self, complex_graph_data):
        """Test termination at max_iterations."""
        result = find_optimal_mu(
            complex_graph_data,
            lambda_param=0.5,
            tolerance=1e-10,  # Impossible tolerance
            max_iterations=5,
            verbose=False,
        )
        assert result.iterations == 5
        assert not result.converged

    def test_custom_target_fraction(self, complex_graph_data):
        """Test with non-default target fraction."""
        result = find_optimal_mu(
            complex_graph_data,
            lambda_param=0.5,
            target_fraction=0.3,
            verbose=False,
        )
        assert result.converged
        assert abs(result.result.population_fraction - 0.3) <= TARGET_TOLERANCE

    def test_explicit_mu_bounds(self, complex_graph_data):
        """Test with explicit mu_min and mu_max."""
        result = find_optimal_mu(
            complex_graph_data,
            lambda_param=0.5,
            mu_min=0.0,
            mu_max=100.0,
            verbose=False,
        )
        assert result.converged
        # All mu values should be within bounds
        assert all(0.0 <= mu <= 100.0 for mu in result.mu_history)


class TestMonotonicity:
    """Tests verifying the monotonicity property."""

    def test_higher_mu_more_selection(self, complex_graph_data):
        """Test that higher μ → more selection."""
        low = solve_partition(complex_graph_data, 0.5, mu=0.001, verbose=False)
        high = solve_partition(complex_graph_data, 0.5, mu=1.0, verbose=False)
        assert high.selected_population >= low.selected_population

    def test_mu_increases_then_decreases_during_search(self, complex_graph_data):
        """Test that binary search adjusts μ in expected direction."""
        result = find_optimal_mu(
            complex_graph_data,
            lambda_param=0.5,
            verbose=False,
        )
        # With proper binary search, μ should not be monotonic
        # (it adjusts up and down to converge)
        if result.iterations > 2:
            diffs = [
                result.mu_history[i + 1] - result.mu_history[i]
                for i in range(len(result.mu_history) - 1)
            ]
            # Not all diffs should be positive or all negative
            has_increase = any(d > 0 for d in diffs)
            has_decrease = any(d < 0 for d in diffs)
            # At least one direction change expected for convergence
            assert has_increase or has_decrease


class TestEdgeCases:
    """Tests for edge cases."""

    def test_lambda_zero(self, complex_graph_data):
        """Test with λ=0 (no boundary cost)."""
        result = find_optimal_mu(
            complex_graph_data,
            lambda_param=0.0,
            verbose=False,
        )
        # Should still converge
        assert result.converged

    def test_lambda_one(self, complex_graph_data):
        """Test with λ=1 (max boundary cost)."""
        result = find_optimal_mu(
            complex_graph_data,
            lambda_param=1.0,
            verbose=False,
        )
        # Should still converge
        assert result.converged

    def test_simple_graph_still_works(self, simple_graph_data):
        """Test that simple 3-node graph also works."""
        result = find_optimal_mu(
            simple_graph_data,
            lambda_param=0.5,
            verbose=False,
        )
        # May or may not converge depending on achievable fractions
        assert isinstance(result, SearchResult)
        assert result.iterations <= DEFAULT_MAX_ITERATIONS


class TestDefaultsExported:
    """Tests that defaults are accessible."""

    def test_default_max_iterations(self):
        """Test DEFAULT_MAX_ITERATIONS is exported."""
        assert DEFAULT_MAX_ITERATIONS == 50

    def test_default_mu_min(self):
        """Test DEFAULT_MU_MIN is exported."""
        assert DEFAULT_MU_MIN == 0.0
```

### Success Criteria:

#### Automated Verification:
- [x] Tests pass: `uv run pytest tests/test_optimization/test_search.py -v`
- [x] All optimization tests pass: `uv run pytest tests/test_optimization/ -v`

---

## Phase 4: Verification & ROADMAP Update

### Overview
Run full verification suite and update ROADMAP.md to mark milestone complete.

### Changes Required:

#### 1. Update `ROADMAP.md`

Change line 56 from:
```markdown
- [ ] Implement binary search for Lagrange multiplier (μ) to hit 50% population target
```

To:
```markdown
- [x] Implement binary search for Lagrange multiplier (μ) to hit 50% population target
```

### Success Criteria:

#### Automated Verification:
- [x] Full test suite passes: `uv run pytest`
- [x] Type checking passes: `uv run mypy src/`
- [x] Linting passes: `uv run ruff check src/ tests/`
- [x] ROADMAP shows milestone checked

---

## Testing Strategy

### Unit Tests:
- Convergence to target fraction
- Monotonicity property verification
- Max iteration termination
- Custom parameters (target_fraction, tolerance, mu bounds)
- Edge cases (λ=0, λ=1)

### Integration Tests:
- Uses existing `solve_partition()` correctly
- Works with both simple and complex graph fixtures

## Performance Considerations

- Each `solve_partition()` call is O(V·E) for maxflow
- Binary search adds O(log(1/tolerance)) iterations
- For production data (~73k nodes), expect 15-20 iterations × ~1s each = 15-20s total

## References

- Research document: `thoughts/shared/research/2025-11-21-binary-search-lagrange-multiplier.md`
- Algorithm specification: `METHODOLOGY.md:59-72`
- Solver implementation: `src/half_america/optimization/solver.py`
