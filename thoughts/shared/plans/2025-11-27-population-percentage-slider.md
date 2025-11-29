# Population Percentage Slider Implementation Plan

## Overview

Add a second slider that allows users to adjust the population percentage target (currently hardcoded to 50%). This enables exploration of questions like "Where does 25% of America live?" or "What area contains 75% of the population?"

Based on research in `thoughts/shared/research/2025-11-27-population-slider-feasibility.md`, we will use **parametric max-flow with the Hochbaum Pseudoflow library**:
- **Lambda (λ)**: 5% steps (0.00, 0.05, 0.10, ..., 0.95) = 20 values
- **Population**: 5% steps (0.05, 0.10, ..., 0.95) = 19 values
- **Total files**: 20 × 19 = 380 files

**Key Innovation**: Instead of running ~15 binary search iterations per (λ, population) target (5,700 max-flow solves total), we use pseudoflow's parametric algorithm to find ALL μ breakpoints in ONE solve per λ value. This yields:
- **~20 parametric solves** instead of ~5,700 standard max-flow solves
- **~150× speedup** in precomputation time
- **Mathematically elegant**: discovers natural breakpoints rather than searching

**How it works**: For each λ, the energy function is linear in μ:
```
E(X) = [λ·boundary + (1-λ)·area] - μ·population
        \_____fixed for this λ____/   \__varies__/
```
Pseudoflow solves for all μ breakpoints simultaneously, giving us every possible partition and its population fraction. We then extract the partitions closest to our 5% target grid.

## Current State Analysis

### Backend
- `sweep_lambda()` in `src/half_america/optimization/sweep.py:59` already accepts `target_fraction` parameter
- `find_optimal_mu()` in `src/half_america/optimization/search.py:27` accepts `target_fraction` parameter
- CLI `precompute` command hardcodes `target_fraction=0.5` implicitly (uses sweep_lambda defaults)
- File naming: `lambda_{λ:.2f}.json` (no population in filename)

### Frontend
- `LAMBDA_VALUES` in `web/src/types/lambda.ts:5-16`: 99 values (0.00 to 0.98 in 0.01 steps)
- `useTopoJsonLoader.ts`: Loads all 99 files into a `Map<LambdaValue, FeatureCollection>`
- `MapTab.tsx:52`: Single `currentLambda` state controls layer visibility
- `LambdaSlider.tsx`: Controlled slider component with tooltip

### Key Discoveries
- `getTopoJsonPath()` at `web/src/types/lambda.ts:24-25` generates file paths
- Layer visibility toggle at `MapTab.tsx:72`: `visible: lambda === currentLambda`
- Batch loading at `useTopoJsonLoader.ts:90`: 10 concurrent requests
- Metadata already includes `population_selected` and `total_population` for display

## Desired End State

After implementation:
1. Users can drag a **Population slider** (5% to 95% in 5% steps) below the existing λ slider
2. Map instantly updates to show the selected (λ, population) combination
3. 380 TopoJSON files precomputed and deployed to GitHub Pages
4. SummaryPanel shows the target population percentage alongside actual achieved percentage
5. Default view: λ=0.50, population=50% (same as current)

### Verification
- `uv run half-america precompute --lambda-step 0.05` runs parametric solve for 20 λ values in ~1-5 minutes
- `uv run half-america export --lambda-step 0.05 --pop-step 0.05` creates 380 TopoJSON files
- Frontend loads all 380 files and both sliders work
- File sizes remain reasonable (~2-3 MB total, similar compression to current)

## What We're NOT Doing

- **Continuous population slider**: Although pseudoflow discovers all natural breakpoints, we snap to a 5% grid for consistent UX
- **Server-side computation**: Would enable real-time but requires infrastructure
- **WebAssembly**: Research shows precomputation is superior for this use case
- **1% population granularity**: Perceptually indistinguishable, would create 2000+ files
- **Fine λ granularity**: 5% steps are sufficient; users won't notice 1% differences
- **Variable slider positions per λ**: Each λ has different natural breakpoints, but we normalize to consistent 5% grid

---

## Phase 1: Backend - Add Pseudoflow Dependency

### Overview
Add the Hochbaum Pseudoflow library for parametric max-flow computation.

### Changes Required

#### 1. Add pseudoflow to dependencies
**File**: `pyproject.toml`
**Changes**: Add pseudoflow to dependencies

```toml
[project]
dependencies = [
    # ... existing dependencies ...
    "pseudoflow>=2024.6.2",
]
```

#### 2. Verify installation
```bash
uv sync
uv run python -c "import pseudoflow; print('pseudoflow installed successfully')"
```

### Success Criteria

#### Automated Verification:
- [ ] `uv sync` completes without errors
- [ ] `uv run python -c "import pseudoflow"` succeeds

#### Manual Verification:
- [ ] Pseudoflow C extension compiled successfully (check for warnings during install)

**Implementation Note**: After completing this phase, proceed to Phase 2.

---

## Phase 2: Backend - Parametric Solver Module

### Overview
Create a new solver module that uses pseudoflow to find all μ breakpoints for a given λ value in a single solve.

### Changes Required

#### 1. Create parametric solver module
**File**: `src/half_america/optimization/parametric.py` (new file)
**Changes**: Implement parametric max-flow solver using pseudoflow

