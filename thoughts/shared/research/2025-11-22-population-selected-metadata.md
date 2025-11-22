---
date: 2025-11-22T10:00:00-08:00
researcher: Claude
git_commit: 60d8df691adbef83eb6cc9ca226255511fe0afc7
branch: master
repository: stevenfazzio/half-america
topic: "Add population_selected to DissolveResult and TopoJSON metadata"
tags: [research, codebase, postprocess, dissolve, export, topojson, metadata]
status: complete
last_updated: 2025-11-22
last_updated_by: Claude
---

# Research: Add population_selected to DissolveResult and TopoJSON metadata

**Date**: 2025-11-22T10:00:00-08:00
**Researcher**: Claude
**Git Commit**: 60d8df691adbef83eb6cc9ca226255511fe0afc7
**Branch**: master
**Repository**: stevenfazzio/half-america

## Research Question

How to implement the ROADMAP.md Phase 4 milestone: "Add `population_selected` to DissolveResult and TopoJSON metadata"?

## Summary

The `population_selected` value is already computed during optimization (`solver.py:76`) and flows through `SweepResult`, but it's dropped when `dissolve_all_lambdas()` extracts only the `partition` array. The export layer already has `ExportMetadata.population_selected` field but hardcodes it to `0` with TODO comments. The fix requires:

1. Add `population_selected: int` field to `DissolveResult` NamedTuple
2. Update `dissolve_partition()` to accept and pass through population
3. Update `dissolve_all_lambdas()` to extract population from `SweepResult`
4. Remove hardcoded `0` values in export functions
5. Update tests to reflect the new field

## Detailed Findings

### DissolveResult Definition

**Location:** `src/half_america/postprocess/dissolve.py:13-19`

```python
class DissolveResult(NamedTuple):
    """Result from dissolving selected tracts."""

    geometry: MultiPolygon | Polygon
    num_parts: int  # Number of disconnected regions
    total_area_sqm: float  # Total area in square meters
    num_tracts: int  # Number of tracts dissolved
    # NOTE: population_selected is NOT present - needs to be added
```

**Functions that create DissolveResult:**
- `dissolve_partition()` at `dissolve.py:22-80` - creates single result
- `dissolve_all_lambdas()` at `dissolve.py:83-112` - batch creation from SweepResult

**Functions that consume DissolveResult:**
- `simplify_all_lambdas()` at `simplify.py:81-123` - only uses `.geometry`
- `export_all_lambdas()` at `export.py:103-154` - uses `.total_area_sqm`, `.num_parts`
- `export_combined_topojson()` at `export.py:157-223` - same fields

### TopoJSON Export Metadata Structure

**Location:** `src/half_america/postprocess/export.py:31-38`

```python
class ExportMetadata(NamedTuple):
    """Metadata to embed in TopoJSON properties."""

    lambda_value: float
    population_selected: int  # Field exists but receives 0
    area_sqm: float
    num_parts: int
```

**Current hardcoded values:**

1. `export.py:137` in `export_all_lambdas()`:
   ```python
   population_selected=0,  # TODO: Add when available in DissolveResult
   ```

2. `export.py:191` in `export_combined_topojson()`:
   ```python
   "population_selected": [0],  # TODO: Add when available
   ```

### Population Data Flow

The population data originates from Census API and flows through the optimization pipeline:

```
Census API (B01003_001E)
    |
    v
gpd.GeoDataFrame["population"]  (data/pipeline.py:40-43)
    |
    v
GraphAttributes.population: np.ndarray  (graph/boundary.py:100)
    |
    v
OptimizationResult.selected_population  (optimization/solver.py:76)
    |    calculated as: int(attrs.population[partition].sum())
    v
SearchResult.result.selected_population  (optimization/search.py:16)
    |
    v
LambdaResult.search_result.result.selected_population  (optimization/sweep.py:17)
    |
    v
SweepResult.results[lambda_val].search_result.result.selected_population
    |
    X  <-- GAP: dissolve_all_lambdas() only extracts partition, drops population
    |
    v
DissolveResult (no population_selected field)
    |
    v
ExportMetadata(population_selected=0)  <-- hardcoded
```

### OptimizationResult Structure

**Location:** `src/half_america/optimization/solver.py:11-24`

```python
class OptimizationResult(NamedTuple):
    partition: np.ndarray        # Boolean array: True = selected
    selected_population: int     # <-- This is what we need
    selected_area: float
    total_population: int
    total_area: float
    population_fraction: float
    satisfied_target: bool
    lambda_param: float
    mu: float
    flow_value: float
    energy: float
```

### Access Path to Population in dissolve_all_lambdas()

**Location:** `src/half_america/postprocess/dissolve.py:101-107`

```python
for lambda_val in sweep_result.lambda_values:
    partition = sweep_result.results[lambda_val].search_result.result.partition
    # Population available at:
    # sweep_result.results[lambda_val].search_result.result.selected_population
    result = dissolve_partition(gdf, partition)
    results[lambda_val] = result
```

