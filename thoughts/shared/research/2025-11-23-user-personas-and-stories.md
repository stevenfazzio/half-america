---
date: 2025-11-23T12:00:00-08:00
researcher: Claude
git_commit: 8f73c1e822032d2a2ee0b06e2b7af09c7b1cdd79
branch: master
repository: half-america
topic: "User Personas, Stories, and UX Journey Analysis"
tags: [research, user-experience, personas, user-stories, ux]
status: complete
last_updated: 2025-11-23
last_updated_by: Claude
---

# Research: User Personas, Stories, and UX Journey Analysis

**Date**: 2025-11-23T12:00:00-08:00
**Researcher**: Claude
**Git Commit**: 8f73c1e822032d2a2ee0b06e2b7af09c7b1cdd79
**Branch**: master
**Repository**: half-america

## Research Question

Who are the users of the Half of America site? What are their personas, why are they using the site, and how do they engage with its features? What might interest or confuse them, and in what order might they engage with the various features?

## Summary

The site targets **three distinct user personas** aligned with the tab structure: (1) **Explorers** who want visual discovery, (2) **Curious Readers** who want narrative understanding, and (3) **Technical Evaluators** who want methodological rigor. Each persona has different entry points, engagement patterns, and potential friction points. The most likely user journey starts with the Map tab (visual hook), moves to Story tab (seeking explanation), and optionally to Method tab (validation/deeper understanding).

---

## User Personas

### Persona 1: The Explorer

**Who they are:**
- Data visualization enthusiasts
- Social media browsers (arrived via shared link/screenshot)
- Casual web surfers looking for interesting content
- People who saw the "half of America" meme elsewhere and want to see it done better

**Demographics & Context:**
- Ages 18-55, broad range
- Any education level
- Limited time commitment (30 seconds to 5 minutes)
- Mobile and desktop users equally

**Why they're here:**
- Curiosity sparked by a link, tweet, or mention
- Want to "see" the visualization without reading
- Looking for a quick "wow" moment to share

**What they value:**
- Immediate visual impact
- Interactivity (the slider)
- Shareability
- Minimal cognitive overhead

**User Story:**
> "As an Explorer, I want to immediately see the map and play with the slider so I can understand the visualization without reading anything."

---

### Persona 2: The Curious Reader

**Who they are:**
- People who became intrigued by the map and want to understand it
- Educators seeking examples for teaching geography or data visualization
- Journalists or bloggers researching population distribution
- Thoughtful generalists who enjoy understanding "how things work"

**Demographics & Context:**
- Ages 25-55
- College-educated or intellectually curious
- Moderate time commitment (5-15 minutes)
- More likely on desktop (reading-focused)

**Why they're here:**
- Converted from Explorer after being intrigued by the map
- Want to understand *why* the map looks the way it does
- Seeking context for the "San Bernardino Problem" and other nuances
- Looking for talking points to share with others

**What they value:**
- Clear, jargon-free explanations
- The "aha moment" when they understand the approach
- Honest acknowledgment of limitations
- Respect for their intelligence (not oversimplified)

**User Story:**
> "As a Curious Reader, I want to understand why traditional 'half of America' maps look wrong so I can appreciate what makes this approach different."

---

### Persona 3: The Technical Evaluator

**Who they are:**
- Data scientists, statisticians, or researchers
- Students in computational/spatial fields
- Hiring managers or portfolio reviewers assessing the author's skills
- Academics or practitioners who might cite, replicate, or extend the work

**Demographics & Context:**
- Ages 22-45
- Technical background (CS, math, geography, economics)
- Variable time commitment (10 minutes to deep dive)
- Desktop users (need to evaluate code, equations)

**Why they're here:**
- To evaluate the rigor of the methodology
- To determine if the approach is novel or sound
- To decide if the author is technically competent (portfolio evaluation)
- To potentially replicate, critique, or build upon the work

**What they value:**
- Mathematical precision
- Reproducibility (access to code, data sources)
- Honest methodology (no hand-waving)
- Evidence of good engineering practices

**User Story:**
> "As a Technical Evaluator, I want to see the objective function and algorithm details so I can assess whether this is rigorous work worth citing or hiring for."

---

## User Journeys

### Journey 1: The Social Media Arrival (Explorer → Curious Reader)

**Entry Point:** Shared link on Twitter/LinkedIn/Reddit

**Flow:**
1. **Landing (Map tab):** Sees the visualization immediately. Spends 5-30 seconds panning and zooming.
2. **Discovery:** Notices the slider, drags it. Watches shapes morph. "Oh, that's cool."
3. **Question emerges:** "Wait, why do the shapes change? What is this slider doing?"
4. **Tab navigation:** Clicks "Story" tab to get answers.
5. **Understanding:** Reads about the San Bernardino Problem, Census Tracts, and perimeter optimization. "Ah, that makes sense."
6. **Potential exit:** Most users leave satisfied here.
7. **Optional deep dive:** Some click "Method" tab to see the math.

