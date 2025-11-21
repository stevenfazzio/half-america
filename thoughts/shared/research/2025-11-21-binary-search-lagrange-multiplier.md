---
date: 2025-11-21T14:30:00-08:00
researcher: Claude
git_commit: 1faf1bb5efe415ddf1d1fda1e52a6ea17a5b3c21
branch: master
repository: half_america
topic: "Implement binary search for Lagrange multiplier (μ) to hit 50% population target"
tags: [research, codebase, optimization, binary-search, lagrange-multiplier, phase3]
status: complete
last_updated: 2025-11-21
last_updated_by: Claude
---

# Research: Binary Search for Lagrange Multiplier (μ)

**Date**: 2025-11-21T14:30:00-08:00
**Researcher**: Claude
**Git Commit**: 1faf1bb5efe415ddf1d1fda1e52a6ea17a5b3c21
**Branch**: master
**Repository**: half_america

## Research Question

What is required to implement "binary search for Lagrange multiplier (μ) to hit 50% population target" as specified in ROADMAP.md Phase 3?

## Summary

The binary search implementation will be a new function `find_optimal_mu()` in `src/half_america/optimization/search.py` that iteratively calls the existing `solve_partition()` wrapper. The algorithm exploits the **monotonicity property**: selected population increases monotonically with μ, guaranteeing binary search convergence.

**Current State:**
- ✅ Solver wrapper `solve_partition()` is complete (`optimization/solver.py`)
- ✅ `OptimizationResult` captures partition and statistics
- ✅ `TARGET_TOLERANCE = 0.01` (1%) is defined
- ❌ Binary search loop is NOT implemented

**Implementation Effort:** ~150 lines of code (search.py + tests)

## Detailed Findings

### Algorithm from METHODOLOGY.md:59-72

```
Target: P_target = 0.5 × P_total

1. Set bounds [μ_min, μ_max]
2. Construct graph with current μ (via solve_partition)
3. Solve Max-Flow
4. Check resulting population sum:
   - If P_selected < P_target → increase μ (reward too low)
   - If P_selected > P_target → decrease μ (reward too high)
5. Repeat until |P_selected - P_target| < ε
```

**Key Property**: Selected population is monotonic with respect to μ, guaranteeing binary search convergence.

### Existing Infrastructure

#### Solver Wrapper (`src/half_america/optimization/solver.py`)

```python
def solve_partition(
    graph_data: GraphData,
    lambda_param: float,
    mu: float,
    verbose: bool = True,
) -> OptimizationResult:
```

**Returns** `OptimizationResult` with:
- `partition: np.ndarray` - Boolean array (True = selected)
- `selected_population: int` - Sum of p_i for selected tracts
- `population_fraction: float` - selected/total
- `satisfied_target: bool` - True if within 1% of 50%

#### Constants

| Constant | Value | Location |
|----------|-------|----------|
| `TARGET_TOLERANCE` | 0.01 | `solver.py:27` |
| Target fraction | 0.5 (50%) | `solver.py:77` |

#### Population Data Access

```python
# Total population
total_population = graph_data.attributes.population.sum()

# Selected population (from partition)
selected_population = graph_data.attributes.population[partition].sum()
```

### Proposed Implementation

#### New File: `src/half_america/optimization/search.py`

