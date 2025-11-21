---
date: 2025-11-21T12:00:00-05:00
researcher: Claude
git_commit: f359d1184d9dd0588a38e4b1247b53dc6e7c66dd
branch: master
repository: half_america
topic: "Phase 2: Graph Construction Implementation"
tags: [research, codebase, phase2, graph-construction, libpysal, pymaxflow, adjacency]
status: complete
last_updated: 2025-11-21
last_updated_by: Claude
---

# Research: Phase 2 Graph Construction

**Date**: 2025-11-21T12:00:00-05:00
**Researcher**: Claude
**Git Commit**: f359d1184d9dd0588a38e4b1247b53dc6e7c66dd
**Branch**: master
**Repository**: half_america

## Research Question

How should Phase 2 (Graph Construction) be implemented for the Half of America project? What libraries, patterns, and data structures are needed to build the spatial adjacency graph from Census Tract data?

## Summary

Phase 2 requires building a spatial adjacency graph from ~73,000 Census Tracts with the following components:
1. **Tract-level attributes**: Population (p_i), Area (a_i), shared boundary lengths (l_ij)
2. **Adjacency graph**: Using libpysal Queen/Rook contiguity
3. **Characteristic length scale**: ρ = median(√a_i) for dimensionless normalization
4. **s-t flow network structure**: For PyMaxFlow optimization in Phase 3

The existing Phase 1 pipeline provides a GeoDataFrame with `population`, `area_sqm`, and cleaned geometries in EPSG:5070 (meters). Phase 2 builds on this foundation.

## Detailed Findings

### 1. Existing Data Pipeline (Phase 1 Foundation)

The Phase 1 implementation provides all necessary inputs for graph construction:

**Key Files:**
- `src/half_america/data/pipeline.py:48-96` - `load_all_tracts()` main entry point
- `src/half_america/data/cleaning.py:113-180` - Geometry cleaning pipeline

**GeoDataFrame Schema After Loading:**

| Column | Type | Source | Purpose in Phase 2 |
|--------|------|--------|-------------------|
| `GEOID` | str | TIGER | Tract identifier |
| `geometry` | Polygon | TIGER | Adjacency detection, boundary calculation |
| `population` | int | Census API | p_i for population reward |
| `area_sqm` | float | Computed | a_i for area cost |

**CRS**: EPSG:5070 (NAD83 / Conus Albers Equal Area) - meters-based, suitable for length calculations.

### 2. Adjacency Graph Construction with libpysal

**Library**: libpysal (already in uv.lock but not yet used)

**Recommended Approach**: Use `Queen.from_dataframe()` for adjacency (polygons sharing any vertex are neighbors).

```python
from libpysal.weights import Queen, attach_islands

def build_adjacency_graph(gdf: gpd.GeoDataFrame) -> tuple:
    """Build Queen contiguity adjacency graph."""
    # Use integer indices for faster lookup with PyMaxFlow
    w = Queen.from_dataframe(gdf, use_index=False)

    # Handle islands (tracts with no neighbors)
    if w.islands:
        w = attach_islands(w, gdf)

    # Extract unique edge pairs (i < j)
    edges = []
    for i, neighbors in w.neighbors.items():
        for j in neighbors:
            if i < j:
                edges.append((i, j))

    return w, edges
```

**Performance Expectations** for 73,000 tracts:
- Construction time: 30 seconds to 2 minutes
- Average neighbors per tract: ~6
- Total edges: ~400,000-500,000

**Key Attributes:**
- `w.neighbors` - Dict of {tract_id: [neighbor_ids]}
- `w.islands` - List of isolated tracts
- `w.n_components` - Number of connected components
- `w.sparse` - Scipy sparse matrix representation

### 3. Shared Boundary Length Calculation

For n-links, we need the shared boundary length (l_ij) between adjacent tracts:

