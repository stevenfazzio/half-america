"""Data pipeline for Half of America."""

from half_america.data.constants import CONTIGUOUS_US_FIPS, FIPS_TO_STATE, TARGET_CRS
from half_america.data.tiger import download_state_tracts, download_all_tracts
from half_america.data.census import fetch_state_population, fetch_all_population
from half_america.data.cleaning import clean_census_tracts, CleaningStats
from half_america.data.pipeline import (
    load_state_tracts,
    load_all_tracts,
    get_pipeline_summary,
)

__all__ = [
    # Constants
    "CONTIGUOUS_US_FIPS",
    "FIPS_TO_STATE",
    "TARGET_CRS",
    # TIGER/Line
    "download_state_tracts",
    "download_all_tracts",
    # Census
    "fetch_state_population",
    "fetch_all_population",
    # Cleaning
    "clean_census_tracts",
    "CleaningStats",
    # Pipeline
    "load_state_tracts",
    "load_all_tracts",
    "get_pipeline_summary",
]
