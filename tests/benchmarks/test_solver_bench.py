"""Benchmarks for optimization solver."""

from half_america.optimization.search import find_optimal_mu
from half_america.optimization.sweep import sweep_lambda


class TestFindOptimalMuBench:
    """Benchmarks for binary search optimization."""

    def test_find_optimal_mu_20x20(self, benchmark, benchmark_graph_data):
        """Benchmark binary search on 20x20 grid."""
        result = benchmark(
            find_optimal_mu,
            benchmark_graph_data,
            lambda_param=0.5,
            target_fraction=0.5,
            tolerance=0.01,
            verbose=False,
        )
        assert result.converged
        assert 0.49 <= result.result.population_fraction <= 0.51

    def test_find_optimal_mu_50x50(self, benchmark, large_graph_data):
        """Benchmark binary search on 50x50 grid."""
        result = benchmark(
            find_optimal_mu,
            large_graph_data,
            lambda_param=0.5,
            target_fraction=0.5,
            tolerance=0.01,
            verbose=False,
        )
        assert result.converged


class TestSweepLambdaBench:
    """Benchmarks for full lambda sweep."""

    def test_sweep_3_lambdas_20x20(self, benchmark, benchmark_graph_data):
        """Benchmark sweep with 3 lambda values on 20x20 grid."""
        result = benchmark(
            sweep_lambda,
            benchmark_graph_data,
            lambda_values=[0.0, 0.5, 0.9],
            tolerance=0.01,
            max_workers=1,  # Sequential for reproducible timing
            verbose=False,
        )
        assert result.all_converged
        assert len(result.results) == 3

    def test_sweep_parallel_20x20(self, benchmark, benchmark_graph_data):
        """Benchmark parallel sweep on 20x20 grid."""
        result = benchmark(
            sweep_lambda,
            benchmark_graph_data,
            lambda_values=[0.0, 0.5, 0.9],
            tolerance=0.01,
            max_workers=3,  # Parallel
            verbose=False,
        )
        assert result.all_converged
