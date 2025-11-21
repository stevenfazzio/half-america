"""Tests for geometry cleaning functions."""

import pytest

from half_america.data.cleaning import (
    clean_census_tracts,
    fix_invalid_geometries,
    quantize_coordinates,
    remove_null_geometries,
    reproject_to_equal_area,
)
from half_america.data.constants import TARGET_CRS


class TestRemoveNullGeometries:
    def test_removes_null_geometries(self, gdf_with_null):
        """Test that null geometries are removed."""
        result, count = remove_null_geometries(gdf_with_null)

        assert count == 2  # One None, one empty Polygon
        assert len(result) == 1
        assert result.iloc[0]["GEOID"] == "001"

    def test_preserves_valid_geometries(self, sample_gdf):
        """Test that valid geometries are preserved."""
        result, count = remove_null_geometries(sample_gdf)

        assert count == 0
        assert len(result) == len(sample_gdf)


class TestFixInvalidGeometries:
    def test_fixes_invalid_geometries(self, gdf_with_invalid):
        """Test that invalid geometries are fixed."""
        result, count = fix_invalid_geometries(gdf_with_invalid)

        assert count == 1
        assert result.is_valid.all()

    def test_preserves_valid_geometries(self, sample_gdf):
        """Test that valid geometries remain unchanged."""
        result, count = fix_invalid_geometries(sample_gdf)

        assert count == 0
        assert result.is_valid.all()


class TestReprojectToEqualArea:
    def test_reprojects_to_target_crs(self, sample_gdf):
        """Test reprojection to EPSG:5070."""
        result = reproject_to_equal_area(sample_gdf)

        assert str(result.crs) == TARGET_CRS

    def test_no_op_if_already_target_crs(self, sample_gdf):
        """Test that reprojection is skipped if already in target CRS."""
        projected = sample_gdf.to_crs(TARGET_CRS)
        result = reproject_to_equal_area(projected)

        assert str(result.crs) == TARGET_CRS

    def test_raises_on_missing_crs(self, sample_gdf):
        """Test that error is raised if CRS is missing."""
        sample_gdf.crs = None

        with pytest.raises(ValueError, match="no CRS defined"):
            reproject_to_equal_area(sample_gdf)


class TestQuantizeCoordinates:
    def test_quantizes_coordinates(self, sample_gdf):
        """Test coordinate quantization."""
        projected = sample_gdf.to_crs(TARGET_CRS)
        result, count = quantize_coordinates(projected)

        # Should have no invalid geometries after quantization
        assert result.is_valid.all()


class TestCleanCensusTracts:
    def test_full_pipeline(self, sample_gdf):
        """Test complete cleaning pipeline."""
        result, stats = clean_census_tracts(sample_gdf, verbose=False)

        assert len(result) == len(sample_gdf)
        assert str(result.crs) == TARGET_CRS
        assert "area_sqm" in result.columns
        assert result.is_valid.all()

        assert stats.input_count == 3
        assert stats.output_count == 3

    def test_pipeline_removes_nulls(self, gdf_with_null):
        """Test that pipeline removes null geometries."""
        result, stats = clean_census_tracts(gdf_with_null, verbose=False)

        assert len(result) == 1
        assert stats.null_removed == 2

    def test_pipeline_fixes_invalid(self, gdf_with_invalid):
        """Test that pipeline fixes invalid geometries."""
        result, stats = clean_census_tracts(gdf_with_invalid, verbose=False)

        assert result.is_valid.all()
        assert stats.invalid_fixed == 1
