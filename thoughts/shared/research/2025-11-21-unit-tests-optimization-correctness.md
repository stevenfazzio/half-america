---
date: 2025-11-21T00:00:00-08:00
researcher: Claude
git_commit: 7048b3d9ee7503f6c80854627bc971b5e62b60b5
branch: master
repository: half-america
topic: "Unit tests for optimization correctness"
tags: [research, codebase, optimization, testing, phase3]
status: complete
last_updated: 2025-11-21
last_updated_by: Claude
---

# Research: Unit Tests for Optimization Correctness

**Date**: 2025-11-21
**Researcher**: Claude
**Git Commit**: 7048b3d9ee7503f6c80854627bc971b5e62b60b5
**Branch**: master
**Repository**: half-america

## Research Question

What unit tests are needed for "optimization correctness" as the final remaining task in Phase 3 of the ROADMAP.md?

## Summary

The optimization engine already has comprehensive tests (~40+ tests) covering parameter validation, convergence, monotonicity, and persistence. However, the existing tests focus on **behavioral correctness** (does it converge? does it return the right types?) rather than **mathematical correctness** (does it compute the right answer?).

The key gap is **correctness verification tests** that validate:
1. The energy function is computed correctly
2. The graph cut produces an optimal partition
3. Numerical invariants hold (population sums, area sums)
4. Results are deterministic and reproducible

## Detailed Findings

### Current Test Coverage

The existing test suite has **41 tests** across three files:

| File | Test Count | Focus |
|------|------------|-------|
| `test_solver.py` | 15 tests | Parameter validation, result types, extreme values |
| `test_search.py` | 12 tests | Binary search convergence, monotonicity, edge cases |
| `test_sweep.py` | 14 tests | Parallel execution, persistence, cache paths |

**What IS Tested:**
- Parameter validation (lambda bounds, mu bounds)
- Return types (OptimizationResult, SearchResult, SweepResult)
- Extreme mu values (0 selects none, high selects all)
- Monotonicity property (higher mu → more selection)
- Binary search convergence within tolerance
- Lambda edge cases (0.0 valid, 1.0 rejected, 0.99 valid)
- Result persistence (save/load roundtrip)
- Parallel execution performance

### Gaps: Missing Correctness Tests

The following correctness properties are NOT currently tested:

#### 1. Energy Function Correctness
No tests verify the energy function calculation:
```
E(X) = λ∑(l_ij/ρ)|x_i-x_j| + (1-λ)∑(a_i·x_i) - μ∑(p_i·x_i)
```

**Needed tests:**
- Given a known partition, verify computed energy matches manual calculation
- Verify energy components (boundary cost, area cost, population reward) individually

#### 2. Partition Invariants
No tests verify fundamental partition properties:

**Needed tests:**
- `selected_population + unselected_population == total_population`
- `selected_area + unselected_area == total_area`
- Every node is in exactly one partition (exhaustive, mutually exclusive)
- Partition is a valid s-t cut (no path from source to sink after cut)

#### 3. Optimality Verification
No tests verify the partition is optimal:

**Needed tests:**
- For small graphs, compare against brute-force enumeration of all 2^n partitions
- Verify no single-node swap improves the objective
- Verify the cut is indeed the minimum cut (flow equals cut capacity)

#### 4. Determinism/Reproducibility
No tests verify same inputs → same outputs:

**Needed tests:**
- Run same optimization twice, verify identical results
- Verify partition bits are identical, not just statistics

#### 5. Numerical Stability
No tests for edge cases with extreme values:

**Needed tests:**
- Very small populations (1 person)
- Very large populations (1 million people)
- Very small areas (1 sq meter)
- Very large areas (1 million sq meters)
- Edge lengths near zero vs very long

#### 6. Boundary Calculation Correctness
No tests verify the boundary term is calculated correctly:

**Needed tests:**
- For known geometry, verify total boundary length of selected region
- Verify boundary only counts edges crossing the cut

### Recommended Test Categories

Based on the analysis, here are the recommended test categories to add:

```
tests/test_optimization/
├── test_solver.py          # Existing - behavioral tests
├── test_search.py          # Existing - convergence tests
├── test_sweep.py           # Existing - parallel/persistence tests
└── test_correctness.py     # NEW - mathematical correctness tests
```

#### Proposed `test_correctness.py` Structure:

```python
class TestPartitionInvariants:
    """Tests verifying partition properties."""
    def test_population_sum_invariant(self): ...
    def test_area_sum_invariant(self): ...
    def test_partition_exhaustive(self): ...
    def test_partition_mutually_exclusive(self): ...

class TestEnergyFunction:
    """Tests verifying energy calculation."""
    def test_energy_boundary_term(self): ...
    def test_energy_area_term(self): ...
    def test_energy_population_term(self): ...
    def test_energy_total_matches_manual(self): ...

class TestOptimality:
    """Tests verifying solution is optimal."""
    def test_optimal_vs_brute_force_tiny_graph(self): ...
    def test_no_improving_swap(self): ...
    def test_flow_equals_cut(self): ...

class TestDeterminism:
    """Tests verifying reproducibility."""
    def test_repeated_runs_identical(self): ...
    def test_parallel_determinism(self): ...

class TestNumericalStability:
    """Tests for numerical edge cases."""
    def test_tiny_populations(self): ...
    def test_large_populations(self): ...
    def test_extreme_lambda_values(self): ...
```

## Code References

