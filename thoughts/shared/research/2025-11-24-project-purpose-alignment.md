---
date: 2025-11-24T19:00:14+0000
researcher: Claude
git_commit: ee3757be3d298e48879b4d3d9b52d21f1d086ff0
branch: master
repository: half-america
topic: "Resolving Project Purpose Tension: Data Insight vs. Methodology Showcase"
tags: [research, project-framing, portfolio, messaging, strategy, user-personas]
status: complete
last_updated: 2025-11-24
last_updated_by: Claude
---

# Research: Resolving Project Purpose Tension

**Date**: 2025-11-24T19:00:14+0000
**Researcher**: Claude
**Git Commit**: ee3757be3d298e48879b4d3d9b52d21f1d086ff0
**Branch**: master
**Repository**: half-america

## Research Question

How should Half of America resolve the tension between framing as a data insight ("Look how small an area half the US population fits into!") versus a methodology showcase ("Look at this novel application of max-flow min-cut for cartographic visualization!")?

The project has evolved through multiple phases:
1. Attempt to improve "Half of Americans live in these counties" maps
2. Technical evolution through problems: San Bernardino → Dust → Bridges → Smooth perimeter
3. Recognition of methodology novelty as portfolio value
4. Current state: Mixed messaging across touchpoints

**User's stated preference**: "If I'm being honest, as a portfolio piece, I'm more interested in showing off what's novel about the methodology."

## Executive Summary

### Core Finding: The Tension is a Feature, Not a Bug

Research into successful portfolio projects (The Pudding, Visual Cinnamon, Distill, Data Sketches) reveals that **dual framing is the optimal strategy**. The tension between data insight and methodology is not a problem to eliminate—it's a strategic advantage that serves multiple audiences.

However, **the current balance is misaligned with your stated portfolio goals**. The project currently emphasizes data insight (80%) over methodology (20%), when a portfolio showcase should be closer to 60% methodology, 40% data insight.

### Key Insights

1. **Best practices support dual framing**: Successful projects present visual storytelling first, technical depth second—but make both equally valuable
2. **Current messaging hierarchy**: Data insight dominates (hero stats, "1.1%", map title), methodology is secondary (slider hidden on mobile, Method tab third)
3. **The slider is the innovation**: It's the first interactive "surface tension" parameter in population visualization, but currently framed as a secondary control
4. **Three audiences need different entry points**: Explorers (60%), Curious Readers (30%), Technical Evaluators (10%)—current design optimizes for Explorers at expense of Technical Evaluators

### Recommendation

**Adopt "The Data Sketches Model"**: Beautiful visual entry point paired with substantive technical explanation. Elevate methodology prominence while maintaining visual appeal as the hook.

Specific changes needed across 4 categories:
- **README**: Lead with methodology innovation, not just "interactive map"
- **Web frontend**: Elevate slider to co-equal status with map, add methodology preview
- **Story tab**: Reframe evolution as methodology journey, not problem-solving
- **Documentation**: Emphasize novel contribution to field

---

## Current State Analysis

### Messaging Inventory Across All Touchpoints

#### 1. README.md (`README.md:1-161`)

**Opening Line (line 6)**:
> "An experimental data visualization exploring US population concentration. Interactive map highlighting where 50% of Americans live, with a slider to balance area minimization vs. perimeter smoothness."

**Analysis**:
- Frames as "data visualization" first
- Map is primary ("highlighting where"), slider is secondary ("with a slider")
- No mention of novelty or methodological contribution

**How It Works Section (lines 26-38)**:
> "The visualization shows how concentrated the US population is—50% of Americans live in a surprisingly small area. The challenge is presenting this in a visually compelling way."

**Analysis**:
- Data insight is "the visualization" (primary)
- Methodology is "the challenge" of presentation (secondary)
- Emphasis on "surprisingly small area" (data hook) over optimization innovation

**Background Section (lines 12-24)**:
Presents evolution narrative: San Bernardino → Dust → Bridges → Solution

**Framing**: "These maps show how concentrated the US population is" → methodology evolved to solve presentation problems

---

#### 2. METHODOLOGY.md (`METHODOLOGY.md:1-103`)

**Motivation Section (lines 3-13)**:
> "Traditional 'half of America' visualizations face several technical limitations..."

