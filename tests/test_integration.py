"""Integration tests for data pipeline.

These tests make real network requests and should be run sparingly.
Mark with @pytest.mark.integration and skip by default.
"""

import pytest

# Skip integration tests by default (run with: pytest -m integration)
pytestmark = pytest.mark.integration


@pytest.fixture
def skip_without_api_key():
    """Skip test if Census API key is not configured."""
    from half_america.config import CENSUS_API_KEY

    if not CENSUS_API_KEY:
        pytest.skip("CENSUS_API_KEY not configured")


class TestTigerDownload:
    def test_download_dc_tracts(self):
        """Test downloading DC tracts (smallest state)."""
        from half_america.data import download_state_tracts

        gdf = download_state_tracts("11")

        assert len(gdf) > 0
        assert "GEOID" in gdf.columns
        assert gdf.crs is not None

    def test_dc_tract_count_reasonable(self):
        """Test that DC has reasonable number of tracts."""
        from half_america.data import download_state_tracts

        gdf = download_state_tracts("11")

        # DC should have ~200 tracts
        assert 150 < len(gdf) < 300


class TestCensusFetch:
    def test_fetch_dc_population(self, skip_without_api_key):
        """Test fetching DC population data."""
        from half_america.data import fetch_state_population

        df = fetch_state_population("11")

        assert len(df) > 0
        assert "GEOID" in df.columns
        assert "population" in df.columns

    def test_dc_population_reasonable(self, skip_without_api_key):
        """Test that DC population is reasonable."""
        from half_america.data import fetch_state_population

        df = fetch_state_population("11")
        total_pop = df["population"].sum()

        # DC population should be ~700k
        assert 600_000 < total_pop < 800_000


class TestFullPipeline:
    def test_load_dc_tracts(self, skip_without_api_key):
        """Test loading DC tracts with full pipeline."""
        from half_america.data import load_state_tracts, get_pipeline_summary

        gdf = load_state_tracts("11")
        summary = get_pipeline_summary(gdf)

        assert summary["tract_count"] > 0
        assert summary["total_population"] > 0
        assert summary["crs"] == "EPSG:5070"
