# Story Tab Content Implementation Plan

## Overview

Add narrative content to the Story tab to explain the "Half of America" visualization for a general audience. The content follows a "martini glass" structure: author-driven storytelling that guides readers through the key insight, then transitions to reader-driven exploration via links to the Map tab.

## Current State Analysis

**What exists:**
- `web/src/components/StoryTab.tsx:1-16` - Stub component with placeholder content
- `web/src/components/StoryTab.css:1-46` - Basic styling (container, h1, subtitle, placeholder cards)

**What's missing:**
- Actual narrative content
- CSS styles for h2, paragraphs, blockquotes, section dividers
- Statistics display (land area percentage)
- Links to other tabs
- Image placeholders for future visual assets

**Data available in TopoJSON:**
- `population_selected`: ~165 million at λ=0.50
- `area_sqm`: ~111,115 km² (~1.1% of US land area, roughly Virginia-sized)

## Desired End State

The Story tab displays:
1. An engaging narrative explaining what users are seeing
2. The "evolution story" (San Bernardino → Dust → Bridges → Solution)
3. An accessible explanation of the smoothness slider
4. Links to the Map and Method tabs
5. Placeholder divs for future images/diagrams

**Verification:**
- Story tab renders without errors at `#story`
- Content follows the voice guide: clear / pedagogical / confident
- No marketing tone or jargon
- Build passes: `npm run build`
- Lint passes: `npm run lint`

## What We're NOT Doing

- Scrollytelling / scroll-triggered animations (deferred)
- Static images showing the evolution (placeholders only, asset creation deferred to Phase 6)
- Dynamic statistics from loaded data (use hard-coded values for v1)
- Mobile-specific content adjustments beyond existing responsive CSS

## Implementation Approach

Single-phase implementation: Update StoryTab.tsx with content and StoryTab.css with additional styles. Keep it simple - pure static content with inline tab navigation.

---

## Phase 1: Add Story Tab Content and Styling

### Overview
Replace placeholder content with the full narrative, add necessary CSS styles, and implement tab navigation links.

### Changes Required:

#### 1. StoryTab.css - Add new styles
**File**: `web/src/components/StoryTab.css`
**Changes**: Add styles for h2 headings, paragraphs, blockquotes, section dividers, tab links, and image placeholders.

```css
/* Add after existing styles */

.story-content h2 {
  font-size: 24px;
  font-weight: 600;
  margin: 32px 0 16px 0;
  color: rgba(255, 255, 255, 0.95);
}

.story-content p {
  font-size: 16px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 16px 0;
}

.story-content .hook {
  font-size: 20px;
  font-style: italic;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 32px 0;
  padding-left: 20px;
  border-left: 3px solid #0072B2;
}

.story-content .section-divider {
  border: none;
  border-top: 1px solid rgba(255, 255, 255, 0.15);
  margin: 32px 0;
}

.story-content .stat-highlight {
  font-size: 18px;
  font-weight: 600;
  color: #0072B2;
}

.story-content strong {
  color: rgba(255, 255, 255, 0.95);
}

.story-content .section-card {
  padding: 20px 24px;
  background: rgba(30, 30, 30, 0.95);
  border-radius: 8px;
  margin: 24px 0;
}

.story-content .section-card h3 {
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 8px 0;
}

.story-content .section-card p {
  margin: 0;
  font-size: 14px;
}

.story-content .tab-links {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 32px;
}

.story-content .tab-link {
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

.story-content .tab-link:hover {
  background: rgba(0, 114, 178, 0.25);
  border-color: rgba(0, 114, 178, 0.5);
}

.story-content .image-placeholder {
  background: rgba(255, 255, 255, 0.05);
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  color: rgba(255, 255, 255, 0.4);
  font-size: 14px;
  margin: 24px 0;
}
```

#### 2. StoryTab.tsx - Add content
**File**: `web/src/components/StoryTab.tsx`
**Changes**: Replace placeholder with full narrative content.

