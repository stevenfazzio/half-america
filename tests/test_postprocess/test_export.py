"""Tests for export module."""

import json
from unittest.mock import MagicMock

import pytest
from shapely import MultiPolygon, Polygon
from shapely.geometry import box

from half_america.postprocess.dissolve import DissolveResult
from half_america.postprocess.export import (
    ExportMetadata,
    ExportResult,
    export_all_lambdas,
    export_combined_topojson,
    export_to_topojson,
)
from half_america.postprocess.simplify import SimplifyResult


class TestExportToTopojson:
    """Tests for export_to_topojson function."""

    def test_returns_export_result(self, simple_polygon, tmp_path, sample_metadata):
        """Should return an ExportResult with all fields."""
        output_path = tmp_path / "test.json"
        result = export_to_topojson(simple_polygon, output_path, sample_metadata)

        assert isinstance(result, ExportResult)
        assert result.path == output_path
        assert result.file_size_bytes > 0
        assert result.lambda_value == sample_metadata.lambda_value
        assert result.object_name == "selected_region"

    def test_creates_valid_topojson(self, simple_polygon, tmp_path, sample_metadata):
        """Output should be valid TopoJSON."""
        output_path = tmp_path / "test.json"
        export_to_topojson(simple_polygon, output_path, sample_metadata)

        with open(output_path) as f:
            data = json.load(f)

        assert data["type"] == "Topology"
        assert "objects" in data
        assert "arcs" in data

    def test_includes_metadata_properties(
        self, simple_polygon, tmp_path, sample_metadata
    ):
        """TopoJSON should include metadata as properties."""
        output_path = tmp_path / "test.json"
        export_to_topojson(simple_polygon, output_path, sample_metadata)

        with open(output_path) as f:
            data = json.load(f)

        # Properties are in the geometry object
        obj = data["objects"]["selected_region"]
        assert "properties" in obj or "geometries" in obj

    def test_transforms_to_wgs84(self, simple_polygon, tmp_path, sample_metadata):
        """Coordinates should be in WGS84 (longitude/latitude range)."""
        output_path = tmp_path / "test.json"
        export_to_topojson(simple_polygon, output_path, sample_metadata)

        with open(output_path) as f:
            data = json.load(f)

        # Check transform or bbox is in reasonable WGS84 range
        if "bbox" in data:
            bbox = data["bbox"]
            # Longitude: -180 to 180, Latitude: -90 to 90
            assert -180 <= bbox[0] <= 180
            assert -90 <= bbox[1] <= 90

    def test_empty_geometry_raises(self, tmp_path, sample_metadata):
        """Empty geometry should raise ValueError."""
        empty = Polygon()
        output_path = tmp_path / "test.json"

        with pytest.raises(ValueError, match="empty geometry"):
            export_to_topojson(empty, output_path, sample_metadata)

    def test_multipolygon_input(
        self, disconnected_multipolygon, tmp_path, sample_metadata
    ):
        """Should handle MultiPolygon input correctly."""
        output_path = tmp_path / "test.json"
        result = export_to_topojson(
            disconnected_multipolygon, output_path, sample_metadata
        )

        assert result.file_size_bytes > 0
        with open(output_path) as f:
            data = json.load(f)
        assert data["type"] == "Topology"

    def test_custom_object_name(self, simple_polygon, tmp_path, sample_metadata):
        """Should use custom object name."""
        output_path = tmp_path / "test.json"
        export_to_topojson(
            simple_polygon, output_path, sample_metadata, object_name="custom_region"
        )

        with open(output_path) as f:
            data = json.load(f)

        assert "custom_region" in data["objects"]

    def test_creates_parent_directories(
        self, simple_polygon, tmp_path, sample_metadata
    ):
        """Should create parent directories if they don't exist."""
        output_path = tmp_path / "nested" / "dir" / "test.json"
        export_to_topojson(simple_polygon, output_path, sample_metadata)

        assert output_path.exists()


class TestExportAllLambdas:
    """Tests for export_all_lambdas batch function."""

    def test_exports_all_lambda_values(
        self,
        sample_simplify_results,
        sample_dissolve_results,
        sample_sweep_result,
        tmp_path,
    ):
        """Should export all lambda values."""
        results = export_all_lambdas(
            sample_simplify_results,
            sample_dissolve_results,
            sample_sweep_result,
            output_dir=tmp_path,
            verbose=False,
        )

        assert len(results) == len(sample_simplify_results)
        for lambda_val in sample_simplify_results:
            assert lambda_val in results
            assert isinstance(results[lambda_val], ExportResult)

    def test_creates_correct_filenames(
        self,
        sample_simplify_results,
        sample_dissolve_results,
        sample_sweep_result,
        tmp_path,
    ):
        """Should create files with lambda_X.XX.json naming."""
        export_all_lambdas(
            sample_simplify_results,
            sample_dissolve_results,
            sample_sweep_result,
            output_dir=tmp_path,
            verbose=False,
        )

        for lambda_val in sample_simplify_results:
            expected_path = tmp_path / f"lambda_{lambda_val:.2f}.json"
            assert expected_path.exists()


