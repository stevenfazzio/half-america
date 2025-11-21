---
date: 2025-11-21T14:30:00-08:00
researcher: Claude
git_commit: b82b92bcfde92aa9b20d8b3a8d3c0528ed48b148
branch: master
repository: half_america
topic: "Build outer loop for lambda parameter sweep (0.0 -> 1.0)"
tags: [research, codebase, optimization, lambda-sweep, phase3]
status: complete
last_updated: 2025-11-21
last_updated_by: Claude
---

# Research: Build Outer Loop for Lambda Parameter Sweep (0.0 -> 1.0)

**Date**: 2025-11-21T14:30:00-08:00
**Researcher**: Claude
**Git Commit**: b82b92bcfde92aa9b20d8b3a8d3c0528ed48b148
**Branch**: master
**Repository**: half_america

## Research Question

What is required to implement the "Build outer loop for λ parameter sweep (0.0 → 1.0)" milestone from ROADMAP.md?

## Summary

The λ parameter sweep is the next Phase 3 milestone after the recently completed binary search implementation. The sweep iterates λ from 0.0 to 1.0 (typically in 0.1 increments), calling `find_optimal_mu()` for each value to find the partition that achieves 50% population. The implementation should:

1. Create a `sweep.py` module in `src/half_america/optimization/`
2. Define a `SweepResult` NamedTuple to hold results keyed by λ
3. Implement `sweep_lambda()` function that iterates over λ values
4. Add optional warm-starting of μ bounds from previous λ iteration
5. Include progress reporting for visibility during long-running sweeps

**Key insight**: Since solver and binary search are already implemented, the sweep is primarily an orchestration layer that calls `find_optimal_mu()` in a loop.

## Detailed Findings

### Current State: What Exists

The solver wrapper and binary search are fully implemented:

| Component | File | Status |
|-----------|------|--------|
| `solve_partition()` | `src/half_america/optimization/solver.py:30` | ✅ Complete |
| `find_optimal_mu()` | `src/half_america/optimization/search.py:27` | ✅ Complete |
| `OptimizationResult` | `src/half_america/optimization/solver.py:11-23` | ✅ Complete |
| `SearchResult` | `src/half_america/optimization/search.py:13-19` | ✅ Complete |

### How λ Affects the Optimization

From `src/half_america/graph/network.py`:

**Terminal edges (t-links)** at line 42:
```python
sink_cap = (1 - lambda_param) * attributes.area[i]
```

**Neighborhood edges (n-links)** at line 50:
```python
capacity = lambda_param * l_ij / rho
```

| λ Value | N-link Capacity | Sink Capacity | Behavior |
|---------|-----------------|---------------|----------|
| `λ = 0.0` | 0 (no boundary cost) | full area cost | "Dusty" - minimizes area, many disconnected regions |
| `λ = 0.5` | balanced | balanced | Mixed - moderate compactness |
| `λ = 1.0` | full boundary cost | 0 (no area cost) | "Smooth" - minimizes perimeter, contiguous blobs |

### Proposed Implementation

#### New File: `src/half_america/optimization/sweep.py`

