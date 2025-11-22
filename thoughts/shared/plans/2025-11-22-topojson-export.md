# TopoJSON Export Implementation Plan

## Overview

Implement TopoJSON export as the final Phase 4 post-processing milestone. This creates web-ready TopoJSON files from simplified geometries, enabling the Phase 5 React/Mapbox GL JS frontend to render optimized population regions.

## Current State Analysis

| Component | Status | Location |
|-----------|--------|----------|
| Dissolve module | Complete | `postprocess/dissolve.py` |
| Simplification | Complete | `postprocess/simplify.py` |
| TopoJSON library | Installed | `topojson>=1.6` in pyproject.toml |
| Export module | **Not implemented** | Needs `postprocess/export.py` |
| CLI export command | **Not implemented** | Needs addition to `cli.py` |
| Output directory | **Not defined** | Needs `OUTPUT_DIR` in config.py |

### Key Discoveries:

- Python `topojson` library (mattijn) accepts GeoDataFrame, GeoSeries, or Shapely geometry directly (`postprocess/dissolve.py:16`)
- Existing pattern: NamedTuple result types + single function + `_all_lambdas` batch function (`postprocess/simplify.py:11-78`)
- SimplifyResult provides geometry in EPSG:5070 (meters) - must transform to EPSG:4326 for web
- CLI uses Click with `--lambda-step`, `--force` patterns (`cli.py:20-64`)

## Desired End State

After implementation:

1. `half-america export` CLI command generates TopoJSON files
2. Files written to `data/output/topojson/lambda_X.X.json`
3. Each file contains WGS84 geometry with metadata properties
4. Optional `--combined` flag creates single multi-object TopoJSON
5. Full test coverage in `tests/test_postprocess/test_export.py`

### Verification:

```bash
# Generate TopoJSON files
uv run half-america export

# Verify output
ls data/output/topojson/
# lambda_0.0.json  lambda_0.1.json  ...  lambda_0.9.json

# Validate JSON structure
python -c "import json; json.load(open('data/output/topojson/lambda_0.5.json'))"

# Check file contains expected properties
python -c "
import json
data = json.load(open('data/output/topojson/lambda_0.5.json'))
assert data['type'] == 'Topology'
assert 'selected_region' in data['objects']
props = data['objects']['selected_region']['properties']
assert 'lambda_value' in props
assert 'population_selected' in props
"
```

## What We're NOT Doing

- Frontend integration (Phase 5 scope)
- Additional simplification in TopoJSON conversion (already done in simplify.py)
- Custom quantization CLI options (use sensible default of 1e5)
- GeoJSON export (TopoJSON is the target format)

## Implementation Approach

Follow established postprocess module patterns:
1. `ExportResult` NamedTuple with export metadata
2. `export_to_topojson()` for single geometry export
3. `export_all_lambdas()` for batch export
4. `export_combined_topojson()` for multi-object single file
5. CLI `export` command with `--combined` flag

---

## Phase 1: Core Export Module

### Overview
Create `export.py` with result types and single-geometry export function.

### Changes Required:

#### 1. Add OUTPUT_DIR to config.py
**File**: `src/half_america/config.py`
**Changes**: Add output directory constant

```python
# After line 20 (PROCESSED_DIR)
OUTPUT_DIR = DATA_DIR / "output"
TOPOJSON_DIR = OUTPUT_DIR / "topojson"
```

#### 2. Create export.py module
**File**: `src/half_america/postprocess/export.py`
**Changes**: New file with core export functionality

