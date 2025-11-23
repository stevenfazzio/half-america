# Method Tab Content Implementation Plan

## Overview

Implement the Method tab content, transforming the current placeholder into a full technical methodology page with mathematical equations rendered via KaTeX. The content will present the optimization formulation from METHODOLOGY.md in a well-structured, visually appealing format following the tab strategy guidance.

## Current State Analysis

**MethodTab.tsx** (`web/src/components/MethodTab.tsx:1-17`):
- Minimal placeholder with title, subtitle, and "coming soon" message
- No props or state (pure presentational)

**MethodTab.css** (`web/src/components/MethodTab.css:1-47`):
- Base layout in place (absolute positioning, scrollable, 680px max-width)
- Responsive padding for desktop/mobile tab bars
- Missing: h2, p, section-card, and other content styles

**Content Source**: METHODOLOGY.md (103 lines, 5 major sections)

### Key Discoveries:
- StoryTab provides reusable CSS patterns: `.hook`, `.section-card`, `.section-divider`, `.tab-links`
- Tab strategy requires "precise / formal / modest" voice and prominent objective function
- Research recommends excluding Motivation section (covered by Story tab)

## Desired End State

A fully functional Method tab that:
1. Displays the objective function prominently at the top using KaTeX with underbraces
2. Presents variable definitions, algorithm details, and implementation stack
3. Links to GitHub repository with commit SHA references for code
4. Scrolls horizontally on mobile for wide equations
5. Follows the visual patterns established by StoryTab

### Verification:
- KaTeX renders equations correctly (no raw LaTeX visible)
- All sections are readable and well-formatted
- Navigation links to Map and Story tabs work
- Mobile viewport shows horizontal scroll hint for equations
- `npm run build` succeeds without errors

## What We're NOT Doing

- Adding interactive elements or animations
- Including the Motivation section (already in Story tab)
- Creating a separate math component library
- Adding equation numbering or cross-references
- Implementing copy-to-clipboard for equations

## Implementation Approach

Follow the research recommendations:
1. Use KaTeX via `@matejmazur/react-katex` for math rendering
2. Copy CSS patterns from StoryTab.css rather than creating new abstractions
3. Keep content as JSX (not markdown parsing) for full control
4. Use horizontal scroll container for mobile equation handling

---

## Phase 1: Setup and Dependencies

### Overview
Install KaTeX and copy CSS patterns from StoryTab to MethodTab.

### Changes Required:

#### 1. Install KaTeX packages
**Command**: `cd web && npm install katex @matejmazur/react-katex`

#### 2. Add TypeScript declarations (if needed)
**File**: `web/src/vite-env.d.ts` or create `web/src/types/react-katex.d.ts`

If TypeScript complains about missing types:
```typescript
declare module '@matejmazur/react-katex' {
  import { ComponentType } from 'react';

  interface KatexProps {
    math: string;
    errorColor?: string;
    renderError?: (error: Error) => React.ReactNode;
  }

  export const InlineMath: ComponentType<KatexProps>;
  export const BlockMath: ComponentType<KatexProps>;
}
```

#### 3. Copy CSS patterns from StoryTab.css to MethodTab.css
**File**: `web/src/components/MethodTab.css`

Add after existing styles (copy and adapt from StoryTab.css):
```css
/* Typography */
.method-content h2 {
  font-size: 24px;
  font-weight: 600;
  margin: 32px 0 16px 0;
  color: rgba(255, 255, 255, 0.95);
}

.method-content h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 24px 0 12px 0;
  color: rgba(255, 255, 255, 0.9);
}

.method-content p {
  font-size: 16px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 16px 0;
}

.method-content .hook {
  font-size: 20px;
  font-style: italic;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 32px 0;
  padding-left: 20px;
  border-left: 3px solid #0072B2;
}

.method-content .section-divider {
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.15);
  margin: 32px 0;
}

.method-content strong {
  color: rgba(255, 255, 255, 0.95);
}

/* Section cards */
.method-content .section-card {
  padding: 20px 24px;
  background: rgba(30, 30, 30, 0.95);
  border-radius: 8px;
  margin: 24px 0;
}

.method-content .section-card h3 {
  margin: 0 0 8px 0;
}

.method-content .section-card p {
  margin: 0;
  font-size: 14px;
}

.method-content .section-card p + p {
  margin-top: 12px;
}

/* Tab links */
.method-content .tab-links {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 32px;
}

.method-content .tab-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: rgba(0, 114, 178, 0.15);
  border: 1px solid rgba(0, 114, 178, 0.3);
  border-radius: 8px;
  color: #0072B2;
  font-size: 16px;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: background-color 0.15s, border-color 0.15s;
}

.method-content .tab-link:hover {
  background: rgba(0, 114, 178, 0.25);
  border-color: rgba(0, 114, 178, 0.5);
}

/* External links */
.method-content a {
  color: #0072B2;
  text-decoration: none;
}

.method-content a:hover {
  text-decoration: underline;
}
```

