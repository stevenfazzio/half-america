# Roadmap

This document outlines the implementation plan for Half of America.

## Current Status

**Phase 6: Final Touches** is in progress. The site is live at https://stevenfazzio.github.io/half-america

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
- [x] Performance optimization (based on benchmark analysis)
  - Benchmarks show ~10-15s for full sweep (acceptable for pre-computation)
  - Primary bottleneck is PyMaxFlow C++ solver (not optimizable from Python)
  - Micro-optimizations deferred as unnecessary
- [x] Unit tests for optimization correctness

---

## Phase 4: Post-Processing

Transform optimization output into web-ready geometries.

### Milestones

- [x] Dissolve selected tracts into MultiPolygon geometries (shapely.ops.unary_union)
- [x] Apply Douglas-Peucker simplification for web performance
- [x] Export as TopoJSON
- [x] Add CLI `export` command for TopoJSON output
- [x] Generate pre-computed geometry files for all λ values
- [x] Add `population_selected` to DissolveResult and TopoJSON metadata

---

## Phase 5: Web Frontend

Build the interactive visualization and deploy to GitHub Pages.

### Technology Stack

- **Framework**: React + Vite
- **Basemap**: MapLibre GL JS (via react-map-gl) with CARTO basemaps
- **Data Visualization**: deck.gl (@deck.gl/react, @deck.gl/mapbox, @deck.gl/layers)
- **TopoJSON Parsing**: topojson-client
- **Hosting**: GitHub Pages (static site)
- **CI/CD**: GitHub Actions

deck.gl renders the census tract polygons as a visualization layer on top of MapLibre's basemap. This separation provides better performance for large polygon datasets and built-in transition support. See [thoughts/shared/research/2025-11-22-deck-gl-feasibility.md](thoughts/shared/research/2025-11-22-deck-gl-feasibility.md) for detailed research.

### Project Structure

```
web/                        # Frontend application
├── public/
│   └── data/               # Pre-computed TopoJSON files
├── src/
│   ├── components/
│   │   ├── Map.tsx
│   │   └── LambdaSlider.tsx
│   └── App.tsx
├── vite.config.ts          # base: '/half-america/'
└── package.json
```

### Sub-Phase 5.1: Project Setup

- [x] Set up React + Vite application in `web/` directory
- [x] Configure Vite with `base: '/half-america/'` for GitHub Pages
- [x] Copy TopoJSON files to `web/public/data/`
- [ ] Configure GitHub Pages source to "GitHub Actions" in repository settings (deferred to Sub-Phase 5.3)

### Sub-Phase 5.2: Core Visualization

- [x] Integrate MapLibre GL JS basemap via react-map-gl
- [x] Add deck.gl with MapboxOverlay in interleaved mode
- [x] Implement TopoJSON → GeoJSON conversion via topojson-client
- [x] Create GeoJsonLayer for census tract polygons
- [x] Add loading state/skeleton during initial data fetch
- [x] Implement λ slider control for surface tension parameter
- [x] Pre-load layers for each λ value with visibility toggling (instant slider response)

### Sub-Phase 5.3: Deployment

- [x] Set up GitHub Actions workflow (`working-directory: ./web`)
- [x] Deploy to GitHub Pages (`stevenfazzio.github.io/half-america`)

---

## Phase 6: Final Touches

Polish for initial release

### Milestones

- [x] Fine λ granularity: Move to 0.01 increments (99 values, 0.00-0.98) for smoother slider interaction
- [x] Create tab structure with Map, Story, and Method stubs (see [docs/tab_strategy.md](docs/tab_strategy.md))
  - Hash-based routing (`#map`, `#story`, `#method`)
  - Responsive navigation (top pills desktop, bottom nav mobile)
  - WebGL state preserved across tab switches via KeepMounted pattern
- [x] Add content to Story tab (narrative explanation for general audience)
  - Key statistics, evolution story, slider explanation
  - Navigation links to Map and Method tabs
  - Image placeholder for evolution diagram
- [ ] Create evolution diagram images for Story tab (San Bernardino → Tracts → Bridges → Smooth)
- [x] Add content to Method tab (technical methodology)
  - KaTeX math rendering with prominent objective function
  - Variable definitions, algorithm details, data sources, post-processing
  - Implementation stack and navigation links
- [x] Add map title overlay ("Half of America / Where 50% of Americans live") for first-glance clarity
- [x] Add slider endpoint labels ("Fragmented" ← → "Compact") to encourage exploration
- [ ] Redesign legend: prominently display population %, reorder metrics, improve formatting
- [x] Add tab bar glassmorphism container (backdrop-filter blur) for desktop visibility

---

## Future Enhancements

Ideas for future development:

- **Hover tooltips**: Add per-region statistics on hover (requires exporting per-region data instead of aggregate MultiPolygon)
- **Light/dark mode toggle**: Allow users to switch between Positron (light) and Dark Matter (dark) basemaps
- **Variable region granularity**: Support other region types (e.g. state, county)
- **Alternative metrics**: Optimize for other variables (e.g. number of regions instead of perimeter)
- **Custom thresholds**: Allow users to select different population percentages (25%, 75%, etc.)
- **State-level views**: Run optimization within individual states
- **Real-time computation**: WebAssembly port for client-side optimization
- **Animation**: Animate the λ sweep from dusty (λ=0) to smooth (λ=1)
