---
date: 2025-11-23T17:55:00-05:00
researcher: Claude
git_commit: c927f2fae03b81cccbabaae0c738dd0259026be5
branch: master
repository: half-america
topic: "Add content to Story tab (narrative explanation for general audience)"
tags: [research, story-tab, narrative, content-strategy, frontend]
status: complete
last_updated: 2025-11-23
last_updated_by: Claude
---

# Research: Story Tab Content Strategy

**Date**: 2025-11-23T17:55:00-05:00
**Researcher**: Claude
**Git Commit**: c927f2fae03b81cccbabaae0c738dd0259026be5
**Branch**: master
**Repository**: half-america

## Research Question

How should we add content to the Story tab to create a compelling narrative explanation for a general audience?

## Summary

The Story tab should follow a **"martini glass" narrative structure**: start with author-driven storytelling that guides the reader through the key insight, then transition to reader-driven exploration with the lambda slider. The content should:

1. Open with a counterintuitive hook
2. Explain the evolution of the visualization approach (San Bernardino → Dust → Bridges → Solution)
3. Use accessible language without technical jargon
4. Maintain a "clear / pedagogical / confident" voice
5. Avoid marketing tone - write as a guide for intelligent readers
6. Link to the Map tab for exploration and Method tab for technical details

## Detailed Findings

### Content Strategy (from docs/tab_strategy.md)

The tab strategy document establishes clear guidelines:

**Target Audience**: "General-curious readers" who want an approachable story

**Required Elements**:
- A clean intro
- A short section explaining why the naive approach is insufficient
- Brief conclusions

**Voice**: Clear / pedagogical / confident

**Key Principle**: "Don't just describe what we did - explain *why it matters*"

**Critical Warning**: "People *hate* being sold to in this space. Write it as a guide written by someone who respects the reader's intelligence."

### Narrative Arc (from README.md Background)

The README already contains the evolution story that should form the backbone of the Story tab:

1. **The San Bernardino Problem**: County-level maps include vast empty areas
2. **The Dust Problem**: Census tracts create thousands of tiny disconnected specks
3. **The Bridge Problem**: Minimizing region count created oddly-shaped regions
4. **The Solution**: Minimize perimeter for smooth, organic shapes

### Best Practices from Web Research

**Martini Glass Structure** (Data.Europa.eu):
- Start author-driven: introduce data, present curated view, share observations
- Transition to reader-driven: give controls to explore (the lambda slider)

**The Pudding's Approach**:
- "Data has to really speak and provide a conclusion"
- Prioritize longevity over news cycles
- Open with emotional scale rather than methodology

**99% Invisible's Population Map Article**:
- Opens with a relatable misconception
- Demystifies methodology in concrete terms
- Uses progressive zoom from global to specific
- Maintains an accessible, curious tone

**Urban Institute Do No Harm Guide**:
- "Limit the 'big idea' to a central theme"
- "Use no more than two or three concepts to reduce cognitive load"
- "Carefully select only the data that supports clarity of intent"

### Scrollytelling Consideration

**Recommendation**: Static narrative for v1, consider scrollytelling later.

Scrollytelling (scroll-triggered animations) is powerful but:
- Adds significant implementation complexity
- Can be "distracting from the story at hand"
- Has accessibility concerns on older devices
- May be overkill for a three-section narrative

The current static tab structure with a link to the interactive Map tab follows the martini glass pattern without technical overhead.

## Recommended Story Tab Structure

### Section 1: Opening Hook
> "What if half of all Americans lived in an area smaller than you'd expect?"

- Start with counterintuitive insight
- Don't reveal everything immediately
- Create curiosity

### Section 2: The Revelation
- Show that 50% of Americans live in a surprisingly small area
- Use concrete comparisons (e.g., "smaller than X states combined")
- Keep it brief and impactful

### Section 3: The Evolution (Why This Visualization)
Brief version of the four problems:

1. **The San Bernardino Problem**: County maps include vast deserts
2. **The Dust Problem**: Census tracts create visual noise
3. **The Bridge Problem**: Minimizing regions creates odd shapes
4. **The Solution**: Minimize perimeter for smooth, organic boundaries

### Section 4: The Tradeoff (Lambda Explained)
- Explain the slider in accessible terms
- "Precision vs. visual clarity" framing
- Don't use the word "lambda" - call it "smoothness" or "surface tension"

### Section 5: Call to Explore
- Link to Map tab: "Explore the interactive map"
- Link to Method tab: "Read the full methodology"

## CSS Styling Patterns

The existing StoryTab.css provides the foundation:

