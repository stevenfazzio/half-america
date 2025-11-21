# Optimization Correctness Unit Tests Implementation Plan

## Overview

Implement mathematical correctness tests for the optimization engine as the final Phase 3 task. The existing 41 tests cover behavioral correctness (convergence, types, validation) but not mathematical correctness (does it compute the right answer?). This plan adds `test_correctness.py` with tests for partition invariants, energy function, optimality, determinism, and numerical stability.

## Current State Analysis

**Existing test coverage (41 tests):**
- `test_solver.py` (15 tests): Parameter validation, result types, extreme values
- `test_search.py` (12 tests): Binary search convergence, monotonicity
- `test_sweep.py` (14 tests): Parallel execution, persistence

**Gap:** No tests verify:
- Energy function computed correctly
- Partition is mathematically optimal
- Numerical invariants hold (population/area sums)
- Results are deterministic

### Key Discoveries:
- Energy function: `E(X) = λΣ(l_ij/ρ)|x_i-x_j| + (1-λ)Σ(a_i·x_i) - μΣ(p_i·x_i)` (METHODOLOGY.md:36)
- Flow network encoding at `network.py:37-51`
- Existing fixtures: `simple_graph_data` (3-node), `complex_graph_data` (5-node) at `conftest.py:9-52`
- `OptimizationResult` at `solver.py:11-23` - need to add `energy` field

## Desired End State

A new `tests/test_optimization/test_correctness.py` file with 5 test classes (~15-20 tests total) verifying mathematical correctness. The `OptimizationResult` will include an `energy` field for verification.

**Verification:**
- All tests pass: `uv run pytest tests/test_optimization/test_correctness.py -v`
- Full suite still passes: `uv run pytest`
- Type checking passes: `uv run mypy src/`

## What We're NOT Doing

- Adding integration tests with real Census data (already covered by existing integration tests)
- Testing the binary search convergence (already covered in `test_search.py`)
- Adding CLI or visualization tests
- Refactoring existing test files

## Implementation Approach

Add `energy` field to production code first, then add test classes in priority order: invariants → energy → optimality → determinism → numerical stability.

---

## Phase 1: Add Energy Field to OptimizationResult

### Overview
Extend `OptimizationResult` with an `energy` field that computes the full energy function value. This enables correctness verification in tests and is useful for users who want to see energy values.

### Changes Required:

#### 1. Add `compute_energy` function to `network.py`
**File**: `src/half_america/graph/network.py`
**Changes**: Add function to compute energy from partition

```python
def compute_energy(
    attributes: GraphAttributes,
    edges: list[tuple[int, int]],
    partition: np.ndarray,
    lambda_param: float,
    mu: float,
) -> float:
    """
    Compute energy function value for a given partition.

    E(X) = λ Σ(l_ij/ρ)|x_i - x_j| + (1-λ) Σ a_i x_i - μ Σ p_i x_i

    Args:
        attributes: GraphAttributes with population, area, rho, edge_lengths
        edges: List of (i, j) neighbor pairs
        partition: Boolean array where True = selected
        lambda_param: Surface tension parameter [0, 1)
        mu: Lagrange multiplier

    Returns:
        Total energy value (lower is better for the optimizer)
    """
    # Boundary cost: λ Σ(l_ij/ρ)|x_i - x_j|
    # Only count edges crossing the cut (where x_i != x_j)
    boundary_cost = 0.0
    rho = attributes.rho
    for i, j in edges:
        if partition[i] != partition[j]:
            l_ij = attributes.edge_lengths[(i, j)]
            boundary_cost += lambda_param * l_ij / rho

    # Area cost: (1-λ) Σ a_i x_i (for selected nodes only)
    area_cost = (1 - lambda_param) * attributes.area[partition].sum()

    # Population reward: μ Σ p_i x_i (for selected nodes only)
    population_reward = mu * attributes.population[partition].sum()

    return boundary_cost + area_cost - population_reward
```

#### 2. Update `OptimizationResult` to include `energy`
**File**: `src/half_america/optimization/solver.py`
**Changes**: Add energy field, import compute_energy, call it in solve_partition

Update the NamedTuple:
```python
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
    energy: float  # Full energy function value
```

Update the import at top of file:
```python
from half_america.graph.network import build_flow_network, get_partition, compute_energy
```

Compute energy in `solve_partition()` before return:
```python
    # Compute energy function value
    energy = compute_energy(
        graph_data.attributes,
        graph_data.edges,
        partition,
        lambda_param,
        mu,
    )

    return OptimizationResult(
        partition=partition,
        # ... existing fields ...
        flow_value=flow_value,
        energy=energy,
    )
```

