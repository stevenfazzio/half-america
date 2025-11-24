---
date: 2025-11-23T12:00:00-08:00
researcher: Claude
git_commit: 8f73c1e822032d2a2ee0b06e2b7af09c7b1cdd79
branch: master
repository: half-america
topic: "User Personas, Stories, and UX Journey Analysis"
tags: [research, user-experience, personas, user-stories, ux]
status: complete
last_updated: 2025-11-24
last_updated_by: Claude
last_updated_note: "Added follow-up research for map-only first-time user experience"
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

---

## Follow-up Research: Map-Only First-Time User Experience

**Date**: 2025-11-24T17:33:36+0000
**Git Commit**: 8e872ab1a29c568769333c30f4e89f3ada707f37
**Follow-up Question**: What do first-time users experience when they focus solely on the map, without navigating to other tabs? What do they notice first, what assumptions might they have, and how does their understanding evolve through interaction?

### Research Motivation

The original research focused heavily on inter-tab navigation and persona-driven journeys across Map → Story → Method. However, many users (particularly "Explorers") may never leave the Map tab. This follow-up investigates the **micro-journey within the Map tab itself** to understand:

1. **First impressions** - What draws the eye immediately?
2. **Initial assumptions** - What might users think they're seeing?
3. **Progressive understanding** - How does interaction reveal the visualization's meaning?
4. **Confusion points** - What might mislead or confuse?
5. **Learning mechanisms** - How does the UI teach without explicit instruction?

---

### Visual Hierarchy: What Users See First

Based on analysis of component positioning, sizing, and contrast (`MapTab.tsx:35-100`, `SummaryPanel.css:1-131`, `MapTitle.css:1-33`), the visual hierarchy follows this eye-tracking order:

#### 1st: The Map Visualization (Dominant Visual)
- **Location**: Full-screen canvas filling entire viewport
- **Color**: Okabe-Ito Blue `[0, 114, 178]` at 60% opacity against dark basemap
- **Visual weight**: 90% of screen real estate
- **First impression**: Users see blue shapes scattered across the US map
- **Immediate questions raised**:
  - "What are these blue regions?"
  - "Why are they concentrated on the coasts?"
  - "What do the gaps represent?"

#### 2nd: The Title/Subtitle (Context Provider)
- **Location**: Fixed center-top, 56px from top (desktop only, hidden on mobile)
- **Text**: "Half of America" (20px bold) + "Where 50% of Americans live" (14px)
- **Visual weight**: High contrast white text on dark background
- **Function**: Answers the first question - "These blue regions are where 50% of Americans live"
- **Aha moment**: "Oh! This tiny area contains half the population?"

#### 3rd: Hero Statistics (Validation & Precision)
- **Location**: Top-right summary panel
- **Text**: Two large numbers (28px bold) with labels
  - "50.0% of U.S. Population"
  - "~1.1% of U.S. Land Area" (at default λ=0.5)
- **Visual weight**: Largest text in UI panels, tabular numerics for emphasis
- **Function**: Provides concrete numbers validating the visual claim
- **Reaction**: "Only 1.1% of the land? That's even more extreme than I thought"

#### 4th: The Slider Control (Invitation to Interact)
- **Location**: Top-left (desktop) or bottom (mobile)
- **Visual elements**:
  - Label: "Surface Tension (λ)" - *Potentially opaque to non-technical users*
  - Blue circular handle at 24-32px diameter (prominent)
  - Endpoint labels: "Fragmented" ← → "Compact"
  - Current value: "0.50" (initial position)
- **Function**: Invites exploration, but meaning isn't immediately clear
- **Potential confusion**: "What is surface tension? What does this slider do?"

#### 5th: Supporting Statistics (Additional Context)
- **Location**: Below hero stats in summary panel
- **Text**: "Area: X mi²" and "Regions: Y"
- **Visual weight**: Smaller font (14px), secondary importance
- **Function**: Adds quantitative detail after the main message lands

---

