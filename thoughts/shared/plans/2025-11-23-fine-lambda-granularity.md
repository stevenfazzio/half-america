# Fine Lambda Granularity Implementation Plan

## Overview

Increase lambda (surface tension) granularity from 0.1 to 0.01 increments, expanding from 10 values to 100 values. This enables smoother slider interaction with less visual "jumping" between adjacent lambda values.

## Current State Analysis

### Current Configuration
- **Lambda values**: `[0.0, 0.1, 0.2, ..., 0.9]` (10 values)
- **File naming**: `lambda_X.X.json` with 1 decimal precision
- **Total data size**: ~1.2 MB (10 files + combined.json)
- **Load time**: ~1-2 seconds (10 sequential HTTP requests)

### File Size Pattern (important for projections)
| Lambda | File Size | Notes |
|--------|-----------|-------|
| 0.0 | 362 KB | Most fragmented (many small regions) |
| 0.1 | 218 KB | |
| 0.2 | 146 KB | |
| 0.3 | 104 KB | |
| 0.4 | 87 KB | |
| 0.5 | 71 KB | |
| 0.6 | 61 KB | |
| 0.7 | 49 KB | |
| 0.8 | 41 KB | |
| 0.9 | 30 KB | Smoothest (few large blobs) |

**Projected 100-file total**: ~12-15 MB (interpolating the pattern)

### Key Discoveries
- Backend already supports `--lambda-step 0.01` via CLI (`src/half_america/cli.py:37-41`)
- Frontend uses hardcoded `LAMBDA_VALUES` array (`web/src/types/lambda.ts:5`)
- All `toFixed(1)` calls assume single-decimal precision
- Sequential loading in `useTopoJsonLoader.ts` will scale linearly with file count

## Desired End State

After implementation:
- **Lambda values**: `[0.0, 0.01, 0.02, ..., 0.99]` (100 values)
- **File naming**: `lambda_X.XX.json` with 2 decimal precision
- **Slider**: 100 discrete positions with smooth stepping
- **Load time**: Acceptable (<5 seconds target, achieved via parallel loading)

### Verification
1. Slider moves smoothly through 100 positions
2. Each lambda value displays correctly with 2 decimal places
3. Map visualization updates correctly for all 100 values
4. Initial load completes in <5 seconds on typical connection

## What We're NOT Doing

- **Polygon morphing animation**: Not feasible due to differing polygon counts between lambda values
- **Chunked file strategy**: Adds backend complexity; parallel loading is simpler and sufficient
- **On-demand/lazy loading**: Would add slider latency; pre-loading all values is preferred
- **Changing the backend code**: CLI already supports arbitrary step sizes

---

## Phase 1: Generate Data

### Overview
Run the existing CLI commands with `--lambda-step 0.01` to generate 100 TopoJSON files.

### Commands Required

```bash
# 1. Precompute optimization results (one-time, ~15-25 minutes)
uv run half-america precompute --lambda-step 0.01

# 2. Export TopoJSON files (generates 100 files)
uv run half-america export --lambda-step 0.01

# 3. Remove old 10-value files from web directory
rm web/public/data/lambda_*.json

# 4. Copy new 100-value files to web directory
cp data/output/topojson/lambda_*.json web/public/data/

# 5. Optionally regenerate combined.json (not used by current frontend)
# cp data/output/topojson/combined.json web/public/data/
```

### Expected Output
- 100 files: `lambda_0.00.json` through `lambda_0.99.json`
- Cache file: `data/cache/processed/sweep_2024_2022_0.01.pkl`
- Total size: ~12-15 MB

### Success Criteria

#### Automated Verification:
- [ ] 100 files exist in `web/public/data/`: `ls web/public/data/lambda_*.json | wc -l` returns 100
- [ ] Files follow naming pattern: `ls web/public/data/lambda_0.00.json` succeeds
- [ ] No old single-decimal files remain: `ls web/public/data/lambda_0.0.json` fails

#### Manual Verification:
- [ ] Spot-check a few files open correctly in a JSON viewer
- [ ] Verify file sizes follow expected pattern (0.00 largest, 0.99 smallest)

