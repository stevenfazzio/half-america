# Legend Redesign Implementation Plan

## Overview

Redesign the SummaryPanel legend to prominently display population % and add the missing "% of US Land Area" hero stat, reorder metrics by importance, and improve visual formatting to communicate the core narrative at a glance.

## Current State Analysis

**Current legend stats** (`web/src/components/SummaryPanel.tsx:33-54`):
1. Population % (50.0%)
2. Area (42,902 mi²)
3. Regions (847)
4. Area/Region (51 mi²)
5. Lambda (λ = 0.50)

**Problem**: The legend is missing "% of US Land Area" - the second half of the core narrative. The Story tab says "half of Americans live in 1.1% of land" but the legend only shows population %.

**Data availability**:
- `OptimizationResult.total_area` exists (solver.py:111) but isn't exported
- Currently exported `area_sqm` = selected area only, not total US area

## Desired End State

**Hero Section** (visually prominent):
```
┌─────────────────────────────┐
│   50%                       │  ← Large, bold
│   of U.S. Population        │  ← Label
├─────────────────────────────┤
│   1.1%                      │  ← Large, bold (NEW!)
│   of U.S. Land Area         │  ← Label
└─────────────────────────────┘
```

**Supporting Stats** (smaller):
```
│  Area: 42,902 mi²           │
│  Regions: 847               │
```

**Technical Stats** (de-emphasized):
```
│  λ = 0.50                   │  ← Smaller, dimmer
```

**Removed**:
- Area/Region (low value derived stat)

### Success Criteria:
- Legend displays two hero stats: Population % and Land Area %
- Land Area % is calculated from exported total_area_all_sqm
- Area/Region stat is removed
- Lambda is de-emphasized with smaller/dimmer styling
- TypeScript types are updated for new property

## What We're NOT Doing

