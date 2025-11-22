"""Geometry simplification for web performance."""

from typing import NamedTuple

import shapely
from shapely import MultiPolygon, Polygon

from half_america.postprocess.dissolve import DissolveResult


class SimplifyResult(NamedTuple):
    """Result from simplifying a dissolved geometry."""

    geometry: MultiPolygon | Polygon
    original_vertex_count: int
    simplified_vertex_count: int
    reduction_percent: float


# Default tolerance in meters (EPSG:5070)
# 500m provides 98.3% vertex reduction with good visual fidelity
DEFAULT_TOLERANCE = 500.0


def simplify_geometry(
    geometry: MultiPolygon | Polygon,
    tolerance: float = DEFAULT_TOLERANCE,
    preserve_topology: bool = True,
) -> SimplifyResult:
    """
    Simplify a dissolved geometry for web display.

    Uses Douglas-Peucker algorithm via shapely.simplify() with topology
    preservation. This is appropriate for dissolved geometries where
    polygon parts are disconnected (not sharing edges).

    Parameters
    ----------
    geometry : MultiPolygon | Polygon
        Dissolved geometry from dissolve_partition()
    tolerance : float
        Simplification tolerance in CRS units (meters for EPSG:5070).
        Default is 500m which provides ~98% vertex reduction.
    preserve_topology : bool
        If True, ensures valid output geometry (no self-intersections).
        Default is True.

    Returns
    -------
    SimplifyResult
        Simplified geometry with reduction statistics

    Examples
    --------
    >>> from half_america.postprocess import dissolve_partition, simplify_geometry
    >>> dissolve_result = dissolve_partition(gdf, partition)
    >>> simplify_result = simplify_geometry(dissolve_result.geometry)
    >>> print(f"Reduced by {simplify_result.reduction_percent:.1f}%")
    """
    original_count = int(shapely.get_num_coordinates(geometry))

    simplified = shapely.simplify(
        geometry,
        tolerance=tolerance,
        preserve_topology=preserve_topology,
    )

    simplified_count = int(shapely.get_num_coordinates(simplified))
    reduction = (
        (1 - simplified_count / original_count) * 100 if original_count > 0 else 0.0
    )

    return SimplifyResult(
        geometry=simplified,
        original_vertex_count=original_count,
        simplified_vertex_count=simplified_count,
        reduction_percent=float(reduction),
    )


def simplify_all_lambdas(
    dissolve_results: dict[float, DissolveResult],
    tolerance: float = DEFAULT_TOLERANCE,
    verbose: bool = True,
) -> dict[float, SimplifyResult]:
    """
    Simplify dissolved geometries for all lambda values.

    Parameters
    ----------
    dissolve_results : dict[float, DissolveResult]
        Dictionary mapping lambda values to DissolveResult from dissolve_all_lambdas()
    tolerance : float
        Simplification tolerance in CRS units (meters for EPSG:5070)
    verbose : bool
        Print progress messages

    Returns
    -------
    dict[float, SimplifyResult]
        Dictionary mapping lambda values to SimplifyResult

    Examples
    --------
    >>> dissolve_results = dissolve_all_lambdas(gdf, sweep_result)
    >>> simplify_results = simplify_all_lambdas(dissolve_results)
    """
    results: dict[float, SimplifyResult] = {}

    for lambda_val, dissolve_result in dissolve_results.items():
        if verbose:
            print(f"Simplifying λ={lambda_val:.2f}...")

        result = simplify_geometry(dissolve_result.geometry, tolerance=tolerance)
        results[lambda_val] = result

        if verbose:
            orig = result.original_vertex_count
            simp = result.simplified_vertex_count
            pct = result.reduction_percent
            print(f"  {orig:,} → {simp:,} vertices ({pct:.1f}% reduction)")

    return results