```python
"""Export geometries to TopoJSON format for web delivery."""

from pathlib import Path
from typing import NamedTuple

import geopandas as gpd
from shapely import MultiPolygon, Polygon
from topojson import Topology

from half_america.config import TOPOJSON_DIR

# Default quantization factor (1e5 = good balance of precision vs file size)
DEFAULT_QUANTIZATION = 1e5


class ExportResult(NamedTuple):
    """Result from exporting a geometry to TopoJSON."""

    path: Path
    file_size_bytes: int
    lambda_value: float
    object_name: str


class ExportMetadata(NamedTuple):
    """Metadata to embed in TopoJSON properties."""

    lambda_value: float
    population_selected: int
    area_sqm: float
    num_parts: int


def export_to_topojson(
    geometry: MultiPolygon | Polygon,
    output_path: Path,
    metadata: ExportMetadata,
    object_name: str = "selected_region",
    quantization: float = DEFAULT_QUANTIZATION,
) -> ExportResult:
    """
    Export a geometry to TopoJSON format.

    Args:
        geometry: Shapely geometry in EPSG:5070 (Conus Albers)
        output_path: Path for output .json file
        metadata: Metadata to embed as properties
        object_name: Name for the geometry object in TopoJSON
        quantization: Quantization factor (default 1e5)

    Returns:
        ExportResult with path and file size

    Raises:
        ValueError: If geometry is empty
    """
    if geometry.is_empty:
        raise ValueError("Cannot export empty geometry")

    # Create GeoDataFrame with metadata as properties
    gdf = gpd.GeoDataFrame(
        {
            "lambda_value": [metadata.lambda_value],
            "population_selected": [metadata.population_selected],
            "area_sqm": [metadata.area_sqm],
            "num_parts": [metadata.num_parts],
            "geometry": [geometry],
        },
        crs="EPSG:5070",
    )

    # Transform to WGS84 for web (Mapbox GL JS expects EPSG:4326)
    gdf_wgs84 = gdf.to_crs("EPSG:4326")

    # Create TopoJSON
    topo = Topology(
        data=gdf_wgs84,
        prequantize=quantization,
        topology=True,
        object_name=object_name,
    )

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to file
    topo.to_json(str(output_path))

    return ExportResult(
        path=output_path,
        file_size_bytes=output_path.stat().st_size,
        lambda_value=metadata.lambda_value,
        object_name=object_name,
    )
```

#### 3. Update postprocess __init__.py
**File**: `src/half_america/postprocess/__init__.py`
**Changes**: Export new types and functions

```python
"""Post-processing for optimization results."""

from half_america.postprocess.dissolve import (
    DissolveResult,
    dissolve_all_lambdas,
    dissolve_partition,
)
from half_america.postprocess.export import (
    DEFAULT_QUANTIZATION,
    ExportMetadata,
    ExportResult,
    export_to_topojson,
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
    # Export
    "DEFAULT_QUANTIZATION",
    "ExportMetadata",
    "ExportResult",
    "export_to_topojson",
]
```

### Success Criteria:

#### Automated Verification:
- [ ] Type checking passes: `uv run mypy src/half_america/postprocess/export.py`
- [ ] Linting passes: `uv run ruff check src/half_america/postprocess/`
- [ ] Module imports successfully: `uv run python -c "from half_america.postprocess import export_to_topojson"`

#### Manual Verification:
- [ ] Test export with sample geometry produces valid TopoJSON file
- [ ] Output file is valid JSON and contains expected structure

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation before proceeding to Phase 2.

---

## Phase 2: Batch Export Functions

### Overview
Add `export_all_lambdas()` batch function and combined multi-object export.

### Changes Required:

#### 1. Add batch export functions to export.py
**File**: `src/half_america/postprocess/export.py`
**Changes**: Add after `export_to_topojson()` function