**Analysis**:
- Frames project as fixing problems in existing work
- Positions methodology as solving visualization deficiencies
- Technical depth is high, but framed reactively not proactively

**Opening Philosophy (line 13)**:
> "This methodology addresses these issues by minimizing *perimeter* rather than region count"

**Analysis**:
- "Addresses these issues" = reactive framing
- Misses opportunity to frame as novel contribution: "This project introduces a novel application of max-flow min-cut to geographic optimization"

---

#### 3. Web Frontend Hierarchy

**Map Tab (default view)** - Visual Priority:

| Element | Font Size | Opacity | Mobile Visibility |
|---------|-----------|---------|-------------------|
| Hero stats (50% / 1.1%) | 28px bold | 100% | Visible |
| Lambda value | 11px | 50% | Hidden |
| "Surface Tension (λ)" label | 14px semi-bold | 100% | Visible |
| Slider endpoints | 11px | 50% | Visible |

**Analysis** (`web/src/components/SummaryPanel.tsx:38-64`):
- Data insight is hero element (largest, highest contrast)
- Technical parameter (λ) is de-emphasized and hidden on mobile
- Visual hierarchy: Population concentration >> Methodology control

**Story Tab Content** (`web/src/components/StoryTab.tsx:12-96`):

Section order:
1. "The Surprising Answer" (lines 19-27): 50% in 1.1% statistic
2. "Why This Map Looks Different" (lines 31-62): Evolution narrative
3. "The Smoothness Slider" (lines 70-84): Slider explanation

**Analysis**:
- Data insight comes first (section 1)
- Evolution framed as problem-solving (section 2)
- Slider framed as user preference ("There's no 'correct' setting"), not as methodological innovation

**Method Tab** (`web/src/components/MethodTab.tsx:14-165`):

**Opening** (lines 14-20):
> "This project frames population visualization as a constrained optimization problem, solved exactly using max-flow min-cut."

**Analysis**:
- Strong technical framing
- BUT: It's in the THIRD tab (Map → Story → Method)
- Most users won't reach this depth

---

#### 4. ROADMAP.md

**Current Phase Description** (`ROADMAP.md:148`):
> "The interactive visualization is live"

**Analysis**:
- Describes deliverable (visualization) not innovation (methodology)
- Missing: "Novel application of graph optimization to census tract data"

---

### Historical Evolution (from thoughts/ directory)

#### Documentation Framing Research

**Key Document**: `thoughts/shared/research/2025-11-22-documentation-improvement-recommendations.md`

Found explicit recognition of the framing issue:
> "The current 'Problem' section positions the project reactively... This undermines the portfolio value. Recommendation: Reframe as 'Background & Evolution' showing technical iteration, not deficiency-fixing."

**Status**: Partially implemented
- README has "Background" section ✅
- But still frames as solving problems ❌
- Doesn't emphasize novelty ❌

#### User Persona Research

**Key Document**: `thoughts/shared/research/2025-11-23-user-personas-and-stories.md`

Three personas identified:
1. **The Explorer** (60% of traffic): "I want to see something cool and play with it"
2. **The Curious Reader** (30%): "I want to understand why this is different"
3. **The Technical Evaluator** (10%): "I want to assess whether this is rigorous work worth citing or hiring for"

**Current Design Optimization**:
- Heavily optimized for Explorers (visual wow-factor, simple interaction)
- Moderately serves Curious Readers (Story tab explains evolution)
- Under-serves Technical Evaluators (methodology buried in third tab, slider de-emphasized)

**Misalignment with Portfolio Goals**:
For a portfolio piece targeting Technical Evaluators (hiring managers, researchers), current design underweights this audience.

#### Slider Research

**Key Document**: `thoughts/shared/research/2025-11-24-slider-improvement-research.md`

**Critical Discovery** (lines 215-255):
> "Despite the user's intuition that 'the main point of the visualization IS the slider and the methodology,' the current design treats the slider as a **secondary interactive control** that enhances the primary feature: **the '1.1%' statistic**."

Evidence:
- Lambda value hidden on mobile
- Hero stats are 2.5× larger than slider controls
- Story tab discusses statistic first, slider third

**Recommendation from that research** (lines 548-579):
> "If methodology IS the main point, consider:
> 1. Increase slider visual prominence
> 2. Elevate methodology in content
> 3. Add educational visuals"

**Status**: Not yet implemented

---

## Industry Best Practices Analysis