```python
"""Parametric max-flow solver using Hochbaum's Pseudoflow algorithm."""

from typing import NamedTuple

import networkx as nx
import numpy as np
from pseudoflow import hpf

from half_america.graph.pipeline import GraphData


class Breakpoint(NamedTuple):
    """A single breakpoint in the parametric solution."""

    mu_upper: float  # Upper bound of μ for this interval
    partition: np.ndarray  # Boolean array: True = selected
    population_fraction: float  # Fraction of total population selected
    selected_population: int
    selected_area: float


class ParametricResult(NamedTuple):
    """Result from parametric max-flow solve for a single λ value."""

    lambda_param: float
    breakpoints: list[Breakpoint]  # Sorted by population_fraction ascending
    total_population: int
    total_area: float
    num_breakpoints: int


def solve_parametric(
    graph_data: GraphData,
    lambda_param: float,
    mu_max: float = 10.0,
    verbose: bool = True,
) -> ParametricResult:
    """
    Solve parametric max-flow for all μ values in one pass.

    For a fixed λ, finds all breakpoints in μ where the optimal partition changes.
    Each breakpoint corresponds to a different population fraction.

    Args:
        graph_data: GraphData from load_graph_data()
        lambda_param: Surface tension parameter [0, 1)
        mu_max: Upper bound for μ search range
        verbose: Print diagnostic output

    Returns:
        ParametricResult with all breakpoints and their partitions
    """
    if not 0 <= lambda_param < 1:
        raise ValueError(f"lambda_param must be in [0, 1), got {lambda_param}")

    attrs = graph_data.attributes
    num_nodes = graph_data.num_nodes
    total_pop = int(attrs.population.sum())
    total_area = float(attrs.area.sum())
    rho = attrs.rho
    rho_sq = rho ** 2

    if verbose:
        print(f"Building parametric graph for λ={lambda_param:.2f}...")

    # Build NetworkX graph for pseudoflow
    # Capacity = const + mult * μ
    # Source edges: const=0, mult=p_i (population reward increases with μ)
    # Sink edges: const=(1-λ)*a_i/ρ², mult=0 (area cost fixed)
    # Interior edges: const=λ*l_ij/ρ, mult=0 (boundary cost fixed)

    G = nx.DiGraph()

    # Add source edges (μ * population reward)
    # Pseudoflow requires: source-adjacent arcs have mult >= 0
    for i in range(num_nodes):
        G.add_edge('source', i, const=0.0, mult=float(attrs.population[i]))

    # Add sink edges (area cost, fixed for this λ)
    # Pseudoflow requires: sink-adjacent arcs have mult <= 0
    for i in range(num_nodes):
        area_cost = (1 - lambda_param) * attrs.area[i] / rho_sq
        G.add_edge(i, 'sink', const=area_cost, mult=0.0)

    # Add interior edges (boundary cost, fixed for this λ)
    # Pseudoflow requires: interior arcs have mult = 0
    for i, j in graph_data.edges:
        l_ij = attrs.edge_lengths[(i, j)]
        boundary_cost = lambda_param * l_ij / rho
        # Add both directions for undirected graph
        G.add_edge(i, j, const=boundary_cost, mult=0.0)
        G.add_edge(j, i, const=boundary_cost, mult=0.0)

    if verbose:
        print(f"  Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        print(f"  Solving parametric max-flow for μ ∈ [0, {mu_max}]...")

    # Run parametric max-flow
    bp_values, cuts, info = hpf(
        G,
        source='source',
        sink='sink',
        const_cap='const',
        mult_cap='mult',
        lambdaRange=[0.0, mu_max],
        roundNegativeCapacity=False,
    )

    if verbose:
        print(f"  Found {len(bp_values)} breakpoints in {info['solveTime']:.2f}s")

    # Extract breakpoints with statistics
    breakpoints: list[Breakpoint] = []

    for interval_idx, mu_upper in enumerate(bp_values):
        # Extract partition for this interval
        # cuts[node] is a list of source-set indicators per interval
        # 1 = in source set (selected), 0 = in sink set
        partition = np.array([
            cuts[i][interval_idx] == 1
            for i in range(num_nodes)
        ])

        selected_pop = int(attrs.population[partition].sum())
        selected_area = float(attrs.area[partition].sum())
        pop_fraction = selected_pop / total_pop

        breakpoints.append(Breakpoint(
            mu_upper=mu_upper,
            partition=partition,
            population_fraction=pop_fraction,
            selected_population=selected_pop,
            selected_area=selected_area,
        ))

    # Sort by population fraction (should already be sorted by μ, but ensure)
    breakpoints.sort(key=lambda bp: bp.population_fraction)

    if verbose:
        print(f"  Population range: {breakpoints[0].population_fraction:.1%} → {breakpoints[-1].population_fraction:.1%}")

    return ParametricResult(
        lambda_param=lambda_param,
        breakpoints=breakpoints,
        total_population=total_pop,
        total_area=total_area,
        num_breakpoints=len(breakpoints),
    )


def find_partition_for_target(
    result: ParametricResult,
    target_fraction: float,
    tolerance: float = 0.01,
) -> Breakpoint | None:
    """
    Find the breakpoint closest to a target population fraction.

    Args:
        result: ParametricResult from solve_parametric()
        target_fraction: Desired population fraction (e.g., 0.5 for 50%)
        tolerance: Maximum allowed deviation from target

    Returns:
        Breakpoint closest to target, or None if no breakpoint within tolerance
    """
    best_bp = None
    best_error = float('inf')

    for bp in result.breakpoints:
        error = abs(bp.population_fraction - target_fraction)
        if error < best_error:
            best_error = error
            best_bp = bp

    if best_error <= tolerance:
        return best_bp
    return None
```

#### 2. Create parametric sweep function
**File**: `src/half_america/optimization/parametric.py` (append to above)
**Changes**: Add sweep function that runs parametric solve for each λ