```python
def export_all_lambdas(
    simplify_results: dict[float, "SimplifyResult"],
    dissolve_results: dict[float, "DissolveResult"],
    output_dir: Path | None = None,
    verbose: bool = True,
) -> dict[float, ExportResult]:
    """
    Export simplified geometries for all lambda values to individual TopoJSON files.

    Args:
        simplify_results: Dictionary mapping lambda values to SimplifyResult
        dissolve_results: Dictionary mapping lambda values to DissolveResult
            (needed for population/area metadata)
        output_dir: Output directory (default: data/output/topojson)
        verbose: Print progress messages

    Returns:
        Dictionary mapping lambda values to ExportResult
    """
    if output_dir is None:
        output_dir = TOPOJSON_DIR

    results: dict[float, ExportResult] = {}

    for lambda_val in simplify_results:
        if verbose:
            print(f"Exporting λ={lambda_val:.2f}...")

        simplify_result = simplify_results[lambda_val]
        dissolve_result = dissolve_results[lambda_val]

        # Build metadata from dissolve result
        metadata = ExportMetadata(
            lambda_value=lambda_val,
            population_selected=0,  # TODO: Add when available in DissolveResult
            area_sqm=dissolve_result.total_area_sqm,
            num_parts=dissolve_result.num_parts,
        )

        output_path = output_dir / f"lambda_{lambda_val}.json"
        result = export_to_topojson(
            geometry=simplify_result.geometry,
            output_path=output_path,
            metadata=metadata,
        )
        results[lambda_val] = result

        if verbose:
            size_kb = result.file_size_bytes / 1024
            print(f"  → {result.path.name} ({size_kb:.1f} KB)")

    return results


def export_combined_topojson(
    simplify_results: dict[float, "SimplifyResult"],
    dissolve_results: dict[float, "DissolveResult"],
    output_path: Path | None = None,
    quantization: float = DEFAULT_QUANTIZATION,
    verbose: bool = True,
) -> Path:
    """
    Export all lambda values to a single multi-object TopoJSON file.

    Args:
        simplify_results: Dictionary mapping lambda values to SimplifyResult
        dissolve_results: Dictionary mapping lambda values to DissolveResult
        output_path: Output file path (default: data/output/topojson/combined.json)
        quantization: Quantization factor
        verbose: Print progress messages

    Returns:
        Path to the combined TopoJSON file
    """
    if output_path is None:
        output_path = TOPOJSON_DIR / "combined.json"

    # Build list of GeoDataFrames with object names
    gdfs = []
    object_names = []

    for lambda_val in sorted(simplify_results.keys()):
        simplify_result = simplify_results[lambda_val]
        dissolve_result = dissolve_results[lambda_val]

        gdf = gpd.GeoDataFrame(
            {
                "lambda_value": [lambda_val],
                "population_selected": [0],  # TODO: Add when available
                "area_sqm": [dissolve_result.total_area_sqm],
                "num_parts": [dissolve_result.num_parts],
                "geometry": [simplify_result.geometry],
            },
            crs="EPSG:5070",
        )
        gdf_wgs84 = gdf.to_crs("EPSG:4326")
        gdfs.append(gdf_wgs84)
        object_names.append(f"lambda_{lambda_val}")

    if verbose:
        print(f"Creating combined TopoJSON with {len(gdfs)} objects...")

    # Create multi-object TopoJSON
    topo = Topology(
        data=gdfs,
        prequantize=quantization,
        topology=True,
        object_name=object_names,
    )

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to file
    topo.to_json(str(output_path))

    if verbose:
        size_kb = output_path.stat().st_size / 1024
        print(f"  → {output_path.name} ({size_kb:.1f} KB)")

    return output_path


# Import for type hints (avoid circular import)
from half_america.postprocess.simplify import SimplifyResult  # noqa: E402
from half_america.postprocess.dissolve import DissolveResult  # noqa: E402
```

#### 2. Update __init__.py exports
**File**: `src/half_america/postprocess/__init__.py`
**Changes**: Add new exports

```python
from half_america.postprocess.export import (
    DEFAULT_QUANTIZATION,
    ExportMetadata,
    ExportResult,
    export_all_lambdas,
    export_combined_topojson,
    export_to_topojson,
)

# Update __all__ to include:
    # Export
    "DEFAULT_QUANTIZATION",
    "ExportMetadata",
    "ExportResult",
    "export_to_topojson",
    "export_all_lambdas",
    "export_combined_topojson",
```

### Success Criteria:

#### Automated Verification:
- [ ] Type checking passes: `uv run mypy src/half_america/postprocess/export.py`
- [ ] Linting passes: `uv run ruff check src/half_america/postprocess/`
- [ ] All exports available: `uv run python -c "from half_america.postprocess import export_all_lambdas, export_combined_topojson"`