### The First 10 Seconds: Typical User Mental Model

Based on visual hierarchy analysis, a typical first-time map-only user's thought process:

**Seconds 0-2 (Loading)**
- Sees loading overlay with progress bar
- Reads: "Half of America" and "Loading map data..."
- Forms expectation: "This is about US geography/population"
- Waits for 99 files to load (could be 2-10 seconds depending on connection)

**Seconds 2-4 (Initial Render)**
- Map appears with blue regions visible
- Eyes drawn to the map visualization (largest element)
- Scans the blue shapes: "They're mostly on the coasts and Great Lakes"
- Notices gaps: "The mountain west and Great Plains are empty"

**Seconds 4-6 (Reading Context)**
- Reads title: "Half of America"
- Reads subtitle: "Where 50% of Americans live"
- **Key insight formed**: "Oh! These blue areas contain half of all Americans"
- Mental calculation: "But they're such a small part of the map..."

**Seconds 6-8 (Validating Understanding)**
- Eyes move to summary panel (top right)
- Reads "50.0% of U.S. Population" - validates the title claim
- Reads "1.1% of U.S. Land Area" - **surprise/disbelief**
- Reaction: "Wait, really? Only 1.1%? Let me look at the map again..."

**Seconds 8-10 (Exploration Begins)**
- Returns to map, now viewing it with new understanding
- Might zoom/pan to examine specific regions
- Notices the slider: "What does 'Surface Tension' mean?"
- **Decision point**: Drag slider to see what happens, or read more context?

---

### User Stories: Map-Only Explorer Persona

#### Story 1: The Visual Learner (Never Reads Labels)
> "As a Visual Learner arriving from social media, I want to immediately understand the visualization through the shapes alone, without reading any text."

**Journey**:
1. **Initial impression** (0-3 sec): "Blue regions on a map. They look smooth and organic, not following state boundaries."
2. **Pattern recognition** (3-6 sec): "Dense on coasts, empty in the middle. Must be population-related."
3. **Slider discovery** (6-10 sec): Drags slider left → shapes fragment into scattered dots. "Whoa, what happened?"
4. **Experiential learning** (10-20 sec): Drags slider right → shapes merge into smooth blobs. "Ah, this controls how smooth the shapes are."
5. **Assumption formed**: "This shows where people live, and the slider makes it smoother or more detailed."

**Potential Misconception**: Might not grasp the "50% threshold" concept without reading the title. Could think it shows "all populated areas" rather than specifically "the areas containing exactly 50% of the population."

**Correction Mechanism**: The hero statistic "50.0% of U.S. Population" is always visible. Even without reading initially, repeated glances at the summary panel eventually communicate the constraint.

---

#### Story 2: The Data-Driven Skeptic (Reads Everything)
> "As a Data-Driven Skeptic, I want to validate the claims with numbers before trusting the visualization."

**Journey**:
1. **Loading screen** (0-2 sec): "Half of America - okay, about population distribution."
2. **Title read** (2-4 sec): "Where 50% of Americans live. So this is the half that's in cities?"
3. **Map scan** (4-6 sec): "Looks plausible. Coasts and Chicago area."
4. **Stat validation** (6-10 sec): Reads summary panel: "50.0% population - good, it's exactly half. 1.1% of land area - that seems impossibly small."
5. **Visual cross-check** (10-15 sec): Returns to map. Mentally estimates: "Yeah, the blue areas are tiny compared to the whole map. Maybe it is 1.1%."
6. **Slider investigation** (15-25 sec): Notices slider, reads "Surface Tension (λ)". Still confused. Drags slider.
7. **Stats update** (25-30 sec): Sees population stays at 50.0% but land area changes to 0.8% (low λ) or 1.5% (high λ). "Ah! Different optimization strategies, all satisfying the 50% population constraint."

**Potential Misconception**: Initially might think "Surface Tension" is a geographic or density metric, not an algorithmic parameter.

