# Dissolve Selected Tracts Implementation Plan

## Overview

Implement the first Phase 4 milestone: dissolving selected tracts into MultiPolygon geometries. This transforms the optimization output (boolean partition arrays) into merged geometries ready for simplification and TopoJSON export.

## Current State Analysis

### What Exists Now

- **Optimization output:** `SweepResult` contains partition arrays for each λ value (`sweep.py:21-28`)
- **Data loading:** `load_all_tracts()` returns GeoDataFrame with tract geometries (`pipeline.py:48-96`)
- **Geometry validation patterns:** `make_valid()`, `is_valid` checks in `cleaning.py:37-51`
- **Index mapping guarantee:** Partition array indices map 1:1 to GeoDataFrame rows (`adjacency.py:77`)

### What's Missing

- No `postprocess/` module exists
- No dissolve functionality implemented
- No tests for geometry merging operations

### Key Discoveries

- `gdf[partition].geometry.union_all()` is the recommended approach for pure geometry merge
- Census tracts are non-overlapping, enabling `dissolve(method="coverage")` optimization
- Output will be `MultiPolygon` for most λ values due to disconnected "islands"
- Existing test fixtures (`grid_3x3_gdf`, `grid_with_island_gdf`) can test dissolve behavior

## Desired End State

After this plan is complete:

1. A new `src/half_america/postprocess/` module exists with dissolve functionality
2. `dissolve_partition(gdf, partition)` returns a `DissolveResult` with merged geometry
3. `dissolve_all_lambdas(gdf, sweep_result)` batch-processes all λ values
4. Comprehensive unit tests verify correctness and edge cases
5. The dissolve output is ready for the next milestone (Visvalingam-Whyatt simplification)

### Verification

```bash
uv run pytest tests/test_postprocess/ -v  # All tests pass
uv run mypy src/half_america/postprocess/  # No type errors
uv run ruff check src/half_america/postprocess/  # No lint errors
```

## What We're NOT Doing

- Simplification (next milestone)
- TopoJSON export (later milestone)
- CLI command for export (Phase 5)
- Performance optimization beyond using `method="coverage"`
- Island filtering (explicitly preserved per Phase 4 research)

## Implementation Approach

Follow the existing codebase patterns:
- NamedTuple for result types (like `OptimizationResult`)
- Validation patterns from `cleaning.py`
- Test organization matching `test_graph/` structure
- Reuse existing test fixtures where possible

---

## Phase 1: Create Postprocess Module Structure

### Overview

Create the `postprocess/` module with the dissolve functionality.

### Changes Required

#### 1. Module Init
**File:** `src/half_america/postprocess/__init__.py`
**Changes:** Create module with public exports

```python
"""Post-processing for optimization results."""

from half_america.postprocess.dissolve import (
    DissolveResult,
    dissolve_all_lambdas,
    dissolve_partition,
)

__all__ = [
    "DissolveResult",
    "dissolve_partition",
    "dissolve_all_lambdas",
]
```

#### 2. Dissolve Module
**File:** `src/half_america/postprocess/dissolve.py`
**Changes:** Implement dissolve functions

