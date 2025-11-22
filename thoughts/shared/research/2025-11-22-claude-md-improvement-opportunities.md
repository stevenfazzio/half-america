---
date: 2025-11-22T00:00:00-05:00
researcher: Claude
git_commit: 0b79d6ec5270900c34b9b2bdeadfdc34696b68ac
branch: master
repository: half-america
topic: "CLAUDE.md Improvement Opportunities"
tags: [research, documentation, claude-md, developer-experience]
status: complete
last_updated: 2025-11-22
last_updated_by: Claude
---

# Research: CLAUDE.md Improvement Opportunities

**Date**: 2025-11-22
**Researcher**: Claude
**Git Commit**: 0b79d6ec5270900c34b9b2bdeadfdc34696b68ac
**Branch**: master
**Repository**: half-america

## Research Question

What information should be added to CLAUDE.md to prevent common mistakes and improve typical workflows? Current CLAUDE.md is 49 lines; target is ~100 lines. Known pain points include stale caches and API confusion.

## Summary

The research identified **6 high-priority additions** for CLAUDE.md:

1. **Cache Management** - How to clear stale caches (major pain point)
2. **Parameter Naming** - `lambda_param` not `lambda` (API confusion)
3. **Lambda Range** - λ ∈ [0, 1) excludes 1.0 (causes convergence failure)
4. **Data Directory Structure** - Where files live, what's gitignored
5. **Test Commands** - How to run specific test categories
6. **Import Conventions** - Absolute imports, NamedTuple pattern

## Detailed Findings

### 1. Cache Management (Critical)

The codebase has **5 cache layers** that can become stale:

| Cache | Location | Clear Command |
|-------|----------|---------------|
| HTTP requests | `data/cache/requests_cache.sqlite` | `rm data/cache/requests_cache.sqlite` |
| TIGER shapefiles | `data/cache/raw/tiger/*.parquet` | `rm -rf data/cache/raw/tiger/` |
| Census data | `data/cache/raw/census/*.parquet` | `rm -rf data/cache/raw/census/` |
| Processed tracts | `data/cache/processed/all_tracts_*.parquet` | `rm data/cache/processed/all_tracts_*.parquet` |
| Graph data | `data/cache/processed/graph_*.pkl` | `rm data/cache/processed/graph_*.pkl` |
| Sweep results | `data/cache/processed/sweep_*.pkl` | `rm data/cache/processed/sweep_*.pkl` |

**Stale Cache Scenarios:**
- If `config.py` years change (TIGER_YEAR/ACS_YEAR), old caches remain but are orphaned
- If tract data changes, graph cache becomes stale (no content hash verification)
- CLI `--force` flag only rebuilds sweep cache, not upstream data

**Recommended CLAUDE.md Addition:**
```markdown
## Cache Management

Clear all caches: `rm -rf data/cache/`
Clear processed only: `rm -rf data/cache/processed/`

Use `--force` flag with CLI commands to rebuild specific caches.
Programmatic bypass: `force_download=True`, `force_rebuild=True`, `use_cache=False`
```

### 2. Parameter Naming Convention (API Confusion)

The Greek letter λ is used in documentation, but code uses `lambda_param` (since `lambda` is reserved):

| Context | Name Used |
|---------|-----------|
| Docstrings/math | λ |
| Function params | `lambda_param` |
| NamedTuple fields | `lambda_param` |
| CLI flags | `--lambda-step` |

**Common Mistake:** Writing `lambda=0.5` instead of `lambda_param=0.5`

**Recommended CLAUDE.md Addition:**
```markdown
**Parameter Naming:**
- Use `lambda_param` (not `lambda`) in code - Python reserved word
- Use `mu` for Lagrange multiplier (no `_param` suffix)
```

### 3. Lambda Range Constraint (Critical)

λ=1.0 is explicitly excluded and raises `ValueError`:

```python
# solver.py:53-57
if not 0 <= lambda_param < 1:
    raise ValueError(
        f"lambda_param must be in [0, 1), got {lambda_param}. "
        "lambda=1.0 causes convergence failure (zero area cost)."
    )
```

**Why:** At λ=1.0, sink capacity = (1-λ)*area = 0, so 100% selection is always optimal regardless of μ. Binary search cannot converge.

**Recommended CLAUDE.md Addition:**
Already partially covered but should emphasize: "λ=1.0 is excluded (causes convergence failure)."