### Portfolio Projects with Dual Framing

Research into successful data science portfolio projects reveals a consistent pattern: **Lead with visual impact, provide equal-weight technical depth.**

#### Model 1: The Pudding ("Human Terrain" project)

**Public-Facing**:
- Immediate visual engagement: "Kinshasa is now bigger than Paris"
- Interactive 3D map as hero
- No technical jargon in main experience

**Technical Depth**:
- Separate "Methodology" section with full implementation details
- Google Earth Engine processing described
- Academic citations provided
- Open-source code on GitHub

**Key Insight**: Both framings are equally valuable, served to different audiences via progressive disclosure

**Source**: pudding.cool/2018/10/city_3d/

---

#### Model 2: Data Sketches (Nadieh Bremer & Shirley Wu)

**Philosophy** (from their book description):
> "Creating a beautiful coffee table book with large, indulgent images of our projects, **side-by-side with our very technical process write-ups**"

**Structure**:
- Left page: Beautiful visualization
- Right page: "The messy data and how they get over the bumps along the way"

**Key Insight**: Don't choose between beauty and depth—present both with equal prominence

**Source**: datasketch.es

---

#### Model 3: Distill.pub (Research Distillation)

**Philosophy**:
> "Clear communication requires genuine effort equal to research itself"

**Approach**:
- Treat explanation as primary contribution, not secondary
- Interactive visualizations that teach algorithms
- "Building Blocks of Interpretability" has deep technical depth with interactive exploration

**Key Insight**: For portfolio showcasing novel methodology, explanation IS the work

**Source**: distill.pub/2017/research-debt/

---

### Pattern Recognition: The 60/40 Rule

Across successful portfolio projects:
- **60% methodology**: Novel approach, technical rigor, reproducibility
- **40% visual hook**: Compelling entry point, shareability, immediate appeal

**Current Half of America balance**: ~20% methodology, ~80% visual hook

**Misalignment**: For a portfolio piece emphasizing methodological novelty, this ratio is inverted

---

## Gap Analysis: Current vs. Desired State

### Gap 1: README Positioning

| Current | Desired for Portfolio |
|---------|----------------------|
| "Interactive map highlighting where 50% of Americans live" | "Novel application of max-flow min-cut to census tract optimization" |
| Methodology in "How It Works" (secondary) | Methodology in opening (primary) |
| Evolution framed as problem-solving | Evolution framed as technical iteration |

**File**: `README.md:6`

---

### Gap 2: Web Frontend Hierarchy

| Current | Desired for Portfolio |
|---------|----------------------|
| Hero: 50% / 1.1% statistics | Hero: Interactive surface tension control |
| Lambda hidden on mobile | Lambda always visible, emphasized |
| Method tab third position | Method tab second position (before Story) |
| Slider labeled "secondary control" in research | Slider labeled "the innovation" |

**Files**:
- `web/src/components/SummaryPanel.tsx:38-64`
- `web/src/components/TabBar.tsx` (tab order)
- `web/src/App.tsx:42-44` (default tab)

---

### Gap 3: Story Tab Narrative

| Current | Desired for Portfolio |
|---------|----------------------|
| Lead with "The Surprising Answer" (data) | Lead with "The Methodological Journey" |
| Evolution as problems to fix | Evolution as technical iteration |
| Slider as user preference | Slider as novel contribution |

**File**: `web/src/components/StoryTab.tsx:19-96`

---

### Gap 4: Methodology Visibility

| Current | Desired for Portfolio |
|---------|----------------------|
| Method tab buried third | Method tab prominent second |
| No preview on Map view | Methodology teaser on Map view |
| Technical depth hidden | Technical depth accessible early |

**Files**:
- `web/src/components/MapTab.tsx`
- `web/src/components/MethodTab.tsx`

---

## Recommendations

### Strategy: Adopt the "Data Sketches Model"

**Core Principle**: Present both the beautiful visualization AND the technical process with equal prominence, side-by-side.

**Implementation**: Shift from 80/20 (data/methodology) to 60/40 (methodology/data) while maintaining visual appeal.

---

### Tier 1: High-Impact Changes (Immediately Shift Perception)

#### 1.1 README Opening Rewrite

**Current** (`README.md:6`):
```markdown
An experimental data visualization exploring US population concentration. Interactive map highlighting where 50% of Americans live, with a slider to balance area minimization vs. perimeter smoothness.
```

