# Tab Structure Implementation Plan

## Overview

Implement a three-tab navigation structure (Map, Story, Method) for the Half of America web frontend. The Map tab contains the existing interactive visualization, while Story and Method tabs are stub placeholders for future content. Navigation uses URL hash routing for shareability and a responsive design (top pills on desktop, bottom nav on mobile).

## Current State Analysis

**App.tsx** (`web/src/App.tsx`): Monolithic component containing all Map logic directly:
- Uses `useTopoJsonLoader` hook (starts loading on module import)
- Renders `Map`, `DeckGLOverlay`, `LambdaSlider`, `SummaryPanel`
- Loading/error states block the entire app

**Styling**: Component-scoped CSS with dark theme pattern:
- Panel background: `rgba(30, 30, 30, 0.95)`
- Primary text: `#fff`
- Secondary text: `rgba(255, 255, 255, 0.7)`
- Accent: `#0072B2` (Okabe-Ito Blue)

**Key Constraint**: deck.gl breaks with `display: none` (infinite resize loops). Must use `visibility: collapse` pattern.

## Desired End State

1. Three tabs accessible via URL hash: `#map` (default), `#story`, `#method`
2. Map tab preserves WebGL state when switching away (KeepMounted pattern)
3. Story/Method tabs show immediately without waiting for Map data to load
4. Map controls (LambdaSlider, SummaryPanel) only visible on Map tab
5. Responsive navigation: top center pills (desktop), bottom nav bar (mobile)
6. Ultra-minimal chrome that doesn't compete with the visualization

### Verification:
- Navigate to site → lands on Map tab with `#map` in URL
- Click Story tab → URL changes to `#story`, Story content shows, Map hidden but preserved
- Click back to Map → Map reappears instantly without reloading data
- Direct navigation to `https://site.com/#method` → Method tab shows immediately
- Mobile: bottom nav is thumb-reachable, LambdaSlider positioned above nav bar

## What We're NOT Doing

- **Content for Story/Method tabs** - stubs only, content is a separate task
- **react-router-dom** - overkill for 3 tabs, using native hash routing
- **Lazy loading of TopoJSON** - keeping current eager loading behavior (simpler)
- **Animation/transitions** - keep tab switches instant for now
- **Hamburger menu on mobile** - research shows 20%+ drop in discoverability

## Implementation Approach

Use React state + native `hashchange` event listener for routing. Implement KeepMounted pattern to preserve Map's WebGL context. Extract Map logic to dedicated component. Create responsive TabBar with CSS media queries.

---

## Phase 1: Core Infrastructure

### Overview
Create the `useKeepMounted` hook and `TabBar` component that will be used by the rest of the implementation.

### Changes Required:

#### 1. Create useKeepMounted Hook
**File**: `web/src/hooks/useKeepMounted.ts` (NEW)

```typescript
import { useState, useEffect } from 'react';

/**
 * Hook to implement lazy mount + state persistence pattern.
 * Component mounts on first activation and stays mounted thereafter.
 * Use with visibility: collapse (NOT display: none) for deck.gl compatibility.
 */
export function useKeepMounted(isActive: boolean) {
  const [hasBeenMounted, setHasBeenMounted] = useState(false);

  useEffect(() => {
    if (isActive && !hasBeenMounted) {
      setHasBeenMounted(true);
    }
  }, [isActive, hasBeenMounted]);

  return {
    /** Whether the component should render at all */
    shouldRender: hasBeenMounted,
    /** Whether the component is currently visible */
    isVisible: isActive,
  };
}
```

#### 2. Create TabBar Component
**File**: `web/src/components/TabBar.tsx` (NEW)

