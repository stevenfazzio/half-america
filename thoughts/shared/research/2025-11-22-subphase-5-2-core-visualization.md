---
date: 2025-11-22T21:30:00-05:00
researcher: Claude
git_commit: 6f1491a3a88a650c03e6fa703f6dd49e794acb3a
branch: master
repository: half-america
topic: "Sub-Phase 5.2: Core Visualization Implementation Research"
tags: [research, codebase, phase-5, web-frontend, maplibre, deck-gl, react, topojson, visualization]
status: complete
last_updated: 2025-11-22
last_updated_by: Claude
---

# Research: Sub-Phase 5.2 - Core Visualization

**Date**: 2025-11-22T21:30:00-05:00
**Researcher**: Claude
**Git Commit**: 6f1491a3a88a650c03e6fa703f6dd49e794acb3a
**Branch**: master
**Repository**: half-america

## Research Question

What are the implementation patterns and best practices for Sub-Phase 5.2: Core Visualization, which includes:
1. Integrating MapLibre GL JS basemap via react-map-gl
2. Adding deck.gl with MapboxOverlay in interleaved mode
3. Implementing TopoJSON → GeoJSON conversion via topojson-client
4. Creating GeoJsonLayer for census tract polygons
5. Adding loading state/skeleton during initial data fetch
6. Implementing λ slider control for surface tension parameter
7. Pre-loading layers for each λ value with visibility toggling

## Summary

Sub-Phase 5.2 builds on the existing React + Vite scaffold with all required dependencies already installed. The implementation follows established patterns from deck.gl and react-map-gl documentation.

**Key Implementation Decisions:**

| Component | Recommendation |
|-----------|----------------|
| Map import | `react-map-gl/maplibre` (not `@vis.gl/react-maplibre`) |
| Basemap | CARTO Positron (no API key required) |
| deck.gl integration | `MapboxOverlay` with `interleaved: true` |
| Layer type | `GeoJsonLayer` from `@deck.gl/layers` |
| TopoJSON conversion | `topojson-client` with `feature()` function |
| Slider interaction | Pre-load all 10 layers, toggle `visible` prop |
| Loading state | Discriminated union pattern with progress tracking |

**Estimated Complexity:** Medium - all dependencies installed, patterns well-documented.

## Detailed Findings

### 1. MapLibre GL JS Integration via react-map-gl

**Current State:** Dependencies installed in `web/package.json`:
- `maplibre-gl@^5.13.0`
- `react-map-gl@^8.1.0`

**Import Pattern:**
```tsx
import { Map } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';
```

**Configuration:**
```tsx
const CARTO_STYLE = 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json';

const INITIAL_VIEW_STATE = {
  longitude: -98.5795,  // Geographic center of contiguous US
  latitude: 39.8283,
  zoom: 3.5,
  pitch: 0,
  bearing: 0
};

<Map
  initialViewState={INITIAL_VIEW_STATE}
  style={{ width: '100%', height: '100vh' }}
  mapStyle={CARTO_STYLE}
/>
```

**Key Points:**
- No API key required for MapLibre + CARTO basemaps
- CSS import is essential for proper control rendering
- Alternative basemaps: Dark Matter, Voyager (all free from CARTO)

### 2. deck.gl MapboxOverlay with Interleaved Mode

**Pattern:** Create a `DeckGLOverlay` component using react-map-gl's `useControl` hook:

```tsx
// components/DeckGLOverlay.tsx
import { useControl } from 'react-map-gl/maplibre';
import { MapboxOverlay } from '@deck.gl/mapbox';
import type { MapboxOverlayProps } from '@deck.gl/mapbox';

export function DeckGLOverlay(props: MapboxOverlayProps) {
  const overlay = useControl<MapboxOverlay>(() => new MapboxOverlay(props));
  overlay.setProps(props);
  return null;
}
```

**Usage:**
```tsx
<Map mapStyle={CARTO_STYLE}>
  <DeckGLOverlay layers={layers} interleaved />
</Map>
```

**Benefits of Interleaved Mode:**
- deck.gl layers share WebGL context with MapLibre
- Enables `beforeId` prop for layer ordering (render under labels)
- Better visual integration with basemap

### 3. TopoJSON → GeoJSON Conversion