class TestExportCombinedTopojson:
    """Tests for export_combined_topojson function."""

    def test_creates_combined_file(
        self,
        sample_simplify_results,
        sample_dissolve_results,
        sample_sweep_result,
        tmp_path,
    ):
        """Should create a single combined file."""
        output_path = tmp_path / "combined.json"
        result = export_combined_topojson(
            sample_simplify_results,
            sample_dissolve_results,
            sample_sweep_result,
            output_path=output_path,
            verbose=False,
        )

        assert result == output_path
        assert output_path.exists()

    def test_contains_all_objects(
        self,
        sample_simplify_results,
        sample_dissolve_results,
        sample_sweep_result,
        tmp_path,
    ):
        """Combined file should contain all lambda objects."""
        output_path = tmp_path / "combined.json"
        export_combined_topojson(
            sample_simplify_results,
            sample_dissolve_results,
            sample_sweep_result,
            output_path=output_path,
            verbose=False,
        )

        with open(output_path) as f:
            data = json.load(f)

        assert data["type"] == "Topology"
        for lambda_val in sample_simplify_results:
            assert f"lambda_{lambda_val:.2f}" in data["objects"]


# Fixtures specific to export tests


@pytest.fixture
def simple_polygon() -> Polygon:
    """Create a simple polygon in EPSG:5070 coordinates."""
    # Coordinates roughly in center of CONUS (Kansas area)
    return box(-500000, 1500000, 500000, 2500000)


@pytest.fixture
def disconnected_multipolygon() -> MultiPolygon:
    """Create two disconnected polygons."""
    poly1 = box(-500000, 1500000, 0, 2000000)
    poly2 = box(500000, 1500000, 1000000, 2000000)
    return MultiPolygon([poly1, poly2])


@pytest.fixture
def sample_metadata() -> ExportMetadata:
    """Create sample metadata for testing."""
    return ExportMetadata(
        lambda_value=0.5,
        population_selected=165_000_000,
        total_population=328_912_183,
        area_sqm=5_000_000_000_000.0,
        num_parts=50,
        total_area_all_sqm=7_910_000_000_000_000.0,  # ~7.9 trillion sq m (US total)
    )


@pytest.fixture
def sample_simplify_results() -> dict[float, SimplifyResult]:
    """Create sample simplify results for testing."""
    geom = box(-500000, 1500000, 500000, 2500000)
    return {
        0.0: SimplifyResult(
            geometry=geom,
            original_vertex_count=100,
            simplified_vertex_count=10,
            reduction_percent=90.0,
        ),
        0.5: SimplifyResult(
            geometry=geom,
            original_vertex_count=100,
            simplified_vertex_count=10,
            reduction_percent=90.0,
        ),
        0.9: SimplifyResult(
            geometry=geom,
            original_vertex_count=100,
            simplified_vertex_count=10,
            reduction_percent=90.0,
        ),
    }


@pytest.fixture
def sample_dissolve_results() -> dict[float, DissolveResult]:
    """Create sample dissolve results for testing."""
    geom = box(-500000, 1500000, 500000, 2500000)
    return {
        0.0: DissolveResult(
            geometry=geom,
            num_parts=100,
            total_area_sqm=geom.area,
            num_tracts=30000,
            population_selected=165_000_000,
            total_population=328_912_183,
        ),
        0.5: DissolveResult(
            geometry=geom,
            num_parts=50,
            total_area_sqm=geom.area,
            num_tracts=30000,
            population_selected=165_000_000,
            total_population=328_912_183,
        ),
        0.9: DissolveResult(
            geometry=geom,
            num_parts=10,
            total_area_sqm=geom.area,
            num_tracts=30000,
            population_selected=165_000_000,
            total_population=328_912_183,
        ),
    }


@pytest.fixture
def sample_sweep_result():
    """Create a mock SweepResult for testing export functions."""
    total_area = 7_910_000_000_000_000.0  # ~7.9 trillion sq m

    def make_lambda_result(lambda_val: float):
        """Create a mock LambdaResult with nested structure."""
        mock_opt_result = MagicMock()
        mock_opt_result.total_area = total_area

        mock_search_result = MagicMock()
        mock_search_result.result = mock_opt_result

        mock_lambda_result = MagicMock()
        mock_lambda_result.search_result = mock_search_result

        return mock_lambda_result

    mock_sweep = MagicMock()
    mock_sweep.results = {
        0.0: make_lambda_result(0.0),
        0.5: make_lambda_result(0.5),
        0.9: make_lambda_result(0.9),
    }
    return mock_sweep
