---
date: 2025-11-20T00:00:00-08:00
researcher: Claude
git_commit: b99adbd87ff997309b4561afbe26d13e5eaeddb4
branch: master
repository: half_america
topic: "Phase 1: Data Pipeline Implementation Research"
tags: [research, codebase, data-pipeline, census, tiger-line, geopandas, caching]
status: complete
last_updated: 2025-11-20
last_updated_by: Claude
---

# Research: Phase 1 Data Pipeline Implementation

**Date**: 2025-11-20
**Researcher**: Claude
**Git Commit**: b99adbd87ff997309b4561afbe26d13e5eaeddb4
**Branch**: master
**Repository**: half_america

## Research Question

What is needed to implement Phase 1: Data Pipeline as defined in ROADMAP.md? This includes:
- Adding production dependencies
- Downloading TIGER/Line Shapefiles
- Fetching ACS 5-Year population estimates
- Implementing geometry cleaning
- Creating a data caching layer
- Writing unit tests

## Summary

Phase 1 requires building a complete data acquisition and preprocessing pipeline for ~73,000 US Census Tracts. The implementation should use:

- **cenpy** for Census API access (ACS 5-Year population estimates)
- **geopandas/shapely** for loading TIGER/Line shapefiles and geometry operations
- **topojson** for coordinate quantization and topology preservation
- **GeoParquet + requests-cache** for data caching

The current codebase is in skeleton phase with no data pipeline code yet. All Phase 1 milestones are unchecked in ROADMAP.md.

## Detailed Findings

### Current Codebase Status

The project is in initial skeleton phase:

| Component | Status |
|-----------|--------|
| `src/half_america/__init__.py` | Exists (placeholder) |
| `tests/test_sanity.py` | Exists (sanity test only) |
| `data/` directory | Does not exist |
| `cache/` directory | Does not exist |
| Production dependencies | None added yet |

---

### 1. Production Dependencies to Add

Based on METHODOLOGY.md and research findings, add to `pyproject.toml`:

```toml
dependencies = [
    # Data ingestion
    "pandas>=2.0",
    "cenpy>=1.0",

    # Spatial operations
    "geopandas>=0.14",
    "shapely>=2.0",
    "libpysal>=4.9",

    # TopoJSON/Topology
    "topojson>=1.6",

    # Caching
    "requests-cache>=1.1",

    # File formats
    "pyarrow>=14.0",  # Required for GeoParquet
]
```

**Note**: PyMaxFlow is for Phase 3 (Optimization Engine), not Phase 1.

---

### 2. TIGER/Line Shapefile Downloads

**Source URL Pattern**:
```
https://www2.census.gov/geo/tiger/TIGER2024/TRACT/tl_2024_[FIPS]_tract.zip
```

**File Structure**:
- Files are state-level (one ZIP per state)
- File naming: `tl_2024_06_tract.zip` (California = FIPS 06)
- Each ZIP contains: `.shp`, `.shx`, `.dbf`, `.prj`, `.cpg`, `.xml` files

**Contiguous US FIPS Codes** (48 states + DC = 49 files):
```python
CONTIGUOUS_US_FIPS = [
    '01', '04', '05', '06', '08', '09', '10', '11', '12', '13',
    '16', '17', '18', '19', '20', '21', '22', '23', '24', '25',
    '26', '27', '28', '29', '30', '31', '32', '33', '34', '35',
    '36', '37', '38', '39', '40', '41', '42', '44', '45', '46',
    '47', '48', '49', '50', '51', '53', '54', '55', '56'
]
# Excludes: Alaska (02), Hawaii (15)
```

**Expected File Sizes**:
- Total for contiguous US: ~350-400 MB compressed
- Largest states: California, Texas (~31 MB each)
- Smallest: DC, Rhode Island (<1 MB each)

**Download Implementation**:
```python
import geopandas as gpd
from pathlib import Path

def download_tract_shapefiles(
    state_fips: str,
    year: int = 2024,
    cache_dir: Path = Path("data/raw/tiger")
) -> gpd.GeoDataFrame:
    """Download TIGER/Line tract shapefile for a state."""
    cache_path = cache_dir / f"tl_{year}_{state_fips}_tract.parquet"

    if cache_path.exists():
        return gpd.read_parquet(cache_path)

    url = f"https://www2.census.gov/geo/tiger/TIGER{year}/TRACT/tl_{year}_{state_fips}_tract.zip"
    gdf = gpd.read_file(url)

    cache_dir.mkdir(parents=True, exist_ok=True)
    gdf.to_parquet(cache_path)

    return gdf
```

