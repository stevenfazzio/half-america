# Phase 3 Documentation Updates Implementation Plan

## Overview

Update project documentation to reflect Phase 3 (Optimization Engine) completion. This includes status updates in README.md and CLAUDE.md, plus adding a new Optimization section to README.md documenting the CLI and API.

## Current State Analysis

Phase 3 implementation is complete with all ROADMAP.md milestones checked. Documentation currently reflects Phase 2 status:

- **README.md:167** shows "Graph Construction Complete (Phase 2)"
- **CLAUDE.md:33** shows optimization as "*Phase 3*" (not implemented)
- **CLAUDE.md** commands section missing `precompute` command
- **README.md** missing Optimization API section (Phase 1 and Phase 2 have sections)

### Key Discoveries:
- ROADMAP.md already updated during implementation (no changes needed)
- METHODOLOGY.md has no status indicators by design (no changes needed)
- Optimization module exports: `sweep_lambda`, `find_optimal_mu`, `solve_partition`, `save_sweep_result`, `load_sweep_result`
- CLI command: `half-america precompute [--force] [--lambda-step FLOAT] [--skip-failures]`

## Desired End State

After this plan is complete:
1. README.md shows "Optimization Engine Complete (Phase 3)"
2. CLAUDE.md shows optimization as "*implemented*"
3. CLAUDE.md includes `precompute` command in quick reference
4. README.md has Optimization section documenting CLI and high-level API

### Verification:
- `grep "Optimization Engine Complete (Phase 3)" README.md` returns a match
- `grep "Optimization.*implemented" CLAUDE.md` returns a match
- `grep "precompute" CLAUDE.md` returns a match
- `grep "## Optimization" README.md` returns a match

## What We're NOT Doing

- Updating ROADMAP.md (already current)
- Updating METHODOLOGY.md (no status indicators by design)
- Adding benchmark results to documentation (keep in research docs)
- Duplicating low-level graph operations already in Graph Construction section
- Adding detailed mathematical explanations (link to METHODOLOGY.md instead)

## Implementation Approach

Two-phase approach: quick status updates first, then new content addition. This allows verification after each phase and minimizes risk.

---

## Phase 1: Status Updates

### Overview
Update existing status indicators in README.md and CLAUDE.md. Add precompute command to CLAUDE.md quick reference.

### Changes Required:

#### 1. README.md - Update Current Phase Status
**File**: `README.md`
**Line**: 167
**Changes**: Update phase status from Phase 2 to Phase 3

**Current (line 167):**
```markdown
**Current Phase**: Graph Construction Complete (Phase 2)
```

**New:**
```markdown
**Current Phase**: Optimization Engine Complete (Phase 3)
```

#### 2. CLAUDE.md - Update Implementation Stack Annotation
**File**: `CLAUDE.md`
**Line**: 33
**Changes**: Change "*Phase 3*" to "*implemented*"

**Current (line 33):**
```markdown
- **Optimization:** PyMaxFlow (C++ graph cuts wrapper) - *Phase 3*
```

**New:**
```markdown
- **Optimization:** PyMaxFlow (C++ graph cuts wrapper) - *implemented*
```

#### 3. CLAUDE.md - Add Precompute Command
**File**: `CLAUDE.md`
**Lines**: 25-26
**Changes**: Add precompute command after the CLI command

**Current (lines 24-26):**
```markdown
uv run mypy src/                     # Type check
uv run half-america                  # Run CLI
```

**New:**
```markdown
uv run mypy src/                     # Type check
uv run half-america                  # Run CLI
uv run half-america precompute       # Pre-compute optimization results
```

### Success Criteria:

#### Automated Verification:
- [x] `grep "Optimization Engine Complete (Phase 3)" README.md` returns a match
- [x] `grep "Optimization.*implemented" CLAUDE.md` returns a match
- [x] `grep "precompute" CLAUDE.md` returns a match

#### Manual Verification:
- [x] README project status accurately reflects Phase 3 completion
- [x] CLAUDE.md implementation stack shows all completed phases as "implemented"
- [x] CLAUDE.md commands section includes `precompute` with appropriate comment

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation before proceeding to Phase 2.