```python
class ParametricSweepResult(NamedTuple):
    """Result from parametric sweep across λ values."""

    results: dict[float, ParametricResult]  # λ → ParametricResult
    lambda_values: list[float]
    total_breakpoints: int
    elapsed_seconds: float


def sweep_lambda_parametric(
    graph_data: GraphData,
    lambda_values: list[float] | None = None,
    mu_max: float = 10.0,
    verbose: bool = True,
) -> ParametricSweepResult:
    """
    Run parametric max-flow for each λ value.

    Unlike the binary search approach, this finds ALL breakpoints for each λ
    in a single solve, enabling extraction of any population target.

    Args:
        graph_data: GraphData from load_graph_data()
        lambda_values: λ values to sweep (default: 0.0, 0.05, ..., 0.95)
        mu_max: Upper bound for μ search range
        verbose: Print progress

    Returns:
        ParametricSweepResult with results for each λ
    """
    import time

    if lambda_values is None:
        lambda_values = [round(i * 0.05, 2) for i in range(20)]  # 0.0 to 0.95

    if verbose:
        print(f"Starting parametric sweep: {len(lambda_values)} λ values")

    start_time = time.perf_counter()
    results: dict[float, ParametricResult] = {}
    total_breakpoints = 0

    for lambda_param in lambda_values:
        result = solve_parametric(
            graph_data,
            lambda_param=lambda_param,
            mu_max=mu_max,
            verbose=verbose,
        )
        results[lambda_param] = result
        total_breakpoints += result.num_breakpoints

    elapsed = time.perf_counter() - start_time

    if verbose:
        print(f"\nSweep complete: {total_breakpoints} total breakpoints in {elapsed:.2f}s")

    return ParametricSweepResult(
        results=results,
        lambda_values=lambda_values,
        total_breakpoints=total_breakpoints,
        elapsed_seconds=elapsed,
    )
```

#### 3. Update module exports
**File**: `src/half_america/optimization/__init__.py`
**Changes**: Export new parametric functions

```python
from half_america.optimization.parametric import (
    Breakpoint,
    ParametricResult,
    ParametricSweepResult,
    find_partition_for_target,
    solve_parametric,
    sweep_lambda_parametric,
)
```

### Success Criteria

#### Automated Verification:
- [ ] `uv run pytest tests/test_optimization/` passes
- [ ] `uv run mypy src/half_america/optimization/parametric.py` passes
- [ ] `uv run ruff check src/half_america/` passes

#### Manual Verification:
- [ ] Run a small test: `uv run python -c "from half_america.optimization.parametric import solve_parametric; print('OK')"`
- [ ] Verify breakpoints are found for a test λ value

**Implementation Note**: After completing this phase and verifying the parametric solver works, proceed to Phase 3.

---

## Phase 3: Backend - CLI Precompute Updates

### Overview
Update the CLI precompute command to use parametric max-flow and extract partitions for target population grid.

### Changes Required

#### 1. Update CLI precompute command
**File**: `src/half_america/cli.py`
**Changes**: Replace binary search approach with parametric solver

```python
from half_america.optimization.parametric import (
    find_partition_for_target,
    sweep_lambda_parametric,
)

@cli.command()
@click.option(
    "--force",
    is_flag=True,
    help="Rebuild cache even if it exists",
)
@click.option(
    "--lambda-step",
    type=float,
    default=0.05,
    help="Lambda increment (default: 0.05)",
)
@click.option(
    "--lambda-max",
    type=float,
    default=0.99,
    help="Maximum lambda value, exclusive (default: 0.99)",
)
@click.option(
    "--pop-step",
    type=float,
    default=0.05,
    help="Population target increment (default: 0.05)",
)
@click.option(
    "--pop-min",
    type=float,
    default=0.05,
    help="Minimum population target (default: 0.05)",
)
@click.option(
    "--pop-max",
    type=float,
    default=0.95,
    help="Maximum population target (default: 0.95)",
)
def precompute(
    force: bool,
    lambda_step: float,
    lambda_max: float,
    pop_step: float,
    pop_min: float,
    pop_max: float,
) -> None:
    """Pre-compute optimization results using parametric max-flow."""
    cache_path = get_parametric_cache_path(lambda_step)

    if cache_path.exists() and not force:
        click.echo(f"Cache exists: {cache_path}")
        click.echo("Use --force to rebuild")
        return

    # Generate lambda values
    num_lambda_steps = int(lambda_max / lambda_step)
    lambda_values = [round(i * lambda_step, 2) for i in range(num_lambda_steps)]

    # Generate population targets for extraction
    num_pop_steps = int((pop_max - pop_min) / pop_step) + 1
    pop_values = [round(pop_min + i * pop_step, 2) for i in range(num_pop_steps)]

    click.echo(f"Parametric precomputation:")
    click.echo(f"  {len(lambda_values)} λ values (0.00 to {lambda_values[-1]:.2f})")
    click.echo(f"  {len(pop_values)} population targets ({pop_min:.0%} to {pop_max:.0%})")
    click.echo(f"  Will export {len(lambda_values) * len(pop_values)} files")

    click.echo("\nLoading tract data...")
    gdf = load_all_tracts()

    click.echo("Building graph data...")
    graph_data = load_graph_data(gdf)

    click.echo("\nRunning parametric sweep (one solve per λ)...")
    parametric_result = sweep_lambda_parametric(
        graph_data,
        lambda_values=lambda_values,
        verbose=True,
    )

    # Save parametric result
    save_parametric_result(parametric_result, cache_path)
    click.echo(f"\nSaved parametric result to: {cache_path}")

    # Summary
    click.echo(f"\nTotal breakpoints found: {parametric_result.total_breakpoints}")
    click.echo(f"Time: {parametric_result.elapsed_seconds:.2f}s")
```

#### 2. Add cache path and save functions
**File**: `src/half_america/data/cache.py`
**Changes**: Add parametric cache path function