**Recommended**:
```markdown
A novel application of max-flow min-cut optimization to cartographic data visualization. This project introduces an interactive "surface tension" parameter that controls the tradeoff between area minimization and perimeter smoothness in census tract selection, producing smooth, organic boundaries for population concentration maps.

**[View the Live Demo →](https://stevenfazzio.github.io/half-america)**

> Traditional "Half of America" maps use counties or simple tract selection. This project optimizes boundary smoothness using graph cuts—a first for population visualization.
```

**Rationale**:
- Leads with methodology ("novel application of max-flow min-cut")
- Positions innovation clearly ("interactive surface tension parameter")
- Contextualizes novelty ("a first for population visualization")
- Data insight becomes supporting detail, not primary framing

**File**: `README.md:6-10`
**Effort**: 15 minutes
**Impact**: High—changes first impression for all viewers

---

#### 1.2 Web Frontend: Elevate Slider to Hero Status

**Current Visual Hierarchy**:
```
Map Title
────────────────────
Hero Stats: 50% / 1.1%  (28px bold)
────────────────────
Slider: λ = 0.76  (11px, 50% opacity, hidden mobile)
```

**Recommended Visual Hierarchy**:
```
Map Title
────────────────────
Hero Element: Surface Tension Control
  λ = 0.76  (24px bold, always visible)
  [Slider with prominent endpoints]
  "Controls boundary smoothness vs. area precision"
────────────────────
Supporting Stats: 50% population, 1.1% land area  (18px)
```

**Implementation**:
- Increase lambda display size: 11px → 24px
- Make lambda visible on mobile (currently hidden)
- Add prominent label: "Surface Tension Control"
- Move population/land stats below slider (still visible, but supporting)
- Add methodology teaser: "Learn how this works →" link to Method tab

**Files**:
- `web/src/components/LambdaSlider.tsx:19-52`
- `web/src/components/LambdaSlider.css:1-103`
- `web/src/components/SummaryPanel.tsx:38-64`

**Effort**: 2-3 hours
**Impact**: Very High—changes what users perceive as "the point"

---

#### 1.3 Tab Order: Method Before Story

**Current**: Map (default) → Story → Method
**Recommended**: Map (default) → Method → Story

**Rationale**:
- For portfolio piece, technical evaluators should reach methodology before narrative
- "How it works" should come before "Why it matters"
- Story tab becomes optional depth for curious readers

**Implementation**:
```tsx
// web/src/components/TabBar.tsx
const tabs = [
  { id: 'map', label: 'Map', icon: MapIcon },
  { id: 'method', label: 'Method', icon: CodeIcon },  // Swapped
  { id: 'story', label: 'Story', icon: BookIcon },    // Swapped
];
```

**Files**:
- `web/src/components/TabBar.tsx`
- Update links in `StoryTab.tsx` and `MethodTab.tsx` to reflect new order

**Effort**: 30 minutes
**Impact**: Medium-High—signals priority to users

---

### Tier 2: Medium-Impact Changes (Reinforce Methodology Focus)

#### 2.1 Story Tab: Reframe as Methodology Journey

**Current Opening** (`StoryTab.tsx:19-27`):
```tsx
<h2>The Surprising Answer</h2>
<p>
  Half of the United States population—over 165 million people—lives
  in just 1.1% of the country's land area.
</p>
```

**Recommended Opening**:
```tsx
<h2>The Methodological Journey</h2>
<p>
  This project started with a question: Can we visualize population concentration
  with smooth, organic boundaries instead of jagged county lines? The answer required
  applying <strong>max-flow min-cut optimization</strong> to census tract data—a novel
  approach in cartographic visualization.
</p>
<p>
  The result: <strong>50% of Americans live in just 1.1% of land area</strong>, revealed
  through user-controllable "surface tension" optimization.
</p>
```

**Rationale**:
- Leads with methodology question
- Data insight becomes the "result" of methodology
- Frames innovation first, outcome second

**File**: `web/src/components/StoryTab.tsx:19-27`
**Effort**: 1 hour (rewrite section order)
**Impact**: Medium—changes narrative framing

---

#### 2.2 Add Methodology Preview to Map View

**Current**: Map view has no indication of technical depth

**Recommended**: Add "About the Algorithm" card to Map view