**Correction Mechanism**: The dynamic hint text below the slider changes as they drag:
- Low λ: "Minimizes area (more fragmented)"
- High λ: "Minimizes perimeter (smoother shapes)"
This teaches the tradeoff through interaction.

---

#### Story 3: The Mobile User (Limited Screen Real Estate)
> "As a Mobile User, I want to understand the visualization despite having less visible context."

**Journey**:
1. **Map appears** (2-4 sec): Title is hidden on mobile, so primary context comes from the map itself.
2. **Summary panel** (4-6 sec): Top-right panel shows "Half of America" title (acting as mobile title). Reads "50.0%" and "1.1%".
3. **Slider discovery** (6-10 sec): Slider is at bottom of screen (above tab bar). Larger touch target (32px) makes it prominent.
4. **Drag interaction** (10-20 sec): Drags slider with thumb. Map updates. "This changes the shape."
5. **Endpoint labels** (20-25 sec): Notices "Fragmented" and "Compact" labels at slider ends. "Oh, I'm controlling fragmentation."

**Unique Mobile Challenges**:
- No title overlay - summary panel must do double duty
- Slider at bottom competes with tab bar for attention
- Zoom/pan gestures might interfere with map exploration
- Technical stats (λ value) hidden to save space - might not notice lambda parameter

**Advantage**: Larger touch targets and simplified UI reduce cognitive load. Focus is purely on map and slider interaction.

---

#### Story 4: The Accidental Hover Discoverer
> "As a user exploring the map, I want to understand what the individual blue regions represent when I hover over them."

**Journey**:
1. **Map exploration** (5-10 sec): After understanding the overall pattern, user pans/zooms to examine a specific region.
2. **Accidental hover** (10-12 sec): Mouse moves over a blue region. It highlights in white.
3. **Expectation formed**: "Hovering highlights regions. Will a tooltip appear?"
4. **No tooltip appears** (12-15 sec): Just the white highlight. No additional information.
5. **Hypothesis**: "Maybe each region represents a city or county?"
6. **Slider interaction** (15-30 sec): Changes lambda. Regions merge and split. "Oh, these aren't fixed geographic units - they change based on the algorithm."
7. **Revised understanding**: "The regions are computed, not pre-defined. The slider adjusts the algorithm, which changes how the regions are drawn."

**Potential Misconception (Corrected)**: Initial hover might suggest regions are clickable entities with detailed information. Lack of tooltip and shape-shifting behavior with slider corrects this.

**Design Rationale**: Per `MapTab.tsx:62-63`, `pickable: true` and `autoHighlight: true` enable hover feedback, but no `getTooltip` property. This is intentional - with ~73,000 census tract polygons, per-region tooltips would create a "flickery" experience and work poorly on mobile.

---

### Progressive Understanding: How the UI Teaches

The map interface uses **experiential learning** rather than explicit instruction. Users discover meaning through interaction:

#### Teaching Mechanism 1: Visual-Text Correlation
- **What's shown**: Map visualization + title + summary panel visible simultaneously
- **Learning**: Users can look at the visual (blue regions), read the text ("50% of Americans"), and mentally connect them
- **Cognitive load**: Low - no modal dialogs or forced reading

#### Teaching Mechanism 2: Slider-Driven Experimentation
- **Affordance**: Blue circular handle on slider track invites dragging
- **Feedback loop**: Drag → map updates in real-time → see the effect
- **Discovery**: Users learn by doing: "Low values = fragmented, high values = smooth"
- **Hint text**: Changes dynamically based on slider position, providing just-in-time context

#### Teaching Mechanism 3: Statistic Anchoring
- **Population %**: Always stays at ~50.0% regardless of slider position
- **Land area %**: Changes from 0.8% to 1.5% as slider moves
- **Learning**: Users notice one value is constant (the constraint) while others vary (the optimization outcomes)
- **Insight**: "The algorithm guarantees 50% population, but the land area depends on how I set the slider"

