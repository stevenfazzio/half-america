"""Pytest fixtures for graph tests."""

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box

# Create a 3x3 grid of adjacent squares for testing
# Each square is 1000m x 1000m in EPSG:5070 coordinates
GRID_ORIGIN_X = 0
GRID_ORIGIN_Y = 0
GRID_SIZE = 1000  # meters


@pytest.fixture
def grid_3x3_gdf() -> gpd.GeoDataFrame:
    """Create a 3x3 grid of adjacent squares for testing adjacency."""
    geometries = []
    geoids = []
    populations = []

    for row in range(3):
        for col in range(3):
            x0 = GRID_ORIGIN_X + col * GRID_SIZE
            y0 = GRID_ORIGIN_Y + row * GRID_SIZE
            x1 = x0 + GRID_SIZE
            y1 = y0 + GRID_SIZE
            geometries.append(box(x0, y0, x1, y1))
            geoids.append(f"{row}{col}")
            # Population varies by position (center has most)
            populations.append(1000 * (1 + row) * (1 + col))

    gdf = gpd.GeoDataFrame(
        {
            "GEOID": geoids,
            "population": populations,
            "geometry": geometries,
        },
        crs="EPSG:5070",
    )
    gdf["area_sqm"] = gdf.geometry.area
    return gdf


@pytest.fixture
def grid_with_island_gdf(grid_3x3_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Create a 3x3 grid plus one isolated square (island)."""
    island = gpd.GeoDataFrame(
        {
            "GEOID": ["island"],
            "population": [500],
            "geometry": [box(10000, 10000, 11000, 11000)],  # Far away
        },
        crs="EPSG:5070",
    )
    island["area_sqm"] = island.geometry.area

    return gpd.GeoDataFrame(
        pd.concat([grid_3x3_gdf, island], ignore_index=True),
        crs="EPSG:5070",
    )


@pytest.fixture
def simple_edges() -> list[tuple[int, int]]:
    """Simple edge list for a 3x3 grid (Queen contiguity)."""
    # In a 3x3 grid with Queen contiguity:
    # 0-1-2
    # 3-4-5
    # 6-7-8
    # Center (4) has 8 neighbors, corners have 3, edges have 5
    return [
        (0, 1),
        (0, 3),
        (0, 4),
        (1, 2),
        (1, 3),
        (1, 4),
        (1, 5),
        (2, 4),
        (2, 5),
        (3, 4),
        (3, 6),
        (3, 7),
        (4, 5),
        (4, 6),
        (4, 7),
        (4, 8),
        (5, 7),
        (5, 8),
        (6, 7),
        (7, 8),
    ]
