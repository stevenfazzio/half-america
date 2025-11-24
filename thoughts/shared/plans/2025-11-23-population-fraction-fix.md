# Population Fraction Fix Implementation Plan

## Overview

Fix the population percentage display bias where 82% of lambda values show below 50%. The root cause is a frontend/backend population mismatch: the frontend uses a hardcoded US population of 331.9M while the tract data sums to 328.9M.

## Current State Analysis

**The Problem:**
- Frontend constant: `US_TOTAL_POPULATION = 331_893_745` (`SummaryPanel.tsx:17`)
- Backend tract total: `328,912,183` (actual sum from Census tracts)
- Difference: -2,981,562 people (-0.90%)
- Result: All displayed percentages are shifted down by ~0.45%

**Current Data Flow:**
```
OptimizationResult.total_population (exists)
        ↓
DissolveResult (missing total_population)
        ↓
ExportMetadata (missing total_population)
        ↓
TopoJSON properties (missing total_population)
        ↓
Frontend uses hardcoded constant instead
```

### Key Discoveries:
- `OptimizationResult` already has `total_population` (`solver.py:17`)
- `DissolveResult` and `ExportMetadata` don't propagate it
- Frontend `SummaryPanel.tsx` hardcodes `331_893_745`
- λ=0.98 shows anomalous 48.71% (near convergence failure threshold)

## Desired End State

After implementation:
1. TopoJSON files include `total_population` property
2. Frontend reads `total_population` dynamically from data
3. Population percentages display correctly (~50% centered)
4. No hardcoded population constants in frontend
5. (Optional) λ=0.98 removed from slider to avoid anomaly

### Verification:
- λ=0.50 should display ~50.0% (currently shows 49.87%)
- Distribution should be centered around 50%, not biased below

## What We're NOT Doing

- Changing the optimization algorithm or target fraction
- Modifying the binary search tolerance
- Investigating why tract total differs from official Census estimate
- Adding other new properties to TopoJSON

## Implementation Approach

Implement in phases so Phase 1 provides immediate relief while Phases 2-4 create the robust long-term solution.

---

## Phase 1: Quick Fix - Update Frontend Constant

### Overview
Immediately fix the display by updating the hardcoded constant to match the actual tract data.

### Changes Required:

#### 1. Update SummaryPanel.tsx
**File**: `web/src/components/SummaryPanel.tsx`
**Changes**: Update the hardcoded population constant

```typescript
// Line 16-17: Change from
// US population from 2022 ACS (same year as our data)
const US_TOTAL_POPULATION = 331_893_745;

// To:
// Total population from Census tract data (ACS 2022 via tract-level aggregation)
const US_TOTAL_POPULATION = 328_912_183;
```

### Success Criteria:

#### Automated Verification:
- [ ] TypeScript compiles: `cd web && npm run build`
- [ ] Lint passes: `cd web && npm run lint`

#### Manual Verification:
- [ ] λ=0.50 displays ~50.0% instead of 49.87%
- [ ] Population percentages appear more centered around 50%

**Implementation Note**: After completing this phase, the display will be accurate. Phases 2-4 eliminate the hardcoded value entirely for long-term maintainability.

---

## Phase 2: Backend Enhancement - Add total_population to Export Pipeline

### Overview
Propagate `total_population` through the export pipeline so it's included in TopoJSON files.

### Changes Required:

#### 1. Update DissolveResult
**File**: `src/half_america/postprocess/dissolve.py`
**Changes**: Add `total_population` field to `DissolveResult`

```python
# Lines 13-20: Update DissolveResult
class DissolveResult(NamedTuple):
    """Result from dissolving selected tracts into unified geometries."""

    geometry: MultiPolygon | Polygon
    num_parts: int
    total_area_sqm: float
    num_tracts: int
    population_selected: int
    total_population: int  # ADD THIS LINE
```

#### 2. Update dissolve_partition function
**File**: `src/half_america/postprocess/dissolve.py`
**Changes**: Pass `total_population` to `DissolveResult`

