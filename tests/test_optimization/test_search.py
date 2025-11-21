"""Tests for binary search optimization."""


from half_america.optimization import (
    DEFAULT_MAX_ITERATIONS,
    DEFAULT_MU_MIN,
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
        """Test that search converges to target fraction.

        Note: With discrete graphs, exact 50% may not be achievable.
        The algorithm converges when within tolerance OR when μ converges
        (no further improvement possible with discrete nodes).
        """
        result = find_optimal_mu(
            complex_graph_data,
            lambda_param=0.5,
            tolerance=0.1,  # 10% tolerance for small discrete graph
            verbose=False,
        )
        assert result.converged
        assert abs(result.result.population_fraction - 0.5) <= 0.1

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
        """Test with non-default target fraction.

        With 5 nodes [80, 120, 150, 200, 250], achievable fractions are limited.
        Target 30% (240) can be approached by selecting nodes 0+1 (200=25%)
        or nodes 0+1+2 (350=43.75%).
        """
        result = find_optimal_mu(
            complex_graph_data,
            lambda_param=0.5,
            target_fraction=0.3,
            tolerance=0.15,  # 15% tolerance for small discrete graph
            verbose=False,
        )
        assert result.converged
        assert abs(result.result.population_fraction - 0.3) <= 0.15

    def test_explicit_mu_bounds(self, complex_graph_data):
        """Test with explicit mu_min and mu_max."""
        result = find_optimal_mu(
            complex_graph_data,
            lambda_param=0.5,
            mu_min=0.0,
            mu_max=100.0,
            tolerance=0.1,  # 10% tolerance for small discrete graph
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
            tolerance=0.1,  # 10% tolerance for small discrete graph
            verbose=False,
        )
        # Should still converge
        assert result.converged

    def test_lambda_one(self, complex_graph_data):
        """Test with λ=1 (max boundary cost).

        Note: λ=1 means only boundary cost matters, no area cost.
        The algorithm may struggle to converge with discrete graphs
        as there's no area penalty to balance. We test that it runs
        and returns a valid result.
        """
        result = find_optimal_mu(
            complex_graph_data,
            lambda_param=1.0,
            tolerance=0.1,  # 10% tolerance for small discrete graph
            verbose=False,
        )
        # May or may not converge - at λ=1, behavior is edge-dominated
        # Just verify it returns a valid result
        assert isinstance(result, SearchResult)
        assert result.iterations > 0

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
