# Geographic Scope and Disclaimer Implementation Plan

## Overview

Update UI language and add disclaimers to accurately reflect that the visualization covers the contiguous United States only (48 states + DC), excluding Alaska, Hawaii, Puerto Rico, and other territories.

## Current State Analysis

The UI uses terms like "U.S. Population" and "U.S. Land Area" without qualification, implying the full United States is represented. However, the data pipeline explicitly limits to contiguous US via `CONTIGUOUS_US_FIPS` in `src/half_america/data/constants.py`.

### Key Discoveries:
- Tooltip pattern exists in `LambdaSlider.tsx:27-71` with hover/click/focus handling
- Tooltip CSS in `LambdaSlider.css:32-127` can be largely reused
- Text needing updates: `SummaryPanel.tsx:41,45`, `StoryTab.tsx:13,21`, `MapTitle.tsx:7`
- Method Tab has clear section structure with `section-card` styling

## Desired End State

1. All UI text accurately references "contiguous U.S." where appropriate
2. Summary Panel has an info icon with tooltip explaining geographic scope
3. Method Tab has a "Data Scope & Limitations" section with full technical explanation
4. Data Sources section includes specific years (TIGER 2024, ACS 2022)

### Verification:
- All text changes visible in browser
- Tooltip appears on hover/click/focus and is accessible
- Method Tab section renders with correct styling
- No TypeScript/lint errors
- Build succeeds

## What We're NOT Doing

- Changing the project title "Half of America" (keeping it catchy)
- Modifying backend/data pipeline code
- Adding support for non-contiguous territories
- Creating inset maps

## Implementation Approach

Three phases: language updates, summary panel tooltip, method tab section. Each phase is independently deployable.

---

## Phase 1: Language Updates

### Overview
Update text strings across 3 components to reference "contiguous U.S." instead of "U.S."

### Changes Required:

#### 1. SummaryPanel.tsx
**File**: `web/src/components/SummaryPanel.tsx`
**Changes**: Update hero stat labels (lines 41, 45)

```tsx
// Line 41: Change from
<span className="hero-label">of U.S. Population</span>
// To
<span className="hero-label">of Contiguous U.S. Population</span>

// Line 45: Change from
<span className="hero-label">of U.S. Land Area</span>
// To
<span className="hero-label">of Contiguous U.S. Land Area</span>
```

#### 2. StoryTab.tsx
**File**: `web/src/components/StoryTab.tsx`
**Changes**: Update subtitle and body text (lines 13, 21)

```tsx
// Line 13: Change from
<p className="subtitle">Where do half of all Americans actually live?</p>
// To
<p className="subtitle">Where does half the population actually live?</p>

// Line 21: Change from
Half of the United States population—over <span className="stat-highlight">165 million people</span>—lives
// To
Half of the contiguous United States population—over <span className="stat-highlight">165 million people</span>—lives
```

#### 3. MapTitle.tsx
**File**: `web/src/components/MapTitle.tsx`
**Changes**: Update subtitle (line 7)

```tsx
// Line 7: Change from
<p className="map-title-sub">Where 50% of Americans live</p>
// To
<p className="map-title-sub">Where 50% of the population lives</p>
```

### Success Criteria:

#### Automated Verification:
- [ ] TypeScript compiles: `cd web && npm run build`
- [ ] Linting passes: `cd web && npm run lint`

#### Manual Verification:
- [ ] Text changes visible on Map tab (SummaryPanel, MapTitle)
- [ ] Text changes visible on Story tab
- [ ] No layout breaks on mobile viewport

---

## Phase 2: Summary Panel Info Icon

### Overview
Add an info icon next to the Summary Panel title with a tooltip explaining geographic scope.

### Changes Required:

#### 1. SummaryPanel.tsx
**File**: `web/src/components/SummaryPanel.tsx`
**Changes**: Add state, info icon button, and tooltip