```python
"""Binary search for Lagrange multiplier (μ)."""

from typing import NamedTuple

from half_america.graph.pipeline import GraphData
from half_america.optimization.solver import OptimizationResult, solve_partition


class SearchResult(NamedTuple):
    """Result from binary search for optimal μ."""

    result: OptimizationResult  # Final optimization result
    iterations: int             # Number of binary search iterations
    mu_history: list[float]     # μ values tried during search
    converged: bool             # True if converged within max_iterations


# Default parameters
DEFAULT_TOLERANCE = 0.001      # 0.1% of total population
DEFAULT_MAX_ITERATIONS = 50    # ~50 iterations for 0.001 tolerance
DEFAULT_MU_MIN = 0.0
DEFAULT_MU_MAX = None          # Auto-scale based on data


def find_optimal_mu(
    graph_data: GraphData,
    lambda_param: float,
    target_fraction: float = 0.5,
    tolerance: float = DEFAULT_TOLERANCE,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
    mu_min: float = DEFAULT_MU_MIN,
    mu_max: float | None = DEFAULT_MU_MAX,
    verbose: bool = True,
) -> SearchResult:
    """
    Binary search for μ that achieves target population fraction.

    Exploits monotonicity: higher μ → more tracts selected.

    Args:
        graph_data: GraphData from load_graph_data()
        lambda_param: Surface tension parameter [0, 1]
        target_fraction: Target population fraction (default 0.5)
        tolerance: Acceptable deviation from target (default 0.001 = 0.1%)
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

    mu_history = []

    for iteration in range(max_iterations):
        mu = (mu_min + mu_max) / 2
        mu_history.append(mu)

        result = solve_partition(
            graph_data,
            lambda_param,
            mu,
            verbose=False
        )

        error = result.selected_population - target_pop

        if verbose:
            print(f"  [{iteration+1}] μ={mu:.6f}, "
                  f"pop={result.selected_population:,} "
                  f"({100*result.population_fraction:.2f}%), "
                  f"error={error:+,.0f}")

        # Check convergence
        if abs(error) <= pop_tolerance:
            if verbose:
                print(f"  Converged in {iteration+1} iterations")
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

### Parameters and Tuning

#### Tolerance Selection

| Tolerance | Population Error | Iterations (est.) |
|-----------|-----------------|-------------------|
| 0.01 (1%) | ~1.6M people | ~10-15 |
| 0.001 (0.1%) | ~160k people | ~15-20 |
| 0.0001 (0.01%) | ~16k people | ~20-25 |

**Recommendation**: Use `tolerance=0.001` (0.1%) for good precision without excessive iterations.

#### Initial μ Bounds

The μ parameter must be scaled appropriately:

```python
# Heuristic: μ × avg_pop should be comparable to (1-λ) × avg_area
total_pop = attrs.population.sum()       # ~330 million
total_area = attrs.area.sum()            # ~8e12 m² (contiguous US)
mu_scale = total_area / total_pop        # ~24,000 m²/person

mu_min = 0.0
mu_max = mu_scale * 10                   # ~240,000 (headroom)
```

### Test Strategy

#### Unit Tests (`tests/test_optimization/test_search.py`)

```python
class TestFindOptimalMu:
    def test_converges_to_target(self, simple_graph_data):
        """Test that search converges to target fraction."""
        result = find_optimal_mu(simple_graph_data, lambda_param=0.5)
        assert result.converged
        assert abs(result.result.population_fraction - 0.5) < 0.01

    def test_monotonicity(self, simple_graph_data):
        """Test that higher μ → more selection."""
        low = solve_partition(simple_graph_data, 0.5, mu=0.001)
        high = solve_partition(simple_graph_data, 0.5, mu=1.0)
        assert high.selected_population >= low.selected_population

    def test_respects_max_iterations(self, simple_graph_data):
        """Test termination at max_iterations."""
        result = find_optimal_mu(
            simple_graph_data,
            lambda_param=0.5,
            tolerance=1e-10,  # Impossible tolerance
            max_iterations=5,
        )
        assert result.iterations == 5
        assert not result.converged

    def test_mu_history_tracked(self, simple_graph_data):
        """Test that μ history is recorded."""
        result = find_optimal_mu(simple_graph_data, lambda_param=0.5)
        assert len(result.mu_history) == result.iterations
