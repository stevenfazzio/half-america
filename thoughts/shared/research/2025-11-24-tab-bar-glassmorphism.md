---
date: 2025-11-24T10:00:00-08:00
researcher: Claude
git_commit: 65ac8c9
branch: master
repository: half-america
topic: "Tab Bar Glassmorphism Container for Desktop Visibility"
tags: [research, ui, css, glassmorphism, backdrop-filter, tab-bar, desktop]
status: complete
last_updated: 2025-11-24
last_updated_by: Claude
---

# Research: Tab Bar Glassmorphism Container for Desktop Visibility

**Date**: 2025-11-24T10:00:00-08:00
**Researcher**: Claude
**Git Commit**: 65ac8c9
**Branch**: master
**Repository**: half-america

## Research Question

How should we implement glassmorphism (backdrop-filter blur) on the desktop tab bar to improve visibility against varying map backgrounds?

## Summary

The desktop tab bar currently has no container background, making it difficult to see against varying map content. Adding a glassmorphism container with `backdrop-filter: blur()` will provide visual "grounding" while maintaining the minimal aesthetic. This will be the **first use of backdrop-filter** in the codebase.

| Aspect | Current State | Recommended Change |
|--------|---------------|-------------------|
| Container background | None (transparent) | `rgba(30, 30, 30, 0.5)` with blur |
| Inactive tab text | `rgba(255, 255, 255, 0.5)` | `rgba(255, 255, 255, 0.7)` |
| Container border | None | `1px solid rgba(255, 255, 255, 0.1)` |
| Backdrop blur | None | `blur(12px)` |
| Scope | Desktop only | Desktop only (mobile already has solid bg) |

## Detailed Findings

### 1. Current TabBar Desktop Styling

**File**: `web/src/components/TabBar.css`

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
  /* NO background - completely transparent */
}

.tab-button {
  background: transparent;
  color: rgba(255, 255, 255, 0.5);  /* 50% opacity - hard to see */
  /* ... */
}

.tab-button.active {
  color: #fff;
  background: rgba(30, 30, 30, 0.7);  /* Only active has background */
  border-radius: 4px;
}
```

**Problem**: Desktop tabs are floating text with no visual container. Against varying map tiles (especially over lighter areas like suburban regions), the 50% opacity white text can be nearly invisible.

### 2. Mobile TabBar Already Has Solid Background

```css
@media (max-width: 767px) {
  .tab-bar {
    /* ... */
    background: rgba(30, 30, 30, 0.95);  /* Solid dark background */
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }
}
```

Mobile doesn't need glassmorphism because it already has a solid, near-opaque background.

### 3. Existing Container Patterns in Codebase

**No backdrop-filter usage exists in the codebase**. All UI containers use solid semi-transparent backgrounds:

| Component | Background |
|-----------|------------|
| SummaryPanel | `rgba(30, 30, 30, 0.95)` |
| MapTitle | `rgba(30, 30, 30, 0.95)` |
| LambdaSlider | `rgba(30, 30, 30, 0.95)` |
| Mobile TabBar | `rgba(30, 30, 30, 0.95)` |
| Active tab button | `rgba(30, 30, 30, 0.7)` |

**Pattern**: Dark gray `rgb(30, 30, 30)` at 95% opacity is the standard container color.

### 4. Glassmorphism Design Considerations

**Why glassmorphism for the tab bar specifically:**
- Tab bar overlays the map directly (unlike SummaryPanel which has solid content below it)
- Need to see map content "through" the tabs for context
- Ultra-minimal aesthetic calls for blur rather than opaque blocking
- Creates subtle "floating glass" effect that aligns with modern design trends

**Why NOT glassmorphism for other panels:**
- SummaryPanel, LambdaSlider, MapTitle are informational panels that benefit from high contrast
- They don't need the map visible behind them
- The current 95% opacity provides good readability

### 5. Browser Support for backdrop-filter

`backdrop-filter` has excellent modern browser support (96%+ global coverage), but requires webkit prefix for Safari:

```css
backdrop-filter: blur(12px);
-webkit-backdrop-filter: blur(12px);  /* Safari support */
```

**Fallback**: If backdrop-filter is unsupported, the `rgba(30, 30, 30, 0.5)` background still provides some visibility improvement.

### 6. Accessibility Considerations

Per NN/g research: "Unselected tabs must remain visible to remind users of available options."

Current 50% opacity fails this test. WCAG requires 4.5:1 contrast for normal text. Recommendations:
- Increase inactive text to 70% opacity
- Add background container for guaranteed contrast
- Ensure the blur amount doesn't affect text legibility

## Recommended CSS Implementation

**Desktop-only changes** (add before the mobile media query):

```css
/* Desktop: Glassmorphism container for visibility */
.tab-bar {
  position: fixed;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 4px;  /* Reduced from 8px - buttons have own padding */
  z-index: 10;

  /* NEW: Glassmorphism container */
  background: rgba(30, 30, 30, 0.5);  /* Semi-transparent dark */
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);  /* Safari */
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 4px;
}

