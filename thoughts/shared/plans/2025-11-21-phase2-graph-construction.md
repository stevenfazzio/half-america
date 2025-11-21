# Phase 2: Graph Construction Implementation Plan

## Overview

Build the spatial adjacency graph from Census Tract data, including tract-level attributes (population, area, shared boundary lengths), Queen contiguity adjacency, and the s-t flow network structure required for Phase 3 optimization.

## Current State Analysis

**Phase 1 provides:**
- `load_all_tracts()` returns a GeoDataFrame with ~73,000 Census Tracts
- Columns: `GEOID` (str), `geometry` (Polygon), `population` (int), `area_sqm` (float)
- CRS: EPSG:5070 (NAD83 / Conus Albers Equal Area) - meters-based
- Caching: `data/cache/processed/all_tracts_{TIGER_YEAR}_{ACS_YEAR}.parquet`

**What Phase 2 adds:**
- Spatial adjacency graph using libpysal Queen contiguity
- Shared boundary lengths (l_ij) between adjacent tracts
- Characteristic length scale (ρ = median(√a_i))
- s-t flow network structure for PyMaxFlow

### Key Discoveries:
- `src/half_america/data/pipeline.py:48-96` - `load_all_tracts()` main entry point
- `src/half_america/data/cleaning.py:106-110` - `add_area_column()` adds `area_sqm`
- `src/half_america/data/constants.py` - `TARGET_CRS = "EPSG:5070"`
- `src/half_america/config.py:14-19` - Cache directory constants
- libpysal already in `uv.lock` but not yet used
- PyMaxFlow needs to be added as a dependency

## Desired End State

After Phase 2, the system can:
1. Build a spatial adjacency graph from the Phase 1 GeoDataFrame
2. Compute shared boundary lengths for all ~400,000-500,000 neighbor pairs
3. Calculate the characteristic length scale (ρ)
4. Construct a PyMaxFlow graph structure given λ and μ parameters
5. Cache computed graph data for reuse

**Verification:**
- `uv run pytest tests/test_graph/` passes
- `uv run mypy src/half_america/graph/` passes with no errors
- Manual verification: Load cached graph, inspect neighbor counts and boundary lengths

## What We're NOT Doing

- **Phase 3 optimization**: Binary search for μ, solving max-flow, extracting results
- **Phase 4 post-processing**: Dissolving selected tracts, simplification, TopoJSON export
- **Performance optimization**: Parallelization, Numba JIT (can be added later if needed)
- **Alternative contiguity**: Rook contiguity, distance-based neighbors

## Implementation Approach

1. Create new `src/half_america/graph/` module following Phase 1 patterns
2. Use integer indexing (0 to n-1) for PyMaxFlow compatibility
3. Store raw values (meters), normalize at network construction time
4. Cache computed graph data to avoid recomputation

---

## Phase 2.1: Dependencies and Module Setup

### Overview
Add PyMaxFlow dependency and create the graph module structure.

### Changes Required:

#### 1. Add PyMaxFlow Dependency
**File**: `pyproject.toml`
**Changes**: Add PyMaxFlow to dependencies

```toml
dependencies = [
    # ... existing dependencies ...

    # Graph construction (Phase 2)
    "libpysal>=4.9",
    "PyMaxflow>=1.3",
]
```

#### 2. Create Module Structure
**Files**: Create new module files

```
src/half_america/graph/
├── __init__.py
├── adjacency.py
├── boundary.py
└── network.py
```

#### 3. Module Init
**File**: `src/half_america/graph/__init__.py`

```python
"""Graph construction for Half of America optimization."""

from half_america.graph.adjacency import build_adjacency, AdjacencyResult
from half_america.graph.boundary import (
    compute_boundary_lengths,
    compute_rho,
    GraphAttributes,
)
from half_america.graph.network import build_flow_network

__all__ = [
    "build_adjacency",
    "AdjacencyResult",
    "compute_boundary_lengths",
    "compute_rho",
    "GraphAttributes",
    "build_flow_network",
]
```

### Success Criteria:

#### Automated Verification:
- [x] Dependencies install cleanly: `uv sync`
- [x] Import works: `python -c "from half_america.graph import build_adjacency"`
- [x] Type checking passes: `uv run mypy src/half_america/graph/`