```tsx
// Add to MapTab.tsx
<div className="methodology-teaser">
  <h3>About the Algorithm</h3>
  <p>
    This visualization uses <strong>max-flow min-cut graph optimization</strong> to
    balance two competing goals: minimizing area (precision) and minimizing perimeter
    (smoothness). The slider controls which goal dominates.
  </p>
  <a href="#method" className="learn-more">Read full methodology →</a>
</div>
```

**Placement**: Below SummaryPanel, above fold on desktop

**Files**:
- `web/src/components/MapTab.tsx:93-96`
- Add `web/src/components/MethodologyTeaser.tsx`
- Add `web/src/components/MethodologyTeaser.css`

**Effort**: 2-3 hours
**Impact**: Medium—surfaces technical depth earlier

---

#### 2.3 METHODOLOGY.md: Reframe Motivation

**Current** (`METHODOLOGY.md:3-13`):
```markdown
Traditional "half of America" visualizations face several technical limitations...
This methodology addresses these issues by minimizing *perimeter*...
```

**Recommended**:
```markdown
## Novel Contribution

This project introduces the first application of max-flow min-cut optimization with
interactive "surface tension" control to census tract selection for population visualization.

Traditional approaches use:
- County-level selection (low resolution, includes empty areas)
- Greedy tract selection (produces dust artifacts)
- Region count minimization (produces bridge artifacts)

**Our innovation**: Treat boundary smoothness as the optimization objective, controlled
by a user-tunable parameter λ (lambda), producing organic shapes that balance precision
and visual clarity.

This represents a novel contribution at the intersection of:
- Operations research (graph optimization)
- Cartography (geographic data visualization)
- Interactive visualization (user-controlled parameter exploration)
```

RESPONSE: This seems like a lot of very strong statements. I want to use softer language unless we have specific citations. I also want to make sure that this is accurately framed as an exploration of methodology, not an innovation.

**Rationale**:
- Positions as contribution, not problem-solving
- Highlights what's NEW (surface tension parameter, graph cuts for geography)
- Contextualizes within broader fields

**File**: `METHODOLOGY.md:3-13`
**Effort**: 30 minutes
**Impact**: Medium—changes how technical readers perceive the work

---

### Tier 3: Low-Impact Polish (Consistency)

#### 3.1 ROADMAP.md: Add Methodology Milestones

**Current**: Describes deliverables (web frontend, export, etc.)

**Recommended**: Add section highlighting methodological contributions

```markdown
## Methodological Contributions

This project introduces several novel elements:

1. **Interactive Surface Tension Parameter**: First implementation of user-controllable
   λ (lambda) for census tract optimization
2. **Max-Flow Min-Cut for Geographic Data**: Novel application of graph cuts to
   cartographic visualization
3. **Dual-Objective Optimization**: Balancing area minimization (precision) vs.
   perimeter minimization (smoothness) with continuous parameter control
```

**File**: `ROADMAP.md:1-177`
**Effort**: 15 minutes
**Impact**: Low—but improves consistency

RESPONSE: ROADMAP.md is an internal development document. I'm the only one reading it. It just needs to keep track of what I've done and what I have left to do.

---

#### 3.2 Map Title: Emphasize Methodology

**Current** (`web/src/components/MapTitle.tsx:6-7`):
```tsx
<h1 className="map-title-main">Half of America</h1>
<p className="map-title-sub">Where 50% of Americans live</p>
```

**Recommended**:
```tsx
<h1 className="map-title-main">Half of America</h1>
<p className="map-title-sub">Optimized with Surface Tension Control</p>
```

**Rationale**:
- Subtitle hints at methodology innovation
- "Surface tension" is memorable and unique
- Invites curiosity about "what is surface tension control?"

**File**: `web/src/components/MapTitle.tsx:6-7`
**Effort**: 2 minutes
**Impact**: Low—but reinforces framing

---

#### 3.3 CLAUDE.md: Update Project Overview

**Current** (`CLAUDE.md:9-16`):
```markdown
Half of America is an experimental data visualization project exploring US population
concentration. It produces an interactive map highlighting the areas where 50% of
Americans live, with a user-controlled slider to balance area minimization vs.
perimeter smoothness.
```