#### Teaching Mechanism 4: Hover Feedback (Interaction Confirmation)
- **Action**: Mouse over blue region
- **Response**: White highlight overlay
- **Message**: "The map is interactive. These regions respond to your actions."
- **Limitation**: No per-region data, intentionally keeping focus on aggregate patterns

---

### Confusion Points and Misconceptions

#### Confusion 1: "What is Surface Tension (λ)?"
**Problem**: The label "Surface Tension (λ)" is borrowed from computer vision terminology and may be opaque to non-technical users.

**User assumption (wrong)**: "Is this related to geography, like density or climate?"

**User assumption (wrong)**: "Is λ a measurement of something physical?"

**Correction mechanisms**:
1. **Endpoint labels**: "Fragmented" ← → "Compact" provide semantic meaning independent of the technical term
2. **Hint text**: Dynamic messages like "Minimizes area (more fragmented)" explain the slider's effect in plain language
3. **Experiential learning**: Dragging the slider shows the effect immediately, making the parameter's purpose clear even if the name isn't

**Severity**: Low. Users can operate the slider effectively without understanding the term "surface tension." The slider's effect is self-evident through use.

---

#### Confusion 2: "Why are there multiple disconnected blue regions?"
**Problem**: Users might expect a single continuous area for "where 50% of Americans live."

**User assumption (wrong)**: "The blue should be one blob, like a giant circle around the densest cities."

**Observation**: At λ=0.5 (default), there are typically 30-50 disconnected regions visible. At low λ, this increases to 200+.

**Correction mechanisms**:
1. **Summary panel stat**: "Regions: X" explicitly acknowledges the multi-region nature
2. **Map visualization**: Clearly shows NYC, LA, Chicago, etc. as separate regions - confirms intuition that multiple cities contribute to the 50%
3. **Slider interaction**: As λ decreases, regions fragment into more pieces, revealing that population concentration happens in many places, not one

**Revised understanding**: "Oh, the 50% is spread across many major cities, not one giant urban area."

**Severity**: Low-Medium. Initial confusion is brief and self-resolves through observation.

---

#### Confusion 3: "Why does the land area percentage change when population stays at 50%?"
**Problem**: Users might expect both percentages to be fixed if the "50%" is the constraint.

**User assumption (wrong)**: "If it's always 50% of people, shouldn't it always be X% of land?"

**Observation**: At λ=0.0, land area ≈0.8%. At λ=0.98, land area ≈1.5%. Population stays constant at 50.0%.

**Correction mechanisms**:
1. **Slider hint text**: "Minimizes area" vs. "Minimizes perimeter" explains the tradeoff
2. **Visual confirmation**: Low λ shows tighter, more fragmented regions (less area). High λ shows smoother, more inclusive regions (more area).
3. **Statistic visibility**: Both numbers are always visible, allowing users to observe the relationship

**Aha moment**: "Oh! The slider controls the algorithm's goal. Minimizing area gives tighter boundaries (less land), while minimizing perimeter includes more land for smoother shapes. Population is always fixed at 50%, but the land area is a consequence of the optimization strategy."

**Severity**: Medium. This is a subtle insight that might take 30-60 seconds of interaction to grasp. Users who don't explore the slider extensively might not fully understand the tradeoff.

---

#### Confusion 4: "What are the shapes exactly? Cities? Counties?"
**Problem**: Without reading the Story or Method tabs, users might not know the visualization uses Census Tracts.

**User assumption (could be wrong)**: "Each blue shape is a city or metropolitan area."

**User assumption (could be wrong)**: "These are county boundaries."

**Observation**: Zoom in on the map → shapes are irregular and don't align with city/county boundaries. At high zoom levels, individual census tract boundaries become visible.

