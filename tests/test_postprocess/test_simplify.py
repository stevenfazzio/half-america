"""Tests for simplify module."""

import pytest
from shapely import MultiPolygon, Polygon
from shapely.geometry import box

from half_america.postprocess.dissolve import DissolveResult
from half_america.postprocess.simplify import (
    DEFAULT_TOLERANCE,
    SimplifyResult,
    simplify_all_lambdas,
    simplify_geometry,
)


class TestSimplifyGeometry:
    """Tests for simplify_geometry function."""

    def test_returns_simplify_result(self, complex_polygon):
        """Should return a SimplifyResult with all fields."""
        result = simplify_geometry(complex_polygon)

        assert isinstance(result, SimplifyResult)
        assert isinstance(result.geometry, (Polygon, MultiPolygon))
        assert isinstance(result.original_vertex_count, int)
        assert isinstance(result.simplified_vertex_count, int)
        assert isinstance(result.reduction_percent, float)

    def test_reduces_vertex_count(self, complex_polygon):
        """Simplification should reduce vertex count."""
        result = simplify_geometry(complex_polygon, tolerance=100.0)

        assert result.simplified_vertex_count < result.original_vertex_count
        assert result.reduction_percent > 0

    def test_preserves_validity(self, complex_polygon):
        """Output geometry should always be valid."""
        result = simplify_geometry(complex_polygon)
        assert result.geometry.is_valid

    def test_simple_geometry_minimal_change(self, simple_square):
        """Simple geometry should have minimal simplification."""
        result = simplify_geometry(simple_square, tolerance=10.0)

        # Square has 5 coordinates (4 corners + closing point)
        assert result.original_vertex_count == 5
        # Should remain mostly unchanged (can't simplify a square much)
        assert result.simplified_vertex_count >= 4

    def test_multipolygon_input(self, disconnected_multipolygon):
        """Should handle MultiPolygon input correctly."""
        result = simplify_geometry(disconnected_multipolygon)

        assert isinstance(result.geometry, MultiPolygon)
        # Both parts should be preserved
        assert len(result.geometry.geoms) == 2

    def test_custom_tolerance(self, complex_polygon):
        """Higher tolerance should result in more reduction."""
        result_low = simplify_geometry(complex_polygon, tolerance=50.0)
        result_high = simplify_geometry(complex_polygon, tolerance=500.0)

        assert result_high.simplified_vertex_count <= result_low.simplified_vertex_count
        assert result_high.reduction_percent >= result_low.reduction_percent

    def test_default_tolerance(self):
        """Default tolerance should be 500m."""
        assert DEFAULT_TOLERANCE == 500.0

    def test_preserve_topology_true(self, complex_polygon):
        """preserve_topology=True should prevent self-intersections."""
        result = simplify_geometry(
            complex_polygon, tolerance=1000.0, preserve_topology=True
        )
        assert result.geometry.is_valid
        assert not result.geometry.is_empty

    def test_empty_geometry_handling(self):
        """Empty geometry should return zero reduction."""
        empty = Polygon()
        result = simplify_geometry(empty)

        assert result.original_vertex_count == 0
        assert result.simplified_vertex_count == 0
        assert result.reduction_percent == 0.0


class TestSimplifyAllLambdas:
    """Tests for simplify_all_lambdas batch function."""

    def test_processes_all_lambda_values(self, sample_dissolve_results):
        """Should process all lambda values from dissolve results."""
        results = simplify_all_lambdas(sample_dissolve_results, verbose=False)

        assert len(results) == len(sample_dissolve_results)
        for lambda_val in sample_dissolve_results:
            assert lambda_val in results
            assert isinstance(results[lambda_val], SimplifyResult)

    def test_all_results_valid(self, sample_dissolve_results):
        """All simplified geometries should be valid."""
        results = simplify_all_lambdas(sample_dissolve_results, verbose=False)

        for result in results.values():
            assert result.geometry.is_valid

    def test_custom_tolerance(self, sample_dissolve_results):
        """Should apply custom tolerance to all geometries."""
        results_low = simplify_all_lambdas(
            sample_dissolve_results, tolerance=50.0, verbose=False
        )
        results_high = simplify_all_lambdas(
            sample_dissolve_results, tolerance=500.0, verbose=False
        )

        for lambda_val in sample_dissolve_results:
            assert (
                results_high[lambda_val].simplified_vertex_count
                <= results_low[lambda_val].simplified_vertex_count
            )


# Fixtures specific to simplify tests


@pytest.fixture
def simple_square() -> Polygon:
    """Create a simple square polygon."""
    return box(0, 0, 1000, 1000)


@pytest.fixture
def complex_polygon() -> Polygon:
    """Create a polygon with many vertices for simplification testing.

    Creates a jagged polygon with 40+ vertices that can be meaningfully simplified.
    """
    coords = [(0, 0)]
    # Create jagged edge along top
    for i in range(20):
        x = i * 100
        y = 1000 + (50 if i % 2 == 0 else 0)  # Zigzag
        coords.append((x, y))
    coords.append((2000, 1000))
    # Create jagged edge along right
    for i in range(10):
        x = 2000 + (50 if i % 2 == 0 else 0)
        y = 1000 - i * 100
        coords.append((x, y))
    coords.append((2000, 0))
    coords.append((0, 0))  # Close

    return Polygon(coords)


@pytest.fixture
def disconnected_multipolygon() -> MultiPolygon:
    """Create two disconnected squares."""
    square1 = box(0, 0, 1000, 1000)
    square2 = box(5000, 5000, 6000, 6000)  # Far away
    return MultiPolygon([square1, square2])


@pytest.fixture
def sample_dissolve_results() -> dict[float, DissolveResult]:
    """Create sample dissolve results for testing simplify_all_lambdas."""
    # Create a simple complex geometry
    coords = [(0, 0)]
    for i in range(20):
        coords.append((i * 100, 1000 + (50 if i % 2 == 0 else 0)))
    coords.append((2000, 1000))
    coords.append((2000, 0))
    coords.append((0, 0))
    geom = Polygon(coords)

    return {
        0.0: DissolveResult(
            geometry=geom,
            num_parts=1,
            total_area_sqm=geom.area,
            num_tracts=10,
        ),
        0.5: DissolveResult(
            geometry=geom,
            num_parts=1,
            total_area_sqm=geom.area,
            num_tracts=10,
        ),
        0.9: DissolveResult(
            geometry=geom,
            num_parts=1,
            total_area_sqm=geom.area,
            num_tracts=10,
        ),
    }
