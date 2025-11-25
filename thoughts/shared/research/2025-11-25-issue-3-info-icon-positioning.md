---
date: 2025-11-25T17:30:00-08:00
researcher: Claude
git_commit: 0debb03685b8964c81fd333cb1b5c2afa1b7ed10
branch: fix/3-info-icon-positioning
repository: half-america
topic: "Info icon in SummaryPanel has phantom absolute positioning"
tags: [research, codebase, css, bug, positioning, issue-3]
status: complete
last_updated: 2025-11-25
last_updated_by: Claude
---

# Research: Info Icon Positioning Bug (Issue #3)

**Date**: 2025-11-25T17:30:00-08:00
**Researcher**: Claude
**Git Commit**: 0debb03685b8964c81fd333cb1b5c2afa1b7ed10
**Branch**: fix/3-info-icon-positioning
**Repository**: half-america

## Research Question

Why does the info icon in SummaryPanel appear in the wrong position (near the title) when the DOM shows it's correctly placed inside `.technical-stats`, and why does `getComputedStyle()` show `position: absolute` when SummaryPanel.css doesn't define it?

## Summary

**Root Cause Found**: The bug is caused by a CSS specificity/cascade issue.

`LambdaSlider.css` defines an **unscoped** `.info-icon` selector with `position: absolute`, which acts as a global style affecting ALL elements with that class, including the info icon in SummaryPanel.

`SummaryPanel.css` defines `.summary-panel .info-icon` with higher specificity, but it does NOT override the `position` property, allowing the absolute positioning from LambdaSlider.css to leak through.

## Detailed Findings

### The Conflicting CSS Rules

**LambdaSlider.css:32-49** (unscoped selector - affects ALL `.info-icon` elements):
```css
.info-icon {
  position: absolute;    /* <-- THIS IS THE PROBLEM */
  top: 16px;
  right: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  /* ... other properties ... */
}
```

**SummaryPanel.css:33-48** (scoped selector - but missing position override):
```css
.summary-panel .info-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  /* ... other properties ... */
  /* NOTE: No `position` property defined! */
}
```

### CSS Cascade Behavior

1. `.info-icon` (specificity: 0,0,1,0) sets `position: absolute`
2. `.summary-panel .info-icon` (specificity: 0,0,2,0) overrides properties it defines
3. Since `.summary-panel .info-icon` doesn't define `position`, the value from `.info-icon` wins by default
4. Result: The SummaryPanel info icon gets `position: absolute; top: 16px; right: 16px;` from LambdaSlider.css

### Why the Icon Appears Near the Title

With `position: absolute; top: 16px; right: 16px;`:
- The icon is removed from normal document flow
- It positions relative to the nearest positioned ancestor (`.summary-panel` with `position: fixed`)
- It appears at top-right of the panel (16px from top, 16px from right)
- This visually places it near the "Half of America" title instead of next to the lambda value

### Related Tooltip Issue

The tooltip positioning problem mentioned in the issue is also explained:
- `.scope-tooltip` uses `position: absolute; bottom: 100%` to position above its parent
- But since the info icon is absolutely positioned at the top of `.summary-panel`, the tooltip appears above the panel (near where the icon actually renders)
- Expected: tooltip should appear above the `technical-stats` section at the bottom

## Code References

- `web/src/components/LambdaSlider.css:32-49` - Unscoped `.info-icon` with `position: absolute`
- `web/src/components/SummaryPanel.css:33-48` - Scoped `.summary-panel .info-icon` missing position override
- `web/src/components/SummaryPanel.css:64-78` - `.scope-tooltip` positioning
- `web/src/components/SummaryPanel.tsx:67-78` - Info icon JSX placement in DOM
- `web/src/components/SummaryPanel.tsx:81-98` - Tooltip JSX (sibling of `.technical-stats`)

## Architecture Insights

The codebase has two info icon implementations:
1. **LambdaSlider**: Icon intentionally positioned absolutely in top-right corner
2. **SummaryPanel**: Icon should flow inline with the lambda value

Both share the `.info-icon` class name but need different positioning strategies. The current implementation accidentally creates a global style from what should be a component-scoped style.

## Recommended Fixes

### Option A: Scope the LambdaSlider selector (Preferred)

Change `LambdaSlider.css` to use a scoped selector:

```css
/* Before */
.info-icon {
  position: absolute;
  ...
}

/* After */
.lambda-slider .info-icon {
  position: absolute;
  ...
}
```

**Pros**: Fixes the root cause, prevents future leakage
**Cons**: Need to update hover/focus selectors too

### Option B: Add explicit position to SummaryPanel

Add `position: static` to `SummaryPanel.css`:

```css
.summary-panel .info-icon {
  position: static;  /* Override the leaked absolute positioning */
  ...
}
```

**Pros**: Quick fix, minimal changes
**Cons**: Doesn't fix the root cause (global selector remains)

### Option C: Both (Most Thorough)

Apply both fixes:
1. Scope the LambdaSlider selectors
2. Add explicit position to SummaryPanel for defensive CSS

## Files Requiring Changes

| File | Change Required |
|------|-----------------|
| `web/src/components/LambdaSlider.css` | Scope `.info-icon` to `.lambda-slider .info-icon` |
| `web/src/components/SummaryPanel.css` | (Optional) Add `position: static` defensively |

## Testing Plan

1. Run dev server: `cd web && npm run dev`
2. Verify SummaryPanel info icon appears next to lambda value (bottom-right of panel)
3. Verify SummaryPanel tooltip appears above the panel (near bottom of panel)
4. Verify LambdaSlider info icon still appears in top-right corner
5. Verify LambdaSlider tooltip still appears below the slider panel
6. Test on mobile viewport (icon visibility, tooltip positioning)

## Open Questions

None - root cause identified and fix is straightforward.