#### Manual Verification:
- [x] Verify libpysal and PyMaxflow versions are compatible

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation before proceeding to the next phase.

---

## Phase 2.2: Adjacency Graph Construction

### Overview
Build the spatial adjacency graph using libpysal Queen contiguity with integer indexing for PyMaxFlow compatibility.

### Changes Required:

#### 1. Adjacency Module
**File**: `src/half_america/graph/adjacency.py`

```python
"""Spatial adjacency graph construction using libpysal."""

from typing import NamedTuple
import geopandas as gpd
from libpysal.weights import Queen, W, attach_islands


class AdjacencyResult(NamedTuple):
    """Result of adjacency graph construction."""

    weights: W
    edges: list[tuple[int, int]]
    num_nodes: int
    num_edges: int
    num_islands_attached: int


def build_adjacency(
    gdf: gpd.GeoDataFrame,
    verbose: bool = True,
) -> AdjacencyResult:
    """
    Build Queen contiguity adjacency graph from tract geometries.

    Uses integer indexing (0 to n-1) for PyMaxFlow compatibility.
    Islands (isolated tracts) are attached to their nearest neighbors.

    Args:
        gdf: GeoDataFrame with tract geometries (from load_all_tracts)
        verbose: If True, print progress messages

    Returns:
        AdjacencyResult with weights object, edge list, and statistics
    """
    num_nodes = len(gdf)

    if verbose:
        print(f"Building adjacency graph for {num_nodes:,} tracts...")

    # Build Queen contiguity with integer indices (0 to n-1)
    # use_index=False ensures integer indexing for PyMaxFlow compatibility
    w = Queen.from_dataframe(gdf, use_index=False)

    if verbose:
        print(f"  Initial neighbors: mean={w.mean_neighbors:.1f}, max={w.max_neighbors}")

    # Handle islands (tracts with no neighbors)
    num_islands = len(w.islands)
    if num_islands > 0:
        if verbose:
            print(f"  Attaching {num_islands} island tracts to nearest neighbors...")
        w = attach_islands(w, gdf)

    # Extract unique edge pairs (i < j to avoid duplicates)
    edges: list[tuple[int, int]] = []
    for i, neighbors in w.neighbors.items():
        for j in neighbors:
            if i < j:
                edges.append((i, j))

    num_edges = len(edges)

    if verbose:
        print(f"  Final graph: {num_nodes:,} nodes, {num_edges:,} edges")
        print(f"  Connected components: {w.n_components}")

    return AdjacencyResult(
        weights=w,
        edges=edges,
        num_nodes=num_nodes,
        num_edges=num_edges,
        num_islands_attached=num_islands,
    )
```

### Success Criteria:

#### Automated Verification:
- [x] Unit tests pass: `uv run pytest tests/test_graph/test_adjacency.py -v`
- [x] Type checking passes: `uv run mypy src/half_america/graph/adjacency.py`
- [x] Linting passes: `uv run ruff check src/half_america/graph/adjacency.py`

#### Manual Verification:
- [x] Run with sample data: verify neighbor counts are reasonable (mean ~6)
- [x] Verify no islands remain after `attach_islands()`

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation before proceeding to the next phase.

---

## Phase 2.3: Boundary Length Calculation

### Overview
Compute shared boundary lengths (l_ij) between adjacent tracts and the characteristic length scale (ρ).

### Changes Required:

#### 1. Boundary Module
**File**: `src/half_america/graph/boundary.py`

