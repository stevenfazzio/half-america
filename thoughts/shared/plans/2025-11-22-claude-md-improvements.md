# CLAUDE.md Improvements Implementation Plan

## Overview

Expand CLAUDE.md from 49 to ~100 lines by adding sections for cache management, data directory structure, and common gotchas, plus expanding existing commands section. This addresses known pain points: stale caches and API parameter confusion.

## Current State Analysis

CLAUDE.md currently has 49 lines covering:
- Project Overview (~10 lines)
- Naming Convention (~4 lines)
- Commands (~12 lines) - basic pytest, ruff, mypy, CLI
- Architecture (~12 lines) - stack, algorithm, parameters
- Documentation (~5 lines) - links to other docs

### Key Gaps (from research):
- No cache management guidance (5 cache layers exist)
- No `lambda_param` naming convention note
- No data directory structure explanation
- Limited test commands (missing `-m`, `-k` patterns)
- No common gotchas section

## Desired End State

CLAUDE.md expanded to ~100 lines with:
1. **Cache Management** section explaining how to clear stale caches
2. **Data Files** section showing directory structure
3. **Common Gotchas** section preventing frequent mistakes
4. Expanded **Commands** section with test filtering
5. Enhanced **Key Parameters** with `lambda_param` note

### Verification:
- `wc -l CLAUDE.md` shows ~100 lines (90-110 acceptable)
- All 5 cache locations documented
- `lambda_param` naming convention explained
- Test filtering commands (`-m`, `-k`) included

## What We're NOT Doing

- Not duplicating full API surface (link to docs/API.md instead)
- Not adding extensive troubleshooting section
- Not exceeding ~100 lines target
- Not restructuring existing sections that work well

## Implementation Approach

Single-phase edit to CLAUDE.md, adding content in logical order to maintain readability.

## Phase 1: Update CLAUDE.md

### Overview
Add 4 new sections and expand 2 existing sections in CLAUDE.md.

### Changes Required:

#### 1. Expand Commands Section
**File**: `CLAUDE.md`
**Location**: After existing commands block (line 27)
**Changes**: Add test filtering and cache clearing commands

Add after existing commands:
```markdown
# Test filtering
uv run pytest -m "not integration"   # Skip network-dependent tests
uv run pytest -k "dissolve"          # Run tests matching pattern

# Cache management
rm -rf data/cache/                   # Clear all caches
rm -rf data/cache/processed/         # Clear processed only (keeps downloads)
```

#### 2. Add Cache Management Section
**File**: `CLAUDE.md`
**Location**: After Commands section
**Changes**: New section explaining cache structure and clearing

