# Phase 1: Data Pipeline Implementation Plan

## Overview

Implement the data acquisition and preprocessing pipeline for Half of America. This phase builds the foundation for loading ~73,000 US Census Tract geometries and population data, cleaning geometries for topological correctness, and caching results to avoid repeated downloads.

## Current State Analysis

The project is in skeleton phase:
- `src/half_america/__init__.py` contains only a stub `main()` function
- No production dependencies in `pyproject.toml`
- No `data/` module or directory structure
- Single sanity test in `tests/test_sanity.py`

### Key Discoveries:
- `pyproject.toml:11` - Empty dependencies array
- `ROADMAP.md:17-25` - Phase 1 milestones definition
- `METHODOLOGY.md:85-89` - Implementation stack (geopandas, cenpy, shapely, etc.)
- Research doc specifies 2024 TIGER/Line + 2022 ACS 5-Year data

## Desired End State

After this plan is complete:
- All production dependencies installed and working
- Module structure: `src/half_america/data/` with census.py, tiger.py, cleaning.py, cache.py
- Can download all 49 contiguous US state/DC tract shapefiles
- Can fetch population data for all tracts via Census API
- Geometries cleaned: valid, quantized, no gaps
- All data cached in GeoParquet format
- Unit tests passing with DC fixtures

### Verification:
```bash
# All tests pass
uv run pytest

# Can import and use modules
uv run python -c "from half_america.data import tiger, census, cleaning"

# Type checking passes
uv run mypy src/

# Linting passes
uv run ruff check src/ tests/
```

## What We're NOT Doing

- CLI commands (just Python modules for now)
- Phase 2 graph construction (adjacency, libpysal)
- Phase 3 optimization (PyMaxFlow)
- Chunked/streaming processing (24GB RAM is sufficient)
- Supporting non-contiguous US (Alaska, Hawaii, territories)

## Implementation Approach

State-by-state processing with aggressive caching:
1. Download each state's TIGER/Line shapefile → cache as GeoParquet
2. Fetch each state's population via Census API → cache responses
3. Clean geometries (make_valid, quantize)
4. Merge all states into single national dataset
5. Join population data to geometries

---

## Phase 1: Project Setup

### Overview
Add production dependencies and create the module structure.

### Changes Required:

#### 1. Production Dependencies
**File**: `pyproject.toml`
**Changes**: Add all Phase 1 dependencies

```toml
dependencies = [
    # Data ingestion
    "pandas>=2.0",
    "cenpy>=1.0",

    # Spatial operations
    "geopandas>=0.14",
    "shapely>=2.0",

    # TopoJSON/Topology
    "topojson>=1.6",

    # Caching
    "requests-cache>=1.1",

    # File formats
    "pyarrow>=14.0",

    # Environment variables
    "python-dotenv>=1.0",
]
```

#### 2. Environment Configuration
**File**: `.env.example` (new file)
**Changes**: Create template for required environment variables

```
# Census API Key (get from https://api.census.gov/data/key_signup.html)
CENSUS_API_KEY=your_api_key_here
```

#### 3. Git Ignore Updates
**File**: `.gitignore`
**Changes**: Add data directories and .env

```gitignore
# Environment
.env

# Data cache (large files)
data/
```

#### 4. Module Structure
**Files**: Create empty module files

```
src/half_america/
├── __init__.py          (existing)
├── config.py            (new)
└── data/
    ├── __init__.py      (new)
    ├── constants.py     (new)
    ├── cache.py         (new)
    ├── tiger.py         (new)
    ├── census.py        (new)
    └── cleaning.py      (new)
```

#### 5. Configuration Module
**File**: `src/half_america/config.py` (new)
**Changes**: Central configuration with paths and constants

```python
"""Central configuration for Half of America."""

from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project root (relative to this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
CACHE_DIR = DATA_DIR / "cache"
RAW_DIR = CACHE_DIR / "raw"
TIGER_DIR = RAW_DIR / "tiger"
CENSUS_DIR = RAW_DIR / "census"
PROCESSED_DIR = CACHE_DIR / "processed"

# Census API configuration
CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")

# Data year configuration (locked versions)
TIGER_YEAR = 2024
ACS_YEAR = 2022
```

