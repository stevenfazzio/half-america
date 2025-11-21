"""TIGER/Line shapefile download and caching."""

import geopandas as gpd
import pandas as pd

from half_america.config import TIGER_YEAR
from half_america.data.cache import ensure_cache_dirs, get_tiger_cache_path
from half_america.data.constants import CONTIGUOUS_US_FIPS, FIPS_TO_STATE


def get_tiger_url(state_fips: str, year: int = TIGER_YEAR) -> str:
    """Construct TIGER/Line download URL for a state."""
    return f"https://www2.census.gov/geo/tiger/TIGER{year}/TRACT/tl_{year}_{state_fips}_tract.zip"


def download_state_tracts(
    state_fips: str,
    year: int = TIGER_YEAR,
    force_download: bool = False,
) -> gpd.GeoDataFrame:
    """
    Download TIGER/Line tract shapefile for a state.

    Args:
        state_fips: Two-digit FIPS code for the state
        year: TIGER/Line year (default: 2024)
        force_download: If True, re-download even if cached

    Returns:
        GeoDataFrame with tract geometries
    """
    ensure_cache_dirs()
    cache_path = get_tiger_cache_path(state_fips, year)

    # Return cached data if available
    if cache_path.exists() and not force_download:
        return gpd.read_parquet(cache_path)

    # Download from Census Bureau
    url = get_tiger_url(state_fips, year)
    state_name = FIPS_TO_STATE.get(state_fips, state_fips)
    print(f"Downloading TIGER/Line tracts for {state_name} ({state_fips})...")

    gdf = gpd.read_file(url)

    # Cache as GeoParquet
    gdf.to_parquet(cache_path)
    print(f"  Cached {len(gdf)} tracts to {cache_path}")

    return gdf


def download_all_tracts(
    year: int = TIGER_YEAR,
    force_download: bool = False,
) -> gpd.GeoDataFrame:
    """
    Download TIGER/Line tracts for all contiguous US states.

    Args:
        year: TIGER/Line year (default: 2024)
        force_download: If True, re-download even if cached

    Returns:
        GeoDataFrame with all tract geometries concatenated
    """
    all_gdfs: list[gpd.GeoDataFrame] = []

    for fips in CONTIGUOUS_US_FIPS:
        gdf = download_state_tracts(fips, year, force_download)
        all_gdfs.append(gdf)

    # Concatenate all states
    print(f"Concatenating {len(all_gdfs)} state datasets...")
    combined = gpd.GeoDataFrame(
        pd.concat(all_gdfs, ignore_index=True),
        crs=all_gdfs[0].crs,
    )

    print(f"Total tracts: {len(combined)}")
    return combined
