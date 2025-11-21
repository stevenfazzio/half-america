"""Full data pipeline for loading and processing Census Tract data."""

import geopandas as gpd
import pandas as pd

from half_america.config import ACS_YEAR, TIGER_YEAR
from half_america.data.cache import ensure_cache_dirs, get_processed_cache_path
from half_america.data.census import fetch_state_population
from half_america.data.cleaning import clean_census_tracts
from half_america.data.constants import CONTIGUOUS_US_FIPS
from half_america.data.tiger import download_state_tracts


def load_state_tracts(
    state_fips: str,
    force_download: bool = False,
) -> gpd.GeoDataFrame:
    """
    Load tract data for a single state with population.

    Downloads geometry, fetches population, cleans, and joins.

    Args:
        state_fips: Two-digit FIPS code
        force_download: If True, re-download/fetch even if cached

    Returns:
        GeoDataFrame with cleaned geometries and population
    """
    # Download geometry
    gdf = download_state_tracts(state_fips, force_download=force_download)

    # Clean geometry
    gdf, _stats = clean_census_tracts(gdf, verbose=False)

    # Fetch population
    pop_df = fetch_state_population(state_fips, force_fetch=force_download)

    # Join population to geometry
    gdf = gdf.merge(pop_df[["GEOID", "population"]], on="GEOID", how="left")

    # Fill missing population with 0 (water-only tracts, etc.)
    gdf["population"] = gdf["population"].fillna(0).astype(int)

    return gdf


def load_all_tracts(
    force_download: bool = False,
    use_cache: bool = True,
) -> gpd.GeoDataFrame:
    """
    Load all contiguous US tract data with population.

    Args:
        force_download: If True, re-download everything
        use_cache: If True, use processed cache if available

    Returns:
        GeoDataFrame with all tracts, cleaned geometries, and population
    """
    ensure_cache_dirs()
    cache_path = get_processed_cache_path(f"all_tracts_{TIGER_YEAR}_{ACS_YEAR}")

    # Return processed cache if available
    if use_cache and cache_path.exists() and not force_download:
        print(f"Loading cached processed data from {cache_path}")
        return gpd.read_parquet(cache_path)

    print("Loading all contiguous US tract data...")

    all_gdfs: list[gpd.GeoDataFrame] = []
    total_population = 0

    for fips in CONTIGUOUS_US_FIPS:
        gdf = load_state_tracts(fips, force_download=force_download)
        all_gdfs.append(gdf)
        total_population += gdf["population"].sum()

    # Concatenate all states
    print(f"Concatenating {len(all_gdfs)} state datasets...")
    combined = gpd.GeoDataFrame(
        pd.concat(all_gdfs, ignore_index=True),
        crs=all_gdfs[0].crs,
    )

    # Cache processed result
    combined.to_parquet(cache_path)
    print(f"Cached processed data to {cache_path}")

    print("\nSummary:")
    print(f"  Total tracts: {len(combined):,}")
    print(f"  Total population: {total_population:,}")
    print(f"  50% population: {total_population // 2:,}")

    return combined


def get_pipeline_summary(gdf: gpd.GeoDataFrame) -> dict:
    """
    Get summary statistics for loaded tract data.

    Args:
        gdf: GeoDataFrame with tract data

    Returns:
        Dictionary with summary statistics
    """
    return {
        "tract_count": len(gdf),
        "total_population": int(gdf["population"].sum()),
        "half_population": int(gdf["population"].sum() // 2),
        "total_area_sqkm": float(gdf["area_sqm"].sum() / 1e6),
        "median_tract_area_sqkm": float(gdf["area_sqm"].median() / 1e6),
        "min_population": int(gdf["population"].min()),
        "max_population": int(gdf["population"].max()),
        "median_population": int(gdf["population"].median()),
        "crs": str(gdf.crs),
    }
