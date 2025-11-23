---
date: 2025-11-23T12:00:00-08:00
researcher: Claude
git_commit: 6604a5d9c3c6bcffa5c206a2748323c68603c4a6
branch: master
repository: half-america
topic: "Add content to Method tab (technical methodology)"
tags: [research, codebase, method-tab, methodology, math-rendering, react]
status: complete
last_updated: 2025-11-23
last_updated_by: Claude
last_updated_note: "Investigated all 4 open questions with detailed analysis"
---

# Research: Add content to Method tab (technical methodology)

**Date**: 2025-11-23T12:00:00-08:00
**Researcher**: Claude
**Git Commit**: 6604a5d9c3c6bcffa5c206a2748323c68603c4a6
**Branch**: master
**Repository**: half-america

## Research Question

How should we implement the Method tab content, including the technical methodology with mathematical equations from METHODOLOGY.md?

## Summary

The Method tab is currently a placeholder component requiring full technical content. The implementation involves two key decisions:

1. **Math rendering approach**: The METHODOLOGY.md file contains extensive LaTeX notation. Options include KaTeX (full rendering), Unicode approximations, or descriptive HTML.

2. **Content structure**: Following the tab strategy guidance to "render, not dump" - the content should be reformatted with intentional presentation, featuring the objective function prominently.

The StoryTab implementation provides an excellent template for content structure and CSS patterns.

## Detailed Findings

### Current MethodTab Implementation

**File**: `web/src/components/MethodTab.tsx` (17 lines)

The component is a minimal placeholder:
- Title: "Methodology"
- Subtitle: "Technical details for replication, critique, and extension"
- Placeholder message about content coming soon
- No props or state (pure presentational)

**File**: `web/src/components/MethodTab.css` (47 lines)

Basic styling already in place:
- Same layout pattern as StoryTab (absolute positioning, scrollable, dark background)
- Content wrapper with 680px max-width
- Responsive padding for desktop/mobile tab bars
- Placeholder box styling (dashed border, muted text)

### Content Source: METHODOLOGY.md

**File**: `METHODOLOGY.md` (103 lines)

Contains five major sections:
1. **Motivation** - Technical limitations of traditional approaches
2. **Data Sources & Preprocessing** - Census Tracts, granularity, topological cleaning
3. **Mathematical Formulation** - Dimensional analysis, the objective function
4. **Algorithmic Approach** - Max-Flow Min-Cut, graph construction, nested optimization
5. **Post-Processing & Visualization** - Dissolve, simplification, TopoJSON export
6. **Implementation Stack** - Libraries used

### Math Notation Requirements

The METHODOLOGY.md contains extensive LaTeX:

| Category | Examples |
|----------|----------|
| Greek letters | λ, μ, ρ, ε |
| Subscripts | p_i, a_i, l_{ij}, x_i |
| Fractions | l_{ij}/ρ, a_i/ρ² |
| Summations | Σ_{(i,j)∈N}, Σ_i |
| Set notation | {0,1}, ∈, [0,1) |
| Square roots | √a_i |
| Absolute values | \|x_i - x_j\| |

**Key equation** (the objective function):
```
E(X) = λ Σ(l_ij/ρ)|x_i - x_j| + (1-λ) Σ(a_i/ρ²)x_i - μ Σ p_i x_i
       \_____________________/   \________________/   \________/
          Boundary Cost              Area Cost       Population Reward
```

### Math Rendering Options

**Option A: KaTeX (Recommended for full fidelity)**
- Package: `katex` + `react-katex`
- Pros: Full LaTeX support, fast rendering, good documentation
- Cons: Adds ~30KB to bundle, requires learning KaTeX syntax
- Use case: If the objective function display is important

**Option B: Unicode + HTML (Lightweight)**
- Pros: Zero dependencies, works everywhere
- Cons: Limited to basic symbols, fractions look less elegant
- Example: λ∈[0,1), p_i → p<sub>i</sub>, √a → √a