### Success Criteria:

#### Automated Verification:
- [x] KaTeX packages installed: `cd web && npm ls katex @matejmazur/react-katex`
- [x] TypeScript compiles: `cd web && npm run build`
- [x] No lint errors: `cd web && npm run lint`

#### Manual Verification:
- [x] CSS file contains new styles matching StoryTab patterns

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation before proceeding to Phase 2.

---

## Phase 2: Core Content Implementation

### Overview
Replace the placeholder content with the full methodology, featuring the objective function prominently.

### Changes Required:

#### 1. Update MethodTab.tsx with full content
**File**: `web/src/components/MethodTab.tsx`

Replace entire file with:

```tsx
import 'katex/dist/katex.min.css';
import { BlockMath, InlineMath } from '@matejmazur/react-katex';
import './MethodTab.css';

export function MethodTab() {
  const handleTabClick = (tab: string) => (e: React.MouseEvent) => {
    e.preventDefault();
    window.location.hash = tab;
  };

  return (
    <div className="method-tab" role="tabpanel" id="method-tab" aria-labelledby="method">
      <div className="method-content">
        <h1>Methodology</h1>
        <p className="subtitle">Technical details for replication, critique, and extension</p>

        <p className="hook">
          This project frames population visualization as a constrained optimization problem,
          solved exactly using max-flow min-cut.
        </p>

        {/* Objective Function - Prominent */}
        <div className="equation-hero">
          <h2>The Objective Function</h2>
          <p>
            We seek a binary partition where <InlineMath math="x_i \in \{0, 1\}" /> indicates
            whether tract <InlineMath math="i" /> is selected. The energy function balances
            three competing terms:
          </p>
          <div className="equation-block">
            <BlockMath math={`
              E(X) = \\underbrace{\\lambda \\sum_{(i,j) \\in N} \\frac{\\ell_{ij}}{\\rho} |x_i - x_j|}_{\\text{Boundary Cost}}
              + \\underbrace{(1-\\lambda) \\sum_i \\frac{a_i}{\\rho^2} x_i}_{\\text{Area Cost}}
              - \\underbrace{\\mu \\sum_i p_i x_i}_{\\text{Population Reward}}
            `} />
          </div>
          <div className="equation-legend">
            <p>
              <strong><InlineMath math="\lambda \in [0, 1)" /></strong> — User-controlled "surface tension" (the slider).
              Higher values favor smooth boundaries over minimal area.
            </p>
            <p>
              <strong><InlineMath math="\mu" /></strong> — Lagrange multiplier tuned via binary search
              to satisfy the 50% population constraint.
            </p>
            <p>
              <strong><InlineMath math="\rho = \text{median}(\sqrt{a_i})" /></strong> — Characteristic
              length scale for dimensional consistency.
            </p>
          </div>
        </div>

        <hr className="section-divider" />

        {/* Variable Definitions */}
        <h2>Variable Definitions</h2>
        <p>For each Census Tract <InlineMath math="t_i" /> in the set <InlineMath math="T" /> (~73,000 tracts):</p>
        <div className="variable-list">
          <p><InlineMath math="p_i" /> — Population</p>
          <p><InlineMath math="a_i" /> — Land area</p>
          <p><InlineMath math="\ell_{ij}" /> — Length of shared boundary between adjacent tracts <InlineMath math="i" /> and <InlineMath math="j" /></p>
        </div>

        <hr className="section-divider" />

        {/* Algorithm */}
        <h2>Algorithm: Max-Flow Min-Cut</h2>
        <p>
          We solve for the global optimum using the max-flow min-cut theorem, avoiding
          local optima common in greedy region-growing algorithms.
        </p>

        <div className="section-card">
          <h3>Graph Construction (s-t Cut)</h3>
          <p>
            We construct a flow network with a Source (selected) and Sink (unselected):
          </p>
          <p>
            <strong>Neighborhood edges (n-links):</strong> Connect adjacent tracts with
            capacity <InlineMath math="w_{ij} = \lambda \cdot \ell_{ij} / \rho" />.
            Cutting creates a boundary; high-capacity edges encourage smoothness.
          </p>
          <p>
            <strong>Terminal edges (t-links):</strong> Source edges have
            capacity <InlineMath math="\mu \cdot p_i" /> (selection reward).
            Sink edges have capacity <InlineMath math="(1-\lambda) \cdot a_i / \rho^2" /> (area cost).
          </p>
        </div>

        <div className="section-card">
          <h3>Binary Search for <InlineMath math="\mu" /></h3>
          <p>
            Since the population constraint (<InlineMath math="\sum p_i \approx 0.5 P_{\text{total}}" />)
            is hard but graph cuts are soft, we use binary search:
          </p>
          <p>
            1. Set bounds <InlineMath math="[\mu_{\min}, \mu_{\max}]" /><br />
            2. Construct graph with current <InlineMath math="\mu" /><br />
            3. Solve max-flow<br />
            4. If <InlineMath math="P_{\text{selected}} < P_{\text{target}}" />, increase <InlineMath math="\mu" /><br />
            5. Repeat until <InlineMath math="|P_{\text{selected}} - P_{\text{target}}| < \epsilon" />
          </p>
        </div>

        <hr className="section-divider" />

        {/* Data Sources */}
        <h2>Data Sources</h2>
        <p>
          <strong>US Census Bureau TIGER/Line Shapefiles</strong> and <strong>ACS 5-Year Estimates</strong> provide
          tract geometries and population data. At ~73,000 tracts (vs. ~3,100 counties), this offers
          population resolution of 1,200–8,000 people per unit.
        </p>
        <p>
          Raw shapefiles undergo topological cleaning: coordinates are quantized to eliminate
          micro-gaps, and geometries are validated to fix self-intersections before graph construction.
        </p>

        <hr className="section-divider" />

        {/* Post-Processing */}
        <h2>Post-Processing</h2>
        <p>
          The raw output (~30,000+ tract IDs) is processed for web rendering:
        </p>
        <p>
          <strong>Dissolve</strong> — Merge selected tracts into unified MultiPolygon geometries.<br />
          <strong>Simplify</strong> — Douglas-Peucker simplification (500m tolerance) reduces vertices ~98%.<br />
          <strong>Export</strong> — TopoJSON encoding preserves shared topology, preventing rendering gaps.
        </p>

        <hr className="section-divider" />

        {/* Implementation Stack */}
        <h2>Implementation Stack</h2>
        <div className="stack-list">
          <p><strong>Data:</strong> pandas, cenpy (Census API)</p>
          <p><strong>Spatial:</strong> geopandas, libpysal (adjacency graphs)</p>
          <p><strong>Optimization:</strong> PyMaxFlow (C++ graph cuts)</p>
          <p><strong>Geometry:</strong> shapely, topojson</p>
          <p><strong>Web:</strong> React, MapLibre GL JS, deck.gl</p>
        </div>

        <hr className="section-divider" />

        {/* Navigation */}
        <h2>Explore</h2>
        <div className="tab-links">
          <a href="#map" className="tab-link" onClick={handleTabClick('map')}>
            View the Interactive Map →
          </a>
          <a href="#story" className="tab-link" onClick={handleTabClick('story')}>
            Read the Story →
          </a>
        </div>

        <p className="repo-link">
          <a
            href="https://github.com/stevenfazzio/half-america"
            target="_blank"
            rel="noopener noreferrer"
          >
            View full source on GitHub →
          </a>
        </p>
      </div>
    </div>
  );
}
```