```python
"""Dissolve selected tracts into merged geometries."""

from typing import NamedTuple

import geopandas as gpd
import numpy as np
import shapely
from shapely import MultiPolygon, Polygon

from half_america.optimization.sweep import SweepResult


class DissolveResult(NamedTuple):
    """Result from dissolving selected tracts."""

    geometry: MultiPolygon | Polygon
    num_parts: int  # Number of disconnected regions
    total_area_sqm: float  # Total area in square meters
    num_tracts: int  # Number of tracts dissolved


def dissolve_partition(
    gdf: gpd.GeoDataFrame,
    partition: np.ndarray,
) -> DissolveResult:
    """
    Dissolve selected tracts into a single geometry.

    Args:
        gdf: GeoDataFrame with tract geometries (from load_all_tracts)
        partition: Boolean array where True = selected tract

    Returns:
        DissolveResult with merged geometry and metadata

    Raises:
        ValueError: If partition length doesn't match gdf length
        ValueError: If no tracts are selected (partition is all False)
    """
    # Validate inputs
    if len(partition) != len(gdf):
        raise ValueError(
            f"Partition length ({len(partition)}) doesn't match "
            f"GeoDataFrame length ({len(gdf)})"
        )

    num_selected = partition.sum()
    if num_selected == 0:
        raise ValueError("No tracts selected (partition is all False)")

    # Filter to selected tracts
    selected = gdf[partition]

    # Merge all geometries using coverage union (efficient for non-overlapping)
    geom = selected.geometry.union_all()

    # Validate and fix if needed
    if not geom.is_valid:
        geom = shapely.make_valid(geom)

    # Count parts
    if geom.geom_type == "MultiPolygon":
        num_parts = len(geom.geoms)
    elif geom.geom_type == "Polygon":
        num_parts = 1
    else:
        # GeometryCollection or other - extract polygons
        polygons = [g for g in geom.geoms if g.geom_type in ("Polygon", "MultiPolygon")]
        if polygons:
            geom = shapely.union_all(polygons)
            num_parts = len(geom.geoms) if geom.geom_type == "MultiPolygon" else 1
        else:
            num_parts = 0

    return DissolveResult(
        geometry=geom,
        num_parts=num_parts,
        total_area_sqm=geom.area,
        num_tracts=int(num_selected),
    )


def dissolve_all_lambdas(
    gdf: gpd.GeoDataFrame,
    sweep_result: SweepResult,
    verbose: bool = True,
) -> dict[float, DissolveResult]:
    """
    Dissolve partitions for all lambda values in a sweep result.

    Args:
        gdf: GeoDataFrame with tract geometries (from load_all_tracts)
        sweep_result: SweepResult from sweep_lambda()
        verbose: Print progress messages

    Returns:
        Dictionary mapping lambda values to DissolveResult
    """
    results: dict[float, DissolveResult] = {}

    for lambda_val in sweep_result.lambda_values:
        if verbose:
            print(f"Dissolving λ={lambda_val:.2f}...")

        partition = sweep_result.results[lambda_val].search_result.result.partition
        result = dissolve_partition(gdf, partition)
        results[lambda_val] = result

        if verbose:
            print(f"  {result.num_tracts:,} tracts → {result.num_parts} parts")

    return results
```

### Success Criteria

#### Automated Verification:
- [ ] Module imports without error: `python -c "from half_america.postprocess import dissolve_partition"`
- [ ] Type checking passes: `uv run mypy src/half_america/postprocess/`
- [ ] Linting passes: `uv run ruff check src/half_america/postprocess/`

#### Manual Verification:
- [ ] Code review confirms patterns match existing codebase style

**Implementation Note:** After completing this phase and all automated verification passes, proceed to Phase 2.

---

## Phase 2: Add Unit Tests

### Overview

Create comprehensive unit tests for the dissolve functionality.

### Changes Required

#### 1. Test Module Init
**File:** `tests/test_postprocess/__init__.py`
**Changes:** Create empty init file

```python
"""Tests for postprocess module."""
```

#### 2. Test Fixtures
**File:** `tests/test_postprocess/conftest.py`
**Changes:** Create fixtures for dissolve tests

```python
"""Pytest fixtures for postprocess tests."""

import geopandas as gpd
import numpy as np
import pytest
from shapely.geometry import box


@pytest.fixture
def grid_4x4_gdf() -> gpd.GeoDataFrame:
    """Create a 4x4 grid for testing dissolve with various partition patterns."""
    geometries = []
    populations = []

    cell_size = 1000  # meters
    for row in range(4):
        for col in range(4):
            x0 = col * cell_size
            y0 = row * cell_size
            geometries.append(box(x0, y0, x0 + cell_size, y0 + cell_size))
            populations.append(1000 * (1 + row + col))

    gdf = gpd.GeoDataFrame(
        {"population": populations, "geometry": geometries},
        crs="EPSG:5070",
    )
    gdf["area_sqm"] = gdf.geometry.area
    return gdf


@pytest.fixture
def checkerboard_partition() -> np.ndarray:
    """Checkerboard pattern for 4x4 grid (8 selected, 8 not)."""
    # Creates disconnected regions
    pattern = np.zeros(16, dtype=bool)
    for i in range(16):
        row, col = divmod(i, 4)
        pattern[i] = (row + col) % 2 == 0
    return pattern


@pytest.fixture
def contiguous_partition() -> np.ndarray:
    """Select bottom-left 2x2 quadrant (4 contiguous cells)."""
    pattern = np.zeros(16, dtype=bool)
    pattern[[0, 1, 4, 5]] = True  # Bottom-left 2x2
    return pattern


@pytest.fixture
def single_cell_partition() -> np.ndarray:
    """Select only one cell."""
    pattern = np.zeros(16, dtype=bool)
    pattern[0] = True
    return pattern


@pytest.fixture
def all_selected_partition() -> np.ndarray:
    """Select all cells."""
    return np.ones(16, dtype=bool)


@pytest.fixture
def none_selected_partition() -> np.ndarray:
    """Select no cells."""
    return np.zeros(16, dtype=bool)
```

#### 3. Dissolve Tests
**File:** `tests/test_postprocess/test_dissolve.py`
**Changes:** Create comprehensive dissolve tests

```python
"""Tests for dissolve module."""

import numpy as np
import pytest
from shapely import MultiPolygon, Polygon

from half_america.postprocess.dissolve import DissolveResult, dissolve_partition


class TestDissolvePartition:
    """Tests for dissolve_partition function."""

    def test_contiguous_returns_polygon(self, grid_4x4_gdf, contiguous_partition):
        """Contiguous selection should produce a single Polygon."""
        result = dissolve_partition(grid_4x4_gdf, contiguous_partition)

        assert isinstance(result, DissolveResult)
        assert result.geometry.geom_type == "Polygon"
        assert result.num_parts == 1
        assert result.num_tracts == 4

    def test_checkerboard_returns_multipolygon(self, grid_4x4_gdf, checkerboard_partition):
        """Disconnected selection should produce MultiPolygon."""
        result = dissolve_partition(grid_4x4_gdf, checkerboard_partition)

        assert result.geometry.geom_type == "MultiPolygon"
        assert result.num_parts == 8  # Each cell is isolated
        assert result.num_tracts == 8

    def test_single_cell_returns_polygon(self, grid_4x4_gdf, single_cell_partition):
        """Single cell selection returns that cell's geometry."""
        result = dissolve_partition(grid_4x4_gdf, single_cell_partition)

        assert result.geometry.geom_type == "Polygon"
        assert result.num_parts == 1
        assert result.num_tracts == 1
        # Area should be one cell (1000m x 1000m = 1,000,000 sqm)
        assert result.total_area_sqm == pytest.approx(1_000_000, rel=0.01)

    def test_all_selected_merges_all(self, grid_4x4_gdf, all_selected_partition):
        """Selecting all cells should produce one merged geometry."""
        result = dissolve_partition(grid_4x4_gdf, all_selected_partition)

        assert result.num_parts == 1
        assert result.num_tracts == 16
        # Total area should be 16 cells
        assert result.total_area_sqm == pytest.approx(16_000_000, rel=0.01)

    def test_geometry_is_valid(self, grid_4x4_gdf, checkerboard_partition):
        """Output geometry should always be valid."""
        result = dissolve_partition(grid_4x4_gdf, checkerboard_partition)
        assert result.geometry.is_valid

    def test_area_equals_sum_of_selected(self, grid_4x4_gdf, contiguous_partition):
        """Total area should equal sum of selected tract areas."""
        selected_area = grid_4x4_gdf[contiguous_partition]["area_sqm"].sum()
        result = dissolve_partition(grid_4x4_gdf, contiguous_partition)
        assert result.total_area_sqm == pytest.approx(selected_area, rel=0.001)


class TestDissolvePartitionErrors:
    """Tests for error handling in dissolve_partition."""

    def test_empty_partition_raises(self, grid_4x4_gdf, none_selected_partition):
        """Empty partition should raise ValueError."""
        with pytest.raises(ValueError, match="No tracts selected"):
            dissolve_partition(grid_4x4_gdf, none_selected_partition)

    def test_mismatched_length_raises(self, grid_4x4_gdf):
        """Partition length mismatch should raise ValueError."""
        wrong_size = np.ones(10, dtype=bool)
        with pytest.raises(ValueError, match="doesn't match"):
            dissolve_partition(grid_4x4_gdf, wrong_size)


class TestDissolveWithIsland:
    """Tests using grid_with_island_gdf fixture from test_graph."""

    def test_island_preserved_when_selected(self, grid_with_island_gdf):
        """Island should be preserved as separate part when selected."""
        # Select main grid center (index 4) and island (index 9)
        partition = np.zeros(10, dtype=bool)
        partition[4] = True  # Center of 3x3 grid
        partition[9] = True  # Island

        result = dissolve_partition(grid_with_island_gdf, partition)

        # Should have 2 disconnected parts
        assert result.num_parts == 2
        assert result.num_tracts == 2
```

