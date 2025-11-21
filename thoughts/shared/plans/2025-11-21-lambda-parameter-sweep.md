# Lambda Parameter Sweep Implementation Plan

## Overview

Implement the λ parameter sweep - an orchestration layer that calls `find_optimal_mu()` across multiple λ values (0.0 to 1.0) to pre-compute optimization results. This completes the "Build outer loop for λ parameter sweep" milestone in Phase 3.

## Current State Analysis

The solver wrapper and binary search are fully implemented:

| Component | File | Status |
|-----------|------|--------|
| `solve_partition()` | `src/half_america/optimization/solver.py:30` | Complete |
| `find_optimal_mu()` | `src/half_america/optimization/search.py:27` | Complete |
| `OptimizationResult` | `src/half_america/optimization/solver.py:11-23` | Complete |
| `SearchResult` | `src/half_america/optimization/search.py:13-19` | Complete |

### Key Discoveries

- λ affects terminal edges (t-links) at `network.py:42`: `sink_cap = (1 - lambda_param) * attributes.area[i]`
- λ affects neighborhood edges (n-links) at `network.py:50`: `capacity = lambda_param * l_ij / rho`
- Each λ optimization is independent - suitable for parallel execution
- PyMaxFlow releases GIL during maxflow computation, so `ThreadPoolExecutor` is appropriate

## Desired End State

After implementation:
1. `sweep_lambda()` function exists in `src/half_america/optimization/sweep.py`
2. Supports parallel execution via `ThreadPoolExecutor` for independent λ values
3. Includes timing information per λ in results
4. Stops early if any λ value fails to converge
5. Exports available from `half_america.optimization`
6. All tests pass with `uv run pytest tests/test_optimization/test_sweep.py`

## What We're NOT Doing

- Progress callbacks (deferred - not needed for CLI usage)
- Warm-starting μ bounds (incompatible with parallel execution)
- Finer granularity (0.01 increments) - deferred to Future Enhancements
- CLI integration - separate task after sweep is working

## Implementation Approach

Create a new `sweep.py` module that orchestrates parallel calls to `find_optimal_mu()`. Use `ThreadPoolExecutor` since PyMaxFlow releases the GIL. Include per-λ timing and early termination on convergence failure.

---

## Phase 1: Create `sweep.py` Module

### Overview

Create the core sweep functionality with parallel execution support.

### Changes Required

#### 1. New File: `src/half_america/optimization/sweep.py`

