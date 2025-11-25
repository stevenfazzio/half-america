# Optimize Default Map View Implementation Plan

## Overview

Replace the hardcoded zoom/center in `INITIAL_VIEW_STATE` with react-map-gl's bounds-based configuration to automatically calculate optimal zoom and center for the contiguous US, adapting to any viewport size.

## Current State Analysis

**File**: `web/src/components/MapTab.tsx:18-24`

```typescript
const INITIAL_VIEW_STATE = {
  longitude: -98.5795,
  latitude: 39.8283,
  zoom: 3.5,
  pitch: 0,
  bearing: 0,
};
```

**Issues:**
- Fixed zoom level doesn't adapt to viewport dimensions
- On wide monitors, extra horizontal space is wasted
- On narrow/mobile screens, US may extend beyond viewport

### UI Overlay Positions

**Desktop (≥768px):**
| Element | Position | Dimensions |
|---------|----------|------------|
| TabBar | top: 16px, centered | ~32px height |
| MapTitle | top: 56px, centered | ~60px height with padding |
| LambdaSlider | top: 16px, left: 16px | 360px wide, ~120px tall |
| SummaryPanel | top: 16px, right: 16px | ~160px wide |

**Mobile (<768px):**
| Element | Position | Notes |
|---------|----------|-------|
| TabBar | bottom: 0 | 50px + safe-area-inset |
| LambdaSlider | bottom: 70px | Full width |
| SummaryPanel | top: 16px, right: 16px | Smaller |
| MapTitle | hidden | |

## Desired End State

The map should:
1. Show the entire contiguous US on initial load
2. Maximize the visible US area within the viewport
3. Account for UI overlays (title, slider, legend, tab bar)
4. Work consistently across desktop, tablet, and mobile viewports

**Verification:**
- US is fully visible with no clipping on all viewport sizes
- Map fills available space without excessive margins
- User can still pan/zoom after initial load

## What We're NOT Doing

- No dynamic re-fitting on window resize (standard map behavior)
- No "reset view" button (could be future enhancement)
- No different bounds for mobile vs desktop (padding handles this)

## Implementation Approach

Use react-map-gl's `initialViewState.bounds` feature which automatically calculates optimal zoom and center to fit specified bounds within the viewport.

## Phase 1: Update INITIAL_VIEW_STATE

### Overview
Replace the hardcoded zoom/center with bounds-based configuration.

### Changes Required:

#### 1. MapTab.tsx
**File**: `web/src/components/MapTab.tsx`
**Changes**: Replace `INITIAL_VIEW_STATE` definition

**Before (lines 18-24):**
```typescript
const INITIAL_VIEW_STATE = {
  longitude: -98.5795,
  latitude: 39.8283,
  zoom: 3.5,
  pitch: 0,
  bearing: 0,
};
```

**After:**
```typescript
// Contiguous US bounds: [Southwest, Northeast] as [lng, lat]
const CONTIGUOUS_US_BOUNDS: [[number, number], [number, number]] = [
  [-125.0, 24.5],
  [-66.5, 49.5],
];

const INITIAL_VIEW_STATE = {
  bounds: CONTIGUOUS_US_BOUNDS,
  fitBoundsOptions: {
    padding: {
      top: 120,    // TabBar + MapTitle + buffer
      bottom: 100, // LambdaSlider (mobile) + buffer
      left: 20,    // Small buffer
      right: 20,   // Small buffer
    },
  },
  pitch: 0,
  bearing: 0,
};
```

**Padding Rationale:**
- `top: 120`: On desktop, accounts for TabBar (16+32=48px) + MapTitle (56+60=116px). Using 120px provides buffer. On mobile, MapTitle is hidden so extra padding just adds margin.
- `bottom: 100`: On mobile, LambdaSlider is at bottom: 70px with ~100px height. On desktop, slider is at top, so bottom padding is just margin.
- `left/right: 20`: Small buffer from edges. Desktop has LambdaSlider (360px) and SummaryPanel (~160px) at top, not overlapping vertical map content.

### Success Criteria:

#### Automated Verification:
- [ ] TypeScript compiles without errors: `cd web && npm run build`
- [ ] Linting passes: `cd web && npm run lint`

#### Manual Verification:
- [ ] Desktop (1920x1080): US fully visible, well-centered with appropriate margins
- [ ] Desktop (ultrawide): US fills more horizontal space than before
- [ ] Tablet (768x1024): US fully visible in portrait and landscape
- [ ] Mobile (375x667): US fully visible, not clipped by bottom slider
- [ ] User can still pan and zoom after initial load
- [ ] No visual regression in existing UI elements

**Implementation Note**: After completing this phase and all automated verification passes, pause for manual testing across different viewport sizes.

---

## Testing Strategy

### Unit Tests:
No new unit tests needed - this is a configuration change verified by visual inspection.

### Manual Testing Steps:
1. Open site in Chrome DevTools responsive mode
2. Test viewports: 375x667 (iPhone SE), 768x1024 (iPad), 1920x1080 (desktop), 2560x1080 (ultrawide)
3. For each viewport:
   - Verify entire contiguous US is visible (Alaska/Hawaii excluded is expected)
   - Verify no part of the US is clipped by viewport edges
   - Verify map fills available space without excessive margins
   - Verify UI overlays don't obscure important map areas
   - Verify user can pan and zoom

## Performance Considerations

None - bounds calculation happens once on initial load. No runtime performance impact.

## References

- Research document: `thoughts/shared/research/2025-11-25-optimize-default-map-view.md`
- [react-map-gl initialViewState.bounds docs](https://visgl.github.io/react-map-gl/docs/api-reference/map#initialviewstate)
- [MapLibre fitBounds API](https://maplibre.org/maplibre-gl-js/docs/API/classes/Map/#fitbounds)
