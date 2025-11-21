# Roadmap

This document outlines the implementation plan for Half of America.

## Current Status

**Phase 2: Graph Construction** is complete. The project can build spatial adjacency graphs using Queen contiguity, compute shared boundary lengths, and construct s-t flow networks ready for optimization.

---

## Phase 1: Data Pipeline

Build the data acquisition and preprocessing pipeline.

### Milestones

- [x] Add production dependencies to `pyproject.toml` (geopandas, shapely, cenpy, pandas)
- [x] Download TIGER/Line Shapefiles for Census Tract geometries (contiguous US)
- [x] Fetch ACS 5-Year population estimates via Census API
- [x] Implement geometry cleaning:
  - Quantize coordinates to integer grid (`shapely.set_precision`)
  - Fix self-intersections via `shapely.make_valid()`
  - Eliminate micro-gaps/slivers between tracts
- [x] Create data caching layer to avoid repeated API calls
- [x] Unit tests for data pipeline

---

## Phase 2: Graph Construction

Build the spatial adjacency graph from Census Tract data.

### Milestones

- [x] Compute tract-level attributes:
  - Population (p_i)
  - Land Area (a_i)
  - Shared boundary lengths with neighbors (l_ij)
- [x] Build adjacency graph using libpysal (Queen contiguity)
- [x] Calculate characteristic length scale ρ = median(√a_i)
- [x] Construct s-t flow network structure:
  - n-links (neighborhood edges): capacity = λ × l_ij / ρ
  - t-links (terminal edges to source/sink)
- [x] Unit tests for graph construction

---

## Phase 3: Optimization Engine

Implement the Max-Flow Min-Cut solver with constraint tuning.

### Milestones

- [x] Add PyMaxFlow dependency (done in Phase 2)
- [x] Implement graph-cut solver wrapper
- [x] Implement binary search for Lagrange multiplier (μ) to hit 50% population target
- [x] Build outer loop for λ parameter sweep (0.0 → 1.0)
- [x] Pre-compute results for discrete λ values (e.g., 0.0, 0.1, 0.2, ..., 1.0)
- [x] Add CLI `precompute` command
- [x] Performance benchmarking infrastructure (pytest-benchmark suite)
- [ ] Performance optimization (based on benchmark analysis)
- [ ] Unit tests for optimization correctness

---

## Phase 4: Post-Processing

Transform optimization output into web-ready geometries.

### Milestones

- [ ] Dissolve selected tracts into MultiPolygon geometries (shapely.ops.unary_union)
- [ ] Filter out small disconnected islands (artifact removal)
- [ ] Apply Visvalingam-Whyatt simplification for web performance
- [ ] Export as TopoJSON
- [ ] Generate pre-computed geometry files for all λ values
- [ ] Validate output geometries

---

## Phase 5: Web Frontend

Build the interactive visualization.

### Milestones

- [ ] Add CLI `export` subcommand for TopoJSON output
- [ ] Set up React application
- [ ] Integrate Mapbox GL JS for map rendering
- [ ] Implement λ slider control for surface tension parameter
- [ ] Load and display pre-computed TopoJSON geometries
- [ ] Add smooth transitions between λ values
- [ ] Style and polish UI
- [ ] Deploy static site

---

## Future Enhancements

Ideas for future development:

- **Historical comparisons**: Show how the 50% boundary has shifted over census periods
- **Custom thresholds**: Allow users to select different population percentages (25%, 75%, etc.)
- **State-level views**: Run optimization within individual states
- **Alternative metrics**: Optimize for other variables (income, housing, etc.)
- **Real-time computation**: WebAssembly port for client-side optimization
- **Animation**: Animate the λ sweep from dusty (λ=0) to smooth (λ=1)
- **Fine λ granularity**: Support 0.01 increments (101 values) for smooth animations
