---
date: 2025-11-23T00:00:00-08:00
researcher: Claude
git_commit: 1b1e17d303539f33234073fbc480baf9210f97a2
branch: master
repository: half-america
topic: "Create tab structure with Map, Story, and Method stubs"
tags: [research, codebase, web-frontend, tabs, navigation, react]
status: complete
last_updated: 2025-11-23
last_updated_by: Claude
last_updated_note: "Investigated open questions for Map persistence, tab bar position, and mobile UX"
---

# Research: Create Tab Structure with Map, Story, and Method Stubs

**Date**: 2025-11-23
**Researcher**: Claude
**Git Commit**: 1b1e17d303539f33234073fbc480baf9210f97a2
**Branch**: master
**Repository**: half-america

## Research Question

How should we implement a tab structure with Map, Story, and Method tabs for the Half of America web frontend?

## Summary

The web frontend is currently a single-page application with no routing or navigation. The tab strategy is well-documented in `docs/tab_strategy.md`. Implementation requires:

1. **No routing library is installed** - Simple React state-based tabs are recommended (no URL routing needed for this use case)
2. **Current structure is monolithic** - App.tsx contains all logic for the Map view
3. **Styling approach is plain CSS** - Component-scoped CSS files with dark theme
4. **Clear design guidance exists** - Tab names, content strategy, and voice documented

**Recommended approach**: State-based tabs with the Map view as default, Story and Method as stub placeholders.

## Detailed Findings

### Current Frontend Architecture

**App.tsx Structure** (`web/src/App.tsx`):
```
<div className="app">
  <Map>                          // MapLibre GL (100vw x 100vh)
    <DeckGLOverlay layers={...}/>
  </Map>
  <LambdaSlider />               // Floating control
  <SummaryPanel />               // Floating stats panel
</div>
```

**Component Files**:
| Component | Purpose |
|-----------|---------|
| `DeckGLOverlay.tsx` | Bridges deck.gl with MapLibre |
| `LambdaSlider.tsx` | Surface tension slider control |
| `SummaryPanel.tsx` | Statistics display panel |
| `LoadingOverlay.tsx` | Full-screen loading state |
| `ErrorOverlay.tsx` | Error display with retry |

**Dependencies** (no UI library):
- React 19.2.0
- react-map-gl 8.1.0, maplibre-gl 5.13.0
- deck.gl 9.2.2
- topojson-client 3.1.0

### Tab Strategy (from docs/tab_strategy.md)

**Three audiences**:
1. **Explorers** → want to see and play (Map tab)
2. **General-curious** → want approachable story (Story tab)
3. **Technical evaluators** → want rigor, reproducibility (Method tab)

**Tab specifications**:

| Tab | Name | Focus | Voice |
|-----|------|-------|-------|
| 1 | Map | Immersive visualization, minimal chrome | Minimal, confident, terse |
| 2 | Story | Teach intuition without math | Clear, pedagogical, confident |
| 3 | Method | Replicate, critique, extend | Precise, formal, modest |

**Key design principle**: "The first tab should feel like *the point of the site*. The other two should feel supportive."

### Styling Patterns

**Color palette**:
- Background: `#1a1a1a`
- Primary text: `rgba(255, 255, 255, 0.87)`
- Secondary text: `rgba(255, 255, 255, 0.7)`
- Accent (Okabe-Ito Blue): `#0072B2`
- Panel background: `rgba(30, 30, 30, 0.95)`

**Panel pattern** (used by LambdaSlider, SummaryPanel):
```css
position: fixed;
padding: 16px;
background: rgba(30, 30, 30, 0.95);
border-radius: 8px;
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
z-index: 1;
color: #fff;
```

**Responsive**: Single breakpoint at `768px` (mobile/desktop)

### Implementation Options

| Approach | Pros | Cons |
|----------|------|------|
| **React state tabs** | Simple, no dependencies, fast | No URL sharing |
| **Hash routing** (`#map`, `#story`) | Shareable URLs, no library | Manual implementation |
| **react-router-dom** | Full routing features | Overkill for 3 tabs, new dependency |

**Recommendation**: React state-based tabs with optional hash sync later.

## Code References

- `web/src/App.tsx` - Main application component to refactor
- `web/src/App.css` - App container styles
- `web/src/index.css` - Global styles and CSS variables
- `web/src/components/LambdaSlider.css:7-12` - Panel styling pattern
- `web/src/components/SummaryPanel.css:6-12` - Panel styling pattern
- `docs/tab_strategy.md` - Tab strategy and content guidance
- `METHODOLOGY.md` - Content source for Method tab

