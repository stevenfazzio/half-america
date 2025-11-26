# Markdown Documentation Consolidation Implementation Plan

## Overview

Consolidate documentation by creating a single-source-of-truth pattern where markdown files (`METHODOLOGY.md`, new `STORY.md`) serve both as GitHub-readable documentation AND as rendered content in the web application. This eliminates ~70-80% content duplication between markdown files and React components.

## Current State Analysis

### Content Comparison

**METHODOLOGY.md** (117 lines) and **MethodTab.tsx** (227 lines) have ~70% overlap but each contains unique content:

**In METHODOLOGY.md only:**
- Motivation section explaining technical limitations (County Resolution, Dust Artifacts, Bridge Artifacts)
- Subsection numbering (1.1, 1.2, 2.1, etc.)
- Outer Loop description for the user slider
- Target population formula definition
- Final coordinate transformation note (EPSG:5070 → WGS84)

**In MethodTab.tsx only:**
- Subtitle: "Technical details for replication, critique, and extension"
- Hook paragraph framing the optimization problem
- Geographic Coverage statistics (328M people, ~98.5% of population, 3.12M mi², ~82% of land)
- Detailed exclusion list with population/area for each excluded region (Alaska, Hawaii, Puerto Rico, territories)
- Expanded "Why Conterminous U.S. Only?" section with detailed rationale

**StoryTab.tsx** (100 lines) contains narrative content that has no markdown equivalent—this content will be extracted to a new `STORY.md`.

### Current Implementation

- **MethodTab.tsx**: Uses `@matejmazur/react-katex` for LaTeX rendering, JSX for content structure
- **StoryTab.tsx**: Pure JSX, no math rendering
- **CSS**: Both use similar patterns (`.section-card`, `.hook`, `.tab-links`) with scoped CSS files
- **Navigation**: Hash-based routing via `handleTabClick` pattern

### Key Files
- `METHODOLOGY.md:1-117` - Codebase documentation
- `web/src/components/MethodTab.tsx:1-227` - Web component with LaTeX
- `web/src/components/StoryTab.tsx:1-100` - Web component, plain text
- `web/src/components/MethodTab.css:1-278` - Method styling
- `web/src/components/StoryTab.css:1-143` - Story styling
- `web/package.json:17-18` - Already has katex dependency

## Desired End State

After implementation:

1. **METHODOLOGY.md** serves as the single source for technical methodology (readable on GitHub, rendered in MethodTab)
2. **STORY.md** (new) serves as the single source for the narrative story (readable on GitHub, rendered in StoryTab)
3. **MethodTab.tsx** imports and renders `METHODOLOGY.md` via react-markdown
4. **StoryTab.tsx** imports and renders `STORY.md` via react-markdown
5. **MarkdownRenderer.tsx** (new) provides shared rendering configuration with KaTeX support
6. Content updates only need to happen in one place (the markdown files)

### How to Verify

1. METHODOLOGY.md renders correctly on GitHub (equations display as raw LaTeX—acceptable)
2. METHODOLOGY.md renders in web app with proper LaTeX equations
3. STORY.md renders correctly on GitHub
4. STORY.md renders in web app with proper styling
5. Navigation links still work in both tabs
6. Visual appearance matches current implementation (close enough, simpler styling accepted)

## What We're NOT Doing

- NOT using MDX (LaTeX escaping issues)
- NOT using vite-plugin-markdown (unnecessary complexity)
- NOT adding custom remark plugins for `.section-card` styling (accept simpler styling)
- NOT rendering README.md in the app
- NOT preserving exact visual styling—simpler markdown-native styling is acceptable

## Implementation Approach

Use Vite's built-in `?raw` import suffix with `react-markdown` for runtime rendering. The research document confirmed this approach:
- Works with standard `.md` files (GitHub-readable)
- `remark-math` + `rehype-katex` handle LaTeX correctly
- No Vite plugins needed
- Project already has KaTeX installed

---

## Phase 0: Merge Content into METHODOLOGY.md

### Overview
Before implementing the technical changes, merge all unique content from MethodTab.tsx into METHODOLOGY.md. This ensures METHODOLOGY.md is a strict superset of both files and no content is lost during consolidation.

### Changes Required:

#### 1. Add subtitle and hook to METHODOLOGY.md
**File**: `METHODOLOGY.md`