#### Manual Verification:
- [ ] Batch export produces correct number of files
- [ ] Combined export creates single file with multiple objects

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation before proceeding to Phase 3.

---

## Phase 3: CLI Export Command

### Overview
Add `export` command to CLI with `--combined` flag option.

### Changes Required:

#### 1. Add export command to cli.py
**File**: `src/half_america/cli.py`
**Changes**: Add export command after precompute

```python
from half_america.postprocess import (
    dissolve_all_lambdas,
    export_all_lambdas,
    export_combined_topojson,
    simplify_all_lambdas,
)
from half_america.config import TOPOJSON_DIR


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
    help=f"Output directory (default: {TOPOJSON_DIR})",
)
@click.option(
    "--combined",
    is_flag=True,
    help="Also export all lambdas to a single combined.json file",
)
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite existing output files",
)
def export(
    lambda_step: float,
    output_dir: Path | None,
    combined: bool,
    force: bool,
) -> None:
    """Export post-processed geometries as TopoJSON for web delivery."""
    from half_america.data.cache import get_sweep_cache_path
    from half_america.optimization.sweep import load_sweep_result

    # Resolve output directory
    if output_dir is None:
        output_dir = TOPOJSON_DIR

    # Check for existing output
    if output_dir.exists() and any(output_dir.glob("*.json")) and not force:
        click.echo(f"Output files exist in: {output_dir}")
        click.echo("Use --force to overwrite")
        return

    # Load sweep result
    cache_path = get_sweep_cache_path(lambda_step)
    if not cache_path.exists():
        click.echo(f"Sweep cache not found: {cache_path}")
        click.echo("Run 'half-america precompute' first")
        return

    click.echo(f"Loading sweep result from {cache_path}...")
    sweep_result = load_sweep_result(cache_path)

    click.echo("Loading tract data...")
    gdf = load_all_tracts()

    # Run postprocessing pipeline
    click.echo("Dissolving partitions...")
    dissolve_results = dissolve_all_lambdas(gdf, sweep_result, verbose=False)

    click.echo("Simplifying geometries...")
    simplify_results = simplify_all_lambdas(dissolve_results, verbose=False)

    # Export to TopoJSON
    click.echo(f"Exporting TopoJSON to {output_dir}...")
    export_results = export_all_lambdas(
        simplify_results,
        dissolve_results,
        output_dir=output_dir,
        verbose=True,
    )

    # Optionally create combined file
    if combined:
        click.echo("Creating combined TopoJSON...")
        combined_path = export_combined_topojson(
            simplify_results,
            dissolve_results,
            output_path=output_dir / "combined.json",
            verbose=True,
        )
        click.echo(f"Combined file: {combined_path}")

    # Summary
    total_size = sum(r.file_size_bytes for r in export_results.values())
    click.echo(f"\nExported {len(export_results)} files ({total_size / 1024:.1f} KB total)")
```

### Success Criteria:

#### Automated Verification:
- [ ] Type checking passes: `uv run mypy src/half_america/cli.py`
- [ ] Linting passes: `uv run ruff check src/half_america/cli.py`
- [ ] CLI help shows export command: `uv run half-america --help`
- [ ] Export command help works: `uv run half-america export --help`

#### Manual Verification:
- [ ] `uv run half-america export` creates TopoJSON files in `data/output/topojson/`
- [ ] `uv run half-america export --combined` also creates `combined.json`
- [ ] `--force` flag properly overwrites existing files
- [ ] Error handling works when sweep cache doesn't exist

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation before proceeding to Phase 4.

---

## Phase 4: Tests & Documentation

### Overview
Add comprehensive tests and update API documentation.

### Changes Required:

#### 1. Create test_export.py
**File**: `tests/test_postprocess/test_export.py`
**Changes**: New test file