**Total time:** 3-10 minutes

**What interests them:**
- The immediate visual impact
- The slider's effect on shape smoothness
- The "1.1% of land area" statistic (shareable fact)
- The evolution from county maps to smooth shapes

**What might confuse them:**
- What "lambda" or "surface tension" means (before reading Story tab)
- Why there are multiple disconnected regions
- What the blue shapes actually represent (until they read the subtitle)

---

### Journey 2: The Direct Link to Story (Curious Reader Entry)

**Entry Point:** Blog post or article that links directly to `#story`

**Flow:**
1. **Landing (Story tab):** Starts reading the narrative.
2. **Understanding:** Learns about the problem and solution.
3. **Desire to see:** Clicks "View the Interactive Map" link.
4. **Exploration:** Now plays with the map with context. The slider makes sense.
5. **Optional validation:** Some click "Method" to verify the claims.

**Total time:** 5-15 minutes

**What interests them:**
- The 165 million people / 1.1% of land statistic
- The clear explanation of why county maps fail
- The computer vision connection (unexpected!)

**What might confuse them:**
- The mathematical notation in Method tab (if they venture there without technical background)
- Why lambda goes from 0 to 0.98 instead of 0 to 1

---

### Journey 3: The Portfolio Reviewer (Technical Evaluator)

**Entry Point:** GitHub profile link or resume/portfolio reference

**Flow:**
1. **Landing (Map tab):** Quick visual check. "Looks polished."
2. **Immediate navigation:** Clicks "Method" tab to assess rigor.
3. **Evaluation:** Reviews the objective function, graph construction, binary search algorithm.
4. **Code check:** Clicks GitHub link to examine implementation.
5. **Optional:** Returns to Story tab to see how well the author communicates to non-technical audiences.

**Total time:** 10-30 minutes

**What interests them:**
- The formal mathematical framing
- The choice of max-flow min-cut (solid algorithm choice)
- The implementation stack (pandas, geopandas, PyMaxFlow, React)
- Code quality on GitHub

**What might confuse them:**
- Nothing likely confuses them (the Method tab is designed for this audience)
- They might want *more* detail (links to specific code files, benchmark results)

---

### Journey 4: The Casual Return Visitor

**Entry Point:** Bookmarked site or remembered URL

**Flow:**
1. **Landing (Map tab):** Goes straight to slider.
2. **Exploration:** Tries different lambda values to observe patterns.
3. **Sharing:** Takes screenshot to share with someone.
4. **Exit:** Leaves after 2-3 minutes.

**What interests them:**
- Finding a specific lambda value that "looks right" to them
- Comparing their home region to others

---

## Feature Engagement Analysis

### Map Tab Features

| Feature | Interest Level | Confusion Risk | Engagement Order |
|---------|---------------|----------------|------------------|
| Map visualization | Very High | Low | 1st |
| Pan/zoom | High | None | 2nd |
| Lambda slider | High | Medium | 3rd |
| Hover highlighting | Medium | Low | During exploration |
| Summary panel | Medium | Low | After slider interaction |

**Slider Understanding:**
- Without context, "Surface Tension (λ)" is opaque to non-technical users
- The hint text ("Minimizes area" / "Minimizes perimeter") helps but is still abstract
- Most users will experiment and learn by doing

### Story Tab Features

| Feature | Interest Level | Confusion Risk | Engagement Order |
|---------|---------------|----------------|------------------|
| Opening hook | High | None | 1st |
| Statistics (165M, 1.1%) | Very High | None | 2nd |
| San Bernardino explanation | High | None | 3rd |
| Census Tract explanation | Medium | Low | 4th |
| Navigation links | Medium | None | Last |

**Content Understanding:**
- Clear, jargon-free language works well
- The "evolution" from county → tract → smooth is compelling
- The placeholder image note might disappoint (Phase 6 content)

### Method Tab Features

| Feature | Interest Level (Technical Users) | Confusion Risk (Non-Technical) | Engagement Order |
|---------|--------------------------------|-------------------------------|------------------|
| Objective function equation | Very High | Very High | 1st |
| Variable definitions | High | High | 2nd |
| Algorithm description | High | Very High | 3rd |
| Data sources | Medium | Low | 4th |
| Implementation stack | High | Low | 5th |
| GitHub link | Very High | None | Last |

**Self-Selection:**
- Non-technical users who accidentally click Method tab will quickly self-select out
- This is fine—the tab structure prevents forcing math on unwilling readers

---

## Potential Friction Points

### 1. Lambda Slider Opacity
**Problem:** "Surface Tension (λ)" means nothing to most users initially.
**Impact:** Users might not understand what they're controlling.
**Mitigation:** The hint text helps, and the Story tab explains it. Most users learn by experimenting.