Add after the title:
```markdown
# Technical Methodology

*Technical details for replication, critique, and extension*

> This project frames population visualization as a constrained optimization problem, solved exactly using max-flow min-cut.

## Motivation
...
```

#### 2. Enhance Geographic Scope section with statistics
**File**: `METHODOLOGY.md`

Update section 1.3 to include the coverage statistics from MethodTab.tsx:

**Current (lines 27-39):**
```markdown
### 1.3 Geographic Scope

This analysis covers the **conterminous United States only**—the 48 states physically connected on the North American mainland, plus the District of Columbia.

**Excluded Areas:**
- Alaska, Hawaii, Puerto Rico, and other territories

**Rationale:**
- **Projection**: Albers Equal Area Conic (EPSG:5070) is optimized for conterminous U.S.
- **Visualization**: Assumes continuous landmass without inset maps
- **Interpretation**: Connected landmass simplifies visual story

**Terminology**: "America" in this document refers specifically to the conterminous United States.
```

**Updated:**
```markdown
### 1.3 Geographic Scope

This analysis covers the **conterminous United States only**—the 48 states physically connected on the North American mainland, plus the District of Columbia.

This totals 49 jurisdictions containing approximately **328 million people** (~98.5% of U.S. population) across **3.12 million square miles** (~82% of U.S. land area).

**Excluded Areas:**
- **Alaska** — ~733,000 people, ~665,000 mi²
- **Hawaii** — ~1.4 million people, ~10,900 mi²
- **Puerto Rico** — ~3.2 million people, ~3,500 mi²
- **Other territories** — Guam, USVI, American Samoa, CNMI

**Rationale:**
- **Projection:** The Albers Equal Area Conic projection (EPSG:5070) used for accurate area calculations is optimized for the conterminous U.S. Alaska would be significantly distorted, and Hawaii would require a separate projection.
- **Visualization:** The map assumes a continuous landmass. Non-conterminous areas would require inset maps, adding complexity beyond the scope of this demonstration.
- **Interpretation:** Working with a connected landmass simplifies both implementation and the visual story of population concentration.

**Terminology:** When this visualization refers to "America," "Americans," or "U.S.," these terms specifically refer to the conterminous United States, or residents thereof, unless otherwise noted.
```

### Success Criteria:

#### Automated Verification:
- [ ] METHODOLOGY.md has valid markdown syntax (no broken formatting)
- [ ] All LaTeX equations are properly delimited with `$` or `$$`

#### Manual Verification:
- [ ] METHODOLOGY.md renders correctly on GitHub
- [ ] All content from MethodTab.tsx is now present in METHODOLOGY.md
- [ ] No information has been lost
- [ ] Document reads well as a cohesive whole

**Implementation Note**: After completing this phase and all verification passes, pause here for manual confirmation before proceeding to the technical implementation phases.

---

## Phase 1: Install Dependencies and Setup Types

### Overview
Install react-markdown ecosystem and add TypeScript declarations for raw markdown imports.

### Changes Required:

#### 1. Install npm packages
**Command**: Run in `web/` directory
```bash
npm install react-markdown remark-math rehype-katex
```

Expected additions to package.json:
- `react-markdown` - Markdown renderer
- `remark-math` - Parse math syntax in markdown
- `rehype-katex` - Render math with KaTeX