**Option C: Static SVG/Images**
- Pros: Perfect rendering, no runtime cost
- Cons: Not editable, accessibility concerns

**Recommendation**: Start with Unicode + HTML for most content. Consider adding KaTeX only if the objective function needs elegant display.

### StoryTab Pattern Reference

**File**: `web/src/components/StoryTab.tsx` (100 lines)

Provides reusable patterns:

| Pattern | Usage |
|---------|-------|
| `.hook` | Lead-in question with left border accent |
| `.section-card` | Boxed content with heading + description |
| `.section-divider` | Horizontal rule between sections |
| `.stat-highlight` | Inline emphasis in accent color |
| `.tab-links` | Navigation to other tabs |
| `handleTabClick()` | Curried handler for internal navigation |

### Tab Strategy Guidance

**File**: `docs/tab_strategy.md`

Key requirements for Method tab:
- **Voice**: precise / formal / modest
- **Goal**: satisfy technically literate skeptics (replicate, critique, extend)
- **DO**: Retain notation, include references, link to repo, full optimization objective
- **DON'T**: Copy/paste literally - "render it, don't dump it"
- **Special guidance**: Extract objective function into a "neat boxed section near the top"

## Proposed Content Structure

Based on tab strategy guidance and StoryTab patterns:

```
1. Title + Subtitle (existing)
2. Hook: Brief statement of the optimization framing
3. Objective Function Box (prominent, possibly styled as hero)
4. Section: Data Sources
   - Granularity card
   - Topological cleaning card
5. Section: Mathematical Formulation
   - Variable definitions
   - Dimensional analysis
   - Energy function explanation
6. Section: Algorithm
   - Graph construction (n-links, t-links)
   - Binary search for μ
7. Section: Post-Processing
   - Dissolve + simplify + export
8. Section: Implementation Stack
   - Links to libraries
9. Navigation links to Map and Story tabs
10. GitHub repository link
```

## Code References

- `web/src/components/MethodTab.tsx:1-17` - Current placeholder implementation
- `web/src/components/MethodTab.css:1-47` - Current styling (base layout ready)
- `web/src/components/StoryTab.tsx:1-100` - Reference implementation for content patterns
- `web/src/components/StoryTab.css:1-143` - CSS patterns to extend
- `METHODOLOGY.md:1-103` - Source content to render
- `docs/tab_strategy.md:49-61` - Specific guidance for Method tab

## Architecture Insights

1. **Component Pattern**: Follow the existing pattern of pure presentational components with CSS modules
2. **Navigation Pattern**: Reuse the `handleTabClick` curried handler pattern from StoryTab
3. **CSS Reuse**: Many StoryTab CSS classes can be copied directly to MethodTab.css (h2, p, .section-card, .section-divider, etc.)
4. **Content Rendering**: Keep content as JSX rather than markdown parsing to maintain full control

## Related Research

- `thoughts/shared/research/2025-11-23-story-tab-content.md` - Story tab content strategy
- `thoughts/shared/research/2025-11-23-tab-structure-implementation.md` - Tab navigation implementation
- `thoughts/shared/plans/2025-11-23-tab-structure-implementation.md` - Original tab implementation plan

## Investigated Questions

### 1. Math rendering decision: Should we use KaTeX for the objective function, or can Unicode + CSS achieve acceptable results?

**Investigation Summary**

Researched four approaches: KaTeX, Unicode+CSS, PureTex.css, and native MathML. The objective function `E(X) = λ Σ(l_ij/ρ)|x_i - x_j| + (1-λ) Σ(a_i/ρ²)x_i - μ Σ p_i x_i` with underbrace annotations requires sophisticated rendering.

**Options Analysis**