```python
def get_parametric_cache_path(lambda_step: float = 0.05) -> Path:
    """Get the path for parametric sweep cache file."""
    filename = f"parametric_{TIGER_YEAR}_{ACS_YEAR}_lstep{lambda_step:.2f}.pkl"
    return PROCESSED_DIR / filename


def save_parametric_result(result: "ParametricSweepResult", path: Path) -> None:
    """Save parametric sweep result to disk."""
    import pickle
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(result, f)


def load_parametric_result(path: Path) -> "ParametricSweepResult":
    """Load parametric sweep result from disk."""
    import pickle
    with open(path, "rb") as f:
        return pickle.load(f)
```

### Success Criteria

#### Automated Verification:
- [ ] `uv run pytest tests/test_cli.py -v` passes
- [ ] `uv run mypy src/half_america/cli.py` passes
- [ ] `uv run ruff check src/half_america/` passes

#### Manual Verification:
- [ ] `uv run half-america precompute --help` shows new options
- [ ] Running precompute creates a single parametric cache file
- [ ] Precompute completes in ~1-5 minutes (vs ~30+ minutes for binary search)
- [ ] Output shows breakpoint counts per λ

**Implementation Note**: After completing this phase, proceed to Phase 4.

---

## Phase 4: Backend - Export Pipeline Updates

### Overview
Update the export command to extract partitions from parametric results for target population grid.

### Changes Required

#### 1. Update CLI export command
**File**: `src/half_america/cli.py`
**Changes**: Extract partitions from parametric results

```python
@cli.command()
@click.option(
    "--lambda-step",
    type=float,
    default=0.05,
    help="Lambda step size (must match precomputed sweep)",
)
@click.option(
    "--pop-step",
    type=float,
    default=0.05,
    help="Population target increment (default: 0.05)",
)
@click.option(
    "--pop-min",
    type=float,
    default=0.05,
    help="Minimum population target (default: 0.05)",
)
@click.option(
    "--pop-max",
    type=float,
    default=0.95,
    help="Maximum population target (default: 0.95)",
)
@click.option(
    "--output-dir",
    type=click.Path(path_type=Path),
    default=None,
    help=f"Output directory (default: {TOPOJSON_DIR})",
)
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite existing output files",
)
def export(
    lambda_step: float,
    pop_step: float,
    pop_min: float,
    pop_max: float,
    output_dir: Path | None,
    force: bool,
) -> None:
    """Export TopoJSON files from parametric precomputation results."""
    if output_dir is None:
        output_dir = TOPOJSON_DIR

    # Load parametric result
    cache_path = get_parametric_cache_path(lambda_step)
    if not cache_path.exists():
        click.echo(f"Parametric cache not found: {cache_path}")
        click.echo("Run 'half-america precompute' first")
        return

    click.echo(f"Loading parametric result from {cache_path}...")
    parametric_result = load_parametric_result(cache_path)

    click.echo("Loading tract data...")
    gdf = load_all_tracts()

    # Generate population targets
    num_pop_steps = int((pop_max - pop_min) / pop_step) + 1
    pop_values = [round(pop_min + i * pop_step, 2) for i in range(num_pop_steps)]

    click.echo(f"\nExporting {len(parametric_result.lambda_values)} λ × {len(pop_values)} pop = {len(parametric_result.lambda_values) * len(pop_values)} files...")

    total_files = 0
    total_size = 0
    skipped = 0

    for lambda_val in parametric_result.lambda_values:
        lambda_result = parametric_result.results[lambda_val]

        for pop_target in pop_values:
            # Find closest breakpoint to target
            bp = find_partition_for_target(lambda_result, pop_target, tolerance=0.10)

            if bp is None:
                click.echo(f"  WARNING: No breakpoint within 10% of {pop_target:.0%} for λ={lambda_val:.2f}")
                skipped += 1
                continue

            # Export this partition
            output_path = output_dir / f"lambda_{lambda_val:.2f}_pop_{pop_target:.2f}.json"

            if output_path.exists() and not force:
                skipped += 1
                continue

            result = export_partition_to_topojson(
                gdf=gdf,
                partition=bp.partition,
                lambda_val=lambda_val,
                pop_target=pop_target,
                bp=bp,
                output_path=output_path,
            )

            total_files += 1
            total_size += result.file_size_bytes

    click.echo(f"\nExported {total_files} files ({total_size / 1024:.1f} KB total)")
    if skipped > 0:
        click.echo(f"Skipped {skipped} files (already exist or no matching breakpoint)")
```

#### 2. Add export function for partitions
**File**: `src/half_america/postprocess/export.py`
**Changes**: Add function to export a single partition

```python
def export_partition_to_topojson(
    gdf: gpd.GeoDataFrame,
    partition: np.ndarray,
    lambda_val: float,
    pop_target: float,
    bp: "Breakpoint",
    output_path: Path,
    quantization: float = DEFAULT_QUANTIZATION,
) -> ExportResult:
    """
    Export a single partition to TopoJSON.

    Args:
        gdf: GeoDataFrame with all tracts
        partition: Boolean array indicating selected tracts
        lambda_val: Lambda value
        pop_target: Target population fraction (for filename/metadata)
        bp: Breakpoint with statistics
        output_path: Output file path
        quantization: TopoJSON quantization

    Returns:
        ExportResult with path and file size
    """
    # Dissolve selected tracts
    selected_gdf = gdf[partition].copy()
    dissolved = selected_gdf.dissolve()
    geometry = dissolved.geometry.iloc[0]

    if geometry.is_empty:
        raise ValueError(f"Empty geometry for λ={lambda_val}, pop={pop_target}")

    # Count parts
    if geometry.geom_type == "MultiPolygon":
        num_parts = len(geometry.geoms)
    else:
        num_parts = 1

    # Get total area from full dataset
    total_area = float(gdf.geometry.area.sum())

    metadata = ExportMetadata(
        lambda_value=lambda_val,
        population_selected=bp.selected_population,
        total_population=int(gdf["population"].sum()),
        area_sqm=bp.selected_area,
        num_parts=num_parts,
        total_area_all_sqm=total_area,
    )

    return export_to_topojson(
        geometry=geometry,
        output_path=output_path,
        metadata=metadata,
        quantization=quantization,
    )
```