```tsx
import './TabBar.css';

export type TabId = 'map' | 'story' | 'method';

interface TabBarProps {
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
}

const TABS: { id: TabId; label: string }[] = [
  { id: 'map', label: 'Map' },
  { id: 'story', label: 'Story' },
  { id: 'method', label: 'Method' },
];

export function TabBar({ activeTab, onTabChange }: TabBarProps) {
  return (
    <nav className="tab-bar" role="tablist" aria-label="Main navigation">
      {TABS.map(({ id, label }) => (
        <button
          key={id}
          role="tab"
          aria-selected={activeTab === id}
          aria-controls={`${id}-tab`}
          className={`tab-button ${activeTab === id ? 'active' : ''}`}
          onClick={() => onTabChange(id)}
        >
          {label}
        </button>
      ))}
    </nav>
  );
}
```

#### 3. Create TabBar Styles
**File**: `web/src/components/TabBar.css` (NEW)

```css
/* Desktop: Ultra-minimal floating pills at top center */
.tab-bar {
  position: fixed;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
  z-index: 10;
}

.tab-button {
  background: transparent;
  color: rgba(255, 255, 255, 0.5);
  border: none;
  padding: 6px 12px;
  font-size: 12px;
  font-family: inherit;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: color 0.15s ease, background 0.15s ease;
}

.tab-button:hover {
  color: rgba(255, 255, 255, 0.9);
}

.tab-button.active {
  color: #fff;
  background: rgba(30, 30, 30, 0.7);
  border-radius: 4px;
}

/* Mobile: Bottom navigation bar */
@media (max-width: 767px) {
  .tab-bar {
    top: auto;
    bottom: 0;
    left: 0;
    right: 0;
    transform: none;
    height: 50px;
    justify-content: space-around;
    align-items: center;
    background: rgba(30, 30, 30, 0.95);
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    gap: 0;
    padding-bottom: env(safe-area-inset-bottom);
  }

  .tab-button {
    flex: 1;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    padding: 0;
  }

  .tab-button.active {
    background: transparent;
    color: #0072B2;
  }
}
```

### Success Criteria:

#### Automated Verification:
- [x] TypeScript compiles without errors: `cd web && npm run build`
- [x] No lint errors: `npm run lint`

#### Manual Verification:
- [ ] (Deferred to Phase 3 - components not yet integrated)

**Implementation Note**: After completing this phase and all automated verification passes, proceed to Phase 2.

---

## Phase 2: Extract MapTab Component

### Overview
Extract the current Map logic from App.tsx into a dedicated MapTab component with the KeepMounted pattern.

### Changes Required:

#### 1. Create MapTab Component
**File**: `web/src/components/MapTab.tsx` (NEW)

```tsx
import { useState, useMemo, useRef, useEffect } from 'react';
import { Map, MapRef } from 'react-map-gl/maplibre';
import { GeoJsonLayer } from '@deck.gl/layers';
import 'maplibre-gl/dist/maplibre-gl.css';
import { DeckGLOverlay } from './DeckGLOverlay';
import { LambdaSlider } from './LambdaSlider';
import { SummaryPanel } from './SummaryPanel';
import { useKeepMounted } from '../hooks/useKeepMounted';
import { LAMBDA_VALUES } from '../types/lambda';
import type { LambdaValue } from '../types/lambda';
import type { LoaderState } from '../hooks/useTopoJsonLoader';
import './MapTab.css';

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
const HIGHLIGHT_COLOR: [number, number, number, number] = [255, 255, 255, 100];

interface MapTabProps {
  isActive: boolean;
  loaderState: LoaderState;
}

export function MapTab({ isActive, loaderState }: MapTabProps) {
  const { shouldRender, isVisible } = useKeepMounted(isActive);
  const mapRef = useRef<MapRef>(null);
  const [currentLambda, setCurrentLambda] = useState<LambdaValue>(0.5);

  // Trigger map resize when becoming visible
  useEffect(() => {
    if (isVisible && mapRef.current) {
      // Use requestAnimationFrame to ensure DOM has updated
      requestAnimationFrame(() => {
        mapRef.current?.resize();
      });
    }
  }, [isVisible]);

  const layers = useMemo(() => {
    if (loaderState.status !== 'success') return [];

    return LAMBDA_VALUES.map((lambda) => {
      const data = loaderState.data.get(lambda);
      return new GeoJsonLayer({
        id: `layer-${lambda.toFixed(2)}`,
        data,
        visible: lambda === currentLambda,
        filled: true,
        stroked: false,
        getFillColor: FILL_COLOR,
        pickable: true,
        autoHighlight: true,
        highlightColor: HIGHLIGHT_COLOR,
      });
    });
  }, [loaderState, currentLambda]);

  if (!shouldRender) {
    return null;
  }

  const showMap = loaderState.status === 'success';

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
            initialViewState={INITIAL_VIEW_STATE}
            style={{ width: '100%', height: '100vh' }}
            mapStyle={CARTO_DARK_MATTER}
          >
            <DeckGLOverlay layers={layers} interleaved />
          </Map>
          <LambdaSlider value={currentLambda} onChange={setCurrentLambda} />
          <SummaryPanel data={loaderState.data.get(currentLambda)} lambda={currentLambda} />
        </>
      )}
    </div>
  );
}
```

