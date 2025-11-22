---
date: 2025-11-21T00:00:00-08:00
researcher: Claude
git_commit: 50e397252c134e2f1c1f607c6a26541daae030bf
branch: master
repository: half-america
topic: "Phase 4: Post-Processing Implementation"
tags: [research, codebase, post-processing, topojson, simplification, geometry]
status: complete
last_updated: 2025-11-21
last_updated_by: Claude
---

# Research: Phase 4: Post-Processing Implementation

**Date**: 2025-11-21
**Researcher**: Claude
**Git Commit**: 50e397252c134e2f1c1f607c6a26541daae030bf
**Branch**: master
**Repository**: half-america

## Research Question

What is the current state of Phase 4 (Post-Processing) implementation, what capabilities exist in the codebase, and what needs to be built?

## Summary

Phase 4 transforms optimization output into web-ready geometries. The codebase has **all necessary dependencies installed** (shapely, topojson, geopandas) but **no post-processing functions implemented yet**. The optimization engine outputs boolean partition arrays, which must be converted to dissolved MultiPolygon geometries, simplified, and exported as TopoJSON.

### Phase 4 Milestones (from ROADMAP.md:74-79)

| Milestone | Status | Notes |
|-----------|--------|-------|
| Dissolve selected tracts into MultiPolygon | Not Started | Use `shapely.ops.unary_union` |
| Apply Visvalingam-Whyatt simplification | Not Started | Options available via shapely/geopandas |
| Export as TopoJSON | Not Started | `topojson>=1.6` already installed |
| Generate pre-computed geometry files for all lambda values | Not Started | Loop over SweepResult |
| Validate output geometries | Not Started | Check for validity and area thresholds |

## Detailed Findings

### 1. Optimization Output Structure

The optimization engine outputs a nested data structure stored in pickle files.

**Data Structure Hierarchy:**

```
SweepResult                           # sweep.py:21-28
  └── results: dict[float, LambdaResult]
        └── LambdaResult              # sweep.py:13-18
              └── search_result: SearchResult
                    └── SearchResult  # search.py:13-19
                          └── result: OptimizationResult
                                └── OptimizationResult  # solver.py:11-25
                                      └── partition: np.ndarray (bool)
```

**Key Field:** `OptimizationResult.partition` is a boolean numpy array where `True` indicates a selected tract. The array index corresponds to the GeoDataFrame row index.

**Cache Location:** `data/cache/processed/sweep_{TIGER_YEAR}_{ACS_YEAR}_{lambda_step}.pkl`

Example: `data/cache/processed/sweep_2024_2022_0.1.pkl`

**Relevant Files:**
- `src/half_america/optimization/solver.py:11-25` - OptimizationResult definition
- `src/half_america/optimization/sweep.py:21-28` - SweepResult definition
- `src/half_america/optimization/sweep.py:169-194` - Save/load functions
- `src/half_america/data/cache.py:30-41` - Cache path generation

### 2. Existing Geometry Processing

**Current shapely usage:**

| Function | Location | Purpose |
|----------|----------|---------|
| `shapely.make_valid()` | `data/cleaning.py:49, 93-94` | Repair invalid geometries |
| `shapely.set_precision()` | `data/cleaning.py:86` | Coordinate quantization (1cm grid) |
| `shapely.intersection()` | `graph/boundary.py:64` | Compute boundary intersections |
| `shapely.length()` | `graph/boundary.py:65` | Compute boundary lengths |

**Not currently used but available:**
- `shapely.ops.unary_union` - Required for dissolve
- `shapely.coverage_simplify()` - Visvalingam-Whyatt (requires GEOS 3.12+)
- `geopandas.GeoDataFrame.dissolve()` - High-level dissolve
- `geopandas.GeoSeries.simplify_coverage()` - V-W simplification wrapper

### 3. TopoJSON Capabilities

**Dependency Status:** Installed (`topojson>=1.6` in pyproject.toml:25, version 1.10 resolved)

**Usage Pattern (from research docs):**

