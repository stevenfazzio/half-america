# README Restructuring Implementation Plan

## Overview

Restructure README.md from a 238-line all-in-one document into a ~120-line landing page by extracting the API Reference section (131 lines, 55% of README) to `docs/API.md` and consolidating footer sections.

## Current State Analysis

### File Inventory
| File | Lines | Purpose |
|------|-------|---------|
| README.md | 238 | All-in-one: overview, installation, full API docs |
| docs/API.md | N/A | Does not exist |

### README.md Section Breakdown
| Section | Lines | % of README |
|---------|-------|-------------|
| Title + Badges | 5 | 2% |
| Intro + Quote | 3 | 1% |
| The Problem | 10 | 4% |
| How It Works | 11 | 5% |
| Installation | 17 | 7% |
| Usage | 16 | 7% |
| **API Reference** | **131** | **55%** |
| Project Status | 5 | 2% |
| License + Disclaimer | 6 | 3% |

### Key Discoveries
- API Reference dominates at 55% of content (`README.md:74-224`)
- Four tiny footer sections create visual clutter (`README.md:226-239`)
- Documentation section was already removed in previous cleanup
- CLAUDE.md Documentation section needs updating to reference new location

## Desired End State

### Target Structure
```
half-america/
├── README.md           (~120 lines - landing page)
├── METHODOLOGY.md      (89 lines - unchanged)
├── ROADMAP.md          (112 lines - unchanged)
├── CLAUDE.md           (~50 lines - updated docs reference)
└── docs/
    ├── API.md          (~150 lines - extracted from README)
    └── archive/
        └── PROJECT_SUMMARY.md
```

### Verification Criteria
- README.md ≤ 130 lines
- docs/API.md contains complete API documentation for all three modules
- All internal links work (no broken references)
- No content lost from current README
- CLAUDE.md references docs/API.md

## What We're NOT Doing

- Creating `CONTRIBUTING.md` (deferred to Phase 5/public release)
- Creating `ARCHITECTURE.md` (deferred to post-Phase 5)
- Adding Sphinx/auto-generated docs
- Splitting `docs/API.md` into multiple files
- Adding a Table of Contents to README

## Implementation Approach

Extract API Reference content to `docs/API.md`, replace with Quick Start examples and link in README, then consolidate footer sections. Update CLAUDE.md to reference the new location.

---

## Phase 1: Create docs/API.md

### Overview
Create the new API documentation file with the full API Reference content extracted from README.md.

### Changes Required:

#### 1. Create docs/API.md
**File**: `docs/API.md` (new file)
**Changes**: Create new file with API Reference content

```markdown
# API Reference

This document provides the Python API reference for programmatic use of Half of America. Each module includes a Quick Start example and full function reference.

For installation and CLI usage, see [README.md](../README.md).

---

## Data Pipeline

The data pipeline downloads Census Tract geometries and population data for the contiguous United States.

### Quick Start

```python
from half_america.data import load_state_tracts, get_pipeline_summary

# Load a single state (e.g., California)
gdf = load_state_tracts("06")
print(get_pipeline_summary(gdf))
# Output: {'tract_count': 9129, 'total_population': 39538223, ...}
```

### Load All US Data

```python
from half_america.data import load_all_tracts

# Load all ~73,000 tracts (downloads ~400MB on first run, cached thereafter)
gdf = load_all_tracts()
```

### Function Reference

| Function | Description |
|----------|-------------|
| `load_all_tracts()` | Load all US tracts with population (main entry point) |
| `load_state_tracts(fips)` | Load single state by FIPS code |
| `get_pipeline_summary(gdf)` | Get statistics for loaded data |
| `CONTIGUOUS_US_FIPS` | List of 49 state FIPS codes |
| `FIPS_TO_STATE` | FIPS code to state name mapping |

Data is cached in `data/cache/` after first download.

---

## Graph Construction

The graph module builds spatial adjacency graphs from Census Tract data for Max-Flow Min-Cut optimization.

### Quick Start

```python
from half_america.data import load_all_tracts
from half_america.graph import load_graph_data, get_graph_summary

# Load tract data (from Phase 1)
gdf = load_all_tracts()

# Build or load graph (cached after first run)
graph_data = load_graph_data(gdf)
print(get_graph_summary(graph_data))
# {'num_nodes': 73000, 'num_edges': 450000, 'rho_km': 2.5, ...}
```

### Building Flow Networks

```python
from half_america.graph import build_flow_network, get_partition

# Build flow network for specific λ and μ
g = build_flow_network(graph_data.attributes, graph_data.edges, lambda_param=0.5, mu=0.001)
g.maxflow()

# Extract selected tracts
selected = get_partition(g, graph_data.num_nodes)
print(f"Selected {selected.sum()} tracts")
```

### Function Reference

| Function | Description |
|----------|-------------|
| `load_graph_data(gdf)` | Main entry point - builds or loads cached graph data |
| `get_graph_summary(graph_data)` | Get statistics for loaded graph |
| `build_flow_network(attrs, edges, λ, μ)` | Construct PyMaxFlow graph for optimization |
| `get_partition(g, num_nodes)` | Extract selected tracts after maxflow |

### Data Types

| Type | Description |
|------|-------------|
| `GraphData` | Complete graph data (edges, attributes, statistics) |
| `GraphAttributes` | Node/edge attributes (population, area, rho, edge_lengths) |

Graph data is cached in `data/cache/` after first computation.

---

## Optimization

The optimization module runs Max-Flow Min-Cut optimization across lambda values to find population partitions.

### CLI Usage

```bash
# Pre-compute optimization results for all lambda values (recommended)
uv run half-america precompute