## Code References

| Component | File | Lines |
|-----------|------|-------|
| DissolveResult definition | `src/half_america/postprocess/dissolve.py` | 13-19 |
| dissolve_partition() | `src/half_america/postprocess/dissolve.py` | 22-80 |
| dissolve_all_lambdas() | `src/half_america/postprocess/dissolve.py` | 83-112 |
| ExportMetadata definition | `src/half_america/postprocess/export.py` | 31-38 |
| export_all_lambdas() TODO | `src/half_america/postprocess/export.py` | 137 |
| export_combined_topojson() TODO | `src/half_america/postprocess/export.py` | 191 |
| OptimizationResult definition | `src/half_america/optimization/solver.py` | 11-24 |
| Population calculation | `src/half_america/optimization/solver.py` | 76 |
| Population extraction point | `src/half_america/postprocess/dissolve.py` | 105 |

## Architecture Insights

1. **NamedTuple pattern**: The codebase uses `NamedTuple` for all result types, providing immutability and type safety. Adding `population_selected` to `DissolveResult` follows this pattern.

2. **Data flow separation**: The dissolve module intentionally separates geometry operations from optimization data. This is why `dissolve_partition()` takes a `partition` array rather than an `OptimizationResult`. To add population, we either:
   - Pass population as a separate parameter (cleaner)
   - Pass the full `OptimizationResult` (more coupling)

3. **Export metadata already prepared**: The `ExportMetadata` type was designed with `population_selected` field from the start, indicating this was always intended to be populated.

## Implementation Plan

### Step 1: Update DissolveResult (dissolve.py:13-19)

```python
class DissolveResult(NamedTuple):
    """Result from dissolving selected tracts."""

    geometry: MultiPolygon | Polygon
    num_parts: int
    total_area_sqm: float
    num_tracts: int
    population_selected: int  # NEW FIELD
```

### Step 2: Update dissolve_partition() (dissolve.py:22-80)

Add `population_selected` parameter:

```python
def dissolve_partition(
    gdf: gpd.GeoDataFrame,
    partition: np.ndarray,
    population_selected: int = 0,  # NEW PARAMETER with default for backward compat
) -> DissolveResult:
```

Include in return:

```python
return DissolveResult(
    geometry=geom,
    num_parts=num_parts,
    total_area_sqm=geom.area,
    num_tracts=int(num_selected),
    population_selected=population_selected,  # NEW
)
```

### Step 3: Update dissolve_all_lambdas() (dissolve.py:101-107)

Extract population from SweepResult:

```python
for lambda_val in sweep_result.lambda_values:
    opt_result = sweep_result.results[lambda_val].search_result.result
    partition = opt_result.partition
    population_selected = opt_result.selected_population  # NEW
    result = dissolve_partition(gdf, partition, population_selected)  # UPDATED
    results[lambda_val] = result
```

### Step 4: Update export_all_lambdas() (export.py:135-140)

Replace hardcoded 0:

```python
metadata = ExportMetadata(
    lambda_value=lambda_val,
    population_selected=dissolve_result.population_selected,  # UPDATED
    area_sqm=dissolve_result.total_area_sqm,
    num_parts=dissolve_result.num_parts,
)
```

### Step 5: Update export_combined_topojson() (export.py:188-194)

Replace hardcoded 0:

```python
gdf = gpd.GeoDataFrame(
    {
        "lambda_value": [lambda_val],
        "population_selected": [dissolve_result.population_selected],  # UPDATED
        "area_sqm": [dissolve_result.total_area_sqm],
        "num_parts": [dissolve_result.num_parts],
        "geometry": [simplify_result.geometry],
    },
    crs="EPSG:5070",
)
```

### Step 6: Update Tests

Files to update:
- `tests/test_postprocess/test_dissolve.py` - assertions for new field
- `tests/test_postprocess/test_simplify.py` - fixture `sample_dissolve_results()`
- `tests/test_postprocess/test_export.py` - fixture `sample_dissolve_results()`

## Related Research

- `thoughts/shared/research/2025-11-21-dissolve-tracts-implementation.md` - Dissolve implementation research
- `thoughts/shared/research/2025-11-22-topojson-export.md` - TopoJSON export research
- `thoughts/shared/research/2025-11-21-phase4-post-processing.md` - Phase 4 overview

## Open Questions

1. **Backward compatibility for pickle files**: Existing saved `SweepResult` pickle files will work since `SweepResult` is unchanged. However, if there were any saved `DissolveResult` objects (unlikely), they would need regeneration.

2. **Population validation**: Should we validate that `population_selected` matches what we'd calculate from `gdf["population"][partition].sum()`? Currently we trust the value from `OptimizationResult`.

3. **Total population in metadata**: Consider adding `total_population` to `ExportMetadata` so frontend can calculate percentage without hardcoding the total.