### Success Criteria

#### Automated Verification:
- [ ] `uv run pytest tests/test_postprocess/test_export.py -v` passes
- [ ] `uv run mypy src/half_america/postprocess/export.py` passes
- [ ] `uv run ruff check src/half_america/` passes

#### Manual Verification:
- [ ] `uv run half-america export --help` shows new options
- [ ] Running export creates files named `lambda_0.XX_pop_0.YY.json`
- [ ] Total of 380 files created (20 λ × 19 pop)
- [ ] Total file size is reasonable (~2-5 MB)
- [ ] Files contain valid TopoJSON with correct metadata

**Implementation Note**: After completing this phase, proceed to Phase 5.

---

## Phase 5: Frontend - Parameter Configuration Updates

### Overview
Update the parameter configuration to support 2D grid of (λ, population) values.

### Changes Required

#### 1. Rename and extend lambda types
**File**: `web/src/types/lambda.ts` → rename to `web/src/types/parameters.ts`
**Changes**: Add population values and update lambda to 5% steps

```typescript
// Lambda values: 0.00, 0.05, 0.10, ..., 0.95 (20 values)
export const LAMBDA_VALUES = [
  0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45,
  0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95,
] as const;

export type LambdaValue = (typeof LAMBDA_VALUES)[number];

// Population values: 0.05, 0.10, ..., 0.95 (19 values)
export const POPULATION_VALUES = [
  0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45,
  0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95,
] as const;

export type PopulationValue = (typeof POPULATION_VALUES)[number];

// Default values
export const DEFAULT_LAMBDA: LambdaValue = 0.5;
export const DEFAULT_POPULATION: PopulationValue = 0.5;

// File path generation - now includes both parameters
export const getTopoJsonPath = (lambda: LambdaValue, population: PopulationValue): string =>
  `${import.meta.env.BASE_URL}data/lambda_${lambda.toFixed(2)}_pop_${population.toFixed(2)}.json`;

// For backwards compatibility during migration (can remove later)
export const getLegacyTopoJsonPath = (lambda: LambdaValue): string =>
  `${import.meta.env.BASE_URL}data/lambda_${lambda.toFixed(2)}.json`;
```

#### 2. Update imports across frontend
**Files**: All files importing from `types/lambda.ts`
**Changes**: Update import paths to `types/parameters`

Files to update:
- `web/src/hooks/useTopoJsonLoader.ts`
- `web/src/components/LambdaSlider.tsx`
- `web/src/components/MapTab.tsx`
- `web/src/components/SummaryPanel.tsx`

### Success Criteria

#### Automated Verification:
- [ ] `cd web && npm run build` succeeds (no TypeScript errors)
- [ ] `cd web && npm run lint` passes

#### Manual Verification:
- [ ] All imports updated to use new file path
- [ ] TypeScript types are correctly inferred

**Implementation Note**: After completing this phase, proceed directly to Phase 6 (no manual pause needed - this is just type refactoring).

---

## Phase 6: Frontend - Population Slider Component

### Overview
Create the PopulationSlider component, styled to match LambdaSlider.

### Changes Required

#### 1. Create PopulationSlider component
**File**: `web/src/components/PopulationSlider.tsx` (new file)
**Changes**: Create component similar to LambdaSlider

```tsx
import { useState } from 'react';
import { POPULATION_VALUES, PopulationValue } from '../types/parameters';
import './PopulationSlider.css';

interface PopulationSliderProps {
  value: PopulationValue;
  onChange: (value: PopulationValue) => void;
  disabled?: boolean;
}

export function PopulationSlider({ value, onChange, disabled }: PopulationSliderProps) {
  const stepIndex = POPULATION_VALUES.indexOf(value);
  const [showTooltip, setShowTooltip] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const index = parseInt(e.target.value, 10);
    onChange(POPULATION_VALUES[index]);
  };

  return (
    <div
      className={`population-slider ${showTooltip ? 'tooltip-visible' : ''}`}
    >
      <div className="slider-header">
        <label htmlFor="population-slider">Population Target</label>
        <button
          className="info-icon"
          aria-label="What is population target?"
          onClick={() => setShowTooltip(!showTooltip)}
          onBlur={() => setShowTooltip(false)}
        >
          ?
        </button>
      </div>

      {showTooltip && (
        <div className="tooltip" role="tooltip">
          <p>
            <strong>Population target</strong> sets how much of America's population
            to include in the highlighted region.
          </p>
          <p>
            At 50%, you see where half of Americans live. Try 25% to see
            extreme concentration, or 75% to see how much land is needed
            for three-quarters of the population.
          </p>
        </div>
      )}

      <div className="slider-labels">
        <span className="label-left">5%</span>
        <span className="label-right">95%</span>
      </div>

      <input
        id="population-slider"
        type="range"
        min={0}
        max={POPULATION_VALUES.length - 1}
        step={1}
        value={stepIndex}
        onChange={handleChange}
        disabled={disabled}
        aria-valuemin={5}
        aria-valuemax={95}
        aria-valuenow={value * 100}
        aria-valuetext={`${(value * 100).toFixed(0)}% of population`}
      />
      <span className="population-value">{(value * 100).toFixed(0)}%</span>
    </div>
  );
}
```