```python
"""Shared boundary length calculations."""

from typing import NamedTuple
import numpy as np
import geopandas as gpd
from shapely import intersection, length


class GraphAttributes(NamedTuple):
    """Computed graph attributes for optimization."""

    population: np.ndarray      # p_i for each tract (int)
    area: np.ndarray            # a_i for each tract in sq meters (float)
    rho: float                  # Characteristic length scale in meters
    edge_lengths: dict[tuple[int, int], float]  # l_ij in meters


def compute_rho(gdf: gpd.GeoDataFrame) -> float:
    """
    Compute characteristic length scale for normalization.

    ρ = median(√a_i) where a_i is tract area in square meters.

    Args:
        gdf: GeoDataFrame with area_sqm column

    Returns:
        Characteristic length scale in meters
    """
    sqrt_areas = np.sqrt(gdf["area_sqm"].values)
    return float(np.median(sqrt_areas))


def compute_boundary_lengths(
    gdf: gpd.GeoDataFrame,
    edges: list[tuple[int, int]],
    verbose: bool = True,
) -> dict[tuple[int, int], float]:
    """
    Compute shared boundary lengths for all adjacent tract pairs.

    Uses vectorized Shapely operations for performance.

    Args:
        gdf: GeoDataFrame with tract geometries
        edges: List of (i, j) neighbor pairs from adjacency graph
        verbose: If True, print progress messages

    Returns:
        Dictionary mapping (i, j) -> shared boundary length in meters
    """
    if verbose:
        print(f"Computing boundary lengths for {len(edges):,} edges...")

    # Extract geometry boundaries (LineStrings)
    boundaries = gdf.geometry.boundary.values

    # Prepare index arrays for vectorized operation
    i_indices = np.array([e[0] for e in edges])
    j_indices = np.array([e[1] for e in edges])

    # Vectorized intersection and length calculation
    shared_boundaries = intersection(boundaries[i_indices], boundaries[j_indices])
    lengths = length(shared_boundaries)

    # Build dictionary with both directions for easy lookup
    edge_lengths: dict[tuple[int, int], float] = {}
    for idx, (i, j) in enumerate(edges):
        l_ij = float(lengths[idx])
        edge_lengths[(i, j)] = l_ij
        edge_lengths[(j, i)] = l_ij  # Symmetric

    if verbose:
        nonzero_count = sum(1 for l in lengths if l > 0)
        print(f"  Non-zero boundary lengths: {nonzero_count:,} ({100*nonzero_count/len(edges):.1f}%)")
        print(f"  Mean boundary length: {np.mean(lengths):.1f} m")
        print(f"  Max boundary length: {np.max(lengths):.1f} m")

    return edge_lengths


def compute_graph_attributes(
    gdf: gpd.GeoDataFrame,
    edges: list[tuple[int, int]],
    verbose: bool = True,
) -> GraphAttributes:
    """
    Compute all graph attributes needed for optimization.

    Args:
        gdf: GeoDataFrame with population, area_sqm, and geometry columns
        edges: List of (i, j) neighbor pairs from adjacency graph
        verbose: If True, print progress messages

    Returns:
        GraphAttributes with population, area, rho, and edge_lengths
    """
    population = gdf["population"].values.astype(np.int64)
    area = gdf["area_sqm"].values.astype(np.float64)
    rho = compute_rho(gdf)
    edge_lengths = compute_boundary_lengths(gdf, edges, verbose=verbose)

    if verbose:
        print(f"  Characteristic length scale (ρ): {rho:.1f} m ({rho/1000:.2f} km)")
        print(f"  Total population: {population.sum():,}")
        print(f"  Total area: {area.sum()/1e6:.0f} km²")

    return GraphAttributes(
        population=population,
        area=area,
        rho=rho,
        edge_lengths=edge_lengths,
    )
```

### Success Criteria:

#### Automated Verification:
- [x] Unit tests pass: `uv run pytest tests/test_graph/test_boundary.py -v`
- [x] Type checking passes: `uv run mypy src/half_america/graph/boundary.py`
- [x] Linting passes: `uv run ruff check src/half_america/graph/boundary.py`

#### Manual Verification:
- [x] Verify ρ is reasonable (expected: ~2-5 km for typical census tracts)
- [x] Verify boundary lengths are in reasonable range (0 to ~100 km)
- [x] Check that corner-only neighbors have near-zero boundary lengths

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation before proceeding to the next phase.

---

## Phase 2.4: Flow Network Construction

### Overview
Build the PyMaxFlow graph structure with terminal edges (t-links) and neighborhood edges (n-links).

### Changes Required:

#### 1. Network Module
**File**: `src/half_america/graph/network.py`