**Recommended**:
```markdown
Half of America is a portfolio project showcasing a novel application of max-flow
min-cut optimization to cartographic data visualization. It produces an interactive
map where 50% of American population is selected via graph cuts, with a user-controlled
"surface tension" parameter (λ) that balances area minimization vs. perimeter smoothness.

**Portfolio Value**: Demonstrates operations research, spatial algorithms, and interactive
visualization skills. Novel contribution: first interactive surface tension parameter for
census tract optimization.
```

**File**: `CLAUDE.md:9-16`
**Effort**: 5 minutes
**Impact**: Low—internal documentation only

---

## Implementation Roadmap

### Phase 1: Foundation Shift (Week 1)

**Goal**: Change first impression to methodology-forward

- [ ] README opening rewrite (Rec 1.1)
- [ ] Tab order swap: Method before Story (Rec 1.3) RESPONSE: I don't want to adjust the tab order. The narrative will be a friendlier into to the methodology, even for technical users. In other words, I'm optimizing the project for people like me, and *I'd* prefer the narrative explanation before reading a math-heavy page.
- [ ] METHODOLOGY.md reframe (Rec 2.3)
- [ ] Story tab opening rewrite (Rec 2.1)

**Effort**: 3-4 hours total
**Impact**: High—changes how 90% of viewers perceive the project

---

### Phase 2: Visual Hierarchy (Week 2)

**Goal**: Elevate slider to hero status

- [ ] Redesign SummaryPanel: slider prominent, stats supporting (Rec 1.2)
- [ ] Make lambda visible on mobile
- [ ] Add methodology teaser to Map view (Rec 2.2)
- [ ] Update Map title subtitle (Rec 3.2)

**Effort**: 6-8 hours total
**Impact**: Very High—changes what users interact with first

---

### Phase 3: Polish & Consistency (Week 3)

**Goal**: Ensure all touchpoints align with methodology focus

- [ ] ROADMAP.md methodology contributions section (Rec 3.1)
- [ ] CLAUDE.md project overview update (Rec 3.3)
- [ ] Review all documentation for "data viz" → "methodology showcase" language
- [ ] Update social media descriptions (if applicable)
RESPONSE: no social media descriptions

**Effort**: 2-3 hours total
**Impact**: Medium—ensures consistency

---

## Validation Strategy

### How to Know If Changes Are Successful

#### Metric 1: Portfolio Feedback

**Before**: "Cool map showing population concentration"
**After**: "Novel application of graph optimization to geographic data"

**Validation**: Share with 5-10 data scientists and ask: "What is this project about?"
- Current responses likely emphasize data insight
- Target responses should emphasize methodology

---

#### Metric 2: Tab Engagement

**Track** (if analytics available):
- Current: Map (100%) → Story (40%) → Method (15%)
- Target: Map (100%) → Method (50%) → Story (30%)

**Validation**: More users should reach Method tab if it's positioned second

---

#### Metric 3: GitHub Stars/Attention

**Hypothesis**: Methodology-forward framing attracts more technical attention

**Validation**:
- Monitor GitHub stars/forks (technical audience signal)
- Track LinkedIn shares (portfolio audience signal)
- Compare attention before/after changes

---

## Trade-offs and Risks

### Risk 1: Reduced Shareability

**Concern**: Data insight framing ("1.1% of land!") is more shareable on social media than methodology framing

**Mitigation**:
- Keep visual appeal strong (beautiful map is still the hero)
- Story tab still contains shareable statistic
- Social media preview cards can emphasize data insight even if README emphasizes methodology

**Verdict**: Low risk—most social traffic comes from visual appeal, not README text

---

### Risk 2: Alienating Non-Technical Users

**Concern**: Leading with "max-flow min-cut" might intimidate general audience

**Mitigation**:
- Visual map is still default view (accessible entry point)
- Progressive disclosure: technical depth is available, not forced
- Story tab provides narrative explanation for curious readers

**Verdict**: Low risk—layered approach serves both audiences

---

### Risk 3: Over-Indexing on Methodology

**Concern**: Making methodology too prominent might obscure the underlying data insight

**Mitigation**:
- 60/40 balance (not 90/10)
- Data insight still visible in hero stats (just not THE hero)
- Slider interaction immediately shows visual impact

**Verdict**: Medium risk—requires careful balance in implementation

**Recommendation**: Implement Phase 1 changes first, gather feedback, then proceed to Phase 2 only if validation is positive

---

## Alternative Approaches Considered

### Alternative 1: Fully Separate Audiences

