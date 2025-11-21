"""Pytest fixtures for data pipeline tests."""

from pathlib import Path

import geopandas as gpd
import pytest
from shapely.geometry import Polygon, box

# Use realistic US coordinates (around DC area) for EPSG:4326 -> EPSG:5070 reprojection
# DC is approximately at (-77.0, 38.9)
DC_LON, DC_LAT = -77.0, 38.9


@pytest.fixture
def sample_polygon() -> Polygon:
    """Create a simple valid polygon in US coordinates."""
    return box(DC_LON, DC_LAT, DC_LON + 0.01, DC_LAT + 0.01)


@pytest.fixture
def invalid_polygon() -> Polygon:
    """Create a self-intersecting (bowtie) polygon in US coordinates."""
    # Bowtie shape - self-intersecting
    return Polygon(
        [
            (DC_LON, DC_LAT),
            (DC_LON + 0.01, DC_LAT + 0.01),
            (DC_LON + 0.01, DC_LAT),
            (DC_LON, DC_LAT + 0.01),
            (DC_LON, DC_LAT),
        ]
    )


@pytest.fixture
def sample_gdf(sample_polygon) -> gpd.GeoDataFrame:
    """Create a simple GeoDataFrame with valid geometries in US coordinates."""
    return gpd.GeoDataFrame(
        {
            "GEOID": ["001", "002", "003"],
            "NAME": ["Tract 1", "Tract 2", "Tract 3"],
            "geometry": [
                box(DC_LON, DC_LAT, DC_LON + 0.01, DC_LAT + 0.01),
                box(DC_LON + 0.01, DC_LAT, DC_LON + 0.02, DC_LAT + 0.01),
                box(DC_LON, DC_LAT + 0.01, DC_LON + 0.01, DC_LAT + 0.02),
            ],
        },
        crs="EPSG:4326",
    )


@pytest.fixture
def gdf_with_invalid(invalid_polygon) -> gpd.GeoDataFrame:
    """Create a GeoDataFrame with one invalid geometry."""
    return gpd.GeoDataFrame(
        {
            "GEOID": ["001", "002"],
            "NAME": ["Valid", "Invalid"],
            "geometry": [
                box(DC_LON, DC_LAT, DC_LON + 0.01, DC_LAT + 0.01),
                invalid_polygon,
            ],
        },
        crs="EPSG:4326",
    )


@pytest.fixture
def gdf_with_null() -> gpd.GeoDataFrame:
    """Create a GeoDataFrame with null geometries."""
    return gpd.GeoDataFrame(
        {
            "GEOID": ["001", "002", "003"],
            "NAME": ["Valid", "Null", "Empty"],
            "geometry": [
                box(DC_LON, DC_LAT, DC_LON + 0.01, DC_LAT + 0.01),
                None,
                Polygon(),
            ],
        },
        crs="EPSG:4326",
    )


@pytest.fixture
def temp_cache_dir(tmp_path) -> Path:
    """Create a temporary cache directory."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir
