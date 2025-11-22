---
date: 2025-11-21T00:00:00-08:00
researcher: Claude
git_commit: bfb80acc3206c6a873ae1faffb465444083d6089
branch: master
repository: half-america
topic: "Dissolve Selected Tracts into MultiPolygon Geometries"
tags: [research, codebase, dissolve, unary_union, geometry, phase4]
status: complete
last_updated: 2025-11-21
last_updated_by: Claude
---

# Research: Dissolve Selected Tracts into MultiPolygon Geometries

**Date**: 2025-11-21
**Researcher**: Claude
**Git Commit**: bfb80acc3206c6a873ae1faffb465444083d6089
**Branch**: master
**Repository**: half-america

## Research Question

How to implement the first Phase 4 milestone: "Dissolve selected tracts into MultiPolygon geometries (shapely.ops.unary_union)" (ROADMAP.md:75)?

## Summary

The dissolve operation converts the optimization output (boolean partition array) into a single merged geometry. The implementation is straightforward:

1. Load GeoDataFrame and SweepResult
2. Filter GeoDataFrame using partition boolean array
3. Call `gdf[partition].geometry.union_all()` to merge
4. Validate result with `make_valid()` if needed

**Recommended approach:** Use `gdf.geometry.union_all()` directly for pure geometry merging, or `gdf.dissolve(method="coverage")` if aggregated attributes are needed.

## Detailed Findings

### 1. Data Flow: Partition Array to Geometry

The optimization output is a boolean NumPy array where indices directly correspond to GeoDataFrame row positions.

**Access Pattern:**

```python
from half_america.data.pipeline import load_all_tracts
from half_america.optimization.sweep import load_sweep_result

# Load data
gdf = load_all_tracts()
sweep = load_sweep_result(cache_path)

# Get partition for specific lambda
partition = sweep.results[0.5].search_result.result.partition  # np.ndarray[bool]

# Filter to selected tracts
selected_gdf = gdf[partition]  # ~30,000+ tracts at 50% population
```

**Key insight:** The partition array index `i` directly maps to GeoDataFrame row `i`. This is guaranteed by `Queen.from_dataframe(gdf, use_index=False)` at `graph/adjacency.py:77`.

### 2. Dissolve Options

| Method | Code | Output Type | Best For |
|--------|------|-------------|----------|
| GeoSeries.union_all() | `gdf[partition].geometry.union_all()` | Geometry | Pure geometry merge |
| shapely.union_all() | `shapely.union_all(gdf[partition].geometry.values)` | Geometry | Direct GEOS call |
| GeoDataFrame.dissolve() | `gdf[partition].dissolve()` | GeoDataFrame | With attribute aggregation |
| dissolve(method="coverage") | `gdf[partition].dissolve(method="coverage")` | GeoDataFrame | Non-overlapping polygons (faster) |

**Recommended:** `gdf[partition].geometry.union_all()` for simplicity, or `dissolve(method="coverage")` since Census tracts are guaranteed non-overlapping.

### 3. Expected Output Types by Lambda

| Lambda (λ) | Visual Result | Geometry Type |
|------------|---------------|---------------|
| λ ≈ 0 (dusty) | Many disconnected specks | MultiPolygon (many parts) |
| λ ≈ 0.5 (medium) | Fewer larger regions | MultiPolygon |
| λ ≈ 0.9 (smooth) | Connected blobs | Polygon or MultiPolygon |

The output is `MultiPolygon` in most cases because selected tracts form disconnected "islands" at low lambda values.

### 4. Post-Dissolve Validation

Follow existing validation patterns from `data/cleaning.py`:

```python
import shapely

def validate_dissolved_geometry(geom):
    """Validate and fix dissolved geometry."""
    # Check validity
    if not geom.is_valid:
        geom = shapely.make_valid(geom)

    # Check for empty
    if geom.is_empty:
        raise ValueError("Dissolved geometry is empty")

    return geom
```

**Existing patterns to reuse:**
- `shapely.make_valid()` - `cleaning.py:49, 93-94`
- Validity check via `geom.is_valid` - `cleaning.py:45`
- Empty check via `geom.is_empty` - `cleaning.py:28`

### 5. Implementation Sketch

```python
# src/half_america/postprocess/dissolve.py

from typing import NamedTuple
import geopandas as gpd
import numpy as np
import shapely
from shapely import MultiPolygon, Polygon


class DissolveResult(NamedTuple):
    """Result from dissolving selected tracts."""
    geometry: MultiPolygon | Polygon
    num_parts: int  # Number of disconnected regions
    total_area_sqm: float


def dissolve_partition(
    gdf: gpd.GeoDataFrame,
    partition: np.ndarray,
) -> DissolveResult:
    """
    Dissolve selected tracts into a single MultiPolygon.

    Args:
        gdf: GeoDataFrame with tract geometries (from load_all_tracts)
        partition: Boolean array where True = selected tract

    Returns:
        DissolveResult with merged geometry and metadata
    """
    # Filter to selected tracts
    selected = gdf[partition]

    # Merge all geometries
    # Using method="coverage" since tracts are non-overlapping
    merged = selected.dissolve(method="coverage")
    geom = merged.geometry.iloc[0]

    # Validate
    if not geom.is_valid:
        geom = shapely.make_valid(geom)

    # Count parts
    if geom.geom_type == "MultiPolygon":
        num_parts = len(geom.geoms)
    else:
        num_parts = 1

    return DissolveResult(
        geometry=geom,
        num_parts=num_parts,
        total_area_sqm=geom.area,
    )
```

### 6. Performance Considerations

**Scale:** ~73,000 total tracts, ~30,000+ selected per lambda value

**Performance factors:**
- `union_all()` is O(n log n) using cascaded union algorithm
- Census tracts are non-overlapping, enabling `method="coverage"` optimization
- Adjacent polygons are more efficient than scattered ones (spatial indexing)

**Benchmark fixtures exist** at `tests/benchmarks/conftest.py:44-127`:
- 400 tracts (20x20 grid)
- 2,500 tracts (50x50 grid)

These can be extended to benchmark dissolve performance.

## Code References

- `src/half_america/optimization/solver.py:11-25` - OptimizationResult.partition definition
- `src/half_america/optimization/sweep.py:21-28` - SweepResult structure
- `src/half_america/optimization/sweep.py:181-194` - load_sweep_result()
- `src/half_america/data/pipeline.py:66-68` - load_all_tracts() cache loading
- `src/half_america/graph/adjacency.py:75-77` - Index mapping guarantee
- `src/half_america/data/cleaning.py:37-51` - fix_invalid_geometries() pattern
- `src/half_america/data/cleaning.py:69-97` - Post-operation revalidation pattern

## Architecture Insights

### Module Placement

Per the Phase 4 research document, create `src/half_america/postprocess/`:

```
src/half_america/postprocess/
├── __init__.py
├── dissolve.py     # This milestone
├── simplify.py     # Next milestone
├── export.py       # TopoJSON export
└── pipeline.py     # Orchestration
```

### Integration with Existing Code

The dissolve module should:
1. Accept GeoDataFrame from `load_all_tracts()`
2. Accept partition from `SweepResult.results[λ].search_result.result.partition`
3. Return geometry compatible with simplification step
4. Follow validation patterns from `data/cleaning.py`

## Related Research

- `thoughts/shared/research/2025-11-21-phase4-post-processing.md` - Overall Phase 4 research

## Open Questions

1. **Return type:** Should `dissolve_partition()` return just the geometry, or a GeoDataFrame with lambda metadata?
2. **Batch processing:** Process all lambda values in one call, or expose per-lambda function?
3. **Error handling:** What if all tracts are selected (no partition)? Or none?
