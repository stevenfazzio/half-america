"""Data caching utilities."""

from pathlib import Path
from half_america.config import TIGER_DIR, CENSUS_DIR, PROCESSED_DIR


def ensure_cache_dirs() -> None:
    """Create cache directories if they don't exist."""
    TIGER_DIR.mkdir(parents=True, exist_ok=True)
    CENSUS_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def get_tiger_cache_path(state_fips: str, year: int) -> Path:
    """Get cache path for a state's TIGER/Line data."""
    return TIGER_DIR / f"tracts_{state_fips}_{year}.parquet"


def get_census_cache_path(state_fips: str, year: int) -> Path:
    """Get cache path for a state's Census population data."""
    return CENSUS_DIR / f"population_{state_fips}_{year}.parquet"


def get_processed_cache_path(name: str) -> Path:
    """Get cache path for processed data."""
    return PROCESSED_DIR / f"{name}.parquet"