```python
"""Lambda parameter sweep for pre-computing optimization results."""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import NamedTuple

from half_america.graph.pipeline import GraphData
from half_america.optimization.search import SearchResult, find_optimal_mu


class LambdaResult(NamedTuple):
    """Result for a single λ value."""

    lambda_param: float  # The λ value
    search_result: SearchResult  # Result from find_optimal_mu
    elapsed_seconds: float  # Time taken for this λ


class SweepResult(NamedTuple):
    """Result from lambda parameter sweep."""

    results: dict[float, LambdaResult]  # λ → LambdaResult mapping
    lambda_values: list[float]  # λ values in order
    total_iterations: int  # Total binary search iterations across all λ
    total_elapsed_seconds: float  # Total wall-clock time
    all_converged: bool  # True if all λ values converged


# Default λ values: 0.0, 0.1, 0.2, ..., 1.0
DEFAULT_LAMBDA_VALUES = [round(i * 0.1, 1) for i in range(11)]


def _run_single_lambda(
    graph_data: GraphData,
    lambda_param: float,
    target_fraction: float,
    tolerance: float,
) -> LambdaResult:
    """Run optimization for a single λ value with timing."""
    start = time.perf_counter()
    search_result = find_optimal_mu(
        graph_data,
        lambda_param=lambda_param,
        target_fraction=target_fraction,
        tolerance=tolerance,
        verbose=False,
    )
    elapsed = time.perf_counter() - start
    return LambdaResult(
        lambda_param=lambda_param,
        search_result=search_result,
        elapsed_seconds=elapsed,
    )


def sweep_lambda(
    graph_data: GraphData,
    lambda_values: list[float] | None = None,
    target_fraction: float = 0.5,
    tolerance: float = 0.01,
    max_workers: int | None = None,
    verbose: bool = True,
) -> SweepResult:
    """
    Run optimization across a range of λ (surface tension) values.

    Uses parallel execution since each λ optimization is independent.
    Stops early if any λ value fails to converge.

    Args:
        graph_data: Input graph with edges and attributes
        lambda_values: λ values to sweep (default: 0.0 to 1.0 by 0.1)
        target_fraction: Target population fraction (default: 0.5)
        tolerance: Population tolerance (default: 0.01 = 1%)
        max_workers: Maximum parallel workers (default: None = CPU count)
        verbose: Print progress information

    Returns:
        SweepResult with optimization results for each λ value

    Raises:
        RuntimeError: If any λ value fails to converge (early termination)
    """
    if lambda_values is None:
        lambda_values = DEFAULT_LAMBDA_VALUES.copy()

    if verbose:
        print(f"Starting λ sweep: {len(lambda_values)} values")
        print(f"  λ range: {lambda_values[0]} → {lambda_values[-1]}")
        print(f"  Target: {target_fraction*100:.0f}% population ± {tolerance*100:.0f}%")
        print(f"  Parallel workers: {max_workers or 'auto'}")

    results: dict[float, LambdaResult] = {}
    total_start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_lambda = {
            executor.submit(
                _run_single_lambda,
                graph_data,
                lam,
                target_fraction,
                tolerance,
            ): lam
            for lam in lambda_values
        }

        # Collect results as they complete
        for future in as_completed(future_to_lambda):
            lam = future_to_lambda[future]
            try:
                result = future.result()
                results[lam] = result

                if verbose:
                    opt = result.search_result.result
                    print(
                        f"  λ={lam:.1f}: {opt.population_fraction*100:.2f}% pop, "
                        f"μ={opt.mu:.6f}, {result.search_result.iterations} iters, "
                        f"{result.elapsed_seconds:.2f}s"
                    )

                # Early termination check
                if not result.search_result.converged:
                    # Cancel remaining futures
                    for f in future_to_lambda:
                        f.cancel()
                    raise RuntimeError(
                        f"λ={lam} failed to converge after "
                        f"{result.search_result.iterations} iterations"
                    )

            except Exception as e:
                # Cancel remaining futures on any error
                for f in future_to_lambda:
                    f.cancel()
                raise

    total_elapsed = time.perf_counter() - total_start
    total_iterations = sum(r.search_result.iterations for r in results.values())
    all_converged = all(r.search_result.converged for r in results.values())

    if verbose:
        print(f"\n{'='*50}")
        print(f"Sweep complete: {total_iterations} total iterations")
        print(f"Total time: {total_elapsed:.2f}s")
        print(f"All converged: {all_converged}")

    return SweepResult(
        results=results,
        lambda_values=lambda_values,
        total_iterations=total_iterations,
        total_elapsed_seconds=total_elapsed,
        all_converged=all_converged,
    )
```

### Success Criteria

#### Automated Verification:
- [x] File exists: `src/half_america/optimization/sweep.py`
- [x] Type checking passes: `uv run mypy src/half_america/optimization/sweep.py`
- [x] Linting passes: `uv run ruff check src/half_america/optimization/sweep.py`

#### Manual Verification:
- [ ] None required for this phase

---

## Phase 2: Update Module Exports

### Overview

Add sweep exports to the optimization module's public API.

### Changes Required

#### 1. Update `src/half_america/optimization/__init__.py`

Add imports and exports for the new sweep module:

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
from half_america.optimization.sweep import (
    DEFAULT_LAMBDA_VALUES,
    LambdaResult,
    SweepResult,
    sweep_lambda,
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
    # Sweep
    "DEFAULT_LAMBDA_VALUES",
    "LambdaResult",
    "SweepResult",
    "sweep_lambda",
]
```

### Success Criteria

#### Automated Verification:
- [x] Type checking passes: `uv run mypy src/half_america/optimization/`
- [x] Linting passes: `uv run ruff check src/half_america/optimization/`
- [x] Import works: `uv run python -c "from half_america.optimization import sweep_lambda, SweepResult, LambdaResult, DEFAULT_LAMBDA_VALUES"`

#### Manual Verification:
- [ ] None required for this phase

---

## Phase 3: Add Unit Tests

### Overview

Create comprehensive tests for the sweep functionality.

### Changes Required

#### 1. New File: `tests/test_optimization/test_sweep.py`

```python
"""Tests for lambda parameter sweep."""

