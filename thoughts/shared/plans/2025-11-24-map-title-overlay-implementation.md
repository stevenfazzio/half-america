# Map Title Overlay Implementation Plan

## Overview

Add a map title overlay displaying "Half of America" with subtitle "Where 50% of Americans live" to the Map tab for first-glance clarity. This addresses Phase 6 item in ROADMAP.md.

## Current State Analysis

The Map tab has three fixed-position overlays:
- **LambdaSlider** - top-left, 280px wide
- **TabBar** - top-center, z-index: 10
- **SummaryPanel** - top-right, min-width: 160px

All overlays share consistent styling: `rgba(30, 30, 30, 0.95)` background, `border-radius: 8px`, `z-index: 1`.

### Key Discoveries:
- TabBar uses `left: 50%; transform: translateX(-50%)` for centering (`TabBar.css:5-6`)
- SummaryPanel already shows "Half of America" title on mobile (`SummaryPanel.tsx:32`)
- Mobile breakpoint is `@media (max-width: 767px)` (`TabBar.css:36`)
- TabBar is at `top: 16px` with ~32px height, so new title should start at `top: 56px`

## Desired End State

A pill-shaped title overlay appears below the TabBar on desktop showing:
- Main title: "Half of America" (20px, bold)
- Subtitle: "Where 50% of Americans live" (14px, muted)

The title is hidden on mobile where SummaryPanel already provides context.

### Verification:
- Desktop: Title visible at top-center, below TabBar, doesn't overlap other elements
- Mobile: Title hidden, SummaryPanel visible with "Half of America" heading

## What We're NOT Doing

- No dismissible/minimize functionality
- No fade-in animation
- No mobile-specific condensed version
- No changes to SummaryPanel

## Implementation Approach

Create a simple `MapTitle` component following the established overlay pattern. Add it as a sibling to other overlays in `MapTab.tsx`.

## Phase 1: Create MapTitle Component

### Overview
Create the new component with CSS styling matching existing panel patterns.

### Changes Required:

#### 1. Create MapTitle.tsx
**File**: `web/src/components/MapTitle.tsx` (new)

```tsx
import './MapTitle.css';

export function MapTitle() {
  return (
    <div className="map-title">
      <h1 className="map-title-main">Half of America</h1>
      <p className="map-title-sub">Where 50% of Americans live</p>
    </div>
  );
}
```

#### 2. Create MapTitle.css
**File**: `web/src/components/MapTitle.css` (new)

```css
.map-title {
  position: fixed;
  top: 56px; /* Below TabBar (16px top + ~32px height + 8px gap) */
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 20px;
  background: rgba(30, 30, 30, 0.95);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  z-index: 1;
  color: #fff;
  text-align: center;
}

.map-title-main {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
}

.map-title-sub {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin: 4px 0 0 0;
}

/* Hide on mobile - SummaryPanel already has title */
@media (max-width: 767px) {
  .map-title {
    display: none;
  }
}
```

### Success Criteria:

#### Automated Verification:
- [ ] Build passes: `cd web && npm run build`
- [ ] Lint passes: `cd web && npm run lint`
- [ ] TypeScript compiles without errors

#### Manual Verification:
- [ ] Files created at correct paths

**Implementation Note**: Proceed to Phase 2 immediately after creating files.

---

## Phase 2: Integrate into MapTab

### Overview
Import and render MapTitle in MapTab.tsx as a sibling to other overlays.

### Changes Required:

#### 1. Update MapTab.tsx
**File**: `web/src/components/MapTab.tsx`
**Changes**: Add import and render MapTitle

Add import at line 8 (after SummaryPanel import):
```tsx
import { MapTitle } from './MapTitle';
```

Add component render at line 92 (after Map, before LambdaSlider):
```tsx
<MapTitle />
```

The render section should look like:
```tsx
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
    <MapTitle />
    <LambdaSlider value={currentLambda} onChange={setCurrentLambda} />
    <SummaryPanel data={loaderState.data.get(currentLambda)} lambda={currentLambda} />
  </>
)}
```

### Success Criteria:

#### Automated Verification:
- [ ] Build passes: `cd web && npm run build`
- [ ] Lint passes: `cd web && npm run lint`
- [ ] Dev server starts: `cd web && npm run dev`

#### Manual Verification:
- [ ] Desktop: Title visible at top-center, below TabBar
- [ ] Desktop: Title doesn't overlap LambdaSlider or SummaryPanel
- [ ] Mobile: Title hidden (use browser DevTools responsive mode)
- [ ] Mobile: SummaryPanel still visible with "Half of America" heading

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 3: Update Documentation

### Overview
Mark the ROADMAP.md item as complete.

### Changes Required:

#### 1. Update ROADMAP.md
**File**: `ROADMAP.md`
**Changes**: Mark map title overlay item complete

Change line 158 from:
```markdown
- [ ] Add map title overlay ("Half of America / Where 50% of Americans live") for first-glance clarity
```

To:
```markdown
- [x] Add map title overlay ("Half of America / Where 50% of Americans live") for first-glance clarity
```

### Success Criteria:

#### Automated Verification:
- [ ] File updated correctly

#### Manual Verification:
- [ ] ROADMAP.md reflects completed status

---

## Testing Strategy

### Unit Tests:
- No unit tests required - this is a presentational component with no logic

### Manual Testing Steps:
1. Open http://localhost:5173 in browser
2. Verify title appears below TabBar, centered horizontally
3. Verify title doesn't overlap slider (left) or summary panel (right)
4. Open browser DevTools and toggle to mobile view (< 768px width)
5. Verify title disappears on mobile
6. Verify SummaryPanel still shows "Half of America" on mobile
7. Switch between tabs and verify title reappears on Map tab

## Performance Considerations

None - this is a simple static component with no state or effects.

## References

- Original research: `thoughts/shared/research/2025-11-24-map-title-overlay-implementation.md`
- ROADMAP item: `ROADMAP.md:158`
- Styling patterns: `web/src/components/SummaryPanel.css:1-12`, `web/src/components/TabBar.css:1-10`
