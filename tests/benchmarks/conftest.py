"""Fixtures for performance benchmarks.

These fixtures provide larger test data than unit test fixtures
to produce meaningful performance measurements.
"""

import gc

import pytest
from shapely import box

import geopandas as gpd

from half_america.graph.adjacency import build_adjacency
from half_america.graph.boundary import compute_graph_attributes
from half_america.graph.pipeline import GraphData


def build_graph_data(gdf: gpd.GeoDataFrame) -> GraphData:
    """Build GraphData from GeoDataFrame without caching.

    This is a simplified version of load_graph_data for benchmarks.
    """
    adj_result = build_adjacency(gdf, verbose=False)
    attributes = compute_graph_attributes(gdf, adj_result.edges, verbose=False)
    return GraphData(
        edges=adj_result.edges,
        attributes=attributes,
        num_nodes=adj_result.num_nodes,
        num_edges=adj_result.num_edges,
    )


@pytest.fixture
def benchmark_setup(benchmark):
    """Configure benchmark to disable GC during measurement."""
    benchmark.extra_info["gc_disabled"] = True
    gc.collect()
    gc.disable()
    yield
    gc.enable()


@pytest.fixture(scope="module")
def grid_20x20_gdf() -> gpd.GeoDataFrame:
    """Create a 20x20 grid of adjacent squares for benchmarking.

    This creates 400 tracts with ~1,500 edges (Queen contiguity),
    which is ~0.5% of the real dataset size but sufficient for
    meaningful benchmarks without excessive test time.

    Returns:
        GeoDataFrame with 400 square polygons in EPSG:5070
    """
    rows, cols = 20, 20
    cell_size = 1000  # 1km cells

    geometries = []
    populations = []
    areas = []

    for row in range(rows):
        for col in range(cols):
            x0 = col * cell_size
            y0 = row * cell_size
            geom = box(x0, y0, x0 + cell_size, y0 + cell_size)
            geometries.append(geom)
            # Vary population to create interesting optimization landscape
            populations.append(1000 * (1 + row) * (1 + col))
            areas.append(cell_size * cell_size)

    gdf = gpd.GeoDataFrame(
        {
            "population": populations,
            "area_sqm": areas,
            "geometry": geometries,
        },
        crs="EPSG:5070",
    )
    return gdf


@pytest.fixture(scope="module")
def benchmark_graph_data(grid_20x20_gdf) -> GraphData:
    """Build GraphData from 20x20 grid for benchmarking.

    This fixture is module-scoped to avoid rebuilding the graph
    for each benchmark iteration.
    """
    return build_graph_data(grid_20x20_gdf)


@pytest.fixture(scope="module")
def grid_50x50_gdf() -> gpd.GeoDataFrame:
    """Create a 50x50 grid for larger-scale benchmarks.

    This creates 2,500 tracts with ~9,800 edges, which is ~3.4%
    of the real dataset size. Use for benchmarks where you need
    to measure scaling behavior.

    Returns:
        GeoDataFrame with 2,500 square polygons in EPSG:5070
    """
    rows, cols = 50, 50
    cell_size = 1000

    geometries = []
    populations = []
    areas = []

    for row in range(rows):
        for col in range(cols):
            x0 = col * cell_size
            y0 = row * cell_size
            geom = box(x0, y0, x0 + cell_size, y0 + cell_size)
            geometries.append(geom)
            populations.append(1000 * (1 + row) * (1 + col))
            areas.append(cell_size * cell_size)

    gdf = gpd.GeoDataFrame(
        {
            "population": populations,
            "area_sqm": areas,
            "geometry": geometries,
        },
        crs="EPSG:5070",
    )
    return gdf


@pytest.fixture(scope="module")
def large_graph_data(grid_50x50_gdf) -> GraphData:
    """Build GraphData from 50x50 grid for scaling benchmarks."""
    return build_graph_data(grid_50x50_gdf)
