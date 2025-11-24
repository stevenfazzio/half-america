---
date: 2025-11-23T12:00:00-08:00
researcher: Claude
git_commit: e589922a0021eda434314c05e92a482097d098d8
branch: master
repository: half-america
topic: "UI Style and Polish Research"
tags: [research, ui, ux, design, visualization, map, slider, legend, tooltips]
status: complete
last_updated: 2025-11-23
last_updated_by: Claude
---

# Research: UI Style and Polish

**Date**: 2025-11-23T12:00:00-08:00
**Researcher**: Claude
**Git Commit**: e589922a0021eda434314c05e92a482097d098d8
**Branch**: master
**Repository**: half-america

## Research Question

The user requested comprehensive research on UI style and polish improvements for the Half of America visualization, covering:
1. Map title/subtitle clarity and placement
2. Slider UX for showing range extremes
3. Hover tooltip content for regions
4. Legend design and metric ordering
5. Tab bar visibility on desktop
6. Population fraction data analysis
7. Lambda range and high-value behavior
8. Lambda decimal precision bug

## Summary

This research synthesizes findings from UX best practices, data visualization style guides (Urban Institute, NYT Graphics, The Pudding), design systems (Material Design, Apple HIG), and population data analysis. Key findings:

| Issue | Finding | Recommendation |
|-------|---------|----------------|
| Map clarity | 85% of users won't interact; title in corner is insufficient | Add prominent title overlay: "Half of America / Where 50% of Americans live" |
| Slider extremes | Status quo bias prevents exploration from "balanced" default | Add static endpoint labels: "Fragmented" ← → "Smooth" |
| Hover tooltips | Support the narrative (population concentration) | Show: Population, Area, Density. Skip: tract count, perimeter |
| Legend format | Units after value is preferred | "42,902 mi²" not "Area (mi²): 42,902" |
| Tab visibility | 50% opacity insufficient on desktop | Add glassmorphism container with backdrop-filter blur |
| Population data | 81/99 values below 50%, range 48.59%-50.45% | Consider algorithm tweak to bias toward ≥50% |
| Lambda range | λ=0.98 has 48.71% (lowest), λ=0.97 has 50.26% | Consider capping slider at λ=0.97 or λ=0.96 |
| Lambda precision | Legend shows 1 decimal, slider supports 2 | Fix: `lambda.toFixed(2)` in SummaryPanel |

## Detailed Findings

### 1. Map Title/Subtitle Clarity

**Current State**: "Half of America" only appears in the top-right legend panel at 16px font size.

**Problem**: Per NYT Graphics Director Archie Tse, "only 10-15% of users click on interactive elements" and "if you make a tooltip or rollover, assume no one will ever see it." Critical context must be visible by default.

**Research Sources**:
- Urban Institute Style Guide: Titles should be left-aligned at top, active/storytelling language
- ProPublica: "The most important editorial element should be the most noticeable thing on the page"
- The Pudding (Human Terrain): Uses large title + subtitle + hook statement before map

**Recommendations** (prioritized):

1. **Option A: Title Overlay (Recommended)**
   - Semi-transparent header at top of viewport
   - Title: "Half of America" (24-32px, bold)
   - Subtitle: "Where 50% of Americans live" (16-18px)
   - Style: `rgba(30, 30, 30, 0.9)` background

2. **Option B: Hero Introduction Screen**
   - First-visit modal with explanation
   - "Explore Map" button to dismiss
   - Use localStorage to show only once

3. **Option C: Promote Panel Text**
   - Make title larger in existing panel
   - Add one-line explanation below

### 2. Slider Endpoint Labels

**Current State**: Dynamic microcopy shows only current position:
- `value < 0.3`: "Minimizes area (more fragmented)"
- `value > 0.7`: "Minimizes perimeter (smoother shapes)"
- Middle: "Balanced optimization"

**Problem**: Status quo bias and anchoring bias make users reluctant to explore from "balanced" default. Users face a "guessing game" without knowing what the extremes offer.

**Research Sources**:
- Smashing Magazine: "The ranges should be clearly labelled" - use dual display
- Material Design: "Place icons at both ends to reflect value intensity"
- Apple HIG: Supports endpoint icons for min/max
- Carbon Design: "Min and max value text indicate a slider's minimum and maximum value range"

**Recommendation**: Add static endpoint labels + keep dynamic microcopy:

```
Surface Tension (λ)

Fragmented ─────────────●───────────── Smooth
                        ↑
                       0.50
              Balanced optimization
```

