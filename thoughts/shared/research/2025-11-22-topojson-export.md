---
date: 2025-11-22T12:00:00-08:00
researcher: Claude
git_commit: 667a2bfce772decad0d443b69453e9936abb978f
branch: master
repository: half-america
topic: "Export as TopoJSON - Phase 4 Post-Processing"
tags: [research, codebase, topojson, export, postprocessing, phase4]
status: complete
last_updated: 2025-11-22
last_updated_by: Claude
---

# Research: Export as TopoJSON

**Date**: 2025-11-22
**Researcher**: Claude
**Git Commit**: 667a2bfce772decad0d443b69453e9936abb978f
**Branch**: master
**Repository**: half-america

## Research Question

What is needed to implement "Export as TopoJSON" as the next Phase 4 milestone? What libraries, code patterns, and implementation approach should be used?

## Summary

The TopoJSON export milestone is well-positioned for implementation. The `topojson>=1.6` library is **already installed** as a dependency, the dissolve and simplify modules are **complete**, and the CLI infrastructure exists with the `precompute` command as a template. Implementation requires:

1. Create `src/half_america/postprocess/export.py` with TopoJSON conversion functions
2. Add CLI `export` command to `cli.py`
3. Generate web-ready TopoJSON files for all lambda values

### Current State

| Component | Status | Location |
|-----------|--------|----------|
| Dissolve module | Complete | `postprocess/dissolve.py` |
| Simplification | Complete | `postprocess/simplify.py` |
| TopoJSON library | Installed | `topojson>=1.6` in pyproject.toml |
| Export module | Not implemented | Needs `postprocess/export.py` |
| CLI export command | Not implemented | Needs addition to `cli.py` |

## Detailed Findings

### 1. TopoJSON Format Benefits

TopoJSON is an extension of GeoJSON that encodes **topology** via shared arcs:

| Aspect | GeoJSON | TopoJSON |
|--------|---------|----------|
| Shared Boundaries | Duplicated | Stored once |
| Coordinate Encoding | Floating-point | Delta-encoded integers |
| Typical File Size | Baseline | 80%+ smaller |
| Topology | Lost | Preserved |

**Key benefit for half-america:** When rendering adjacent regions in the web frontend, TopoJSON prevents gaps between shapes during zooming/panning because topology is explicitly encoded.

### 2. Python `topojson` Library

**Package:** `topojson` by mattijn (already in pyproject.toml:25)
**Documentation:** https://mattijn.github.io/topojson

**Basic Usage:**

```python
from topojson import Topology
import geopandas as gpd

# Convert GeoDataFrame to TopoJSON
topo = Topology(gdf, prequantize=1e5)

# Export to file
topo.to_json("output.topo.json")

# Get as dictionary
topo_dict = topo.to_dict()
```

**Supported Inputs:**
- `geopandas.GeoDataFrame`
- `geopandas.GeoSeries`
- Shapely geometry objects (`Polygon`, `MultiPolygon`)
- GeoJSON dictionaries

### 3. Current Postprocessing Pipeline

**Data Flow:**

```
SweepResult (pickle)
    │
    ▼
dissolve_partition(gdf, partition) → DissolveResult
    │                                    └── geometry: MultiPolygon | Polygon
    ▼
simplify_geometry(geometry) → SimplifyResult
    │                            └── geometry: MultiPolygon | Polygon
    ▼
[NEW] export_to_topojson(geometry) → TopoJSON file
```

**Key Functions:**

- `dissolve_partition()` (`postprocess/dissolve.py:22`) - Merges selected tracts into unified geometry
- `dissolve_all_lambdas()` (`postprocess/dissolve.py:83`) - Batch dissolve for all lambda values
- `simplify_geometry()` (`postprocess/simplify.py:25`) - Simplifies geometry with Douglas-Peucker
- `simplify_all_lambdas()` (`postprocess/simplify.py:81`) - Batch simplify for all lambda values

**Result Types:**

```python
class DissolveResult(NamedTuple):
    geometry: MultiPolygon | Polygon
    num_parts: int
    total_area_sqm: float
    num_tracts: int

class SimplifyResult(NamedTuple):
    geometry: MultiPolygon | Polygon
    original_vertex_count: int
    simplified_vertex_count: int
    reduction_percent: float
```

### 4. Recommended TopoJSON Settings

For web map delivery with the half-america project:

```python
from topojson import Topology
import geopandas as gpd
from shapely.geometry import MultiPolygon, Polygon

def export_to_topojson(
    geometry: MultiPolygon | Polygon,
    output_path: Path,
    object_name: str = "selected_region",
    quantization: float = 1e5,
) -> None:
    """Export a geometry to TopoJSON format.

    Args:
        geometry: Shapely geometry to export
        output_path: Path for output .json file
        object_name: Name for the geometry object in TopoJSON
        quantization: Quantization factor (1e5 = good default)
    """
    # Create GeoDataFrame from geometry
    gdf = gpd.GeoDataFrame(geometry=[geometry], crs="EPSG:5070")

    # Convert to WGS84 for web (Mapbox GL JS expects EPSG:4326)
    gdf_wgs84 = gdf.to_crs("EPSG:4326")

    # Create TopoJSON
    topo = Topology(
        data=gdf_wgs84,
        prequantize=quantization,  # Quantize before topology
        topology=True,             # Enable topology detection
        object_name=object_name,
    )

    # Write to file
    topo.to_json(str(output_path))
```

**Quantization Guidelines:**

| Value | Use Case |
|-------|----------|
| `1e4` | Aggressive compression, lower detail |
| `1e5` | Good default balance |
| `1e6` | High precision, larger files |

### 5. Output Format Options