**Implementation Note**: This phase can be run independently before any code changes.

---

## Phase 2: Frontend Updates

### Overview
Update the frontend to use 100 lambda values with 2-decimal precision.

### Changes Required

#### 1. Lambda Type Definitions
**File**: `web/src/types/lambda.ts`
**Changes**: Expand `LAMBDA_VALUES` to 100 elements, update `toFixed(1)` to `toFixed(2)`

```typescript
/**
 * Lambda parameter values for surface tension control.
 * λ≈0 minimizes area (dusty map), λ≈0.99 minimizes perimeter (smooth blobs).
 */
export const LAMBDA_VALUES = [
  0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09,
  0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19,
  0.2, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29,
  0.3, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.37, 0.38, 0.39,
  0.4, 0.41, 0.42, 0.43, 0.44, 0.45, 0.46, 0.47, 0.48, 0.49,
  0.5, 0.51, 0.52, 0.53, 0.54, 0.55, 0.56, 0.57, 0.58, 0.59,
  0.6, 0.61, 0.62, 0.63, 0.64, 0.65, 0.66, 0.67, 0.68, 0.69,
  0.7, 0.71, 0.72, 0.73, 0.74, 0.75, 0.76, 0.77, 0.78, 0.79,
  0.8, 0.81, 0.82, 0.83, 0.84, 0.85, 0.86, 0.87, 0.88, 0.89,
  0.9, 0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99,
] as const;

export type LambdaValue = (typeof LAMBDA_VALUES)[number];

/**
 * Get the path to a TopoJSON file for a given lambda value.
 * Files are served from /half-america/data/ in production.
 */
export const getTopoJsonPath = (lambda: LambdaValue): string =>
  `${import.meta.env.BASE_URL}data/lambda_${lambda.toFixed(2)}.json`;
```

#### 2. Lambda Slider Component
**File**: `web/src/components/LambdaSlider.tsx`
**Changes**: Update `toFixed(1)` to `toFixed(2)`, adjust hint thresholds

```typescript
// Line 35: Update aria-valuemax
aria-valuemax={0.99}

// Line 37: Update aria-valuetext precision
aria-valuetext={`Lambda ${value.toFixed(2)}`}

// Line 39: Update display precision
<span className="lambda-value">{value.toFixed(2)}</span>

// Lines 42-44: Adjust hint thresholds (proportionally same at 30%/70%)
{value < 0.30 ? 'Minimizes area (more fragmented)' :
 value > 0.70 ? 'Minimizes perimeter (smoother shapes)' :
 'Balanced optimization'}
```

#### 3. App Component
**File**: `web/src/App.tsx`
**Changes**: Update layer ID precision

```typescript
// Line 39: Update layer ID to use 2 decimals
id: `layer-${lambda.toFixed(2)}`,
```

#### 4. TopoJSON Loader Hook
**File**: `web/src/hooks/useTopoJsonLoader.ts`
**Changes**: Update error message precision

```typescript
// Line 53: Update error message
throw new Error(`Failed to load lambda_${lambda.toFixed(2)}.json: ${response.status}`);
```

### Success Criteria

#### Automated Verification:
- [ ] TypeScript compiles: `cd web && npm run build`
- [ ] Linting passes: `cd web && npm run lint`
- [ ] No runtime errors in dev server: `cd web && npm run dev`

#### Manual Verification:
- [ ] Slider displays values with 2 decimal places (e.g., "0.50" not "0.5")
- [ ] Slider has 100 discrete positions
- [ ] Map updates correctly when moving slider
- [ ] All 100 lambda values load and display correctly

**Implementation Note**: After completing this phase, test locally before proceeding. Load time may be slow (~10-20s) - this is expected and addressed in Phase 3.

---

## Phase 3: Performance Assessment

### Overview
Measure actual load time with 100 files and determine if optimization is needed.

### Testing Procedure

1. **Build and serve production build**:
   ```bash
   cd web
   npm run build
   npm run preview
   ```

2. **Measure load time**:
   - Open browser DevTools → Network tab
   - Hard refresh (Cmd+Shift+R)
   - Note total time until "Loading" overlay disappears
   - Test on both fast connection and throttled (3G)