import pytest

from half_america.optimization import (
    DEFAULT_LAMBDA_VALUES,
    LambdaResult,
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
            tolerance=0.15,  # Relaxed for small test graph
            verbose=False,
        )
        assert isinstance(result, SweepResult)

    def test_contains_all_lambda_values(self, complex_graph_data):
        """Result contains entry for each λ value."""
        lambda_values = [0.0, 0.25, 0.5, 0.75, 1.0]
        result = sweep_lambda(
            complex_graph_data,
            lambda_values=lambda_values,
            tolerance=0.15,  # Relaxed for small test graph
            verbose=False,
        )
        assert result.lambda_values == lambda_values
        assert set(result.results.keys()) == set(lambda_values)

    def test_all_results_meet_target(self, complex_graph_data):
        """All results achieve target population fraction."""
        result = sweep_lambda(
            complex_graph_data,
            lambda_values=[0.0, 0.5, 1.0],
            tolerance=0.15,  # Relaxed for small test graph
            verbose=False,
        )
        for lambda_result in result.results.values():
            pop_frac = lambda_result.search_result.result.population_fraction
            assert 0.35 <= pop_frac <= 0.65  # Within 15% of 50%

    def test_default_lambda_values(self):
        """Default values cover 0.0 to 1.0 by 0.1."""
        expected = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        assert DEFAULT_LAMBDA_VALUES == expected

    def test_tracks_total_iterations(self, complex_graph_data):
        """Total iterations is sum across all λ values."""
        result = sweep_lambda(
            complex_graph_data,
            lambda_values=[0.0, 1.0],
            tolerance=0.15,  # Relaxed for small test graph
            verbose=False,
        )
        expected_total = sum(
            r.search_result.iterations for r in result.results.values()
        )
        assert result.total_iterations == expected_total

    def test_tracks_total_elapsed_time(self, complex_graph_data):
        """Total elapsed time is tracked."""
        result = sweep_lambda(
            complex_graph_data,
            lambda_values=[0.0, 0.5],
            tolerance=0.15,  # Relaxed for small test graph
            verbose=False,
        )
        assert result.total_elapsed_seconds > 0
        # Total should be >= max of individual times (parallel execution)
        max_individual = max(r.elapsed_seconds for r in result.results.values())
        assert result.total_elapsed_seconds >= max_individual * 0.9  # Allow 10% margin


class TestLambdaResult:
    """Tests for LambdaResult type."""

    def test_lambda_result_structure(self, complex_graph_data):
        """LambdaResult contains expected fields."""
        result = sweep_lambda(
            complex_graph_data,
            lambda_values=[0.5],
            tolerance=0.15,  # Relaxed for small test graph
            verbose=False,
        )
        lambda_result = result.results[0.5]
        assert isinstance(lambda_result, LambdaResult)
        assert lambda_result.lambda_param == 0.5
        assert lambda_result.elapsed_seconds > 0
        assert lambda_result.search_result is not None

    def test_per_lambda_timing(self, complex_graph_data):
        """Each λ result has timing information."""
        result = sweep_lambda(
            complex_graph_data,
            lambda_values=[0.0, 0.5, 1.0],
            tolerance=0.15,  # Relaxed for small test graph
            verbose=False,
        )
        for lam, lambda_result in result.results.items():
            assert lambda_result.elapsed_seconds > 0
            assert lambda_result.lambda_param == lam


class TestParallelExecution:
    """Tests for parallel execution."""

    def test_parallel_faster_than_sequential(self, complex_graph_data):
        """Parallel execution should not be slower than sequential."""
        # Run with 1 worker (sequential)
        sequential = sweep_lambda(
            complex_graph_data,
            lambda_values=[0.0, 0.5, 1.0],
            tolerance=0.15,  # Relaxed for small test graph
            max_workers=1,
            verbose=False,
        )

        # Run with multiple workers (parallel)
        parallel = sweep_lambda(
            complex_graph_data,
            lambda_values=[0.0, 0.5, 1.0],
            tolerance=0.15,  # Relaxed for small test graph
            max_workers=3,
            verbose=False,
        )

        # Parallel should be comparable or faster
        # (may not be faster for small test graph due to overhead)
        assert parallel.total_elapsed_seconds <= sequential.total_elapsed_seconds * 1.5


