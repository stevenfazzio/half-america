"""Dissolve selected tracts into merged geometries."""

from typing import NamedTuple

import geopandas as gpd
import numpy as np
import shapely
from shapely import MultiPolygon, Polygon

from half_america.optimization.sweep import SweepResult


class DissolveResult(NamedTuple):
    """Result from dissolving selected tracts."""

    geometry: MultiPolygon | Polygon
    num_parts: int  # Number of disconnected regions
    total_area_sqm: float  # Total area in square meters
    num_tracts: int  # Number of tracts dissolved


def dissolve_partition(
    gdf: gpd.GeoDataFrame,
    partition: np.ndarray,
) -> DissolveResult:
    """
    Dissolve selected tracts into a single geometry.

    Args:
        gdf: GeoDataFrame with tract geometries (from load_all_tracts)
        partition: Boolean array where True = selected tract

    Returns:
        DissolveResult with merged geometry and metadata

    Raises:
        ValueError: If partition length doesn't match gdf length
        ValueError: If no tracts are selected (partition is all False)
    """
    # Validate inputs
    if len(partition) != len(gdf):
        raise ValueError(
            f"Partition length ({len(partition)}) doesn't match "
            f"GeoDataFrame length ({len(gdf)})"
        )

    num_selected = partition.sum()
    if num_selected == 0:
        raise ValueError("No tracts selected (partition is all False)")

    # Filter to selected tracts
    selected = gdf[partition]

    # Merge all geometries using coverage union (efficient for non-overlapping)
    geom = selected.geometry.union_all()

    # Validate and fix if needed
    if not geom.is_valid:
        geom = shapely.make_valid(geom)

    # Count parts
    if geom.geom_type == "MultiPolygon":
        num_parts = len(geom.geoms)
    elif geom.geom_type == "Polygon":
        num_parts = 1
    else:
        # GeometryCollection or other - extract polygons
        polygons = [g for g in geom.geoms if g.geom_type in ("Polygon", "MultiPolygon")]
        if polygons:
            geom = shapely.union_all(polygons)
            num_parts = len(geom.geoms) if geom.geom_type == "MultiPolygon" else 1
        else:
            num_parts = 0

    return DissolveResult(
        geometry=geom,
        num_parts=num_parts,
        total_area_sqm=geom.area,
        num_tracts=int(num_selected),
    )


def dissolve_all_lambdas(
    gdf: gpd.GeoDataFrame,
    sweep_result: SweepResult,
    verbose: bool = True,
) -> dict[float, DissolveResult]:
    """
    Dissolve partitions for all lambda values in a sweep result.

    Args:
        gdf: GeoDataFrame with tract geometries (from load_all_tracts)
        sweep_result: SweepResult from sweep_lambda()
        verbose: Print progress messages

    Returns:
        Dictionary mapping lambda values to DissolveResult
    """
    results: dict[float, DissolveResult] = {}

    for lambda_val in sweep_result.lambda_values:
        if verbose:
            print(f"Dissolving λ={lambda_val:.2f}...")

        partition = sweep_result.results[lambda_val].search_result.result.partition
        result = dissolve_partition(gdf, partition)
        results[lambda_val] = result

        if verbose:
            print(f"  {result.num_tracts:,} tracts → {result.num_parts} parts")

    return results