Implementation:
```jsx
<div className="slider-extremes">
  <span className="extreme-left">Fragmented</span>
  <span className="extreme-right">Smooth</span>
</div>
```

### 3. Hover Tooltip Content

**Current State**: `autoHighlight: true` with `highlightColor` but no tooltip content.

**Problem**: Users hovering over regions have no information about what they're looking at.

**Research Sources**:
- Datawrapper: Tooltips serve orientation, transparency, and explanation
- LogRocket: "Concise, direct, and in clear, simple language"
- Leaflet Choropleth: Uses fixed info panel that updates on hover

**Recommended Tooltip Content** (priority order):

| Priority | Metric | Why |
|----------|--------|-----|
| 1 | Population | Core story - "X million people live here" |
| 2 | Area | Geographic concentration contrast |
| 3 | Density | Derived insight that synthesizes the story |

**Skip**: Number of tracts (implementation detail), perimeter (algorithm artifact), lambda/mu values (technical)

**Recommended Format**:
```
Metro NYC Region
━━━━━━━━━━━━━━━━━━
8.3 million people
12,400 per sq mi

Area: 670 sq mi
```

**Implementation Note**: Consider fixed info panel (Leaflet pattern) instead of cursor-following tooltip for large regions.

### 4. Legend Design

**Current State**:
```jsx
<dl className="summary-stats">
  <dt>Population</dt><dd>{populationPercent}%</dd>
  <dt>Area</dt><dd>{areaSqMiles} mi²</dd>
  <dt>Regions</dt><dd>{props.num_parts}</dd>
  <dt>Area/Region</dt><dd>{areaPerRegion} mi²</dd>
  <dt>Lambda (λ)</dt><dd>{lambda.toFixed(1)}</dd>  // BUG: should be .toFixed(2)
</dl>
```

**Unit Formatting**: Urban Institute: "Unit of measurement should be mentioned only once"
- **Preferred**: `42,902 mi²` (value with unit inline)
- **Avoid**: `Area (mi²): 42,902` (adds visual noise)

**Metric Ordering**: Lead with story metric, then supporting metrics:
1. Population % (hero metric - should be visually prominent)
2. Area
3. Regions
4. Area/Region (derived)
5. Lambda (consider hiding or "Advanced" section)

**Population % Styling**: As the key takeaway, should have:
- Larger font size (2-3x other metrics)
- Possibly accent color
- Format as `50%` not `50.0%`

**Recommended Layout**:
```
┌──────────────────────────┐
│  50%                     │  ← Large, bold
│  of U.S. Population      │  ← Smaller label
├──────────────────────────┤
│  Area: 42,902 mi²        │
│  Regions: 847            │
│  Avg Size: 51 mi²        │
│  λ = 0.50                │  ← Or hide in Advanced
└──────────────────────────┘
```

**Missing Metrics**: Consider adding:
- Total number of selected tracts (if meaningful to users)
- Area as % of US land area (reinforces the story)

### 5. Tab Bar Visibility

**Current State** (`TabBar.css`):
```css
.tab-button {
  color: rgba(255, 255, 255, 0.5);
  background: transparent;
}
```

**Problem**: 50% opacity white text on transparent background has insufficient visual "grounding" against varying map content. Desktop tabs are hard to discover.

**Research Sources**:
- NN/g: "Unselected tabs must remain visible to remind users of available options"
- SetProduct: Inactive tabs should be 40% opacity reduction, not 50%
- WebAIM: WCAG requires 4.5:1 contrast for normal text

**Recommended CSS** (Glassmorphism container):
```css
.tab-bar {
  background: rgba(30, 30, 30, 0.5);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 4px;
}

.tab-button {
  color: rgba(255, 255, 255, 0.7);  /* Increased from 0.5 */
  font-weight: 500;
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
```

### 6. Population Fraction Data Analysis

**Analysis Results** (from TopoJSON files):

| Statistic | Value |
|-----------|-------|
| Below 50% | 81 values |
| At/above 50% | 18 values |
| Minimum | 48.59% (λ=0.75) |
| Maximum | 50.45% (λ=0.91) |
| Range | 1.86 percentage points |

**Notable Values**:
- λ=0.98: **48.71%** (current max slider value, problematic)
- λ=0.97: 50.26% (good)
- λ=0.96: 50.01% (good)
- λ=0.00: 49.47%
- λ=0.50: 49.87%