```python
# Around line 83: Update return statement in dissolve_partition()
# Add total_population parameter to function signature and return
def dissolve_partition(
    gdf: gpd.GeoDataFrame,
    partition: np.ndarray,
    population_selected: int,
    total_population: int,  # ADD THIS PARAMETER
) -> DissolveResult:
    # ... existing code ...

    return DissolveResult(
        geometry=dissolved,
        num_parts=num_parts,
        total_area_sqm=total_area,
        num_tracts=num_tracts,
        population_selected=population_selected,
        total_population=total_population,  # ADD THIS LINE
    )
```

#### 3. Update dissolve_all_lambdas function
**File**: `src/half_america/postprocess/dissolve.py`
**Changes**: Extract and pass `total_population` from `OptimizationResult`

```python
# Around lines 109-118: Update the call to dissolve_partition
opt_result = sweep_result.results[lambda_val].search_result.result
partition = opt_result.partition
population_selected = opt_result.selected_population
total_population = opt_result.total_population  # ADD THIS LINE

result = dissolve_partition(
    gdf,
    partition,
    population_selected,
    total_population,  # ADD THIS ARGUMENT
)
```

#### 4. Update ExportMetadata
**File**: `src/half_america/postprocess/export.py`
**Changes**: Add `total_population` field

```python
# Lines 31-38: Update ExportMetadata
class ExportMetadata(NamedTuple):
    """Metadata to embed in TopoJSON properties."""

    lambda_value: float
    population_selected: int
    total_population: int  # ADD THIS LINE
    area_sqm: float
    num_parts: int
```

#### 5. Update export_to_topojson GeoDataFrame
**File**: `src/half_america/postprocess/export.py`
**Changes**: Include `total_population` in exported properties

```python
# Lines 67-76: Update GeoDataFrame creation
gdf = gpd.GeoDataFrame(
    {
        "lambda_value": [metadata.lambda_value],
        "population_selected": [metadata.population_selected],
        "total_population": [metadata.total_population],  # ADD THIS LINE
        "area_sqm": [metadata.area_sqm],
        "num_parts": [metadata.num_parts],
        "geometry": [geometry],
    },
    crs="EPSG:5070",
)
```

#### 6. Update export_all_lambdas metadata creation
**File**: `src/half_america/postprocess/export.py`
**Changes**: Include `total_population` when building `ExportMetadata`

```python
# Lines 135-140: Update ExportMetadata creation
metadata = ExportMetadata(
    lambda_value=lambda_val,
    population_selected=dissolve_result.population_selected,
    total_population=dissolve_result.total_population,  # ADD THIS LINE
    area_sqm=dissolve_result.total_area_sqm,
    num_parts=dissolve_result.num_parts,
)
```

#### 7. Update export_combined_topojson GeoDataFrame
**File**: `src/half_america/postprocess/export.py`
**Changes**: Include `total_population` in combined export

```python
# Lines 188-197: Update GeoDataFrame in export_combined_topojson
gdf = gpd.GeoDataFrame(
    {
        "lambda_value": [lambda_val],
        "population_selected": [dissolve_result.population_selected],
        "total_population": [dissolve_result.total_population],  # ADD THIS LINE
        "area_sqm": [dissolve_result.total_area_sqm],
        "num_parts": [dissolve_result.num_parts],
        "geometry": [simplify_result.geometry],
    },
    crs="EPSG:5070",
)
```

### Success Criteria:

#### Automated Verification:
- [ ] Type check passes: `uv run mypy src/half_america/postprocess/`
- [ ] Lint passes: `uv run ruff check src/half_america/postprocess/`
- [ ] Unit tests pass: `uv run pytest tests/test_postprocess/ -v`

#### Manual Verification:
- [ ] None required for this phase (tested in Phase 4)

---

## Phase 3: Frontend Update - Use Dynamic total_population

### Overview
Update the frontend to read `total_population` from TopoJSON data instead of using a hardcoded constant.

### Changes Required:

#### 1. Update HalfAmericaProperties interface
**File**: `web/src/components/SummaryPanel.tsx`
**Changes**: Add `total_population` to the interface

```typescript
// Lines 4-9: Update interface
interface HalfAmericaProperties {
  lambda_value: number;
  population_selected: number;
  total_population: number;  // ADD THIS LINE
  area_sqm: number;
  num_parts: number;
}
```

