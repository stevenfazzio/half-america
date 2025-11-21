---
date: 2025-11-21T12:00:00-08:00
researcher: Claude
git_commit: 7514a6988003d8d39d93491c705e568cb0750dec
branch: master
repository: half_america
topic: "Pre-compute results for discrete λ values (e.g., 0.0, 0.1, 0.2, ..., 1.0)"
tags: [research, codebase, optimization, lambda, precomputation, caching]
status: complete
last_updated: 2025-11-21
last_updated_by: Claude
---

# Research: Pre-compute Results for Discrete λ Values

**Date**: 2025-11-21T12:00:00-08:00
**Researcher**: Claude
**Git Commit**: 7514a6988003d8d39d93491c705e568cb0750dec
**Branch**: master
**Repository**: half_america

## Research Question

How should we implement "Pre-compute results for discrete λ values (e.g., 0.0, 0.1, 0.2, ..., 1.0)" as specified in ROADMAP.md Phase 3?

## Summary

The core optimization logic for sweeping λ values is **already implemented** in `sweep_lambda()`. What's missing is **persistence of results** - saving computed partitions to disk so the web frontend can load them without re-running optimization. The implementation requires:

1. **Serialization format** for `SweepResult` data (partition arrays + metadata)
2. **CLI command** to trigger pre-computation
3. **Output structure** aligned with Phase 4's TopoJSON export needs

## Detailed Findings

### Current Implementation Status

The ROADMAP.md milestone checklist shows:

| Milestone | Status |
|-----------|--------|
| Add PyMaxFlow dependency | ✅ Complete |
| Implement graph-cut solver wrapper | ✅ Complete |
| Implement binary search for μ | ✅ Complete |
| Build outer loop for λ parameter sweep | ✅ Complete |
| **Pre-compute results for discrete λ values** | ❌ **Not started** |
| Performance benchmarking and optimization | ❌ Not started |
| Unit tests for optimization correctness | ❌ Not started |

### What "Pre-compute" Means in Context

From METHODOLOGY.md Section 3.2 and Phase 5 requirements:

1. **Outer Loop (User Slider):** Iterate through λ values (0.0, 0.1, ..., 1.0)
2. **Web Frontend Need:** "Load and display pre-computed TopoJSON geometries"
3. **Animation Support:** Future enhancement mentions "Animate the λ sweep from dusty (λ=0) to smooth (λ=1)"

Pre-computation means running the full optimization sweep **offline** and saving results so the web frontend can instantly load geometries for any λ value without waiting for computation.

### Existing Components

#### 1. Lambda Sweep (`src/half_america/optimization/sweep.py`)

The `sweep_lambda()` function already handles the core computation:

```python
# sweep.py:56-63
def sweep_lambda(
    graph_data: GraphData,
    lambda_values: list[float] | None = None,  # defaults to [0.0, 0.1, ..., 1.0]
    target_fraction: float = 0.5,
    tolerance: float = 0.01,
    max_workers: int | None = None,  # parallel execution
    verbose: bool = True,
) -> SweepResult:
```

**Key features already implemented:**
- Parallel execution via `ThreadPoolExecutor` (sweep.py:96-138)
- Default λ values: `[0.0, 0.1, 0.2, ..., 1.0]` (sweep.py:30)
- Per-λ timing tracking (sweep.py:33-53)
- Early termination on convergence failure (sweep.py:124-132)

#### 2. Result Data Structures

`SweepResult` (sweep.py:19-26) contains all computed data:

```python
class SweepResult(NamedTuple):
    results: dict[float, LambdaResult]  # λ → result mapping
    lambda_values: list[float]          # ordered λ values
    total_iterations: int
    total_elapsed_seconds: float
    all_converged: bool
```

Each `LambdaResult` contains:
- `search_result.result.partition: np.ndarray` - Boolean array of selected tracts

#### 3. Caching Patterns

The codebase has established caching patterns in `src/half_america/data/cache.py`:

| Data Type | Format | Location |
|-----------|--------|----------|
| TIGER geometry | GeoParquet | `data/cache/raw/tiger/` |
| Census population | Parquet | `data/cache/raw/census/` |
| Graph data | Pickle | `data/cache/processed/graph_{year}_{year}.pkl` |
| **Optimization results** | **Not implemented** | — |

### What's Missing

#### 1. Result Serialization

No code exists to persist `SweepResult` to disk. Options:

**Option A: Pickle (simple)**
```python
# Matches existing graph caching pattern
def save_sweep_result(result: SweepResult, path: Path) -> None:
    with open(path, "wb") as f:
        pickle.dump(result, f)
```

**Option B: Structured format (Phase 4 aligned)**
```
data/cache/processed/sweep_{tiger}_{acs}/
├── metadata.json          # λ values, timestamps, convergence info
├── lambda_0.0.parquet     # partition array + statistics
├── lambda_0.1.parquet
├── ...
└── lambda_1.0.parquet
```