**User's Concern Validated**: The algorithm does bias toward below 50%. Of 99 lambda values, 81 (82%) are below 50%.

**Recommendation**: If erring on one side is necessary, prefer ≥50% since "half of Americans live here" is more compelling than "slightly less than half." Consider:
1. Algorithm tweak to target 50.5% instead of 50.0%
2. Or document this as expected behavior

### 7. Lambda Range and High-Value Behavior

**Current Slider Range**: λ = 0.00 to 0.98 (99 values)

**Problem at Extremes**:
- λ=1.0 causes convergence failure (documented in `2025-11-21-lambda-one-convergence-failure.md`)
- λ=0.98 has 48.71% population (outside ±1% target)
- λ=0.97 has 50.26% (acceptable)

**Recommendation**: Cap slider at λ=0.97 (or λ=0.96 for extra safety):
- λ=0.97 → 50.26% (within target)
- λ=0.96 → 50.01% (very close to 50%)

**Update `lambda.ts`**:
```typescript
export const LAMBDA_VALUES = [
  0.0, 0.01, ..., 0.96, 0.97  // Remove 0.98
] as const;
```

**Documentation**: Note in METHODOLOGY.md that λ values near 1.0 cause algorithm breakdown.

### 8. Lambda Decimal Precision Bug

**Bug Location**: `SummaryPanel.tsx:54`
```jsx
<dd>{lambda.toFixed(1)}</dd>  // Shows "0.5" for λ=0.50
```

**Slider displays**: `{value.toFixed(2)}` (correct - shows "0.50")

**Fix**:
```jsx
<dd>{lambda.toFixed(2)}</dd>  // Shows "0.50" to match slider
```

### 9. Methodology Visualization (ρ Diagram)

**User's Suggestion**: Visual showing geometric meaning of ρ = median(√aᵢ)

**Concept**:
```
┌─────────────────┐    ┌─────────┐
│  Irregular      │    │         │
│    Census  ───────→  │         │ ← ρ (side length)
│      Tract      │    │   □     │
│    (area aᵢ)    │    │         │
└─────────────────┘    └─────────┘
                       Perfect square
                       with area aᵢ
```

**Caption**: "ρ represents the 'standard width' of a neighborhood in this model. It converts 2D area into a 1D length we can use to measure the border."

**Implementation**: Could be SVG in MethodTab.tsx or a PNG image. Relatively simple to create.

## Code References

- `web/src/components/SummaryPanel.tsx:54` - Lambda precision bug
- `web/src/components/LambdaSlider.tsx:42-44` - Current microcopy logic
- `web/src/components/TabBar.css:12-15` - Tab button styling
- `web/src/types/lambda.ts:5-16` - Lambda value array
- `web/src/components/MapTab.tsx:54-64` - GeoJsonLayer configuration (autoHighlight)

## Implementation Priority

| Priority | Issue | Effort | Impact |
|----------|-------|--------|--------|
| 1 | Lambda precision bug | 5 min | Quick win |
| 2 | Tab bar glassmorphism | 15 min | High visibility |
| 3 | Slider endpoint labels | 30 min | High UX impact |
| 4 | Title overlay | 30 min | Critical for orientation |
| 5 | Cap lambda at 0.97 | 10 min | Data quality |
| 6 | Legend population prominence | 20 min | Story emphasis |
| 7 | Hover tooltips | 1-2 hrs | Feature addition |
| 8 | ρ diagram | 1 hr | Nice-to-have |

## Open Questions

1. **Region naming**: How to name disconnected regions in tooltips? Derive from containing county/metro?
RESPONSE: I'm confused. Regions don't have names, they're groups of connected census tracts. They can't be disconnected, by definition.
2. **Mobile tooltips**: deck.gl hover behavior is problematic on touch devices. Use tap-to-reveal or fixed panel?
RESPONSE: If there's an easy best practice, we should do that. I don't want to spend too much time optimizing for mobile.
3. **Area comparison**: Worth showing "smaller than Rhode Island" style comparisons?
4. **Algorithm bias**: Should we retarget to 50.5% to ensure ≥50%?

## Related Research

- [2025-11-21-lambda-one-convergence-failure.md](2025-11-21-lambda-one-convergence-failure.md) - Why λ=1.0 fails
- [2025-11-21-lambda-edge-cases.md](2025-11-21-lambda-edge-cases.md) - Lambda boundary behavior
- [2025-11-23-tab-structure-implementation.md](2025-11-23-tab-structure-implementation.md) - Tab navigation design