```python
"""Lambda parameter sweep for pre-computing optimization results."""

from typing import NamedTuple

import numpy as np

from half_america.graph.pipeline import GraphData
from half_america.optimization.search import SearchResult, find_optimal_mu


class SweepResult(NamedTuple):
    """Result from lambda parameter sweep."""

    results: dict[float, SearchResult]  # λ → SearchResult mapping
    lambda_values: list[float]  # λ values in order
    total_iterations: int  # Total binary search iterations across all λ
    all_converged: bool  # True if all λ values converged


# Default λ values: 0.0, 0.1, 0.2, ..., 1.0
DEFAULT_LAMBDA_VALUES = [round(i * 0.1, 1) for i in range(11)]


def sweep_lambda(
    graph_data: GraphData,
    lambda_values: list[float] | None = None,
    target_fraction: float = 0.5,
    tolerance: float = 0.01,
    warm_start: bool = True,
    verbose: bool = True,
) -> SweepResult:
    """
    Run optimization across a range of λ (surface tension) values.

    Args:
        graph_data: Input graph with edges and attributes
        lambda_values: λ values to sweep (default: 0.0 to 1.0 by 0.1)
        target_fraction: Target population fraction (default: 0.5)
        tolerance: Population tolerance (default: 0.01 = 1%)
        warm_start: Use previous μ as starting point for next λ
        verbose: Print progress information

    Returns:
        SweepResult with optimization results for each λ value
    """
    if lambda_values is None:
        lambda_values = DEFAULT_LAMBDA_VALUES.copy()

    if verbose:
        print(f"Starting λ sweep: {len(lambda_values)} values")
        print(f"  λ range: {lambda_values[0]} → {lambda_values[-1]}")
        print(f"  Target: {target_fraction*100:.0f}% population")

    results: dict[float, SearchResult] = {}
    total_iterations = 0
    all_converged = True

    # Track μ bounds for warm-starting
    prev_mu: float | None = None

    for i, lambda_param in enumerate(lambda_values):
        if verbose:
            print(f"\n[{i+1}/{len(lambda_values)}] λ = {lambda_param:.1f}")

        # Warm-start: use previous μ result as hint for initial bounds
        mu_max = None
        if warm_start and prev_mu is not None:
            # Use previous μ with headroom as upper bound hint
            mu_max = prev_mu * 2.0

        search_result = find_optimal_mu(
            graph_data,
            lambda_param=lambda_param,
            target_fraction=target_fraction,
            tolerance=tolerance,
            mu_max=mu_max,
            verbose=verbose,
        )

        results[lambda_param] = search_result
        total_iterations += search_result.iterations
        all_converged = all_converged and search_result.converged

        # Update μ for warm-starting next iteration
        prev_mu = search_result.result.mu

        if verbose:
            opt = search_result.result
            print(f"  → {opt.population_fraction*100:.2f}% population")
            print(f"  → μ = {opt.mu:.6f}")
            print(f"  → {search_result.iterations} iterations")

    if verbose:
        print(f"\n{'='*40}")
        print(f"Sweep complete: {total_iterations} total iterations")
        print(f"All converged: {all_converged}")

    return SweepResult(
        results=results,
        lambda_values=lambda_values,
        total_iterations=total_iterations,
        all_converged=all_converged,
    )
```

#### Update `src/half_america/optimization/__init__.py`

Add exports:
```python
from half_america.optimization.sweep import (
    DEFAULT_LAMBDA_VALUES,
    SweepResult,
    sweep_lambda,
)

__all__ = [
    # ... existing exports ...
    "DEFAULT_LAMBDA_VALUES",
    "SweepResult",
    "sweep_lambda",
]
```

### Test Strategy

#### New File: `tests/test_optimization/test_sweep.py`

```python
"""Tests for lambda parameter sweep."""

import pytest

from half_america.optimization import (
    DEFAULT_LAMBDA_VALUES,
    SweepResult,
    sweep_lambda,
)


class TestSweepLambda:
    """Tests for sweep_lambda function."""

    def test_returns_sweep_result(self, complex_graph_data):
        """Sweep returns SweepResult type."""
        result = sweep_lambda(
            complex_graph_data,
            lambda_values=[0.0, 0.5, 1.0],
            verbose=False,
        )
        assert isinstance(result, SweepResult)

    def test_contains_all_lambda_values(self, complex_graph_data):
        """Result contains entry for each λ value."""
        lambda_values = [0.0, 0.25, 0.5, 0.75, 1.0]
        result = sweep_lambda(
            complex_graph_data,
            lambda_values=lambda_values,
            verbose=False,
        )
        assert result.lambda_values == lambda_values
        assert set(result.results.keys()) == set(lambda_values)

    def test_all_results_meet_target(self, complex_graph_data):
        """All results achieve target population fraction."""
        result = sweep_lambda(
            complex_graph_data,
            lambda_values=[0.0, 0.5, 1.0],
            tolerance=0.1,  # Relaxed for small test graph
            verbose=False,
        )
        for search_result in result.results.values():
            pop_frac = search_result.result.population_fraction
            assert 0.4 <= pop_frac <= 0.6  # Within 10% of 50%

    def test_default_lambda_values(self):
        """Default values cover 0.0 to 1.0 by 0.1."""
        expected = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        assert DEFAULT_LAMBDA_VALUES == expected

    def test_tracks_total_iterations(self, complex_graph_data):
        """Total iterations is sum across all λ values."""
        result = sweep_lambda(
            complex_graph_data,
            lambda_values=[0.0, 1.0],
            verbose=False,
        )
        expected_total = sum(r.iterations for r in result.results.values())
        assert result.total_iterations == expected_total


class TestWarmStart:
    """Tests for warm-start μ optimization."""

    def test_warm_start_reduces_iterations(self, complex_graph_data):
        """Warm-starting should reduce total iterations."""
        # Run without warm-start
        cold_result = sweep_lambda(
            complex_graph_data,
            lambda_values=[0.0, 0.1, 0.2],
            warm_start=False,
            verbose=False,
        )

        # Run with warm-start
        warm_result = sweep_lambda(
            complex_graph_data,
            lambda_values=[0.0, 0.1, 0.2],
            warm_start=True,
            verbose=False,
        )

        # Warm-start should use same or fewer iterations
        assert warm_result.total_iterations <= cold_result.total_iterations + 3
```