#### 2. CLI Command

The current CLI (`src/half_america/__init__.py:1-2`) is a placeholder:

```python
def main() -> None:
    print("Hello from half-america!")
```

A pre-compute command would look like:

```python
# Example CLI structure (not implemented)
uv run half-america precompute --output data/precomputed/
uv run half-america precompute --lambda-step 0.05  # finer granularity
```

#### 3. Integration with Phase 4

Phase 4 (Post-Processing) expects partition results as input:

1. **Dissolve:** Merge selected tracts into MultiPolygon
2. **Filter:** Remove small disconnected islands
3. **Simplify:** Visvalingam-Whyatt for web performance
4. **Export:** TopoJSON format

The pre-compute step should either:
- Save raw partitions (let Phase 4 process them), OR
- Perform full pipeline through TopoJSON export

### Recommended Implementation Approach

#### Phase 1: Basic Persistence

1. Add `save_sweep_result()` and `load_sweep_result()` to sweep.py
2. Use pickle format (matches existing patterns)
3. Cache key: `sweep_{TIGER_YEAR}_{ACS_YEAR}_{step}.pkl` where step is λ increment

#### Phase 2: CLI Integration

1. Add `click` or `typer` dependency for CLI framework
2. Create `precompute` subcommand
3. Options: `--output`, `--lambda-step`, `--force-rebuild`

#### Phase 3: Structured Export

1. Save individual λ results as separate files
2. Include tract GEOIDs for geometry reconstruction
3. Add metadata file with versioning info

### Code References

| Component | Location | Description |
|-----------|----------|-------------|
| `sweep_lambda()` | `src/half_america/optimization/sweep.py:56` | Main sweep function |
| `SweepResult` | `src/half_america/optimization/sweep.py:19` | Result container |
| `DEFAULT_LAMBDA_VALUES` | `src/half_america/optimization/sweep.py:30` | Default [0.0-1.0] |
| `_run_single_lambda()` | `src/half_america/optimization/sweep.py:33` | Per-λ worker |
| Graph caching pattern | `src/half_america/graph/pipeline.py:51-78` | Example pickle caching |
| Cache paths | `src/half_america/data/cache.py:24-26` | `get_processed_cache_path()` |
| CLI entry | `src/half_america/__init__.py:1-2` | Placeholder main() |

### Architecture Insights

1. **Separation of concerns:** The sweep computes partitions, Phase 4 converts to geometries. Pre-compute should save partitions, not geometries.

2. **Versioning:** Cache keys should include data years (TIGER_YEAR, ACS_YEAR) since partitions depend on source data.

3. **Granularity:** Default 0.1 step (11 values) is reasonable for initial implementation. ROADMAP mentions "Fine λ granularity: Support 0.01 increments (101 values)" as future enhancement.

4. **File format:** Pickle is simple but not portable. Consider Parquet for partition arrays if cross-language access needed.

### Historical Context (from thoughts/)

Related research documents:

| Document | Key Content |
|----------|-------------|
| `thoughts/shared/research/2025-11-21-lambda-parameter-sweep.md` | Original sweep research; mentions pre-computation as orchestration layer |
| `thoughts/shared/plans/2025-11-21-lambda-parameter-sweep.md` | Implementation plan for `sweep_lambda()` |
| `thoughts/shared/research/2025-11-21-lambda-edge-cases.md` | Confirms λ=0 and λ=1 work correctly |

### Related Research

- `thoughts/shared/research/2025-11-21-binary-search-lagrange-multiplier.md` - Inner loop optimization
- `thoughts/shared/research/2025-11-21-solver-wrapper-implementation.md` - Graph cut solver

## Open Questions

1. **Output format:** Should pre-compute save raw partitions (tract indices) or processed geometries (dissolved MultiPolygon)?

2. **Versioning strategy:** How to handle cache invalidation when source data or algorithm changes?

3. **Incremental updates:** If user wants λ=0.05 (not in default set), should we support adding to existing cache?

4. **Memory constraints:** For 73,000 tracts × 11 λ values, what's the expected file size? (Estimate: ~3MB per partition × 11 = ~33MB total)

5. **CLI framework:** Should we use `click`, `typer`, or `argparse` for the command-line interface?

## Implementation Checklist

- [ ] Add `save_sweep_result()` function to sweep.py
- [ ] Add `load_sweep_result()` function to sweep.py
- [ ] Add cache path helper `get_sweep_cache_path()` to cache.py
- [ ] Add CLI framework dependency (click/typer) to pyproject.toml
- [ ] Implement `precompute` CLI command
- [ ] Add `--lambda-values` and `--output` CLI options
- [ ] Write unit tests for serialization
- [ ] Write integration test for full pre-compute pipeline
- [ ] Update ROADMAP.md milestone as complete
