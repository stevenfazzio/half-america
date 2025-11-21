"""Geometry cleaning and validation utilities."""

from typing import NamedTuple

import geopandas as gpd
import shapely

from half_america.data.constants import QUANTIZATION_GRID_SIZE, TARGET_CRS


class CleaningStats(NamedTuple):
    """Statistics from geometry cleaning."""

    input_count: int
    null_removed: int
    invalid_fixed: int
    invalid_after_quantize: int
    output_count: int


def remove_null_geometries(gdf: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, int]:
    """
    Remove rows with null or empty geometries.

    Returns:
        Tuple of (cleaned GeoDataFrame, count removed)
    """
    null_mask = gdf.geometry.isna() | gdf.geometry.is_empty
    removed_count = null_mask.sum()

    if removed_count > 0:
        gdf = gdf[~null_mask].copy()

    return gdf, removed_count


def fix_invalid_geometries(gdf: gpd.GeoDataFrame) -> tuple[gpd.GeoDataFrame, int]:
    """
    Fix invalid geometries using shapely.make_valid().

    Returns:
        Tuple of (fixed GeoDataFrame, count fixed)
    """
    gdf = gdf.copy()
    invalid_mask = ~gdf.is_valid
    invalid_count = invalid_mask.sum()

    if invalid_count > 0:
        gdf["geometry"] = shapely.make_valid(gdf["geometry"])

    return gdf, invalid_count


def reproject_to_equal_area(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Reproject to Albers Equal Area (EPSG:5070) for US.

    This CRS is required for accurate area calculations.
    """
    if gdf.crs is None:
        raise ValueError("GeoDataFrame has no CRS defined")

    if str(gdf.crs) != TARGET_CRS:
        gdf = gdf.to_crs(TARGET_CRS)

    return gdf


def quantize_coordinates(
    gdf: gpd.GeoDataFrame,
    grid_size: float = QUANTIZATION_GRID_SIZE,
) -> tuple[gpd.GeoDataFrame, int]:
    """
    Quantize coordinates to a fixed grid to close micro-gaps.

    Args:
        gdf: GeoDataFrame to quantize
        grid_size: Grid cell size in CRS units (default: 0.01m = 1cm)

    Returns:
        Tuple of (quantized GeoDataFrame, count re-fixed after quantization)
    """
    gdf = gdf.copy()

    # Quantize coordinates
    gdf["geometry"] = shapely.set_precision(gdf["geometry"], grid_size=grid_size)

    # Quantization can introduce new invalid geometries - fix them
    invalid_mask = ~gdf.is_valid
    invalid_count = invalid_mask.sum()

    if invalid_count > 0:
        gdf.loc[invalid_mask, "geometry"] = shapely.make_valid(
            gdf.loc[invalid_mask, "geometry"]
        )

    return gdf, invalid_count


def normalize_geometries(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Normalize coordinate order for consistent comparisons."""
    gdf = gdf.copy()
    gdf["geometry"] = gdf.normalize()
    return gdf


def add_area_column(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Add area_sqm column with geometry area in square meters."""
    gdf = gdf.copy()
    gdf["area_sqm"] = gdf.geometry.area
    return gdf


def clean_census_tracts(
    gdf: gpd.GeoDataFrame,
    verbose: bool = True,
) -> tuple[gpd.GeoDataFrame, CleaningStats]:
    """
    Complete geometry cleaning pipeline for Census Tracts.

    Pipeline steps:
    1. Remove null/empty geometries
    2. Reproject to Albers Equal Area (EPSG:5070)
    3. Fix invalid geometries (make_valid)
    4. Quantize coordinates (close micro-gaps)
    5. Normalize coordinate order
    6. Add area column

    Args:
        gdf: GeoDataFrame with tract geometries
        verbose: If True, print progress messages

    Returns:
        Tuple of (cleaned GeoDataFrame, cleaning statistics)
    """
    input_count = len(gdf)

    if verbose:
        print(f"Cleaning {input_count} tract geometries...")

    # 1. Remove null/empty geometries
    gdf, null_removed = remove_null_geometries(gdf)
    if verbose and null_removed > 0:
        print(f"  Removed {null_removed} null/empty geometries")

    # 2. Reproject to equal area CRS
    gdf = reproject_to_equal_area(gdf)
    if verbose:
        print(f"  Reprojected to {TARGET_CRS}")

    # 3. Fix invalid geometries
    gdf, invalid_fixed = fix_invalid_geometries(gdf)
    if verbose and invalid_fixed > 0:
        print(f"  Fixed {invalid_fixed} invalid geometries")

    # 4. Quantize coordinates
    gdf, invalid_after_quantize = quantize_coordinates(gdf)
    if verbose and invalid_after_quantize > 0:
        print(f"  Re-fixed {invalid_after_quantize} geometries after quantization")

    # 5. Normalize coordinate order
    gdf = normalize_geometries(gdf)

    # 6. Add area column
    gdf = add_area_column(gdf)
    if verbose:
        print("  Added area_sqm column")

    output_count = len(gdf)
    stats = CleaningStats(
        input_count=input_count,
        null_removed=null_removed,
        invalid_fixed=invalid_fixed,
        invalid_after_quantize=invalid_after_quantize,
        output_count=output_count,
    )

    if verbose:
        print(f"  Done: {output_count} clean geometries")

    return gdf, stats