---

### 3. Census API Population Data (cenpy)

**Key Variable**: `B01003_001E` (Total Population, ACS 5-Year Estimate)

**API Key Requirement**:
- Get key at: https://api.census.gov/data/key_signup.html
- Set environment variable: `CENSUS_API_KEY`
- Without key: ~500 requests/day limit (insufficient for all tracts)

**Data Format**:
- Returns all values as strings (must convert to numeric)
- GEOID format: `state + county + tract` (e.g., "06037101110")

**Implementation Pattern**:
```python
import cenpy
import pandas as pd
import os

def fetch_tract_population(state_fips: str, year: int = 2022) -> pd.DataFrame:
    """Fetch population for all tracts in a state."""
    conn = cenpy.remote.APIConnection(f"ACSDT5Y{year}")

    data = conn.query(
        cols=["NAME", "B01003_001E", "GEO_ID"],
        geo_unit="tract:*",
        geo_filter={"state": state_fips, "county": "*"}
    )

    # Convert population to numeric
    data["population"] = pd.to_numeric(data["B01003_001E"], errors="coerce")

    # Create GEOID for joining with TIGER data
    data["GEOID"] = data["state"] + data["county"] + data["tract"]

    return data
```

**Rate Limiting Best Practices**:
- Add 0.5s delay between state requests
- Cache results aggressively (data updates annually)
- Implement retry logic for API errors

---

### 4. Geometry Cleaning Pipeline

Based on METHODOLOGY.md requirements:

#### 4.1 Fix Self-Intersections

Use `shapely.make_valid()` (preferred over `buffer(0)`):

```python
import shapely
import geopandas as gpd

def fix_invalid_geometries(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Fix self-intersecting and invalid geometries."""
    gdf = gdf.copy()

    # Check for invalid geometries
    invalid_count = (~gdf.is_valid).sum()
    if invalid_count > 0:
        print(f"Fixing {invalid_count} invalid geometries")
        gdf["geometry"] = shapely.make_valid(gdf["geometry"])

    return gdf
```

#### 4.2 Coordinate Quantization (TopoJSON)

Use `shapely.set_precision()` for coordinate snapping:

```python
import shapely

def quantize_coordinates(
    gdf: gpd.GeoDataFrame,
    grid_size: float = 0.01  # 1cm for projected CRS in meters
) -> gpd.GeoDataFrame:
    """Quantize coordinates to integer grid."""
    gdf = gdf.copy()
    gdf["geometry"] = shapely.set_precision(gdf["geometry"], grid_size=grid_size)

    # Re-validate after quantization (can introduce invalidity)
    invalid_mask = ~gdf.is_valid
    if invalid_mask.any():
        gdf.loc[invalid_mask, "geometry"] = shapely.make_valid(
            gdf.loc[invalid_mask, "geometry"]
        )

    return gdf
```

For TopoJSON-based quantization (better for web output):

```python
import topojson as tp

def create_topojson(gdf: gpd.GeoDataFrame) -> tp.Topology:
    """Create TopoJSON with quantization to close micro-gaps."""
    return tp.Topology(
        gdf,
        prequantize=True,      # Close micro-gaps before topology detection
        topoquantize=1e5,      # 100k grid points (good balance)
        toposimplify=False,    # Don't simplify yet (Phase 4)
    )
```

#### 4.3 Micro-Gap/Sliver Detection

```python
def check_topology_gaps(gdf: gpd.GeoDataFrame, tolerance: float = 1e-6) -> dict:
    """Check for gaps between adjacent polygons."""
    total_individual_area = gdf.geometry.area.sum()
    union_area = gdf.union_all().area
    overlap_area = total_individual_area - union_area

    return {
        "total_individual_area": total_individual_area,
        "union_area": union_area,
        "overlap_area": overlap_area,
        "has_overlaps": overlap_area > tolerance,
    }
```