3. **Record metrics**:
   - Total load time (fast connection)
   - Total load time (slow 3G)
   - Total transferred size
   - Number of requests

### Decision Criteria

| Load Time (Fast) | Action |
|------------------|--------|
| < 3 seconds | No optimization needed, skip Phase 4 |
| 3-5 seconds | Acceptable, Phase 4 optional |
| > 5 seconds | Proceed to Phase 4 |

### Success Criteria

#### Manual Verification:
- [ ] Load time measured and documented
- [ ] Decision made: proceed to Phase 4 or skip

---

## Phase 4: Performance Optimization (Conditional)

### Overview
If load time exceeds 5 seconds, implement parallel HTTP requests to speed up loading.

### Changes Required

#### 1. Parallel Loading in useTopoJsonLoader.ts
**File**: `web/src/hooks/useTopoJsonLoader.ts`
**Changes**: Replace sequential loading with `Promise.all` batched parallel requests

```typescript
async function performLoad() {
  cachedState = { status: 'loading', loaded: 0, total: LAMBDA_VALUES.length };
  notifyListeners();

  const dataMap = new Map<LambdaValue, FeatureCollection<Geometry, HalfAmericaProperties>>();

  try {
    // Load all files in parallel with batching to avoid overwhelming the browser
    const BATCH_SIZE = 10; // 10 concurrent requests at a time
    const batches: LambdaValue[][] = [];

    for (let i = 0; i < LAMBDA_VALUES.length; i += BATCH_SIZE) {
      batches.push(LAMBDA_VALUES.slice(i, i + BATCH_SIZE) as LambdaValue[]);
    }

    let loadedCount = 0;
    for (const batch of batches) {
      const results = await Promise.all(
        batch.map(async (lambda) => {
          const geojson = await loadSingleTopoJSON(lambda);
          return { lambda, geojson };
        })
      );

      for (const { lambda, geojson } of results) {
        dataMap.set(lambda, geojson);
      }

      loadedCount += batch.length;
      cachedState = { status: 'loading', loaded: loadedCount, total: LAMBDA_VALUES.length };
      notifyListeners();
    }

    cachedState = { status: 'success', data: dataMap };
  } catch (err) {
    cachedState = { status: 'error', error: err instanceof Error ? err : new Error(String(err)) };
  }

  loadPromise = null;
  notifyListeners();
}
```

### Success Criteria

#### Automated Verification:
- [ ] TypeScript compiles: `cd web && npm run build`
- [ ] No runtime errors: `cd web && npm run dev`

#### Manual Verification:
- [ ] Load time reduced to <5 seconds
- [ ] Progress indicator still updates smoothly
- [ ] All 100 files load correctly
- [ ] No browser console errors

---

## Testing Strategy

### Unit Tests
No new unit tests required - this is primarily a configuration change.

### Integration Tests
- Verify all 100 TopoJSON files parse correctly
- Verify slider traverses all 100 values

### Manual Testing Steps
1. Load the application fresh (clear cache)
2. Verify loading overlay shows progress (0/100 → 100/100)
3. Move slider from 0.00 to 0.99, verify smooth stepping
4. Verify map updates at each position
5. Check that lambda value display shows 2 decimal places
6. Test on mobile device (responsive layout)
7. Test on slow connection (3G throttle)

## Performance Considerations

- **Memory**: 100 FeatureCollections in memory (~50-100 MB depending on geometry complexity)
- **deck.gl layers**: 100 layers created, only 1 visible at a time (deck.gl handles this efficiently)
- **Initial load**: Target <5 seconds; parallel loading achieves ~3-5x speedup over sequential

## Migration Notes

- Old 10-value files should be removed from `web/public/data/` before copying new files
- Existing `sweep_2024_2022_0.1.pkl` cache remains valid (different filename)
- No database or API changes required

## References

- Research document: `thoughts/shared/research/2025-11-23-fine-lambda-granularity.md`
- ROADMAP.md Phase 6: "Fine λ granularity: Move to 0.01 increments (100 values) for smooth animations"
- deck.gl feasibility: `thoughts/shared/research/2025-11-22-deck-gl-feasibility.md`