```python
"""Tests for export module."""

import json
from pathlib import Path

import pytest
from shapely import MultiPolygon, Polygon
from shapely.geometry import box

from half_america.postprocess.dissolve import DissolveResult
from half_america.postprocess.export import (
    DEFAULT_QUANTIZATION,
    ExportMetadata,
    ExportResult,
    export_all_lambdas,
    export_combined_topojson,
    export_to_topojson,
)
from half_america.postprocess.simplify import SimplifyResult


class TestExportToTopojson:
    """Tests for export_to_topojson function."""

    def test_returns_export_result(self, simple_polygon, tmp_path, sample_metadata):
        """Should return an ExportResult with all fields."""
        output_path = tmp_path / "test.json"
        result = export_to_topojson(
            simple_polygon, output_path, sample_metadata
        )

        assert isinstance(result, ExportResult)
        assert result.path == output_path
        assert result.file_size_bytes > 0
        assert result.lambda_value == sample_metadata.lambda_value
        assert result.object_name == "selected_region"

    def test_creates_valid_topojson(self, simple_polygon, tmp_path, sample_metadata):
        """Output should be valid TopoJSON."""
        output_path = tmp_path / "test.json"
        export_to_topojson(simple_polygon, output_path, sample_metadata)

        with open(output_path) as f:
            data = json.load(f)

        assert data["type"] == "Topology"
        assert "objects" in data
        assert "arcs" in data

    def test_includes_metadata_properties(self, simple_polygon, tmp_path, sample_metadata):
        """TopoJSON should include metadata as properties."""
        output_path = tmp_path / "test.json"
        export_to_topojson(simple_polygon, output_path, sample_metadata)

        with open(output_path) as f:
            data = json.load(f)

        # Properties are in the geometry object
        obj = data["objects"]["selected_region"]
        assert "properties" in obj or "geometries" in obj

    def test_transforms_to_wgs84(self, simple_polygon, tmp_path, sample_metadata):
        """Coordinates should be in WGS84 (longitude/latitude range)."""
        output_path = tmp_path / "test.json"
        export_to_topojson(simple_polygon, output_path, sample_metadata)

        with open(output_path) as f:
            data = json.load(f)

        # Check transform or bbox is in reasonable WGS84 range
        if "bbox" in data:
            bbox = data["bbox"]
            # Longitude: -180 to 180, Latitude: -90 to 90
            assert -180 <= bbox[0] <= 180
            assert -90 <= bbox[1] <= 90

    def test_empty_geometry_raises(self, tmp_path, sample_metadata):
        """Empty geometry should raise ValueError."""
        empty = Polygon()
        output_path = tmp_path / "test.json"

        with pytest.raises(ValueError, match="empty geometry"):
            export_to_topojson(empty, output_path, sample_metadata)

    def test_multipolygon_input(self, disconnected_multipolygon, tmp_path, sample_metadata):
        """Should handle MultiPolygon input correctly."""
        output_path = tmp_path / "test.json"
        result = export_to_topojson(
            disconnected_multipolygon, output_path, sample_metadata
        )

        assert result.file_size_bytes > 0
        with open(output_path) as f:
            data = json.load(f)
        assert data["type"] == "Topology"

    def test_custom_object_name(self, simple_polygon, tmp_path, sample_metadata):
        """Should use custom object name."""
        output_path = tmp_path / "test.json"
        export_to_topojson(
            simple_polygon, output_path, sample_metadata, object_name="custom_region"
        )

        with open(output_path) as f:
            data = json.load(f)

        assert "custom_region" in data["objects"]

    def test_creates_parent_directories(self, simple_polygon, tmp_path, sample_metadata):
        """Should create parent directories if they don't exist."""
        output_path = tmp_path / "nested" / "dir" / "test.json"
        export_to_topojson(simple_polygon, output_path, sample_metadata)

        assert output_path.exists()


class TestExportAllLambdas:
    """Tests for export_all_lambdas batch function."""

    def test_exports_all_lambda_values(
        self, sample_simplify_results, sample_dissolve_results, tmp_path
    ):
        """Should export all lambda values."""
        results = export_all_lambdas(
            sample_simplify_results,
            sample_dissolve_results,
            output_dir=tmp_path,
            verbose=False,
        )

        assert len(results) == len(sample_simplify_results)
        for lambda_val in sample_simplify_results:
            assert lambda_val in results
            assert isinstance(results[lambda_val], ExportResult)

    def test_creates_correct_filenames(
        self, sample_simplify_results, sample_dissolve_results, tmp_path
    ):
        """Should create files with lambda_X.X.json naming."""
        export_all_lambdas(
            sample_simplify_results,
            sample_dissolve_results,
            output_dir=tmp_path,
            verbose=False,
        )

        for lambda_val in sample_simplify_results:
            expected_path = tmp_path / f"lambda_{lambda_val}.json"
            assert expected_path.exists()


class TestExportCombinedTopojson:
    """Tests for export_combined_topojson function."""

    def test_creates_combined_file(
        self, sample_simplify_results, sample_dissolve_results, tmp_path
    ):
        """Should create a single combined file."""
        output_path = tmp_path / "combined.json"
        result = export_combined_topojson(
            sample_simplify_results,
            sample_dissolve_results,
            output_path=output_path,
            verbose=False,
        )

        assert result == output_path
        assert output_path.exists()

    def test_contains_all_objects(
        self, sample_simplify_results, sample_dissolve_results, tmp_path
    ):
        """Combined file should contain all lambda objects."""
        output_path = tmp_path / "combined.json"
        export_combined_topojson(
            sample_simplify_results,
            sample_dissolve_results,
            output_path=output_path,
            verbose=False,
        )

        with open(output_path) as f:
            data = json.load(f)

        assert data["type"] == "Topology"
        for lambda_val in sample_simplify_results:
            assert f"lambda_{lambda_val}" in data["objects"]


# Fixtures specific to export tests


@pytest.fixture
def simple_polygon() -> Polygon:
    """Create a simple polygon in EPSG:5070 coordinates."""
    # Coordinates roughly in center of CONUS (Kansas area)
    return box(-500000, 1500000, 500000, 2500000)


@pytest.fixture
def disconnected_multipolygon() -> MultiPolygon:
    """Create two disconnected polygons."""
    poly1 = box(-500000, 1500000, 0, 2000000)
    poly2 = box(500000, 1500000, 1000000, 2000000)
    return MultiPolygon([poly1, poly2])


@pytest.fixture
def sample_metadata() -> ExportMetadata:
    """Create sample metadata for testing."""
    return ExportMetadata(
        lambda_value=0.5,
        population_selected=165_000_000,
        area_sqm=5_000_000_000_000.0,
        num_parts=50,
    )


@pytest.fixture
def sample_simplify_results() -> dict[float, SimplifyResult]:
    """Create sample simplify results for testing."""
    geom = box(-500000, 1500000, 500000, 2500000)
    return {
        0.0: SimplifyResult(
            geometry=geom,
            original_vertex_count=100,
            simplified_vertex_count=10,
            reduction_percent=90.0,
        ),
        0.5: SimplifyResult(
            geometry=geom,
            original_vertex_count=100,
            simplified_vertex_count=10,
            reduction_percent=90.0,
        ),
        0.9: SimplifyResult(
            geometry=geom,
            original_vertex_count=100,
            simplified_vertex_count=10,
            reduction_percent=90.0,
        ),
    }


@pytest.fixture
def sample_dissolve_results() -> dict[float, DissolveResult]:
    """Create sample dissolve results for testing."""
    geom = box(-500000, 1500000, 500000, 2500000)
    return {
        0.0: DissolveResult(
            geometry=geom,
            num_parts=100,
            total_area_sqm=geom.area,
            num_tracts=30000,
        ),
        0.5: DissolveResult(
            geometry=geom,
            num_parts=50,
            total_area_sqm=geom.area,
            num_tracts=30000,
        ),
        0.9: DissolveResult(
            geometry=geom,
            num_parts=10,
            total_area_sqm=geom.area,
            num_tracts=30000,
        ),
    }
```