#### 4.4 Complete Cleaning Pipeline

```python
import geopandas as gpd
import shapely

def clean_census_tracts(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Complete geometry cleaning pipeline for Census Tracts."""
    gdf = gdf.copy()

    # 1. Remove null/empty geometries
    null_mask = gdf.geometry.isna() | gdf.geometry.is_empty
    if null_mask.any():
        print(f"Removing {null_mask.sum()} null/empty geometries")
        gdf = gdf[~null_mask]

    # 2. Project to Albers Equal Area (EPSG:5070) for US
    if gdf.crs != "EPSG:5070":
        gdf = gdf.to_crs("EPSG:5070")

    # 3. Fix invalid geometries
    invalid_count = (~gdf.is_valid).sum()
    if invalid_count > 0:
        print(f"Fixing {invalid_count} invalid geometries")
        gdf["geometry"] = shapely.make_valid(gdf["geometry"])

    # 4. Quantize coordinates (1cm precision for meters-based CRS)
    gdf["geometry"] = shapely.set_precision(gdf["geometry"], grid_size=0.01)

    # 5. Re-validate after quantization
    invalid_after = (~gdf.is_valid).sum()
    if invalid_after > 0:
        gdf["geometry"] = shapely.make_valid(gdf["geometry"])

    # 6. Normalize coordinate order
    gdf["geometry"] = gdf.normalize()

    # 7. Calculate area (for Phase 2 graph construction)
    gdf["area_sqm"] = gdf.geometry.area

    return gdf
```

---

### 5. Data Caching Layer

**Recommended Stack**:
- **requests-cache**: For Census API HTTP caching
- **GeoParquet**: For processed GeoDataFrame caching
- **Repository pattern**: For clean data access abstraction

**Directory Structure**:
```
data/
├── cache/
│   ├── raw/                    # Cached API responses / shapefiles
│   │   ├── tiger/              # TIGER/Line shapefiles (as parquet)
│   │   └── census/             # Census population data
│   ├── processed/              # Cleaned/merged data
│   └── requests_cache.sqlite   # requests-cache database
└── output/                     # Final outputs
```

**Cache Implementation**:

```python
# src/half_america/data/cache.py
from pathlib import Path
import requests_cache
from datetime import timedelta

class CacheConfig:
    """Central cache configuration."""
    BASE_DIR = Path("data/cache")
    RAW_DIR = BASE_DIR / "raw"
    TIGER_DIR = RAW_DIR / "tiger"
    CENSUS_DIR = RAW_DIR / "census"
    PROCESSED_DIR = BASE_DIR / "processed"

    # Census data is updated annually - cache for 30 days
    API_TTL_DAYS = 30

    @classmethod
    def setup(cls):
        """Initialize cache directories and requests-cache."""
        cls.TIGER_DIR.mkdir(parents=True, exist_ok=True)
        cls.CENSUS_DIR.mkdir(parents=True, exist_ok=True)
        cls.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

        # Install requests-cache for Census API
        requests_cache.install_cache(
            str(cls.BASE_DIR / "requests_cache"),
            backend="sqlite",
            expire_after=timedelta(days=cls.API_TTL_DAYS),
            stale_if_error=True,
        )
```

**Repository Pattern for Data Access**:

```python
# src/half_america/data/repository.py
from abc import ABC, abstractmethod
import geopandas as gpd
from pathlib import Path

class TractRepository(ABC):
    """Abstract interface for tract data access."""

    @abstractmethod
    def get_geometries(self, state_fips: str) -> gpd.GeoDataFrame:
        """Get tract geometries for a state."""
        pass

    @abstractmethod
    def get_population(self, state_fips: str) -> gpd.GeoDataFrame:
        """Get tract population for a state."""
        pass


class CachedTractRepository(TractRepository):
    """Repository with file-based caching."""

    def __init__(self, cache_dir: Path):
        self._cache_dir = cache_dir

    def get_geometries(self, state_fips: str) -> gpd.GeoDataFrame:
        cache_path = self._cache_dir / "tiger" / f"tracts_{state_fips}.parquet"

        if cache_path.exists():
            return gpd.read_parquet(cache_path)

        # Download from Census
        url = f"https://www2.census.gov/geo/tiger/TIGER2024/TRACT/tl_2024_{state_fips}_tract.zip"
        gdf = gpd.read_file(url)

        cache_path.parent.mkdir(parents=True, exist_ok=True)
        gdf.to_parquet(cache_path)

        return gdf
```

