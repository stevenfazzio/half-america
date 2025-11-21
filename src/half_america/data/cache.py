"""Data caching utilities."""

from pathlib import Path

from half_america.config import CENSUS_DIR, PROCESSED_DIR, TIGER_DIR


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


def get_sweep_cache_path(lambda_step: float = 0.1) -> Path:
    """Get cache path for sweep results.

    Args:
        lambda_step: Lambda increment used in sweep (default 0.1)

    Returns:
        Path like data/cache/processed/sweep_2024_2022_0.1.pkl
    """
    from half_america.config import ACS_YEAR, TIGER_YEAR

    return PROCESSED_DIR / f"sweep_{TIGER_YEAR}_{ACS_YEAR}_{lambda_step}.pkl"
