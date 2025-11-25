# Info Icon Positioning Bug Fix (Issue #3) Implementation Plan

## Overview

Fix the info icon positioning bug in SummaryPanel where the icon appears near the title instead of next to the λ value. The root cause is an unscoped `.info-icon` CSS selector in LambdaSlider.css that leaks `position: absolute` to all elements with that class.

## Current State Analysis

### The Bug
- SummaryPanel's info icon visually appears near the "Half of America" title
- DOM inspection confirms the icon IS correctly placed inside `.technical-stats`
- `getComputedStyle()` shows `position: absolute` even though SummaryPanel.css doesn't define it

### Root Cause
`LambdaSlider.css:32-49` defines an unscoped `.info-icon` selector:
```css
.info-icon {
  position: absolute;
  top: 16px;
  right: 16px;
  /* ... */
}
```

This acts as a global style affecting ALL `.info-icon` elements. SummaryPanel.css defines `.summary-panel .info-icon` with higher specificity but doesn't override `position`, so the absolute positioning leaks through.

### Key Discoveries
- `web/src/components/LambdaSlider.css:32-49` - Unscoped `.info-icon` with `position: absolute`
- `web/src/components/LambdaSlider.css:51-57` - Unscoped `.info-icon:hover, .info-icon:focus`
- `web/src/components/LambdaSlider.css:59-62` - Unscoped `.info-icon:focus-visible`
- `web/src/components/SummaryPanel.css:33-48` - Scoped `.summary-panel .info-icon` (missing position override)

## Desired End State

- SummaryPanel info icon appears in the bottom-right corner next to "λ = 0.50"
- SummaryPanel tooltip appears above the technical-stats section (near bottom of panel)
- LambdaSlider info icon continues to appear in top-right corner of its panel
- LambdaSlider tooltip continues to work correctly
- No global CSS selectors for `.info-icon`

## What We're NOT Doing

- Adding defensive `position: static` to SummaryPanel.css (masks root cause)
- Renaming CSS classes (unnecessary churn)
- Refactoring to CSS modules or scoped styles (over-engineering)

## Implementation Approach

Scope all `.info-icon` selectors in LambdaSlider.css to `.lambda-slider .info-icon` to prevent style leakage to other components.

## Phase 1: Scope LambdaSlider CSS Selectors

### Overview
Change all unscoped `.info-icon` selectors in LambdaSlider.css to be scoped under `.lambda-slider`.

### Changes Required

#### 1. LambdaSlider.css
**File**: `web/src/components/LambdaSlider.css`

**Change 1**: Scope the main `.info-icon` selector (lines 32-49)

```css
/* Before */
.info-icon {
  position: absolute;
  top: 16px;
  right: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  padding: 0;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

/* After */
.lambda-slider .info-icon {
  position: absolute;
  top: 16px;
  right: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  padding: 0;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}
```

**Change 2**: Scope the hover/focus selectors (lines 51-57)

```css
/* Before */
.info-icon:hover,
.info-icon:focus {
  background: rgba(0, 114, 178, 0.2);
  border-color: rgba(0, 114, 178, 0.6);
  color: #0072B2;
  outline: none;
}

/* After */
.lambda-slider .info-icon:hover,
.lambda-slider .info-icon:focus {
  background: rgba(0, 114, 178, 0.2);
  border-color: rgba(0, 114, 178, 0.6);
  color: #0072B2;
  outline: none;
}
```

**Change 3**: Scope the focus-visible selector (lines 59-62)

```css
/* Before */
.info-icon:focus-visible {
  outline: 2px solid #0072B2;
  outline-offset: 2px;
}

/* After */
.lambda-slider .info-icon:focus-visible {
  outline: 2px solid #0072B2;
  outline-offset: 2px;
}
```

### Success Criteria

#### Automated Verification:
- [ ] Build succeeds: `cd web && npm run build`
- [ ] Lint passes: `cd web && npm run lint`
- [ ] No TypeScript errors (CSS changes only, but verify build)

#### Manual Verification:
- [ ] SummaryPanel info icon appears next to λ value (bottom-right of panel)
- [ ] SummaryPanel tooltip appears above the panel content (near bottom of screen)
- [ ] LambdaSlider info icon still appears in top-right corner of slider panel
- [ ] LambdaSlider tooltip still appears below the slider panel (desktop) / above (mobile)
- [ ] Hover/focus states work correctly on both info icons
- [ ] Test on mobile viewport (≤767px)

**Implementation Note**: After completing this phase and all automated verification passes, pause for manual confirmation that the visual positioning is correct before closing the issue.

---

## Testing Strategy

### Visual Testing Steps
1. Run dev server: `cd web && npm run dev`
2. Open browser to `http://localhost:5173`
3. **Desktop (≥768px)**:
   - Verify LambdaSlider panel in top-left with info icon in its top-right corner
   - Verify SummaryPanel in top-right with info icon next to "λ = X.XX" at bottom
   - Click each info icon and verify tooltip positioning
4. **Mobile (≤767px)**:
   - Resize browser or use DevTools device mode
   - Verify LambdaSlider at bottom with info icon in top-right of that panel
   - Verify SummaryPanel info icon visible and correctly positioned
   - Test tooltip positioning on mobile

### Edge Cases
- Rapid toggling of tooltips
- Keyboard navigation (Tab to info icon, Enter to activate)
- Focus states visible with keyboard navigation

## References

- GitHub Issue: https://github.com/stevenfazzio/half-america/issues/3
- Research document: `thoughts/shared/research/2025-11-25-issue-3-info-icon-positioning.md`
- LambdaSlider CSS: `web/src/components/LambdaSlider.css:32-62`
- SummaryPanel CSS: `web/src/components/SummaryPanel.css:33-61`