```python
"""s-t flow network construction for graph cut optimization."""

import numpy as np
import maxflow

from half_america.graph.boundary import GraphAttributes


def build_flow_network(
    attributes: GraphAttributes,
    edges: list[tuple[int, int]],
    lambda_param: float,
    mu: float,
) -> maxflow.Graph:
    """
    Construct s-t flow network for graph cut optimization.

    The network encodes the energy function:
    E(X) = λ Σ(l_ij/ρ)|x_i - x_j| + (1-λ) Σ a_i x_i - μ Σ p_i x_i

    Args:
        attributes: GraphAttributes with population, area, rho, edge_lengths
        edges: List of (i, j) neighbor pairs (only i < j pairs)
        lambda_param: Surface tension parameter [0, 1]
        mu: Lagrange multiplier for population constraint

    Returns:
        PyMaxFlow Graph ready for maxflow() computation
    """
    num_nodes = len(attributes.population)
    num_edges = len(edges)

    # Create graph with float capacities
    g: maxflow.Graph = maxflow.Graph[float](num_nodes, num_edges)
    g.add_nodes(num_nodes)

    # Add terminal edges (t-links)
    # Source capacity: μ × p_i (population reward for inclusion)
    # Sink capacity: (1-λ) × a_i (area cost for inclusion)
    for i in range(num_nodes):
        source_cap = mu * attributes.population[i]
        sink_cap = (1 - lambda_param) * attributes.area[i]
        g.add_tedge(i, source_cap, sink_cap)

    # Add neighborhood edges (n-links)
    # Capacity: λ × l_ij / ρ (boundary cost, normalized)
    rho = attributes.rho
    for i, j in edges:
        l_ij = attributes.edge_lengths[(i, j)]
        capacity = lambda_param * l_ij / rho
        g.add_edge(i, j, capacity, capacity)  # Symmetric

    return g


def get_partition(g: maxflow.Graph, num_nodes: int) -> np.ndarray:
    """
    Extract partition assignment after maxflow computation.

    Args:
        g: PyMaxFlow Graph after maxflow() has been called
        num_nodes: Number of nodes in the graph

    Returns:
        Boolean array where True = node in source partition (selected)
    """
    return np.array([g.get_segment(i) == 0 for i in range(num_nodes)])
```

### Success Criteria:

#### Automated Verification:
- [x] Unit tests pass: `uv run pytest tests/test_graph/test_network.py -v`
- [x] Type checking passes: `uv run mypy src/half_america/graph/network.py`
- [x] Linting passes: `uv run ruff check src/half_america/graph/network.py`

#### Manual Verification:
- [x] Build network with test data, verify maxflow() runs without error
- [x] Verify partition extraction works correctly

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation before proceeding to the next phase.

---

## Phase 2.5: Caching and Integration

### Overview
Add caching for computed graph data and create the main pipeline function.

### Changes Required:

#### 1. Update Graph Init with Pipeline Function
**File**: `src/half_america/graph/__init__.py`
**Changes**: Add pipeline function and cache support

```python
"""Graph construction for Half of America optimization."""

from half_america.graph.adjacency import build_adjacency, AdjacencyResult
from half_america.graph.boundary import (
    compute_boundary_lengths,
    compute_rho,
    compute_graph_attributes,
    GraphAttributes,
)
from half_america.graph.network import build_flow_network, get_partition
from half_america.graph.pipeline import load_graph_data, GraphData

__all__ = [
    # Adjacency
    "build_adjacency",
    "AdjacencyResult",
    # Boundary
    "compute_boundary_lengths",
    "compute_rho",
    "compute_graph_attributes",
    "GraphAttributes",
    # Network
    "build_flow_network",
    "get_partition",
    # Pipeline
    "load_graph_data",
    "GraphData",
]
```

#### 2. Graph Pipeline with Caching
**File**: `src/half_america/graph/pipeline.py`