---

## Phase 2: Add Optimization Section to README

### Overview
Add new Optimization section to README.md documenting the CLI and high-level Python API, following the pattern established by Data Pipeline and Graph Construction sections.

### Changes Required:

#### 1. README.md - Add Optimization Section
**File**: `README.md`
**Location**: After Graph Construction section (after line 163), before Project Status section (before line 165)
**Changes**: Insert new Optimization section

**Insert after line 163 (after "Graph data is cached..."):**

```markdown

### Optimization

The optimization module runs Max-Flow Min-Cut optimization across lambda values to find population partitions.

#### CLI Usage

```bash
# Pre-compute optimization results for all lambda values (recommended)
uv run half-america precompute

# Options
uv run half-america precompute --force           # Rebuild cache
uv run half-america precompute --lambda-step 0.05  # Finer granularity
uv run half-america precompute --skip-failures   # Continue on convergence errors
```

Results are cached in `data/cache/processed/` after computation.

#### Quick Start

```python
from half_america.data import load_all_tracts
from half_america.graph import load_graph_data
from half_america.optimization import sweep_lambda, save_sweep_result

# Load data and graph
gdf = load_all_tracts()
graph_data = load_graph_data(gdf)

# Run optimization across all lambda values
result = sweep_lambda(graph_data)

# Check results
for lambda_val, lambda_result in result.results.items():
    opt = lambda_result.search_result.result
    print(f"lambda={lambda_val:.1f}: {opt.population_fraction:.2%} selected")

# Persist for post-processing
save_sweep_result(result, Path("data/cache/processed/sweep.pkl"))
```

#### Function Reference

| Function | Description |
|----------|-------------|
| `sweep_lambda(graph_data)` | Run optimization across all lambda values (main entry point) |
| `find_optimal_mu(graph_data, lambda_val)` | Find mu that achieves 50% population for given lambda |
| `solve_partition(graph_data, lambda_val, mu)` | Solve single graph-cut for specific parameters |
| `save_sweep_result(result, path)` | Persist sweep results to disk |
| `load_sweep_result(path)` | Load persisted sweep results |

#### Data Types

| Type | Description |
|------|-------------|
| `SweepResult` | Full sweep results (dict of lambda to result, timing, convergence) |
| `SearchResult` | Binary search result (final result, iterations, mu history) |
| `OptimizationResult` | Single solve result (partition, statistics, energy) |

See [METHODOLOGY.md](METHODOLOGY.md) for mathematical details on the optimization algorithm.

```

### Success Criteria:

#### Automated Verification:
- [x] `grep "## Optimization" README.md` returns a match (note: section uses `###`)
- [x] `grep "### Optimization" README.md` returns a match
- [x] `grep "sweep_lambda" README.md` returns a match
- [x] `grep "half-america precompute" README.md` returns a match

#### Manual Verification:
- [x] Optimization section appears between Graph Construction and Project Status
- [x] CLI documentation matches actual `--help` output
- [x] Python example is syntactically correct and follows project patterns
- [x] Function reference matches actual module exports
- [x] No redundant content with Graph Construction section
- [x] Link to METHODOLOGY.md works correctly

**Implementation Note**: After completing this phase and all verification passes, the documentation update is complete.

---

## Testing Strategy

### Automated Tests:
- Grep commands in success criteria verify content presence
- No code changes, so no unit tests needed

### Manual Testing Steps:
1. Read through updated README.md for clarity and accuracy
2. Verify all internal links work (`METHODOLOGY.md`, `ROADMAP.md`)
3. Confirm Optimization section flows naturally between Graph Construction and Project Status
4. Spot-check that Python example matches actual API signatures

---

## References

- Research document: `thoughts/shared/research/2025-11-21-phase3-documentation-updates.md`
- Phase 2 documentation plan (pattern reference): `thoughts/shared/plans/2025-11-21-phase2-documentation-updates.md`
- Optimization module: `src/half_america/optimization/__init__.py`