# Options
uv run half-america precompute --force           # Rebuild cache
uv run half-america precompute --lambda-step 0.05  # Finer granularity
uv run half-america precompute --skip-failures   # Continue on convergence errors
```

Results are cached in `data/cache/processed/` after computation.

### Quick Start

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

### Function Reference

| Function | Description |
|----------|-------------|
| `sweep_lambda(graph_data)` | Run optimization across all lambda values (main entry point) |
| `find_optimal_mu(graph_data, lambda_val)` | Find mu that achieves 50% population for given lambda |
| `solve_partition(graph_data, lambda_val, mu)` | Solve single graph-cut for specific parameters |
| `save_sweep_result(result, path)` | Persist sweep results to disk |
| `load_sweep_result(path)` | Load persisted sweep results |

### Data Types

| Type | Description |
|------|-------------|
| `SweepResult` | Full sweep results (dict of lambda to result, timing, convergence) |
| `SearchResult` | Binary search result (final result, iterations, mu history) |
| `OptimizationResult` | Single solve result (partition, statistics, energy) |

See [METHODOLOGY.md](../METHODOLOGY.md) for mathematical details on the optimization algorithm.
```

### Success Criteria:

#### Automated Verification:
- [ ] File exists: `test -f docs/API.md`
- [ ] File has expected content: `grep -q "# API Reference" docs/API.md`
- [ ] Links are valid markdown: Check for `](../README.md)` and `](../METHODOLOGY.md)`

#### Manual Verification:
- [ ] Content matches current README API sections
- [ ] Code examples are properly formatted
- [ ] Tables render correctly in GitHub preview

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 2: Update README.md

### Overview
Replace the detailed API Reference section with a condensed version containing Quick Start examples and a link to the full docs/API.md.

### Changes Required:

#### 1. Replace API Reference Section
**File**: `README.md`
**Changes**: Replace lines 74-224 (API Reference section) with condensed version

**Current** (131 lines starting at line 74):
```markdown
## API Reference

The following sections document the Python API for programmatic use. Each module includes a Quick Start example and full function reference.

### Data Pipeline
[... 44 lines of detailed content ...]

### Graph Construction
[... 50 lines of detailed content ...]

### Optimization
[... 37 lines of detailed content ...]
```

**New** (~35 lines):
```markdown
## API Reference

For complete API documentation, see [docs/API.md](docs/API.md).

### Quick Start

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

See [METHODOLOGY.md](METHODOLOGY.md) for algorithm details.
```

#### 2. Consolidate Footer Sections
**File**: `README.md`
**Changes**: Consolidate 4 footer sections into 2

**Current** (lines 226-239):
```markdown
## Project Status

**Current Phase**: Optimization Engine Complete (Phase 3)

See [ROADMAP.md](ROADMAP.md) for the full implementation plan.

## License

[MIT](LICENSE)

## Disclaimer

This is a personal experimental project exploring topology optimization and cartography. Not intended as a production tool.
```

**New**:
```markdown
## Project Status

**Current Phase**: Optimization Engine Complete (Phase 3)

For more information:
- [ROADMAP.md](ROADMAP.md) - Implementation plan
- [METHODOLOGY.md](METHODOLOGY.md) - Mathematical details

## License

MIT License. See [LICENSE](LICENSE).

*This is a personal experimental project exploring topology optimization and cartography. Not intended as a production tool.*
```

### Success Criteria:

#### Automated Verification:
- [ ] README line count: `wc -l README.md` should be ~115-130 lines
- [ ] Link to API.md exists: `grep -q "docs/API.md" README.md`
- [ ] No broken internal links: All `](*.md)` links point to existing files

#### Manual Verification:
- [ ] README reads well as a landing page
- [ ] Quick Start example is self-contained and demonstrates core workflow
- [ ] Footer sections are clean and not cluttered

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 3: Update CLAUDE.md

### Overview
Update the Documentation section in CLAUDE.md to reference the new docs/API.md file.

### Changes Required:

#### 1. Update Documentation Section
**File**: `CLAUDE.md`
**Changes**: Add docs/API.md to Documentation section

**Current** (lines 44-49):
```markdown
## Documentation

- [README.md](README.md) - Project overview, installation, and usage
- [METHODOLOGY.md](METHODOLOGY.md) - Mathematical formulation and algorithm details
- [ROADMAP.md](ROADMAP.md) - Implementation phases and roadmap
```

**New**:
```markdown
## Documentation

- [README.md](README.md) - Project overview, installation, and usage
- [docs/API.md](docs/API.md) - Python API reference
- [METHODOLOGY.md](METHODOLOGY.md) - Mathematical formulation and algorithm details
- [ROADMAP.md](ROADMAP.md) - Implementation phases and roadmap
```

### Success Criteria:

#### Automated Verification:
- [ ] Link added: `grep -q "docs/API.md" CLAUDE.md`
- [ ] File still valid markdown

#### Manual Verification:
- [ ] Documentation section is complete and accurate

**Implementation Note**: After completing this phase, all changes are complete.

---

## Testing Strategy

### Automated Tests
- Verify file existence and line counts
- Check all internal markdown links resolve
- Grep for expected content patterns

### Manual Testing Steps
1. Open README.md in GitHub and verify it renders correctly
2. Click all links in README.md to verify they work
3. Open docs/API.md and verify code examples are formatted correctly
4. Verify the Quick Start example in README is self-contained and makes sense

---

## References

- Research document: `thoughts/shared/research/2025-11-21-readme-restructuring-strategy.md`
- Related research: `thoughts/shared/research/2025-11-21-readme-organization-audit.md`
- Related research: `thoughts/shared/research/2025-11-21-readme-critical-evaluation.md`
- Previous plan: `thoughts/shared/plans/2025-11-21-readme-organization.md`
