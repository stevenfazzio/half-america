---
date: 2025-11-22T16:00:00-08:00
researcher: Claude
git_commit: 355d0de69b520f0a13e014b91d9b6ba15208c533
branch: master
repository: half-america
topic: "README.md Improvement Analysis - Comparing Three Versions"
tags: [research, documentation, readme, comparison, restructuring]
status: complete
last_updated: 2025-11-22
last_updated_by: Claude
---

# Research: README.md Improvement Analysis

**Date**: 2025-11-22T16:00:00-08:00
**Researcher**: Claude
**Git Commit**: 355d0de69b520f0a13e014b91d9b6ba15208c533
**Branch**: master
**Repository**: half-america

## Research Question

How can we improve README.md based on comparison with two alternative rewrites (README_alt.md and README_alt2.md)? What should be restructured, added, or removed while staying under 170 lines?

## Summary

The current README.md (140 lines) is well-structured after recent framing improvements, but comparison with the alternative versions reveals several enhancement opportunities. Key findings:

1. **Separate Development from Usage** - The alternatives both do this; current README mixes CLI and dev commands
2. **Add precompute command** - Main workflow command is missing from Usage section
3. **Shorten API example** - 32 lines could be ~20 lines by trimming post-processing
4. **Consider Cache Management** - Alternatives include this; useful for developers

Estimated changes: +20 lines (new sections) - 12 lines (API trimming) = net +8 lines → ~148 lines total

## File Comparison

### Line Counts

| File | Lines | Status |
|------|-------|--------|
| README.md (current) | 140 | ✓ Under 170 target |
| README_alt.md | 190 | ✗ Exceeds 170 target |
| README_alt2.md | 102 | Outline only (not actual content) |

### Section-by-Section Comparison

| Section | README.md | README_alt.md | README_alt2.md |
|---------|:---------:|:-------------:|:--------------:|
| Title + Badges | ✓ | ✗ (no badges) | ✗ (no badges) |
| Tagline/Hook | ✓ | ✓ | ✓ |
| Background/Problem | ✓ | ✓ | ✓ |
| Evolution Narrative | ✓ | ✓ | ✓ |
| How It Works | ✓ | ✓ (detailed) | ✓ (with subsections) |
| Installation | ✓ | ✓ | ✓ |
| Census API Key | ✓ | ✓ (optional) | ✓ |
| **CLI Usage** | Mixed | ✓ Separate | ✓ Separate |
| **precompute cmd** | ✗ Missing | ✓ | ✓ |
| Python API example | ✓ (32 lines) | ✓ (18 lines) | ✓ (brief) |
| API Reference link | ✓ | ✓ | ✓ |
| **Project Structure** | ✗ | ✓ | ✓ |
| **Development section** | Mixed | ✓ Separate | ✓ Separate |
| **Cache Management** | ✗ | ✓ | ✓ |
| Technology Stack | ✗ | ✓ | ✗ |
| Project Status | ✓ | ✓ | ✓ |
| License | ✓ | ✓ | ✓ |
| Disclaimer | ✓ | ✗ | ✗ |
| Author | ✗ | ✓ | ✗ |
| Acknowledgments | ✗ | ✗ | ✓ |
| Data Sources | ✗ | ✗ | ✓ (mention) |

**Bold** = significant gap in current README

## Prioritized Recommendations

### HIGH Priority - Structural (Net: +5 lines)

#### 1. Separate Usage and Development Sections

**Current Issue**: Lines 60-84 mix CLI usage (precompute, export) with development commands (pytest, ruff, mypy).

**Recommendation**: Split into "Usage" (CLI commands for users) and "Development" (testing/linting for contributors).

**Benefits**:
- Clearer audience targeting
- Easier to scan for what you need
- Aligns with both alternative versions

**Estimated Change**: +5 lines (section header + reorganization)

#### 2. Add precompute Command to Usage

**Current Issue**: The `precompute` command—the main computational workflow—is not shown in the Usage section. Export is shown but not the step that creates the data to export.

