# Add population_selected to DissolveResult and TopoJSON Metadata

## Overview

Add the `population_selected` field to `DissolveResult` and flow it through to TopoJSON export metadata. This completes a Phase 4 milestone tracked in ROADMAP.md. The population value is already computed during optimization but is currently dropped when creating `DissolveResult` objects.

## Current State Analysis

The population data flows correctly through the optimization pipeline but is lost at the dissolve layer:

```
OptimizationResult.selected_population (computed at solver.py:76)
    ↓
SweepResult.results[λ].search_result.result.selected_population
    ↓
    X  <-- GAP: dissolve_all_lambdas() only extracts partition, drops population
    ↓
DissolveResult (no population_selected field)
    ↓
ExportMetadata(population_selected=0)  <-- hardcoded
```

### Key Discoveries:
- `DissolveResult` at `dissolve.py:13-19` is a NamedTuple with 4 fields, missing `population_selected`
- `dissolve_partition()` at `dissolve.py:22-80` creates `DissolveResult` without population
- `dissolve_all_lambdas()` at `dissolve.py:101-107` has access to population but doesn't use it
- `export.py:137` and `export.py:191` have TODO comments with hardcoded `0` values
- `ExportMetadata` already has `population_selected` field, just receives `0`

## Desired End State

After implementation:
1. `DissolveResult` includes `population_selected: int` field
2. `dissolve_partition()` accepts and passes through population parameter
3. `dissolve_all_lambdas()` extracts population from `SweepResult` and passes it to `dissolve_partition()`
4. TopoJSON exports contain actual population values instead of `0`
5. All existing tests pass with updated fixtures

### Verification:
- Run `uv run pytest tests/test_postprocess/` - all tests pass
- Run `uv run mypy src/` - no type errors
- Run `uv run ruff check src/ tests/` - no linting issues
- Generated TopoJSON files contain non-zero `population_selected` values

## What We're NOT Doing

- Adding `total_population` to `ExportMetadata` (future enhancement)
- Adding population validation (trust the value from `OptimizationResult`)
- Regenerating existing pickle files (not affected by this change)
- Modifying any optimization or sweep logic

## Implementation Approach

The fix is straightforward: add the field to the NamedTuple, thread the parameter through function signatures, and update test fixtures. Total changes are minimal and localized to the postprocess module.

## Phase 1: Update DissolveResult and dissolve_partition()

### Overview
Add `population_selected` field to `DissolveResult` and update `dissolve_partition()` to accept and return it.

### Changes Required:

#### 1. DissolveResult definition
**File**: `src/half_america/postprocess/dissolve.py`
**Lines**: 13-19

Add `population_selected: int` as the 5th field:

```python
class DissolveResult(NamedTuple):
    """Result from dissolving selected tracts."""

    geometry: MultiPolygon | Polygon
    num_parts: int  # Number of disconnected regions
    total_area_sqm: float  # Total area in square meters
    num_tracts: int  # Number of tracts dissolved
    population_selected: int  # Population in selected tracts
```

#### 2. dissolve_partition() signature
**File**: `src/half_america/postprocess/dissolve.py`
**Lines**: 22-80

Add `population_selected` parameter with default value for backward compatibility:

```python
def dissolve_partition(
    gdf: gpd.GeoDataFrame,
    partition: np.ndarray,
    population_selected: int = 0,
) -> DissolveResult:
```

Update the docstring Args section:
```python
    Args:
        gdf: GeoDataFrame with tract geometries (from load_all_tracts)
        partition: Boolean array where True = selected tract
        population_selected: Population in selected tracts (default 0)
```

Update the return statement at lines 75-80:
```python
    return DissolveResult(
        geometry=geom,
        num_parts=num_parts,
        total_area_sqm=geom.area,
        num_tracts=int(num_selected),
        population_selected=population_selected,
    )
```

### Success Criteria:

#### Automated Verification:
- [x] Type checking passes: `uv run mypy src/half_america/postprocess/dissolve.py`
- [x] Linting passes: `uv run ruff check src/half_america/postprocess/dissolve.py`

**Implementation Note**: After completing this phase, proceed to Phase 2 immediately (no manual verification needed).

---

## Phase 2: Update dissolve_all_lambdas()

### Overview
Extract `population_selected` from `SweepResult` and pass it to `dissolve_partition()`.

### Changes Required:

#### 1. dissolve_all_lambdas() loop
**File**: `src/half_america/postprocess/dissolve.py`
**Lines**: 101-107

Update the loop to extract and pass population:

```python
    for lambda_val in sweep_result.lambda_values:
        if verbose:
            print(f"Dissolving λ={lambda_val:.2f}...")

        opt_result = sweep_result.results[lambda_val].search_result.result
        partition = opt_result.partition
        population_selected = opt_result.selected_population
        result = dissolve_partition(gdf, partition, population_selected)
        results[lambda_val] = result

        if verbose:
            print(f"  {result.num_tracts:,} tracts → {result.num_parts} parts")
```

### Success Criteria:

#### Automated Verification:
- [x] Type checking passes: `uv run mypy src/half_america/postprocess/dissolve.py`
- [x] Linting passes: `uv run ruff check src/half_america/postprocess/dissolve.py`

**Implementation Note**: After completing this phase, proceed to Phase 3 immediately.

---

## Phase 3: Update Export Functions

### Overview
Replace hardcoded `0` values with actual `population_selected` from `DissolveResult`.

### Changes Required:

#### 1. export_all_lambdas()
**File**: `src/half_america/postprocess/export.py`
**Lines**: 135-140

Replace hardcoded `0`:

```python
        # Build metadata from dissolve result
        metadata = ExportMetadata(
            lambda_value=lambda_val,
            population_selected=dissolve_result.population_selected,
            area_sqm=dissolve_result.total_area_sqm,
            num_parts=dissolve_result.num_parts,
        )
```

#### 2. export_combined_topojson()
**File**: `src/half_america/postprocess/export.py`
**Lines**: 188-197

Replace hardcoded `0` in the GeoDataFrame creation:

```python
        gdf = gpd.GeoDataFrame(
            {
                "lambda_value": [lambda_val],
                "population_selected": [dissolve_result.population_selected],
                "area_sqm": [dissolve_result.total_area_sqm],
                "num_parts": [dissolve_result.num_parts],
                "geometry": [simplify_result.geometry],
            },
            crs="EPSG:5070",
        )
```

### Success Criteria:

#### Automated Verification:
- [x] Type checking passes: `uv run mypy src/half_america/postprocess/export.py`
- [x] Linting passes: `uv run ruff check src/half_america/postprocess/export.py`

**Implementation Note**: After completing this phase, proceed to Phase 4 immediately.

---

## Phase 4: Update Test Fixtures

### Overview
Update `DissolveResult` fixtures in test files to include the new `population_selected` field.

### Changes Required:

#### 1. test_simplify.py fixture
**File**: `tests/test_postprocess/test_simplify.py`
**Lines**: 165-195 (sample_dissolve_results fixture)

Add `population_selected` to each `DissolveResult`:

```python
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
            population_selected=165_000_000,
        ),
        0.5: DissolveResult(
            geometry=geom,
            num_parts=1,
            total_area_sqm=geom.area,
            num_tracts=10,
            population_selected=165_000_000,
        ),
        0.9: DissolveResult(
            geometry=geom,
            num_parts=1,
            total_area_sqm=geom.area,
            num_tracts=10,
            population_selected=165_000_000,
        ),
    }
```

#### 2. test_export.py fixture
**File**: `tests/test_postprocess/test_export.py`
**Lines**: 248-270 (sample_dissolve_results fixture)

Add `population_selected` to each `DissolveResult`:

```python
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
            population_selected=165_000_000,
        ),
        0.5: DissolveResult(
            geometry=geom,
            num_parts=50,
            total_area_sqm=geom.area,
            num_tracts=30000,
            population_selected=165_000_000,
        ),
        0.9: DissolveResult(
            geometry=geom,
            num_parts=10,
            total_area_sqm=geom.area,
            num_tracts=30000,
            population_selected=165_000_000,
        ),
    }
```

### Success Criteria:

#### Automated Verification:
- [x] All postprocess tests pass: `uv run pytest tests/test_postprocess/ -v`
- [x] Full test suite passes: `uv run pytest`
- [x] Type checking passes: `uv run mypy src/`
- [x] Linting passes: `uv run ruff check src/ tests/`

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation that the implementation is complete.

---

## Phase 5: Update ROADMAP.md

### Overview
Mark the milestone as complete in ROADMAP.md.

### Changes Required:

#### 1. ROADMAP.md
**File**: `ROADMAP.md`
**Line**: 80

Change from:
```markdown
- [ ] Add `population_selected` to DissolveResult and TopoJSON metadata
```

To:
```markdown
- [x] Add `population_selected` to DissolveResult and TopoJSON metadata
```

### Success Criteria:

#### Automated Verification:
- [x] Linting passes: `uv run ruff check ROADMAP.md` (if applicable)

#### Manual Verification:
- [x] ROADMAP.md reflects the completed milestone

---

## Testing Strategy

### Unit Tests:
- Existing tests in `test_dissolve.py` verify `DissolveResult` structure - will fail until fixtures updated
- Existing tests in `test_simplify.py` and `test_export.py` use `sample_dissolve_results` fixture

### Integration Tests:
- `test_dissolve.py::TestDissolveAllLambdas::test_processes_all_lambda_values` runs full pipeline
- This test will verify population flows through correctly

### Manual Testing Steps:
1. Run `uv run half-america export --lambda 0.5` with pre-computed data
2. Verify the output TopoJSON contains `population_selected` > 0

## Performance Considerations

None - this is a simple data passthrough with no computational overhead.

## Migration Notes

None - this change only affects `DissolveResult` which is generated on-the-fly and not persisted.

## References

- Original research: `thoughts/shared/research/2025-11-22-population-selected-metadata.md`
- Related research: `thoughts/shared/research/2025-11-22-topojson-export.md`
- ROADMAP milestone: `ROADMAP.md:80`