### Success Criteria:

#### Automated Verification:
- [x] TypeScript compiles: `cd web && npm run build`
- [x] No lint errors: `cd web && npm run lint`
- [x] Dev server starts: `cd web && npm run dev`

#### Manual Verification:
- [x] Objective function renders with underbraces
- [x] All inline math renders correctly (no raw LaTeX)
- [x] Section structure is clear and readable
- [x] Tab navigation links work (switch to Map and Story tabs)
- [x] GitHub link opens in new tab

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation before proceeding to Phase 3.

---

## Phase 3: Styling and Mobile Optimization

### Overview
Add equation-specific styling, the equation hero box, and horizontal scroll support for mobile.

### Changes Required:

#### 1. Add equation and hero styling to MethodTab.css
**File**: `web/src/components/MethodTab.css`

Add after existing styles:

```css
/* Equation hero box */
.method-content .equation-hero {
  background: rgba(0, 114, 178, 0.08);
  border: 1px solid rgba(0, 114, 178, 0.2);
  border-radius: 12px;
  padding: 24px;
  margin: 0 0 32px 0;
}

.method-content .equation-hero h2 {
  margin-top: 0;
  color: #0072B2;
}

/* Equation block with horizontal scroll for mobile */
.method-content .equation-block {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  padding: 16px 0;
  margin: 16px 0;
  position: relative;
}

.method-content .equation-block .katex-display {
  margin: 0;
}

/* Equation legend */
.method-content .equation-legend {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 114, 178, 0.15);
}

.method-content .equation-legend p {
  font-size: 14px;
  margin: 0 0 8px 0;
}

.method-content .equation-legend p:last-child {
  margin-bottom: 0;
}

/* Variable list */
.method-content .variable-list {
  background: rgba(30, 30, 30, 0.95);
  border-radius: 8px;
  padding: 16px 20px;
  margin: 16px 0;
}

.method-content .variable-list p {
  font-size: 15px;
  margin: 0 0 8px 0;
}

.method-content .variable-list p:last-child {
  margin-bottom: 0;
}

/* Stack list */
.method-content .stack-list {
  background: rgba(30, 30, 30, 0.95);
  border-radius: 8px;
  padding: 16px 20px;
}

.method-content .stack-list p {
  font-size: 15px;
  margin: 0 0 8px 0;
}

.method-content .stack-list p:last-child {
  margin-bottom: 0;
}

/* Repo link */
.method-content .repo-link {
  margin-top: 24px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

/* Mobile scroll hint for equations */
@media (max-width: 767px) {
  .method-content .equation-block {
    margin-left: -16px;
    margin-right: -16px;
    padding-left: 16px;
    padding-right: 16px;
  }

  .method-content .equation-hero {
    padding: 20px 16px;
  }
}
```

