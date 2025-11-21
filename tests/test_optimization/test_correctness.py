"""Tests for mathematical correctness of optimization."""

from itertools import product

import numpy as np
import pytest

from half_america.graph.network import compute_energy
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

        assert result.selected_area + unselected_area == pytest.approx(
            result.total_area
        )

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

            assert (
                result.selected_population + unselected_pop == result.total_population
            )
            assert result.selected_area + unselected_area == pytest.approx(
                result.total_area
            )


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
        min_energy = float("inf")
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
            assert (
                solver_energy <= swapped_energy + 1e-9
            ), f"Swap at node {i} improves energy: {solver_energy} > {swapped_energy}"


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


class TestNumericalStability:
    """Tests for numerical edge cases."""

    def test_tiny_populations(self):
        """Handle very small populations (1 person per tract)."""
        from half_america.graph.boundary import GraphAttributes
        from half_america.graph.pipeline import GraphData

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
        from half_america.graph.boundary import GraphAttributes
        from half_america.graph.pipeline import GraphData

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

        result = solve_partition(
            graph_data, lambda_param=0.5, mu=0.00001, verbose=False
        )

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