```

### Performance Considerations

| Metric | Value | Notes |
|--------|-------|-------|
| Single maxflow solve | ~1 second | 73k nodes, 292k edges |
| Binary search iterations | 15-20 | For 0.1% tolerance |
| Total search time | 15-20 seconds | Per λ value |
| Full sweep (11 λ values) | ~3-4 minutes | Sequential |

**Optimization Opportunities:**
1. **Warm-start μ**: Use previous λ's optimal μ as starting point
2. **Coarse-to-fine**: Start with 1% tolerance, refine to 0.1%
3. **Parallel λ sweep**: Independent optimizations can run in parallel

### Module Integration

Update `src/half_america/optimization/__init__.py`:

```python
from half_america.optimization.search import (
    DEFAULT_MAX_ITERATIONS,
    DEFAULT_MU_MAX,
    DEFAULT_MU_MIN,
    DEFAULT_TOLERANCE,
    SearchResult,
    find_optimal_mu,
)

__all__ = [
    # Existing exports
    "TARGET_TOLERANCE",
    "OptimizationResult",
    "solve_partition",
    # New exports
    "DEFAULT_MAX_ITERATIONS",
    "DEFAULT_MU_MAX",
    "DEFAULT_MU_MIN",
    "DEFAULT_TOLERANCE",
    "SearchResult",
    "find_optimal_mu",
]
```

## Code References

| Component | File | Lines |
|-----------|------|-------|
| solve_partition() | `src/half_america/optimization/solver.py` | 30-103 |
| OptimizationResult | `src/half_america/optimization/solver.py` | 11-24 |
| TARGET_TOLERANCE | `src/half_america/optimization/solver.py` | 27 |
| GraphData | `src/half_america/graph/pipeline.py` | 16-22 |
| GraphAttributes | `src/half_america/graph/boundary.py` | 10-16 |
| Population access | `solver.py:72` | `attrs.population[partition].sum()` |

## Architecture Insights

### Design Patterns to Follow

1. **NamedTuple for results** - Use `SearchResult` to match `OptimizationResult`, `GraphAttributes`
2. **Verbose parameter** - All functions accept `verbose: bool` for diagnostic output
3. **Default constants** - Export constants (`DEFAULT_TOLERANCE`, etc.) for documentation
4. **Thin wrapper approach** - `find_optimal_mu()` orchestrates, delegates to `solve_partition()`

### Data Flow

```
find_optimal_mu(graph_data, lambda_param)
        ↓
    Binary search loop:
        ↓
        solve_partition(graph_data, lambda_param, mu)
        ↓
        Check: |selected_pop - target_pop| < tolerance?
        ↓
        Adjust: mu_min/mu_max based on result
        ↓
    SearchResult(result, iterations, mu_history, converged)
```

## Historical Context (from thoughts/)

- `thoughts/shared/research/2025-11-21-phase3-optimization-engine.md` - Comprehensive Phase 3 research including binary search algorithm design
- `thoughts/shared/plans/2025-11-21-solver-wrapper.md` - Solver wrapper implementation plan (now complete)

## Related Research

- [Phase 3 Optimization Engine](2025-11-21-phase3-optimization-engine.md) - Full Phase 3 roadmap

## Open Questions

1. **Edge case: No valid μ** - What if no μ achieves 50% (e.g., total population < target)?
2. **Tolerance selection** - Is 0.1% (~160k people) acceptable for production?
RESPONSE: Yes.
3. **Warm-start benefit** - How much time saved by warm-starting from previous λ?
4. **λ=0 handling** - When boundary cost is zero, many disconnected regions may form
RESPONSE: That is fine. Part of the purpose of this project is to see what happens at the extremes.

## Implementation Checklist

- [ ] Create `src/half_america/optimization/search.py` with `find_optimal_mu()`
- [ ] Create `SearchResult` NamedTuple
- [ ] Implement `_estimate_mu_max()` auto-scaling
- [ ] Update `optimization/__init__.py` exports
- [ ] Create `tests/test_optimization/test_search.py`
- [ ] Add monotonicity tests
- [ ] Add convergence tests
- [ ] Run full test suite: `uv run pytest`
- [ ] Type check: `uv run mypy src/half_america/optimization/`
- [ ] Lint: `uv run ruff check src/half_america/`
- [ ] Update ROADMAP.md to mark milestone complete