#### 2. Create PopulationSlider styles
**File**: `web/src/components/PopulationSlider.css` (new file)
**Changes**: Style to match LambdaSlider, positioned below it

```css
.population-slider {
  position: fixed;
  bottom: 16px;
  left: 16px;
  right: 16px;
  background: rgba(30, 30, 30, 0.9);
  padding: 12px 16px;
  border-radius: 8px;
  z-index: 100;
  backdrop-filter: blur(8px);
}

/* Position below lambda slider on desktop */
@media (min-width: 768px) {
  .population-slider {
    position: fixed;
    top: 100px; /* Below LambdaSlider which is at top: 16px */
    left: 16px;
    right: auto;
    bottom: auto;
    width: 360px;
  }
}

/* Mobile: stack above lambda slider */
@media (max-width: 767px) {
  .population-slider {
    bottom: 140px; /* Lambda slider is at bottom: 70px, this is above */
  }
}

.population-slider.tooltip-visible {
  z-index: 10000;
}

.slider-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.slider-header label {
  font-size: 14px;
  font-weight: 500;
  color: #fff;
}

.info-icon {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.5);
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.info-icon:hover {
  background: rgba(255, 255, 255, 0.1);
}

.tooltip {
  background: rgba(0, 0, 0, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
  font-size: 13px;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.9);
}

.tooltip p {
  margin: 0 0 8px 0;
}

.tooltip p:last-child {
  margin-bottom: 0;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 4px;
}

input[type="range"] {
  width: 100%;
  height: 6px;
  -webkit-appearance: none;
  appearance: none;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
  outline: none;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #0072b2;
  cursor: pointer;
  border: 2px solid #fff;
}

input[type="range"]::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #0072b2;
  cursor: pointer;
  border: 2px solid #fff;
}

input[type="range"]:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.population-value {
  display: block;
  text-align: center;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 4px;
}
```

### Success Criteria

#### Automated Verification:
- [ ] `cd web && npm run build` succeeds
- [ ] `cd web && npm run lint` passes

#### Manual Verification:
- [ ] Component renders correctly in isolation
- [ ] Slider thumb moves smoothly
- [ ] Tooltip appears on ? click
- [ ] Styling matches LambdaSlider

**Implementation Note**: After completing this phase, proceed to Phase 7 to update the data loader.

---

## Phase 7: Frontend - Data Loader Updates

### Overview
Update the TopoJSON loader to handle 2D grid of (λ, population) files.

### Changes Required

#### 1. Update loader hook for 2D grid
**File**: `web/src/hooks/useTopoJsonLoader.ts`
**Changes**: Load all (λ × population) combinations

```typescript
import { Feature, FeatureCollection, Geometry, MultiPolygon, Position } from 'geojson';
import { useCallback, useSyncExternalStore } from 'react';
import * as topojson from 'topojson-client';
import {
  LAMBDA_VALUES,
  POPULATION_VALUES,
  LambdaValue,
  PopulationValue,
  getTopoJsonPath
} from '../types/parameters';

// ... existing interfaces ...

// Key type for the 2D map
type DataKey = `${LambdaValue}_${PopulationValue}`;

const makeKey = (lambda: LambdaValue, population: PopulationValue): DataKey =>
  `${lambda}_${population}`;

// Update LoaderState to use new key type
type LoaderState =
  | { status: 'idle' }
  | { status: 'loading'; loaded: number; total: number }
  | { status: 'success'; data: Map<DataKey, FeatureCollection<Geometry, HalfAmericaProperties>> }
  | { status: 'error'; error: Error };

// ... existing helper functions ...

async function loadSingleTopoJSON(
  lambda: LambdaValue,
  population: PopulationValue
): Promise<FeatureCollection<Geometry, HalfAmericaProperties>> {
  const response = await fetch(getTopoJsonPath(lambda, population));
  if (!response.ok) {
    throw new Error(
      `Failed to load lambda_${lambda.toFixed(2)}_pop_${population.toFixed(2)}.json: ${response.status}`
    );
  }
  const topology = (await response.json()) as HalfAmericaTopology;
  const geojson = topojson.feature(
    topology,
    topology.objects.selected_region
  ) as FeatureCollection<Geometry, HalfAmericaProperties>;
  return explodeMultiPolygons(geojson);
}

async function performLoad() {
  const total = LAMBDA_VALUES.length * POPULATION_VALUES.length;
  cachedState = { status: 'loading', loaded: 0, total };
  notifyListeners();

  const dataMap = new Map<DataKey, FeatureCollection<Geometry, HalfAmericaProperties>>();

  try {
    const BATCH_SIZE = 10;

    // Generate all (lambda, population) pairs
    const pairs: Array<{ lambda: LambdaValue; population: PopulationValue }> = [];
    for (const lambda of LAMBDA_VALUES) {
      for (const population of POPULATION_VALUES) {
        pairs.push({ lambda, population });
      }
    }

    // Batch load
    const batches: typeof pairs[] = [];
    for (let i = 0; i < pairs.length; i += BATCH_SIZE) {
      batches.push(pairs.slice(i, i + BATCH_SIZE));
    }

    let loadedCount = 0;
    for (const batch of batches) {
      const results = await Promise.all(
        batch.map(async ({ lambda, population }) => {
          const geojson = await loadSingleTopoJSON(lambda, population);
          return { lambda, population, geojson };
        })
      );

      for (const { lambda, population, geojson } of results) {
        dataMap.set(makeKey(lambda, population), geojson);
      }

      loadedCount += batch.length;
      cachedState = { status: 'loading', loaded: loadedCount, total };
      notifyListeners();
    }

    cachedState = { status: 'success', data: dataMap };
  } catch (err) {
    cachedState = {
      status: 'error',
      error: err instanceof Error ? err : new Error(String(err)),
    };
  }
  notifyListeners();
}

// Export helper for components to get data
export function getDataForParams(
  state: LoaderState,
  lambda: LambdaValue,
  population: PopulationValue
): FeatureCollection<Geometry, HalfAmericaProperties> | undefined {
  if (state.status !== 'success') return undefined;
  return state.data.get(makeKey(lambda, population));
}

// ... rest of hook unchanged ...
```