```python
"""Graph data pipeline with caching."""

from typing import NamedTuple
from pathlib import Path
import pickle

import numpy as np
import geopandas as gpd

from half_america.data.cache import ensure_cache_dirs, get_processed_cache_path
from half_america.config import TIGER_YEAR, ACS_YEAR
from half_america.graph.adjacency import build_adjacency
from half_america.graph.boundary import compute_graph_attributes, GraphAttributes


class GraphData(NamedTuple):
    """Complete graph data for optimization."""

    edges: list[tuple[int, int]]
    attributes: GraphAttributes
    num_nodes: int
    num_edges: int


def _get_graph_cache_path() -> Path:
    """Get path to cached graph data."""
    return get_processed_cache_path(f"graph_{TIGER_YEAR}_{ACS_YEAR}").with_suffix(".pkl")


def load_graph_data(
    gdf: gpd.GeoDataFrame,
    force_rebuild: bool = False,
    use_cache: bool = True,
    verbose: bool = True,
) -> GraphData:
    """
    Load or build graph data from tract GeoDataFrame.

    Args:
        gdf: GeoDataFrame from load_all_tracts()
        force_rebuild: If True, rebuild even if cached
        use_cache: If True, use cached data if available
        verbose: If True, print progress messages

    Returns:
        GraphData with edges, attributes, and statistics
    """
    ensure_cache_dirs()
    cache_path = _get_graph_cache_path()

    # Return cached data if available
    if use_cache and cache_path.exists() and not force_rebuild:
        if verbose:
            print(f"Loading cached graph data from {cache_path}")
        with open(cache_path, "rb") as f:
            return pickle.load(f)

    if verbose:
        print("Building graph data...")

    # Build adjacency graph
    adj_result = build_adjacency(gdf, verbose=verbose)

    # Compute graph attributes
    attributes = compute_graph_attributes(gdf, adj_result.edges, verbose=verbose)

    graph_data = GraphData(
        edges=adj_result.edges,
        attributes=attributes,
        num_nodes=adj_result.num_nodes,
        num_edges=adj_result.num_edges,
    )

    # Cache result
    with open(cache_path, "wb") as f:
        pickle.dump(graph_data, f)
    if verbose:
        print(f"Cached graph data to {cache_path}")

    return graph_data


def get_graph_summary(graph_data: GraphData) -> dict:
    """
    Get summary statistics for graph data.

    Args:
        graph_data: GraphData from load_graph_data()

    Returns:
        Dictionary with summary statistics
    """
    attrs = graph_data.attributes
    edge_lengths = list(attrs.edge_lengths.values())[::2]  # Dedupe symmetric entries

    return {
        "num_nodes": graph_data.num_nodes,
        "num_edges": graph_data.num_edges,
        "total_population": int(attrs.population.sum()),
        "half_population": int(attrs.population.sum() // 2),
        "total_area_sqkm": float(attrs.area.sum() / 1e6),
        "rho_meters": float(attrs.rho),
        "rho_km": float(attrs.rho / 1000),
        "mean_boundary_length_m": float(np.mean(edge_lengths)),
        "max_boundary_length_m": float(np.max(edge_lengths)),
        "mean_neighbors": graph_data.num_edges * 2 / graph_data.num_nodes,
    }
```

### Success Criteria:

#### Automated Verification:
- [x] Unit tests pass: `uv run pytest tests/test_graph/test_pipeline.py -v`
- [x] Full test suite passes: `uv run pytest tests/test_graph/ -v`
- [x] Type checking passes: `uv run mypy src/half_america/graph/`
- [x] Linting passes: `uv run ruff check src/half_america/graph/`

#### Manual Verification:
- [x] Run `load_graph_data()` with real data, verify cache file is created
- [x] Run again, verify cache is used (faster load)
- [x] Inspect `get_graph_summary()` output for reasonable values

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation before proceeding to the next phase.

---

## Phase 2.6: Unit Tests

### Overview
Create comprehensive unit tests for all graph modules.

### Changes Required:

#### 1. Test Directory Structure
```
tests/
├── test_graph/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_adjacency.py
│   ├── test_boundary.py
│   ├── test_network.py
│   └── test_pipeline.py
```

#### 2. Test Fixtures
**File**: `tests/test_graph/conftest.py`