#### 2. Add TypeScript declaration for raw imports
**File**: `web/src/vite-env.d.ts` (create if doesn't exist, or add to existing)

```typescript
/// <reference types="vite/client" />

declare module '*.md?raw' {
  const content: string
  export default content
}
```

### Success Criteria:

#### Automated Verification:
- [ ] Dependencies install without errors: `npm install`
- [ ] TypeScript recognizes `*.md?raw` imports: `npm run build` (no type errors)

#### Manual Verification:
- [ ] None required for this phase

---

## Phase 2: Create MarkdownRenderer Component

### Overview
Create a shared component that handles markdown rendering with KaTeX math support and consistent styling.

### Changes Required:

#### 1. Create MarkdownRenderer component
**File**: `web/src/components/MarkdownRenderer.tsx`

```tsx
import ReactMarkdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import 'katex/dist/katex.min.css'
import './MarkdownRenderer.css'

interface MarkdownRendererProps {
  content: string
  className?: string
}

export function MarkdownRenderer({ content, className = '' }: MarkdownRendererProps) {
  return (
    <div className={`markdown-content ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={{
          // Style blockquotes as hooks (intro text)
          blockquote: ({ children }) => (
            <blockquote className="hook">{children}</blockquote>
          ),
          // Add section-divider class to hr
          hr: () => <hr className="section-divider" />,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
```

#### 2. Create MarkdownRenderer CSS
**File**: `web/src/components/MarkdownRenderer.css`

Extract and consolidate the shared prose styles from MethodTab.css and StoryTab.css:

```css
/* Markdown content base styles */
.markdown-content {
  color: rgba(255, 255, 255, 0.9);
}

/* Typography */
.markdown-content h1 {
  font-size: 32px;
  font-weight: bold;
  margin: 0 0 8px 0;
  line-height: 1.2;
}

.markdown-content h2 {
  font-size: 24px;
  font-weight: 600;
  margin: 32px 0 16px 0;
  color: rgba(255, 255, 255, 0.95);
}

.markdown-content h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 12px 0;
  color: rgba(255, 255, 255, 0.9);
}

.markdown-content p {
  font-size: 16px;
  line-height: 1.6;
  margin: 0 0 16px 0;
  color: rgba(255, 255, 255, 0.8);
}

.markdown-content strong {
  color: rgba(255, 255, 255, 0.95);
}

.markdown-content em {
  font-style: italic;
}

.markdown-content a {
  color: #0072B2;
  text-decoration: none;
}

.markdown-content a:hover {
  text-decoration: underline;
}

/* Lists */
.markdown-content ul,
.markdown-content ol {
  margin: 0 0 16px 0;
  padding-left: 24px;
}

.markdown-content li {
  font-size: 16px;
  line-height: 1.6;
  margin-bottom: 8px;
  color: rgba(255, 255, 255, 0.8);
}

/* Hook/intro blockquote */
.markdown-content .hook {
  font-size: 20px;
  font-style: italic;
  color: rgba(255, 255, 255, 0.85);
  border-left: 3px solid #0072B2;
  padding-left: 20px;
  margin: 24px 0;
}

.markdown-content .hook p {
  font-size: inherit;
  color: inherit;
  margin: 0;
}

/* Section divider */
.markdown-content .section-divider {
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin: 32px 0;
}

/* Code blocks */
.markdown-content code {
  background: rgba(0, 0, 0, 0.3);
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'SF Mono', Monaco, monospace;
  font-size: 14px;
}

.markdown-content pre {
  background: rgba(0, 0, 0, 0.3);
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin: 16px 0;
}

.markdown-content pre code {
  background: none;
  padding: 0;
}

/* KaTeX math styling */
.markdown-content .katex-display {
  margin: 24px 0;
  overflow-x: auto;
  padding: 16px 0;
}

.markdown-content .katex {
  font-size: 1.1em;
}
```

### Success Criteria:

#### Automated Verification:
- [ ] Component compiles without TypeScript errors: `npm run build`
- [ ] No linting errors: `npm run lint`

#### Manual Verification:
- [ ] None required—will test in Phase 3

---

## Phase 3: Refactor MethodTab to Use Markdown

### Overview
Replace the JSX content in MethodTab with the MarkdownRenderer importing METHODOLOGY.md. Keep navigation as separate JSX.

**Note:** METHODOLOGY.md was already updated with the subtitle and hook in Phase 0, so no markdown changes needed here.

### Changes Required:

#### 1. Refactor MethodTab.tsx
**File**: `web/src/components/MethodTab.tsx`

Replace the entire content with:

```tsx
import { MarkdownRenderer } from './MarkdownRenderer'
import methodologyContent from '../../../METHODOLOGY.md?raw'
import './MethodTab.css'

export function MethodTab() {
  const handleTabClick = (tab: string) => (e: React.MouseEvent) => {
    e.preventDefault()
    window.location.hash = tab
  }

  return (
    <div className="method-tab" role="tabpanel" id="method-tab" aria-labelledby="method">
      <div className="method-content">
        <MarkdownRenderer content={methodologyContent} />

        {/* Navigation - kept as JSX for interactivity */}
        <hr className="section-divider" />
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
  )
}
```

#### 2. Simplify MethodTab.css
**File**: `web/src/components/MethodTab.css`

Remove the duplicated typography styles (now in MarkdownRenderer.css) and keep only:
- Layout styles (`.method-tab`, `.method-content`)
- Navigation styles (`.tab-links`, `.tab-link`)
- Any MethodTab-specific overrides

```css
/* Layout */
.method-tab {
  position: absolute;
  inset: 0;
  overflow-y: auto;
  background: #1a1a1a;
  padding: 80px 24px 24px;
}

@media (max-width: 768px) {
  .method-tab {
    padding: 24px 16px 100px;
  }
}

.method-content {
  max-width: 680px;
  margin: 0 auto;
}

/* Navigation */
.tab-links {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.tab-link {
  display: inline-block;
  padding: 12px 20px;
  background: rgba(0, 114, 178, 0.1);
  border: 1px solid rgba(0, 114, 178, 0.3);
  border-radius: 8px;
  color: #0072B2;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
}

.tab-link:hover {
  background: rgba(0, 114, 178, 0.2);
  border-color: rgba(0, 114, 178, 0.5);
}

.repo-link {
  margin-top: 32px;
  text-align: center;
}

.repo-link a {
  color: rgba(255, 255, 255, 0.5);
  text-decoration: none;
  font-size: 14px;
}

.repo-link a:hover {
  color: rgba(255, 255, 255, 0.7);
}

/* Section divider (used by navigation section) */
.section-divider {
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin: 32px 0;
}
```

### Success Criteria:

#### Automated Verification:
- [ ] Build succeeds: `npm run build`
- [ ] No TypeScript errors
- [ ] No linting errors: `npm run lint`

#### Manual Verification:
- [ ] MethodTab renders with LaTeX equations displaying correctly
- [ ] Navigation links work (clicking "View the Interactive Map" goes to map tab)
- [ ] GitHub repo link opens in new tab
- [ ] Styling is acceptable (may be simpler than before—this is OK)
- [ ] Mobile layout works correctly
- [ ] METHODOLOGY.md still renders nicely on GitHub

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 4: Create STORY.md and Refactor StoryTab

### Overview
Extract StoryTab content to a new STORY.md file and refactor StoryTab to render it.

### Changes Required:

#### 1. Create STORY.md
**File**: `STORY.md` (in repository root)

```markdown
# Half of America

*Where do half of all Americans actually live?*

> What if half of all Americans lived in an area smaller than you'd expect?

## The Surprising Answer

Half of the United States population—over **165 million people**—lives in just **1.1% of the country's land area**. That's roughly the size of Virginia.

The blue shapes on the map represent these areas: dense urban cores and their surrounding suburbs where Americans have concentrated. The rest of the country? Mostly empty.

---

## Why This Map Looks Different

You've probably seen maps like this before. They usually show counties, and they usually look wrong. Here's why we took a different approach:

### The San Bernardino Problem

San Bernardino County, California is larger than nine US states. It's also mostly desert. When you highlight it on a "half of America" map, you're including thousands of square miles where almost nobody lives.

### Going Smaller: Census Tracts

We used Census Tracts instead—about 73,000 small neighborhoods across the country. This gives us much higher resolution, but creates a new problem: thousands of tiny disconnected dots that are hard to visually process.

### Finding the Shape

The solution was to let the boundaries find themselves. Using an optimization technique from computer vision, we minimize the *perimeter* of the selected regions. This produces smooth, organic shapes that are both accurate and visually clear.

---

## The Smoothness Slider

The slider on the map controls a tradeoff between precision and visual clarity:

**Low values** give you maximum precision. You see every dense neighborhood, but as scattered dots that are hard to reason about.

**High values** give you maximum smoothness. The regions merge into coherent shapes that reveal the overall pattern of where Americans live.

There's no "correct" setting—it depends on what you want to see.
```

#### 2. Refactor StoryTab.tsx
**File**: `web/src/components/StoryTab.tsx`

```tsx
import { MarkdownRenderer } from './MarkdownRenderer'
import storyContent from '../../../STORY.md?raw'
import './StoryTab.css'

export function StoryTab() {
  const handleTabClick = (tab: string) => (e: React.MouseEvent) => {
    e.preventDefault()
    window.location.hash = tab
  }

  return (
    <div className="story-tab" role="tabpanel" id="story-tab" aria-labelledby="story">
      <div className="story-content">
        <MarkdownRenderer content={storyContent} />

        {/* Navigation - kept as JSX for interactivity */}
        <hr className="section-divider" />
        <h2>Explore</h2>
        <div className="tab-links">
          <a href="#map" className="tab-link" onClick={handleTabClick('map')}>
            View the Interactive Map →
          </a>
          <a href="#method" className="tab-link" onClick={handleTabClick('method')}>
            Read the Full Methodology →
          </a>
        </div>
      </div>
    </div>
  )
}
```

#### 3. Simplify StoryTab.css
**File**: `web/src/components/StoryTab.css`

Similar to MethodTab.css, keep only layout and navigation:

```css
/* Layout */
.story-tab {
  position: absolute;
  inset: 0;
  overflow-y: auto;
  background: #1a1a1a;
  padding: 80px 24px 24px;
}

@media (max-width: 768px) {
  .story-tab {
    padding: 24px 16px 100px;
  }
}

.story-content {
  max-width: 680px;
  margin: 0 auto;
}

/* Navigation */
.tab-links {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.tab-link {
  display: inline-block;
  padding: 12px 20px;
  background: rgba(0, 114, 178, 0.1);
  border: 1px solid rgba(0, 114, 178, 0.3);
  border-radius: 8px;
  color: #0072B2;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
}

.tab-link:hover {
  background: rgba(0, 114, 178, 0.2);
  border-color: rgba(0, 114, 178, 0.5);
}

/* Section divider (used by navigation section) */
.section-divider {
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  margin: 32px 0;
}
```

### Success Criteria:

#### Automated Verification:
- [ ] Build succeeds: `npm run build`
- [ ] No TypeScript errors
- [ ] No linting errors: `npm run lint`

#### Manual Verification:
- [ ] StoryTab renders correctly with all content
- [ ] Navigation links work
- [ ] Styling is acceptable
- [ ] Mobile layout works
- [ ] STORY.md renders nicely on GitHub

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to the next phase.

---

## Phase 5: Cleanup and Documentation

### Overview
Remove unused code, update documentation references, and verify final state.

### Changes Required:

#### 1. Remove react-katex dependency
**Command**: Run in `web/` directory
```bash
npm uninstall @matejmazur/react-katex
```

#### 2. Remove react-katex type declaration
**File**: Delete `web/src/types/react-katex.d.ts`

#### 3. Update CLAUDE.md
**File**: `CLAUDE.md`

Update the Documentation section to mention STORY.md:

```markdown
## Documentation

- [README.md](README.md) - Project overview, installation, and usage
- [STORY.md](STORY.md) - Narrative explanation of the visualization
- [docs/API.md](docs/API.md) - Python API reference
- [METHODOLOGY.md](METHODOLOGY.md) - Mathematical formulation and algorithm details
- [ROADMAP.md](ROADMAP.md) - Implementation phases and roadmap
- [docs/archive/tab_strategy.md](docs/archive/tab_strategy.md) - Tab structure design rationale (archived)
```

#### 4. Update README.md
**File**: `README.md`

Add STORY.md to any documentation section if one exists.

### Success Criteria:

#### Automated Verification:
- [ ] Build succeeds: `npm run build`
- [ ] No unused dependencies warning
- [ ] All tests pass (if any): `npm test`

#### Manual Verification:
- [ ] Full app works correctly
- [ ] Both tabs render content from markdown
- [ ] LaTeX equations display properly
- [ ] Navigation works
- [ ] GitHub renders both markdown files nicely

---

## Testing Strategy

### Unit Tests
No new unit tests required—this is primarily a refactoring that preserves behavior.

### Integration Tests
- Verify markdown imports work at build time
- Verify KaTeX renders equations correctly

### Manual Testing Steps
1. Run `npm run dev` and open localhost:5173
2. Navigate to Method tab—verify LaTeX equations render
3. Navigate to Story tab—verify content displays
4. Click navigation links—verify tab switching works
5. View on mobile viewport—verify responsive layout
6. Open METHODOLOGY.md on GitHub—verify readable
7. Open STORY.md on GitHub—verify readable

## Performance Considerations

- **Bundle size**: react-markdown + plugins adds ~60kb minzipped (acceptable for portfolio)
- **Runtime parsing**: Markdown is parsed at runtime, but content is small enough this is negligible
- **HMR**: Vite's `?raw` import should support hot module replacement for markdown files

## References

- Research document: `thoughts/shared/research/2025-11-25-markdown-consolidation.md`
- METHODOLOGY.md: `METHODOLOGY.md:1-117`
- MethodTab.tsx: `web/src/components/MethodTab.tsx:1-227`
- StoryTab.tsx: `web/src/components/StoryTab.tsx:1-100`