## Architecture Insights

### Recommended Implementation Structure

```
web/src/
├── App.tsx                    # Tab state + conditional rendering
├── App.css                    # Add tab bar styles
├── components/
│   ├── TabBar.tsx             # NEW: Tab navigation component
│   ├── TabBar.css             # NEW: Tab bar styles
│   ├── MapTab.tsx             # NEW: Extract current map logic
│   ├── StoryTab.tsx           # NEW: Stub placeholder
│   ├── StoryTab.css           # NEW
│   ├── MethodTab.tsx          # NEW: Stub placeholder
│   ├── MethodTab.css          # NEW
│   └── ... (existing)
```

### Tab Bar Design

Position: Top of viewport, minimal height
Style: Match existing panel pattern (semi-transparent dark background)

```tsx
// Conceptual TabBar structure
<nav className="tab-bar">
  <button className={active === 'map' ? 'active' : ''}>Map</button>
  <button className={active === 'story' ? 'active' : ''}>Story</button>
  <button className={active === 'method' ? 'active' : ''}>Method</button>
</nav>
```

### State Management

```tsx
// In App.tsx
type TabId = 'map' | 'story' | 'method';
const [activeTab, setActiveTab] = useState<TabId>('map');

// Conditional rendering
{activeTab === 'map' && <MapTab />}
{activeTab === 'story' && <StoryTab />}
{activeTab === 'method' && <MethodTab />}
```

### Map Tab Considerations

The Map tab needs special handling because:
1. TopoJSON loading should happen once (not on every tab switch)
2. Map state should persist when switching away and back
3. deck.gl layers are expensive to recreate

**Solution**: Keep Map mounted but hidden, or lift loading state to App level.

## Historical Context (from thoughts/)

No prior research on tabs found in thoughts/ directory. This is a greenfield implementation guided by `docs/tab_strategy.md`.

## Related Research

- `thoughts/shared/research/2025-11-22-deck-gl-feasibility.md` - deck.gl integration research

## Investigated Questions

### 1. URL sync: Should tabs sync to URL hash for shareability?

**User Response**: Yes

**Implementation**: Use hash routing (`#map`, `#story`, `#method`) with the Map tab as default when no hash is present.

---

### 2. Map persistence: Keep Map mounted when on other tabs, or unmount and remount?

**Investigation Summary**

Using `display: none` on deck.gl components causes severe issues (infinite resize loops, WebGL warnings). The recommended approach is a "KeepMounted" pattern with `visibility: collapse`.

**Options Analysis**

| Option | Pros | Cons |
|--------|------|------|
| **Conditional render** | Lower memory when hidden, clean initial load | Loses all state, expensive to recreate WebGL resources |
| **display: none** | Preserves state, simple | **Breaks deck.gl** - causes infinite resize loops |
| **visibility: collapse** | Preserves state, deck.gl compatible | Mounts at startup even if never accessed |
| **KeepMounted + visibility** | Lazy init + state persistence | Slightly more complex |

**Recommendation**: Use **KeepMounted pattern with `visibility: collapse`**

```tsx
// hooks/useKeepMounted.ts
export function useKeepMounted(isActive: boolean) {
  const [hasBeenMounted, setHasBeenMounted] = useState(false);
  useEffect(() => {
    if (isActive && !hasBeenMounted) setHasBeenMounted(true);
  }, [isActive, hasBeenMounted]);
  return { shouldRender: hasBeenMounted, isVisible: isActive };
}

// Usage in MapTab
function MapTab({ isActive }: { isActive: boolean }) {
  const { shouldRender, isVisible } = useKeepMounted(isActive);
  const mapRef = useRef<MapRef>(null);

  useEffect(() => {
    if (isVisible && mapRef.current) {
      requestAnimationFrame(() => mapRef.current?.resize());
    }
  }, [isVisible]);

  if (!shouldRender) return null;

  return (
    <div style={{ visibility: isVisible ? 'visible' : 'collapse' }}>
      <Map ref={mapRef} ... />
    </div>
  );
}
```

**Key implementation notes**:
- Use `visibility: collapse` not `display: none`
- Call `map.resize()` after showing the map
- Move TopoJSON loading to trigger on first Map tab access

---

### 3. Loading state: Should loading overlay show for all tabs or just Map?