### Success Criteria

#### Automated Verification:
- [ ] All tests pass: `uv run pytest tests/test_postprocess/ -v`
- [ ] Type checking passes: `uv run mypy tests/test_postprocess/`
- [ ] Linting passes: `uv run ruff check tests/test_postprocess/`

#### Manual Verification:
- [ ] Test coverage is reasonable for the dissolve functionality
- [ ] Edge cases are adequately tested

**Implementation Note:** After completing this phase and all automated verification passes, proceed to Phase 3.

---

## Phase 3: Integration Verification

### Overview

Verify the dissolve module works correctly with real sweep results.

### Changes Required

#### 1. Integration Test
**File:** `tests/test_postprocess/test_dissolve.py` (append to existing)
**Changes:** Add integration test class

```python
class TestDissolveAllLambdas:
    """Tests for dissolve_all_lambdas batch function."""

    def test_processes_all_lambda_values(self, grid_4x4_gdf):
        """Should process all lambda values from sweep result."""
        from half_america.graph.pipeline import load_graph_data
        from half_america.optimization import sweep_lambda

        # Build graph and run mini sweep
        graph_data = load_graph_data(grid_4x4_gdf)
        sweep_result = sweep_lambda(
            graph_data,
            lambda_values=[0.0, 0.5],
            verbose=False,
        )

        from half_america.postprocess.dissolve import dissolve_all_lambdas

        results = dissolve_all_lambdas(grid_4x4_gdf, sweep_result, verbose=False)

        assert len(results) == 2
        assert 0.0 in results
        assert 0.5 in results

        for lambda_val, result in results.items():
            assert isinstance(result, DissolveResult)
            assert result.geometry.is_valid
            assert result.num_tracts > 0
```

### Success Criteria

#### Automated Verification:
- [ ] Integration test passes: `uv run pytest tests/test_postprocess/test_dissolve.py::TestDissolveAllLambdas -v`
- [ ] Full test suite passes: `uv run pytest -v`
- [ ] Type checking passes: `uv run mypy src/`

#### Manual Verification:
- [ ] Review dissolve output for a real sweep result looks reasonable
- [ ] Confirm num_parts decreases as λ increases (smoother boundaries = fewer islands)

**Implementation Note:** After completing this phase and all verification passes, the dissolve implementation is complete and ready for the next Phase 4 milestone (Visvalingam-Whyatt simplification).

---

## Testing Strategy

### Unit Tests
- Basic dissolve functionality (contiguous, disconnected, single cell)
- Edge cases (empty partition, full partition, mismatched lengths)
- Geometry validity verification
- Area preservation verification

### Integration Tests
- End-to-end with real sweep results
- Batch processing multiple lambda values

### Manual Testing Steps
1. Load a real sweep result and dissolve a few lambda values
2. Visually inspect that low-λ has many parts, high-λ has fewer
3. Verify dissolved geometry can be plotted with matplotlib/geopandas

## Performance Considerations

- `union_all()` is O(n log n) using cascaded union algorithm
- Census tracts are non-overlapping, which is efficient for union operations
- No additional optimization needed for ~30,000 tracts per partition
- If performance becomes an issue, consider `dissolve(method="coverage")` which is optimized for non-overlapping polygons

## References

- Research document: `thoughts/shared/research/2025-11-21-dissolve-tracts-implementation.md`
- Phase 4 research: `thoughts/shared/research/2025-11-21-phase4-post-processing.md`
- ROADMAP milestone: `ROADMAP.md:75`
- Similar pattern: `src/half_america/optimization/solver.py` (NamedTuple result type)
- Validation pattern: `src/half_america/data/cleaning.py:37-51` (make_valid usage)