```python
"""Pytest fixtures for graph tests."""

import pytest
import geopandas as gpd
import numpy as np
from shapely.geometry import box

# Create a 3x3 grid of adjacent squares for testing
# Each square is 1000m x 1000m in EPSG:5070 coordinates
GRID_ORIGIN_X = 0
GRID_ORIGIN_Y = 0
GRID_SIZE = 1000  # meters


@pytest.fixture
def grid_3x3_gdf() -> gpd.GeoDataFrame:
    """Create a 3x3 grid of adjacent squares for testing adjacency."""
    geometries = []
    geoids = []
    populations = []

    for row in range(3):
        for col in range(3):
            x0 = GRID_ORIGIN_X + col * GRID_SIZE
            y0 = GRID_ORIGIN_Y + row * GRID_SIZE
            x1 = x0 + GRID_SIZE
            y1 = y0 + GRID_SIZE
            geometries.append(box(x0, y0, x1, y1))
            geoids.append(f"{row}{col}")
            # Population varies by position (center has most)
            populations.append(1000 * (1 + row) * (1 + col))

    gdf = gpd.GeoDataFrame(
        {
            "GEOID": geoids,
            "population": populations,
            "geometry": geometries,
        },
        crs="EPSG:5070",
    )
    gdf["area_sqm"] = gdf.geometry.area
    return gdf


@pytest.fixture
def grid_with_island_gdf(grid_3x3_gdf) -> gpd.GeoDataFrame:
    """Create a 3x3 grid plus one isolated square (island)."""
    island = gpd.GeoDataFrame(
        {
            "GEOID": ["island"],
            "population": [500],
            "geometry": [box(10000, 10000, 11000, 11000)],  # Far away
        },
        crs="EPSG:5070",
    )
    island["area_sqm"] = island.geometry.area

    return gpd.GeoDataFrame(
        pd.concat([grid_3x3_gdf, island], ignore_index=True),
        crs="EPSG:5070",
    )


@pytest.fixture
def simple_edges() -> list[tuple[int, int]]:
    """Simple edge list for a 3x3 grid (Queen contiguity)."""
    # In a 3x3 grid with Queen contiguity:
    # 0-1-2
    # 3-4-5
    # 6-7-8
    # Center (4) has 8 neighbors, corners have 3, edges have 5
    return [
        (0, 1), (0, 3), (0, 4),
        (1, 2), (1, 3), (1, 4), (1, 5),
        (2, 4), (2, 5),
        (3, 4), (3, 6), (3, 7),
        (4, 5), (4, 6), (4, 7), (4, 8),
        (5, 7), (5, 8),
        (6, 7),
        (7, 8),
    ]
```

#### 3. Adjacency Tests
**File**: `tests/test_graph/test_adjacency.py`

```python
"""Tests for adjacency graph construction."""

import pytest
from half_america.graph.adjacency import build_adjacency


class TestBuildAdjacency:
    def test_builds_adjacency_for_grid(self, grid_3x3_gdf):
        """Test adjacency construction for a 3x3 grid."""
        result = build_adjacency(grid_3x3_gdf, verbose=False)

        assert result.num_nodes == 9
        # Queen contiguity: 3x3 grid has 20 unique edges
        assert result.num_edges == 20
        assert result.num_islands_attached == 0

    def test_handles_islands(self, grid_with_island_gdf):
        """Test that islands are attached to nearest neighbors."""
        result = build_adjacency(grid_with_island_gdf, verbose=False)

        assert result.num_nodes == 10
        assert result.num_islands_attached == 1
        # Island should now have at least one neighbor
        assert result.weights.islands == []

    def test_edges_are_unique(self, grid_3x3_gdf):
        """Test that edge list contains only unique pairs (i < j)."""
        result = build_adjacency(grid_3x3_gdf, verbose=False)

        for i, j in result.edges:
            assert i < j, f"Edge ({i}, {j}) should have i < j"

        # No duplicates
        assert len(result.edges) == len(set(result.edges))

    def test_center_has_most_neighbors(self, grid_3x3_gdf):
        """Test that center cell has 8 neighbors (Queen contiguity)."""
        result = build_adjacency(grid_3x3_gdf, verbose=False)

        # Center is index 4 in row-major order
        center_neighbors = result.weights.neighbors[4]
        assert len(center_neighbors) == 8
```

#### 4. Boundary Tests
**File**: `tests/test_graph/test_boundary.py`