---

### 6. Unit Test Strategy

**Test Categories**:

1. **Data Download Tests** (integration, optional skip)
   - Test single state download
   - Verify expected columns exist
   - Mock API responses for CI

2. **Geometry Cleaning Tests**
   - Test self-intersection fix
   - Test quantization preserves topology
   - Test null/empty geometry removal

3. **Cache Tests**
   - Test cache hit/miss behavior
   - Test cache invalidation

4. **Integration Tests**
   - Full pipeline for single small state (DC, Rhode Island)
   - Verify output schema

**Example Test Structure**:

```python
# tests/test_data_pipeline.py
import pytest
import geopandas as gpd
from half_america.data.repository import CachedTractRepository
from half_america.data.cleaning import clean_census_tracts

class TestGeometryCleaning:
    def test_fixes_invalid_geometry(self):
        """Test that invalid geometries are fixed."""
        # Create intentionally invalid geometry
        ...

    def test_quantization_preserves_count(self):
        """Test that quantization doesn't lose features."""
        ...

    def test_removes_empty_geometries(self):
        """Test that empty geometries are removed."""
        ...


@pytest.mark.integration
class TestDataDownload:
    def test_download_dc_tracts(self):
        """Test downloading DC tracts (smallest state)."""
        repo = CachedTractRepository(Path("data/cache/raw"))
        gdf = repo.get_geometries("11")  # DC FIPS code

        assert len(gdf) > 0
        assert "GEOID" in gdf.columns
        assert gdf.crs is not None
```

---

## Architecture Insights

### Recommended Module Structure

```
src/half_america/
├── __init__.py
├── config.py              # Configuration (paths, constants)
├── data/
│   ├── __init__.py
│   ├── cache.py           # Cache configuration
│   ├── repository.py      # Data access abstraction
│   ├── tiger.py           # TIGER/Line download logic
│   ├── census.py          # Census API client (cenpy wrapper)
│   └── cleaning.py        # Geometry cleaning functions
└── cli.py                 # CLI entry point
```

### Key Design Decisions

1. **State-by-state processing**: Process one state at a time to manage memory
2. **Cache-first architecture**: Always check cache before network requests
3. **Idempotent operations**: Running pipeline twice produces same result
4. **Separation of concerns**: Download, clean, and cache as separate steps

---

## Code References

- `ROADMAP.md:11-26` - Phase 1 milestones definition
- `METHODOLOGY.md:1-14` - Data sources and preprocessing requirements
- `METHODOLOGY.md:85-89` - Implementation stack specification
- `pyproject.toml:11` - Current empty dependencies array
- `src/half_america/__init__.py` - Current placeholder module

---

## Open Questions

1. **Year selection**: Should we use 2024 TIGER/Line with 2022 ACS 5-Year (most recent stable), or wait for 2023 ACS release?

2. **Territory handling**: Include Puerto Rico (72) and other territories, or contiguous US only?
RESPONSE: conterminous US only (this should be noted in `METHODOLOGY.md`)

3. **Memory management**: For all ~73,000 tracts merged, expected memory usage is 2-4 GB. Should we implement chunked processing?

4. **API key storage**: Use environment variable, `.env` file, or config file for Census API key?
RESPONSE: `.env` file

5. **Test data fixtures**: Create small fixture files (e.g., single county) for fast unit tests?

---

## Implementation Checklist

Based on ROADMAP.md Phase 1 milestones:

- [ ] Add production dependencies to `pyproject.toml`
- [ ] Implement TIGER/Line download function
- [ ] Implement Census API population fetch
- [ ] Implement geometry cleaning pipeline:
  - [ ] Coordinate quantization
  - [ ] Self-intersection fix (`make_valid`)
  - [ ] Micro-gap elimination
- [ ] Create cache layer with directory structure
- [ ] Write unit tests for each component
- [ ] Integration test with small state (DC)
