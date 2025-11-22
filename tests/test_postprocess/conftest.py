"""Pytest fixtures for postprocess tests."""

import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import box


@pytest.fixture
def grid_4x4_gdf() -> gpd.GeoDataFrame:
    """Create a 4x4 grid for testing dissolve with various partition patterns.

    Areas vary to allow gradual selection when area cost is normalized by rho².
    Center cells are smaller (denser), corner cells are larger (sparser).
    """
    geometries = []
    populations = []
    areas = []

    base_cell_size = 1000  # meters
    for row in range(4):
        for col in range(4):
            x0 = col * base_cell_size
            y0 = row * base_cell_size
            geometries.append(box(x0, y0, x0 + base_cell_size, y0 + base_cell_size))
            populations.append(1000 * (1 + row + col))
            # Vary area: center cells are smaller (denser)
            dist_from_center = abs(row - 1.5) + abs(col - 1.5)
            size_factor = 1.0 + dist_from_center / 4  # 1.0 to ~1.75
            areas.append((base_cell_size * size_factor) ** 2)

    gdf = gpd.GeoDataFrame(
        {"population": populations, "area_sqm": areas, "geometry": geometries},
        crs="EPSG:5070",
    )
    return gdf


@pytest.fixture
def checkerboard_partition() -> np.ndarray:
    """Checkerboard pattern for 4x4 grid (8 selected, 8 not)."""
    # Creates disconnected regions
    pattern = np.zeros(16, dtype=bool)
    for i in range(16):
        row, col = divmod(i, 4)
        pattern[i] = (row + col) % 2 == 0
    return pattern


@pytest.fixture
def contiguous_partition() -> np.ndarray:
    """Select bottom-left 2x2 quadrant (4 contiguous cells)."""
    pattern = np.zeros(16, dtype=bool)
    pattern[[0, 1, 4, 5]] = True  # Bottom-left 2x2
    return pattern


@pytest.fixture
def single_cell_partition() -> np.ndarray:
    """Select only one cell."""
    pattern = np.zeros(16, dtype=bool)
    pattern[0] = True
    return pattern


@pytest.fixture
def all_selected_partition() -> np.ndarray:
    """Select all cells."""
    return np.ones(16, dtype=bool)


@pytest.fixture
def none_selected_partition() -> np.ndarray:
    """Select no cells."""
    return np.zeros(16, dtype=bool)


@pytest.fixture
def grid_with_island_gdf() -> gpd.GeoDataFrame:
    """Create a 3x3 grid plus one isolated square (island)."""
    geometries = []
    populations = []

    cell_size = 1000  # meters
    # 3x3 grid
    for row in range(3):
        for col in range(3):
            x0 = col * cell_size
            y0 = row * cell_size
            geometries.append(box(x0, y0, x0 + cell_size, y0 + cell_size))
            populations.append(1000 * (1 + row + col))

    # Add isolated island far away
    geometries.append(box(10000, 10000, 11000, 11000))
    populations.append(500)

    gdf = gpd.GeoDataFrame(
        {"population": populations, "geometry": geometries},
        crs="EPSG:5070",
    )
    gdf["area_sqm"] = gdf.geometry.area
    return gdf
