# Sub-Phase 5.2: Core Visualization Implementation Plan

## Overview

Implement the core interactive map visualization for Half of America, including MapLibre basemap, deck.gl polygon overlay, lambda slider control, and loading states. This transforms the placeholder React app into a functional data visualization.

## Current State Analysis

**What exists:**
- React + Vite scaffold in `web/` directory
- All dependencies installed (maplibre-gl, react-map-gl, @deck.gl/*, topojson-client)
- 10 TopoJSON files in `web/public/data/` (lambda_0.0.json through lambda_0.9.json)
- Lambda type definitions in `web/src/types/lambda.ts`
- Placeholder App.tsx listing available data files

**What's missing:**
- MapLibre basemap integration
- deck.gl layer rendering
- TopoJSON → GeoJSON conversion
- Lambda slider control
- Loading states
- Summary panel

### Key Discoveries:
- `web/src/types/lambda.ts:5` - LAMBDA_VALUES array and getTopoJsonPath helper already exist
- `web/package.json:12-21` - All required dependencies installed
- TopoJSON files use `"selected_region"` as the object key
- TopoJSON properties: `lambda_value`, `population_selected`, `area_sqm`, `num_parts`

## Desired End State

A fully functional interactive map where:
1. User sees a Dark Matter basemap centered on the contiguous US
2. Census tract polygons are rendered as a semi-transparent blue overlay
3. A lambda slider allows switching between 10 pre-computed optimizations
4. Layer switching is instant (all layers pre-loaded, visibility toggled)
5. A fixed summary panel shows: population %, region count, λ value
6. Loading state shows progress during initial data fetch
7. Mobile-responsive layout with proper touch targets

### Verification:
- `npm run build` succeeds without errors
- `npm run dev` shows interactive map at localhost:5173
- Slider changes visualization instantly (no loading delay after initial load)
- Summary panel updates when lambda changes
- Works on mobile viewport (responsive slider positioning)

## What We're NOT Doing

- Light/dark mode toggle (deferred to Future Enhancements)
- Text tooltips on hover (only visual highlight)
- Animation between lambda values
- Combined file loading (using individual files with lazy loading)
- 100-value lambda granularity (Phase 6)

## Implementation Approach

Build incrementally with visual verification at each phase:
1. Get basemap rendering first
2. Add deck.gl integration
3. Load and display a single lambda value
4. Add slider and multi-layer support
5. Add loading states and summary panel
6. Polish responsive behavior

## Phase 1: MapLibre Basemap Integration

### Overview
Get the MapLibre basemap rendering with CARTO Dark Matter style.

### Changes Required:

#### 1. Create DeckGLOverlay Component
**File**: `web/src/components/DeckGLOverlay.tsx`

```tsx
import { useControl } from 'react-map-gl/maplibre';
import { MapboxOverlay } from '@deck.gl/mapbox';
import type { MapboxOverlayProps } from '@deck.gl/mapbox';

export function DeckGLOverlay(props: MapboxOverlayProps) {
  const overlay = useControl<MapboxOverlay>(() => new MapboxOverlay(props));
  overlay.setProps(props);
  return null;
}
```

#### 2. Update App.tsx with Basic Map
**File**: `web/src/App.tsx`

Replace placeholder content with:

```tsx
import { Map } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';
import { DeckGLOverlay } from './components/DeckGLOverlay';
import './App.css';

const CARTO_DARK_MATTER = 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json';

const INITIAL_VIEW_STATE = {
  longitude: -98.5795,
  latitude: 39.8283,
  zoom: 3.5,
  pitch: 0,
  bearing: 0,
};

function App() {
  return (
    <div className="app">
      <Map
        initialViewState={INITIAL_VIEW_STATE}
        style={{ width: '100%', height: '100vh' }}
        mapStyle={CARTO_DARK_MATTER}
      >
        <DeckGLOverlay layers={[]} interleaved />
      </Map>
    </div>
  );
}

export default App;
```

#### 3. Update App.css
**File**: `web/src/App.css`

Replace with minimal styles:

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.app {
  width: 100%;
  height: 100vh;
}
```

### Success Criteria:

#### Automated Verification:
- [x] TypeScript compiles: `cd web && npm run build`
- [x] No ESLint errors: `cd web && npm run lint`

#### Manual Verification:
- [ ] `npm run dev` shows Dark Matter basemap
- [ ] Map is pannable and zoomable
- [ ] Map fills entire viewport

---

## Phase 2: TopoJSON Loading and GeoJsonLayer

### Overview
Load a single TopoJSON file, convert to GeoJSON, and render with deck.gl GeoJsonLayer.

### Changes Required:

#### 1. Create TopoJSON Loader Hook
**File**: `web/src/hooks/useTopoJsonLoader.ts`

```tsx
import { useState, useEffect, useCallback } from 'react';
import * as topojson from 'topojson-client';
import type { Topology, GeometryCollection } from 'topojson-specification';
import type { FeatureCollection, Geometry } from 'geojson';
import { LAMBDA_VALUES, LambdaValue, getTopoJsonPath } from '../types/lambda';

interface HalfAmericaProperties {
  lambda_value: number;
  population_selected: number;
  area_sqm: number;
  num_parts: number;
}

interface HalfAmericaTopology extends Topology<{
  selected_region: GeometryCollection<HalfAmericaProperties>;
}> {}

export type LoaderState =
  | { status: 'idle' }
  | { status: 'loading'; loaded: number; total: number }
  | { status: 'error'; error: Error }
  | { status: 'success'; data: Map<LambdaValue, FeatureCollection<Geometry, HalfAmericaProperties>> };

async function loadSingleTopoJSON(lambda: LambdaValue): Promise<FeatureCollection<Geometry, HalfAmericaProperties>> {
  const response = await fetch(getTopoJsonPath(lambda));
  if (!response.ok) {
    throw new Error(`Failed to load lambda_${lambda.toFixed(1)}.json: ${response.status}`);
  }
  const topology = await response.json() as HalfAmericaTopology;
  return topojson.feature(topology, topology.objects.selected_region) as FeatureCollection<Geometry, HalfAmericaProperties>;
}

export function useTopoJsonLoader() {
  const [state, setState] = useState<LoaderState>({ status: 'idle' });

  const load = useCallback(async () => {
    setState({ status: 'loading', loaded: 0, total: LAMBDA_VALUES.length });

    const dataMap = new Map<LambdaValue, FeatureCollection<Geometry, HalfAmericaProperties>>();

    try {
      // Load all files in parallel
      const results = await Promise.all(
        LAMBDA_VALUES.map(async (lambda) => {
          const geojson = await loadSingleTopoJSON(lambda);
          return { lambda, geojson };
        })
      );

      for (const { lambda, geojson } of results) {
        dataMap.set(lambda, geojson);
      }

      setState({ status: 'success', data: dataMap });
    } catch (err) {
      setState({ status: 'error', error: err instanceof Error ? err : new Error(String(err)) });
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const retry = useCallback(() => {
    load();
  }, [load]);

  return { state, retry };
}
```

#### 2. Update App.tsx to Use Loader and Render Layer
**File**: `web/src/App.tsx`

```tsx
import { useState, useMemo, useCallback } from 'react';
import { Map } from 'react-map-gl/maplibre';
import { GeoJsonLayer } from '@deck.gl/layers';
import type { PickingInfo } from '@deck.gl/core';
import 'maplibre-gl/dist/maplibre-gl.css';
import { DeckGLOverlay } from './components/DeckGLOverlay';
import { useTopoJsonLoader } from './hooks/useTopoJsonLoader';
import { LAMBDA_VALUES, LambdaValue } from './types/lambda';
import './App.css';

const CARTO_DARK_MATTER = 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json';

const INITIAL_VIEW_STATE = {
  longitude: -98.5795,
  latitude: 39.8283,
  zoom: 3.5,
  pitch: 0,
  bearing: 0,
};

// Okabe-Ito Blue at 60% opacity
const FILL_COLOR: [number, number, number, number] = [0, 114, 178, 153];
const LINE_COLOR: [number, number, number, number] = [255, 255, 255, 230];
const HIGHLIGHT_COLOR: [number, number, number, number] = [255, 255, 255, 100];

function App() {
  const { state } = useTopoJsonLoader();
  const [currentLambda, setCurrentLambda] = useState<LambdaValue>(0.5);

  const layers = useMemo(() => {
    if (state.status !== 'success') return [];

    return LAMBDA_VALUES.map((lambda) => {
      const data = state.data.get(lambda);
      return new GeoJsonLayer({
        id: `layer-${lambda.toFixed(1)}`,
        data,
        visible: lambda === currentLambda,
        filled: true,
        stroked: true,
        getFillColor: FILL_COLOR,
        getLineColor: LINE_COLOR,
        getLineWidth: 1,
        lineWidthMinPixels: 1,
        pickable: true,
        autoHighlight: true,
        highlightColor: HIGHLIGHT_COLOR,
      });
    });
  }, [state, currentLambda]);

  if (state.status === 'loading' || state.status === 'idle') {
    return (
      <div className="app loading">
        <p>Loading map data...</p>
      </div>
    );
  }

  if (state.status === 'error') {
    return (
      <div className="app error">
        <p>Error loading data: {state.error.message}</p>
      </div>
    );
  }

  return (
    <div className="app">
      <Map
        initialViewState={INITIAL_VIEW_STATE}
        style={{ width: '100%', height: '100vh' }}
        mapStyle={CARTO_DARK_MATTER}
      >
        <DeckGLOverlay layers={layers} interleaved />
      </Map>
    </div>
  );
}

export default App;
```

### Success Criteria:

#### Automated Verification:
- [x] TypeScript compiles: `cd web && npm run build`
- [x] No ESLint errors: `cd web && npm run lint`

#### Manual Verification:
- [ ] Loading state appears briefly on page load
- [ ] Blue polygons render on the map showing selected census tracts
- [ ] Polygons have white outline
- [ ] Hovering over polygons shows subtle highlight effect
- [ ] Map remains pannable/zoomable with polygons rendered

---

## Phase 3: Lambda Slider Control

### Overview
Add an interactive slider to switch between lambda values, with instant layer switching.

### Changes Required:

#### 1. Create LambdaSlider Component
**File**: `web/src/components/LambdaSlider.tsx`

```tsx
import { LAMBDA_VALUES, LambdaValue } from '../types/lambda';
import './LambdaSlider.css';

interface LambdaSliderProps {
  value: LambdaValue;
  onChange: (value: LambdaValue) => void;
  disabled?: boolean;
}

export function LambdaSlider({ value, onChange, disabled }: LambdaSliderProps) {
  const stepIndex = LAMBDA_VALUES.indexOf(value);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const index = parseInt(e.target.value, 10);
    onChange(LAMBDA_VALUES[index]);
  };

  return (
    <div className="lambda-slider">
      <label htmlFor="lambda-slider" className="lambda-label">
        Surface Tension (λ)
      </label>
      <div className="slider-container">
        <input
          id="lambda-slider"
          type="range"
          min={0}
          max={LAMBDA_VALUES.length - 1}
          step={1}
          value={stepIndex}
          onChange={handleChange}
          disabled={disabled}
          aria-valuemin={0}
          aria-valuemax={0.9}
          aria-valuenow={value}
          aria-valuetext={`Lambda ${value.toFixed(1)}`}
        />
        <span className="lambda-value">{value.toFixed(1)}</span>
      </div>
      <p className="lambda-hint">
        {value < 0.3 ? 'Minimizes area (more fragmented)' :
         value > 0.7 ? 'Minimizes perimeter (smoother shapes)' :
         'Balanced optimization'}
      </p>
    </div>
  );
}
```

#### 2. Create LambdaSlider Styles
**File**: `web/src/components/LambdaSlider.css`

```css
.lambda-slider {
  position: fixed;
  bottom: 80px;
  left: 16px;
  right: 16px;
  padding: 16px;
  background: rgba(30, 30, 30, 0.95);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  z-index: 1;
  color: #fff;
}

@media (min-width: 768px) {
  .lambda-slider {
    bottom: auto;
    top: 16px;
    left: 16px;
    right: auto;
    width: 280px;
  }
}

.lambda-label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
}

.slider-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.slider-container input[type="range"] {
  flex: 1;
  height: 8px;
  -webkit-appearance: none;
  appearance: none;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  cursor: pointer;
}

.slider-container input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 24px;
  height: 24px;
  background: #0072B2;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid #fff;
}

.slider-container input[type="range"]::-moz-range-thumb {
  width: 24px;
  height: 24px;
  background: #0072B2;
  border-radius: 50%;
  cursor: pointer;
  border: 2px solid #fff;
}

/* Larger touch target on mobile */
@media (max-width: 767px) {
  .slider-container input[type="range"]::-webkit-slider-thumb {
    width: 32px;
    height: 32px;
  }

  .slider-container input[type="range"]::-moz-range-thumb {
    width: 32px;
    height: 32px;
  }
}

.lambda-value {
  font-size: 18px;
  font-weight: 700;
  min-width: 36px;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.lambda-hint {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 8px;
  margin-bottom: 0;
}
```

#### 3. Update App.tsx to Include Slider
**File**: `web/src/App.tsx`

Add import and component:

```tsx
import { LambdaSlider } from './components/LambdaSlider';

// ... in the return statement, after <Map>...</Map>:
<LambdaSlider value={currentLambda} onChange={setCurrentLambda} />
```

### Success Criteria:

#### Automated Verification:
- [x] TypeScript compiles: `cd web && npm run build`
- [x] No ESLint errors: `cd web && npm run lint`

#### Manual Verification:
- [ ] Slider appears in top-left on desktop, bottom on mobile
- [ ] Dragging slider changes lambda value displayed
- [ ] Map polygons change instantly when slider moves (no loading delay)
- [ ] Slider hint text updates based on lambda value
- [ ] Touch target is large enough on mobile (test in device mode)

---

## Phase 4: Summary Panel

### Overview
Add a fixed panel showing aggregate statistics for the current lambda selection.

### Changes Required:

#### 1. Create SummaryPanel Component
**File**: `web/src/components/SummaryPanel.tsx`

```tsx
import type { FeatureCollection, Geometry } from 'geojson';
import './SummaryPanel.css';

interface HalfAmericaProperties {
  lambda_value: number;
  population_selected: number;
  area_sqm: number;
  num_parts: number;
}

interface SummaryPanelProps {
  data: FeatureCollection<Geometry, HalfAmericaProperties> | undefined;
  lambda: number;
}

// US population from 2022 ACS (same year as our data)
const US_TOTAL_POPULATION = 331_893_745;

export function SummaryPanel({ data, lambda }: SummaryPanelProps) {
  if (!data || data.features.length === 0) {
    return null;
  }

  // Get properties from first feature (all features share the same aggregate properties)
  const props = data.features[0].properties;
  const populationPercent = ((props.population_selected / US_TOTAL_POPULATION) * 100).toFixed(1);

  return (
    <div className="summary-panel">
      <h2 className="summary-title">Half of America</h2>
      <dl className="summary-stats">
        <div className="stat">
          <dt>Population</dt>
          <dd>{populationPercent}%</dd>
        </div>
        <div className="stat">
          <dt>Regions</dt>
          <dd>{props.num_parts.toLocaleString()}</dd>
        </div>
        <div className="stat">
          <dt>Lambda (λ)</dt>
          <dd>{lambda.toFixed(1)}</dd>
        </div>
      </dl>
    </div>
  );
}
```

#### 2. Create SummaryPanel Styles
**File**: `web/src/components/SummaryPanel.css`

```css
.summary-panel {
  position: fixed;
  top: 16px;
  right: 16px;
  padding: 16px;
  background: rgba(30, 30, 30, 0.95);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  z-index: 1;
  color: #fff;
  min-width: 160px;
}

@media (max-width: 767px) {
  .summary-panel {
    top: 16px;
    right: 16px;
    left: auto;
    padding: 12px;
    min-width: auto;
  }
}

.summary-title {
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.summary-stats {
  margin: 0;
  display: grid;
  gap: 8px;
}

.stat {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 16px;
}

.stat dt {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.stat dd {
  font-size: 14px;
  font-weight: 600;
  margin: 0;
  font-variant-numeric: tabular-nums;
}
```

#### 3. Update App.tsx to Include SummaryPanel
**File**: `web/src/App.tsx`

Add import and component:

```tsx
import { SummaryPanel } from './components/SummaryPanel';

// ... in the return statement, after <LambdaSlider ... />:
<SummaryPanel data={state.data.get(currentLambda)} lambda={currentLambda} />
```

### Success Criteria:

#### Automated Verification:
- [x] TypeScript compiles: `cd web && npm run build`
- [x] No ESLint errors: `cd web && npm run lint`

#### Manual Verification:
- [ ] Summary panel appears in top-right corner
- [ ] Shows population percentage (should be ~50%)
- [ ] Shows region count and lambda value
- [ ] Values update when slider is moved
- [ ] Panel is readable on mobile (appropriate sizing)

---

## Phase 5: Loading State Polish

### Overview
Improve loading and error states with better visual feedback.

### Changes Required:

#### 1. Create LoadingOverlay Component
**File**: `web/src/components/LoadingOverlay.tsx`

```tsx
import './LoadingOverlay.css';

interface LoadingOverlayProps {
  loaded: number;
  total: number;
}

export function LoadingOverlay({ loaded, total }: LoadingOverlayProps) {
  const percent = Math.round((loaded / total) * 100);

  return (
    <div className="loading-overlay">
      <div className="loading-content">
        <h1>Half of America</h1>
        <p>Loading map data...</p>
        <div className="progress-bar">
          <div className="progress-fill" style={{ width: `${percent}%` }} />
        </div>
        <p className="progress-text">{loaded} / {total} files</p>
      </div>
    </div>
  );
}
```

#### 2. Create LoadingOverlay Styles
**File**: `web/src/components/LoadingOverlay.css`

```css
.loading-overlay {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1a1a1a;
  color: #fff;
  z-index: 1000;
}

.loading-content {
  text-align: center;
  padding: 24px;
}

.loading-content h1 {
  font-size: 24px;
  margin: 0 0 16px 0;
}

.loading-content p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 16px 0;
}

.progress-bar {
  width: 200px;
  height: 4px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  overflow: hidden;
  margin: 0 auto 8px;
}

.progress-fill {
  height: 100%;
  background: #0072B2;
  transition: width 0.2s ease;
}

.progress-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
}
```

#### 3. Create ErrorOverlay Component
**File**: `web/src/components/ErrorOverlay.tsx`

```tsx
import './ErrorOverlay.css';

interface ErrorOverlayProps {
  message: string;
  onRetry: () => void;
}

export function ErrorOverlay({ message, onRetry }: ErrorOverlayProps) {
  return (
    <div className="error-overlay">
      <div className="error-content">
        <h1>Error Loading Data</h1>
        <p>{message}</p>
        <button onClick={onRetry} className="retry-button">
          Try Again
        </button>
      </div>
    </div>
  );
}
```

#### 4. Create ErrorOverlay Styles
**File**: `web/src/components/ErrorOverlay.css`

```css
.error-overlay {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1a1a1a;
  color: #fff;
  z-index: 1000;
}

.error-content {
  text-align: center;
  padding: 24px;
}

.error-content h1 {
  font-size: 24px;
  margin: 0 0 16px 0;
  color: #ff6b6b;
}

.error-content p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 24px 0;
  max-width: 300px;
}

.retry-button {
  padding: 12px 24px;
  background: #0072B2;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.retry-button:hover {
  background: #005a8c;
}
```

#### 5. Update useTopoJsonLoader for Progress Tracking
**File**: `web/src/hooks/useTopoJsonLoader.ts`

Update the load function to track progress:

```tsx
const load = useCallback(async () => {
  setState({ status: 'loading', loaded: 0, total: LAMBDA_VALUES.length });

  const dataMap = new Map<LambdaValue, FeatureCollection<Geometry, HalfAmericaProperties>>();
  let loadedCount = 0;

  try {
    // Load files sequentially to track progress
    for (const lambda of LAMBDA_VALUES) {
      const geojson = await loadSingleTopoJSON(lambda);
      dataMap.set(lambda, geojson);
      loadedCount++;
      setState({ status: 'loading', loaded: loadedCount, total: LAMBDA_VALUES.length });
    }

    setState({ status: 'success', data: dataMap });
  } catch (err) {
    setState({ status: 'error', error: err instanceof Error ? err : new Error(String(err)) });
  }
}, []);
```

#### 6. Update App.tsx to Use New Components
**File**: `web/src/App.tsx`

```tsx
import { LoadingOverlay } from './components/LoadingOverlay';
import { ErrorOverlay } from './components/ErrorOverlay';

// Replace the loading/error returns with:
if (state.status === 'loading') {
  return <LoadingOverlay loaded={state.loaded} total={state.total} />;
}

if (state.status === 'idle') {
  return <LoadingOverlay loaded={0} total={LAMBDA_VALUES.length} />;
}

if (state.status === 'error') {
  return <ErrorOverlay message={state.error.message} onRetry={retry} />;
}
```

### Success Criteria:

#### Automated Verification:
- [x] TypeScript compiles: `cd web && npm run build`
- [x] No ESLint errors: `cd web && npm run lint`

#### Manual Verification:
- [ ] Loading overlay shows with progress bar during initial load
- [ ] Progress updates as files load (shows X/10)
- [ ] Error overlay appears if network is disabled
- [ ] Retry button works when clicked

---

## Phase 6: Final Integration and Cleanup

### Overview
Final integration, code cleanup, and update ROADMAP.md.

### Changes Required:

#### 1. Final App.tsx (Complete File)
**File**: `web/src/App.tsx`

Ensure all pieces are integrated correctly:

```tsx
import { useState, useMemo } from 'react';
import { Map } from 'react-map-gl/maplibre';
import { GeoJsonLayer } from '@deck.gl/layers';
import 'maplibre-gl/dist/maplibre-gl.css';
import { DeckGLOverlay } from './components/DeckGLOverlay';
import { LambdaSlider } from './components/LambdaSlider';
import { SummaryPanel } from './components/SummaryPanel';
import { LoadingOverlay } from './components/LoadingOverlay';
import { ErrorOverlay } from './components/ErrorOverlay';
import { useTopoJsonLoader } from './hooks/useTopoJsonLoader';
import { LAMBDA_VALUES, LambdaValue } from './types/lambda';
import './App.css';

const CARTO_DARK_MATTER = 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json';

const INITIAL_VIEW_STATE = {
  longitude: -98.5795,
  latitude: 39.8283,
  zoom: 3.5,
  pitch: 0,
  bearing: 0,
};

const FILL_COLOR: [number, number, number, number] = [0, 114, 178, 153];
const LINE_COLOR: [number, number, number, number] = [255, 255, 255, 230];
const HIGHLIGHT_COLOR: [number, number, number, number] = [255, 255, 255, 100];

function App() {
  const { state, retry } = useTopoJsonLoader();
  const [currentLambda, setCurrentLambda] = useState<LambdaValue>(0.5);

  const layers = useMemo(() => {
    if (state.status !== 'success') return [];

    return LAMBDA_VALUES.map((lambda) => {
      const data = state.data.get(lambda);
      return new GeoJsonLayer({
        id: `layer-${lambda.toFixed(1)}`,
        data,
        visible: lambda === currentLambda,
        filled: true,
        stroked: true,
        getFillColor: FILL_COLOR,
        getLineColor: LINE_COLOR,
        getLineWidth: 1,
        lineWidthMinPixels: 1,
        pickable: true,
        autoHighlight: true,
        highlightColor: HIGHLIGHT_COLOR,
      });
    });
  }, [state, currentLambda]);

  if (state.status === 'loading') {
    return <LoadingOverlay loaded={state.loaded} total={state.total} />;
  }

  if (state.status === 'idle') {
    return <LoadingOverlay loaded={0} total={LAMBDA_VALUES.length} />;
  }

  if (state.status === 'error') {
    return <ErrorOverlay message={state.error.message} onRetry={retry} />;
  }

  return (
    <div className="app">
      <Map
        initialViewState={INITIAL_VIEW_STATE}
        style={{ width: '100%', height: '100vh' }}
        mapStyle={CARTO_DARK_MATTER}
      >
        <DeckGLOverlay layers={layers} interleaved />
      </Map>
      <LambdaSlider value={currentLambda} onChange={setCurrentLambda} />
      <SummaryPanel data={state.data.get(currentLambda)} lambda={currentLambda} />
    </div>
  );
}

export default App;
```

#### 2. Update ROADMAP.md
**File**: `ROADMAP.md`

Mark Sub-Phase 5.2 tasks as complete and add light/dark toggle to Future Enhancements:

```markdown
### Sub-Phase 5.2: Core Visualization

- [x] Integrate MapLibre GL JS basemap via react-map-gl
- [x] Add deck.gl with MapboxOverlay in interleaved mode
- [x] Implement TopoJSON → GeoJSON conversion via topojson-client
- [x] Create GeoJsonLayer for census tract polygons
- [x] Add loading state/skeleton during initial data fetch
- [x] Implement λ slider control for surface tension parameter
- [x] Pre-load layers for each λ value with visibility toggling (instant slider response)
```

Add to Future Enhancements:
```markdown
- **Light/dark mode toggle**: Allow users to switch between Positron (light) and Dark Matter (dark) basemaps
```

### Success Criteria:

#### Automated Verification:
- [x] TypeScript compiles: `cd web && npm run build`
- [x] No ESLint errors: `cd web && npm run lint`
- [x] Production build succeeds and runs: `cd web && npm run build && npm run preview`

#### Manual Verification:
- [x] Complete user flow works: loading → map → slider interaction
- [x] All components properly styled and positioned
- [x] Mobile responsive (test at 375px width)
- [x] No console errors or warnings
- [x] Summary panel shows accurate data
- [x] Slider provides instant feedback

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful.

---

## Phase 7: Individual Polygon Hover Highlighting

### Overview
Enable hover highlighting of individual disconnected regions rather than the entire MultiPolygon feature.

### Problem
The dissolved TopoJSON geometries store all selected regions as a single MultiPolygon feature. When hovering, deck.gl highlights the entire feature (all regions) rather than just the polygon under the cursor.

### Solution
Split MultiPolygon features into individual Polygon features client-side after loading. This allows deck.gl's `autoHighlight` to work on individual polygons.

### Changes Required:

#### 1. Add explodeMultiPolygons helper to useTopoJsonLoader
**File**: `web/src/hooks/useTopoJsonLoader.ts`

```typescript
function explodeMultiPolygons(
  fc: FeatureCollection<Geometry, HalfAmericaProperties>
): FeatureCollection<Geometry, HalfAmericaProperties> {
  const features: Feature<Geometry, HalfAmericaProperties>[] = [];
  for (const feature of fc.features) {
    if (feature.geometry.type === 'MultiPolygon') {
      for (const coordinates of feature.geometry.coordinates) {
        features.push({
          type: 'Feature',
          properties: feature.properties,
          geometry: { type: 'Polygon', coordinates },
        });
      }
    } else {
      features.push(feature);
    }
  }
  return { type: 'FeatureCollection', features };
}
```

#### 2. Apply explodeMultiPolygons after TopoJSON conversion
In `loadSingleTopoJSON`, wrap the return:

```typescript
const geojson = topojson.feature(...);
return explodeMultiPolygons(geojson);
```

### Performance Analysis
- Worst case (λ=0): ~2,779 individual polygon features
- Best case (λ=0.9): ~288 individual polygon features
- All 10 layers combined: ~15,000 features total
- Well within deck.gl's performance envelope (handles 100k+ features)

### Success Criteria:

#### Automated Verification:
- [x] TypeScript compiles: `cd web && npm run build`
- [x] No ESLint errors: `cd web && npm run lint`

#### Manual Verification:
- [x] Hovering over a region highlights only that specific region
- [x] Other regions remain unhighlighted
- [x] Works at all lambda values (test λ=0 with many regions and λ=0.9 with few)
- [x] No performance degradation when switching lambda values

---

## Phase 8: UI Refinements

### Overview
Polish the visual presentation by removing polygon outlines and adding area statistics to the summary panel.

### Changes Required:

#### 1. Remove white outline from GeoJsonLayer
**File**: `web/src/App.tsx`

Update the GeoJsonLayer configuration:
```typescript
return new GeoJsonLayer({
  // ...
  stroked: false,  // Changed from true
  // Remove getLineColor and getLineWidth
});
```

#### 2. Add Area statistic to SummaryPanel
**File**: `web/src/components/SummaryPanel.tsx`

Add area calculation and display between Population and Regions:
```tsx
// Convert area from square meters to square miles
const areaSqMiles = (props.area_sqm / 2_589_988).toLocaleString(undefined, { maximumFractionDigits: 0 });

// In the JSX, between Population and Regions:
<div className="stat">
  <dt>Area</dt>
  <dd>{areaSqMiles} mi²</dd>
</div>
```

#### 3. Add Area per Region statistic to SummaryPanel
**File**: `web/src/components/SummaryPanel.tsx`

Add area per region calculation and display below Regions:
```tsx
// Calculate area per region in square miles
const areaPerRegion = (props.area_sqm / 2_589_988 / props.num_parts).toLocaleString(undefined, { maximumFractionDigits: 0 });

// In the JSX, after Regions:
<div className="stat">
  <dt>Area/Region</dt>
  <dd>{areaPerRegion} mi²</dd>
</div>
```

### Success Criteria:

#### Automated Verification:
- [x] TypeScript compiles: `cd web && npm run build`
- [x] No ESLint errors: `cd web && npm run lint`

#### Manual Verification:
- [x] Polygons render without white outline
- [x] Area displays in square miles in summary panel
- [x] Area per Region displays in square miles in summary panel
- [x] All values update when lambda changes

---

## Testing Strategy

### Manual Testing Steps:
1. Start dev server: `cd web && npm run dev`
2. Observe loading screen with progress
3. Verify map loads with Dark Matter basemap
4. Verify blue polygons appear on map
5. Test slider movement - layers should switch instantly
6. Verify summary panel updates with slider
7. Test hover highlight on polygons
8. Test on mobile viewport (Chrome DevTools device mode)
9. Test error state by disabling network and refreshing
10. Build and preview: `npm run build && npm run preview`

### Edge Cases:
- Slow network (throttle in DevTools)
- Mobile viewport sizes (320px - 768px)
- Touch interactions on slider
- Offline/network error recovery

## Performance Considerations

- All 10 TopoJSON files loaded in parallel (~2.3MB total)
- All 10 GeoJsonLayers created upfront, visibility toggled (not recreated)
- GPU buffers preserved across layer switches for instant response
- Estimated memory: ~50-100MB (acceptable for modern browsers)

## References

- Research: `thoughts/shared/research/2025-11-22-subphase-5-2-core-visualization.md`
- ROADMAP: `ROADMAP.md` Sub-Phase 5.2
- Lambda types: `web/src/types/lambda.ts`
- deck.gl docs: https://deck.gl/docs/api-reference/layers/geojson-layer
- react-map-gl docs: https://visgl.github.io/react-map-gl/docs
