---
date: 2025-11-24T10:30:00-08:00
researcher: Claude
git_commit: 7e197eb4ceccbc6f286ae27adbb37970a477ce8b
branch: master
repository: half-america
topic: "Map Title Overlay Implementation Research"
tags: [research, ui, map, title, overlay, react, css]
status: complete
last_updated: 2025-11-24
last_updated_by: Claude
---

# Research: Map Title Overlay Implementation

**Date**: 2025-11-24T10:30:00-08:00
**Researcher**: Claude
**Git Commit**: 7e197eb4ceccbc6f286ae27adbb37970a477ce8b
**Branch**: master
**Repository**: half-america

## Research Question

How to implement a map title overlay ("Half of America / Where 50% of Americans live") for first-glance clarity, as specified in Phase 6 of ROADMAP.md and item 1 in the UI style polish research.

## Summary

The title overlay should be a new `MapTitle` component rendered as a sibling to `LambdaSlider` and `SummaryPanel` within `MapTab.tsx`. It should use the established fixed-position overlay pattern with `rgba(30, 30, 30, 0.95)` background. The optimal placement is **top-center on desktop** (below TabBar) and **hidden on mobile** (where SummaryPanel already shows the title).

| Decision | Recommendation |
|----------|----------------|
| **Component location** | New `MapTitle.tsx` in `web/src/components/` |
| **Parent container** | `MapTab.tsx`, sibling to other overlays |
| **Desktop position** | Top-center, below TabBar |
| **Mobile position** | Hidden (SummaryPanel already has title) |
| **Z-index** | `1` (same as other panels) |
| **Background** | `rgba(30, 30, 30, 0.95)` with `border-radius: 8px` |

## Detailed Findings

### Current Layout Analysis

The map viewport has fixed-position overlays at specific locations:

**Desktop Layout:**
```
┌────────────────────────────────────────────────────────┐
│ [LambdaSlider]     [TabBar]      [SummaryPanel]        │
│ top-left           top-center    top-right             │
│ 280px wide                       min-width: 160px      │
│                                                        │
│                                                        │
│                    [MAP]                               │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Mobile Layout:**
```
┌────────────────────┐
│     [SummaryPanel] │ ← Has "Half of America" title
│     top-right      │
│                    │
│       [MAP]        │
│                    │
│ [LambdaSlider]     │ ← bottom: 70px
│ [TabBar]           │ ← bottom: 0
└────────────────────┘
```

### Available Positions for Title Overlay

| Position | Desktop Viability | Mobile Viability |
|----------|-------------------|------------------|
| **Top-center** (below TabBar) | Excellent | Poor - crowded |
| **Top-left** | Conflicts with LambdaSlider | Poor |
| **Top-right** | Conflicts with SummaryPanel | Poor |
| **Center viewport** | Too intrusive | Too intrusive |

**Recommendation**: Top-center below TabBar on desktop, hidden on mobile.

### Existing Component Patterns

**Current titles in app:**
| Location | Size | Context |
|----------|------|---------|
| `SummaryPanel.tsx:32` | 16px | Panel heading |
| `LoadingOverlay.tsx:14` | 24px | Full-screen intro |
| `StoryTab.tsx:12` | 32px | Page heading |

**Panel styling pattern** (from `SummaryPanel.css`):
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
}
```

**Centering pattern** (from `TabBar.css`):
```css
.tab-bar {
  position: fixed;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
}
```

### Proposed Implementation

#### 1. Create `MapTitle.tsx`

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

#### 2. Create `MapTitle.css`

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

#### 3. Update `MapTab.tsx`

Add import and render alongside other overlays:

```tsx
// Add import
import { MapTitle } from './MapTitle';

// In render (around line 90):
<Map ...>
  <DeckGLOverlay layers={layers} interleaved />
</Map>
<MapTitle />  {/* Add this line */}
<LambdaSlider value={currentLambda} onChange={setCurrentLambda} />
<SummaryPanel data={loaderState.data.get(currentLambda)} lambda={currentLambda} />
```

### Design Alternatives