### Success Criteria

#### Automated Verification:
- [ ] `cd web && npm run build` succeeds
- [ ] `cd web && npm run lint` passes

#### Manual Verification:
- [ ] Loading screen shows correct total (380 files)
- [ ] All files load successfully
- [ ] No console errors

**Implementation Note**: After completing this phase, proceed to Phase 8 to wire up the map.

---

## Phase 8: Frontend - Map Integration

### Overview
Wire up both sliders to control map layer visibility.

### Changes Required

#### 1. Update MapTab with population state
**File**: `web/src/components/MapTab.tsx`
**Changes**: Add population state and update layer logic

```typescript
import { useState, useMemo, useEffect, useRef } from 'react';
import { Map, MapRef } from 'react-map-gl/maplibre';
import { GeoJsonLayer } from '@deck.gl/layers';
import { DeckGLOverlay } from './DeckGLOverlay';
import { LambdaSlider } from './LambdaSlider';
import { PopulationSlider } from './PopulationSlider';
import { SummaryPanel } from './SummaryPanel';
import { MapTitle } from './MapTitle';
import { useKeepMounted } from '../hooks/useKeepMounted';
import { getDataForParams } from '../hooks/useTopoJsonLoader';
import {
  LAMBDA_VALUES,
  POPULATION_VALUES,
  LambdaValue,
  PopulationValue,
  DEFAULT_LAMBDA,
  DEFAULT_POPULATION
} from '../types/parameters';

// ... existing constants ...

export function MapTab({ isActive, loaderState }: MapTabProps) {
  const { shouldRender, isVisible } = useKeepMounted(isActive);
  const mapRef = useRef<MapRef>(null);
  const [currentLambda, setCurrentLambda] = useState<LambdaValue>(DEFAULT_LAMBDA);
  const [currentPopulation, setCurrentPopulation] = useState<PopulationValue>(DEFAULT_POPULATION);

  // ... existing resize effect ...

  // Create layers for all (lambda, population) combinations
  const layers = useMemo(() => {
    if (loaderState.status !== 'success') return [];

    const allLayers: GeoJsonLayer[] = [];

    for (const lambda of LAMBDA_VALUES) {
      for (const population of POPULATION_VALUES) {
        const data = getDataForParams(loaderState, lambda, population);
        if (!data) continue;

        allLayers.push(
          new GeoJsonLayer({
            id: `layer-${lambda.toFixed(2)}-${population.toFixed(2)}`,
            data,
            visible: lambda === currentLambda && population === currentPopulation,
            filled: true,
            stroked: false,
            getFillColor: FILL_COLOR,
            pickable: true,
            autoHighlight: true,
            highlightColor: HIGHLIGHT_COLOR,
          })
        );
      }
    }

    return allLayers;
  }, [loaderState, currentLambda, currentPopulation]);

  // ... rest of component ...

  return (
    <div
      className="map-tab"
      role="tabpanel"
      id="map-tab"
      aria-labelledby="map"
      style={{ visibility: isVisible ? 'visible' : 'collapse' }}
    >
      {showMap && (
        <>
          <Map
            ref={mapRef}
            initialViewState={getInitialViewState()}
            style={{ width: '100%', height: '100vh' }}
            mapStyle={CARTO_DARK_MATTER}
          >
            <DeckGLOverlay layers={layers} interleaved />
          </Map>
          <MapTitle />
          <LambdaSlider
            value={currentLambda}
            onChange={setCurrentLambda}
            disabled={loaderState.status !== 'success'}
          />
          <PopulationSlider
            value={currentPopulation}
            onChange={setCurrentPopulation}
            disabled={loaderState.status !== 'success'}
          />
          <SummaryPanel
            data={getDataForParams(loaderState, currentLambda, currentPopulation)}
            lambda={currentLambda}
            populationTarget={currentPopulation}
          />
        </>
      )}
    </div>
  );
}
```

#### 2. Update SummaryPanel to show target
**File**: `web/src/components/SummaryPanel.tsx`
**Changes**: Add population target display

```typescript
interface SummaryPanelProps {
  data: FeatureCollection<Geometry, HalfAmericaProperties> | undefined;
  lambda: LambdaValue;
  populationTarget: PopulationValue;
}

export function SummaryPanel({ data, lambda, populationTarget }: SummaryPanelProps) {
  // ... existing logic ...

  return (
    <div className={`summary-panel ${showTooltip ? 'tooltip-visible' : ''}`}>
      {/* ... existing content ... */}

      {/* Add target vs actual comparison if different */}
      <div className="summary-row">
        <span className="summary-label">Target</span>
        <span className="summary-value">{(populationTarget * 100).toFixed(0)}%</span>
      </div>

      {/* ... rest of existing rows ... */}
    </div>
  );
}
```

#### 3. Update LambdaSlider positioning
**File**: `web/src/components/LambdaSlider.css`
**Changes**: Adjust positioning to accommodate population slider below

```css
/* Desktop: Lambda slider stays at top */
@media (min-width: 768px) {
  .lambda-slider {
    top: 16px;
    /* No change needed - PopulationSlider positions itself below */
  }
}

/* Mobile: Lambda slider at bottom, population above it */
@media (max-width: 767px) {
  .lambda-slider {
    bottom: 70px;
    /* Population slider at bottom: 140px, above this */
  }
}
```