```python
from shapely import intersection, length

def compute_boundary_lengths(gdf: gpd.GeoDataFrame, w) -> dict:
    """Compute shared boundary lengths for all neighbor pairs."""
    boundaries = gdf.geometry.boundary.values

    edge_lengths = {}
    for i, neighbors in w.neighbors.items():
        for j in neighbors:
            if i < j:
                shared = intersection(boundaries[i], boundaries[j])
                l_ij = length(shared)
                edge_lengths[(i, j)] = l_ij
                edge_lengths[(j, i)] = l_ij  # Symmetric

    return edge_lengths
```

**Vectorized Approach** (faster for large datasets):
```python
def compute_boundary_lengths_vectorized(gdf, edges):
    """Vectorized boundary length computation."""
    boundaries = gdf.geometry.boundary.values
    i_idx = np.array([e[0] for e in edges])
    j_idx = np.array([e[1] for e in edges])

    shared = intersection(boundaries[i_idx], boundaries[j_idx])
    lengths = length(shared)

    return dict(zip(edges, lengths))
```

### 4. Characteristic Length Scale (ρ)

Per METHODOLOGY.md Section 2.1, normalize using:

```python
import numpy as np

def compute_rho(gdf: gpd.GeoDataFrame) -> float:
    """Compute characteristic length scale for normalization."""
    # ρ = median(√a_i)
    sqrt_areas = np.sqrt(gdf['area_sqm'].values)
    rho = np.median(sqrt_areas)
    return rho
```

### 5. s-t Flow Network Structure (for Phase 3)

Using PyMaxFlow (C++ wrapper for fast graph cuts):

```python
import maxflow
import numpy as np

def build_flow_network(
    num_tracts: int,
    edges: list,           # List of (i, j) pairs
    edge_lengths: dict,    # {(i, j): l_ij in meters}
    population: np.ndarray,
    area: np.ndarray,
    rho: float,
    lambda_param: float,
    mu: float
) -> maxflow.Graph:
    """Construct s-t flow network for graph cut optimization."""

    g = maxflow.Graph[float](num_tracts, len(edges))
    g.add_nodes(num_tracts)

    # Terminal edges (t-links)
    for i in range(num_tracts):
        source_cap = mu * population[i]           # Population reward
        sink_cap = (1 - lambda_param) * area[i]   # Area cost
        g.add_tedge(i, source_cap, sink_cap)

    # Neighborhood edges (n-links)
    for (i, j) in edges:
        l_ij = edge_lengths[(i, j)]
        capacity = lambda_param * l_ij / rho      # Boundary cost (normalized)
        g.add_edge(i, j, capacity, capacity)      # Symmetric

    return g
```

**Capacity Interpretation:**
- **Source capacity (t-link from S)**: Reward for including tract in "half"
- **Sink capacity (t-link to T)**: Cost for including tract (area penalty)
- **Edge capacity (n-link)**: Cost of cutting boundary (perimeter penalty)

### 6. Complete Phase 2 Module Structure

Recommended organization following Phase 1 patterns:

```
src/half_america/
├── graph/
│   ├── __init__.py          # Public API exports
│   ├── adjacency.py         # libpysal adjacency graph
│   ├── boundary.py          # Shared boundary calculations
│   ├── attributes.py        # Tract-level attributes (p_i, a_i, rho)
│   └── network.py           # s-t flow network construction
```

**Suggested Function Signatures:**

```python
# adjacency.py
def build_adjacency(gdf: gpd.GeoDataFrame) -> tuple[W, list[tuple[int, int]]]:
    """Build Queen contiguity graph. Returns (weights, edge_list)."""

# boundary.py
def compute_boundary_lengths(
    gdf: gpd.GeoDataFrame,
    edges: list[tuple[int, int]]
) -> dict[tuple[int, int], float]:
    """Compute shared boundary lengths for all edges."""

# attributes.py
def compute_tract_attributes(gdf: gpd.GeoDataFrame) -> TractAttributes:
    """Compute p_i, a_i, and rho from GeoDataFrame."""

# network.py
def build_network(
    attributes: TractAttributes,
    edges: list[tuple[int, int]],
    boundary_lengths: dict,
    lambda_param: float,
    mu: float
) -> maxflow.Graph:
    """Construct s-t flow network for graph cut."""
```