#### 2. Create MapTab Styles
**File**: `web/src/components/MapTab.css` (NEW)

```css
.map-tab {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100vh;
}
```

#### 3. Update LambdaSlider Mobile Position
**File**: `web/src/components/LambdaSlider.css`
**Changes**: Adjust mobile bottom position to account for bottom nav bar

Replace the mobile `bottom: 80px` with `bottom: 70px` to leave space for the 50px bottom nav plus some padding:

```css
/* Change this line */
.lambda-slider {
  position: fixed;
  bottom: 70px;  /* Was 80px, adjusted for bottom nav */
  left: 16px;
  right: 16px;
  /* ... rest unchanged ... */
}
```

### Success Criteria:

#### Automated Verification:
- [x] TypeScript compiles without errors: `cd web && npm run build`
- [x] No lint errors: `npm run lint`

#### Manual Verification:
- [ ] (Deferred to Phase 3 - component not yet integrated into App)

**Implementation Note**: After completing this phase and all automated verification passes, proceed to Phase 3.

---

## Phase 3: Hash Routing & Tab State in App.tsx

### Overview
Update App.tsx to manage tab state, implement hash routing, and render tabs conditionally. This is where everything comes together.

### Changes Required:

#### 1. Rewrite App.tsx
**File**: `web/src/App.tsx`

```tsx
import { useState, useEffect, useCallback } from 'react';
import { TabBar } from './components/TabBar';
import { MapTab } from './components/MapTab';
import { StoryTab } from './components/StoryTab';
import { MethodTab } from './components/MethodTab';
import { LoadingOverlay } from './components/LoadingOverlay';
import { ErrorOverlay } from './components/ErrorOverlay';
import { useTopoJsonLoader } from './hooks/useTopoJsonLoader';
import { LAMBDA_VALUES } from './types/lambda';
import type { TabId } from './components/TabBar';
import './App.css';

function getTabFromHash(): TabId {
  const hash = window.location.hash.slice(1); // Remove #
  if (hash === 'story' || hash === 'method') {
    return hash;
  }
  return 'map';
}

function App() {
  const { state: loaderState, retry } = useTopoJsonLoader();
  const [activeTab, setActiveTab] = useState<TabId>(getTabFromHash);

  // Sync tab state with URL hash
  useEffect(() => {
    const handleHashChange = () => {
      setActiveTab(getTabFromHash());
    };

    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const handleTabChange = useCallback((tab: TabId) => {
    window.location.hash = tab;
    setActiveTab(tab);
  }, []);

  // Set initial hash if not present
  useEffect(() => {
    if (!window.location.hash) {
      window.location.hash = 'map';
    }
  }, []);

  // Show loading overlay only when Map tab is active and data is loading
  const showLoading = activeTab === 'map' &&
    (loaderState.status === 'loading' || loaderState.status === 'idle');

  // Show error overlay only when Map tab is active and there's an error
  const showError = activeTab === 'map' && loaderState.status === 'error';

  if (showLoading) {
    const loaded = loaderState.status === 'loading' ? loaderState.loaded : 0;
    return (
      <>
        <TabBar activeTab={activeTab} onTabChange={handleTabChange} />
        <LoadingOverlay loaded={loaded} total={LAMBDA_VALUES.length} />
      </>
    );
  }

  if (showError) {
    return (
      <>
        <TabBar activeTab={activeTab} onTabChange={handleTabChange} />
        <ErrorOverlay message={loaderState.error.message} onRetry={retry} />
      </>
    );
  }

  return (
    <div className="app">
      <TabBar activeTab={activeTab} onTabChange={handleTabChange} />
      <MapTab isActive={activeTab === 'map'} loaderState={loaderState} />
      {activeTab === 'story' && <StoryTab />}
      {activeTab === 'method' && <MethodTab />}
    </div>
  );
}

export default App;
```

