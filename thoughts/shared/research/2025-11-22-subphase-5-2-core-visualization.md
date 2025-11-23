---
date: 2025-11-22T21:30:00-05:00
researcher: Claude
git_commit: 6f1491a3a88a650c03e6fa703f6dd49e794acb3a
branch: master
repository: half-america
topic: "Sub-Phase 5.2: Core Visualization Implementation Research"
tags: [research, codebase, phase-5, web-frontend, maplibre, deck-gl, react, topojson, visualization, color-scheme, basemap, tooltips, mobile, data-loading]
status: complete
last_updated: 2025-11-22
last_updated_by: Claude
last_updated_note: "Deep dive on 100-file loading: chunked files recommended over combined"
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

## Open Questions - Analysis and Recommendations

### 1. Color Scheme for Selected Regions

**Question:** What fill color should be used for the selected regions?

#### Options Analysis

| Option | Pros | Cons |
|--------|------|------|
| **Cool Blue (#0072B2)** | Maximally colorblind accessible; professional/trustworthy; doesn't imply value judgment; cool colors "recede" and layer well | May not grab attention as strongly as warm colors |
| **Teal/Cyan (#009E73)** | Fresh, modern; distinctive; good basemap contrast | Less traditional for geographic visualization |
| **Warm Orange (#E69F00)** | Eye-catching; creates urgency; colorblind-safe with blue | May imply warning/danger; can feel aggressive |
| **Semi-transparent Red** | High attention; "hot spot" aesthetic | Red-green colorblind issues; implies negative connotation |

#### Transparency Considerations
- **40-60% opacity** is the research consensus ("50% sweet spot")
- Semi-transparent preserves basemap context (roads, cities visible through overlay)
- **White outlines** (100% opacity) create clean separation and help polygons "pop"

#### Recommendation: **Deep Blue with White Outline**

```javascript
getFillColor: [0, 114, 178, 153]     // Okabe-Ito Blue at 60% opacity
getLineColor: [255, 255, 255, 230]   // White at 90% opacity
lineWidthMinPixels: 1.5
```

**Rationale:**
1. Blue is maximally colorblind accessible (works for 100% of viewers)
2. 60% opacity preserves geographic context while clearly marking selected regions
3. White outline creates clean separation on any basemap
4. Professional appearance appropriate for portfolio piece
5. Does not imply value judgment (unlike red=danger or green=good)

---

### 2. Basemap Style (Light vs Dark)

**Question:** Should we use Positron (light) or Dark Matter (dark) basemap?

#### Options Analysis

| Factor | Positron (Light) | Dark Matter (Dark) |
|--------|------------------|-------------------|
| **Best for** | Text-heavy maps, point data | Polygon/line data, dashboards |
| **Visual effect** | Professional, informative | Eye-catching, dramatic |
| **Readability** | Better text/label legibility | Reduced eye strain in low-light |
| **Accessibility** | Easier to meet WCAG | Higher contrast requirements |
| **Color approach** | Dark fill = higher values | Light fill = higher values |

#### CARTO Recommendation
CARTO explicitly states: "Positron is good for point data" while "Dark Matter is good for polygon/line data."

#### Recommendation: **Dark Matter (with light mode toggle)**

**Primary:** Start with Dark Matter for visual impact:
- Your primary visualization is polygon-based (CARTO recommends dark for polygons)
- Portfolio piece benefits from dramatic effect
- "Where 50% of Americans live" narrative is more compelling with glowing regions against darkness
- deck.gl examples commonly use dark basemaps

**Secondary:** Consider adding a light/dark toggle:
- Some users prefer light mode for accessibility or personal preference
- Allows detailed exploration with better label readability

**Color adjustment for dark basemap:**
- Use bright, saturated fill colors (blue/teal/orange will "glow")
- White or light-colored outlines for visibility

---

### 3. Tooltip Content

**Question:** Should hovering show region statistics?

#### Options Analysis

| Approach | Pros | Cons |
|----------|------|------|
| **Rich tooltips** | Progressive disclosure; expected UX pattern | Distracting with ~73,000 potential targets; doesn't work on mobile |
| **Minimal tooltips** | Location context only | Still creates "flickery" experience |
| **No tooltips** | Clean, focused; better mobile experience | May feel unresponsive |
| **Fixed panel** | Always accessible; works on mobile; shows aggregate stats | Takes screen space |

#### Key Insight
The interesting properties (`lambda`, `population_selected`, `tract_count`) describe the **entire selection**, not individual tracts. These belong in a fixed panel, not per-tract tooltips.

#### Recommendation: **Fixed Summary Panel + Hover Highlight (No Text Tooltip)**

**Implementation:**
1. **Fixed Summary Panel** (always visible, top-left or bottom-left):
   ```
   Selected Areas: [tract_count] tracts
   Population: [population_selected] (50.0%)
   Surface Tension: λ = [lambda]
   ```

2. **Hover highlight** (visual feedback only):
   ```javascript
   pickable: true,
   autoHighlight: true,
   highlightColor: [255, 255, 255, 100]  // Subtle white highlight
   // No getTooltip - let visual highlight speak
   ```

**Rationale:**
- Focus on the overall pattern, not individual parts
- 73,000 tracts = tooltip noise; hover constantly firing
- Aggregate statistics belong in fixed panel (accessible on mobile)
- Visual highlight confirms interactivity without text overhead

---

### 4. Mobile Responsiveness

**Question:** Should the slider be repositioned on mobile screens?

#### Placement Options Analysis

| Pattern | Pros | Cons |
|---------|------|------|
| **Bottom-right overlay** | Thumb-zone accessible; Google Maps pattern; always visible | Can conflict with map gestures |
| **Bottom sheet** | Scalable for more controls; familiar pattern | Heavy for single slider; complex implementation |
| **Top position** | Doesn't conflict with bottom nav | Hard to reach one-handed; violates mobile-first principles |
| **Full-width bottom** | Natural swipe direction; maximizes precision | Takes significant space |

#### Touch Target Requirements
- Apple minimum: **44x44 pt**
- Android minimum: **48x48 dp**
- At least 8px spacing between interactive elements

#### Recommendation: **Floating Bottom-Right Overlay with Responsive Sizing**

**Desktop (>768px):**
- Position: bottom-left or top-left corner
- Orientation: horizontal
- Width: ~280px fixed

**Mobile (<768px):**
- Position: bottom area (above MapLibre attribution)
- Full-width minus padding (16px on each side)
- Slider thumb: minimum 48x48px touch target
- Semi-transparent background panel for visibility

**CSS Implementation:**
```css
.slider-control {
  position: fixed;
  bottom: 80px;
  right: 16px;
  left: 16px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  z-index: 1;
}

@media (min-width: 768px) {
  .slider-control {
    bottom: auto;
    top: 16px;
    left: 16px;
    right: auto;
    width: 280px;
  }
}
```

**Touch enhancements:**
- `touch-action: none` on slider to prevent scroll conflicts
- Show lambda value prominently during drag

---

### 5. Combined vs Individual Files

**Question:** Load individual TopoJSON files or the combined file?

#### Options Analysis

| Factor | Individual Files (10 × 200-350KB) | Combined File (~1MB) |
|--------|-----------------------------------|---------------------|
| **Compression** | ~500-700KB total (worse) | ~200-300KB (better, ~2x smaller) |
| **Lazy loading** | Yes - load only what user selects | No - must download all |
| **Caching** | Granular - update one without invalidating others | All-or-nothing invalidation |
| **Progress UX** | "Loading 3/10..." (more informative) | Single progress bar |
| **HTTP/2** | Parallel downloads work well | Single request |
| **Fault tolerance** | One failure doesn't block others | All-or-nothing |

#### Key Consideration
Most users likely won't explore all 10 lambda values. If average user tries 2-3 values, lazy loading means 400-1000KB instead of full 1MB (compressed).

#### Recommendation: **Individual Files with Lazy Loading + Preloading**

**Strategy:**
1. Load default lambda (0.5) immediately on page load
2. Preload adjacent values (0.4, 0.6) in background after initial render
3. Load others on-demand as user explores via slider

**Implementation:**
```javascript
// Load default immediately
const defaultData = await loadTopoJSON(0.5);

// After initial render, preload neighbors
useEffect(() => {
  prefetch(getTopoJsonPath(0.4));
  prefetch(getTopoJsonPath(0.6));
}, []);

// On slider change, load if not cached
async function onLambdaChange(lambda: LambdaValue) {
  if (!cache.has(lambda)) {
    cache.set(lambda, await loadTopoJSON(lambda));
  }
  setCurrentLambda(lambda);
}
```

**Rationale (for current 10-file setup):**
- 10 files is well under HTTP/2's "50 files per page" threshold
- Lazy loading savings outweigh compression penalty for typical usage
- Users see results faster (wait for one file, not all)
- Better progress tracking UX
- Individual files enable preloading strategy

#### Future Consideration: 100 Lambda Values

Per ROADMAP.md, a future milestone plans to increase lambda granularity to 0.01 increments (100 values) for smooth animations. This changes the calculus significantly:

| Factor | 10 Files (Current) | 100 Files (Future) |
|--------|-------------------|-------------------|
| HTTP/2 threshold | Well under 50 | At/above 50 threshold |
| Server overhead | Minimal | Significant (100 file reads) |
| Compression benefit | ~2x worse than combined | ~5-10x worse than combined |
| Lazy loading value | High (users try 2-3) | Lower (animation needs many) |

#### Deep Dive: Combined File vs Chunked Files for 100 Lambda Values

##### Critical Finding: No TopoJSON Arc Sharing Benefit

TopoJSON's arc sharing only works for **exactly matching coordinate sequences**. Since different lambda values produce different polygon boundaries (the whole point of the optimization), there is **zero arc sharing** between lambda values. This means:

- Combined file size ≈ sum of individual file sizes
- The compression benefit of combined files is **only** from gzip/brotli dictionary sharing, not topology
- Estimated savings: ~10-20% smaller combined vs sum of individuals (gzip benefit only)

##### JSON Parsing Performance Considerations

| File Size | Parse Time (Desktop) | Parse Time (Mobile) | UI Impact |
|-----------|---------------------|---------------------|-----------|
| 500KB-1MB | 15-30ms | 50-100ms | Imperceptible |
| 2-3MB | 60-100ms | 200-300ms | Noticeable |
| 5-10MB | 150-300ms | 500-1000ms | **Blocks UI** |

**Key threshold:** UI jank becomes perceptible at ~50ms blocking. A single 5-10MB combined file would block the main thread for 150-300ms on desktop.

##### Animation Use Case Analysis

Per ROADMAP.md, the 100-file phase is for "smooth animations". This favors chunked loading:

1. **Animation can start before all data loads** - show first frames immediately
2. **Scrubber UX** - if user drags to λ=0.5, only need that chunk loaded
3. **Preloading works naturally** - load current chunk, prefetch adjacent chunks in background

##### Options Comparison

| Factor | Combined File | Chunked Files (10 × 10) |
|--------|---------------|------------------------|
| **File size** | ~5-10MB (all 100 values) | ~500KB-1MB per chunk |
| **Parse time** | 150-300ms (blocks UI) | 15-30ms per chunk (safe) |
| **Time to first frame** | Must wait for full download + parse | First chunk only (~100-200ms) |
| **HTTP requests** | 1 | 10 (well under HTTP/2 threshold) |
| **Compression** | Best (~10-20% smaller) | Good |
| **Animation start** | Delayed until all loaded | Immediate with first chunk |
| **Memory** | All 100 values in RAM | Can evict unused chunks |
| **Caching** | All-or-nothing | Granular per chunk |
| **Implementation** | Simpler | Moderate complexity |

##### Web Worker Consideration

Moving JSON parsing to a Web Worker keeps UI responsive but doesn't change the fundamental tradeoffs:
- Combined file: Worker parses 150-300ms, then ~100-200ms structured clone overhead to return
- Chunked: Each chunk parses fast, progressive rendering possible

**Web Workers are recommended regardless of approach** for files >1MB.

##### Recommendation: **Chunked Files**

For the 100-lambda animation use case, **chunked files (10 files × 10 values)** is the better approach.

**Rationale:**
1. **No TopoJSON arc sharing** - combined file offers only ~10-20% size reduction, not the dramatic savings that shared topology would provide
2. **Animation UX** - users can see the map and start interacting after loading just the first chunk (100-200ms) vs waiting for full download (1-3 seconds)
3. **Parse time under jank threshold** - each 500KB-1MB chunk parses in ~30ms, avoiding UI blocking
4. **Natural preloading** - load current chunk, prefetch ±1 chunks in background
5. **HTTP/2 efficient** - 10 parallel requests is well under the recommended maximum
6. **Better caching** - changing one lambda range only invalidates one chunk

**Implementation pattern:**
```javascript
// Chunk naming: lambda_00-09.json, lambda_10-19.json, etc.
function getChunkForLambda(lambda: number): string {
  const chunkStart = Math.floor(lambda * 10) * 10;
  return `/data/lambda_${chunkStart.toString().padStart(2, '0')}-${(chunkStart + 9).toString().padStart(2, '0')}.json`;
}

// Progressive loading for animation
async function loadForAnimation(startLambda: number) {
  // Load starting chunk immediately
  const startChunk = await loadChunk(startLambda);
  renderFrame(startLambda, startChunk);

  // Prefetch adjacent chunks in background
  prefetchChunk(startLambda + 0.1);
  prefetchChunk(startLambda - 0.1);
}
```

**When to reconsider combined file:**
- If analytics show users always watch full animation start-to-finish
- If server doesn't support HTTP/2
- If implementation simplicity is paramount and UX tradeoff is acceptable