#### 6. Constants Module
**File**: `src/half_america/data/constants.py` (new)
**Changes**: FIPS codes and other constants

```python
"""Constants for data pipeline."""

# Contiguous US FIPS codes (48 states + DC = 49)
# Excludes: Alaska (02), Hawaii (15), territories
CONTIGUOUS_US_FIPS: list[str] = [
    "01",  # Alabama
    "04",  # Arizona
    "05",  # Arkansas
    "06",  # California
    "08",  # Colorado
    "09",  # Connecticut
    "10",  # Delaware
    "11",  # District of Columbia
    "12",  # Florida
    "13",  # Georgia
    "16",  # Idaho
    "17",  # Illinois
    "18",  # Indiana
    "19",  # Iowa
    "20",  # Kansas
    "21",  # Kentucky
    "22",  # Louisiana
    "23",  # Maine
    "24",  # Maryland
    "25",  # Massachusetts
    "26",  # Michigan
    "27",  # Minnesota
    "28",  # Mississippi
    "29",  # Missouri
    "30",  # Montana
    "31",  # Nebraska
    "32",  # Nevada
    "33",  # New Hampshire
    "34",  # New Jersey
    "35",  # New Mexico
    "36",  # New York
    "37",  # North Carolina
    "38",  # North Dakota
    "39",  # Ohio
    "40",  # Oklahoma
    "41",  # Oregon
    "42",  # Pennsylvania
    "44",  # Rhode Island
    "45",  # South Carolina
    "46",  # South Dakota
    "47",  # Tennessee
    "48",  # Texas
    "49",  # Utah
    "50",  # Vermont
    "51",  # Virginia
    "53",  # Washington
    "54",  # West Virginia
    "55",  # Wisconsin
    "56",  # Wyoming
]

# State FIPS to name mapping (for logging/debugging)
FIPS_TO_STATE: dict[str, str] = {
    "01": "Alabama",
    "04": "Arizona",
    "05": "Arkansas",
    "06": "California",
    "08": "Colorado",
    "09": "Connecticut",
    "10": "Delaware",
    "11": "District of Columbia",
    "12": "Florida",
    "13": "Georgia",
    "16": "Idaho",
    "17": "Illinois",
    "18": "Indiana",
    "19": "Iowa",
    "20": "Kansas",
    "21": "Kentucky",
    "22": "Louisiana",
    "23": "Maine",
    "24": "Maryland",
    "25": "Massachusetts",
    "26": "Michigan",
    "27": "Minnesota",
    "28": "Mississippi",
    "29": "Missouri",
    "30": "Montana",
    "31": "Nebraska",
    "32": "Nevada",
    "33": "New Hampshire",
    "34": "New Jersey",
    "35": "New Mexico",
    "36": "New York",
    "37": "North Carolina",
    "38": "North Dakota",
    "39": "Ohio",
    "40": "Oklahoma",
    "41": "Oregon",
    "42": "Pennsylvania",
    "44": "Rhode Island",
    "45": "South Carolina",
    "46": "South Dakota",
    "47": "Tennessee",
    "48": "Texas",
    "49": "Utah",
    "50": "Vermont",
    "51": "Virginia",
    "53": "Washington",
    "54": "West Virginia",
    "55": "Wisconsin",
    "56": "Wyoming",
}

# Target CRS for all spatial operations (Albers Equal Area for US)
TARGET_CRS = "EPSG:5070"

# Coordinate quantization grid size (1cm for meters-based CRS)
QUANTIZATION_GRID_SIZE = 0.01
```

### Success Criteria:

#### Automated Verification:
- [x] Dependencies install cleanly: `uv sync`
- [x] Module imports work: `uv run python -c "from half_america.data import constants"`
- [x] Type checking passes: `uv run mypy src/`
- [x] Linting passes: `uv run ruff check src/`