#### 2. Create StoryTab Stub
**File**: `web/src/components/StoryTab.tsx` (NEW)

```tsx
import './StoryTab.css';

export function StoryTab() {
  return (
    <div className="story-tab" role="tabpanel" id="story-tab" aria-labelledby="story">
      <div className="story-content">
        <h1>The Story</h1>
        <p className="subtitle">How half of America fits in a surprisingly small space</p>
        <div className="placeholder">
          <p>Content coming soon.</p>
          <p>This tab will explain the intuition behind the visualization without the math.</p>
        </div>
      </div>
    </div>
  );
}
```

#### 3. Create StoryTab Styles
**File**: `web/src/components/StoryTab.css` (NEW)

```css
.story-tab {
  position: absolute;
  inset: 0;
  overflow-y: auto;
  background: #1a1a1a;
  padding: 80px 24px 24px; /* Top padding for tab bar */
}

@media (max-width: 767px) {
  .story-tab {
    padding: 24px 16px 80px; /* Bottom padding for mobile nav */
  }
}

.story-content {
  max-width: 680px;
  margin: 0 auto;
}

.story-content h1 {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px 0;
}

.story-content .subtitle {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 32px 0;
}

.story-content .placeholder {
  padding: 24px;
  background: rgba(30, 30, 30, 0.95);
  border-radius: 8px;
  border: 1px dashed rgba(255, 255, 255, 0.2);
}

.story-content .placeholder p {
  margin: 0 0 8px 0;
  color: rgba(255, 255, 255, 0.5);
}

.story-content .placeholder p:last-child {
  margin-bottom: 0;
}
```

#### 4. Create MethodTab Stub
**File**: `web/src/components/MethodTab.tsx` (NEW)

```tsx
import './MethodTab.css';

export function MethodTab() {
  return (
    <div className="method-tab" role="tabpanel" id="method-tab" aria-labelledby="method">
      <div className="method-content">
        <h1>Methodology</h1>
        <p className="subtitle">Technical details for replication, critique, and extension</p>
        <div className="placeholder">
          <p>Content coming soon.</p>
          <p>This tab will contain the full mathematical formulation and implementation details.</p>
        </div>
      </div>
    </div>
  );
}
```

#### 5. Create MethodTab Styles
**File**: `web/src/components/MethodTab.css` (NEW)

```css
.method-tab {
  position: absolute;
  inset: 0;
  overflow-y: auto;
  background: #1a1a1a;
  padding: 80px 24px 24px; /* Top padding for tab bar */
}

@media (max-width: 767px) {
  .method-tab {
    padding: 24px 16px 80px; /* Bottom padding for mobile nav */
  }
}

.method-content {
  max-width: 680px;
  margin: 0 auto;
}

.method-content h1 {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 8px 0;
}

.method-content .subtitle {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0 0 32px 0;
}

.method-content .placeholder {
  padding: 24px;
  background: rgba(30, 30, 30, 0.95);
  border-radius: 8px;
  border: 1px dashed rgba(255, 255, 255, 0.2);
}

.method-content .placeholder p {
  margin: 0 0 8px 0;
  color: rgba(255, 255, 255, 0.5);
}

.method-content .placeholder p:last-child {
  margin-bottom: 0;
}
```

