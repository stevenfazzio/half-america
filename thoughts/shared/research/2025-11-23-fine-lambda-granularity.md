---
date: 2025-11-23T12:00:00-08:00
researcher: Claude
git_commit: b193fd9817af3be73196f4cac3c04859c1359297
branch: master
repository: half-america
topic: "Fine lambda granularity: Move to 0.01 increments (100 values) for smooth animations"
tags: [research, codebase, lambda, granularity, animation, performance, phase-6]
status: complete
last_updated: 2025-11-23
last_updated_by: Claude
---

# Research: Fine Lambda Granularity (100 Values)

**Date**: 2025-11-23T12:00:00-08:00
**Researcher**: Claude
**Git Commit**: b193fd9817af3be73196f4cac3c04859c1359297
**Branch**: master
**Repository**: half-america

## Research Question

What changes are needed to implement "Fine lambda granularity: Move to 0.01 increments (100 values) for smooth animations" from ROADMAP.md Phase 6?

## Summary

The backend already supports arbitrary lambda step sizes via the `--lambda-step` CLI option. The primary work is:
1. **Backend**: Run precompute and export with `--lambda-step 0.01` (~15-25 minutes one-time)
2. **Frontend**: Update `LAMBDA_VALUES` array and `toFixed()` precision from 1 to 2 decimal places
3. **Performance optimization**: Consider chunked loading strategy (10 files x 10 values) to avoid UI jank

**Key insight**: True polygon morphing animation is not practical because polygon counts and vertex indices differ between lambda values. The 100 values enable smoother *slider stepping*, not animated transitions.

## Detailed Findings

### Current State (10 Values)

| Component | Current Value | Location |
|-----------|--------------|----------|
| Lambda values | `[0.0, 0.1, ..., 0.9]` | `web/src/types/lambda.ts:5` |
| File naming | `lambda_X.X.json` | `web/src/types/lambda.ts:14` |
| Slider precision | `toFixed(1)` | `LambdaSlider.tsx:37,39` |
| CLI default | `--lambda-step 0.1` | `cli.py:39` |
| Precompute cache | `sweep_2024_2022_0.1.pkl` | `data/cache/processed/` |
| Total file size | ~2.3 MB | 10 TopoJSON files |

### Backend Changes Required

The backend is **already designed to support arbitrary step sizes**. No code changes needed.

**To generate 100 values:**
```bash
# Precompute optimization results (one-time, ~15-25 minutes)
uv run half-america precompute --lambda-step 0.01

# Export TopoJSON files (100 files)
uv run half-america export --lambda-step 0.01

# Copy to web directory
cp data/output/topojson/lambda_*.json web/public/data/
```

**Implementation details:**
- `src/half_america/cli.py:63-64` generates values: `[round(i * 0.01, 2) for i in range(100)]`
- New cache file: `sweep_2024_2022_0.01.pkl` (does not conflict with existing)
- Output files: `lambda_0.00.json`, `lambda_0.01.json`, ..., `lambda_0.99.json`

### Frontend Changes Required

| File | Line | Current | Change To |
|------|------|---------|-----------|
| `web/src/types/lambda.ts` | 5 | 10-value array | 100-value array |
| `web/src/types/lambda.ts` | 14 | `toFixed(1)` | `toFixed(2)` |
| `web/src/components/LambdaSlider.tsx` | 37 | `toFixed(1)` | `toFixed(2)` |
| `web/src/components/LambdaSlider.tsx` | 39 | `toFixed(1)` | `toFixed(2)` |
| `web/src/App.tsx` | 39 | `toFixed(1)` | `toFixed(2)` |
| `web/src/components/LambdaSlider.tsx` | 42-44 | Thresholds 0.3/0.7 | Adjust appropriately |

**Example `types/lambda.ts` change:**
```typescript
// Current
export const LAMBDA_VALUES = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9] as const;

// New (can be generated programmatically)
export const LAMBDA_VALUES = Array.from({ length: 100 }, (_, i) => i * 0.01) as const;
// Or explicit for type safety: [0.0, 0.01, 0.02, ..., 0.99]
```

### Performance Considerations

#### Precomputation Time

| Metric | 10 Values | 100 Values (Projected) |
|--------|-----------|------------------------|
| Time per lambda | ~1.0-1.5s | ~1.0-1.5s |
| Total time (parallel) | ~10-15s | ~100-150s |
| Cache file size | ~5 MB | ~50 MB |

The sweep uses `ThreadPoolExecutor` for parallelization (`src/half_america/optimization/sweep.py:103-114`), so actual wall-clock time depends on CPU cores.

#### TopoJSON File Sizes

| Metric | 10 Values | 100 Values (Projected) |
|--------|-----------|------------------------|
| Files | 10 | 100 |
| Total size | ~2.3 MB | ~23 MB |
| Per-file average | ~230 KB | ~230 KB |

#### Frontend Loading Concerns

**Current approach** (`useTopoJsonLoader.ts`):
- Sequential HTTP requests (one per lambda value)
- All files held in memory as FeatureCollections
- All deck.gl layers created upfront

**Impact of 100 files:**
| Concern | 10 Files | 100 Files |
|---------|----------|-----------|
| HTTP requests | 10 sequential | 100 sequential |
| Load time | ~1-2s | ~10-20s |
| Memory | ~10 FeatureCollections | ~100 FeatureCollections |
| deck.gl layers | 10 | 100 |

