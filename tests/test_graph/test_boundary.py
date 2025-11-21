"""Tests for boundary length calculations."""

import pytest

from half_america.graph.boundary import (
    compute_boundary_lengths,
    compute_graph_attributes,
    compute_rho,
)


class TestComputeRho:
    def test_computes_median_sqrt_area(self, grid_3x3_gdf):
        """Test rho computation for uniform grid."""
        rho = compute_rho(grid_3x3_gdf)

        # Each cell is 1000m x 1000m = 1,000,000 sqm
        # sqrt(1,000,000) = 1000m
        # Median of all equal values = 1000m
        assert rho == pytest.approx(1000.0, rel=0.01)


class TestComputeBoundaryLengths:
    def test_computes_shared_boundary(self, grid_3x3_gdf):
        """Test boundary length computation."""
        # Build actual edges from adjacency
        from half_america.graph.adjacency import build_adjacency

        result = build_adjacency(grid_3x3_gdf, verbose=False)

        edge_lengths = compute_boundary_lengths(
            grid_3x3_gdf, result.edges, verbose=False
        )

        # Adjacent squares share 1000m boundary
        # Diagonal neighbors share only a point (0m boundary)

        # Check a horizontal adjacency (0, 1)
        assert edge_lengths[(0, 1)] == pytest.approx(1000.0, rel=0.01)

        # Check a diagonal adjacency (0, 4) - should be ~0
        assert edge_lengths[(0, 4)] < 1.0  # Nearly zero

    def test_symmetric_edge_lengths(self, grid_3x3_gdf):
        """Test that edge lengths are symmetric."""
        from half_america.graph.adjacency import build_adjacency

        result = build_adjacency(grid_3x3_gdf, verbose=False)

        edge_lengths = compute_boundary_lengths(
            grid_3x3_gdf, result.edges, verbose=False
        )

        for i, j in result.edges:
            assert edge_lengths[(i, j)] == edge_lengths[(j, i)]


class TestComputeGraphAttributes:
    def test_returns_all_attributes(self, grid_3x3_gdf):
        """Test that all attributes are computed."""
        from half_america.graph.adjacency import build_adjacency

        result = build_adjacency(grid_3x3_gdf, verbose=False)

        attrs = compute_graph_attributes(grid_3x3_gdf, result.edges, verbose=False)

        assert len(attrs.population) == 9
        assert len(attrs.area) == 9
        assert attrs.rho > 0
        assert len(attrs.edge_lengths) > 0