#### 2. Remove hardcoded constant and use dynamic value
**File**: `web/src/components/SummaryPanel.tsx`
**Changes**: Replace hardcoded constant with dynamic calculation

```typescript
// DELETE lines 16-17:
// // Total population from Census tract data (ACS 2022 via tract-level aggregation)
// const US_TOTAL_POPULATION = 328_912_183;

// UPDATE line 26: Change calculation to use props
const populationPercent = ((props.population_selected / props.total_population) * 100).toFixed(1);
```

### Success Criteria:

#### Automated Verification:
- [ ] TypeScript compiles: `cd web && npm run build`
- [ ] Lint passes: `cd web && npm run lint`

#### Manual Verification:
- [ ] Verify no TypeScript errors about missing `total_population` property
- [ ] (Full verification after Phase 4 when data is regenerated)

**Implementation Note**: The frontend will show errors until Phase 4 completes (TopoJSON files need regeneration). This is expected.

---

## Phase 4: Re-export TopoJSON Data

### Overview
Regenerate all TopoJSON files to include the new `total_population` property.

### Changes Required:

#### 1. Run the export pipeline
**Command**:
```bash
uv run half-america export --force
```

This will regenerate all 99 lambda files plus the combined file with `total_population` included.

#### 2. Copy to web public directory
**Command**:
```bash
cp data/output/topojson/lambda_*.json web/public/data/
cp data/output/topojson/combined.json web/public/data/
```

### Success Criteria:

#### Automated Verification:
- [ ] Export completes without errors
- [ ] All 99 files + combined.json are generated
- [ ] Files contain `total_population` property:
  ```bash
  python3 -c "import json; d=json.load(open('web/public/data/lambda_0.50.json')); print('total_population' in str(d))"
  # Should print: True
  ```

#### Manual Verification:
- [ ] Start dev server: `cd web && npm run dev`
- [ ] λ=0.50 displays ~50.0%
- [ ] Multiple lambda values show percentages centered around 50%
- [ ] No console errors about missing properties

---

## Phase 5 (Optional): Cap Lambda at 0.97

### Overview
Remove λ=0.98 from the slider to avoid the anomalous 48.71% result near the convergence failure threshold.

### Changes Required:

#### 1. Update LAMBDA_VALUES array
**File**: `web/src/types/lambda.ts`
**Changes**: Remove 0.98 from the array

```typescript
// Line 15: Change from
  0.9, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98,
// To:
  0.9, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97,
```

#### 2. Delete the unused TopoJSON file
**Command**:
```bash
rm web/public/data/lambda_0.98.json
```

### Success Criteria:

#### Automated Verification:
- [ ] TypeScript compiles: `cd web && npm run build`
- [ ] Slider max is 0.97 (98 values instead of 99)

#### Manual Verification:
- [ ] Slider cannot reach 0.98
- [ ] No 404 errors when sliding to max

---

## Testing Strategy

### Unit Tests:
- Existing tests in `tests/test_postprocess/` should continue to pass
- No new unit tests required (this is a data propagation fix, not logic change)

### Integration Tests:
- Export pipeline should complete successfully
- TopoJSON files should contain all expected properties

### Manual Testing Steps:
1. Build and run the frontend: `cd web && npm run dev`
2. Navigate to the Map tab
3. Slide to λ=0.50, verify population shows ~50.0%
4. Slide to extremes (0.00, 0.97), verify reasonable percentages
5. Check console for any property access errors

## Performance Considerations

- No performance impact expected
- TopoJSON file sizes increase negligibly (~20 bytes per file for new property)
- Frontend calculation unchanged (just different denominator source)

## Migration Notes

- Phase 1 is backwards-compatible (just changes a constant)
- Phases 2-4 require regenerating TopoJSON files before frontend works correctly
- Phase 5 is optional and can be done independently

## References

- Original research: `thoughts/shared/research/2025-11-23-population-fraction-bias.md`
- Lambda convergence failure: `thoughts/shared/research/2025-11-21-lambda-one-convergence-failure.md`
- UI polish research: `thoughts/shared/research/2025-11-23-ui-style-polish.md`