### Optimization Implementation
- [`src/half_america/optimization/solver.py:30-106`](https://github.com/stevenfazzio/half-america/blob/7048b3d9ee7503f6c80854627bc971b5e62b60b5/src/half_america/optimization/solver.py#L30-L106) - `solve_partition()` main solver
- [`src/half_america/optimization/search.py:27-119`](https://github.com/stevenfazzio/half-america/blob/7048b3d9ee7503f6c80854627bc971b5e62b60b5/src/half_america/optimization/search.py#L27-L119) - `find_optimal_mu()` binary search
- [`src/half_america/optimization/sweep.py:58-163`](https://github.com/stevenfazzio/half-america/blob/7048b3d9ee7503f6c80854627bc971b5e62b60b5/src/half_america/optimization/sweep.py#L58-L163) - `sweep_lambda()` parallel sweep
- [`src/half_america/graph/network.py:9-53`](https://github.com/stevenfazzio/half-america/blob/7048b3d9ee7503f6c80854627bc971b5e62b60b5/src/half_america/graph/network.py#L9-L53) - `build_flow_network()` graph construction

### Existing Tests
- [`tests/test_optimization/test_solver.py`](https://github.com/stevenfazzio/half-america/blob/7048b3d9ee7503f6c80854627bc971b5e62b60b5/tests/test_optimization/test_solver.py) - 15 behavioral tests
- [`tests/test_optimization/test_search.py`](https://github.com/stevenfazzio/half-america/blob/7048b3d9ee7503f6c80854627bc971b5e62b60b5/tests/test_optimization/test_search.py) - 12 convergence tests
- [`tests/test_optimization/test_sweep.py`](https://github.com/stevenfazzio/half-america/blob/7048b3d9ee7503f6c80854627bc971b5e62b60b5/tests/test_optimization/test_sweep.py) - 14 parallel/persistence tests

### Test Fixtures
- [`tests/test_optimization/conftest.py:9-23`](https://github.com/stevenfazzio/half-america/blob/7048b3d9ee7503f6c80854627bc971b5e62b60b5/tests/test_optimization/conftest.py#L9-L23) - `simple_graph_data` (3-node chain)
- [`tests/test_optimization/conftest.py:26-52`](https://github.com/stevenfazzio/half-america/blob/7048b3d9ee7503f6c80854627bc971b5e62b60b5/tests/test_optimization/conftest.py#L26-L52) - `complex_graph_data` (5-node chain)

### Key Constants
- `TARGET_TOLERANCE = 0.01` at `solver.py:27`
- `DEFAULT_MAX_ITERATIONS = 50` at `search.py:23`
- `DEFAULT_LAMBDA_VALUES = [0.0, 0.1, ..., 0.9]` at `sweep.py:32`

## Architecture Insights

### Energy Function Encoding
The optimization encodes the energy function into a flow network:
- **Source capacity (t-link)**: `mu * p_i` - population reward
- **Sink capacity (t-link)**: `(1 - lambda) * a_i` - area cost
- **Edge capacity (n-link)**: `lambda * l_ij / rho` - boundary cost

This is the standard graph-cut formulation for binary MRF optimization.

### Test Design Pattern
Current tests use class-based organization:
- `TestXxx` classes group related tests
- Fixtures from `conftest.py` provide test data
- `pytest.approx()` for floating-point comparisons
- `pytest.raises()` with regex matching for exceptions

### Fixture Design
Test fixtures use synthetic grid geometries rather than real Census data:
- `simple_graph_data`: 3-node linear chain (populations: 100, 200, 300)
- `complex_graph_data`: 5-node linear chain (populations: 80, 120, 150, 200, 250)

This ensures deterministic, fast tests but means edge cases from real data aren't tested.

## Historical Context (from thoughts/)

Related implementation documents:
- `thoughts/shared/plans/2025-11-21-solver-wrapper.md` - Solver implementation plan
- `thoughts/shared/plans/2025-11-21-binary-search-lagrange-multiplier.md` - Binary search plan
- `thoughts/shared/research/2025-11-21-lambda-edge-cases.md` - Lambda edge case analysis
- `thoughts/shared/research/2025-11-21-performance-benchmarking-optimization.md` - Performance research

## Implementation Recommendations

### Priority 1: Partition Invariants (Quick Wins)
- Simple to implement
- High confidence impact
- Tests: population sum, area sum, exhaustive partition

### Priority 2: Energy Function Tests
- Requires manual energy calculation for known cases
- Medium complexity
- Tests: individual terms, total energy

### Priority 3: Optimality Tests
- Requires brute-force comparison for tiny graphs
- Higher complexity but high value
- Tests: compare against enumeration for 3-4 node graphs

### Priority 4: Determinism Tests
- Simple but important
- Tests: repeated runs, parallel consistency

### Priority 5: Numerical Stability
- Lower priority unless issues arise
- Tests: extreme values, edge cases

## Open Questions

1. **Test data coverage**: Should correctness tests use real Census data or synthetic fixtures?
   - Pro synthetic: Deterministic, fast, known expected values
   - Pro real data: Catches real-world edge cases

2. **Brute force scope**: For optimality tests, what's the maximum graph size for brute-force?
   - 2^n grows fast: n=20 is ~1M partitions
   - Recommend: n≤8 for brute-force tests (256 partitions)

3. **Energy function access**: Currently `solve_partition` doesn't return energy value
   - May need to add `energy` field to `OptimizationResult`
   - Or create separate `compute_energy()` function for testing

4. **Tolerance for "correctness"**: What numerical tolerance is acceptable?
   - Current `TARGET_TOLERANCE = 0.01` (1% population deviation)
   - For testing, might need tighter tolerance on synthetic data
