"""Tests for dissolve module."""

import numpy as np
import pytest

from half_america.postprocess.dissolve import DissolveResult, dissolve_partition


class TestDissolvePartition:
    """Tests for dissolve_partition function."""

    def test_contiguous_returns_polygon(self, grid_4x4_gdf, contiguous_partition):
        """Contiguous selection should produce a single Polygon."""
        result = dissolve_partition(grid_4x4_gdf, contiguous_partition)

        assert isinstance(result, DissolveResult)
        assert result.geometry.geom_type == "Polygon"
        assert result.num_parts == 1
        assert result.num_tracts == 4

    def test_checkerboard_returns_multipolygon(
        self, grid_4x4_gdf, checkerboard_partition
    ):
        """Disconnected selection should produce MultiPolygon."""
        result = dissolve_partition(grid_4x4_gdf, checkerboard_partition)

        assert result.geometry.geom_type == "MultiPolygon"
        assert result.num_parts == 8  # Each cell is isolated
        assert result.num_tracts == 8

    def test_single_cell_returns_polygon(self, grid_4x4_gdf, single_cell_partition):
        """Single cell selection returns that cell's geometry."""
        result = dissolve_partition(grid_4x4_gdf, single_cell_partition)

        assert result.geometry.geom_type == "Polygon"
        assert result.num_parts == 1
        assert result.num_tracts == 1
        # Area should be one cell (1000m x 1000m = 1,000,000 sqm)
        assert result.total_area_sqm == pytest.approx(1_000_000, rel=0.01)

    def test_all_selected_merges_all(self, grid_4x4_gdf, all_selected_partition):
        """Selecting all cells should produce one merged geometry."""
        result = dissolve_partition(grid_4x4_gdf, all_selected_partition)

        assert result.num_parts == 1
        assert result.num_tracts == 16
        # Total area should be 16 cells
        assert result.total_area_sqm == pytest.approx(16_000_000, rel=0.01)

    def test_geometry_is_valid(self, grid_4x4_gdf, checkerboard_partition):
        """Output geometry should always be valid."""
        result = dissolve_partition(grid_4x4_gdf, checkerboard_partition)
        assert result.geometry.is_valid

    def test_area_equals_sum_of_selected(self, grid_4x4_gdf, contiguous_partition):
        """Total area should equal sum of selected tract areas."""
        selected_area = grid_4x4_gdf[contiguous_partition]["area_sqm"].sum()
        result = dissolve_partition(grid_4x4_gdf, contiguous_partition)
        assert result.total_area_sqm == pytest.approx(selected_area, rel=0.001)


class TestDissolvePartitionErrors:
    """Tests for error handling in dissolve_partition."""

    def test_empty_partition_raises(self, grid_4x4_gdf, none_selected_partition):
        """Empty partition should raise ValueError."""
        with pytest.raises(ValueError, match="No tracts selected"):
            dissolve_partition(grid_4x4_gdf, none_selected_partition)

    def test_mismatched_length_raises(self, grid_4x4_gdf):
        """Partition length mismatch should raise ValueError."""
        wrong_size = np.ones(10, dtype=bool)
        with pytest.raises(ValueError, match="doesn't match"):
            dissolve_partition(grid_4x4_gdf, wrong_size)


class TestDissolveWithIsland:
    """Tests using grid_with_island_gdf fixture from test_graph."""

    def test_island_preserved_when_selected(self, grid_with_island_gdf):
        """Island should be preserved as separate part when selected."""
        # Select main grid center (index 4) and island (index 9)
        partition = np.zeros(10, dtype=bool)
        partition[4] = True  # Center of 3x3 grid
        partition[9] = True  # Island

        result = dissolve_partition(grid_with_island_gdf, partition)

        # Should have 2 disconnected parts
        assert result.num_parts == 2
        assert result.num_tracts == 2


class TestDissolveAllLambdas:
    """Tests for dissolve_all_lambdas batch function."""

    def test_processes_all_lambda_values(self, grid_4x4_gdf):
        """Should process all lambda values from sweep result."""
        from half_america.graph.pipeline import load_graph_data
        from half_america.optimization import sweep_lambda
        from half_america.postprocess.dissolve import dissolve_all_lambdas

        # Build graph from test data (not cache) and run mini sweep
        graph_data = load_graph_data(grid_4x4_gdf, use_cache=False, verbose=False)
        sweep_result = sweep_lambda(
            graph_data,
            lambda_values=[0.0, 0.5],
            tolerance=0.15,  # Relaxed tolerance for small discrete graph
            verbose=False,
        )

        results = dissolve_all_lambdas(grid_4x4_gdf, sweep_result, verbose=False)

        assert len(results) == 2
        assert 0.0 in results
        assert 0.5 in results

        for lambda_val, result in results.items():
            assert isinstance(result, DissolveResult)
            assert result.geometry.is_valid
            assert result.num_tracts > 0