```python
"""Tests for boundary length calculations."""

import pytest
import numpy as np
from half_america.graph.boundary import (
    compute_rho,
    compute_boundary_lengths,
    compute_graph_attributes,
)


class TestComputeRho:
    def test_computes_median_sqrt_area(self, grid_3x3_gdf):
        """Test rho computation for uniform grid."""
        rho = compute_rho(grid_3x3_gdf)

        # Each cell is 1000m x 1000m = 1,000,000 sqm
        # sqrt(1,000,000) = 1000m
        # Median of all equal values = 1000m
        assert rho == pytest.approx(1000.0, rel=0.01)


class TestComputeBoundaryLengths:
    def test_computes_shared_boundary(self, grid_3x3_gdf, simple_edges):
        """Test boundary length computation."""
        # Build actual edges from adjacency
        from half_america.graph.adjacency import build_adjacency
        result = build_adjacency(grid_3x3_gdf, verbose=False)

        edge_lengths = compute_boundary_lengths(
            grid_3x3_gdf, result.edges, verbose=False
        )

        # Adjacent squares share 1000m boundary
        # Diagonal neighbors share only a point (0m boundary)

        # Check a horizontal adjacency (0, 1)
        assert edge_lengths[(0, 1)] == pytest.approx(1000.0, rel=0.01)

        # Check a diagonal adjacency (0, 4) - should be ~0
        assert edge_lengths[(0, 4)] < 1.0  # Nearly zero

    def test_symmetric_edge_lengths(self, grid_3x3_gdf):
        """Test that edge lengths are symmetric."""
        from half_america.graph.adjacency import build_adjacency
        result = build_adjacency(grid_3x3_gdf, verbose=False)

        edge_lengths = compute_boundary_lengths(
            grid_3x3_gdf, result.edges, verbose=False
        )

        for i, j in result.edges:
            assert edge_lengths[(i, j)] == edge_lengths[(j, i)]


class TestComputeGraphAttributes:
    def test_returns_all_attributes(self, grid_3x3_gdf):
        """Test that all attributes are computed."""
        from half_america.graph.adjacency import build_adjacency
        result = build_adjacency(grid_3x3_gdf, verbose=False)

        attrs = compute_graph_attributes(
            grid_3x3_gdf, result.edges, verbose=False
        )

        assert len(attrs.population) == 9
        assert len(attrs.area) == 9
        assert attrs.rho > 0
        assert len(attrs.edge_lengths) > 0
```

#### 5. Network Tests
**File**: `tests/test_graph/test_network.py`

```python
"""Tests for flow network construction."""

import pytest
import numpy as np
from half_america.graph.boundary import GraphAttributes
from half_america.graph.network import build_flow_network, get_partition


@pytest.fixture
def simple_attributes():
    """Create simple graph attributes for testing."""
    return GraphAttributes(
        population=np.array([100, 200, 300]),
        area=np.array([1000.0, 1000.0, 1000.0]),
        rho=100.0,
        edge_lengths={(0, 1): 50.0, (1, 0): 50.0, (1, 2): 50.0, (2, 1): 50.0},
    )


class TestBuildFlowNetwork:
    def test_creates_graph(self, simple_attributes):
        """Test that a graph is created."""
        edges = [(0, 1), (1, 2)]
        g = build_flow_network(simple_attributes, edges, lambda_param=0.5, mu=0.01)

        # Should be able to call maxflow without error
        flow = g.maxflow()
        assert flow >= 0

    def test_high_mu_selects_all(self, simple_attributes):
        """Test that high mu (population reward) selects all nodes."""
        edges = [(0, 1), (1, 2)]
        g = build_flow_network(simple_attributes, edges, lambda_param=0.5, mu=1000.0)
        g.maxflow()

        partition = get_partition(g, 3)
        # With very high mu, all nodes should be selected (source partition)
        assert partition.all()

    def test_zero_mu_selects_none(self, simple_attributes):
        """Test that zero mu (no population reward) selects no nodes."""
        edges = [(0, 1), (1, 2)]
        g = build_flow_network(simple_attributes, edges, lambda_param=0.5, mu=0.0)
        g.maxflow()

        partition = get_partition(g, 3)
        # With zero mu, area cost dominates -> no nodes selected
        assert not partition.any()


class TestGetPartition:
    def test_returns_boolean_array(self, simple_attributes):
        """Test partition extraction returns correct format."""
        edges = [(0, 1), (1, 2)]
        g = build_flow_network(simple_attributes, edges, lambda_param=0.5, mu=0.01)
        g.maxflow()

        partition = get_partition(g, 3)

        assert partition.dtype == bool
        assert len(partition) == 3
```