## Code References

### Phase 1 Data Pipeline
- `src/half_america/data/pipeline.py:14-46` - `load_state_tracts()` single state loading
- `src/half_america/data/pipeline.py:48-96` - `load_all_tracts()` main entry point
- `src/half_america/data/cleaning.py:113-180` - `clean_census_tracts()` geometry cleaning
- `src/half_america/data/cleaning.py:106-110` - `add_area_column()` adds `area_sqm`
- `src/half_america/config.py:14-19` - Cache directory constants
- `src/half_america/config.py:25-26` - Year constants (TIGER_YEAR, ACS_YEAR)

### Constants and Configuration
- `src/half_america/data/constants.py` - TARGET_CRS = "EPSG:5070"

## Architecture Insights

### Patterns to Follow (from Phase 1)
1. **Module Organization**: Separate files per concern, public API in `__init__.py`
2. **Caching**: GeoParquet format, `force_download` parameter to bypass
3. **Return Types**: Use `NamedTuple` for structured returns with stats
4. **Verbose Mode**: Include `verbose: bool = True` for progress messages
5. **Testing**: Fixtures in `conftest.py`, separate unit and integration tests

### Key Design Decisions

1. **Integer Indexing**: Use `use_index=False` with libpysal for integer indices (0 to n-1) compatible with PyMaxFlow node IDs.

2. **CRS Already Correct**: Phase 1 outputs EPSG:5070 (meters), no reprojection needed.

3. **Data Available**: `population` and `area_sqm` columns already exist from Phase 1.

4. **Island Handling**: Use `attach_islands()` to connect isolated tracts to nearest neighbors.

## Historical Context (from thoughts/)

No dedicated Phase 2 documents exist yet. Phase 1 documents reference:
- `thoughts/shared/plans/2025-11-20-phase1-data-pipeline.md` - Notes Phase 2 will use libpysal
- `thoughts/shared/research/2025-11-20-phase1-data-pipeline.md` - Notes area_sqm is "for Phase 2 graph construction"

## Related Research

- `thoughts/shared/research/2025-11-20-phase1-data-pipeline.md` - Phase 1 data pipeline research

## Open Questions

1. **Queen vs Rook Contiguity**: Queen includes corner-touching neighbors (shared vertex), Rook only edge-sharing. For boundary lengths, corner-only neighbors have l_ij ≈ 0. Decision: Use Queen for completeness, filter edges with l_ij = 0 if needed.

2. **Caching Strategy**: Should the adjacency graph and boundary lengths be cached? For 73k tracts, computation takes 1-2 minutes. Recommendation: Cache to `data/cache/processed/graph_{TIGER_YEAR}.parquet`.

3. **Normalization Units**: Should boundary lengths be in meters or kilometers? Recommendation: Keep meters (consistent with area_sqm), apply rho normalization for dimensionless capacities.

4. **Zero-Population Tracts**: Phase 1 fills missing population with 0. These tracts (water areas) should still participate in the graph for boundary connectivity. Verify behavior during testing.

---

## Appendix: ROADMAP Phase 2 Milestones

From `ROADMAP.md:29-44`:

- [ ] Compute tract-level attributes:
  - Population (p_i) ✅ Already in Phase 1 output
  - Land Area (a_i) ✅ Already in Phase 1 output as `area_sqm`
  - Shared boundary lengths with neighbors (l_ij)
- [ ] Build adjacency graph using libpysal (Queen contiguity)
- [ ] Calculate characteristic length scale ρ = median(√a_i)
- [ ] Construct s-t flow network structure:
  - n-links (neighborhood edges): capacity = λ × l_ij / ρ
  - t-links (terminal edges to source/sink)
- [ ] Unit tests for graph construction
