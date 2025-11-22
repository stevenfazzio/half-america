# README.md Restructuring Implementation Plan

## Overview

Restructure README.md to separate user-facing CLI commands from developer commands, add the missing precompute command, trim the API example, and add a cache management note. Net change: ~0 lines (better organized, same length).

## Current State Analysis

The current README.md (140 lines) mixes CLI usage commands with development commands in a single "Usage" section. The main `precompute` command is missing, and the API example includes post-processing details that belong in docs/API.md.

### Key Issues:
- `README.md:60-84` - Mixed CLI + dev commands in Usage section
- `README.md:92-123` - API example is 32 lines including post-processing
- Missing `precompute` command (the main computational workflow)
- No cache management guidance

## Desired End State

README.md will have:
1. **Usage section** - CLI commands for end users (precompute, export)
2. **Development section** - Testing, linting, type checking for contributors
3. **Trimmed API example** - Core workflow only (~20 lines), link to API.md for post-processing
4. **Cache management note** - Brief guidance under Development

**Verification**: README.md is ~140-148 lines, clearly separates user/developer concerns, includes precompute command.

## What We're NOT Doing

- Adding Project Structure section (would add ~15 lines)
- Adding Technology Stack section (redundant with METHODOLOGY.md)
- Adding Author section (GitHub shows this)
- Adding Acknowledgments section (not needed for personal project)
- Changing the Background, How It Works, or Installation sections (already good)

## Implementation Approach

Single phase with four edits to README.md. All changes are in the Usage/API sections (lines 60-125).

## Phase 1: Restructure README.md

### Overview
Reorganize Usage section, add precompute command, trim API example, add cache management.

### Changes Required:

#### 1. Replace Usage Section (lines 60-84)

**File**: `README.md`
**Lines**: 60-84
**Change**: Split into Usage (CLI for users) and Development (for contributors)

**Before** (lines 60-84):
````markdown
## Usage

```bash
# Run the CLI
uv run half-america

# Run tests
uv run pytest

# Format code
uv run ruff format src/ tests/

# Lint
uv run ruff check src/ tests/

# Type check
uv run mypy src/

# Export TopoJSON files
uv run half-america export

# Export with options
uv run half-america export --combined      # Include combined.json
uv run half-america export --force         # Overwrite existing
```
````

**After**:
````markdown
## Usage

```bash
# Pre-compute optimization results for all lambda values
uv run half-america precompute

# Precompute options
uv run half-america precompute --force          # Rebuild cache
uv run half-america precompute --lambda-step 0.05  # Finer granularity

# Export TopoJSON files
uv run half-america export

# Export options
uv run half-america export --combined      # Include combined.json
uv run half-america export --force         # Overwrite existing
```

## Development

```bash
# Run tests
uv run pytest

# Skip network-dependent tests
uv run pytest -m "not integration"

# Run tests matching pattern
uv run pytest -k "dissolve"

# Format code
uv run ruff format src/ tests/

# Lint
uv run ruff check src/ tests/

# Type check
uv run mypy src/
```

### Cache Management

Data is cached in `data/cache/`. Clear with `rm -rf data/cache/` if you encounter stale data or change year configurations in `src/half_america/config.py`.
````

**Line count change**: +12 lines (from 25 to 37 lines for this section)

#### 2. Trim API Example (lines 92-123)

**File**: `README.md`
**Lines**: 111-123 (the post-processing part)
**Change**: Remove post-processing code, add link to API.md

**Before** (lines 106-123):
```markdown
# Check results
for lambda_val, lambda_result in result.results.items():
    opt = lambda_result.search_result.result
    print(f"lambda={lambda_val:.1f}: {opt.population_fraction:.2%} selected")

# Post-process for web delivery
from half_america.postprocess import (
    dissolve_all_lambdas,
    simplify_all_lambdas,
    export_all_lambdas,
)

# Transform optimization results to web-ready TopoJSON
dissolve_results = dissolve_all_lambdas(gdf, result)
simplify_results = simplify_all_lambdas(dissolve_results)
export_results = export_all_lambdas(simplify_results, dissolve_results)
# Output: data/output/topojson/lambda_0.0.json, lambda_0.1.json, ...
```

**After**:
```markdown
# Check results
for lambda_val, lambda_result in result.results.items():
    opt = lambda_result.search_result.result
    print(f"lambda={lambda_val:.1f}: {opt.population_fraction:.2%} selected")
```

See [docs/API.md](docs/API.md) for post-processing (dissolve, simplify, export) and the full API reference.

**Line count change**: -12 lines (remove 13 lines of post-processing, add 1 line link)

### Success Criteria:

#### Automated Verification:
- [ ] README.md exists and is valid markdown
- [ ] Line count is between 140-150 lines: `wc -l README.md`
- [ ] All internal links resolve: check that referenced files exist (METHODOLOGY.md, docs/API.md, ROADMAP.md, LICENSE)
- [ ] No broken code blocks (matching triple backticks)

#### Manual Verification:
- [ ] Usage section clearly shows CLI workflow (precompute → export)
- [ ] Development section is separate and clearly labeled
- [ ] API example is concise and shows core workflow
- [ ] Cache management note is present and helpful
- [ ] Overall structure scans well for both users and developers

**Implementation Note**: This is a single-phase plan. After completing the edits and automated verification passes, manual review confirms the restructuring improves readability.

---

## Summary of Line Count Changes

| Change | Lines Added | Lines Removed | Net |
|--------|-------------|---------------|-----|
| Split Usage/Development | +7 | 0 | +7 |
| Add precompute command + options | +5 | 0 | +5 |
| Add pytest patterns | +4 | -2 | +2 |
| Add cache management | +4 | 0 | +4 |
| Trim API example | +1 | -13 | -12 |
| Remove "Run the CLI" line | 0 | -2 | -2 |
| **Total** | +21 | -17 | **+4** |

**Expected result**: 140 → ~144 lines

## References

- Research document: `thoughts/shared/research/2025-11-22-readme-improvement-comparison.md`
- Current README: `README.md` (140 lines)
- Alternative version for reference: `README_alt.md` (190 lines)
- API documentation: `docs/API.md`