#### 2. Update docs/API.md
**File**: `docs/API.md`
**Changes**: Add export module documentation (in Post-Processing section)

```markdown
### Export Module

Export simplified geometries to TopoJSON format for web delivery.

#### Functions

##### `export_to_topojson(geometry, output_path, metadata, object_name="selected_region", quantization=1e5)`

Export a single geometry to TopoJSON format.

**Parameters:**
- `geometry`: Shapely Polygon or MultiPolygon in EPSG:5070
- `output_path`: Path for output .json file
- `metadata`: ExportMetadata with lambda_value, population_selected, area_sqm, num_parts
- `object_name`: Name for geometry object in TopoJSON (default: "selected_region")
- `quantization`: Quantization factor (default: 1e5)

**Returns:** `ExportResult` with path, file_size_bytes, lambda_value, object_name

##### `export_all_lambdas(simplify_results, dissolve_results, output_dir=None, verbose=True)`

Export all lambda values to individual TopoJSON files.

**Parameters:**
- `simplify_results`: dict[float, SimplifyResult] from simplify_all_lambdas()
- `dissolve_results`: dict[float, DissolveResult] from dissolve_all_lambdas()
- `output_dir`: Output directory (default: data/output/topojson)
- `verbose`: Print progress messages

**Returns:** dict[float, ExportResult]

##### `export_combined_topojson(simplify_results, dissolve_results, output_path=None, quantization=1e5, verbose=True)`

Export all lambda values to a single multi-object TopoJSON file.

**Parameters:**
- `simplify_results`: dict[float, SimplifyResult]
- `dissolve_results`: dict[float, DissolveResult]
- `output_path`: Output file path (default: data/output/topojson/combined.json)
- `quantization`: Quantization factor
- `verbose`: Print progress messages

**Returns:** Path to combined file

#### Types

##### `ExportResult`
```python
class ExportResult(NamedTuple):
    path: Path
    file_size_bytes: int
    lambda_value: float
    object_name: str