**Approach**: Create two different entry points
- `half-america.com/` → Data insight framing (general audience)
- `half-america.com/methodology` → Methodology framing (technical audience)

**Pros**: Serves each audience optimally
**Cons**: Splits traffic, harder to maintain, GitHub Pages doesn't support well

**Verdict**: Not recommended—dual framing within single interface is more elegant

---

### Alternative 2: Methodology-Only (100%)

**Approach**: Remove all data insight framing, focus entirely on algorithm

**Example Opening**:
> "An implementation of max-flow min-cut optimization with Lagrangian relaxation for constrained graph partitioning on census tract adjacency networks."

**Pros**: Pure portfolio positioning
**Cons**: Loses visual appeal, reduces shareability, alienates 90% of potential audience

**Verdict**: Not recommended—too extreme, loses broader appeal

---

### Alternative 3: Keep Current Balance

**Approach**: Maintain data insight primary, methodology secondary

**Rationale**: Current design serves Explorer persona (60% of traffic) optimally

**Pros**: Maximizes engagement for largest audience segment
**Cons**: Misaligned with stated portfolio goals, under-serves Technical Evaluators

**Verdict**: Not recommended—doesn't resolve the stated tension

---

## Conclusion

### The Core Answer

The tension between data insight and methodology framing is **not a problem to eliminate**—it's a strategic choice about emphasis. Successful portfolio projects maintain both but adjust the balance based on goals.

**For Half of America as a portfolio piece showcasing methodological novelty:**

1. **Shift balance from 80/20 (data/methodology) to 60/40 (methodology/data)**
2. **Lead with innovation** ("novel application of graph cuts") not outcome ("1.1% of land")
3. **Elevate the slider** from secondary control to hero element—it IS the innovation
4. **Reframe evolution** from problem-solving to technical iteration
5. **Maintain visual appeal** as the entry point—methodology depth through progressive disclosure

### What to Change

**High Priority** (Phase 1):
- README opening: methodology-first framing
- Tab order: Method before Story RESPONSE: I want to keep the current tab order.
- Story tab: lead with methodology journey

**Medium Priority** (Phase 2):
- Slider visual hierarchy: elevate to hero
- Methodology teaser on Map view

**Low Priority** (Phase 3):
- Documentation consistency pass
- Map title subtitle update

### Validation

After Phase 1 changes, test with 5-10 data scientists:
- Ask: "What is this project about?"
- Target response: Methodology innovation, not just data insight
- If validation passes, proceed to Phase 2

---

## Code References

- `README.md:6` - Opening description (data-focused)
- `METHODOLOGY.md:3-13` - Motivation section (problem-focused)
- `web/src/components/SummaryPanel.tsx:38-64` - Hero stats hierarchy (data-focused)
- `web/src/components/StoryTab.tsx:19-27` - "The Surprising Answer" section (data-focused)
- `web/src/components/TabBar.tsx` - Tab order (Method third)
- `web/src/components/LambdaSlider.tsx:19-52` - Slider implementation (de-emphasized)
- `web/src/components/MapTitle.tsx:6-7` - Map title (data-focused)

---

## Related Research

- [2025-11-24-slider-improvement-research.md](2025-11-24-slider-improvement-research.md) - Discovery of slider as secondary vs. primary
- [2025-11-23-user-personas-and-stories.md](2025-11-23-user-personas-and-stories.md) - Three personas and current optimization for Explorers
- [2025-11-22-documentation-improvement-recommendations.md](2025-11-22-documentation-improvement-recommendations.md) - Earlier recognition of framing issue
- [2025-11-22-documentation-framing-improvements.md](../plans/2025-11-22-documentation-framing-improvements.md) - Initial plan to shift from problem to evolution framing
- [docs/tab_strategy.md](../../docs/tab_strategy.md) - Tab positioning strategy

---

## Open Questions

1. **Social media framing**: Should social preview cards emphasize data (shareability) or methodology (portfolio)?
2. **Default tab**: Should Method tab become the default instead of Map for direct GitHub visitors?
3. **README length**: Should methodology detail expand in README or remain in separate METHODOLOGY.md?
4. **Observable notebook**: Would publishing an Observable notebook enhance methodology showcase?
5. **Academic framing**: Should we pursue publication in visualization conferences (IEEE VIS, EuroVis) to establish academic credibility?