.tab-button {
  background: transparent;
  color: rgba(255, 255, 255, 0.7);  /* Increased from 0.5 */
  border: none;
  padding: 6px 12px;
  font-size: 12px;
  font-family: inherit;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: color 0.15s ease, background 0.15s ease;
  border-radius: 4px;  /* Add radius for hover state */
}

.tab-button:hover {
  color: rgba(255, 255, 255, 0.95);
  background: rgba(255, 255, 255, 0.1);  /* Subtle hover background */
}

.tab-button.active {
  color: #fff;
  background: rgba(255, 255, 255, 0.15);  /* Lighter than hover */
  font-weight: 600;  /* Add weight for emphasis */
}
```

### Key Changes Summary

| Property | Old Value | New Value | Reason |
|----------|-----------|-----------|--------|
| `.tab-bar` background | none | `rgba(30, 30, 30, 0.5)` | Visual grounding |
| `.tab-bar` backdrop-filter | none | `blur(12px)` | Glassmorphism effect |
| `.tab-bar` border | none | `1px solid rgba(255, 255, 255, 0.1)` | Edge definition |
| `.tab-bar` padding | none | `4px` | Space around buttons |
| `.tab-bar` border-radius | none | `8px` | Match other panels |
| `.tab-bar` gap | `8px` | `4px` | Tighter grouping |
| `.tab-button` color | `rgba(255, 255, 255, 0.5)` | `rgba(255, 255, 255, 0.7)` | Better visibility |
| `.tab-button:hover` bg | none | `rgba(255, 255, 255, 0.1)` | Hover feedback |
| `.tab-button.active` bg | `rgba(30, 30, 30, 0.7)` | `rgba(255, 255, 255, 0.15)` | Lighter, more visible |
| `.tab-button.active` weight | normal | `600` | Emphasis |

## Mobile Media Query Adjustments

The mobile query needs to **reset** the desktop glassmorphism properties:

```css
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

    /* Reset glassmorphism for mobile's solid background */
    background: rgba(30, 30, 30, 0.95);
    backdrop-filter: none;
    -webkit-backdrop-filter: none;
    border-radius: 0;
    border: none;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    padding: 0;
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
    border-radius: 0;
    font-weight: normal;  /* Reset weight */
  }

  .tab-button.active {
    background: transparent;
    color: #0072B2;
    font-weight: normal;
  }
}
```

## Visual Comparison

**Before (current):**
```
          Map  Story  Method          ← Floating text, no container
         (hard to see on light map)
```

**After (glassmorphism):**
```
        ╭─────────────────────────╮
        │  Map  Story  Method     │   ← Blurred glass container
        ╰─────────────────────────╯
            (always visible)
```

## Code References

- `web/src/components/TabBar.css:1-33` - Desktop styles to modify
- `web/src/components/TabBar.css:36-66` - Mobile styles to adjust
- `web/src/components/SummaryPanel.css:1-12` - Reference container pattern
- `web/src/components/MapTitle.css:1-13` - Reference container pattern

## Implementation Notes

1. **Order matters**: Define desktop styles first, then override in mobile media query
2. **Webkit prefix**: Required for Safari compatibility
3. **Fallback**: The semi-transparent background provides fallback if blur unsupported
4. **No JavaScript changes**: Pure CSS modification
5. **Testing**: Check on both light and dark map areas to verify visibility improvement

## Related Research

- [2025-11-23-ui-style-polish.md](2025-11-23-ui-style-polish.md) - Original research identifying this issue (item 5)
- [2025-11-23-tab-structure-implementation.md](../plans/2025-11-23-tab-structure-implementation.md) - Tab navigation design

## Open Questions

None - this is a straightforward CSS enhancement with clear implementation path.