```markdown
## Cache Management

The `data/` directory (gitignored) contains cached data at multiple levels:

| Cache | Location | When to Clear |
|-------|----------|---------------|
| HTTP requests | `data/cache/requests_cache.sqlite` | API issues |
| TIGER shapefiles | `data/cache/raw/tiger/` | Year config change |
| Census data | `data/cache/raw/census/` | Year config change |
| Processed tracts | `data/cache/processed/*.parquet` | Source data change |
| Graph/sweep | `data/cache/processed/*.pkl` | Algorithm change |

**Force rebuild:** Use `--force` flag with CLI commands, or `force_rebuild=True` in Python API.
```

#### 3. Add Data Files Section
**File**: `CLAUDE.md`
**Location**: After Cache Management section
**Changes**: New section showing directory structure

```markdown
## Data Files

```
data/                          # Gitignored
├── cache/
│   ├── raw/
│   │   ├── tiger/             # TIGER shapefiles (*.parquet)
│   │   └── census/            # Census population (*.parquet)
│   ├── processed/             # Merged data, graphs, sweeps
│   └── requests_cache.sqlite  # HTTP cache
└── output/
    └── topojson/              # Exported results
```

Cache filenames include year keys: `{name}_{TIGER_YEAR}_{ACS_YEAR}.ext`
Year constants in `src/half_america/config.py`: `TIGER_YEAR=2024`, `ACS_YEAR=2022`
```

#### 4. Add Common Gotchas Section
**File**: `CLAUDE.md`
**Location**: After Architecture section (before Documentation)
**Changes**: New section with key pitfalls

```markdown
## Common Gotchas

**Parameter naming:** Use `lambda_param` not `lambda` in Python code (reserved word). Use `mu` for Lagrange multiplier.

**Lambda range:** λ must be in [0, 1). λ=1.0 raises `ValueError` because it causes zero area cost and convergence failure.

**Stale caches:** If you change `TIGER_YEAR`/`ACS_YEAR` in config.py, old caches remain orphaned. Clear with `rm -rf data/cache/`.

**Imports:** Use absolute imports only: `from half_america.data import load_all_tracts`
```

#### 5. Full Updated CLAUDE.md

The complete file should be:

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Half of America is a topology optimization experiment that creates an interactive visualization of US population distribution. Instead of simple county-level "half of America lives here" maps, this project uses Census Tract data (~73,000 tracts) with Max-Flow Min-Cut optimization to generate smooth, organic shapes controlled by a "surface tension" parameter (λ).

**Naming Convention:**
- Repository/PyPI: `half-america` (hyphenated)
- Python module: `half_america` (underscored)
- CLI command: `half-america`

## Commands

Common commands (see [README.md#usage](README.md#usage) for full list):

```bash
uv sync                              # Install dependencies
uv run pytest                        # Run tests
uv run pytest path/to/test.py -v     # Run single test
uv run pytest -m "not integration"   # Skip network-dependent tests
uv run pytest -k "dissolve"          # Run tests matching pattern
uv run ruff format src/ tests/       # Format code
uv run ruff check src/ tests/        # Lint
uv run mypy src/                     # Type check
uv run half-america                  # Run CLI
uv run half-america precompute       # Pre-compute optimization results
```

## Cache Management

The `data/` directory (gitignored) contains cached data at multiple levels:

| Cache | Location | When to Clear |
|-------|----------|---------------|
| HTTP requests | `data/cache/requests_cache.sqlite` | API issues |
| TIGER shapefiles | `data/cache/raw/tiger/` | Year config change |
| Census data | `data/cache/raw/census/` | Year config change |
| Processed tracts | `data/cache/processed/*.parquet` | Source data change |
| Graph/sweep | `data/cache/processed/*.pkl` | Algorithm change |

```bash
rm -rf data/cache/                   # Clear all caches
rm -rf data/cache/processed/         # Clear processed only (keeps downloads)
```

**Force rebuild:** Use `--force` flag with CLI commands, or `force_rebuild=True` in Python API.

## Data Files

```
data/                          # Gitignored
├── cache/
│   ├── raw/
│   │   ├── tiger/             # TIGER shapefiles (*.parquet)
│   │   └── census/            # Census population (*.parquet)
│   ├── processed/             # Merged data, graphs, sweeps
│   └── requests_cache.sqlite  # HTTP cache
└── output/
    └── topojson/              # Exported results
```

Cache filenames include year keys: `{name}_{TIGER_YEAR}_{ACS_YEAR}.ext`
Year constants in `src/half_america/config.py`: `TIGER_YEAR=2024`, `ACS_YEAR=2022`

## Architecture

**Implementation Stack (from METHODOLOGY.md):**
- **Data Ingestion:** pandas, cenpy (Census API) - *implemented*
- **Spatial Logic:** geopandas, libpysal (adjacency graph building) - *implemented*
- **Optimization:** PyMaxFlow (C++ graph cuts wrapper) - *implemented*
- **Geometry Operations:** shapely, topojson - *implemented*
- **Web Frontend:** React, Mapbox GL JS - *Phase 5*

**Core Algorithm:** The optimization uses Lagrangian relaxation with binary search to find the Lagrange multiplier (μ) that satisfies the 50% population constraint. The graph construction uses s-t cut with neighborhood edges (n-links) for boundary costs and terminal edges (t-links) for area costs and population rewards.

**Key Parameters:**
- λ (lambda): User-controlled surface tension [0,1). λ≈0 minimizes area (dusty map), λ≈0.9 minimizes perimeter (smooth blobs). λ=1.0 is excluded (causes convergence failure).
- μ (mu): Lagrange multiplier tuned via binary search to hit 50% population target

## Common Gotchas

**Parameter naming:** Use `lambda_param` not `lambda` in Python code (reserved word). Use `mu` for Lagrange multiplier.

**Lambda range:** λ must be in [0, 1). λ=1.0 raises `ValueError` because it causes zero area cost and convergence failure.

**Stale caches:** If you change `TIGER_YEAR`/`ACS_YEAR` in config.py, old caches remain orphaned. Clear with `rm -rf data/cache/`.

**Imports:** Use absolute imports only: `from half_america.data import load_all_tracts`

## Documentation

- [README.md](README.md) - Project overview, installation, and usage
- [docs/API.md](docs/API.md) - Python API reference
- [METHODOLOGY.md](METHODOLOGY.md) - Mathematical formulation and algorithm details
- [ROADMAP.md](ROADMAP.md) - Implementation phases and roadmap
```

### Success Criteria:

#### Automated Verification:
- [x] File exists and is valid markdown: `cat CLAUDE.md`
- [x] Line count in target range: `wc -l CLAUDE.md` shows 90-110 lines (97 lines)
- [x] No broken internal references (links to existing files)

#### Manual Verification:
- [x] Cache table is readable and accurate
- [x] Directory tree renders correctly
- [x] Commands are copy-pasteable
- [x] Common Gotchas section is helpful

**Implementation Note**: This is a single-phase documentation update. After completing the edit, verify line count and readability.

---

## Testing Strategy

### Automated:
- Verify file exists and has expected line count
- Confirm all linked files exist (README.md, docs/API.md, METHODOLOGY.md, ROADMAP.md)

### Manual:
- Read through updated CLAUDE.md for clarity
- Verify cache paths match actual config.py
- Test that commands work as documented

## References

- Research document: `thoughts/shared/research/2025-11-22-claude-md-improvement-opportunities.md`
- Current config: `src/half_america/config.py:14-29`
- Pytest markers: `pyproject.toml:61-64`