#### 3. Export `compute_energy` from graph module
**File**: `src/half_america/graph/__init__.py`
**Changes**: Add compute_energy to exports

### Success Criteria:

#### Automated Verification:
- [ ] Type checking passes: `uv run mypy src/`
- [ ] Existing tests still pass: `uv run pytest tests/test_optimization/ -v`
- [ ] Linting passes: `uv run ruff check src/`

#### Manual Verification:
- [ ] None required for this phase

**Implementation Note**: After completing this phase and all automated verification passes, proceed to Phase 2.

---

## Phase 2: Implement TestPartitionInvariants

### Overview
Add tests verifying fundamental partition properties: population and area sums, exhaustive/exclusive partition membership.

### Changes Required:

#### 1. Create `test_correctness.py`
**File**: `tests/test_optimization/test_correctness.py`
**Changes**: Create new file with TestPartitionInvariants class

```python
"""Tests for mathematical correctness of optimization."""

import numpy as np
import pytest

from half_america.optimization import solve_partition


class TestPartitionInvariants:
    """Tests verifying partition properties."""

    def test_population_sum_invariant(self, simple_graph_data):
        """Selected + unselected population equals total population."""
        result = solve_partition(
            simple_graph_data,
            lambda_param=0.5,
            mu=0.01,
            verbose=False,
        )
        attrs = simple_graph_data.attributes
        unselected_pop = int(attrs.population[~result.partition].sum())

        assert result.selected_population + unselected_pop == result.total_population

    def test_area_sum_invariant(self, simple_graph_data):
        """Selected + unselected area equals total area."""
        result = solve_partition(
            simple_graph_data,
            lambda_param=0.5,
            mu=0.01,
            verbose=False,
        )
        attrs = simple_graph_data.attributes
        unselected_area = float(attrs.area[~result.partition].sum())

        assert result.selected_area + unselected_area == pytest.approx(result.total_area)

    def test_partition_exhaustive(self, simple_graph_data):
        """Every node is assigned to exactly one partition."""
        result = solve_partition(
            simple_graph_data,
            lambda_param=0.5,
            mu=0.01,
            verbose=False,
        )
        # Partition should cover all nodes
        assert len(result.partition) == simple_graph_data.num_nodes
        # Every value should be True or False (boolean)
        assert result.partition.dtype == bool

    def test_partition_mutually_exclusive(self, simple_graph_data):
        """No node is in both partitions."""
        result = solve_partition(
            simple_graph_data,
            lambda_param=0.5,
            mu=0.01,
            verbose=False,
        )
        # By definition of boolean array, each node is either True or False
        # But let's verify selected_population matches partition
        attrs = simple_graph_data.attributes
        computed_selected_pop = int(attrs.population[result.partition].sum())

        assert computed_selected_pop == result.selected_population

    def test_invariants_hold_for_various_mu(self, simple_graph_data):
        """Partition invariants hold across different mu values."""
        for mu in [0.0, 0.001, 0.01, 0.1, 1.0, 10.0]:
            result = solve_partition(
                simple_graph_data,
                lambda_param=0.5,
                mu=mu,
                verbose=False,
            )
            attrs = simple_graph_data.attributes
            unselected_pop = int(attrs.population[~result.partition].sum())
            unselected_area = float(attrs.area[~result.partition].sum())

            assert result.selected_population + unselected_pop == result.total_population
            assert result.selected_area + unselected_area == pytest.approx(result.total_area)
```

### Success Criteria:

#### Automated Verification:
- [ ] New tests pass: `uv run pytest tests/test_optimization/test_correctness.py::TestPartitionInvariants -v`
- [ ] Full test suite passes: `uv run pytest`

#### Manual Verification:
- [ ] None required for this phase

**Implementation Note**: After completing this phase and all automated verification passes, proceed to Phase 3.

---

## Phase 3: Implement TestEnergyFunction

### Overview
Add tests verifying the energy function is computed correctly by manually calculating expected values for known partitions.

### Changes Required:

#### 1. Add TestEnergyFunction class
**File**: `tests/test_optimization/test_correctness.py`
**Changes**: Add class with energy verification tests