### Success Criteria:

#### Automated Verification:
- [x] Build succeeds: `cd web && npm run build`
- [x] No lint errors: `cd web && npm run lint`

#### Manual Verification:
- [x] Equation hero box has blue accent styling
- [x] Variable list and stack list have card-style backgrounds
- [x] On mobile viewport (< 768px):
  - [x] Equation block scrolls horizontally when needed
  - [x] Content remains readable
- [x] On desktop:
  - [x] All content displays without horizontal scroll
  - [x] Layout looks intentional and professional

**Implementation Note**: After completing this phase, run final verification and testing.

---

## Testing Strategy

### Automated Tests:
- Build succeeds without TypeScript errors
- Lint passes
- No console errors in dev server

### Manual Testing Steps:
1. View Method tab on desktop - verify all equations render
2. Resize browser to mobile width (~375px) - verify equation scrolls horizontally
3. Click "View the Interactive Map" - verify navigates to Map tab
4. Click "Read the Story" - verify navigates to Story tab
5. Click GitHub link - verify opens in new tab
6. Check KaTeX styling matches overall dark theme

## Performance Considerations

- KaTeX adds ~100KB gzipped to bundle (acceptable given deck.gl/MapLibre already ~500KB)
- KaTeX CSS must be imported for proper rendering
- Equations render synchronously (no flash of unstyled content)

## References

- Research document: `thoughts/shared/research/2025-11-23-method-tab-content.md`
- Tab strategy: `docs/tab_strategy.md`
- Source content: `METHODOLOGY.md`
- Pattern reference: `web/src/components/StoryTab.tsx`, `web/src/components/StoryTab.css`