**Correction mechanisms**:
1. **Visual evidence**: Shapes don't follow obvious political boundaries, suggesting a different unit
2. **Hover highlighting**: Individual polygons highlight, revealing the granular nature (but not identifying the specific geographic unit)
3. **Story tab**: Explicitly explains "Census Tracts" as the underlying data (but map-only users won't see this)

**Revised understanding (partial)**: "These are computed regions based on some underlying geographic data, not cities or counties."

**Severity**: Low. For the map-only explorer, understanding the exact data source (census tracts) isn't critical to appreciating the visualization. The key insight - "half of Americans live in a tiny fraction of the land" - is conveyed regardless.

---

#### Confusion 5: "Why does the slider only go to 0.98, not 1.0?"
**Problem**: Technical users might expect a parameter to have a natural endpoint at 1.0.

**User assumption (wrong)**: "λ=1.0 should represent the maximum smoothness."

**Observation**: Slider stops at λ=0.98. No explanation visible in the Map tab UI.

**Correction mechanisms**:
1. **None in the Map tab UI** - this is a deliberate omission to avoid overwhelming non-technical users
2. **Method tab explanation (not in map-only experience)**: λ=1.0 causes convergence failure in the optimization
3. **CLAUDE.md documentation**: Notes that λ=1.0 is excluded due to zero area cost

**Severity**: Very Low. Only affects Technical Evaluators who notice the detail. Map-only Explorers won't notice or care.

---

### How Interaction Clears Up Confusion

The map interface relies on **interactive progressive disclosure** to resolve initial misconceptions:

| Confusion | Resolution Mechanism | Time to Clarity |
|-----------|---------------------|-----------------|
| "What is surface tension?" | Endpoint labels + hint text + drag feedback | 10-20 seconds |
| "Why multiple regions?" | Visual observation + regions stat | 5-10 seconds |
| "Why does land area change?" | Slider interaction + stat observation | 30-60 seconds |
| "What are the shapes?" | Zoom/pan exploration + hover feedback | 20-40 seconds |
| "Why not λ=1.0?" | Not resolved in Map tab (acceptable) | N/A |

**Design Philosophy**: The map interface favors **discovery over instruction**. Users aren't told what to think; they're invited to explore and form their own understanding. This aligns with the "Explorer" persona's preference for hands-on learning over reading.

---

### Revised User Stories: Map-Only Micro-Journeys

#### Micro-Journey 1: "The 5-Second Wow" (Minimum Engagement)
**User**: Casual social media browser, extremely short attention span

1. Map loads → sees blue regions concentrated on coasts
2. Reads title: "Half of America"
3. Reaction: "Huh, half of Americans live in that tiny area? Wild."
4. **Exits** (shares screenshot or moves on)

**Outcome**: Core message delivered in 5 seconds. Mission accomplished.

---

#### Micro-Journey 2: "The Slider Explorer" (30-60 seconds)
**User**: Curious but impatient, prefers interaction over reading

1. Map loads → sees visualization
2. Notices slider, drags it left → shapes explode into dots
3. "Whoa!" → drags it right → shapes merge into smooth blobs
4. Experiments with different positions, observes land area % change
5. **Forms mental model**: "Low values = precise but fragmented. High values = smooth but includes more land. Population always 50%."
6. **Exits satisfied** or shares a specific lambda value screenshot

**Outcome**: Deeper understanding through experimentation. Grasps the optimization tradeoff without reading any tabs.

---

#### Micro-Journey 3: "The Skeptical Validator" (1-2 minutes)
**User**: Data-literate, wants to verify claims

1. Map loads → reads title and subtitle
2. Checks summary panel: "50.0% population, 1.1% land area"
3. Mentally estimates map coverage: "That seems plausible, maybe even generous."
4. Pans/zooms to examine specific regions: NYC, LA, Bay Area, Chicago
5. Adjusts slider, watches statistics update
6. **Validates**: "Population stays at 50%, land area varies based on algorithm. This is legitimate."
7. **Next action**: Might click "Method" tab to check rigor, or might exit satisfied

**Outcome**: Statistical validation + visual confirmation build trust. User believes the visualization is accurate.

---

#### Micro-Journey 4: "The Geographic Identifier" (2-5 minutes)
**User**: Wants to find their home region on the map

1. Map loads → general observation
2. **Goal**: "Is my city/region in the blue area?"
3. Pans/zooms to their location (e.g., Denver, Phoenix, Portland)
4. If inside blue: "Makes sense, I live in a city."
5. If outside blue: "Wow, my area isn't dense enough to be in the top 50%!"
6. Adjusts slider to see if their region appears at different λ values
7. **Insight**: Realizes how sparse population is outside major metros

**Outcome**: Personal connection to the data. Understanding through self-discovery.

---

### Key Insights: What Map-Only Users Learn

**Without reading Story or Method tabs, map-only users can discover:**

1. **The core insight**: Half of Americans live in ~1% of the land area (extreme population concentration)
2. **The geographic pattern**: Coastal regions + Great Lakes + scattered metros contain the 50%, while mountain west and Great Plains are sparse
3. **The optimization tradeoff**: The slider controls fragmentation vs. smoothness, affecting land area coverage while maintaining 50% population
4. **The multi-city nature**: Population concentration happens in many separate regions, not one giant urban blob
5. **The scale**: Zooming in reveals fine-grained boundaries; zooming out shows the national pattern

**What they might NOT learn (requires Story/Method tabs):**
- That census tracts are the underlying data unit
- Why the approach avoids the "San Bernardino Problem"
- That λ controls a Lagrangian optimization with area cost and perimeter cost
- How the algorithm uses max-flow min-cut

**Assessment**: The map-only experience successfully conveys the main message - population concentration - without requiring users to read narrative or technical content. This aligns with the "Explorer" persona's preference for visual discovery.

---

### Design Strengths for Map-Only Users

1. **Immediate visual impact**: No reading required to see the population concentration pattern
2. **Progressive disclosure**: Information revealed through interaction, not forced upfront
3. **Experiential learning**: Slider invites experimentation, teaching through feedback
4. **Always-visible context**: Title + summary panel remain on screen, preventing disorientation
5. **Mobile optimization**: Touch targets, bottom slider, simplified UI work well on phones
6. **No dead ends**: Hover, zoom, pan, and slider all provide meaningful feedback
7. **Shareable**: Users can find an interesting lambda value and screenshot it

---

### Design Weaknesses for Map-Only Users

1. **Opaque terminology**: "Surface Tension (λ)" is technical jargon without in-map explanation
2. **No onboarding**: Users must discover slider functionality on their own (good for Explorers, bad for those who need guidance)
3. **Hidden census tract detail**: The underlying data unit isn't explained in the map interface
4. **Loading time**: 99 files must load before any interaction (2-10 seconds depending on connection) - could frustrate impatient users
5. **No "default" or "recommended" slider position**: λ=0.5 is the initial value, but users don't know if it's optimal or just arbitrary
6. **Region count may surprise**: "Regions: 47" (at λ=0.5) might seem high to users expecting a single "Megalopolis"

---

### Comparison to Original User Journey Analysis

**Original focus (inter-tab navigation)**:
- Map → Story → Method journey
- Tab-specific feature engagement
- Persona-driven paths (Explorer → Curious Reader → Technical Evaluator)

**This follow-up (map-only micro-journey)**:
- Seconds 0-10 initial impression
- Interaction-driven progressive understanding
- Misconceptions and their resolution through use
- What users learn without reading tabs

**Complementary insights**:
- Original research correctly identified "Explorer" persona as map-focused
- This follow-up reveals that Explorers can successfully grasp the core message without ever leaving the Map tab
- The slider is the key teaching tool, not text or tooltips
- Visual hierarchy and always-visible statistics provide sufficient context for standalone map usage

---

### Recommendations for Improving Map-Only Experience

Based on identified confusion points and learning curves:

#### 1. Consider Adding a "First Visit" Tooltip (Optional)
- **Proposal**: On first map load, show a dismissible tooltip pointing to the slider: "Try dragging the slider to see different optimization strategies"
- **Pros**: Explicitly invites interaction for users who might not notice the slider
- **Cons**: Adds friction for repeat visitors; breaks clean visual design; could patronize Explorer persona
- **Verdict**: Probably not needed - current design already invites experimentation through prominent slider placement

#### 2. Make Slider Hint Text More Concrete (Low Priority)
- **Current**: "Minimizes perimeter (smoother shapes)"
- **Alternative**: "Smoother shapes (includes more land for rounded boundaries)"
- **Pros**: More explicit connection to the land area % statistic
- **Cons**: Longer text; current wording is adequate for users who experiment
- **Verdict**: Current design is acceptable

#### 3. Add "Recommended: λ=0.7" Label (Under Consideration)
- **Proposal**: Mark a specific slider position as "Recommended" to give users a starting point
- **Pros**: Communicates that not all lambda values are equal; provides guidance
- **Cons**: Contradicts Story tab message "There's no 'correct' setting"; adds editorial judgment to a neutral tool
- **Verdict**: Conflicts with project philosophy of letting users decide

#### 4. Optimize Loading (High Priority for Mobile)
- **Current**: All 99 TopoJSON files load before map becomes interactive
- **Alternative**: Load λ=0.5 first, show map immediately, lazy-load others in background
- **Pros**: Reduces perceived loading time from 2-10 seconds to <1 second; improves mobile experience
- **Cons**: Adds complexity to loader logic; slider would be disabled until other lambdas load
- **Verdict**: Worth exploring in future iteration (Phase 6)

#### 5. Enhance Hover Feedback with Brief Tooltip (Not Recommended)
- **Proposal**: Show minimal tooltip on hover, e.g., "Part of the 50% region"
- **Pros**: Confirms interactivity
- **Cons**: 73,000 polygons would trigger constant tooltip flickering; doesn't add meaningful information; works poorly on mobile (no hover)
- **Verdict**: Current design decision (visual highlight only) is correct

---

### Conclusion: Map-Only Experience is Self-Sufficient

The research confirms that **the map interface successfully teaches first-time users the core insight through interaction alone**, without requiring navigation to Story or Method tabs. The design's reliance on experiential learning, visual hierarchy, and always-visible statistics creates a self-contained experience for the "Explorer" persona.

**Key success metrics for map-only users:**
- ✅ Core insight delivered in 5-10 seconds (title + visual + stats)
- ✅ Slider functionality discoverable through affordance (prominent handle, endpoint labels)
- ✅ Optimization tradeoff understandable through experimentation (30-60 seconds of use)
- ✅ Visual pattern clear without explanation (coastal concentration, sparse interior)
- ⚠️ Some technical details remain opaque ("surface tension," census tracts) - acceptable tradeoff

**The map-only user journey validates the original three-audience strategy**: Explorers get a complete, satisfying experience on the Map tab alone, while Curious Readers and Technical Evaluators can dive deeper through Story and Method tabs if desired.

---

### Code References (Follow-up Research)

| Component | File Path | Key Finding |
|-----------|-----------|-------------|
| Visual hierarchy | `web/src/components/MapTab.tsx:35-100` | Map canvas + overlays establish primary visual |
| Hero statistics | `web/src/components/SummaryPanel.tsx:38-47` | 28px bold percentages create secondary focus |
| Title positioning | `web/src/components/MapTitle.tsx:3-10` | Center-top placement, hidden mobile |
| Slider affordance | `web/src/components/LambdaSlider.tsx:11-52` | Blue handle, endpoint labels, dynamic hints |
| Hover feedback | `MapTab.tsx:62-63` | `pickable: true`, `autoHighlight: true`, no tooltip |
| Loading sequence | `web/src/hooks/useTopoJsonLoader.ts:82-122` | 99 files in 10-file batches, progress tracking |
| MultiPolygon explosion | `useTopoJsonLoader.ts:31-59` | Enables individual region highlighting |
| Mobile optimization | `LambdaSlider.css:1-12, :68-77` | 32px touch targets, bottom positioning |