```python
import topojson as tp

def create_topojson(gdf: gpd.GeoDataFrame) -> tp.Topology:
    return tp.Topology(
        gdf,
        prequantize=True,      # Close micro-gaps
        topoquantize=1e5,      # 100k grid points
        toposimplify=False,    # Simplify separately
    )
```

**TopoJSON Benefits (from METHODOLOGY.md:81):**
> This format is crucial as it encodes shared topology, preventing gaps from appearing between shapes during rendering.

### 4. Simplification Options

**Visvalingam-Whyatt Options Available:**

| Method | Source | Requirements |
|--------|--------|--------------|
| `shapely.coverage_simplify()` | shapely 2.1+ | GEOS 3.12+ |
| `gdf.geometry.simplify_coverage()` | geopandas | Wraps shapely |
| `topojson` with `algorithm="vw"` | topojson | Requires `simplification` package |

**Recommended Approach:** Use `shapely.coverage_simplify()` or `geopandas.simplify_coverage()` since:
1. Already installed (shapely>=2.0 in dependencies)
2. Preserves coverage topology (shared edges stay aligned)
3. No additional dependencies if GEOS version is sufficient

**Fallback:** Douglas-Peucker via `shapely.simplify()` is always available.

### 5. CLI Structure

**Framework:** Click (>=8.0)

**Current Commands:**
- `half-america precompute` - Pre-compute optimization for all lambda values

**Entry Point:** `src/half_america/__init__.py:4-8` -> `src/half_america/cli.py:14-17`

**Adding New Command:** Add after line 64 in `cli.py`:

```python
@cli.command()
@click.option(...)
def export(...) -> None:
    """Export post-processed geometries as TopoJSON."""
    ...
```

## Code References

- `src/half_america/optimization/solver.py:11-25` - OptimizationResult NamedTuple
- `src/half_america/optimization/sweep.py:21-28` - SweepResult NamedTuple
- `src/half_america/optimization/sweep.py:169-194` - Pickle save/load
- `src/half_america/data/cleaning.py:114-181` - Geometry cleaning pipeline
- `src/half_america/cli.py:37-64` - Precompute command
- `src/half_america/data/cache.py:30-41` - Cache path generation

## Architecture Insights

### Post-Processing Pipeline Design

Based on METHODOLOGY.md:74-81 and codebase analysis:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Post-Processing Pipeline                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Load                                                         │
│     └── SweepResult (pickle) + GeoDataFrame (parquet)           │
│                                                                  │
│  2. For each lambda value:                                       │
│     ├── Extract partition boolean array                          │
│     ├── Filter GeoDataFrame to selected tracts                   │
│     ├── Dissolve → MultiPolygon (unary_union)                   │
│     ├── Simplify → Visvalingam-Whyatt (coverage_simplify)       │
│     └── Validate → check is_valid, area > threshold             │
│                                                                  │
│  3. Export                                                       │
│     ├── Combine all lambda geometries                            │
│     ├── Create TopoJSON (tp.Topology)                            │
│     └── Write to file                                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Suggested Module Structure

```
src/half_america/
├── postprocess/
│   ├── __init__.py
│   ├── dissolve.py      # unary_union, island filtering
│   ├── simplify.py      # Visvalingam-Whyatt wrapper
│   ├── export.py        # TopoJSON generation
│   └── pipeline.py      # Orchestrates post-processing
└── cli.py               # Add export command
```

### Key Implementation Considerations

1. **Preserve All Islands:** Do NOT filter small disconnected polygons - the λ parameter's effect on island count is central to the visualization
2. **Simplification Tolerance:** Needs tuning based on target zoom levels
3. **TopoJSON Quantization:** Use `topoquantize=1e5` for good balance of precision/size
4. **Output Format:** Single TopoJSON with multiple features keyed by lambda value

## Related Research

- `thoughts/shared/research/2025-11-20-phase1-data-pipeline.md` - Earlier research on data pipeline

## Open Questions

1. **GEOS Version:** What GEOS version is installed? Affects `coverage_simplify()` availability
2. **Simplification Tolerance:** What tolerance value balances file size vs. visual quality?
3. **Output Structure:** Single TopoJSON file with all lambdas, or separate files per lambda?
4. **Web Integration:** Should output go to `data/output/` or directly to frontend assets?
