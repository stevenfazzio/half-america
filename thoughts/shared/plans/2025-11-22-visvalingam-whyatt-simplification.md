# Visvalingam-Whyatt Simplification Implementation Plan

## Overview

Implement geometry simplification for web performance as part of Phase 4 post-processing. This adds a `simplify.py` module that reduces vertex counts by ~98% while preserving visual fidelity, preparing geometries for efficient TopoJSON export.

## Current State Analysis

**Existing infrastructure:**
- Dissolve pipeline complete at `src/half_america/postprocess/dissolve.py`
- `DissolveResult` NamedTuple returns `MultiPolygon | Polygon` with metadata
- Test fixtures in `tests/test_postprocess/conftest.py` provide grid patterns
- GEOS 3.13.1 and Shapely 2.1.2 are installed (required for `coverage_simplify`)

**Key discoveries:**
- After dissolve, we have ~2,780 disconnected polygon parts (not adjacent tracts)
- Disconnected parts mean `coverage_simplify()` provides no benefit over `simplify()`
- The simpler `shapely.simplify()` with `preserve_topology=True` is sufficient
- 500m tolerance achieves 98.3% vertex reduction (10.4M → 175K vertices)

## Desired End State

A `simplify.py` module that:
1. Accepts dissolved geometry and returns simplified geometry with reduction stats
2. Provides a batch function to simplify all lambda values from a sweep
3. Integrates seamlessly into the post-processing pipeline

**Verification:**
- All existing tests pass: `uv run pytest`
- New unit tests pass: `uv run pytest tests/test_postprocess/test_simplify.py -v`
- Type checking passes: `uv run mypy src/`
- Linting passes: `uv run ruff check src/ tests/`

## What We're NOT Doing

- TopoJSON export (next milestone)
- CRS reprojection to WGS84 (handled by export module)
- CLI integration (handled by export module)
- Coordinate precision truncation (handled by export module)
- Per-lambda tolerance variation (research concluded: use consistent 500m for all)

## Implementation Approach

Follow the established pattern from `dissolve.py`:
1. Create a `SimplifyResult` NamedTuple with geometry and reduction metrics
2. Implement a single-geometry function `simplify_geometry()`
3. Implement a batch function `simplify_all_lambdas()`
4. Update `__init__.py` exports
5. Add comprehensive unit tests

## Phase 1: Create simplify.py Module

### Overview
Create the core simplification module with `SimplifyResult` and `simplify_geometry()` function.

### Changes Required:

#### 1. Create src/half_america/postprocess/simplify.py
**File**: `src/half_america/postprocess/simplify.py`
**Changes**: New file

```python
"""Geometry simplification for web performance."""

from typing import NamedTuple

import shapely
from shapely import MultiPolygon, Polygon


class SimplifyResult(NamedTuple):
    """Result from simplifying a dissolved geometry."""

    geometry: MultiPolygon | Polygon
    original_vertex_count: int
    simplified_vertex_count: int
    reduction_percent: float


# Default tolerance in meters (EPSG:5070)
# 500m provides 98.3% vertex reduction with good visual fidelity
DEFAULT_TOLERANCE = 500.0


def simplify_geometry(
    geometry: MultiPolygon | Polygon,
    tolerance: float = DEFAULT_TOLERANCE,
    preserve_topology: bool = True,
) -> SimplifyResult:
    """
    Simplify a dissolved geometry for web display.

    Uses Douglas-Peucker algorithm via shapely.simplify() with topology
    preservation. This is appropriate for dissolved geometries where
    polygon parts are disconnected (not sharing edges).

    Parameters
    ----------
    geometry : MultiPolygon | Polygon
        Dissolved geometry from dissolve_partition()
    tolerance : float
        Simplification tolerance in CRS units (meters for EPSG:5070).
        Default is 500m which provides ~98% vertex reduction.
    preserve_topology : bool
        If True, ensures valid output geometry (no self-intersections).
        Default is True.

    Returns
    -------
    SimplifyResult
        Simplified geometry with reduction statistics

    Examples
    --------
    >>> from half_america.postprocess import dissolve_partition, simplify_geometry
    >>> dissolve_result = dissolve_partition(gdf, partition)
    >>> simplify_result = simplify_geometry(dissolve_result.geometry)
    >>> print(f"Reduced by {simplify_result.reduction_percent:.1f}%")
    """
    original_count = shapely.get_num_coordinates(geometry)

    simplified = shapely.simplify(
        geometry,
        tolerance=tolerance,
        preserve_topology=preserve_topology,
    )

    simplified_count = shapely.get_num_coordinates(simplified)
    reduction = (
        (1 - simplified_count / original_count) * 100 if original_count > 0 else 0.0
    )

    return SimplifyResult(
        geometry=simplified,
        original_vertex_count=original_count,
        simplified_vertex_count=simplified_count,
        reduction_percent=reduction,
    )
```

### Success Criteria:

#### Automated Verification:
- [ ] File exists: `ls src/half_america/postprocess/simplify.py`
- [ ] Module imports without error: `uv run python -c "from half_america.postprocess.simplify import SimplifyResult, simplify_geometry"`
- [ ] Type checking passes: `uv run mypy src/half_america/postprocess/simplify.py`
- [ ] Linting passes: `uv run ruff check src/half_america/postprocess/simplify.py`

#### Manual Verification:
- [ ] Code matches the pattern established in `dissolve.py`

**Implementation Note**: After completing this phase and all automated verification passes, proceed to Phase 2.

---

## Phase 2: Add simplify_all_lambdas Batch Function

### Overview
Add the batch function to simplify all lambda values from a sweep result, mirroring `dissolve_all_lambdas()`.

### Changes Required:

#### 1. Extend src/half_america/postprocess/simplify.py
**File**: `src/half_america/postprocess/simplify.py`
**Changes**: Add batch function and necessary imports

Add these imports at the top:
```python
from half_america.postprocess.dissolve import DissolveResult
```

Add this function at the bottom:
```python
def simplify_all_lambdas(
    dissolve_results: dict[float, DissolveResult],
    tolerance: float = DEFAULT_TOLERANCE,
    verbose: bool = True,
) -> dict[float, SimplifyResult]:
    """
    Simplify dissolved geometries for all lambda values.

    Parameters
    ----------
    dissolve_results : dict[float, DissolveResult]
        Dictionary mapping lambda values to DissolveResult from dissolve_all_lambdas()
    tolerance : float
        Simplification tolerance in CRS units (meters for EPSG:5070)
    verbose : bool
        Print progress messages

    Returns
    -------
    dict[float, SimplifyResult]
        Dictionary mapping lambda values to SimplifyResult

    Examples
    --------
    >>> dissolve_results = dissolve_all_lambdas(gdf, sweep_result)
    >>> simplify_results = simplify_all_lambdas(dissolve_results)
    """
    results: dict[float, SimplifyResult] = {}

    for lambda_val, dissolve_result in dissolve_results.items():
        if verbose:
            print(f"Simplifying λ={lambda_val:.2f}...")

        result = simplify_geometry(dissolve_result.geometry, tolerance=tolerance)
        results[lambda_val] = result

        if verbose:
            print(
                f"  {result.original_vertex_count:,} → {result.simplified_vertex_count:,} vertices "
                f"({result.reduction_percent:.1f}% reduction)"
            )

    return results
```

### Success Criteria:

#### Automated Verification:
- [ ] Module imports without error: `uv run python -c "from half_america.postprocess.simplify import simplify_all_lambdas"`
- [ ] Type checking passes: `uv run mypy src/half_america/postprocess/simplify.py`
- [ ] Linting passes: `uv run ruff check src/half_america/postprocess/simplify.py`

#### Manual Verification:
- [ ] Function signature mirrors `dissolve_all_lambdas()` pattern

**Implementation Note**: After completing this phase and all automated verification passes, proceed to Phase 3.

---

## Phase 3: Update Module Exports

### Overview
Update `__init__.py` to export the new simplify functions.

### Changes Required:

#### 1. Update src/half_america/postprocess/__init__.py
**File**: `src/half_america/postprocess/__init__.py`
**Changes**: Add simplify exports

```python
"""Post-processing for optimization results."""

from half_america.postprocess.dissolve import (
    DissolveResult,
    dissolve_all_lambdas,
    dissolve_partition,
)
from half_america.postprocess.simplify import (
    DEFAULT_TOLERANCE,
    SimplifyResult,
    simplify_all_lambdas,
    simplify_geometry,
)

__all__ = [
    # Dissolve
    "DissolveResult",
    "dissolve_partition",
    "dissolve_all_lambdas",
    # Simplify
    "DEFAULT_TOLERANCE",
    "SimplifyResult",
    "simplify_geometry",
    "simplify_all_lambdas",
]
```

### Success Criteria:

#### Automated Verification:
- [ ] All exports work: `uv run python -c "from half_america.postprocess import SimplifyResult, simplify_geometry, simplify_all_lambdas, DEFAULT_TOLERANCE"`
- [ ] Type checking passes: `uv run mypy src/half_america/postprocess/__init__.py`
- [ ] Linting passes: `uv run ruff check src/half_america/postprocess/__init__.py`

#### Manual Verification:
- [ ] Exports follow established pattern (dissolve grouped, simplify grouped)

**Implementation Note**: After completing this phase and all automated verification passes, proceed to Phase 4.

---

## Phase 4: Add Unit Tests

### Overview
Add comprehensive unit tests following the pattern established in `test_dissolve.py`.

### Changes Required:

#### 1. Create tests/test_postprocess/test_simplify.py
**File**: `tests/test_postprocess/test_simplify.py`
**Changes**: New file

```python
"""Tests for simplify module."""

import numpy as np
import pytest
import shapely
from shapely import MultiPolygon, Polygon
from shapely.geometry import box

from half_america.postprocess.dissolve import DissolveResult
from half_america.postprocess.simplify import (
    DEFAULT_TOLERANCE,
    SimplifyResult,
    simplify_all_lambdas,
    simplify_geometry,
)


class TestSimplifyGeometry:
    """Tests for simplify_geometry function."""

    def test_returns_simplify_result(self, complex_polygon):
        """Should return a SimplifyResult with all fields."""
        result = simplify_geometry(complex_polygon)

        assert isinstance(result, SimplifyResult)
        assert isinstance(result.geometry, (Polygon, MultiPolygon))
        assert isinstance(result.original_vertex_count, int)
        assert isinstance(result.simplified_vertex_count, int)
        assert isinstance(result.reduction_percent, float)

    def test_reduces_vertex_count(self, complex_polygon):
        """Simplification should reduce vertex count."""
        result = simplify_geometry(complex_polygon, tolerance=100.0)

        assert result.simplified_vertex_count < result.original_vertex_count
        assert result.reduction_percent > 0

    def test_preserves_validity(self, complex_polygon):
        """Output geometry should always be valid."""
        result = simplify_geometry(complex_polygon)
        assert result.geometry.is_valid

    def test_simple_geometry_minimal_change(self, simple_square):
        """Simple geometry should have minimal simplification."""
        result = simplify_geometry(simple_square, tolerance=10.0)

        # Square has 5 coordinates (4 corners + closing point)
        assert result.original_vertex_count == 5
        # Should remain mostly unchanged (can't simplify a square much)
        assert result.simplified_vertex_count >= 4

    def test_multipolygon_input(self, disconnected_multipolygon):
        """Should handle MultiPolygon input correctly."""
        result = simplify_geometry(disconnected_multipolygon)

        assert isinstance(result.geometry, MultiPolygon)
        # Both parts should be preserved
        assert len(result.geometry.geoms) == 2

    def test_custom_tolerance(self, complex_polygon):
        """Higher tolerance should result in more reduction."""
        result_low = simplify_geometry(complex_polygon, tolerance=50.0)
        result_high = simplify_geometry(complex_polygon, tolerance=500.0)

        assert result_high.simplified_vertex_count <= result_low.simplified_vertex_count
        assert result_high.reduction_percent >= result_low.reduction_percent

    def test_default_tolerance(self):
        """Default tolerance should be 500m."""
        assert DEFAULT_TOLERANCE == 500.0

    def test_preserve_topology_true(self, complex_polygon):
        """preserve_topology=True should prevent self-intersections."""
        result = simplify_geometry(
            complex_polygon, tolerance=1000.0, preserve_topology=True
        )
        assert result.geometry.is_valid
        assert not result.geometry.is_empty

    def test_empty_geometry_handling(self):
        """Empty geometry should return zero reduction."""
        empty = Polygon()
        result = simplify_geometry(empty)

        assert result.original_vertex_count == 0
        assert result.simplified_vertex_count == 0
        assert result.reduction_percent == 0.0


class TestSimplifyAllLambdas:
    """Tests for simplify_all_lambdas batch function."""

    def test_processes_all_lambda_values(self, sample_dissolve_results):
        """Should process all lambda values from dissolve results."""
        results = simplify_all_lambdas(sample_dissolve_results, verbose=False)

        assert len(results) == len(sample_dissolve_results)
        for lambda_val in sample_dissolve_results:
            assert lambda_val in results
            assert isinstance(results[lambda_val], SimplifyResult)

    def test_all_results_valid(self, sample_dissolve_results):
        """All simplified geometries should be valid."""
        results = simplify_all_lambdas(sample_dissolve_results, verbose=False)

        for result in results.values():
            assert result.geometry.is_valid

    def test_custom_tolerance(self, sample_dissolve_results):
        """Should apply custom tolerance to all geometries."""
        results_low = simplify_all_lambdas(
            sample_dissolve_results, tolerance=50.0, verbose=False
        )
        results_high = simplify_all_lambdas(
            sample_dissolve_results, tolerance=500.0, verbose=False
        )

        for lambda_val in sample_dissolve_results:
            assert (
                results_high[lambda_val].simplified_vertex_count
                <= results_low[lambda_val].simplified_vertex_count
            )


# Fixtures specific to simplify tests


@pytest.fixture
def simple_square() -> Polygon:
    """Create a simple square polygon."""
    return box(0, 0, 1000, 1000)


@pytest.fixture
def complex_polygon() -> Polygon:
    """Create a polygon with many vertices for simplification testing.

    Creates a jagged polygon with 40+ vertices that can be meaningfully simplified.
    """
    coords = [(0, 0)]
    # Create jagged edge along top
    for i in range(20):
        x = i * 100
        y = 1000 + (50 if i % 2 == 0 else 0)  # Zigzag
        coords.append((x, y))
    coords.append((2000, 1000))
    # Create jagged edge along right
    for i in range(10):
        x = 2000 + (50 if i % 2 == 0 else 0)
        y = 1000 - i * 100
        coords.append((x, y))
    coords.append((2000, 0))
    coords.append((0, 0))  # Close

    return Polygon(coords)


@pytest.fixture
def disconnected_multipolygon() -> MultiPolygon:
    """Create two disconnected squares."""
    square1 = box(0, 0, 1000, 1000)
    square2 = box(5000, 5000, 6000, 6000)  # Far away
    return MultiPolygon([square1, square2])


@pytest.fixture
def sample_dissolve_results() -> dict[float, DissolveResult]:
    """Create sample dissolve results for testing simplify_all_lambdas."""
    # Create a simple complex geometry
    coords = [(0, 0)]
    for i in range(20):
        coords.append((i * 100, 1000 + (50 if i % 2 == 0 else 0)))
    coords.append((2000, 1000))
    coords.append((2000, 0))
    coords.append((0, 0))
    geom = Polygon(coords)

    return {
        0.0: DissolveResult(
            geometry=geom,
            num_parts=1,
            total_area_sqm=geom.area,
            num_tracts=10,
        ),
        0.5: DissolveResult(
            geometry=geom,
            num_parts=1,
            total_area_sqm=geom.area,
            num_tracts=10,
        ),
        0.9: DissolveResult(
            geometry=geom,
            num_parts=1,
            total_area_sqm=geom.area,
            num_tracts=10,
        ),
    }
```

### Success Criteria:

#### Automated Verification:
- [ ] All tests pass: `uv run pytest tests/test_postprocess/test_simplify.py -v`
- [ ] Type checking passes: `uv run mypy tests/test_postprocess/test_simplify.py`
- [ ] Linting passes: `uv run ruff check tests/test_postprocess/test_simplify.py`
- [ ] Full test suite passes: `uv run pytest`

#### Manual Verification:
- [ ] Test coverage mirrors `test_dissolve.py` patterns

**Implementation Note**: After completing this phase and all automated verification passes, proceed to Phase 5.

---

## Phase 5: Update ROADMAP.md

### Overview
Mark the Visvalingam-Whyatt simplification milestone as complete.

### Changes Required:

#### 1. Update ROADMAP.md
**File**: `ROADMAP.md`
**Changes**: Check the simplification milestone

```markdown
## Phase 4: Post-Processing

Transform optimization output into web-ready geometries.

### Milestones

- [x] Dissolve selected tracts into MultiPolygon geometries (shapely.ops.unary_union)
- [x] Apply Visvalingam-Whyatt simplification for web performance
- [ ] Export as TopoJSON
- [ ] Generate pre-computed geometry files for all λ values
- [ ] Validate output geometries
```

### Success Criteria:

#### Automated Verification:
- [ ] File is valid markdown (no syntax errors)
- [ ] Full test suite still passes: `uv run pytest`

#### Manual Verification:
- [ ] Roadmap accurately reflects project state

**Implementation Note**: After completing this phase, the implementation is complete.

---

## Testing Strategy

### Unit Tests:
- `SimplifyResult` NamedTuple fields are correct types
- `simplify_geometry()` reduces vertex count
- `simplify_geometry()` preserves geometry validity
- `simplify_geometry()` handles Polygon and MultiPolygon inputs
- `simplify_geometry()` handles empty geometry edge case
- `simplify_all_lambdas()` processes all lambda values
- `simplify_all_lambdas()` applies consistent tolerance

### Integration Tests:
- End-to-end: dissolve → simplify pipeline
- Verify existing tests don't break

### Manual Testing Steps:
1. Run `uv run pytest` to verify all tests pass
2. Run `uv run mypy src/` to verify type checking
3. Run `uv run ruff check src/ tests/` to verify linting

## Performance Considerations

- Simplification is fast (~ms for individual geometries)
- Batch processing of 20 lambda values should complete in < 1 second
- No need for parallelization at this scale

## References

- Research document: `thoughts/shared/research/2025-11-22-visvalingam-whyatt-simplification.md`
- Dissolve implementation: `src/half_america/postprocess/dissolve.py`
- Test patterns: `tests/test_postprocess/test_dissolve.py`