**Recommendation**: Add `uv run half-america precompute` before the export commands.

**Benefits**:
- Shows complete workflow
- Matches CLI's actual primary purpose
- README_alt.md demonstrates this well

**Estimated Change**: +2 lines

### MEDIUM Priority - Content Optimization (Net: -10 lines)

#### 3. Trim Python API Example

**Current Issue**: The API example (lines 92-123) is 32 lines including full post-processing pipeline. This is thorough but long.

**Recommendation**: Trim to ~20 lines by:
- Removing the post-processing imports/calls (dissolve, simplify, export)
- Adding "See [docs/API.md](docs/API.md) for post-processing" link

**Why**: Post-processing is an advanced use case. The Quick Start should show data loading → optimization → checking results. Users who need post-processing will find it in API.md.

**Estimated Change**: -12 lines

#### 4. Add Cache Management Note

**Current Issue**: Users may not know about the caching system or how to clear stale caches.

**Recommendation**: Add 3-4 lines under Development:
```markdown
### Cache Management

Data is cached in `data/cache/`. Clear with `rm -rf data/cache/` if you encounter stale data issues or change year configurations.
```

**Benefits**:
- Both alternatives include this
- Common developer need
- Prevents debugging confusion

**Estimated Change**: +5 lines

### LOW Priority - Nice to Have (Would exceed budget)

#### 5. Project Structure Section

**Current Issue**: No overview of directory layout.

**README_alt.md has**:
```markdown
## Project Structure

half-america/
├── src/half_america/       # Python package
│   ├── data/               # Census data pipeline
...
```

**Verdict**: Would add ~15 lines. Skip unless we find other savings. Users can infer structure from imports in API example.

**Priority**: LOW - Not essential for understanding/using the project

#### 6. Technology Stack Section

**Current Issue**: No explicit list of dependencies/technologies.

**README_alt.md has**: pandas, cenpy, geopandas, PyMaxFlow, etc.

**Verdict**: This info exists in METHODOLOGY.md Section 5. Adding it to README is redundant.

**Priority**: LOW - Defer to METHODOLOGY.md

#### 7. Data Sources Mention

**Current Issue**: No explicit mention that data comes from Census Bureau TIGER/Line + ACS.

**Recommendation**: Could add 1 line to Background: "Uses Census Tract data from the US Census Bureau."

**Priority**: LOW - The census API key section implies this

#### 8. Acknowledgments Section

**README_alt2.md suggests**: Credits to Census Bureau, key libraries.

**Verdict**: Nice for open source etiquette but not critical for a personal project.

**Priority**: LOW - Add when/if going public

## Detailed Implementation Plan

### Proposed Structure (Target: ~150 lines)

```
# Half of America                                    # 1-8 (badges, tagline)
## Background                                        # 9-35 (evolution story)
## How It Works                                      # 36-52 (lambda explanation)
## Installation                                      # 53-68 (uv, census key)
## Usage                                             # 69-88 (CLI: precompute, export)
  - precompute command
  - export command
## Python API                                        # 89-112 (trimmed example)
  - Quick Start (load → optimize → check)
  - Link to API.md for full reference
## Development                                       # 113-135 (testing, linting, cache)
  - pytest commands
  - ruff/mypy commands
  - Cache management note
## Project Status                                    # 136-145
## License                                           # 146-150
```

### Specific Edits

#### Edit 1: Split Usage Section (lines 60-84)

**Before** (Usage section has mixed content):
```markdown
## Usage

```bash
# Run the CLI
uv run half-america

# Run tests
uv run pytest
...
```

**After**:
```markdown
## Usage

```bash
# Pre-compute optimization results for all lambda values
uv run half-america precompute

# Export TopoJSON files
uv run half-america export

# Export with options
uv run half-america export --combined      # Include combined.json
uv run half-america export --force         # Overwrite existing
```

## Development

```bash
# Run tests
uv run pytest

# Skip network-dependent tests
uv run pytest -m "not integration"

# Format code
uv run ruff format src/ tests/

# Lint
uv run ruff check src/ tests/

# Type check
uv run mypy src/
```