```tsx
import { useState } from 'react';
import type { FeatureCollection, Geometry } from 'geojson';
import './SummaryPanel.css';

// ... interfaces unchanged ...

export function SummaryPanel({ data, lambda }: SummaryPanelProps) {
  const [showTooltip, setShowTooltip] = useState(false);

  // ... existing logic unchanged ...

  return (
    <div className="summary-panel">
      <div className="summary-header">
        <h2 className="summary-title">Half of America</h2>
        <button
          type="button"
          className="info-icon"
          aria-label="Geographic scope information"
          onMouseEnter={() => setShowTooltip(true)}
          onMouseLeave={() => setShowTooltip(false)}
          onClick={() => setShowTooltip(!showTooltip)}
          onFocus={() => setShowTooltip(true)}
          onBlur={() => setShowTooltip(false)}
        >
          <span className="icon" aria-hidden="true">ⓘ</span>
        </button>
      </div>

      {showTooltip && (
        <div className="scope-tooltip" role="tooltip">
          <div className="tooltip-section">
            <strong>Geographic Scope</strong>
            <p>
              This visualization covers the contiguous United States only
              (48 states + DC).
            </p>
            <p>
              Alaska, Hawaii, Puerto Rico, and other U.S. territories are
              excluded due to map projection constraints.
            </p>
          </div>
          <p className="tooltip-suggestion">
            See the Method tab for details.
          </p>
        </div>
      )}

      {/* Rest of component unchanged */}
    </div>
  );
}
```

#### 2. SummaryPanel.css
**File**: `web/src/components/SummaryPanel.css`
**Changes**: Add header layout and tooltip styles

```css
/* Add after .summary-panel styles */

.summary-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.summary-header .summary-title {
  margin: 0;
  padding: 0;
  border: none;
}

/* Info icon - reuse pattern from LambdaSlider */
.summary-panel .info-icon {
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
  flex-shrink: 0;
}

.summary-panel .info-icon:hover,
.summary-panel .info-icon:focus {
  background: rgba(0, 114, 178, 0.2);
  border-color: rgba(0, 114, 178, 0.6);
  color: #0072B2;
  outline: none;
}

.summary-panel .info-icon:focus-visible {
  outline: 2px solid #0072B2;
  outline-offset: 2px;
}

/* Scope tooltip */
.scope-tooltip {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 8px;
  padding: 14px;
  background: rgba(0, 0, 0, 0.95);
  border: 1px solid rgba(0, 114, 178, 0.4);
  border-radius: 6px;
  font-size: 13px;
  line-height: 1.5;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
}

.scope-tooltip .tooltip-section {
  margin-bottom: 12px;
}

.scope-tooltip .tooltip-section:last-child {
  margin-bottom: 0;
}

.scope-tooltip .tooltip-section strong {
  display: block;
  margin-bottom: 4px;
  color: #56B4E9;
  font-size: 12px;
}

.scope-tooltip .tooltip-section p {
  margin: 0 0 6px 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
}

.scope-tooltip .tooltip-suggestion {
  margin: 0;
  font-size: 11px;
  font-style: italic;
  color: rgba(86, 180, 233, 0.8);
}

/* Mobile adjustments */
@media (max-width: 767px) {
  .summary-header {
    margin-bottom: 8px;
    padding-bottom: 6px;
  }

  .scope-tooltip {
    font-size: 12px;
    padding: 12px;
  }

  .scope-tooltip .tooltip-section p {
    font-size: 11px;
  }

  .scope-tooltip .tooltip-suggestion {
    font-size: 10px;
  }
}
```

### Success Criteria:

#### Automated Verification:
- [ ] TypeScript compiles: `cd web && npm run build`
- [ ] Linting passes: `cd web && npm run lint`

#### Manual Verification:
- [ ] Info icon appears next to "Half of America" title
- [ ] Tooltip appears on hover
- [ ] Tooltip appears on click (mobile)
- [ ] Tooltip appears on keyboard focus
- [ ] Tooltip dismisses correctly
- [ ] Tooltip readable on mobile viewport

---

## Phase 3: Method Tab Section

### Overview
Add a "Data Scope & Limitations" section to the Method Tab with full technical explanation, and update Data Sources with specific years.

### Changes Required:

#### 1. MethodTab.tsx
**File**: `web/src/components/MethodTab.tsx`
**Changes**: Add new section after "Data Sources" (after line 117), update Data Sources text