| Option | Pros | Cons |
|--------|------|------|
| **KaTeX** | - Full LaTeX support, native underbraces<br>- Fast synchronous rendering<br>- Professional typesetting<br>- Easy maintenance (standard LaTeX) | - ~100KB gzipped bundle overhead<br>- Requires CSS import |
| **Unicode + CSS** | - Zero bundle cost<br>- Full styling control | - Underbraces require CSS hack (looks less professional)<br>- Fractions don't render naturally<br>- Manual maintenance burden<br>- Poor accessibility |
| **PureTex.css** | - No JavaScript (~5-10KB CSS)<br>- Supports fractions, summations | - No underbrace support<br>- Requires SVG symbol files<br>- Verbose HTML |
| **Native MathML** | - Zero JavaScript<br>- Semantic, accessible | - Inconsistent browser support (Chrome limited)<br>- Requires polyfill |

**Recommendation: Use KaTeX**

For a portfolio piece targeting data science roles:
1. Professional LaTeX typesetting signals technical competence
2. The equation complexity (subscripts, fractions, underbraces) makes CSS-only fragile
3. ~100KB is modest relative to existing deck.gl (~300KB) + MapLibre (~200KB)
4. Future-proof if more equations are added
5. Aligns with tab strategy's "neat boxed section" guidance

**Implementation:**
```bash
npm install katex @matejmazur/react-katex
```

```tsx
import 'katex/dist/katex.min.css';
import { BlockMath } from '@matejmazur/react-katex';

<BlockMath math={`
  E(X) = \\underbrace{\\lambda \\sum_{(i,j) \\in N} \\frac{\\ell_{ij}}{\\rho} |x_i - x_j|}_{\\text{Boundary Cost}}
  + \\underbrace{(1-\\lambda) \\sum_i \\frac{a_i}{\\rho^2} x_i}_{\\text{Area Cost}}
  - \\underbrace{\\mu \\sum_i p_i x_i}_{\\text{Population Reward}}
`} />
```

---

### 2. Content depth: Should we include all sections from METHODOLOGY.md, or prioritize the most important ones?

**Investigation Summary**

Analyzed all 6 sections of METHODOLOGY.md against the Story tab content and target audience needs ("technically literate skeptics" who want to "replicate, critique, extend").

**Section Analysis**

| Section | Lines | Recommendation | Rationale |
|---------|-------|----------------|-----------|
| Motivation | 3-13 | **EXCLUDE** | Fully covered by Story tab cards (San Bernardino, Census Tracts, perimeter) |
| Data Sources | 15-26 | Include (condensed) | Essential for reproducibility (TIGER/ACS sources, 73K tracts) |
| Mathematical Formulation | 27-53 | **PROMINENT** | Intellectual core - what distinguishes the project |
| Algorithmic Approach | 54-84 | Include (full) | The "how" - essential for replication |
| Post-Processing | 86-94 | Include (condensed) | Explains output artifacts |
| Implementation Stack | 96-102 | Include (as-is) | Quick reference for implementation |

**Recommendation: Include 5 of 6 sections, exclude Motivation**

**Structure:**
1. **Objective Function** (prominent boxed section at top)
2. Variable Definitions
3. Algorithm: Max-Flow Min-Cut (full detail on n-links, t-links, binary search)
4. Data Sources (condensed)
5. Post-Processing (condensed)
6. Implementation Stack

**Target length:** 800-1200 words (~60-80% of METHODOLOGY.md)

**Rationale:** The tab strategy says "the visualization is the primary artifact" and supporting tabs "should feel supportive." Removing the redundant Motivation section and condensing peripheral sections keeps focus on the technical substance.

---

### 3. External links: Should we link to specific lines in the GitHub repository for code references?

**Investigation Summary**

Analyzed existing link patterns in the repository's research documents and evaluated strategies for a portfolio piece.

**Options Analysis**