#### Manual Verification:
- [x] `.env.example` contains clear instructions for API key setup

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation before proceeding to the next phase.

---

## Phase 2: TIGER/Line Download

### Overview
Implement TIGER/Line shapefile downloading with GeoParquet caching.

### Changes Required:

#### 1. Cache Module
**File**: `src/half_america/data/cache.py` (new)
**Changes**: Cache directory setup and utilities

```python
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
```

#### 2. TIGER Download Module
**File**: `src/half_america/data/tiger.py` (new)
**Changes**: Download and cache TIGER/Line shapefiles

```python
"""TIGER/Line shapefile download and caching."""

import geopandas as gpd
from pathlib import Path

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


# Need pandas import for concat
import pandas as pd
```

#### 3. Data Module Init
**File**: `src/half_america/data/__init__.py` (new)
**Changes**: Export public API

```python
"""Data pipeline for Half of America."""

from half_america.data.constants import CONTIGUOUS_US_FIPS, FIPS_TO_STATE, TARGET_CRS
from half_america.data.tiger import download_state_tracts, download_all_tracts

__all__ = [
    "CONTIGUOUS_US_FIPS",
    "FIPS_TO_STATE",
    "TARGET_CRS",
    "download_state_tracts",
    "download_all_tracts",
]
```

### Success Criteria:

#### Automated Verification:
- [x] Module imports: `uv run python -c "from half_america.data import download_state_tracts"`
- [x] Type checking passes: `uv run mypy src/`
- [x] Linting passes: `uv run ruff check src/`

#### Manual Verification:
- [x] Download DC tracts (smallest state): `uv run python -c "from half_america.data import download_state_tracts; gdf = download_state_tracts('11'); print(f'Downloaded {len(gdf)} tracts')"`
- [x] Cache file created at `data/cache/raw/tiger/tracts_11_2024.parquet`
- [x] Second run uses cache (no download message)

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation before proceeding to the next phase.

---

## Phase 3: Census API Integration

### Overview
Implement Census API population fetching with requests-cache.

### Changes Required:

#### 1. Census Module
**File**: `src/half_america/data/census.py` (new)
**Changes**: Census API client with caching

```python
"""Census API population data fetching."""

import pandas as pd
import cenpy
import requests_cache
from datetime import timedelta
from pathlib import Path

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
```

#### 2. Update Data Module Init
**File**: `src/half_america/data/__init__.py`
**Changes**: Add census exports

```python
"""Data pipeline for Half of America."""

from half_america.data.constants import CONTIGUOUS_US_FIPS, FIPS_TO_STATE, TARGET_CRS
from half_america.data.tiger import download_state_tracts, download_all_tracts
from half_america.data.census import fetch_state_population, fetch_all_population

__all__ = [
    "CONTIGUOUS_US_FIPS",
    "FIPS_TO_STATE",
    "TARGET_CRS",
    "download_state_tracts",
    "download_all_tracts",
    "fetch_state_population",
    "fetch_all_population",
]
```

### Success Criteria:

#### Automated Verification:
- [x] Module imports: `uv run python -c "from half_america.data import fetch_state_population"`
- [x] Type checking passes: `uv run mypy src/`
- [x] Linting passes: `uv run ruff check src/`

#### Manual Verification:
- [x] Create `.env` file with valid `CENSUS_API_KEY`
- [x] Fetch DC population: `uv run python -c "from half_america.data import fetch_state_population; df = fetch_state_population('11'); print(f'Got {len(df)} tracts, total pop: {df.population.sum():,}')"`
- [x] Cache file created at `data/cache/raw/census/population_11_2022.parquet`
- [x] requests-cache database created at `data/cache/requests_cache.sqlite`

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation before proceeding to the next phase.

---

## Phase 4: Geometry Cleaning Pipeline

### Overview
Implement geometry validation, repair, and coordinate quantization.

### Changes Required:

#### 1. Cleaning Module
**File**: `src/half_america/data/cleaning.py` (new)
**Changes**: Geometry cleaning functions