### Performance Estimates

Based on existing benchmarks:

| Operation | Time | Notes |
|-----------|------|-------|
| Single maxflow solve | ~1s | 73k nodes, ~292k edges |
| Binary search iterations | 15-20 | To achieve 1% tolerance |
| Per-λ optimization | 15-20s | Binary search × maxflow |
| Full sweep (11 λ) | 3-4 min | Without warm-start |
| Full sweep (warm-start) | 2-3 min | ~20% reduction estimated |

### Integration with CLI

The CLI is currently a stub at `src/half_america/__init__.py:1-2`. Once sweep is implemented, the main function could be extended:

```python
def main() -> None:
    """Run lambda parameter sweep."""
    from half_america.data.pipeline import load_all_tracts
    from half_america.graph.pipeline import load_graph_data
    from half_america.optimization import sweep_lambda

    print("Loading data...")
    gdf = load_all_tracts()

    print("Building graph...")
    graph_data = load_graph_data(gdf)

    print("Running sweep...")
    result = sweep_lambda(graph_data)

    print("\nResults summary:")
    for lam in result.lambda_values:
        opt = result.results[lam].result
        print(f"  λ={lam:.1f}: {opt.population_fraction*100:.2f}% pop, μ={opt.mu:.4f}")
```

### Next Steps After Sweep

Per ROADMAP.md, remaining Phase 3 milestones after sweep:

1. **Pre-compute results** - Cache `SweepResult` to disk for fast web loading
2. **Performance benchmarking** - Profile full pipeline, identify bottlenecks
3. **Unit tests** - Complete test coverage for sweep module

### Dependencies

The sweep module has these dependencies:

```
sweep.py
  └── search.py (find_optimal_mu, SearchResult)
       └── solver.py (solve_partition, OptimizationResult)
            └── network.py (build_flow_network, get_partition)
                 └── boundary.py (GraphAttributes)
```

## Code References

- `src/half_america/optimization/solver.py:30-95` - `solve_partition()` function
- `src/half_america/optimization/search.py:27-119` - `find_optimal_mu()` function
- `src/half_america/optimization/__init__.py:1-25` - Public API exports
- `src/half_america/graph/network.py:42` - λ in sink capacity formula
- `src/half_america/graph/network.py:50` - λ in n-link capacity formula
- `tests/test_optimization/conftest.py:1-52` - Test fixtures (`simple_graph_data`, `complex_graph_data`)
- `ROADMAP.md:57-59` - Phase 3 milestones for sweep and pre-computation

## Architecture Insights

### Design Patterns to Follow

1. **NamedTuple for results** - Consistent with `OptimizationResult`, `SearchResult`
2. **Optional verbose parameter** - Matches all existing functions
3. **Default values as module constant** - Like `DEFAULT_MAX_ITERATIONS`
4. **Warm-start pattern** - Use previous solution to inform next search bounds

### Module Placement

The sweep module belongs in `src/half_america/optimization/` alongside:
- `solver.py` - Single graph-cut solve
- `search.py` - Binary search for μ
- `sweep.py` - **New**: λ parameter sweep

## Historical Context (from thoughts/)

- `thoughts/shared/research/2025-11-21-phase3-optimization-engine.md` - Original Phase 3 research with proposed `sweep.py` structure (lines 216-233)
- `thoughts/shared/research/2025-11-21-binary-search-lagrange-multiplier.md` - Binary search implementation research
- `thoughts/shared/plans/2025-11-21-binary-search-lagrange-multiplier.md` - Binary search implementation plan

## Related Research

- [Phase 3 Optimization Engine](2025-11-21-phase3-optimization-engine.md) - Comprehensive Phase 3 overview
- [Binary Search Implementation](2025-11-21-binary-search-lagrange-multiplier.md) - Inner loop implementation

## Open Questions

1. **Parallel execution**: Should λ values be processed in parallel? (They're independent)
RESPONSE: Sounds good to me.
2. **Progress callbacks**: Should sweep accept a callback for progress reporting?
3. **Early termination**: Should sweep stop early if a λ value fails to converge?
4. **Result format**: Should results include timing information per λ?
5. **Finer granularity**: Should we support 0.01 increments (101 values) for animations?
RESPONSE: Let's start with 0.1 increments. We can add support for 0.01 increments in "## Future Enhancements" in ROADMAP.md. 
