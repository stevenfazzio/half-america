---
date: 2025-11-25T12:00:00-08:00
researcher: Claude
git_commit: 4fb32a516eab01e48c2f0102fa1948a50e5f3399
branch: master
repository: half-america
topic: "Consolidating documentation: single markdown source for both codebase and web"
tags: [research, documentation, markdown, react, vite, katex]
status: complete
last_updated: 2025-11-25
last_updated_by: Claude
---

# Research: Single Markdown Source for Codebase and Web Documentation

**Date**: 2025-11-25
**Researcher**: Claude
**Git Commit**: 4fb32a516eab01e48c2f0102fa1948a50e5f3399
**Branch**: master
**Repository**: half-america

## Research Question

Should we consolidate `METHODOLOGY.md` and `web/src/components/MethodTab.tsx` into a single markdown file that serves both as codebase documentation and on-site documentation? How would we implement this?

## Summary

**Yes, consolidation is worthwhile and feasible.** The current approach has ~70% content duplication between METHODOLOGY.md and MethodTab.tsx. A single-source approach using `react-markdown` + `remark-math` + `rehype-katex` would:

1. Eliminate content drift between docs and web
2. Keep markdown readable on GitHub
3. Render beautifully with LaTeX math on the website
4. Require minimal infrastructure (~4 new npm packages, no Vite plugins)

**Recommended approach**: Use Vite's built-in `?raw` import with `react-markdown` for runtime rendering.

## Detailed Findings

### Current State: Content Duplication

**METHODOLOGY.md** (117 lines) contains:
- Motivation section explaining the problem
- Data sources & preprocessing (TIGER, ACS, geographic scope)
- Mathematical formulation with LaTeX equations
- Algorithm explanation (max-flow min-cut)
- Post-processing steps
- Implementation stack

**MethodTab.tsx** (227 lines) contains:
- Nearly identical content, reformatted as JSX
- Same LaTeX equations rendered via `@matejmazur/react-katex`
- Additional styling with custom CSS classes
- Navigation links to other tabs

**Overlap**: ~80% of the content is duplicated. The main differences:
- MethodTab has styled "card" sections
- MethodTab has tab navigation
- METHODOLOGY.md has slightly more detail in some areas

### StoryTab.tsx: Similar Opportunity

**StoryTab.tsx** (101 lines) contains narrative content that could also be extracted to `STORY.md`:
- "Half of America" introduction
- San Bernardino problem explanation
- Census tract approach
- Smoothness slider explanation

This content doesn't currently exist as a separate markdown file.

### Recommended Implementation: react-markdown + ?raw

**Why this approach**:
1. **LaTeX-friendly**: `remark-math` + `rehype-katex` handle math without escaping issues (unlike MDX)
2. **Single source**: Standard `.md` files work on GitHub AND render in web app
3. **No Vite plugins needed**: Uses built-in `?raw` import suffix
4. **Already have KaTeX**: Project already depends on `katex` for MethodTab

**Required packages**:
```bash
npm install react-markdown remark-math rehype-katex
# katex already installed
```

**TypeScript declaration** (add to `web/src/vite-env.d.ts`):
```typescript
declare module '*.md?raw' {
  const content: string
  export default content
}
```

**Component pattern**:
```tsx
import ReactMarkdown from 'react-markdown'
import remarkMath from 'remark-math'
import rehypeKatex from 'rehype-katex'
import 'katex/dist/katex.min.css'
import methodologyContent from '../../../METHODOLOGY.md?raw'

export function MethodTab() {
  return (
    <div className="method-tab">
      <div className="method-content">
        <ReactMarkdown
          remarkPlugins={[remarkMath]}
          rehypePlugins={[rehypeKatex]}
        >
          {methodologyContent}
        </ReactMarkdown>
        {/* Keep navigation links as JSX */}
        <TabLinks />
      </div>
    </div>
  )
}
```

### CSS Compatibility Analysis

The current CSS approach uses descendant selectors that would work with markdown:

**Works automatically**:
- `h1`, `h2`, `h3` headings
- `p` paragraphs
- `strong`, `em` emphasis
- `a` links
- `ul`, `li` lists
- `hr` dividers

**Needs custom handling**:
- `.hook` (intro blockquote) - use custom blockquote renderer
- `.section-card` (bordered boxes) - use custom div or HTML-in-markdown
- `.equation-hero` (highlighted equation) - use custom component
- `.tab-links` (navigation) - keep as separate JSX component

**Recommendation**: Use react-markdown's `components` prop to map markdown elements to styled components:

```tsx
<ReactMarkdown
  components={{
    blockquote: ({children}) => <blockquote className="hook">{children}</blockquote>,
    hr: () => <hr className="section-divider" />,
  }}
>
```

### Alternative Approaches Considered

| Approach | Pros | Cons |
|----------|------|------|
| **react-markdown + ?raw** | Simple, LaTeX-friendly, pure .md | Runtime parsing overhead |
| **MDX** | Build-time, JSX in markdown | LaTeX escaping nightmares |
| **vite-plugin-markdown** | Multiple formats | Extra complexity |
| **Keep separate** | No changes needed | Content drift, maintenance burden |

**MDX is NOT recommended** because:
- Backslashes in LaTeX confuse the MDX parser
- Underscores in math conflict with markdown italics
- MDX files aren't as portable (GitHub renders differently)

### Proposed File Structure

```
half-america/
├── METHODOLOGY.md          # Single source (enhanced from current)
├── STORY.md                # New file extracted from StoryTab
├── web/src/components/
│   ├── MethodTab.tsx       # Renders METHODOLOGY.md + navigation
│   ├── StoryTab.tsx        # Renders STORY.md + navigation
│   └── MarkdownRenderer.tsx # Shared component with styling
```

### Migration Strategy

**Phase 1: MethodTab consolidation**
1. Install react-markdown, remark-math, rehype-katex
2. Add TypeScript declaration for `*.md?raw`
3. Enhance METHODOLOGY.md with any content unique to MethodTab
4. Create `MarkdownRenderer` component with styling
5. Refactor MethodTab to import and render markdown
6. Keep tab navigation as separate JSX

**Phase 2: StoryTab consolidation**
1. Create STORY.md from StoryTab content
2. Refactor StoryTab to render markdown
3. Reuse MarkdownRenderer component

**Phase 3: CSS consolidation**
1. Extract shared styles to a `prose.css` or similar
2. Reduce duplication between MethodTab.css and StoryTab.css

### Gotchas and Considerations

1. **Block math syntax**: Both `$$` delimiters must be on separate lines:
   ```markdown
   $$
   E(X) = \lambda \sum ...
   $$
   ```

2. **KaTeX CSS must be imported**: Either globally or in the component

3. **Custom sections**: Some MethodTab sections (`.section-card`, `.terminology-note`) use custom styling. Options:
   - Use HTML-in-markdown with classes
   - Define custom markdown extensions
   - Keep these as JSX components interspersed with markdown

4. **Bundle size**: react-markdown + plugins adds ~60kb minzipped (acceptable for portfolio)

5. **Navigation**: Tab links should remain as React components, not markdown

## Code References

- `METHODOLOGY.md:1-117` - Current codebase documentation
- `web/src/components/MethodTab.tsx:1-227` - Current web component
- `web/src/components/StoryTab.tsx:1-101` - Story content (no markdown equivalent)
- `web/src/components/MethodTab.css:1-278` - Method tab styling
- `web/src/components/StoryTab.css:1-143` - Story tab styling
- `web/vite.config.ts:1-8` - Current Vite config (no markdown plugins)
- `web/package.json:17-18` - Already has katex dependency

## Architecture Insights

The current architecture separates concerns well:
- Data processing in Python (`src/half_america/`)
- Static documentation in markdown (root level)
- Web visualization in React (`web/`)

Consolidating documentation follows this pattern by keeping the source of truth in markdown files while rendering them for web consumption.

## Open Questions

1. **Should STORY.md exist at repo root or in `docs/`?** Root keeps it visible, docs/ is more organized.

RESPONSE: Let's keep it in root.

2. **How to handle the `.section-card` styling?** Options:
   - Use `<div class="section-card">` HTML in markdown (works but verbose)
   - Create custom remark plugin (complex)
   - Accept simpler styling for markdown sections
   RESPONSE: I'm fine with simpler styling

3. **Should we also render README.md sections in the app?** Could add an "About" or "Getting Started" tab.
RESPONSE: No.

4. **Hot reloading**: Does Vite's `?raw` import support HMR for markdown files? (Likely yes, but needs testing)

## Recommendation

**Proceed with consolidation using react-markdown.** The benefits outweigh the costs:

| Benefit | Impact |
|---------|--------|
| Single source of truth | High - eliminates content drift |
| GitHub-readable docs | High - works without build step |
| Reduced maintenance | Medium - one place to update |
| Implementation effort | Low - ~2-3 hours of work |

Start with MethodTab since it has the most duplication, then apply the pattern to StoryTab.