```tsx
// Update Data Sources section (lines 107-117) to include years:
{/* Data Sources */}
<h2>Data Sources</h2>
<p>
  <strong>US Census Bureau TIGER/Line Shapefiles (2024)</strong> and <strong>ACS 5-Year Estimates (2022)</strong> provide
  tract geometries and population data. At ~73,000 tracts (vs. ~3,100 counties), this offers
  population resolution of 1,200–8,000 people per unit.
</p>
<p>
  Raw shapefiles undergo topological cleaning: coordinates are quantized to eliminate
  micro-gaps, and geometries are validated to fix self-intersections before graph construction.
</p>

<hr className="section-divider" />

{/* NEW: Data Scope & Limitations - insert after Data Sources */}
<h2>Data Scope & Limitations</h2>

<div className="section-card">
  <h3>Geographic Coverage</h3>
  <p>
    This analysis covers the <strong>contiguous United States only</strong>—the
    48 states physically connected on the North American mainland, plus the
    District of Columbia.
  </p>
  <p>
    This totals 49 jurisdictions containing approximately <strong>328 million
    people</strong> (~98.5% of U.S. population) across <strong>3.12 million
    square miles</strong> (~82% of U.S. land area).
  </p>
</div>

<div className="section-card">
  <h3>Excluded Areas</h3>
  <p>The following are excluded from this visualization:</p>
  <ul className="exclusion-list">
    <li><strong>Alaska</strong> — ~733,000 people, ~665,000 mi²</li>
    <li><strong>Hawaii</strong> — ~1.4 million people, ~10,900 mi²</li>
    <li><strong>Puerto Rico</strong> — ~3.2 million people, ~3,500 mi²</li>
    <li><strong>Other territories</strong> — Guam, USVI, American Samoa, CNMI</li>
  </ul>
</div>

<div className="section-card">
  <h3>Why Contiguous U.S. Only?</h3>
  <p>
    <strong>Projection:</strong> The Albers Equal Area Conic projection (EPSG:5070)
    used for accurate area calculations is optimized for the contiguous U.S.
    Alaska would be significantly distorted, and Hawaii would require a separate
    projection.
  </p>
  <p>
    <strong>Visualization:</strong> The map assumes a continuous landmass.
    Non-contiguous territories would require inset maps, adding complexity
    beyond the scope of this demonstration.
  </p>
  <p>
    <strong>Interpretation:</strong> Working with a connected landmass simplifies
    both implementation and the visual story of population concentration.
  </p>
</div>

<div className="terminology-note">
  <p>
    <strong>Terminology Note:</strong> When this visualization refers to
    "America," "Americans," or "U.S.," these terms specifically mean the
    contiguous United States unless otherwise noted.
  </p>
</div>

<hr className="section-divider" />
```

#### 2. MethodTab.css
**File**: `web/src/components/MethodTab.css`
**Changes**: Add styles for exclusion list and terminology note

```css
/* Add after existing .section-card styles */

.exclusion-list {
  margin: 8px 0 0 0;
  padding-left: 20px;
}

.exclusion-list li {
  margin-bottom: 4px;
  font-size: 14px;
}

.exclusion-list li strong {
  color: #56B4E9;
}

.terminology-note {
  margin-top: 16px;
  padding: 12px 16px;
  background: rgba(0, 114, 178, 0.1);
  border-left: 3px solid #0072B2;
  border-radius: 0 4px 4px 0;
}

.terminology-note p {
  margin: 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
}

.terminology-note strong {
  color: #56B4E9;
}
```

### Success Criteria:

#### Automated Verification:
- [ ] TypeScript compiles: `cd web && npm run build`
- [ ] Linting passes: `cd web && npm run lint`

#### Manual Verification:
- [ ] "Data Scope & Limitations" section appears after "Data Sources"
- [ ] Section cards render with correct styling
- [ ] Exclusion list renders as bulleted list
- [ ] Terminology note has distinctive styling
- [ ] Data Sources section shows "(2024)" and "(2022)" years
- [ ] Section readable on mobile viewport

---

## Testing Strategy

### Automated Tests:
- TypeScript compilation validates all imports and types
- ESLint catches any React/JSX issues

### Manual Testing Steps:
1. Navigate to Map tab - verify SummaryPanel and MapTitle text updates
2. Hover over info icon - verify tooltip appears
3. Click info icon - verify tooltip toggles
4. Tab to info icon - verify focus state and tooltip
5. Navigate to Story tab - verify text updates
6. Navigate to Method tab - verify new section and year updates
7. Test all above on mobile viewport (Chrome DevTools)

## References

- Research document: `thoughts/shared/research/2025-11-25-geographic-scope-disclaimers.md`
- Tooltip pattern: `web/src/components/LambdaSlider.tsx:27-71`
- Tooltip CSS: `web/src/components/LambdaSlider.css:32-127`