### Success Criteria

#### Automated Verification:
- [ ] `cd web && npm run build` succeeds
- [ ] `cd web && npm run lint` passes

#### Manual Verification:
- [ ] Both sliders render and are positioned correctly
- [ ] Changing lambda updates the map
- [ ] Changing population updates the map
- [ ] Changing both together works
- [ ] SummaryPanel shows target percentage
- [ ] Default view shows λ=0.50, pop=50%

**Implementation Note**: After completing this phase and all automated verification passes, pause here for comprehensive manual testing before proceeding to Phase 9.

---

## Phase 9: Cleanup and Documentation

### Overview
Clean up old files, run full precomputation, deploy, and update documentation.

### Changes Required

#### 1. Run full precomputation
```bash
# Clear old cache
rm -rf data/cache/processed/sweep_*.pkl

# Precompute all combinations (this will take several minutes)
uv run half-america precompute --lambda-step 0.05 --pop-step 0.05

# Export to web directory
uv run half-america export --lambda-step 0.05 --pop-step 0.05 --output-dir web/public/data --force
```

#### 2. Remove old TopoJSON files
```bash
# Remove old single-parameter files
rm web/public/data/lambda_*.json

# Verify new files exist
ls web/public/data/ | head -20
```

#### 3. Update ROADMAP.md
**File**: `ROADMAP.md`
**Changes**: Add Phase for population slider, move to Future Enhancements completed

Move "Custom thresholds: Allow users to select different population percentages" from Future Enhancements to completed phases.

#### 4. Update CLAUDE.md if needed
**File**: `CLAUDE.md`
**Changes**: Update any references to single-parameter files

#### 5. Test deployment
```bash
cd web
npm run build
npm run preview
# Test locally before pushing
```

### Success Criteria

#### Automated Verification:
- [ ] `uv run pytest` - all tests pass
- [ ] `uv run mypy src/` - no type errors
- [ ] `uv run ruff check src/` - no lint errors
- [ ] `cd web && npm run build` - builds successfully
- [ ] `cd web && npm run lint` - no lint errors

#### Manual Verification:
- [ ] 380 TopoJSON files exist in `web/public/data/`
- [ ] Total file size is reasonable (target: 2-5 MB)
- [ ] Local preview works with both sliders
- [ ] λ=0.00 and λ=0.95 work correctly
- [ ] pop=5% and pop=95% work correctly
- [ ] Switching between tabs preserves slider positions
- [ ] Mobile layout works correctly

**Implementation Note**: After all verification passes, the feature is ready for deployment to GitHub Pages.

---

## Testing Strategy

### Unit Tests

#### Backend
- Test parametric solver finds breakpoints correctly
- Test `find_partition_for_target` returns closest breakpoint
- Test CLI with new parameters parses correctly
- Test export creates files with correct naming

#### Frontend
- Test parameter types are correctly defined
- Test `getTopoJsonPath` generates correct paths
- Test `makeKey` creates unique keys

### Integration Tests

- Run parametric solve on small test graph, verify breakpoints
- Precompute with 2 λ values and verify cache file
- Export small grid and verify file contents
- Load exported files in browser and verify rendering

### Manual Testing Steps

1. Run `uv run half-america precompute --lambda-step 0.05`
2. Verify single parametric cache file created
3. Check output shows breakpoint counts per λ (expect thousands total)
4. Run `uv run half-america export --lambda-step 0.05 --pop-step 0.05 --output-dir web/public/data`
5. Verify 380 JSON files created
6. Run `cd web && npm run dev`
7. Test lambda slider at λ=0, λ=0.5, λ=0.95
8. Test population slider at 5%, 50%, 95%
9. Test diagonal movement (change both simultaneously)
10. Test on mobile viewport
11. Test tab switching preserves state

## Performance Considerations

- **Precomputation speedup**: ~20 parametric solves instead of ~5,700 binary search iterations (~150× faster)
- **Breakpoint storage**: Thousands of breakpoints per λ stored in cache file (may be ~100-500MB)
- **File count**: 380 TopoJSON files is 3.8× current (99 files). Batch loading should handle this.
- **Memory**: ~380 FeatureCollections in memory. May need to increase batch size for faster loading.
- **Initial load time**: Expect ~2-3× longer initial load. Loading overlay shows progress.
- **Switching speed**: Should remain instant since all layers pre-created.

## Migration Notes

- Old TopoJSON files (`lambda_X.XX.json`) will be replaced with new format (`lambda_X.XX_pop_X.XX.json`)
- Old sweep cache files (`sweep_*.pkl`) will be replaced with parametric cache (`parametric_*.pkl`)
- No backwards compatibility needed - this is a complete replacement
- Old cache files can be deleted after successful migration

## License Considerations

The Hochbaum Pseudoflow library uses an **academic non-commercial license** (UC Berkeley Regents). This is acceptable for:
- Portfolio projects (not sold commercially)
- Academic research
- Personal use

If commercial use is needed in the future, consider:
- Reverting to binary search approach (slower but MIT-licensed PyMaxFlow)
- Implementing custom parametric solver
- Contacting UC Berkeley for commercial licensing

## References

- Research document: `thoughts/shared/research/2025-11-27-population-slider-feasibility.md`
- Pseudoflow library: https://github.com/hochbaumGroup/pseudoflow-parametric-cut
- Gallo, Grigoriadis, Tarjan (1989): "A Fast Parametric Maximum Flow Algorithm and Applications"
- Current frontend architecture: `web/src/` (analyzed via codebase-analyzer agent)
- Export implementation: `src/half_america/postprocess/export.py`
- CLI implementation: `src/half_america/cli.py`
