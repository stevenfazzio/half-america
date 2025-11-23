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

## Open Questions

1. **URL sync**: Should tabs sync to URL hash for shareability? (e.g., `#story`)
RESPONSE: Yes
2. **Map persistence**: Keep Map mounted when on other tabs, or unmount and remount?
3. **Loading state**: Should loading overlay show for all tabs or just Map?
RESPONSE: I think just Map, unless I'm misunderstanding the question. My interpretation is that you're asking whether we should show the loading screen if someone is going directly to the #story tab (as an example). I don't see why we should. If anything, we could either show the relevant content and load the map silently, or just load the map once the user has switched to the Map tab.
4. **Tab bar position**: Top fixed, or integrate with Map controls?
5. **Mobile UX**: Tabs as horizontal bar, bottom navigation, or hamburger menu?

## Implementation Checklist

- [ ] Create `TabBar.tsx` component with Map/Story/Method buttons
- [ ] Create `TabBar.css` with styling matching existing panels
- [ ] Extract current Map logic into `MapTab.tsx`
- [ ] Create `StoryTab.tsx` stub (placeholder content)
- [ ] Create `MethodTab.tsx` stub (placeholder content)
- [ ] Update `App.tsx` with tab state and conditional rendering
- [ ] Ensure TopoJSON loading persists across tab switches
- [ ] Add responsive styles for mobile tab navigation
- [ ] Test all tabs render correctly
