"""Spatial adjacency graph construction using libpysal."""

from typing import NamedTuple

import geopandas as gpd
from libpysal.weights import Queen, W
from libpysal.weights.distance import KNN


class AdjacencyResult(NamedTuple):
    """Result of adjacency graph construction."""

    weights: W
    edges: list[tuple[int, int]]
    num_nodes: int
    num_edges: int
    num_islands_attached: int


def _attach_islands_manual(w: W, gdf: gpd.GeoDataFrame) -> W:
    """
    Attach island nodes to their nearest neighbors using KNN.

    Args:
        w: Weights object with potential islands
        gdf: GeoDataFrame with geometries for distance calculation

    Returns:
        New weights object with islands attached
    """
    if not w.islands:
        return w

    # Build KNN with k=1 to find nearest neighbor for each geometry
    # Use centroids for distance calculation
    knn = KNN.from_dataframe(gdf, k=1)

    # Copy neighbors dict to modify
    new_neighbors = {k: list(v) for k, v in w.neighbors.items()}

    for island in w.islands:
        # Get the nearest neighbor from KNN
        nearest = knn.neighbors[island][0]

        # Add bidirectional connection
        new_neighbors[island].append(nearest)
        new_neighbors[nearest].append(island)

    # Create new weights object
    return W(new_neighbors)


def build_adjacency(
    gdf: gpd.GeoDataFrame,
    verbose: bool = True,
) -> AdjacencyResult:
    """
    Build Queen contiguity adjacency graph from tract geometries.

    Uses integer indexing (0 to n-1) for PyMaxFlow compatibility.
    Islands (isolated tracts) are attached to their nearest neighbors.

    Args:
        gdf: GeoDataFrame with tract geometries (from load_all_tracts)
        verbose: If True, print progress messages

    Returns:
        AdjacencyResult with weights object, edge list, and statistics
    """
    num_nodes = len(gdf)

    if verbose:
        print(f"Building adjacency graph for {num_nodes:,} tracts...")

    # Build Queen contiguity with integer indices (0 to n-1)
    # use_index=False ensures integer indexing for PyMaxFlow compatibility
    w = Queen.from_dataframe(gdf, use_index=False)

    if verbose:
        print(f"  Initial neighbors: mean={w.mean_neighbors:.1f}, max={w.max_neighbors}")

    # Handle islands (tracts with no neighbors)
    num_islands = len(w.islands)
    if num_islands > 0:
        if verbose:
            print(f"  Attaching {num_islands} island tracts to nearest neighbors...")
        w = _attach_islands_manual(w, gdf)

    # Extract unique edge pairs (i < j to avoid duplicates)
    edges: list[tuple[int, int]] = []
    for i, neighbors in w.neighbors.items():
        for j in neighbors:
            if i < j:
                edges.append((i, j))

    num_edges = len(edges)

    if verbose:
        print(f"  Final graph: {num_nodes:,} nodes, {num_edges:,} edges")
        print(f"  Connected components: {w.n_components}")

    return AdjacencyResult(
        weights=w,
        edges=edges,
        num_nodes=num_nodes,
        num_edges=num_edges,
        num_islands_attached=num_islands,
    )
