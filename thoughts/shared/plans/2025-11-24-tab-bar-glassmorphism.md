# Tab Bar Glassmorphism Implementation Plan

## Overview

Add glassmorphism (backdrop-filter blur) to the desktop tab bar for improved visibility against varying map backgrounds. This is a CSS-only change that adds a frosted glass effect to make tabs consistently visible regardless of underlying map content.

## Current State Analysis

**File**: `web/src/components/TabBar.css`

The desktop tab bar currently has no container background - tabs are floating text that can be hard to see against lighter map areas:

```css
.tab-bar {
  /* NO background - completely transparent */
}
.tab-button {
  color: rgba(255, 255, 255, 0.5);  /* 50% opacity - hard to see */
}
```

### Key Discoveries:
- No `backdrop-filter` usage exists in the codebase - this will be the first use
- Mobile tab bar already has solid `rgba(30, 30, 30, 0.95)` background (no glassmorphism needed)
- All other UI panels use 95% opacity dark backgrounds (`SummaryPanel`, `MapTitle`, `LambdaSlider`)
- Current 50% opacity inactive text fails WCAG visibility guidelines

## Desired End State

After implementation:
- Desktop tab bar has a frosted glass container with 12px blur
- Inactive tabs are visible at 70% opacity (up from 50%)
- Container has subtle border for edge definition
- Hover and active states provide clear visual feedback
- Mobile tab bar remains unchanged (solid background)

### Verification:
1. Desktop: Tab bar is visible over both light and dark map areas
2. Desktop: Hover shows subtle background highlight
3. Desktop: Active tab is clearly distinguishable
4. Mobile: Tab bar unchanged from current behavior
5. Safari: Glassmorphism works (webkit prefix applied)

## What We're NOT Doing

- Adding glassmorphism to other panels (SummaryPanel, MapTitle, LambdaSlider)
- Adding JavaScript changes
- Modifying TabBar.tsx component
- Changing mobile tab bar styling (beyond resetting inherited glassmorphism)

## Implementation Approach

Single CSS file modification with desktop-first changes and mobile query resets. The changes follow the existing pattern of dark gray (`rgb(30, 30, 30)`) at reduced opacity for containers.

## Phase 1: Desktop Glassmorphism Styles

### Overview
Add glassmorphism container and improve button visibility for desktop tab bar.

### Changes Required:

#### 1. Desktop Tab Bar Container
**File**: `web/src/components/TabBar.css`
**Lines**: 1-10

Replace the `.tab-bar` rule:

```css
/* Desktop: Ultra-minimal floating pills at top center */
.tab-bar {
  position: fixed;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 4px;
  z-index: 10;

  /* Glassmorphism container */
  background: rgba(30, 30, 30, 0.5);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 4px;
}
```

**Key changes:**
| Property | Old | New | Reason |
|----------|-----|-----|--------|
| `background` | none | `rgba(30, 30, 30, 0.5)` | Visual grounding |
| `backdrop-filter` | none | `blur(12px)` | Glassmorphism effect |
| `-webkit-backdrop-filter` | none | `blur(12px)` | Safari support |
| `border-radius` | none | `8px` | Match other panels |
| `border` | none | `1px solid rgba(255, 255, 255, 0.1)` | Edge definition |
| `padding` | none | `4px` | Space around buttons |
| `gap` | `8px` | `4px` | Tighter grouping (padding provides space) |

#### 2. Tab Button Styles
**File**: `web/src/components/TabBar.css`
**Lines**: 12-23

Replace the `.tab-button` rule:

```css
.tab-button {
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  border: none;
  padding: 6px 12px;
  font-size: 12px;
  font-family: inherit;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: color 0.15s ease, background 0.15s ease;
  border-radius: 4px;
}
```

**Key changes:**
| Property | Old | New | Reason |
|----------|-----|-----|--------|
| `color` | `rgba(255, 255, 255, 0.5)` | `rgba(255, 255, 255, 0.7)` | Better visibility |
| `border-radius` | none | `4px` | Rounded corners for hover state |

#### 3. Hover State
**File**: `web/src/components/TabBar.css`
**Lines**: 25-27

Replace the `.tab-button:hover` rule:

```css
.tab-button:hover {
  color: rgba(255, 255, 255, 0.95);
  background: rgba(255, 255, 255, 0.1);
}
```

**Key changes:**
| Property | Old | New | Reason |
|----------|-----|-----|--------|
| `color` | `rgba(255, 255, 255, 0.9)` | `rgba(255, 255, 255, 0.95)` | Slightly brighter |
| `background` | none | `rgba(255, 255, 255, 0.1)` | Hover feedback |