| Element | Style |
|---------|-------|
| Container | max-width: 680px, centered |
| h1 | 32px, font-weight: 700 |
| Subtitle | 18px, rgba(255,255,255,0.7) |
| Body text | 14px, rgba(255,255,255,0.7) |
| Cards | background: rgba(30,30,30,0.95), border-radius: 8px |

**Additional styles needed**:
- `h2` headings (recommend 24px, font-weight: 600)
- Paragraph spacing (recommend margin-bottom: 16px)
- Emphasis text (consider accent color #0072B2)
- Blockquote styling for the hook

## Code References

- `web/src/components/StoryTab.tsx:1-16` - Current stub implementation
- `web/src/components/StoryTab.css:1-46` - Existing styles
- `docs/tab_strategy.md:38-60` - Content requirements
- `README.md:12-24` - Evolution narrative source

## Draft Content

Below is a draft of the Story tab content following the recommended structure:

```markdown
# Half of America

**Where do half of all Americans actually live?**

---

## The Surprising Answer

Half of the United States population - over 165 million people - lives in just a tiny fraction of the country's land area. The blue shapes on the map represent these areas: dense urban cores and their surrounding suburbs where Americans have concentrated.

The rest of the country? Mostly empty.

---

## Why This Map Looks Different

You've probably seen maps like this before. They usually show counties, and they usually look wrong.

**The Problem with Counties**

San Bernardino County, California is larger than nine US states. It's also mostly desert. When you highlight it on a "half of America" map, you're including thousands of square miles where almost nobody lives.

**Going Smaller**

We used Census Tracts instead - about 73,000 small neighborhoods across the country. This gives us much higher resolution, but creates a new problem: thousands of tiny disconnected dots that are hard to visually process.

**Finding the Shape**

The solution was to let the boundaries find themselves. Using an optimization technique from computer vision, we minimize the *perimeter* of the selected regions. This produces smooth, organic shapes that are both accurate and visually clear.

---

## The Smoothness Slider

The slider on the map controls a tradeoff:

- **Low values**: Maximum precision. You see every dense neighborhood, but as scattered dots.
- **High values**: Maximum smoothness. The regions merge into coherent blobs that are easier to reason about.

There's no "correct" setting - it depends on what you want to see.

---

## Explore

**[View the Interactive Map →](#map)**

Curious about the math? **[Read the Methodology →](#method)**
```

## Architecture Insights

The Story tab is designed as a simple React functional component. No complex state management needed - it's purely presentational content. Links to other tabs should use `onClick` handlers that update `window.location.hash` (matching the existing pattern in App.tsx).

## Historical Context (from thoughts/)

- `thoughts/shared/research/2025-11-22-documentation-improvement-recommendations.md` - Contains the "evolution story" framework and narrative framing recommendations
- `thoughts/shared/plans/2025-11-22-documentation-framing-improvements.md` - Plan for documentation improvements that informed README content
- `docs/tab_strategy.md` - Primary content strategy document with voice and tone guidance

## Related Research

- `thoughts/shared/plans/2025-11-23-tab-structure-implementation.md` - Tab implementation plan (completed)
- `thoughts/shared/research/2025-11-23-tab-structure-implementation.md` - Tab structure research

## Open Questions

1. **Images/Diagrams**: Should the Story tab include static images showing the evolution (county → tracts → bridges → smooth)? This would require creating/exporting these assets.
RESPONSE: Let's postpone the creation of these assets for now, and focus on the text (leaving placeholders for the actual content). We should add a milestone to Phase 6 for creating/embedding these assets.

2. **Statistics**: Should we include specific numbers (e.g., "covering only X% of land area")? This data is available in the TopoJSON metadata but would need to be displayed.
RESPONSE: That sounds reasonable, if it's not too tricky.

3. **Mobile Experience**: The 680px max-width works well on desktop but may need additional consideration for very small screens.

4. **Scrollytelling Later**: If we want scroll-triggered animations in the future, libraries like Scrollama or react-scrollama could be integrated, but this adds complexity.
RESPONSE: Let's hold off on this for now.

## External Sources

- [Data.Europa.eu - Martini Glass Story Structure](https://data.europa.eu/apps/data-visualisation-guide/martini-glass-story-structure)
- [Storybench - How The Pudding Structures Stories](https://www.storybench.org/pudding-structures-stories-visual-essays/)
- [99% Invisible - 99 Darkness](https://99percentinvisible.org/article/99-darkness-see-half-worlds-population-lives-1-land/)
- [Urban Institute - Do No Harm Guide](https://www.urban.org/research/publication/do-no-harm-guide-centering-accessibility-data-visualization)
- [The Pudding - Human Terrain](https://pudding.cool/2018/10/city_3d/)