**User Response**: Just Map tab.

**Implementation**: Show loading overlay only when Map tab is active AND data is loading. If user navigates directly to `#story`, show Story content immediately and load Map data in background (or defer until Map tab is accessed).

---

### 4. Tab bar position: Top fixed, or integrate with Map controls?

**Investigation Summary**

Analyzed current control positioning (LambdaSlider top-left, SummaryPanel top-right) and evaluated options for tab placement that fits the "immersive, minimal chrome" design goal.

**Options Analysis**

| Option | Minimal Chrome | Discoverability | Integration Effort |
|--------|---------------|-----------------|-------------------|
| Top center bar | Medium | High | Low |
| Integrate with slider | Low | Medium | High |
| Top-left stack | Medium | Medium | Medium |
| **Ultra-minimal pills (top center)** | **High** | Low-Medium | Low |
| Bottom nav | Low | High | Medium |

**Recommendation**: **Ultra-minimal floating pills at top center**

```css
.tab-bar {
  position: fixed;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
  z-index: 1;
}
.tab-button {
  background: transparent;
  color: rgba(255, 255, 255, 0.5);
  border: none;
  padding: 6px 12px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.tab-button:hover { color: rgba(255, 255, 255, 0.9); }
.tab-button.active {
  color: #fff;
  background: rgba(30, 30, 30, 0.7);
  border-radius: 4px;
}
```

**Rationale**: Maximizes map visibility, matches "immersive" design goal, does not require repositioning existing controls. Tabs feel like navigation metadata rather than competing chrome.

**Fallback**: If user testing reveals pills are too subtle, use standard panel-styled top center bar.

---

### 5. Mobile UX: Tabs as horizontal bar, bottom navigation, or hamburger menu?

**Investigation Summary**

Research strongly favors visible navigation over hamburger menus (20%+ drop in discoverability). Thumb zone research shows bottom navigation is most accessible for one-handed mobile use.

**Options Analysis**

| Option | Thumb Reachability | Discoverability | Conflict with Slider |
|--------|-------------------|-----------------|---------------------|
| Top horizontal | Poor (stretch zone) | High | None |
| **Bottom nav bar** | **Excellent** | **High** | Requires adjustment |
| Hamburger menu | N/A (2 taps) | Poor (-20%) | None |
| FAB menu | Good | Medium | Minimal |

**Recommendation**: **Compact bottom navigation bar**

```
Mobile Layout:
+---------------------------+
|        FULL SCREEN        |
|           MAP             |
+---------------------------+
|    [LambdaSlider]         |  <- bottom: ~110px (Map tab only)
+---------------------------+
| [Map]  [Story]  [Method]  |  <- bottom: 0, height: ~50px
+---------------------------+
```

```css
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 50px;
  display: flex;
  justify-content: space-around;
  align-items: center;
  background: rgba(30, 30, 30, 0.95);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 10;
  padding-bottom: env(safe-area-inset-bottom);
}
```

**Key adjustments**:
- Move LambdaSlider to `bottom: 110px` on mobile
- Hide LambdaSlider on Story/Method tabs
- Use `env(safe-area-inset-bottom)` for iOS notch safety

**Research sources**: Nielsen Norman Group, Smashing Magazine, Google Maps Platform

## Open Questions

No remaining open questions.

## Implementation Checklist

- [ ] Create `useKeepMounted.ts` hook for lazy mount + state persistence
- [ ] Create `TabBar.tsx` component with ultra-minimal pill styling (desktop)
- [ ] Create `TabBar.css` with desktop (top center pills) and mobile (bottom nav) styles
- [ ] Extract current Map logic into `MapTab.tsx` with KeepMounted pattern
- [ ] Add `map.resize()` call when Map tab becomes visible
- [ ] Create `StoryTab.tsx` stub (placeholder content)
- [ ] Create `MethodTab.tsx` stub (placeholder content)
- [ ] Update `App.tsx` with tab state, hash routing, and conditional rendering
- [ ] Modify `useTopoJsonLoader` to support lazy loading on first Map tab access
- [ ] Move loading overlay logic to only show when Map tab active + loading
- [ ] Adjust LambdaSlider mobile position to `bottom: 110px`
- [ ] Hide LambdaSlider/SummaryPanel on non-Map tabs
- [ ] Add `env(safe-area-inset-bottom)` for iOS notch safety
- [ ] Test all tabs render correctly with hash navigation
