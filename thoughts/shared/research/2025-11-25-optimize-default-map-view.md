---
date: 2025-11-25T10:30:00-08:00
researcher: Claude
git_commit: 78e787efcad23ab9a3cbfc71e7948c08bf19ec2e
branch: master
repository: half-america
topic: "Optimize default map view: Adjust initial zoom/pan so contiguous US is maximally large while fully visible"
tags: [research, codebase, map-view, react-map-gl, maplibre, fitBounds, phase-6]
status: complete
last_updated: 2025-11-25
last_updated_by: Claude
---

# Research: Optimize Default Map View

**Date**: 2025-11-25T10:30:00-08:00
**Researcher**: Claude
**Git Commit**: 78e787efcad23ab9a3cbfc71e7948c08bf19ec2e
**Branch**: master
**Repository**: half-america

## Research Question

How should we adjust the initial zoom/pan so that the contiguous US is maximally large while fully visible?

## Summary

The current implementation uses a static center point and fixed zoom level (`zoom: 3.5`), which doesn't adapt to different viewport sizes. The recommended solution is to use react-map-gl's `initialViewState.bounds` feature, which automatically calculates the optimal zoom and center to fit the contiguous US within any viewport. This is a simple one-line change that replaces the hardcoded zoom/center with bounds coordinates.

## Detailed Findings

### Current Implementation

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

**Issues with current approach:**
- Fixed zoom level doesn't adapt to viewport dimensions
- On wide monitors, extra horizontal space is wasted
- On narrow/mobile screens, US may extend beyond viewport
- Center point is correct but zoom is a guess

### Recommended Solution: `initialViewState.bounds`

react-map-gl supports passing bounds directly to `initialViewState`, which automatically calculates optimal zoom and center:

```typescript
const CONTIGUOUS_US_BOUNDS: [[number, number], [number, number]] = [
  [-125.0, 24.5],   // Southwest [lng, lat]
  [-66.5, 49.5]     // Northeast [lng, lat]
];

const INITIAL_VIEW_STATE = {
  bounds: CONTIGUOUS_US_BOUNDS,
  fitBoundsOptions: {
    padding: 20  // pixels from edge
  },
  pitch: 0,
  bearing: 0,
};
```

**Benefits:**
- Automatically adapts to any viewport size
- Maximizes the visible area of the US
- Works consistently across desktop, tablet, and mobile
- No manual zoom calculation needed

### Contiguous US Bounding Coordinates

Multiple authoritative sources provide consistent bounds:

| Source | West | South | East | North |
|--------|------|-------|------|-------|
| Mapbox Tiling Service | -125.0011 | 24.9493 | -66.9326 | 49.5904 |
| GitHub (jsundram) | -124.7844 | 24.7433 | -66.9514 | 49.3458 |
| **Recommended** | -125.0 | 24.5 | -66.5 | 49.5 |

The recommended values are rounded slightly outward to ensure a small buffer around the actual US boundaries.

### Padding Considerations

The `fitBoundsOptions.padding` parameter adds space between the bounds and viewport edge:

```typescript
// Uniform padding (all sides)
fitBoundsOptions: { padding: 20 }

// Asymmetric padding (for UI overlays)
fitBoundsOptions: {
  padding: {
    top: 80,     // Space for title overlay
    bottom: 100, // Space for slider/legend
    left: 20,
    right: 20
  }
}
```

For this project, consider asymmetric padding to account for:
- Map title overlay at top
- Lambda slider and legend at bottom
- Tab bar at top on desktop / bottom on mobile

### Alternative: Programmatic fitBounds on Load

If dynamic fitting is needed (e.g., after data loads):

```typescript
const mapRef = useRef<MapRef>(null);

useEffect(() => {
  if (mapRef.current) {
    mapRef.current.fitBounds(CONTIGUOUS_US_BOUNDS, {
      padding: 20,
      duration: 0  // No animation on initial load
    });
  }
}, []);
```

This approach is more complex and not needed for a static bounds requirement.

### Resize Handling

The map already calls `resize()` when the tab becomes visible (`MapTab.tsx:42-47`). The bounds-based `initialViewState` automatically handles initial sizing. For window resize events, the map canvas resizes but doesn't re-fit bounds (this is standard behavior - users can manually reset if desired).

## Code References

- `web/src/components/MapTab.tsx:18-24` - Current INITIAL_VIEW_STATE definition
- `web/src/components/MapTab.tsx:85-92` - Map component with initialViewState prop
- `web/src/components/MapTab.tsx:37-48` - Map ref and resize handling

## Implementation Recommendation

### Minimal Change (Recommended)

Replace the current `INITIAL_VIEW_STATE` with bounds-based configuration:

```typescript
// Contiguous US bounds: [Southwest, Northeast] as [lng, lat]
const CONTIGUOUS_US_BOUNDS: [[number, number], [number, number]] = [
  [-125.0, 24.5],
  [-66.5, 49.5]
];

const INITIAL_VIEW_STATE = {
  bounds: CONTIGUOUS_US_BOUNDS,
  fitBoundsOptions: {
    padding: {
      top: 60,     // Title overlay
      bottom: 80,  // Slider + legend
      left: 20,
      right: 20
    }
  },
  pitch: 0,
  bearing: 0,
};
```

### Testing Considerations

- Test on various viewport sizes (mobile, tablet, desktop, ultrawide)
- Verify US is fully visible with no clipping
- Confirm padding doesn't cut off important features
- Check that user can still pan/zoom after initial load

## Architecture Insights

The react-map-gl library provides two viewport management modes:
1. **Uncontrolled** (current): Pass `initialViewState`, map manages state internally
2. **Controlled**: Pass `viewState` + `onMove`, component manages state externally

The bounds feature works with both modes. Using `initialViewState.bounds` keeps the simple uncontrolled pattern while adding responsive sizing.

## Related Documentation

- [react-map-gl initialViewState](https://visgl.github.io/react-map-gl/docs/api-reference/map#initialviewstate)
- [MapLibre fitBounds API](https://maplibre.org/maplibre-gl-js/docs/API/classes/Map/#fitbounds)
- [MapLibre FitBoundsOptions](https://maplibre.org/maplibre-gl-js/docs/API/type-aliases/FitBoundsOptions/)

## Open Questions

1. **Padding values**: What are the exact pixel heights of the title overlay and legend/slider that should inform padding?
2. **Mobile behavior**: Should padding differ on mobile where tab bar is at bottom?
3. **Reset button**: Should there be a "reset view" button to return to the fitted bounds after user panning?
