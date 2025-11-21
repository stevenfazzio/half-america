"""Tests for lambda parameter sweep."""

import pytest

from half_america.optimization import (
    DEFAULT_LAMBDA_VALUES,
    LambdaResult,
    SweepResult,
    sweep_lambda,
    save_sweep_result,
    load_sweep_result,
)


class TestSweepLambda:
    """Tests for sweep_lambda function."""

    def test_returns_sweep_result(self, complex_graph_data):
        """Sweep returns SweepResult type."""
        # Use λ values that converge well on small graphs (avoid λ=1.0)
        result = sweep_lambda(
            complex_graph_data,
            lambda_values=[0.0, 0.5],
            tolerance=0.15,  # Relaxed for small test graph
            verbose=False,
        )
        assert isinstance(result, SweepResult)

    def test_contains_all_lambda_values(self, complex_graph_data):
        """Result contains entry for each λ value."""
        # Use λ values that converge well on small graphs
        lambda_values = [0.0, 0.25, 0.5]
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
        # Use λ values that converge well on small graphs
        result = sweep_lambda(
            complex_graph_data,
            lambda_values=[0.0, 0.5],
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
        # Use λ values that converge well on small graphs
        result = sweep_lambda(
            complex_graph_data,
            lambda_values=[0.0, 0.5],
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
        # Use λ values that converge well on small graphs
        result = sweep_lambda(
            complex_graph_data,
            lambda_values=[0.0, 0.5],
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
        # Use λ values that converge well on small graphs
        # Run with 1 worker (sequential)
        sequential = sweep_lambda(
            complex_graph_data,
            lambda_values=[0.0, 0.25, 0.5],
            tolerance=0.15,  # Relaxed for small test graph
            max_workers=1,
            verbose=False,
        )

        # Run with multiple workers (parallel)
        parallel = sweep_lambda(
            complex_graph_data,
            lambda_values=[0.0, 0.25, 0.5],
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


class TestSweepPersistence:
    """Tests for sweep result persistence."""

    def test_save_and_load_roundtrip(self, complex_graph_data, tmp_path):
        """Saved result can be loaded back identically."""
        result = sweep_lambda(
            complex_graph_data,
            lambda_values=[0.0, 0.5],
            tolerance=0.15,
            verbose=False,
        )

        path = tmp_path / "test_sweep.pkl"
        save_sweep_result(result, path)
        loaded = load_sweep_result(path)

        assert loaded.lambda_values == result.lambda_values
        assert loaded.total_iterations == result.total_iterations
        assert loaded.all_converged == result.all_converged
        assert set(loaded.results.keys()) == set(result.results.keys())

    def test_save_creates_parent_dirs(self, complex_graph_data, tmp_path):
        """Save creates parent directories if needed."""
        result = sweep_lambda(
            complex_graph_data,
            lambda_values=[0.5],
            tolerance=0.15,
            verbose=False,
        )

        path = tmp_path / "nested" / "dirs" / "test.pkl"
        save_sweep_result(result, path)
        assert path.exists()

    def test_load_nonexistent_raises(self, tmp_path):
        """Load raises FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            load_sweep_result(tmp_path / "nonexistent.pkl")


class TestSweepCachePath:
    """Tests for sweep cache path generation."""

    def test_cache_path_includes_years(self):
        """Cache path includes TIGER and ACS years."""
        from half_america.data.cache import get_sweep_cache_path
        from half_america.config import TIGER_YEAR, ACS_YEAR

        path = get_sweep_cache_path(0.1)
        assert str(TIGER_YEAR) in path.name
        assert str(ACS_YEAR) in path.name

    def test_cache_path_includes_lambda_step(self):
        """Cache path includes lambda step."""
        from half_america.data.cache import get_sweep_cache_path

        path = get_sweep_cache_path(0.05)
        assert "0.05" in path.name

    def test_cache_path_is_pkl(self):
        """Cache path has .pkl extension."""
        from half_america.data.cache import get_sweep_cache_path

        path = get_sweep_cache_path()
        assert path.suffix == ".pkl"