**Current State:** TopoJSON files exist in `web/public/data/`:
- 10 individual files: `lambda_0.0.json` through `lambda_0.9.json`
- 1 combined file: `combined.json` (~1MB)

**Conversion Pattern:**
```tsx
import * as topojson from 'topojson-client';
import type { Topology } from 'topojson-specification';
import type { FeatureCollection } from 'geojson';

interface HalfAmericaTopology extends Topology {
  objects: {
    selected: topojson.GeometryObject;
  };
}

async function loadTopoJSON(url: string): Promise<FeatureCollection> {
  const response = await fetch(url);
  const topology = await response.json() as HalfAmericaTopology;
  return topojson.feature(topology, topology.objects.selected) as FeatureCollection;
}
```

**Object Name:** The Python export uses `"selected"` as the object key.

### 4. GeoJsonLayer for Census Tract Polygons

**Layer Configuration:**
```tsx
import { GeoJsonLayer } from '@deck.gl/layers';

new GeoJsonLayer({
  id: 'half-america-regions',
  data: geojsonData,

  // Rendering
  filled: true,
  stroked: true,

  // Styling
  getFillColor: [255, 100, 100, 180],  // Semi-transparent red
  getLineColor: [255, 255, 255, 255],   // White outline
  getLineWidth: 1,
  lineWidthMinPixels: 1,

  // Interaction
  pickable: true,
  autoHighlight: true,
  highlightColor: [255, 200, 0, 128],

  // Layer ordering (render under map labels)
  beforeId: 'label',  // Adjust based on CARTO style layer IDs
})
```

**Finding First Label Layer:**
```tsx
const onMapLoad = useCallback((event: { target: maplibregl.Map }) => {
  const map = event.target;
  const symbolLayer = map.getStyle().layers?.find(
    (layer) => layer.type === 'symbol'
  );
  if (symbolLayer) {
    setLabelLayerId(symbolLayer.id);
  }
}, []);
```

### 5. Loading State Implementation

**Recommended Pattern:** Discriminated union with useReducer for type-safe state management.

**State Types:**
```tsx
type LoaderState =
  | { status: 'idle' }
  | { status: 'loading'; loaded: number; total: number }
  | { status: 'error'; error: Error }
  | { status: 'success'; data: Map<number, FeatureCollection> };
```

**Loading Strategy:** Use `Promise.allSettled` for parallel loading with graceful error handling:

```tsx
const loadPromises = LAMBDA_VALUES.map(async (lambda) => {
  const response = await fetch(getTopoJsonPath(lambda));
  const topology = await response.json();
  const geojson = topojson.feature(topology, topology.objects.selected);
  return { lambda, geojson };
});

const results = await Promise.allSettled(loadPromises);
```

**Loading Skeleton:** Show progress during initial load:
- Display "Loading TopoJSON data... X/10 files"
- Progress bar with percentage
- Error state with retry button

### 6. Lambda Slider Component

**Implementation Approach:** Use HTML `<input type="range">` with discrete steps mapped to lambda values.

**Key Features:**
- 10 discrete steps (0.0 to 0.9)
- Modern CSS styling with blur glass effect
- Full accessibility (aria-labels, keyboard support)
- Positioned as map overlay

**Component Structure:**
```tsx
interface LambdaSliderProps {
  value: LambdaValue;
  onChange: (value: LambdaValue) => void;
  disabled?: boolean;
}

// Map step index (0-9) to lambda values
const stepIndex = LAMBDA_VALUES.indexOf(value);

<input
  type="range"
  min={0}
  max={LAMBDA_VALUES.length - 1}
  step={1}
  value={stepIndex}
  onChange={(e) => {
    const index = parseInt(e.target.value, 10);
    onChange(LAMBDA_VALUES[index]);
  }}
/>
```

### 7. Pre-loading and Visibility Toggling

**Critical Pattern:** Use the `visible` prop, NOT conditional rendering. This preserves GPU buffers for instant switching.

```tsx
// CORRECT: All layers always in array, visibility toggled
const layers = LAMBDA_VALUES.map((lambda) =>
  new GeoJsonLayer({
    id: `layer-${lambda.toFixed(1)}`,
    data: dataCache.get(lambda),
    visible: lambda === currentLambda,  // Only one visible at a time
    // ... other props
  })
);

// INCORRECT: Conditional rendering causes layer recreation
// {currentLambda === 0.5 && new GeoJsonLayer({ ... })}
```