### Success Criteria:

#### Automated Verification:
- [x] All tests pass: `uv run pytest tests/test_graph/ -v`
- [x] Test coverage is adequate: `uv run pytest tests/test_graph/ --cov=half_america.graph` (95%)

#### Manual Verification:
- [x] Review test output for any unexpected warnings
- [x] Verify tests cover edge cases (islands, zero boundaries)

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation before proceeding to the next phase.

---

## Phase 2.7: Integration Test

### Overview
Create an integration test that runs the full Phase 2 pipeline with real (small subset) data.

### Changes Required:

#### 1. Integration Test
**File**: `tests/test_graph/test_integration.py`

```python
"""Integration tests for graph construction pipeline."""

import pytest
from half_america.data import load_state_tracts
from half_america.graph import (
    build_adjacency,
    compute_graph_attributes,
    build_flow_network,
    get_partition,
)


@pytest.mark.integration
class TestGraphIntegration:
    def test_full_pipeline_single_state(self):
        """Test full graph pipeline with DC (smallest state)."""
        # Load DC tracts (District of Columbia, FIPS 11)
        gdf = load_state_tracts("11")

        # Build adjacency
        adj_result = build_adjacency(gdf, verbose=True)
        assert adj_result.num_nodes > 0
        assert adj_result.num_edges > 0

        # Compute attributes
        attrs = compute_graph_attributes(gdf, adj_result.edges, verbose=True)
        assert attrs.rho > 0
        assert attrs.population.sum() > 0

        # Build network and solve
        g = build_flow_network(attrs, adj_result.edges, lambda_param=0.5, mu=0.001)
        flow = g.maxflow()

        partition = get_partition(g, adj_result.num_nodes)
        selected_pop = attrs.population[partition].sum()
        total_pop = attrs.population.sum()

        print(f"\nDC test results:")
        print(f"  Tracts: {adj_result.num_nodes}")
        print(f"  Edges: {adj_result.num_edges}")
        print(f"  Rho: {attrs.rho:.1f} m")
        print(f"  Selected: {partition.sum()} tracts ({100*partition.sum()/len(partition):.1f}%)")
        print(f"  Population: {selected_pop:,} / {total_pop:,} ({100*selected_pop/total_pop:.1f}%)")
```

### Success Criteria:

#### Automated Verification:
- [x] Integration test passes: `uv run pytest tests/test_graph/test_integration.py -v -m integration`
- [x] Full test suite passes: `uv run pytest -v`

#### Manual Verification:
- [x] Review integration test output for reasonable values
- [x] Verify DC has ~179 tracts with expected adjacency structure

**Implementation Note**: After completing this phase and all automated verification passes, the Phase 2 implementation is complete.

---

## Testing Strategy

### Unit Tests:
- Adjacency construction with mock grid data
- Boundary length calculation accuracy
- Flow network capacity assignment
- Partition extraction

### Integration Tests:
- Full pipeline with DC (smallest state, ~179 tracts)
- Cache read/write roundtrip

### Manual Testing Steps:
1. Run `load_all_tracts()` followed by `load_graph_data()` with real data
2. Verify cache file is created and reasonable size (~100-200 MB)
3. Run `get_graph_summary()` and verify statistics match expectations:
   - ~73,000 nodes
   - ~400,000-500,000 edges
   - Mean neighbors ~6
   - ρ ~2-5 km

## Performance Considerations

- **Adjacency construction**: Expected 30 seconds to 2 minutes for 73k tracts
- **Boundary calculation**: Expected 1-5 minutes (vectorized Shapely operations)
- **Cache**: Pickle format chosen for simplicity; graph data ~100-200 MB
- **Memory**: Peak usage during boundary calculation ~2-4 GB

## References

- Research document: `thoughts/shared/research/2025-11-21-phase2-graph-construction.md`
- Phase 1 plan: `thoughts/shared/plans/2025-11-20-phase1-data-pipeline.md`
- Methodology: `METHODOLOGY.md`
- Roadmap: `ROADMAP.md`
