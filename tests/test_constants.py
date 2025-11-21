"""Tests for constants module."""

from half_america.data.constants import (
    CONTIGUOUS_US_FIPS,
    FIPS_TO_STATE,
    QUANTIZATION_GRID_SIZE,
    TARGET_CRS,
)


class TestContiguousUSFips:
    def test_count(self):
        """Test that we have 49 FIPS codes (48 states + DC)."""
        assert len(CONTIGUOUS_US_FIPS) == 49

    def test_excludes_alaska(self):
        """Test that Alaska (02) is excluded."""
        assert "02" not in CONTIGUOUS_US_FIPS

    def test_excludes_hawaii(self):
        """Test that Hawaii (15) is excluded."""
        assert "15" not in CONTIGUOUS_US_FIPS

    def test_includes_dc(self):
        """Test that DC (11) is included."""
        assert "11" in CONTIGUOUS_US_FIPS

    def test_all_two_digit_strings(self):
        """Test that all FIPS codes are two-digit strings."""
        for fips in CONTIGUOUS_US_FIPS:
            assert isinstance(fips, str)
            assert len(fips) == 2
            assert fips.isdigit()


class TestFipsToState:
    def test_all_fips_have_names(self):
        """Test that all FIPS codes have state names."""
        for fips in CONTIGUOUS_US_FIPS:
            assert fips in FIPS_TO_STATE
            assert isinstance(FIPS_TO_STATE[fips], str)
            assert len(FIPS_TO_STATE[fips]) > 0

    def test_dc_name(self):
        """Test DC name is correct."""
        assert FIPS_TO_STATE["11"] == "District of Columbia"


class TestConfig:
    def test_target_crs(self):
        """Test target CRS is Albers Equal Area."""
        assert TARGET_CRS == "EPSG:5070"

    def test_quantization_grid_size(self):
        """Test quantization grid size is 1cm."""
        assert QUANTIZATION_GRID_SIZE == 0.01