**Option A: Semi-transparent header bar (full-width)**
```css
.map-title {
  position: fixed;
  top: 56px;
  left: 0;
  right: 0;
  padding: 12px;
  background: linear-gradient(to bottom, rgba(30, 30, 30, 0.9), transparent);
  text-align: center;
}
```
- Pro: More prominent
- Con: Obscures more of the map

**Option B: No background (text shadow only)**
```css
.map-title {
  position: fixed;
  top: 56px;
  left: 50%;
  transform: translateX(-50%);
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
  /* No background */
}
```
- Pro: Minimally intrusive
- Con: May be hard to read on lighter map areas

**Option C: Inside SummaryPanel (enhance existing)**

Instead of a new component, enhance `SummaryPanel` with larger title and subtitle.
- Pro: No new component
- Con: Right-aligned doesn't have the same "headline" impact

**Recommendation**: Use Option A (pill-shaped container) as it matches existing panel patterns and provides reliable readability.

### Z-Index Considerations

| Component | Z-Index | Notes |
|-----------|---------|-------|
| TabBar | 10 | Must stay above MapTitle |
| MapTitle | 1 | Same level as other panels |
| LambdaSlider | 1 | |
| SummaryPanel | 1 | |

No conflicts expected since MapTitle is positioned below TabBar.

### Mobile Considerations

The title is hidden on mobile because:
1. `SummaryPanel` already displays "Half of America" title
2. Screen real estate is limited
3. Users on mobile can see the title by tapping the Story tab

Alternative: Show a condensed one-line version on mobile at top-center, but this adds complexity for marginal benefit.

## Code References

- [`web/src/components/MapTab.tsx:82-94`](https://github.com/stevenfazzio/half-america/blob/7e197eb4ceccbc6f286ae27adbb37970a477ce8b/web/src/components/MapTab.tsx#L82-L94) - Where to add MapTitle
- [`web/src/components/SummaryPanel.css:1-12`](https://github.com/stevenfazzio/half-america/blob/7e197eb4ceccbc6f286ae27adbb37970a477ce8b/web/src/components/SummaryPanel.css#L1-L12) - Panel styling pattern to follow
- [`web/src/components/TabBar.css:1-10`](https://github.com/stevenfazzio/half-america/blob/7e197eb4ceccbc6f286ae27adbb37970a477ce8b/web/src/components/TabBar.css#L1-L10) - Centering pattern

## Architecture Insights

The project follows a consistent pattern for map overlays:
1. All overlays are siblings within `MapTab`, not children of the `<Map>` component
2. All use `position: fixed` with explicit `top`/`left`/`right`/`bottom`
3. All share `z-index: 1` except TabBar at `z-index: 10`
4. All use the same dark semi-transparent background: `rgba(30, 30, 30, 0.95)`
5. Responsive design uses `@media (max-width: 767px)` breakpoint

## Historical Context (from thoughts/)

- [`thoughts/shared/research/2025-11-23-ui-style-polish.md`](thoughts/shared/research/2025-11-23-ui-style-polish.md) - Original UX research recommending title overlay with specific design guidance

## Related Research

- [2025-11-23-ui-style-polish.md](2025-11-23-ui-style-polish.md) - Comprehensive UI polish research including title recommendations
- [2025-11-22-deck-gl-feasibility.md](2025-11-22-deck-gl-feasibility.md) - Map layer architecture

## Implementation Checklist

- [ ] Create `web/src/components/MapTitle.tsx`
- [ ] Create `web/src/components/MapTitle.css`
- [ ] Import and render `MapTitle` in `MapTab.tsx`
- [ ] Test on desktop (title visible below TabBar)
- [ ] Test on mobile (title hidden, SummaryPanel visible)
- [ ] Update ROADMAP.md to mark item complete

## Open Questions

1. **Dismissible?** Should users be able to dismiss/minimize the title after first view?
   - Recommendation: No, keep it simple. It's small enough not to be intrusive.

2. **Animation?** Should the title fade in after the map loads?
   - Recommendation: No animation needed. Consistent with other static overlays.
