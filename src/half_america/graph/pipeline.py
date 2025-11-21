"""Graph data pipeline with caching."""

import pickle
from pathlib import Path
from typing import NamedTuple

import geopandas as gpd
import numpy as np

from half_america.config import ACS_YEAR, TIGER_YEAR
from half_america.data.cache import ensure_cache_dirs, get_processed_cache_path
from half_america.graph.adjacency import build_adjacency
from half_america.graph.boundary import GraphAttributes, compute_graph_attributes


class GraphData(NamedTuple):
    """Complete graph data for optimization."""

    edges: list[tuple[int, int]]
    attributes: GraphAttributes
    num_nodes: int
    num_edges: int


def _get_graph_cache_path() -> Path:
    """Get path to cached graph data."""
    return get_processed_cache_path(f"graph_{TIGER_YEAR}_{ACS_YEAR}").with_suffix(
        ".pkl"
    )


def load_graph_data(
    gdf: gpd.GeoDataFrame,
    force_rebuild: bool = False,
    use_cache: bool = True,
    verbose: bool = True,
) -> GraphData:
    """
    Load or build graph data from tract GeoDataFrame.

    Args:
        gdf: GeoDataFrame from load_all_tracts()
        force_rebuild: If True, rebuild even if cached
        use_cache: If True, use cached data if available
        verbose: If True, print progress messages

    Returns:
        GraphData with edges, attributes, and statistics
    """
    ensure_cache_dirs()
    cache_path = _get_graph_cache_path()

    # Return cached data if available
    if use_cache and cache_path.exists() and not force_rebuild:
        if verbose:
            print(f"Loading cached graph data from {cache_path}")
        with open(cache_path, "rb") as f:
            return pickle.load(f)

    if verbose:
        print("Building graph data...")

    # Build adjacency graph
    adj_result = build_adjacency(gdf, verbose=verbose)

    # Compute graph attributes
    attributes = compute_graph_attributes(gdf, adj_result.edges, verbose=verbose)

    graph_data = GraphData(
        edges=adj_result.edges,
        attributes=attributes,
        num_nodes=adj_result.num_nodes,
        num_edges=adj_result.num_edges,
    )

    # Cache result
    with open(cache_path, "wb") as f:
        pickle.dump(graph_data, f)
    if verbose:
        print(f"Cached graph data to {cache_path}")

    return graph_data


def get_graph_summary(graph_data: GraphData) -> dict:
    """
    Get summary statistics for graph data.

    Args:
        graph_data: GraphData from load_graph_data()

    Returns:
        Dictionary with summary statistics
    """
    attrs = graph_data.attributes
    edge_lengths = list(attrs.edge_lengths.values())[::2]  # Dedupe symmetric entries

    return {
        "num_nodes": graph_data.num_nodes,
        "num_edges": graph_data.num_edges,
        "total_population": int(attrs.population.sum()),
        "half_population": int(attrs.population.sum() // 2),
        "total_area_sqkm": float(attrs.area.sum() / 1e6),
        "rho_meters": float(attrs.rho),
        "rho_km": float(attrs.rho / 1000),
        "mean_boundary_length_m": float(np.mean(edge_lengths)),
        "max_boundary_length_m": float(np.max(edge_lengths)),
        "mean_neighbors": graph_data.num_edges * 2 / graph_data.num_nodes,
    }
