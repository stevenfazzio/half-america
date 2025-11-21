"""Census API population data fetching."""

import pandas as pd
import cenpy
import requests_cache
from datetime import timedelta

from half_america.config import CENSUS_API_KEY, ACS_YEAR, CACHE_DIR
from half_america.data.cache import ensure_cache_dirs, get_census_cache_path
from half_america.data.constants import CONTIGUOUS_US_FIPS, FIPS_TO_STATE


def _setup_requests_cache() -> None:
    """Install requests-cache for Census API calls."""
    cache_path = CACHE_DIR / "requests_cache"
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    requests_cache.install_cache(
        str(cache_path),
        backend="sqlite",
        expire_after=timedelta(days=30),
        stale_if_error=True,
    )


def fetch_state_population(
    state_fips: str,
    year: int = ACS_YEAR,
    force_fetch: bool = False,
) -> pd.DataFrame:
    """
    Fetch population data for all tracts in a state.

    Args:
        state_fips: Two-digit FIPS code for the state
        year: ACS 5-Year estimate year (default: 2022)
        force_fetch: If True, re-fetch even if cached

    Returns:
        DataFrame with GEOID and population columns
    """
    ensure_cache_dirs()
    cache_path = get_census_cache_path(state_fips, year)

    # Return cached data if available
    if cache_path.exists() and not force_fetch:
        return pd.read_parquet(cache_path)

    # Setup requests caching
    _setup_requests_cache()

    state_name = FIPS_TO_STATE.get(state_fips, state_fips)
    print(f"Fetching ACS population for {state_name} ({state_fips})...")

    # Connect to ACS 5-Year API
    conn = cenpy.remote.APIConnection(f"ACSDT5Y{year}")

    # Query tract-level population
    # B01003_001E = Total Population
    data = conn.query(
        cols=["NAME", "B01003_001E", "GEO_ID"],
        geo_unit="tract:*",
        geo_filter={"state": state_fips, "county": "*"},
    )

    # Process results
    df = pd.DataFrame(data)

    # Convert population to numeric (API returns strings)
    df["population"] = pd.to_numeric(df["B01003_001E"], errors="coerce").fillna(0).astype(int)

    # Create GEOID for joining with TIGER data
    # GEOID format: state (2) + county (3) + tract (6) = 11 digits
    df["GEOID"] = df["state"] + df["county"] + df["tract"]

    # Keep only needed columns
    result = df[["GEOID", "population", "NAME"]].copy()

    # Cache as Parquet
    result.to_parquet(cache_path)
    print(f"  Cached {len(result)} tract populations to {cache_path}")

    return result


def fetch_all_population(
    year: int = ACS_YEAR,
    force_fetch: bool = False,
) -> pd.DataFrame:
    """
    Fetch population data for all contiguous US tracts.

    Args:
        year: ACS 5-Year estimate year (default: 2022)
        force_fetch: If True, re-fetch even if cached

    Returns:
        DataFrame with GEOID and population for all tracts
    """
    all_dfs: list[pd.DataFrame] = []

    for fips in CONTIGUOUS_US_FIPS:
        df = fetch_state_population(fips, year, force_fetch)
        all_dfs.append(df)

    # Concatenate all states
    print(f"Concatenating {len(all_dfs)} state population datasets...")
    combined = pd.concat(all_dfs, ignore_index=True)

    print(f"Total tracts with population: {len(combined)}")
    print(f"Total US population: {combined['population'].sum():,}")

    return combined
