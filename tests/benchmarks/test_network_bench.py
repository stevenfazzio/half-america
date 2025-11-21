"""Benchmarks for flow network construction."""

from half_america.graph.network import build_flow_network, get_partition


class TestBuildFlowNetworkBench:
    """Benchmarks for build_flow_network()."""

    def test_build_network_20x20(self, benchmark, benchmark_graph_data):
        """Benchmark network construction on 20x20 grid (400 nodes)."""
        result = benchmark(
            build_flow_network,
            benchmark_graph_data.attributes,
            benchmark_graph_data.edges,
            lambda_param=0.5,
            mu=0.001,
        )
        # Verify result is a maxflow graph by checking it has expected methods
        assert hasattr(result, "maxflow")
        assert hasattr(result, "get_segment")

    def test_build_network_50x50(self, benchmark, large_graph_data):
        """Benchmark network construction on 50x50 grid (2500 nodes)."""
        result = benchmark(
            build_flow_network,
            large_graph_data.attributes,
            large_graph_data.edges,
            lambda_param=0.5,
            mu=0.001,
        )
        # Verify result is a maxflow graph by checking it has expected methods
        assert hasattr(result, "maxflow")
        assert hasattr(result, "get_segment")


class TestMaxflowSolveBench:
    """Benchmarks for maxflow computation."""

    def test_maxflow_solve_20x20(self, benchmark, benchmark_graph_data):
        """Benchmark maxflow solve on 20x20 grid."""

        def solve():
            # Must rebuild graph each time - PyMaxFlow graphs are single-use
            g = build_flow_network(
                benchmark_graph_data.attributes,
                benchmark_graph_data.edges,
                lambda_param=0.5,
                mu=0.001,
            )
            return g.maxflow()

        result = benchmark(solve)
        assert result >= 0

    def test_maxflow_solve_50x50(self, benchmark, large_graph_data):
        """Benchmark maxflow solve on 50x50 grid."""

        def solve():
            g = build_flow_network(
                large_graph_data.attributes,
                large_graph_data.edges,
                lambda_param=0.5,
                mu=0.001,
            )
            return g.maxflow()

        result = benchmark(solve)
        assert result >= 0


class TestGetPartitionBench:
    """Benchmarks for partition extraction."""

    def test_get_partition_20x20(self, benchmark, benchmark_graph_data):
        """Benchmark partition extraction on 20x20 grid."""
        g = build_flow_network(
            benchmark_graph_data.attributes,
            benchmark_graph_data.edges,
            lambda_param=0.5,
            mu=0.001,
        )
        g.maxflow()
        num_nodes = len(benchmark_graph_data.attributes.population)

        result = benchmark(get_partition, g, num_nodes)
        assert len(result) == num_nodes

    def test_get_partition_50x50(self, benchmark, large_graph_data):
        """Benchmark partition extraction on 50x50 grid."""
        g = build_flow_network(
            large_graph_data.attributes,
            large_graph_data.edges,
            lambda_param=0.5,
            mu=0.001,
        )
        g.maxflow()
        num_nodes = len(large_graph_data.attributes.population)

        result = benchmark(get_partition, g, num_nodes)
        assert len(result) == num_nodes