### 4. Data Directory Structure

Current CLAUDE.md doesn't explain where data lives:

```
data/                    # Gitignored
├── cache/
│   ├── raw/
│   │   ├── tiger/       # TIGER tract geometries (*.parquet)
│   │   └── census/      # Census population data (*.parquet)
│   ├── processed/       # Merged data, graphs, sweep results
│   └── requests_cache.sqlite
└── output/
    └── topojson/        # Exported TopoJSON files
```

**Key Points:**
- Entire `data/` directory is gitignored
- Cache filenames include version keys: `{name}_{TIGER_YEAR}_{ACS_YEAR}.ext`
- Year constants in `config.py`: `TIGER_YEAR=2024`, `ACS_YEAR=2022`

### 5. Test Commands

Current CLAUDE.md only shows basic pytest. Missing:

```bash
uv run pytest -m "not integration"  # Skip network-dependent tests
uv run pytest -m integration         # Only integration tests
uv run pytest -k "dissolve"          # Run tests matching pattern
uv run pytest tests/benchmarks/ --benchmark-only  # Run benchmarks
```

**Test Organization:**
- `tests/test_graph/` - Graph construction tests
- `tests/test_optimization/` - Solver and sweep tests
- `tests/test_postprocess/` - Geometry processing tests
- `tests/benchmarks/` - Performance benchmarks
- Integration tests marked with `@pytest.mark.integration`

### 6. Import Conventions

The codebase uses specific patterns that Claude should follow:

- **Absolute imports only:** `from half_america.data import load_all_tracts`
- **NamedTuple for data classes:** All result types are NamedTuples
- **No relative imports:** Always use full path from `half_america`
- **TYPE_CHECKING for circular imports:** Use `if TYPE_CHECKING:` block

### Additional Discoveries

#### Similar Function Names (Potential Confusion)

| Pattern | Functions | Difference |
|---------|-----------|------------|
| Load | `load_state_tracts`, `load_all_tracts`, `load_graph_data`, `load_sweep_result` | Different data types |
| Download vs Fetch | `download_state_tracts` (HTTP files), `fetch_state_population` (API) | Data source |
| Single vs Batch | `dissolve_partition` vs `dissolve_all_lambdas` | One λ vs sweep |

#### Validation Edge Cases

- Empty partition raises `ValueError` in `dissolve_partition`
- Partition length must match GeoDataFrame length
- Geometry must not be empty for export
- GeoDataFrame must have CRS for cleaning

## Recommended CLAUDE.md Structure

Target: ~100 lines. Proposed sections:

1. **Project Overview** (keep existing, ~10 lines)
2. **Naming Convention** (keep existing, ~4 lines)
3. **Commands** (expand, ~15 lines)
   - Add test filtering commands
   - Add cache clearing
4. **Cache Management** (NEW, ~10 lines)
   - Directory structure
   - How to clear caches
   - Force rebuild flags
5. **Architecture** (keep existing, ~12 lines)
6. **Key Parameters** (expand, ~8 lines)
   - Add `lambda_param` naming note
   - Emphasize λ=1.0 exclusion
7. **Common Gotchas** (NEW, ~10 lines)
   - Stale cache scenarios
   - Parameter naming
   - Validation requirements
8. **Data Files** (NEW, ~8 lines)
   - Directory structure
   - Gitignored locations
9. **Documentation** (keep existing, ~5 lines)

## Code References

- `src/half_america/config.py:14-29` - Directory and year constants
- `src/half_america/data/cache.py:10-41` - Cache path utilities
- `src/half_america/optimization/solver.py:53-59` - Lambda validation
- `tests/conftest.py` - Root test fixtures
- `pyproject.toml:61-64` - Pytest markers configuration

## Architecture Insights

The codebase follows a **unidirectional dependency flow**:
```
config → data → graph → optimization → postprocess → cli
```

This prevents circular imports. The CLI uses lazy imports to avoid loading the entire dependency tree when the package is imported as a library.

## Open Questions

1. Should CLAUDE.md include the full API surface (currently in docs/API.md)?
RESPONSE: No, just a subset of especially high value (e.g. frequently used) API info, along with a link to docs/API.md for more info.
2. Should we add troubleshooting section for common errors?
RESPONSE: Only if we have good stuff to put in it.
3. Is 100 lines the right target, or should we aim for more comprehensive coverage?
RESPONSE: Let's start with ~100 lines for now.