```python
class TestEnergyFunction:
    """Tests verifying energy calculation."""

    def test_energy_for_empty_partition(self, simple_graph_data):
        """Energy for selecting nothing (mu=0) should be zero."""
        result = solve_partition(
            simple_graph_data,
            lambda_param=0.5,
            mu=0.0,
            verbose=False,
        )
        # No nodes selected means:
        # - boundary_cost = 0 (no cuts needed)
        # - area_cost = 0 (no areas selected)
        # - population_reward = 0 (no populations selected)
        assert result.partition.sum() == 0
        assert result.energy == pytest.approx(0.0)

    def test_energy_for_full_partition(self, simple_graph_data):
        """Energy for selecting everything (high mu) should match manual calc."""
        result = solve_partition(
            simple_graph_data,
            lambda_param=0.5,
            mu=1000.0,
            verbose=False,
        )
        assert result.partition.all()

        # Manual calculation for full partition:
        # - boundary_cost = 0 (no cuts - all in same partition)
        # - area_cost = (1-0.5) * (1000+1000+1000) = 0.5 * 3000 = 1500
        # - population_reward = 1000 * (100+200+300) = 600000
        # energy = 0 + 1500 - 600000 = -598500
        expected_energy = 0.0 + 0.5 * 3000.0 - 1000.0 * 600.0
        assert result.energy == pytest.approx(expected_energy)

    def test_energy_boundary_term_only(self, simple_graph_data):
        """Test boundary term calculation in isolation."""
        # With lambda=0, boundary cost vanishes
        # Energy = (1-0)*area - mu*pop = area - mu*pop
        result = solve_partition(
            simple_graph_data,
            lambda_param=0.0,
            mu=1000.0,
            verbose=False,
        )
        # Full selection expected
        assert result.partition.all()

        # boundary_cost = 0 (lambda=0)
        # area_cost = 1.0 * 3000 = 3000
        # population_reward = 1000 * 600 = 600000
        expected_energy = 0.0 + 1.0 * 3000.0 - 1000.0 * 600.0
        assert result.energy == pytest.approx(expected_energy)

    def test_energy_manual_calculation_partial_selection(self, simple_graph_data):
        """Verify energy matches manual calculation for partial selection."""
        # simple_graph_data: 3 nodes in chain 0--1--2
        # populations: [100, 200, 300], areas: [1000, 1000, 1000]
        # edge_lengths: (0,1)=50, (1,2)=50, rho=100

        # Choose mu that selects node 2 only (highest population density)
        # We need to find a mu where only node 2 is selected
        # Area cost for node 2: (1-lambda)*1000 = 500 (at lambda=0.5)
        # Population reward for node 2: mu*300
        # For node 2 to be selected: mu*300 > 500 => mu > 1.67

        # Try various mu values and verify energy
        for mu in [0.5, 1.0, 2.0]:
            result = solve_partition(
                simple_graph_data,
                lambda_param=0.5,
                mu=mu,
                verbose=False,
            )

            # Manually compute expected energy
            attrs = simple_graph_data.attributes
            partition = result.partition

            # Boundary cost
            boundary_cost = 0.0
            for i, j in simple_graph_data.edges:
                if partition[i] != partition[j]:
                    l_ij = attrs.edge_lengths[(i, j)]
                    boundary_cost += 0.5 * l_ij / attrs.rho

            # Area cost
            area_cost = 0.5 * attrs.area[partition].sum()

            # Population reward
            pop_reward = mu * attrs.population[partition].sum()

            expected_energy = boundary_cost + area_cost - pop_reward
            assert result.energy == pytest.approx(expected_energy, rel=1e-9)
```

### Success Criteria:

#### Automated Verification:
- [ ] New tests pass: `uv run pytest tests/test_optimization/test_correctness.py::TestEnergyFunction -v`
- [ ] Full test suite passes: `uv run pytest`

#### Manual Verification:
- [ ] None required for this phase

**Implementation Note**: After completing this phase and all automated verification passes, proceed to Phase 4.

---

## Phase 4: Implement TestOptimality

### Overview
Add brute-force tests that enumerate all 2^n partitions for small graphs (n=3,4,5,6) and verify the graph cut finds the optimal solution.

### Changes Required:

#### 1. Add helper fixture for tiny graphs
**File**: `tests/test_optimization/conftest.py`
**Changes**: Add parametrized fixture for tiny graphs

```python
@pytest.fixture
def tiny_graph_factory():
    """Factory to create tiny graphs for brute-force testing."""
    def _create(n: int) -> GraphData:
        """Create n-node linear chain graph."""
        # Generate populations that sum to nice numbers
        populations = np.array([100 * (i + 1) for i in range(n)])
        areas = np.array([1000.0] * n)

        # Linear chain edges
        edges = [(i, i + 1) for i in range(n - 1)]

        # Edge lengths all equal
        edge_lengths = {}
        for i, j in edges:
            edge_lengths[(i, j)] = 50.0
            edge_lengths[(j, i)] = 50.0

        attributes = GraphAttributes(
            population=populations,
            area=areas,
            rho=100.0,
            edge_lengths=edge_lengths,
        )
        return GraphData(
            edges=edges,
            attributes=attributes,
            num_nodes=n,
            num_edges=len(edges),
        )
    return _create
```