```python
"""Geometry cleaning and validation utilities."""

import geopandas as gpd
import shapely
from typing import NamedTuple

from half_america.data.constants import TARGET_CRS, QUANTIZATION_GRID_SIZE


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
        print(f"  Added area_sqm column")

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
```

#### 2. Update Data Module Init
**File**: `src/half_america/data/__init__.py`
**Changes**: Add cleaning exports

```python
"""Data pipeline for Half of America."""

from half_america.data.constants import CONTIGUOUS_US_FIPS, FIPS_TO_STATE, TARGET_CRS
from half_america.data.tiger import download_state_tracts, download_all_tracts
from half_america.data.census import fetch_state_population, fetch_all_population
from half_america.data.cleaning import clean_census_tracts, CleaningStats

__all__ = [
    "CONTIGUOUS_US_FIPS",
    "FIPS_TO_STATE",
    "TARGET_CRS",
    "download_state_tracts",
    "download_all_tracts",
    "fetch_state_population",
    "fetch_all_population",
    "clean_census_tracts",
    "CleaningStats",
]
```

### Success Criteria:

#### Automated Verification:
- [x] Module imports: `uv run python -c "from half_america.data import clean_census_tracts"`
- [x] Type checking passes: `uv run mypy src/`
- [x] Linting passes: `uv run ruff check src/`

#### Manual Verification:
- [x] Clean DC tracts: `uv run python -c "from half_america.data import download_state_tracts, clean_census_tracts; gdf = download_state_tracts('11'); cleaned, stats = clean_census_tracts(gdf); print(stats)"`
- [x] All geometries valid after cleaning
- [x] CRS is EPSG:5070
- [x] area_sqm column exists

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation before proceeding to the next phase.

---

## Phase 5: Data Merge & Export

### Overview
Join geometries with population data and export merged dataset.

### Changes Required:

#### 1. Pipeline Module
**File**: `src/half_america/data/pipeline.py` (new)
**Changes**: Full data pipeline orchestration

```python
"""Full data pipeline for loading and processing Census Tract data."""

import geopandas as gpd
import pandas as pd

from half_america.data.tiger import download_state_tracts, download_all_tracts
from half_america.data.census import fetch_state_population, fetch_all_population
from half_america.data.cleaning import clean_census_tracts, CleaningStats
from half_america.data.cache import ensure_cache_dirs, get_processed_cache_path
from half_america.data.constants import CONTIGUOUS_US_FIPS
from half_america.config import TIGER_YEAR, ACS_YEAR


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

    print(f"\nSummary:")
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
```

#### 2. Update Data Module Init
**File**: `src/half_america/data/__init__.py`
**Changes**: Add pipeline exports

```python
"""Data pipeline for Half of America."""

from half_america.data.constants import CONTIGUOUS_US_FIPS, FIPS_TO_STATE, TARGET_CRS
from half_america.data.tiger import download_state_tracts, download_all_tracts
from half_america.data.census import fetch_state_population, fetch_all_population
from half_america.data.cleaning import clean_census_tracts, CleaningStats
from half_america.data.pipeline import load_state_tracts, load_all_tracts, get_pipeline_summary

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
```

### Success Criteria:

#### Automated Verification:
- [x] Module imports: `uv run python -c "from half_america.data import load_all_tracts"`
- [x] Type checking passes: `uv run mypy src/`
- [x] Linting passes: `uv run ruff check src/`

#### Manual Verification:
- [x] Load DC tracts with population: `uv run python -c "from half_america.data import load_state_tracts, get_pipeline_summary; gdf = load_state_tracts('11'); print(get_pipeline_summary(gdf))"`
- [x] Verify GEOID, population, area_sqm columns exist
- [x] Population values are reasonable (DC ~700k total)

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation before proceeding to the next phase.

---

## Phase 6: Unit Tests

### Overview
Add comprehensive unit tests with DC fixtures.

### Changes Required:

#### 1. Test Fixtures
**File**: `tests/conftest.py` (new)
**Changes**: Pytest fixtures for testing

```python
"""Pytest fixtures for data pipeline tests."""

import pytest
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon, box
from pathlib import Path
import tempfile


@pytest.fixture
def sample_polygon() -> Polygon:
    """Create a simple valid polygon."""
    return box(0, 0, 100, 100)


@pytest.fixture
def invalid_polygon() -> Polygon:
    """Create a self-intersecting (bowtie) polygon."""
    # Bowtie shape - self-intersecting
    return Polygon([(0, 0), (100, 100), (100, 0), (0, 100), (0, 0)])


@pytest.fixture
def sample_gdf(sample_polygon) -> gpd.GeoDataFrame:
    """Create a simple GeoDataFrame with valid geometries."""
    return gpd.GeoDataFrame(
        {
            "GEOID": ["001", "002", "003"],
            "NAME": ["Tract 1", "Tract 2", "Tract 3"],
            "geometry": [
                box(0, 0, 100, 100),
                box(100, 0, 200, 100),
                box(0, 100, 100, 200),
            ],
        },
        crs="EPSG:4326",
    )


@pytest.fixture
def gdf_with_invalid(invalid_polygon) -> gpd.GeoDataFrame:
    """Create a GeoDataFrame with one invalid geometry."""
    return gpd.GeoDataFrame(
        {
            "GEOID": ["001", "002"],
            "NAME": ["Valid", "Invalid"],
            "geometry": [box(0, 0, 100, 100), invalid_polygon],
        },
        crs="EPSG:4326",
    )


@pytest.fixture
def gdf_with_null() -> gpd.GeoDataFrame:
    """Create a GeoDataFrame with null geometries."""
    return gpd.GeoDataFrame(
        {
            "GEOID": ["001", "002", "003"],
            "NAME": ["Valid", "Null", "Empty"],
            "geometry": [box(0, 0, 100, 100), None, Polygon()],
        },
        crs="EPSG:4326",
    )


@pytest.fixture
def temp_cache_dir(tmp_path) -> Path:
    """Create a temporary cache directory."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir
```

#### 2. Cleaning Tests
**File**: `tests/test_cleaning.py` (new)
**Changes**: Tests for geometry cleaning functions