### Cache Management

Data is cached in `data/cache/`. Clear with `rm -rf data/cache/` if you encounter stale data or change year configurations in `src/half_america/config.py`.
```

#### Edit 2: Trim API Example (lines 92-123)

**Before** (32 lines including post-processing):
```python
from half_america.data import load_all_tracts
from half_america.graph import load_graph_data
from half_america.optimization import sweep_lambda

# Load Census Tract data (~73,000 tracts)
gdf = load_all_tracts()

# Build spatial adjacency graph
graph_data = load_graph_data(gdf)

# Run optimization across lambda values
result = sweep_lambda(graph_data)

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

**After** (20 lines, focused on core workflow):
```python
from half_america.data import load_all_tracts
from half_america.graph import load_graph_data
from half_america.optimization import sweep_lambda

# Load Census Tract data (~73,000 tracts)
gdf = load_all_tracts()

# Build spatial adjacency graph
graph_data = load_graph_data(gdf)

# Run optimization across lambda values
result = sweep_lambda(graph_data)

# Check results
for lambda_val, lambda_result in result.results.items():
    opt = lambda_result.search_result.result
    print(f"lambda={lambda_val:.1f}: {opt.population_fraction:.2%} selected")
```

See [docs/API.md](docs/API.md) for post-processing (dissolve, simplify, export) and the full API reference.

## What NOT to Change

### Keep from Current README

1. **Badges** - Professional appearance; neither alternative has them
2. **Blockquote hook** - "Half of America lives in a *very* small area" is compelling
3. **Background/Evolution section** - Well-written after recent improvements
4. **Disclaimer** - Important for expectations management
5. **"Note: lambda=1.0 is mathematically degenerate"** - Technical accuracy

### Don't Add from Alternatives

1. **Author section** (README_alt.md) - GitHub already shows this; adds clutter
2. **Technology Stack** (README_alt.md) - Redundant with METHODOLOGY.md
3. **Project Structure** (both alts) - Blows line budget; not essential
4. **Full directory tree** - Too detailed for README

## Impact Summary

| Change | Lines Added | Lines Removed | Net |
|--------|-------------|---------------|-----|
| Split Usage/Development | +5 | 0 | +5 |
| Add precompute command | +2 | 0 | +2 |
| Add cache management | +5 | 0 | +5 |
| Trim API example | 0 | -12 | -12 |
| **Total** | +12 | -12 | **0** |

**Result**: 140 lines → ~140 lines (better organized, same length)

If we want to stay conservative and not add cache management: 140 → ~135 lines

## Code References

- `README.md:60-84` - Current Usage section (mixed CLI + dev commands)
- `README.md:92-123` - Current API example (long, includes post-processing)
- `README_alt.md:62-140` - Well-separated Usage, Python API, Development
- `README_alt.md:142-160` - Cache Management table
- `README_alt2.md:44-79` - Structural outline for Usage/Development split

## Historical Context

Previous research documents inform this analysis:
- `thoughts/shared/research/2025-11-22-documentation-improvement-recommendations.md` - Recent framing fixes (already implemented)
- `thoughts/shared/plans/2025-11-22-documentation-framing-improvements.md` - Implementation of evolution narrative
- `thoughts/shared/research/2025-11-21-readme-restructuring-strategy.md` - API extraction strategy (completed - docs/API.md exists)

## Open Questions

1. **Should we add the precompute --force and --lambda-step options to Usage?**
   - README_alt.md shows these; they're useful but add 2 more lines
   - Recommendation: Yes, they're commonly needed

2. **Should the Development section include the pytest -k pattern example?**
   - Currently shown in Usage; useful for developers
   - Recommendation: Yes, include `pytest -k "dissolve"` example

3. **Is the cache management note too brief?**
   - CLAUDE.md has a detailed table; README could just link there
   - Recommendation: Keep brief in README; developers who need detail can check CLAUDE.md (which Claude Code uses anyway)
