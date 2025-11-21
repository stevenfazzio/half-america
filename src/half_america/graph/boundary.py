"""Shared boundary length calculations."""

from typing import NamedTuple

import numpy as np
import geopandas as gpd
from shapely import intersection, length


class GraphAttributes(NamedTuple):
    """Computed graph attributes for optimization."""

    population: np.ndarray  # p_i for each tract (int)
    area: np.ndarray  # a_i for each tract in sq meters (float)
    rho: float  # Characteristic length scale in meters
    edge_lengths: dict[tuple[int, int], float]  # l_ij in meters


def compute_rho(gdf: gpd.GeoDataFrame) -> float:
    """
    Compute characteristic length scale for normalization.

    ρ = median(√a_i) where a_i is tract area in square meters.

    Args:
        gdf: GeoDataFrame with area_sqm column

    Returns:
        Characteristic length scale in meters
    """
    sqrt_areas = np.sqrt(gdf["area_sqm"].values)
    return float(np.median(sqrt_areas))


def compute_boundary_lengths(
    gdf: gpd.GeoDataFrame,
    edges: list[tuple[int, int]],
    verbose: bool = True,
) -> dict[tuple[int, int], float]:
    """
    Compute shared boundary lengths for all adjacent tract pairs.

    Uses vectorized Shapely operations for performance.

    Args:
        gdf: GeoDataFrame with tract geometries
        edges: List of (i, j) neighbor pairs from adjacency graph
        verbose: If True, print progress messages

    Returns:
        Dictionary mapping (i, j) -> shared boundary length in meters
    """
    if verbose:
        print(f"Computing boundary lengths for {len(edges):,} edges...")

    # Extract geometry boundaries (LineStrings)
    boundaries = gdf.geometry.boundary.values

    # Prepare index arrays for vectorized operation
    i_indices = np.array([e[0] for e in edges])
    j_indices = np.array([e[1] for e in edges])

    # Vectorized intersection and length calculation
    shared_boundaries = intersection(boundaries[i_indices], boundaries[j_indices])
    lengths = length(shared_boundaries)

    # Build dictionary with both directions for easy lookup
    edge_lengths: dict[tuple[int, int], float] = {}
    for idx, (i, j) in enumerate(edges):
        l_ij = float(lengths[idx])
        edge_lengths[(i, j)] = l_ij
        edge_lengths[(j, i)] = l_ij  # Symmetric

    if verbose:
        nonzero_count = sum(1 for edge_len in lengths if edge_len > 0)
        print(
            f"  Non-zero boundary lengths: {nonzero_count:,} ({100*nonzero_count/len(edges):.1f}%)"
        )
        print(f"  Mean boundary length: {np.mean(lengths):.1f} m")
        print(f"  Max boundary length: {np.max(lengths):.1f} m")

    return edge_lengths


def compute_graph_attributes(
    gdf: gpd.GeoDataFrame,
    edges: list[tuple[int, int]],
    verbose: bool = True,
) -> GraphAttributes:
    """
    Compute all graph attributes needed for optimization.

    Args:
        gdf: GeoDataFrame with population, area_sqm, and geometry columns
        edges: List of (i, j) neighbor pairs from adjacency graph
        verbose: If True, print progress messages

    Returns:
        GraphAttributes with population, area, rho, and edge_lengths
    """
    population = gdf["population"].values.astype(np.int64)
    area = gdf["area_sqm"].values.astype(np.float64)
    rho = compute_rho(gdf)
    edge_lengths = compute_boundary_lengths(gdf, edges, verbose=verbose)

    if verbose:
        print(f"  Characteristic length scale (ρ): {rho:.1f} m ({rho/1000:.2f} km)")
        print(f"  Total population: {population.sum():,}")
        print(f"  Total area: {area.sum()/1e6:.0f} km²")

    return GraphAttributes(
        population=population,
        area=area,
        rho=rho,
        edge_lengths=edge_lengths,
    )
