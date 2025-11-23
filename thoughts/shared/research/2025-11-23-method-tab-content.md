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

## Open Questions

1. **Math rendering decision**: Should we use KaTeX for the objective function, or can Unicode + CSS achieve acceptable results?

2. **Content depth**: Should we include all sections from METHODOLOGY.md, or prioritize the most important ones?

3. **External links**: Should we link to specific lines in the GitHub repository for code references?

4. **Mobile optimization**: Do mathematical equations need special handling for small screens?

## Implementation Approach

### Phase 1: Content + Structure (No Math Library)
1. Create content sections using Unicode for Greek letters
2. Add CSS patterns from StoryTab
3. Structure the objective function as a styled code/formula block
4. Add navigation links

### Phase 2: Polish (If Needed)
1. Evaluate if KaTeX is worth adding for objective function
2. Add GitHub permalink to repository
3. Fine-tune responsive styling for equations