class TestEarlyTermination:
    """Tests for early termination on convergence failure."""

    def test_raises_on_convergence_failure(self, complex_graph_data):
        """Sweep raises RuntimeError if any λ fails to converge."""
        with pytest.raises(RuntimeError, match="failed to converge"):
            sweep_lambda(
                complex_graph_data,
                lambda_values=[0.5],
                tolerance=1e-10,  # Impossible tolerance
                verbose=False,
            )


class TestDefaultsExported:
    """Tests that defaults are accessible."""

    def test_default_lambda_values_exported(self):
        """Test DEFAULT_LAMBDA_VALUES is exported."""
        assert len(DEFAULT_LAMBDA_VALUES) == 11
        assert DEFAULT_LAMBDA_VALUES[0] == 0.0
        assert DEFAULT_LAMBDA_VALUES[-1] == 1.0
```

### Success Criteria

#### Automated Verification:
- [x] All tests pass: `uv run pytest tests/test_optimization/test_sweep.py -v`
- [x] All existing tests still pass: `uv run pytest tests/test_optimization/ -v`
- [x] Full test suite passes: `uv run pytest`

#### Manual Verification:
- [ ] None required for this phase

**Implementation Note**: After completing this phase and all automated verification passes, the sweep functionality is complete.

---

## Phase 4: Update ROADMAP.md

### Overview

Mark the milestone complete and add finer granularity to Future Enhancements.

### Changes Required

#### 1. Update `ROADMAP.md`

Change line 57 from:
```markdown
- [ ] Build outer loop for λ parameter sweep (0.0 → 1.0)
```

To:
```markdown
- [x] Build outer loop for λ parameter sweep (0.0 → 1.0)
```

Add to Future Enhancements section (after line 104):
```markdown
- **Fine λ granularity**: Support 0.01 increments (101 values) for smooth animations
```

### Success Criteria

#### Automated Verification:
- [x] Linting passes: `uv run ruff check ROADMAP.md` (if applicable) - N/A, ruff doesn't check markdown

#### Manual Verification:
- [x] ROADMAP.md shows milestone as complete
- [x] Future Enhancements includes fine granularity item

---

## Testing Strategy

### Unit Tests

Tests in `tests/test_optimization/test_sweep.py` cover:
- Basic sweep functionality and return types
- All λ values present in results
- Target population achieved for all λ
- Total iterations tracking
- Per-λ timing information
- Parallel execution behavior
- Early termination on convergence failure
- Default values exported correctly

### Integration Testing

After implementation, manually verify with real data:
```bash
uv run python -c "
from half_america.data.pipeline import load_all_tracts
from half_america.graph.pipeline import load_graph_data
from half_america.optimization import sweep_lambda

gdf = load_all_tracts()
graph_data = load_graph_data(gdf)
result = sweep_lambda(graph_data, lambda_values=[0.0, 0.5, 1.0])
print(f'Total time: {result.total_elapsed_seconds:.1f}s')
"
```

## Performance Considerations

Based on existing benchmarks:

| Operation | Estimated Time | Notes |
|-----------|---------------|-------|
| Single maxflow solve | ~1s | 73k nodes, ~292k edges |
| Binary search iterations | 15-20 | To achieve 1% tolerance |
| Per-λ optimization | 15-20s | Binary search × maxflow |
| Full sweep (11 λ, sequential) | 3-4 min | Without parallelization |
| Full sweep (11 λ, parallel) | ~30-60s | With 4+ workers |

Parallel execution should provide ~3-4x speedup on multi-core systems.

## References

- Original ticket: `thoughts/shared/research/2025-11-21-lambda-parameter-sweep.md`
- Related research: `thoughts/shared/research/2025-11-21-phase3-optimization-engine.md`
- Binary search implementation: `src/half_america/optimization/search.py`
- Solver implementation: `src/half_america/optimization/solver.py`