```

##### `ExportMetadata`
```python
class ExportMetadata(NamedTuple):
    lambda_value: float
    population_selected: int
    area_sqm: float
    num_parts: int
```

#### Constants

- `DEFAULT_QUANTIZATION = 1e5` - Default TopoJSON quantization factor
```

#### 3. Update ROADMAP.md
**File**: `ROADMAP.md`
**Changes**: Mark TopoJSON export milestone complete

Find the Phase 4 section and update the TopoJSON export checkbox from `[ ]` to `[x]`.

### Success Criteria:

#### Automated Verification:
- [ ] All tests pass: `uv run pytest tests/test_postprocess/test_export.py -v`
- [ ] Full test suite passes: `uv run pytest`
- [ ] Type checking passes: `uv run mypy src/`
- [ ] Linting passes: `uv run ruff check src/ tests/`

#### Manual Verification:
- [ ] API.md documentation is accurate and complete
- [ ] ROADMAP.md shows TopoJSON export as complete
- [ ] Test coverage is comprehensive (edge cases, error handling)

**Implementation Note**: After completing this phase and all automated verification passes, the TopoJSON export feature is complete.

---

## Testing Strategy

### Unit Tests:
- `export_to_topojson()`: Valid output, metadata inclusion, CRS transformation, error handling
- `export_all_lambdas()`: Correct file count, naming convention, all results valid
- `export_combined_topojson()`: Single file with all objects, correct structure

### Integration Tests:
- Full pipeline: dissolve → simplify → export
- CLI export command with actual sweep data

### Manual Testing Steps:
1. Run `uv run half-america export` and verify files created
2. Open a TopoJSON file in a JSON viewer, verify structure
3. Load TopoJSON in a web map tool (geojson.io or similar) to verify geometry renders
4. Test `--combined` flag creates expected combined file

## Performance Considerations

- TopoJSON quantization at 1e5 provides ~80% file size reduction vs GeoJSON
- CRS transformation (EPSG:5070 → EPSG:4326) is fast for simplified geometries
- Combined export may be slower due to topology detection across all objects

## Migration Notes

None - this is a new feature with no existing data to migrate.

## References

- Original research: `thoughts/shared/research/2025-11-22-topojson-export.md`
- Python topojson library: https://mattijn.github.io/topojson
- TopoJSON specification: https://github.com/topojson/topojson-specification
- Similar implementation pattern: `src/half_america/postprocess/simplify.py`