### Success Criteria:

#### Automated Verification:
- [x] TypeScript compiles without errors: `cd web && npm run build`
- [x] No lint errors: `npm run lint`
- [x] Dev server starts without errors: `npm run dev`

#### Manual Verification:
- [x] Navigate to site root → redirects to `#map`, shows Map tab with visualization
- [x] Click "Story" tab → URL changes to `#story`, Story stub content appears
- [x] Click "Method" tab → URL changes to `#method`, Method stub content appears
- [x] Click "Map" tab → URL changes to `#map`, Map reappears instantly (no reload)
- [x] Direct navigation to `localhost:5173/#story` → Story tab loads immediately
- [x] Direct navigation to `localhost:5173/#method` → Method tab loads immediately
- [x] Browser back/forward buttons work correctly with tab navigation
- [x] Desktop: Tab pills appear at top center, minimal and unobtrusive
- [x] Mobile (dev tools): Bottom nav bar appears, tabs fill width
- [x] Mobile: LambdaSlider positioned above bottom nav (not overlapping)
- [x] Map controls (slider, summary panel) only visible on Map tab

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to Phase 4.

---

## Phase 4: Polish & Edge Cases

### Overview
Handle edge cases and polish the implementation.

### Changes Required:

#### 1. Update App.css for Tab Container
**File**: `web/src/App.css`

Add styles to ensure tabs render correctly:

```css
/* Add to existing file */

/* Tab content container */
.app {
  width: 100%;
  height: 100vh;
  position: relative;
  overflow: hidden;
}
```

(This is mostly already present, but verify the `overflow: hidden` is set)

#### 2. Ensure Loading Overlay Has Tab Bar
Already handled in Phase 3 - the TabBar renders even during loading/error states so users can navigate away.

### Success Criteria:

#### Automated Verification:
- [x] Build succeeds: `cd web && npm run build`
- [x] Production preview works: `npm run preview`

#### Manual Verification:
- [x] While Map is loading, clicking Story/Method tabs shows their content immediately
- [x] After viewing Story/Method, returning to Map while it's still loading shows loading overlay
- [x] Error state on Map tab allows navigation to Story/Method tabs
- [x] No console errors or warnings during tab navigation
- [x] No visual glitches when switching tabs rapidly

**Implementation Note**: After completing this phase and all verification passes, the implementation is complete.

---

## Testing Strategy

### Unit Tests:
- `useKeepMounted` hook: Test that `shouldRender` stays true after first activation
- `getTabFromHash`: Test parsing of hash values

### Integration Tests:
- Tab navigation updates URL hash
- URL hash changes update active tab
- Map state persists across tab switches

### Manual Testing Steps:
1. Load site fresh → verify Map tab active, `#map` in URL
2. Interact with map (zoom, pan, change lambda)
3. Switch to Story tab → verify Map hidden, URL is `#story`
4. Switch back to Map → verify map state preserved (zoom, pan, lambda)
5. Test all URL direct navigation scenarios
6. Test on mobile viewport (Chrome DevTools)
7. Test rapid tab switching (no crashes)

## Performance Considerations

- **Map stays mounted**: WebGL context is expensive to recreate. The KeepMounted pattern avoids this cost.
- **Visibility vs Display**: Using `visibility: collapse` avoids deck.gl resize loop bugs while hiding content.
- **TopoJSON loads eagerly**: We keep the current behavior where data loads on page load regardless of tab. This ensures Map is ready when user navigates to it.

## Migration Notes

No data migration needed. This is a frontend-only change.

## References

- Research document: `thoughts/shared/research/2025-11-23-tab-structure-implementation.md`
- Tab strategy: `docs/tab_strategy.md`
- Current App.tsx: `web/src/App.tsx`
- deck.gl visibility issue research: Documented in research document (display: none causes infinite resize loops)
