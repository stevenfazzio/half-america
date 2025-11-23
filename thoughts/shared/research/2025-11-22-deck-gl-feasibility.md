---
date: 2025-11-22T12:00:00-05:00
researcher: Claude
git_commit: 2a30aa9b98687a205fd1c86247715eff9597e551
branch: master
repository: stevenfazzio/half-america
topic: "deck.gl Feasibility for Half of America Web Frontend"
tags: [research, codebase, deck.gl, mapbox, visualization, web-frontend, phase-5]
status: complete
last_updated: 2025-11-22
last_updated_by: Claude
---

# Research: deck.gl Feasibility for Half of America Web Frontend

> **Update (2025-11-22):** This research was conducted with Mapbox GL JS in mind. We have since decided to use **MapLibre GL JS** instead. All patterns and recommendations in this document apply equally to MapLibre - the `@deck.gl/mapbox` module works with both libraries, and `react-map-gl` supports both via `/mapbox` and `/maplibre` imports. See `thoughts/shared/research/2025-11-22-maplibre-vs-mapbox.md` for the comparison.

**Date**: 2025-11-22
**Researcher**: Claude
**Git Commit**: 2a30aa9b98687a205fd1c86247715eff9597e551
**Branch**: master
**Repository**: stevenfazzio/half-america

## Research Question

Is deck.gl feasible for the Half of America web frontend? Does it make sense given the project's goals? Would it replace Mapbox GL JS or work alongside it?

## Summary

**Yes, deck.gl is feasible and makes sense for this project.** It would work **alongside** Mapbox GL JS (not replace it), with Mapbox providing the basemap and deck.gl rendering the data visualization layers.

**Recommendation**: Use deck.gl + Mapbox GL JS together. This is a well-established pattern used by Uber and many data visualization applications.

### Key Findings

| Question | Answer |
|----------|--------|
| Is deck.gl feasible? | Yes - 30,000+ polygons is well within its performance envelope |
| Replace or augment Mapbox? | **Augment** - deck.gl renders on top of Mapbox basemap |
| TopoJSON support? | Indirect - convert to GeoJSON via `topojson-client` |
| Smooth slider transitions? | Not for polygon morphing, but instant swap or opacity fade works |
| React integration? | First-class support via `@deck.gl/react` |

## Detailed Findings

### 1. What is deck.gl?

deck.gl is an open-source, WebGL2/WebGPU-powered visualization framework originally developed by Uber, now maintained by the vis.gl community (OpenJS Foundation). It specializes in large-scale geospatial data visualization.

**Core Strengths:**
- GPU-accelerated rendering: up to 1M data points at 60 FPS
- Reactive architecture designed for React
- Basemap agnostic: works with Mapbox, MapLibre, Google Maps, or standalone
- Rich layer types: GeoJsonLayer, PolygonLayer, ScatterplotLayer, etc.
- Built-in transition support for animating layer properties

### 2. deck.gl vs Mapbox GL JS

| Aspect | deck.gl | Mapbox GL JS |
|--------|---------|--------------|
| Primary Focus | Data visualization | Cartographic mapping |
| Large Datasets | Optimized for millions of points | Excellent with vector tiles |
| Polygon Rendering | GeoJsonLayer with GPU acceleration | fill/fill-extrusion layers |
| Transitions | Built-in property transitions | Limited to camera transitions |
| 3D Support | Native extrusion, point clouds | fill-extrusion, terrain |

**For this project's use case** (~73,000 census tract polygons with dynamic updates), deck.gl is better suited because:
1. Handles frequent property updates more efficiently via GPU
2. Built-in transition support between layer states
3. Designed for "data visualization" vs "cartographic mapping"

### 3. Integration Pattern: deck.gl + Mapbox Together

deck.gl is designed to work **WITH** Mapbox GL JS, not replace it. This is one of its core design principles.

**Integration Modes:**

| Mode | Description | Best For |
|------|-------------|----------|
| Interleaved | deck.gl renders into Mapbox's WebGL2 context | Layer mixing, 3D occlusion |
| Overlaid | deck.gl renders in separate canvas over Mapbox | 2D visualizations |
| Reverse-Controlled | deck.gl manages interactions, Mapbox as child | Custom interaction handling |

**Recommended Pattern (Interleaved with React):**

