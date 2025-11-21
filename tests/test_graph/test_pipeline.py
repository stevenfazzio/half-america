"""Tests for graph data pipeline."""

import pytest

from half_america.graph.pipeline import get_graph_summary, load_graph_data


class TestLoadGraphData:
    def test_builds_graph_data(self, grid_3x3_gdf):
        """Test that graph data is built from GeoDataFrame."""
        graph_data = load_graph_data(grid_3x3_gdf, use_cache=False, verbose=False)

        assert graph_data.num_nodes == 9
        assert graph_data.num_edges == 20
        assert len(graph_data.edges) == 20
        assert graph_data.attributes.rho > 0

    def test_graph_data_has_correct_attributes(self, grid_3x3_gdf):
        """Test that graph data attributes are correct."""
        graph_data = load_graph_data(grid_3x3_gdf, use_cache=False, verbose=False)

        attrs = graph_data.attributes
        assert len(attrs.population) == 9
        assert len(attrs.area) == 9
        assert attrs.rho == pytest.approx(1000.0, rel=0.01)
        # Each edge has both directions stored
        assert len(attrs.edge_lengths) == 40  # 20 edges * 2 directions


class TestGetGraphSummary:
    def test_returns_summary_dict(self, grid_3x3_gdf):
        """Test that summary statistics are computed."""
        graph_data = load_graph_data(grid_3x3_gdf, use_cache=False, verbose=False)
        summary = get_graph_summary(graph_data)

        assert summary["num_nodes"] == 9
        assert summary["num_edges"] == 20
        assert summary["total_population"] > 0
        assert summary["rho_meters"] == pytest.approx(1000.0, rel=0.01)
        assert summary["rho_km"] == pytest.approx(1.0, rel=0.01)
        assert summary["mean_neighbors"] == pytest.approx(20 * 2 / 9, rel=0.01)