#### 2. Add TestOptimality class
**File**: `tests/test_optimization/test_correctness.py`
**Changes**: Add class with brute-force optimality tests

```python
from itertools import product
from half_america.graph.network import compute_energy


class TestOptimality:
    """Tests verifying solution is optimal."""

    @pytest.mark.parametrize("n", [3, 4, 5, 6])
    def test_optimal_vs_brute_force(self, tiny_graph_factory, n):
        """Verify graph cut finds minimum energy partition."""
        graph_data = tiny_graph_factory(n)

        lambda_param = 0.5
        mu = 0.5  # Moderate mu

        # Get solver result
        result = solve_partition(
            graph_data,
            lambda_param=lambda_param,
            mu=mu,
            verbose=False,
        )
        solver_energy = result.energy

        # Brute-force: enumerate all 2^n partitions
        min_energy = float('inf')
        for bits in product([False, True], repeat=n):
            partition = np.array(bits)
            energy = compute_energy(
                graph_data.attributes,
                graph_data.edges,
                partition,
                lambda_param,
                mu,
            )
            if energy < min_energy:
                min_energy = energy

        # Solver should find the minimum
        assert solver_energy == pytest.approx(min_energy, rel=1e-9)

    def test_no_improving_single_swap(self, simple_graph_data):
        """Verify no single-node swap improves the objective."""
        result = solve_partition(
            simple_graph_data,
            lambda_param=0.5,
            mu=0.5,
            verbose=False,
        )
        solver_energy = result.energy

        # Try flipping each node
        for i in range(simple_graph_data.num_nodes):
            swapped_partition = result.partition.copy()
            swapped_partition[i] = not swapped_partition[i]

            swapped_energy = compute_energy(
                simple_graph_data.attributes,
                simple_graph_data.edges,
                swapped_partition,
                0.5,
                0.5,
            )

            # Original should be at least as good
            assert solver_energy <= swapped_energy + 1e-9, (
                f"Swap at node {i} improves energy: {solver_energy} > {swapped_energy}"
            )
```

### Success Criteria:

#### Automated Verification:
- [ ] New tests pass: `uv run pytest tests/test_optimization/test_correctness.py::TestOptimality -v`
- [ ] Full test suite passes: `uv run pytest`

#### Manual Verification:
- [ ] None required for this phase

**Implementation Note**: After completing this phase and all automated verification passes, proceed to Phase 5.

---

## Phase 5: Implement TestDeterminism

### Overview
Add tests verifying that identical inputs produce identical outputs across multiple runs.

### Changes Required:

#### 1. Add TestDeterminism class
**File**: `tests/test_optimization/test_correctness.py`
**Changes**: Add class with determinism tests

```python
class TestDeterminism:
    """Tests verifying reproducibility."""

    def test_repeated_runs_identical(self, simple_graph_data):
        """Same inputs produce identical outputs."""
        results = []
        for _ in range(5):
            result = solve_partition(
                simple_graph_data,
                lambda_param=0.5,
                mu=0.5,
                verbose=False,
            )
            results.append(result)

        # All results should be identical
        for i in range(1, len(results)):
            assert np.array_equal(results[0].partition, results[i].partition)
            assert results[0].energy == results[i].energy
            assert results[0].selected_population == results[i].selected_population
            assert results[0].flow_value == results[i].flow_value

    def test_determinism_across_lambda_values(self, simple_graph_data):
        """Determinism holds for various lambda values."""
        for lambda_param in [0.0, 0.3, 0.5, 0.7, 0.9]:
            results = []
            for _ in range(3):
                result = solve_partition(
                    simple_graph_data,
                    lambda_param=lambda_param,
                    mu=0.5,
                    verbose=False,
                )
                results.append(result)

            # All results for this lambda should be identical
            for i in range(1, len(results)):
                assert np.array_equal(results[0].partition, results[i].partition)
```

### Success Criteria:

#### Automated Verification:
- [ ] New tests pass: `uv run pytest tests/test_optimization/test_correctness.py::TestDeterminism -v`
- [ ] Full test suite passes: `uv run pytest`

#### Manual Verification:
- [ ] None required for this phase

**Implementation Note**: After completing this phase and all automated verification passes, proceed to Phase 6.

---

## Phase 6: Implement TestNumericalStability