- Adding per-region statistics (significant scope creep)
- Adding hover tooltips with text (data doesn't support it)
- Changing the density calculation
- Moving legend to a different location

## Implementation Approach

Two-phase approach:
1. **Backend**: Add `total_area_all_sqm` to the export chain and regenerate TopoJSON files
2. **Frontend**: Redesign SummaryPanel with hero stats and improved styling

## Phase 1: Backend Data Export

### Overview
Add total US land area to the export chain so frontend can calculate "% of US Land Area".

### Changes Required:

#### 1. Update ExportMetadata
**File**: `src/half_america/postprocess/export.py`
**Changes**: Add `total_area_all_sqm` field to ExportMetadata

```python
class ExportMetadata(NamedTuple):
    """Metadata to embed in TopoJSON properties."""

    lambda_value: float
    population_selected: int
    total_population: int
    area_sqm: float
    num_parts: int
    total_area_all_sqm: float  # NEW: total area of all tracts (entire US)
```

#### 2. Update export_to_topojson
**File**: `src/half_america/postprocess/export.py`
**Changes**: Include new field in GeoDataFrame

```python
# In export_to_topojson function (around line 68)
gdf = gpd.GeoDataFrame(
    {
        "lambda_value": [metadata.lambda_value],
        "population_selected": [metadata.population_selected],
        "total_population": [metadata.total_population],
        "area_sqm": [metadata.area_sqm],
        "num_parts": [metadata.num_parts],
        "total_area_all_sqm": [metadata.total_area_all_sqm],  # NEW
        "geometry": [geometry],
    },
    crs="EPSG:5070",
)
```

#### 3. Update export_all_lambdas
**File**: `src/half_america/postprocess/export.py`
**Changes**: Pass total_area_all_sqm when building metadata

First, update the function signature to accept sweep_result:
```python
def export_all_lambdas(
    simplify_results: dict[float, SimplifyResult],
    dissolve_results: dict[float, DissolveResult],
    sweep_result: SweepResult,  # NEW parameter
    output_dir: Path | None = None,
    verbose: bool = True,
) -> dict[float, ExportResult]:
```

Then use it in metadata construction:
```python
# Get total area from sweep result
opt_result = sweep_result.results[lambda_val].search_result.result
total_area_all_sqm = opt_result.total_area

metadata = ExportMetadata(
    lambda_value=lambda_val,
    population_selected=dissolve_result.population_selected,
    total_population=dissolve_result.total_population,
    area_sqm=dissolve_result.total_area_sqm,
    num_parts=dissolve_result.num_parts,
    total_area_all_sqm=total_area_all_sqm,  # NEW
)
```

#### 4. Update export_combined_topojson
**File**: `src/half_america/postprocess/export.py`
**Changes**: Same pattern - add sweep_result parameter and include total_area_all_sqm

```python
def export_combined_topojson(
    simplify_results: dict[float, SimplifyResult],
    dissolve_results: dict[float, DissolveResult],
    sweep_result: SweepResult,  # NEW parameter
    output_path: Path | None = None,
    quantization: float = DEFAULT_QUANTIZATION,
    verbose: bool = True,
) -> Path:
```

And in the loop:
```python
opt_result = sweep_result.results[lambda_val].search_result.result

gdf = gpd.GeoDataFrame(
    {
        "lambda_value": [lambda_val],
        "population_selected": [dissolve_result.population_selected],
        "total_population": [dissolve_result.total_population],
        "area_sqm": [dissolve_result.total_area_sqm],
        "num_parts": [dissolve_result.num_parts],
        "total_area_all_sqm": [opt_result.total_area],  # NEW
        "geometry": [simplify_result.geometry],
    },
    crs="EPSG:5070",
)
```

#### 5. Update CLI export command
**File**: `src/half_america/cli.py`
**Changes**: Pass sweep_result to export functions (lines 147-152, 157-162)

The `sweep_result` is already loaded at line 133. Add it to the function calls:

```python
# Line 147-152
export_results = export_all_lambdas(
    simplify_results,
    dissolve_results,
    sweep_result,  # NEW parameter
    output_dir=output_dir,
    verbose=True,
)

# Lines 157-162
combined_path = export_combined_topojson(
    simplify_results,
    dissolve_results,
    sweep_result,  # NEW parameter
    output_path=output_dir / "combined.json",
    verbose=True,
)
```

#### 6. Update postprocess __init__.py exports
**File**: `src/half_america/postprocess/__init__.py`
**Changes**: Add SweepResult import for type hints (if needed for re-export)

### Success Criteria:

#### Automated Verification:
- [x] Type checking passes: `uv run mypy src/`
- [x] Linting passes: `uv run ruff check src/`
- [x] Unit tests pass: `uv run pytest tests/ -v`
- [x] Export runs successfully: `uv run half-america export --lambda-step 0.01`

#### Manual Verification:
- [x] Inspect a TopoJSON file and confirm `total_area_all_sqm` is present in properties
- [x] Value should be ~8.1 trillion sq meters (total contiguous US area)

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the TopoJSON files contain the new field before proceeding to Phase 2.

---

## Phase 2: Frontend Legend Redesign

### Overview
Update SummaryPanel to display hero stats prominently and improve overall styling.

### Changes Required:

#### 1. Update TypeScript Interface
**File**: `web/src/components/SummaryPanel.tsx`
**Changes**: Add new property to interface

```typescript
interface HalfAmericaProperties {
  lambda_value: number;
  population_selected: number;
  total_population: number;
  area_sqm: number;
  num_parts: number;
  total_area_all_sqm: number;  // NEW
}
```

#### 2. Update SummaryPanel Component
**File**: `web/src/components/SummaryPanel.tsx`
**Changes**: Calculate land area % and restructure display

```tsx
export function SummaryPanel({ data, lambda }: SummaryPanelProps) {
  if (!data || data.features.length === 0) {
    return null;
  }

  const props = data.features[0].properties;

  // Hero stats
  const populationPercent = ((props.population_selected / props.total_population) * 100).toFixed(1);
  const landAreaPercent = ((props.area_sqm / props.total_area_all_sqm) * 100).toFixed(1);

  // Supporting stats
  const areaSqMiles = (props.area_sqm / 2_589_988).toLocaleString(undefined, { maximumFractionDigits: 0 });

  return (
    <div className="summary-panel">
      <h2 className="summary-title">Half of America</h2>

      {/* Hero stats section */}
      <div className="hero-stats">
        <div className="hero-stat">
          <span className="hero-value">{populationPercent}%</span>
          <span className="hero-label">of U.S. Population</span>
        </div>
        <div className="hero-stat">
          <span className="hero-value">{landAreaPercent}%</span>
          <span className="hero-label">of U.S. Land Area</span>
        </div>
      </div>

      {/* Supporting stats */}
      <dl className="summary-stats">
        <div className="stat">
          <dt>Area</dt>
          <dd>{areaSqMiles} mi²</dd>
        </div>
        <div className="stat">
          <dt>Regions</dt>
          <dd>{props.num_parts.toLocaleString()}</dd>
        </div>
      </dl>

      {/* Technical stats (de-emphasized) */}
      <div className="technical-stats">
        <span className="technical-stat">λ = {lambda.toFixed(2)}</span>
      </div>
    </div>
  );
}
```

#### 3. Update CSS Styling
**File**: `web/src/components/SummaryPanel.css`
**Changes**: Add hero stat styling and de-emphasized technical stat styling

```css
/* Hero stats section */
.hero-stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.hero-stat {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.hero-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
}

.hero-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 2px;
}

/* Supporting stats (existing .stat styles largely unchanged) */
.summary-stats {
  margin: 0;
  display: grid;
  gap: 8px;
}

.stat {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 16px;
}

.stat dt {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.stat dd {
  font-size: 14px;
  font-weight: 600;
  margin: 0;
  font-variant-numeric: tabular-nums;
}

/* Technical stats (de-emphasized) */
.technical-stats {
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.technical-stat {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  font-variant-numeric: tabular-nums;
}

/* Mobile adjustments */
@media (max-width: 767px) {
  .hero-value {
    font-size: 24px;
  }
}
```

### Success Criteria:

#### Automated Verification:
- [x] TypeScript compiles: `npm run build`
- [x] Linting passes: `npm run lint`

#### Manual Verification:
- [x] Legend displays two hero stats prominently (Population % and Land Area %)
- [x] Population % shows ~50% as expected
- [x] Land Area % shows ~1.4% at λ=0.50 (consistent with Story tab)
- [x] Area/Region stat is removed
- [x] Lambda is smaller and dimmer than other stats (hidden on mobile)
- [x] Mobile view looks acceptable
- [x] Slider still updates all values correctly

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation that the visual design is acceptable.

---

## Testing Strategy

### Unit Tests:
- No new unit tests required (this is primarily a data-passing and UI change)
- Existing tests should continue to pass

### Integration Tests:
- Export command produces valid TopoJSON with new field
- Frontend loads and displays data correctly

### Manual Testing Steps:
1. Run export: `uv run half-america export --lambda-step 0.01`
2. Inspect `web/public/data/lambda_0.50.json` for `total_area_all_sqm` field
3. Run frontend: `cd web && npm run dev`
4. Move slider and verify all stats update
5. Check that Land Area % is ~1.1% at λ=0.50
6. Verify responsive behavior on mobile viewport

## Migration Notes

- Requires regenerating all TopoJSON files with new field
- Old TopoJSON files will cause frontend errors (missing property)
- Production deploy requires: backend export → copy files → frontend build → deploy

## References

- Original ticket: ROADMAP.md Phase 6 milestone
- Related research: `thoughts/shared/research/2025-11-24-hover-tooltips-legend-redesign.md`
- Current implementation: `web/src/components/SummaryPanel.tsx:33-54`
