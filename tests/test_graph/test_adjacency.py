"""Tests for adjacency graph construction."""

import pytest
from half_america.graph.adjacency import build_adjacency


class TestBuildAdjacency:
    def test_builds_adjacency_for_grid(self, grid_3x3_gdf):
        """Test adjacency construction for a 3x3 grid."""
        result = build_adjacency(grid_3x3_gdf, verbose=False)

        assert result.num_nodes == 9
        # Queen contiguity: 3x3 grid has 20 unique edges
        assert result.num_edges == 20
        assert result.num_islands_attached == 0

    def test_handles_islands(self, grid_with_island_gdf):
        """Test that islands are attached to nearest neighbors."""
        result = build_adjacency(grid_with_island_gdf, verbose=False)

        assert result.num_nodes == 10
        assert result.num_islands_attached == 1
        # Island should now have at least one neighbor
        assert result.weights.islands == []

    def test_edges_are_unique(self, grid_3x3_gdf):
        """Test that edge list contains only unique pairs (i < j)."""
        result = build_adjacency(grid_3x3_gdf, verbose=False)

        for i, j in result.edges:
            assert i < j, f"Edge ({i}, {j}) should have i < j"

        # No duplicates
        assert len(result.edges) == len(set(result.edges))

    def test_center_has_most_neighbors(self, grid_3x3_gdf):
        """Test that center cell has 8 neighbors (Queen contiguity)."""
        result = build_adjacency(grid_3x3_gdf, verbose=False)

        # Center is index 4 in row-major order
        center_neighbors = result.weights.neighbors[4]
        assert len(center_neighbors) == 8