### 2. Loading Time
**Problem:** 99 TopoJSON files must load before the map is interactive.
**Impact:** Users on slow connections may abandon before seeing the visualization.
**Mitigation:** Loading overlay with progress bar sets expectations. Batch loading (10 at a time) is optimized.

### 3. Mobile Experience
**Problem:** Map interactions are harder on mobile; reading long-form content (Story/Method) is challenging.
**Impact:** Mobile Explorers may have a degraded experience.
**Mitigation:** Responsive design exists. Mobile users are more likely to be Explorers (quick visual check) than deep readers.

### 4. "What Am I Looking At?" Moment
**Problem:** First-time visitors may not immediately understand what the blue shapes represent.
**Impact:** Brief confusion before reading subtitle or Story tab.
**Mitigation:** Subtitle "Where do half of all Americans actually live?" provides context. Summary panel shows "Population: 50.0%".

### 5. Why Not λ = 1.0?
**Problem:** The slider goes to 0.98, not 1.0. Technical users might wonder why.
**Impact:** Minor curiosity for Technical Evaluators.
**Mitigation:** Method tab doesn't explicitly explain this. CLAUDE.md notes it causes "convergence failure." Could be addressed in Method tab.

---

## What Each Persona Finds Most Interesting

### Explorers
1. The immediate visual "wow" factor
2. The morphing shapes when sliding lambda
3. The shareable statistic ("Half of Americans live in 1.1% of the land!")
4. Discovering their city/region on the map

### Curious Readers
1. The San Bernardino Problem explanation (validates their intuition that county maps feel wrong)
2. The "computer vision technique" connection (unexpected!)
3. The honest acknowledgment that there's no "correct" slider setting
4. Understanding why the shapes look organic, not jagged

### Technical Evaluators
1. The formal optimization framing (Lagrangian relaxation, max-flow min-cut)
2. The clean separation of boundary cost, area cost, and population reward terms
3. The binary search approach to satisfy the constraint
4. The implementation stack choices (indicates modern, appropriate tooling)

---

## Recommended Tab Engagement Order by Persona

| Persona | Optimal Order | Rationale |
|---------|--------------|-----------|
| Explorer | Map → (exit) | They want visual interaction, not reading |
| Explorer → Curious | Map → Story → (exit) | Curiosity converted into understanding |
| Curious Reader | Story → Map → (exit) | Context first, then exploration |
| Technical Evaluator | Map → Method → GitHub → (Story?) | Quick visual check, then rigor validation |
| Portfolio Reviewer | Method → GitHub → Story → Map | Assessing technical depth first |

---

## Code References

- `docs/tab_strategy.md:3-13` - Three audience persona definitions
- `web/src/components/TabBar.tsx:10-14` - Tab labels (Map, Story, Method)
- `web/src/components/StoryTab.tsx:19-27` - Key statistics (165M, 1.1%)
- `web/src/components/MethodTab.tsx:30-36` - Objective function LaTeX
- `web/src/components/LambdaSlider.tsx:41-45` - Slider hint text logic
- `web/src/components/SummaryPanel.tsx:32-57` - Statistics display

---

## Architecture Insights

The site architecture directly maps to the persona model:

1. **URL hash routing** (`#map`, `#story`, `#method`) enables deep-linking for each audience
2. **Keep-mounted pattern** for MapTab preserves exploration state when switching tabs
3. **Batch loading** (10 concurrent) balances load time vs. bandwidth for Explorer patience
4. **Three distinct voices** (terse, pedagogical, formal) signal maturity and intentionality

---

## Historical Context (from thoughts/)

- `docs/tab_strategy.md` - Primary strategy document defining the three-audience framework
- `thoughts/shared/research/2025-11-23-story-tab-content.md` - Story tab content strategy for "general-curious readers"
- `thoughts/shared/research/2025-11-23-method-tab-content.md` - Method tab strategy for "technically literate skeptics"
- `thoughts/shared/research/2025-11-22-subphase-5-2-core-visualization.md` - Color scheme, accessibility, mobile considerations

---

## Related Research

- `thoughts/shared/research/2025-11-23-ui-style-polish.md` - UI polish considerations
- `thoughts/shared/research/2025-11-23-tab-structure-implementation.md` - Tab navigation implementation

---

## Open Questions

1. **Should the slider hint text be more explicit?** E.g., "Fewer dots, smoother shapes" instead of "Minimizes perimeter"
2. **Is the loading time acceptable for impatient Explorers?** Consider lazy-loading or a single "default" lambda that loads first
3. **Should Method tab explain why λ < 1.0?** Technical users might appreciate the convergence failure note
4. **Would an "About" or "Author" section help Portfolio Reviewers?** Direct credentialing for that persona
5. **Are there accessibility gaps for screen reader users?** ARIA attributes exist but no explicit screen reader testing documented