```python
"""Tests for geometry cleaning functions."""

import pytest
import geopandas as gpd
from shapely.geometry import box

from half_america.data.cleaning import (
    remove_null_geometries,
    fix_invalid_geometries,
    reproject_to_equal_area,
    quantize_coordinates,
    clean_census_tracts,
)
from half_america.data.constants import TARGET_CRS


class TestRemoveNullGeometries:
    def test_removes_null_geometries(self, gdf_with_null):
        """Test that null geometries are removed."""
        result, count = remove_null_geometries(gdf_with_null)

        assert count == 2  # One None, one empty Polygon
        assert len(result) == 1
        assert result.iloc[0]["GEOID"] == "001"

    def test_preserves_valid_geometries(self, sample_gdf):
        """Test that valid geometries are preserved."""
        result, count = remove_null_geometries(sample_gdf)

        assert count == 0
        assert len(result) == len(sample_gdf)


class TestFixInvalidGeometries:
    def test_fixes_invalid_geometries(self, gdf_with_invalid):
        """Test that invalid geometries are fixed."""
        result, count = fix_invalid_geometries(gdf_with_invalid)

        assert count == 1
        assert result.is_valid.all()

    def test_preserves_valid_geometries(self, sample_gdf):
        """Test that valid geometries remain unchanged."""
        result, count = fix_invalid_geometries(sample_gdf)

        assert count == 0
        assert result.is_valid.all()


class TestReprojectToEqualArea:
    def test_reprojects_to_target_crs(self, sample_gdf):
        """Test reprojection to EPSG:5070."""
        result = reproject_to_equal_area(sample_gdf)

        assert str(result.crs) == TARGET_CRS

    def test_no_op_if_already_target_crs(self, sample_gdf):
        """Test that reprojection is skipped if already in target CRS."""
        projected = sample_gdf.to_crs(TARGET_CRS)
        result = reproject_to_equal_area(projected)

        assert str(result.crs) == TARGET_CRS

    def test_raises_on_missing_crs(self, sample_gdf):
        """Test that error is raised if CRS is missing."""
        sample_gdf.crs = None

        with pytest.raises(ValueError, match="no CRS defined"):
            reproject_to_equal_area(sample_gdf)


class TestQuantizeCoordinates:
    def test_quantizes_coordinates(self, sample_gdf):
        """Test coordinate quantization."""
        projected = sample_gdf.to_crs(TARGET_CRS)
        result, count = quantize_coordinates(projected)

        # Should have no invalid geometries after quantization
        assert result.is_valid.all()


class TestCleanCensusTracts:
    def test_full_pipeline(self, sample_gdf):
        """Test complete cleaning pipeline."""
        result, stats = clean_census_tracts(sample_gdf, verbose=False)

        assert len(result) == len(sample_gdf)
        assert str(result.crs) == TARGET_CRS
        assert "area_sqm" in result.columns
        assert result.is_valid.all()

        assert stats.input_count == 3
        assert stats.output_count == 3

    def test_pipeline_removes_nulls(self, gdf_with_null):
        """Test that pipeline removes null geometries."""
        result, stats = clean_census_tracts(gdf_with_null, verbose=False)

        assert len(result) == 1
        assert stats.null_removed == 2

    def test_pipeline_fixes_invalid(self, gdf_with_invalid):
        """Test that pipeline fixes invalid geometries."""
        result, stats = clean_census_tracts(gdf_with_invalid, verbose=False)

        assert result.is_valid.all()
        assert stats.invalid_fixed == 1
```

#### 3. Constants Tests
**File**: `tests/test_constants.py` (new)
**Changes**: Tests for constants module

```python
"""Tests for constants module."""

from half_america.data.constants import (
    CONTIGUOUS_US_FIPS,
    FIPS_TO_STATE,
    TARGET_CRS,
    QUANTIZATION_GRID_SIZE,
)


class TestContiguousUSFips:
    def test_count(self):
        """Test that we have 49 FIPS codes (48 states + DC)."""
        assert len(CONTIGUOUS_US_FIPS) == 49

    def test_excludes_alaska(self):
        """Test that Alaska (02) is excluded."""
        assert "02" not in CONTIGUOUS_US_FIPS

    def test_excludes_hawaii(self):
        """Test that Hawaii (15) is excluded."""
        assert "15" not in CONTIGUOUS_US_FIPS

    def test_includes_dc(self):
        """Test that DC (11) is included."""
        assert "11" in CONTIGUOUS_US_FIPS

    def test_all_two_digit_strings(self):
        """Test that all FIPS codes are two-digit strings."""
        for fips in CONTIGUOUS_US_FIPS:
            assert isinstance(fips, str)
            assert len(fips) == 2
            assert fips.isdigit()


class TestFipsToState:
    def test_all_fips_have_names(self):
        """Test that all FIPS codes have state names."""
        for fips in CONTIGUOUS_US_FIPS:
            assert fips in FIPS_TO_STATE
            assert isinstance(FIPS_TO_STATE[fips], str)
            assert len(FIPS_TO_STATE[fips]) > 0

    def test_dc_name(self):
        """Test DC name is correct."""
        assert FIPS_TO_STATE["11"] == "District of Columbia"


class TestConfig:
    def test_target_crs(self):
        """Test target CRS is Albers Equal Area."""
        assert TARGET_CRS == "EPSG:5070"

    def test_quantization_grid_size(self):
        """Test quantization grid size is 1cm."""
        assert QUANTIZATION_GRID_SIZE == 0.01
```

#### 4. Integration Tests
**File**: `tests/test_integration.py` (new)
**Changes**: Integration tests (marked for optional skip)