```tsx
import {Map, useControl} from 'react-map-gl/mapbox';
import {MapboxOverlay} from '@deck.gl/mapbox';
import {GeoJsonLayer} from '@deck.gl/layers';

function DeckGLOverlay(props) {
  const overlay = useControl(() => new MapboxOverlay(props));
  overlay.setProps(props);
  return null;
}

function App() {
  const layers = [
    new GeoJsonLayer({
      id: 'census-tracts',
      data: geojsonData,
      getFillColor: d => d.properties.selected ? [255, 100, 100] : [200, 200, 200],
      beforeId: 'waterway-label'  // Render under Mapbox labels
    })
  ];

  return (
    <Map
      initialViewState={{longitude: -98, latitude: 39, zoom: 4}}
      mapStyle="mapbox://styles/mapbox/light-v11"
      mapboxAccessToken={MAPBOX_TOKEN}
    >
      <DeckGLOverlay layers={layers} interleaved />
    </Map>
  );
}
```

**Benefits:**
- Layer interleaving: deck.gl layers can render between Mapbox layers (e.g., polygons below labels)
- Synchronized camera: MapView syncs with Mapbox at every zoom/rotation
- Use Mapbox controls: NavigationControl, GeolocateControl work seamlessly
- Best of both: Mapbox provides beautiful basemaps; deck.gl handles data visualization

### 4. TopoJSON Support

**deck.gl does NOT natively support TopoJSON.** You must convert to GeoJSON first.

```javascript
import * as topojson from 'topojson-client';

// Load TopoJSON
const topoData = await fetch('/data/lambda_0.5.topojson').then(r => r.json());

// Convert to GeoJSON
const geojsonData = topojson.feature(topoData, topoData.objects.selected);

// Use with GeoJsonLayer
const layer = new GeoJsonLayer({
  id: 'selected-tracts',
  data: geojsonData,
  // ...
});
```

This is the standard approach and adds minimal overhead.

### 5. Performance for 30,000+ Polygons

**Expected Performance: Good (60 FPS achievable)**

Based on research:
- deck.gl benchmarks show 60 FPS up to ~1M data items on 2015 MacBook Pro hardware
- "Low thousands should not have a visible overhead"
- 30,000 polygons is well within acceptable range

**Potential Bottlenecks:**
- Polygon vertex complexity (total vertex count matters more than polygon count)
- Buffer regeneration when switching datasets (100-500ms if not pre-loaded)
- Triangulation for complex polygons (can block main thread)

**Optimization Strategies:**
1. Use `_normalize: false` for pre-validated data
2. Pre-load layers with `visible: false` for instant toggling
3. Consider GeoArrow format for maximum performance
4. Use Douglas-Peucker simplification (already implemented in Phase 4)

### 6. Lambda Slider Transitions

**Important Limitation:** Smooth polygon morphing between lambda values is NOT practical because:
- Polygon counts differ between lambda values
- Vertex indices don't match between datasets
- deck.gl transitions interpolate per-vertex by array index

**Recommended Approaches:**

**Option A - Pre-loaded layers (for ≤10 lambda values):**
```javascript
// Pre-load all layers
const layers = lambdaValues.map(lambda =>
  new GeoJsonLayer({
    id: `tracts-${lambda}`,
    data: geojsonByLambda[lambda],
    visible: lambda === currentLambda,
    // ...
  })
);

// Toggle visibility on slider change (instant, no buffer regeneration)
```

**Option B - Dynamic loading (for >10 lambda values):**
```javascript
// Load/unload as slider moves
// Use opacity fade for visual smoothness
new GeoJsonLayer({
  id: 'tracts',
  data: currentGeojson,
  opacity: 1,
  transitions: {
    opacity: 300  // Fade transition
  }
})
```

### 7. React Integration

deck.gl has first-class React support:

```tsx
import {DeckGL} from '@deck.gl/react';
import {GeoJsonLayer} from '@deck.gl/layers';

function App() {
  const [lambda, setLambda] = useState(0.5);

  const layers = [
    new GeoJsonLayer({
      id: 'tracts',
      data: geojsonByLambda[lambda],
      getFillColor: [255, 140, 0, 180],
      updateTriggers: {
        data: lambda  // Re-render when lambda changes
      }
    })
  ];

  return (
    <>
      <DeckGL
        initialViewState={{longitude: -98, latitude: 39, zoom: 4}}
        controller
        layers={layers}
      >
        <Map mapStyle="mapbox://styles/mapbox/light-v11" />
      </DeckGL>
      <LambdaSlider value={lambda} onChange={setLambda} />
    </>
  );
}
```

## Comparison with Current Plan

The current ROADMAP.md specifies:
- React + Vite
- Mapbox GL JS
- GitHub Pages hosting

**Impact of Adding deck.gl:**