#### 4. Active State
**File**: `web/src/components/TabBar.css`
**Lines**: 29-33

Replace the `.tab-button.active` rule:

```css
.tab-button.active {
  color: #fff;
  background: rgba(255, 255, 255, 0.15);
  font-weight: 600;
}
```

**Key changes:**
| Property | Old | New | Reason |
|----------|-----|-----|--------|
| `background` | `rgba(30, 30, 30, 0.7)` | `rgba(255, 255, 255, 0.15)` | Lighter, more visible |
| `border-radius` | `4px` | (removed - inherited from `.tab-button`) | Cleaner |
| `font-weight` | normal | `600` | Added emphasis |

---

## Phase 2: Mobile Media Query Resets

### Overview
Reset glassmorphism properties in mobile media query to maintain existing solid background behavior.

### Changes Required:

#### 1. Mobile Tab Bar Reset
**File**: `web/src/components/TabBar.css`
**Lines**: 35-50

Replace the mobile `.tab-bar` rule:

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
```

**New resets added:**
- `backdrop-filter: none` - Remove blur effect
- `-webkit-backdrop-filter: none` - Remove Safari blur
- `border-radius: 0` - Square corners for edge-to-edge
- `border: none` - Remove container border (separate border-top below)
- `padding: 0` - Remove container padding

#### 2. Mobile Tab Button Reset
**File**: `web/src/components/TabBar.css`
**Lines**: 52-60

Replace the mobile `.tab-button` rule:

```css
  .tab-button {
    flex: 1;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    padding: 0;
    border-radius: 0;
    font-weight: normal;
  }
```

**New resets added:**
- `border-radius: 0` - Square corners for mobile
- `font-weight: normal` - Reset from desktop's 600 weight

#### 3. Mobile Active State Reset
**File**: `web/src/components/TabBar.css`
**Lines**: 62-65

Ensure the mobile active state resets font-weight:

```css
  .tab-button.active {
    background: transparent;
    color: #0072B2;
    font-weight: normal;
  }
}
```

---

## Complete Final CSS

For reference, here is the complete final `TabBar.css`:

```css
/* Desktop: Ultra-minimal floating pills at top center */
.tab-bar {
  position: fixed;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 4px;
  z-index: 10;

  /* Glassmorphism container */
  background: rgba(30, 30, 30, 0.5);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 4px;
}

.tab-button {
  background: transparent;
  color: rgba(255, 255, 255, 0.7);
  border: none;
  padding: 6px 12px;
  font-size: 12px;
  font-family: inherit;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: color 0.15s ease, background 0.15s ease;
  border-radius: 4px;
}

.tab-button:hover {
  color: rgba(255, 255, 255, 0.95);
  background: rgba(255, 255, 255, 0.1);
}

.tab-button.active {
  color: #fff;
  background: rgba(255, 255, 255, 0.15);
  font-weight: 600;
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
    font-weight: normal;
  }

  .tab-button.active {
    background: transparent;
    color: #0072B2;
    font-weight: normal;
  }
}
```

---

## Testing Strategy

### Automated Verification:
- [ ] Build succeeds: `cd web && npm run build`
- [ ] Lint passes: `cd web && npm run lint`
- [ ] Dev server starts: `cd web && npm run dev`

### Manual Verification:
- [ ] **Desktop - Light map area**: Tab bar visible over suburban/light colored map regions
- [ ] **Desktop - Dark map area**: Tab bar visible over urban/dark colored map regions
- [ ] **Desktop - Hover state**: Subtle background highlight appears on hover
- [ ] **Desktop - Active state**: Active tab clearly distinguishable with white text and light background
- [ ] **Desktop - Blur effect**: Frosted glass effect visible (map content blurs through)
- [ ] **Mobile - Unchanged**: Bottom nav bar remains solid dark background with blue active state
- [ ] **Safari**: Glassmorphism works correctly (test webkit prefix)
- [ ] **Fallback**: If blur unsupported, semi-transparent background still provides visibility

---

## Performance Considerations

`backdrop-filter` can be GPU-intensive on some devices. However:
- The tab bar is small (only ~200px wide)
- Only applied on desktop (mobile uses solid background)
- 96%+ browser support means most users have hardware acceleration

No performance issues expected.

---

## References

- Research: `thoughts/shared/research/2025-11-24-tab-bar-glassmorphism.md`
- Related: `thoughts/shared/research/2025-11-23-ui-style-polish.md` (item 5)
- Tab implementation: `thoughts/shared/plans/2025-11-23-tab-structure-implementation.md`