#### Recommended Optimization: Chunked Loading

From prior research (`thoughts/shared/research/2025-11-22-subphase-5-2-core-visualization.md`), a **chunked file strategy** is recommended:

**Option A: 10 Combined Files (Recommended)**
- Create 10 combined files, each containing 10 lambda values
- `chunk_0.json` contains λ = 0.00-0.09
- `chunk_1.json` contains λ = 0.10-0.19
- etc.

**Benefits:**
- Parse time ~15-30ms per chunk (under 50ms jank threshold)
- Time to first frame: ~100-200ms (first chunk only)
- Natural preloading: load current chunk, prefetch adjacent
- Memory efficiency: can evict unused chunks

**Option B: On-Demand Loading**
- Load only current lambda value
- Prefetch adjacent values in background
- Cache recently used values

### Animation Clarification

**Important limitation** from deck.gl research:

True polygon morphing between lambda values is **not feasible** because:
- Polygon counts differ between lambda values (e.g., λ=0.0 has many small regions, λ=0.9 has few large blobs)
- Vertex indices don't correspond between datasets
- Morphing requires 1:1 vertex correspondence

**What "smooth animations" actually means:**
- Smoother slider stepping (100 discrete steps vs 10)
- Less visual "jump" between adjacent lambda values
- Potentially fade transitions (opacity) between swaps

## Code References

### Backend
- `src/half_america/cli.py:37-41` - `--lambda-step` CLI option
- `src/half_america/cli.py:62-64` - Lambda value generation
- `src/half_america/optimization/sweep.py:31-33` - `DEFAULT_LAMBDA_VALUES`
- `src/half_america/postprocess/export.py:142` - Output file naming
- `src/half_america/data/cache.py:30-41` - Cache path with lambda_step

### Frontend
- `web/src/types/lambda.ts:5` - `LAMBDA_VALUES` constant
- `web/src/types/lambda.ts:13-14` - `getTopoJsonPath()` function
- `web/src/components/LambdaSlider.tsx:28-31` - Slider range configuration
- `web/src/hooks/useTopoJsonLoader.ts:80-104` - Sequential loading logic
- `web/src/App.tsx:36-49` - Layer creation per lambda value

### Tests
- `tests/test_optimization/test_sweep.py:55-58` - Tests `DEFAULT_LAMBDA_VALUES`
- `tests/test_postprocess/test_export.py:122` - Tests all lambda export

## Architecture Insights

### Design Decisions
1. **Lambda step as CLI parameter** - Allows flexible granularity without code changes
2. **Separate cache files per step** - `sweep_2024_2022_0.1.pkl` vs `sweep_2024_2022_0.01.pkl` coexist
3. **Hardcoded frontend array** - Type-safe but requires manual sync with backend
4. **Pre-load all layers** - Prioritizes instant slider response over initial load time

### Patterns
- `NamedTuple` for immutable result types throughout
- Module-level singleton pattern in `useTopoJsonLoader.ts` for shared cache
- `useSyncExternalStore` for React integration with external state

## Historical Context (from thoughts/)

| Document | Key Insight |
|----------|-------------|
| `thoughts/shared/plans/2025-11-21-lambda-parameter-sweep.md` | Finer granularity was explicitly deferred to Future Enhancements |
| `thoughts/shared/plans/2025-11-22-subphase-5-2-core-visualization.md` | "100-value lambda granularity" deferred to Phase 6 |
| `thoughts/shared/research/2025-11-22-subphase-5-2-core-visualization.md` | Chunked loading strategy analysis |
| `thoughts/shared/research/2025-11-22-deck-gl-feasibility.md` | Animation limitations for polygon morphing |

## Related Research

- [2025-11-22-subphase-5-2-core-visualization.md](2025-11-22-subphase-5-2-core-visualization.md) - 100-file loading strategy analysis
- [2025-11-22-deck-gl-feasibility.md](2025-11-22-deck-gl-feasibility.md) - deck.gl animation capabilities
- [2025-11-21-benchmark-baselines.md](2025-11-21-benchmark-baselines.md) - Performance timing data

## Implementation Recommendations

### Phase 1: Backend (Minimal Change)
```bash
# Run precomputation with fine granularity
uv run half-america precompute --lambda-step 0.01 --force

# Export all 100 TopoJSON files
uv run half-america export --lambda-step 0.01 --force

# Copy to web public directory
cp data/output/topojson/lambda_*.json web/public/data/
```

### Phase 2: Frontend Updates
1. Update `LAMBDA_VALUES` array to 100 values
2. Change all `toFixed(1)` to `toFixed(2)`
3. Test slider behavior and performance

### Phase 3: Performance Optimization (If Needed)
1. Monitor initial load time with 100 files
2. If >3-5s, implement chunked loading strategy
3. Consider on-demand loading with prefetching

## Open Questions

1. **Actual precomputation time**: Need to benchmark with `--lambda-step 0.01` to get real timing
2. **File size variance**: Do lambda values near 0.0 produce larger files than 0.9?
3. **Mobile performance**: How does 100-file loading perform on mobile devices?
4. **Chunk boundaries**: If chunking, should chunks overlap for smoother prefetching?
5. **Type generation**: Should `LAMBDA_VALUES` be generated programmatically or remain explicit for type safety?