### Overview
Add tests for numerical edge cases with extreme population/area values.

### Changes Required:

#### 1. Add TestNumericalStability class
**File**: `tests/test_optimization/test_correctness.py`
**Changes**: Add class with numerical stability tests

```python
class TestNumericalStability:
    """Tests for numerical edge cases."""

    def test_tiny_populations(self):
        """Handle very small populations (1 person per tract)."""
        attributes = GraphAttributes(
            population=np.array([1, 1, 1]),
            area=np.array([1000.0, 1000.0, 1000.0]),
            rho=100.0,
            edge_lengths={(0, 1): 50.0, (1, 0): 50.0, (1, 2): 50.0, (2, 1): 50.0},
        )
        graph_data = GraphData(
            edges=[(0, 1), (1, 2)],
            attributes=attributes,
            num_nodes=3,
            num_edges=2,
        )

        result = solve_partition(graph_data, lambda_param=0.5, mu=1000.0, verbose=False)

        # Should not crash and should produce valid result
        assert result.total_population == 3
        assert len(result.partition) == 3

    def test_large_populations(self):
        """Handle large populations (1 million per tract)."""
        attributes = GraphAttributes(
            population=np.array([1_000_000, 1_000_000, 1_000_000]),
            area=np.array([1000.0, 1000.0, 1000.0]),
            rho=100.0,
            edge_lengths={(0, 1): 50.0, (1, 0): 50.0, (1, 2): 50.0, (2, 1): 50.0},
        )
        graph_data = GraphData(
            edges=[(0, 1), (1, 2)],
            attributes=attributes,
            num_nodes=3,
            num_edges=2,
        )

        result = solve_partition(graph_data, lambda_param=0.5, mu=0.00001, verbose=False)

        # Should not crash and should produce valid result
        assert result.total_population == 3_000_000
        assert len(result.partition) == 3

    def test_extreme_lambda_near_zero(self, simple_graph_data):
        """Lambda near 0 (minimize area only)."""
        result = solve_partition(
            simple_graph_data,
            lambda_param=0.001,
            mu=0.001,
            verbose=False,
        )

        # Should produce valid result
        assert len(result.partition) == simple_graph_data.num_nodes
        # Invariants should hold
        attrs = simple_graph_data.attributes
        unselected_pop = int(attrs.population[~result.partition].sum())
        assert result.selected_population + unselected_pop == result.total_population

    def test_extreme_lambda_near_one(self, simple_graph_data):
        """Lambda near 1 (minimize boundary only)."""
        result = solve_partition(
            simple_graph_data,
            lambda_param=0.99,
            mu=0.5,
            verbose=False,
        )

        # Should produce valid result
        assert len(result.partition) == simple_graph_data.num_nodes
        # Energy should be computed correctly
        assert isinstance(result.energy, float)
```

### Success Criteria:

#### Automated Verification:
- [ ] New tests pass: `uv run pytest tests/test_optimization/test_correctness.py::TestNumericalStability -v`
- [ ] Full test suite passes: `uv run pytest`
- [ ] All tests pass: `uv run pytest -v`
- [ ] Type checking passes: `uv run mypy src/`
- [ ] Linting passes: `uv run ruff check src/ tests/`

#### Manual Verification:
- [ ] Review test coverage and confirm all recommended correctness tests from research are implemented

**Implementation Note**: After completing this phase and all verification passes, the Phase 3 optimization correctness task is complete.

---

## Testing Strategy

### Unit Tests Added:
- `TestPartitionInvariants`: 5 tests for population/area sum invariants
- `TestEnergyFunction`: 4 tests for energy calculation verification
- `TestOptimality`: 2 tests (1 parametrized over n=3,4,5,6) for brute-force optimality
- `TestDeterminism`: 2 tests for reproducibility
- `TestNumericalStability`: 4 tests for extreme values

### Key Edge Cases:
- Empty partition (mu=0)
- Full partition (high mu)
- Partial partitions with known expected values
- Tiny populations (1 person)
- Large populations (1 million)
- Lambda extremes (0.001 and 0.99)

## Performance Considerations

- Brute-force tests limited to n≤6 (64 partitions max) to keep tests fast
- No real Census data in unit tests - synthetic fixtures only
- Tests should complete in <1 second each

## References

- Research: `thoughts/shared/research/2025-11-21-unit-tests-optimization-correctness.md`
- METHODOLOGY.md energy function: lines 32-36
- Existing tests: `tests/test_optimization/test_*.py`
- Solver implementation: `src/half_america/optimization/solver.py`
- Network construction: `src/half_america/graph/network.py`