```tsx
import './StoryTab.css';

export function StoryTab() {
  const handleTabClick = (tab: string) => (e: React.MouseEvent) => {
    e.preventDefault();
    window.location.hash = tab;
  };

  return (
    <div className="story-tab" role="tabpanel" id="story-tab" aria-labelledby="story">
      <div className="story-content">
        <h1>Half of America</h1>
        <p className="subtitle">Where do half of all Americans actually live?</p>

        <p className="hook">
          What if half of all Americans lived in an area smaller than you'd expect?
        </p>

        <h2>The Surprising Answer</h2>
        <p>
          Half of the United States population—over <span className="stat-highlight">165 million people</span>—lives
          in just <span className="stat-highlight">1.1% of the country's land area</span>. That's roughly the size of Virginia.
        </p>
        <p>
          The blue shapes on the map represent these areas: dense urban cores and their
          surrounding suburbs where Americans have concentrated. The rest of the country? Mostly empty.
        </p>

        <hr className="section-divider" />

        <h2>Why This Map Looks Different</h2>
        <p>
          You've probably seen maps like this before. They usually show counties, and they
          usually look wrong. Here's why we took a different approach:
        </p>

        <div className="section-card">
          <h3>The San Bernardino Problem</h3>
          <p>
            San Bernardino County, California is larger than nine US states. It's also mostly
            desert. When you highlight it on a "half of America" map, you're including
            thousands of square miles where almost nobody lives.
          </p>
        </div>

        <div className="section-card">
          <h3>Going Smaller: Census Tracts</h3>
          <p>
            We used Census Tracts instead—about 73,000 small neighborhoods across the country.
            This gives us much higher resolution, but creates a new problem: thousands of
            tiny disconnected dots that are hard to visually process.
          </p>
        </div>

        <div className="section-card">
          <h3>Finding the Shape</h3>
          <p>
            The solution was to let the boundaries find themselves. Using an optimization
            technique from computer vision, we minimize the <em>perimeter</em> of the selected
            regions. This produces smooth, organic shapes that are both accurate and visually clear.
          </p>
        </div>

        <div className="image-placeholder">
          [Evolution diagram: County → Tracts → Bridges → Smooth - Coming in Phase 6]
        </div>

        <hr className="section-divider" />

        <h2>The Smoothness Slider</h2>
        <p>
          The slider on the map controls a tradeoff between precision and visual clarity:
        </p>
        <p>
          <strong>Low values</strong> give you maximum precision. You see every dense
          neighborhood, but as scattered dots that are hard to reason about.
        </p>
        <p>
          <strong>High values</strong> give you maximum smoothness. The regions merge into
          coherent shapes that reveal the overall pattern of where Americans live.
        </p>
        <p>
          There's no "correct" setting—it depends on what you want to see.
        </p>

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
  );
}
```

### Success Criteria:

#### Automated Verification:
- [ ] Build passes: `cd web && npm run build`
- [ ] Lint passes: `cd web && npm run lint`
- [ ] Dev server starts: `cd web && npm run dev`
- [ ] Story tab accessible at `http://localhost:5173/#story`

#### Manual Verification:
- [ ] Content renders correctly with proper typography
- [ ] Links to Map and Method tabs work
- [ ] Mobile layout looks reasonable (responsive CSS already exists)
- [ ] Dark background and white text provide good contrast
- [ ] No marketing tone - reads as a thoughtful guide

---

## Testing Strategy

### Automated Tests:
- Build compilation verifies TypeScript correctness
- ESLint checks code quality

### Manual Testing Steps:
1. Navigate to `#story` - content should render
2. Click "View the Interactive Map →" - should navigate to `#map`
3. Click "Read the Full Methodology →" - should navigate to `#method`
4. Resize browser to mobile width - content should remain readable
5. Read through content - verify no typos or awkward phrasing

## Future Enhancements (Phase 6)

- Create static images showing the evolution (San Bernardino → Tracts → Bridges → Smooth)
- Replace `image-placeholder` div with actual `<img>` elements
- Consider dynamic statistics from loaded TopoJSON data

## References

- Research document: `thoughts/shared/research/2025-11-23-story-tab-content.md`
- Tab strategy guide: `docs/tab_strategy.md`
- Current implementation: `web/src/components/StoryTab.tsx`
