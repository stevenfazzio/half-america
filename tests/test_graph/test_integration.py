"""Integration tests for graph construction pipeline."""

import pytest
from half_america.data import load_state_tracts
from half_america.graph import (
    build_adjacency,
    compute_graph_attributes,
    build_flow_network,
    get_partition,
)


@pytest.mark.integration
class TestGraphIntegration:
    def test_full_pipeline_single_state(self):
        """Test full graph pipeline with DC (smallest state)."""
        # Load DC tracts (District of Columbia, FIPS 11)
        gdf = load_state_tracts("11")

        # Build adjacency
        adj_result = build_adjacency(gdf, verbose=True)
        assert adj_result.num_nodes > 0
        assert adj_result.num_edges > 0

        # Compute attributes
        attrs = compute_graph_attributes(gdf, adj_result.edges, verbose=True)
        assert attrs.rho > 0
        assert attrs.population.sum() > 0

        # Build network and solve
        g = build_flow_network(attrs, adj_result.edges, lambda_param=0.5, mu=0.001)
        flow = g.maxflow()

        partition = get_partition(g, adj_result.num_nodes)
        selected_pop = attrs.population[partition].sum()
        total_pop = attrs.population.sum()

        print("\nDC test results:")
        print(f"  Tracts: {adj_result.num_nodes}")
        print(f"  Edges: {adj_result.num_edges}")
        print(f"  Rho: {attrs.rho:.1f} m ({attrs.rho/1000:.2f} km)")
        print(
            f"  Selected: {partition.sum()} tracts ({100*partition.sum()/len(partition):.1f}%)"
        )
        print(
            f"  Population: {selected_pop:,} / {total_pop:,} ({100*selected_pop/total_pop:.1f}%)"
        )
        print(f"  Max flow: {flow:.2f}")