| Approach | URL Format | Pros | Cons |
|----------|------------|------|------|
| **Commit SHA** | `/blob/{sha}/path#L10-L20` | Permanent, reproducible, matches documentation | Becomes stale as code evolves |
| **Branch (master)** | `/blob/master/path#L10-L20` | Always current | Line numbers can shift |
| **File only** | `/blob/master/path` | Never breaks | No precision |

**Recommendation: Hybrid approach**

1. **Top-level "View Source" link** to repository root on master:
   ```markdown
   [View full source on GitHub](https://github.com/stevenfazzio/half-america)
   ```

2. **Inline code references** using commit SHA for specific algorithms:
   ```markdown
   > Code references link to commit [`6604a5d`](https://github.com/stevenfazzio/half-america/tree/6604a5d) for reproducibility.
   ```

**Key files to link:**

| File | Lines | Purpose |
|------|-------|---------|
| `src/half_america/graph/network.py` | 9-53 | `build_flow_network()` - s-t cut graph construction |
| `src/half_america/graph/network.py` | 70-108 | `compute_energy()` - energy function |
| `src/half_america/optimization/search.py` | 27-119 | `find_optimal_mu()` - binary search |
| `src/half_america/optimization/solver.py` | 31-118 | `solve_partition()` - main solver |

**Rationale:** The existing research documents already use SHA-based permalinks with line ranges. This pattern aligns with the "replicate" goal. The project is at Phase 6 (mature), so core algorithm files are stable.

---

### 4. Mobile optimization: Do mathematical equations need special handling for small screens?

**Investigation Summary**

Analyzed the main equation width (~500-600px when rendered) vs mobile content width (288-398px after padding), reviewed current responsive patterns in StoryTab.css and MethodTab.css.

**The Problem**

- Mobile content width: 288-398px (screen minus 32px padding)
- Rendered equation width: ~500-600px
- **Result:** Equation overflows on phones

**Audience Context**

The Method tab targets "technically literate skeptics" who are more likely evaluating the portfolio on desktop. Mobile is secondary but should still work.

**Recommendation: Horizontal scroll container**

This is the most appropriate pattern because:
1. Preserves equation integrity (no line breaks or font reduction)
2. Matches industry practice (MDN, academic sites use this)
3. No effect on desktop (primary audience)
4. Familiar interaction pattern on mobile

**CSS Pattern:**
```css
.method-content .equation-block {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  padding: 16px 0;
  margin: 24px 0;
}

/* Optional: scroll hint on mobile */
@media (max-width: 767px) {
  .method-content .equation-block::after {
    content: '';
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    width: 24px;
    background: linear-gradient(to right, transparent, #1a1a1a);
    pointer-events: none;
  }
}
```

**Not recommended:** Font-size reduction (harms readability), line-breaking equations (mathematically problematic), responsive reflow (complex, inconsistent).

---

## Open Questions

No remaining open questions. All questions have been investigated with clear recommendations.

## Implementation Approach

### Phase 1: Setup and Dependencies
1. Install KaTeX: `npm install katex @matejmazur/react-katex`
2. Copy CSS patterns from StoryTab.css to MethodTab.css (h2, p, .section-card, .section-divider, etc.)

### Phase 2: Content Structure
1. Create prominent objective function box using KaTeX BlockMath
2. Add variable definitions section
3. Add Algorithm section with n-links/t-links explanation
4. Add condensed Data Sources and Post-Processing sections
5. Add Implementation Stack with library links
6. Add navigation links to Map and Story tabs

### Phase 3: GitHub Integration and Mobile
1. Add "View Source on GitHub" link at top
2. Add commit SHA reference note for code links
3. Add horizontal scroll container for equation block (mobile support)
4. Test on mobile viewport sizes

### Key Implementation Details
- **Skip Motivation section** - already covered by Story tab
- **Use KaTeX** for the objective function with underbraces
- **Hybrid GitHub links** - master for repo root, SHA for specific lines
- **Horizontal scroll** for equations on mobile (no font reduction)