```python
"""Integration tests for data pipeline.

These tests make real network requests and should be run sparingly.
Mark with @pytest.mark.integration and skip by default.
"""

import pytest

# Skip integration tests by default (run with: pytest -m integration)
pytestmark = pytest.mark.integration


@pytest.fixture
def skip_without_api_key():
    """Skip test if Census API key is not configured."""
    from half_america.config import CENSUS_API_KEY

    if not CENSUS_API_KEY:
        pytest.skip("CENSUS_API_KEY not configured")


class TestTigerDownload:
    def test_download_dc_tracts(self):
        """Test downloading DC tracts (smallest state)."""
        from half_america.data import download_state_tracts

        gdf = download_state_tracts("11")

        assert len(gdf) > 0
        assert "GEOID" in gdf.columns
        assert gdf.crs is not None

    def test_dc_tract_count_reasonable(self):
        """Test that DC has reasonable number of tracts."""
        from half_america.data import download_state_tracts

        gdf = download_state_tracts("11")

        # DC should have ~200 tracts
        assert 150 < len(gdf) < 300


class TestCensusFetch:
    def test_fetch_dc_population(self, skip_without_api_key):
        """Test fetching DC population data."""
        from half_america.data import fetch_state_population

        df = fetch_state_population("11")

        assert len(df) > 0
        assert "GEOID" in df.columns
        assert "population" in df.columns

    def test_dc_population_reasonable(self, skip_without_api_key):
        """Test that DC population is reasonable."""
        from half_america.data import fetch_state_population

        df = fetch_state_population("11")
        total_pop = df["population"].sum()

        # DC population should be ~700k
        assert 600_000 < total_pop < 800_000


class TestFullPipeline:
    def test_load_dc_tracts(self, skip_without_api_key):
        """Test loading DC tracts with full pipeline."""
        from half_america.data import load_state_tracts, get_pipeline_summary

        gdf = load_state_tracts("11")
        summary = get_pipeline_summary(gdf)

        assert summary["tract_count"] > 0
        assert summary["total_population"] > 0
        assert summary["crs"] == "EPSG:5070"
```

#### 5. Pytest Configuration
**File**: `pyproject.toml`
**Changes**: Add pytest markers configuration

Add to end of file:
```toml
[tool.pytest.ini_options]
markers = [
    "integration: marks tests as integration tests (deselect with '-m not integration')",
]
```

### Success Criteria:

#### Automated Verification:
- [x] All unit tests pass: `uv run pytest tests/test_cleaning.py tests/test_constants.py -v`
- [x] Type checking passes: `uv run mypy src/ tests/`
- [x] Linting passes: `uv run ruff check src/ tests/`
- [x] Test coverage reasonable: `uv run pytest --cov=half_america` (pytest-cov not installed, skipped)

#### Manual Verification:
- [x] Integration tests pass with API key: `uv run pytest -m integration -v`

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation before proceeding.

---

## Testing Strategy

### Unit Tests:
- Geometry cleaning functions (remove null, fix invalid, quantize)
- Constants validation (FIPS codes, CRS)
- Cache path generation

### Integration Tests (marked, skip by default):
- TIGER/Line download for DC
- Census API fetch for DC
- Full pipeline for DC

### Test Fixtures:
- Synthetic GeoDataFrames with valid/invalid/null geometries
- No external file dependencies for unit tests

## Performance Considerations

- **Memory**: Loading all ~73k tracts uses ~2-4 GB RAM (well within 24GB)
- **Network**: First run downloads ~400 MB of shapefiles + API calls
- **Caching**: All data cached as GeoParquet for fast subsequent loads
- **Rate limiting**: 0.5s delay between Census API calls recommended

## Migration Notes

N/A - This is a greenfield implementation.

## References

- Research document: `thoughts/shared/research/2025-11-20-phase1-data-pipeline.md`
- Roadmap: `ROADMAP.md:11-25`
- Methodology: `METHODOLOGY.md:1-14, 85-89`
- Census TIGER/Line: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html
- Census API: https://www.census.gov/data/developers/data-sets/acs-5year.html