**Option A: Separate files per lambda (Recommended)**

```
data/output/topojson/
├── lambda_0.0.json
├── lambda_0.1.json
├── lambda_0.2.json
└── ...
```

Pros:
- Simpler to load individual lambda values
- Smaller per-request payload
- Easier caching/CDN optimization

**Option B: Single file with all lambdas**

```python
# Multi-object TopoJSON
topo = Topology(
    data=[gdf_0, gdf_01, gdf_02, ...],
    object_name=['lambda_0.0', 'lambda_0.1', 'lambda_0.2', ...]
)
```

Pros:
- Single HTTP request for all data
- Shared arcs across lambda values (if geometries overlap)

**Recommendation:** Start with Option A (separate files) for simplicity. Option B can be explored later if animation performance requires it.

### 6. CLI Export Command Design

Following the existing `precompute` command pattern in `cli.py:37-64`:

```python
@cli.command()
@click.option(
    "--lambda-step",
    type=float,
    default=0.1,
    help="Lambda step size (must match precomputed sweep)",
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Output directory (default: data/output/topojson)",
)
@click.option(
    "--quantization",
    type=float,
    default=1e5,
    help="TopoJSON quantization factor",
)
def export(
    lambda_step: float,
    output_dir: Path | None,
    quantization: float,
) -> None:
    """Export post-processed geometries as TopoJSON."""
    # 1. Load sweep result
    # 2. Load tract GeoDataFrame
    # 3. For each lambda: dissolve -> simplify -> export
    # 4. Write TopoJSON files
    ...
```

### 7. Coordinate Reference System Considerations

**Current CRS:** EPSG:5070 (Conus Albers Equal Area) - meters
**Web CRS:** EPSG:4326 (WGS84) - degrees (required for Mapbox GL JS)

The export function **must** transform coordinates:

```python
# Transform from projected to geographic
gdf_wgs84 = gdf.to_crs("EPSG:4326")
```

**Note:** Simplification tolerance is in CRS units. Current DEFAULT_TOLERANCE is 500 meters (EPSG:5070). This should remain as-is since simplification happens before CRS transformation.

## Code References

- `src/half_america/postprocess/dissolve.py:22` - `dissolve_partition()` function
- `src/half_america/postprocess/simplify.py:25` - `simplify_geometry()` function
- `src/half_america/postprocess/__init__.py:1-26` - Module exports
- `src/half_america/cli.py:37-64` - `precompute` command (template for `export`)
- `src/half_america/config.py:14-20` - Directory constants
- `pyproject.toml:25` - TopoJSON dependency declaration

## Architecture Insights

### Proposed Module Structure

```
src/half_america/postprocess/
├── __init__.py      # Add export_to_topojson, export_all_lambdas
├── dissolve.py      # Complete
├── simplify.py      # Complete
└── export.py        # NEW - TopoJSON export functions
```

### Implementation Sequence

1. **Create `export.py`** with:
   - `ExportResult` NamedTuple (path, file_size_bytes)
   - `export_to_topojson()` - Single geometry export
   - `export_all_lambdas()` - Batch export for all lambda values

2. **Update `__init__.py`** to export new functions

3. **Add `export` CLI command** to `cli.py`

4. **Add tests** in `tests/test_postprocess/test_export.py`

### Full Pipeline Example

```python
from half_america.data.pipeline import load_all_tracts
from half_america.optimization.sweep import load_sweep_result
from half_america.postprocess import (
    dissolve_all_lambdas,
    simplify_all_lambdas,
    export_all_lambdas,  # NEW
)

# Load data
gdf = load_all_tracts()
sweep_result = load_sweep_result(cache_path)

# Post-process
dissolve_results = dissolve_all_lambdas(gdf, sweep_result)
simplify_results = simplify_all_lambdas(dissolve_results)
export_results = export_all_lambdas(simplify_results, output_dir)  # NEW
```

## Historical Context (from thoughts/)

Previous research has established the post-processing pipeline design:

- `thoughts/shared/research/2025-11-21-phase4-post-processing.md` - Overall Phase 4 design including TopoJSON requirements
- `thoughts/shared/research/2025-11-22-visvalingam-whyatt-simplification.md` - Simplification research (now complete)
- `thoughts/shared/plans/2025-11-21-dissolve-tracts-implementation.md` - Dissolve implementation (now complete)

## Related Research

- [2025-11-21-phase4-post-processing.md](2025-11-21-phase4-post-processing.md) - Phase 4 overview
- [2025-11-22-visvalingam-whyatt-simplification.md](2025-11-22-visvalingam-whyatt-simplification.md) - Simplification implementation

## Open Questions

1. **Output Directory:** Should TopoJSON files go to `data/output/topojson/` or a frontend-specific location?

2. **File Naming:** Use `lambda_0.1.json` or `0.1.json` or `half_america_0.1.topo.json`?

3. **Metadata Properties:** Should the TopoJSON include properties like:
   - `lambda_value`
   - `population_selected`
   - `area_sqm`
   - `num_parts`

4. **Combined Export Option:** Should there be an option to export all lambdas in a single TopoJSON file with multiple objects?

## Implementation Checklist

- [ ] Create `src/half_america/postprocess/export.py`
  - [ ] `ExportResult` NamedTuple
  - [ ] `export_to_topojson()` function
  - [ ] `export_all_lambdas()` batch function
- [ ] Update `src/half_america/postprocess/__init__.py` exports
- [ ] Add `export` command to `src/half_america/cli.py`
- [ ] Create `tests/test_postprocess/test_export.py`
- [ ] Update `ROADMAP.md` to mark milestone complete
- [ ] Update `docs/API.md` with new functions