**Memory Considerations:**
- 10 TopoJSON files: ~2.3MB total
- GPU buffers: ~2-4x JSON size per layer
- Total estimated memory: ~50-100MB (acceptable for modern browsers)

**Pre-loading Strategy:**
1. Load all 10 files in parallel on component mount
2. Convert TopoJSON → GeoJSON and cache in state
3. Create all 10 layers with `visible: false` except current
4. On slider change, update `visible` props (instant response)

## Code References

- `web/package.json:12-21` - Installed dependencies
- `web/src/types/lambda.ts:1-20` - Lambda type definitions and path helpers
- `web/src/App.tsx:1-30` - Current placeholder implementation
- `web/public/data/` - Pre-computed TopoJSON files

## Architecture Insights

**Component Structure for Sub-Phase 5.2:**

```
web/src/
├── App.tsx                 # Main app with state management
├── components/
│   ├── DeckGLOverlay.tsx   # deck.gl + react-map-gl integration
│   ├── LambdaSlider.tsx    # Surface tension slider control
│   ├── LambdaSlider.css    # Slider styling
│   ├── MapSkeleton.tsx     # Loading state skeleton
│   └── LoadingError.tsx    # Error display with retry
├── hooks/
│   ├── useTopoJsonLoader.ts # Data loading state machine
│   └── useLambdaLayers.ts  # Layer management with visibility
└── types/
    └── lambda.ts           # Existing - lambda type definitions
```

**Data Flow:**

```
┌─────────────────────────────────────────────────────────┐
│                       App.tsx                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ useTopoJson  │  │ useLambda    │  │ useState     │  │
│  │ Loader       │→ │ Layers       │← │ (lambda)     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         ↓                 ↓                 ↑          │
│  ┌──────────────────────────────────────────────────┐  │
│  │                    <Map>                          │  │
│  │  ┌──────────────────────────────────────────────┐│  │
│  │  │ <DeckGLOverlay layers={layers} interleaved />││  │
│  │  └──────────────────────────────────────────────┘│  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │ LambdaSlider │  │ MapSkeleton  │ (when loading)     │
│  └──────────────┘  └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
```

## Historical Context (from thoughts/)

- `thoughts/shared/research/2025-11-22-deck-gl-feasibility.md` - deck.gl integration patterns, performance considerations
- `thoughts/shared/research/2025-11-22-maplibre-vs-mapbox.md` - MapLibre selection rationale, CARTO basemap recommendation

## Related Research

- [thoughts/shared/research/2025-11-22-deck-gl-feasibility.md](thoughts/shared/research/2025-11-22-deck-gl-feasibility.md)
- [thoughts/shared/research/2025-11-22-maplibre-vs-mapbox.md](thoughts/shared/research/2025-11-22-maplibre-vs-mapbox.md)

## Implementation Checklist

Based on ROADMAP.md Sub-Phase 5.2 tasks:

| Task | Status | Notes |
|------|--------|-------|
| Integrate MapLibre GL JS basemap via react-map-gl | Ready | Use `react-map-gl/maplibre`, CARTO Positron |
| Add deck.gl with MapboxOverlay in interleaved mode | Ready | `DeckGLOverlay` component pattern |
| Implement TopoJSON → GeoJSON conversion | Ready | `topojson-client` feature() |
| Create GeoJsonLayer for census tract polygons | Ready | Standard GeoJsonLayer config |
| Add loading state/skeleton during initial data fetch | Ready | Discriminated union + skeleton |
| Implement λ slider control | Ready | Range input with discrete steps |
| Pre-load layers for each λ value with visibility toggling | Ready | visible prop toggling |

## Open Questions

1. **Color scheme:** What fill color should be used for the selected regions? Current suggestion: semi-transparent orange-red `[255, 100, 100, 180]`

2. **Basemap style:** Positron (light) or Dark Matter (dark)? Light basemaps typically work better for choropleth-style visualizations.

3. **Tooltip content:** Should hovering show region statistics? Properties available: `lambda`, `population_selected`, `tract_count`

4. **Mobile responsiveness:** Should the slider be repositioned on mobile screens?

5. **Combined vs individual files:** Load individual TopoJSON files (~200-350KB each) or the combined file (~1MB)? Individual files enable progress tracking.