| Aspect | Without deck.gl | With deck.gl |
|--------|----------------|--------------|
| Dependencies | `mapbox-gl`, `react-map-gl` | Add `@deck.gl/core`, `@deck.gl/react`, `@deck.gl/mapbox`, `@deck.gl/layers` |
| Bundle Size | Smaller | Larger (+~200KB gzipped) |
| Learning Curve | Lower | Moderate |
| Polygon Rendering | Mapbox fill layers | deck.gl GeoJsonLayer |
| Transition Support | Manual or none | Built-in |
| Future Flexibility | Limited | High (3D, animations, etc.) |

## Architecture Insights

Using deck.gl follows the pattern established by Uber and other data visualization applications:

1. **Mapbox** provides the basemap (roads, labels, terrain)
2. **deck.gl** provides the data visualization layer (census tract polygons)
3. **react-map-gl** wraps Mapbox for React integration
4. **@deck.gl/mapbox** provides the integration layer

This separation of concerns is cleaner than trying to do everything in Mapbox's style specification.

## Recommendation

**Yes, use deck.gl alongside Mapbox GL JS.**

**Rationale:**
1. The project's core goal is data visualization (showing population concentration), not cartographic mapping
2. deck.gl is purpose-built for this use case
3. ~30,000 polygons is well within deck.gl's performance envelope
4. Built-in transition support (even if limited) is better than none
5. Future enhancements (3D extrusion, animations) become easier
6. This is a well-established pattern with good documentation

**Updated Technology Stack:**
- Framework: React + Vite (unchanged)
- Basemap: Mapbox GL JS via react-map-gl
- Data Visualization: deck.gl (`@deck.gl/react`, `@deck.gl/mapbox`, `@deck.gl/layers`)
- TopoJSON Parsing: `topojson-client`
- Hosting: GitHub Pages (unchanged)

**Implementation Approach:**
1. Use MapboxOverlay in interleaved mode
2. Convert TopoJSON to GeoJSON at load time
3. Pre-load layers for each lambda value (if ≤10 values)
4. Use visibility toggling for instant slider response
5. Consider opacity fade transitions for visual polish

## Code References

- [`ROADMAP.md:84-119`](https://github.com/stevenfazzio/half-america/blob/2a30aa9b98687a205fd1c86247715eff9597e551/ROADMAP.md#L84-L119) - Phase 5 Web Frontend specification
- [`METHODOLOGY.md:96-102`](https://github.com/stevenfazzio/half-america/blob/2a30aa9b98687a205fd1c86247715eff9597e551/METHODOLOGY.md#L96-L102) - Implementation stack reference

## Historical Context (from thoughts/)

- `thoughts/shared/research/2025-11-22-github-pages-hosting.md` - GitHub Pages hosting research (covers React + Vite + Mapbox configuration)
- `thoughts/shared/research/2025-11-22-topojson-export.md` - TopoJSON export research (WGS84 coordinate system for web compatibility)
- `thoughts/shared/research/2025-11-22-visvalingam-whyatt-simplification.md` - Geometry simplification for web performance

**Notable:** No existing research mentioned deck.gl prior to this document.

## Related Research

- [thoughts/shared/research/2025-11-22-github-pages-hosting.md](thoughts/shared/research/2025-11-22-github-pages-hosting.md)

## Open Questions

1. **Bundle size impact** - What is the actual bundle size increase from adding deck.gl?
2. **Mobile performance** - How does deck.gl perform on mobile devices with 30,000 polygons?
3. **Lambda granularity** - If we support 101 lambda values (0.00 to 1.00), is pre-loading all layers feasible?
4. **Pre-triangulation** - Can we pre-triangulate polygons during Python export to avoid main-thread blocking?

## Sources

- [deck.gl GitHub Repository](https://github.com/visgl/deck.gl)
- [deck.gl Official Documentation](https://deck.gl/docs)
- [deck.gl Using with Mapbox](https://deck.gl/docs/developer-guide/base-maps/using-with-mapbox)
- [deck.gl GeoJsonLayer](https://deck.gl/docs/api-reference/layers/geojson-layer)
- [deck.gl Performance Optimization](https://deck.gl/docs/developer-guide/performance)
- [deck.gl Animations and Transitions](https://deck.gl/docs/developer-guide/animations-and-transitions)
- [deck.gl and Mapbox: Better Together](https://medium.com/vis-gl/deckgl-and-mapbox-better-together-47b29d6d4fb1)
- [Mapbox Blog - Custom Layers with Uber](https://blog.mapbox.com/launching-custom-layers-with-uber-2a235841a125)
- [Beyond Vector Tiles: Mapbox, MapLibre or DeckGL](https://geomatico.es/en/vector-tiles-mapbox-maplibre-or-deckgl-for-my-3d-map/)
- [GeoArrow deck.gl-layers](https://github.com/geoarrow/deck.gl-layers)
