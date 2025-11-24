# Documentation Methodology Framing Implementation Plan

## Overview

Update README.md and CLAUDE.md to shift the project framing from data-insight-first (80%) to methodology-forward (60% methodology, 40% data insight), aligning with the stated portfolio goal of showcasing novel methodological exploration rather than just presenting population statistics.

## Current State Analysis

### Key Findings from Research

The research document `thoughts/shared/research/2025-11-24-project-purpose-alignment.md` identifies a misalignment:

- **Current balance**: 80% data insight ("1.1% of land!") vs. 20% methodology
- **Desired for portfolio**: 60% methodology (showcasing approach) vs. 40% data insight (hook)
- **User's stated preference**: "If I'm being honest, as a portfolio piece, I'm more interested in showing off what's novel about the methodology."

### Current Documentation Issues

**README.md (`README.md:6-10`)**:
- Opens with "experimental data visualization" (generic framing)
- Map is primary, slider is secondary: "with a slider to balance..."
- No indication of methodological exploration or what makes it novel
- "How It Works" section emphasizes data insight over approach

**CLAUDE.md (`CLAUDE.md:5-12`)**:
- Similar data-first framing
- Project Goals list data insight first, methodology third
- Doesn't emphasize portfolio value or methodological contribution

## Desired End State

After this implementation:

1. **README.md** will lead with methodological exploration, positioning the interactive surface tension parameter as the primary feature
2. **CLAUDE.md** will frame the project as a portfolio piece with clear emphasis on methodological value
3. Both documents will maintain approachability while shifting the emphasis toward the novel methodological exploration

### Verification
- README opening paragraph emphasizes methodology before data insight
- CLAUDE.md Project Overview includes explicit portfolio value statement
- Language uses "exploration" and "novel application" rather than claims of innovation
- Tone remains accessible and avoids overly academic framing

## What We're NOT Doing

Based on user feedback (`RESPONSE:` comments in research document):

1. **NOT changing tab order** - Current order (Map → Story → Method) is intentional; user prefers narrative before technical depth
2. **NOT making strong innovation claims** - Using softer language like "exploration" and "novel application" without citations
3. **NOT updating METHODOLOGY.md** - Research suggested strong claims; user wants softer language (out of scope for this plan, could be separate task)
4. **NOT updating ROADMAP.md** - Internal document, doesn't need portfolio framing
5. **NOT updating web frontend** - This plan focuses only on documentation files
6. **NOT changing social media descriptions** - None exist

## Implementation Approach

Make targeted edits to two files:
1. README.md: opening paragraph, "How It Works" section
2. CLAUDE.md: Project Overview, Project Goals

Use language that:
- Emphasizes methodological exploration over claims of innovation
- Positions the slider/surface tension parameter as central feature
- Maintains visual appeal as entry point while elevating technical depth
- Stays accessible (avoid overly academic tone)

## Phase 1: README.md Updates

### Overview
Update README.md to lead with methodological exploration while maintaining accessibility.

### Changes Required:

#### 1.1 Opening Paragraph (lines 6-10)

**Current**:
```markdown
An experimental data visualization exploring US population concentration. Interactive map highlighting where 50% of Americans live, with a slider to balance area minimization vs. perimeter smoothness.

**[View the Live Demo →](https://stevenfazzio.github.io/half-america)**

> Half of America lives in a *very* small area. See for yourself.
```

**Updated**:
```markdown
An exploration of max-flow min-cut optimization applied to cartographic data visualization. This project introduces an interactive "surface tension" parameter (λ) that controls the tradeoff between area minimization and perimeter smoothness when selecting census tracts, producing smooth organic boundaries for population concentration maps.

**[View the Live Demo →](https://stevenfazzio.github.io/half-america)**

> The result: Half of America lives in just 1.1% of the country's land area. The slider lets you explore how we balance precision vs. visual clarity.
```

**Rationale**:
- Leads with methodological exploration ("exploration of max-flow min-cut")
- Positions slider/lambda as primary feature ("introduces an interactive surface tension parameter")
- Data insight becomes the result ("The result: Half of America...")
- Avoids strong claims ("novel" → "exploration", "first" → omitted)
- Maintains accessibility with concrete outcome

**File**: `README.md:6-10`

---

#### 1.2 "How It Works" Section (lines 26-38)

**Current**:
```markdown
## How It Works

The visualization shows how concentrated the US population is—50% of Americans live in a surprisingly small area. The challenge is presenting this in a visually compelling way.

A slider controls lambda (0 to <1):

- **lambda ~ 0**: Minimizes total area. Shows high-resolution "dusty" city centers—accurate but hard to visually process.
- **lambda ~ 0.9**: Minimizes perimeter. Creates smooth, compact blobs that are easier to reason about while still being accurate.

The slider lets you explore the tradeoff between precision and visual clarity.

Note: lambda=1.0 is mathematically degenerate and excluded from valid values. Due to computational complexity, geometries for various lambda values are pre-calculated. The web app serves as a visualizer for these pre-computed states.

See [METHODOLOGY.md](METHODOLOGY.md) for the mathematical formulation.
```

**Updated**:
```markdown
## How It Works

This project treats census tract selection as a graph optimization problem. Given ~73,000 census tracts and their spatial adjacencies, we use **max-flow min-cut** to find the optimal 50% population subset while balancing two competing objectives:

1. **Minimize area** (precision): Select the smallest possible land area
2. **Minimize perimeter** (smoothness): Create smooth, organic boundaries

The interactive slider controls lambda (λ), the "surface tension" parameter (0 to <1):

- **λ ≈ 0**: Prioritizes area minimization. Produces high-resolution "dusty" city centers—accurate but hard to visually process.
- **λ ≈ 0.9**: Prioritizes perimeter minimization. Creates smooth, compact regions that are easier to reason about while remaining accurate.

The result: **50% of Americans live in just 1.1% of the country's land area**, revealed through smooth boundaries at λ ≈ 0.76.

**Technical Note**: λ=1.0 is mathematically degenerate and excluded. Due to computational complexity, geometries for various lambda values are pre-calculated offline; the web app visualizes these pre-computed states.

See [METHODOLOGY.md](METHODOLOGY.md) for the mathematical formulation and algorithm details.
```

**Rationale**:
- Opens with methodology ("graph optimization problem")
- Emphasizes the dual-objective tradeoff as the core challenge
- Data insight (1.1%) becomes a result of the methodology
- Adds context about census tracts and max-flow min-cut
- Maintains technical accessibility

**File**: `README.md:26-40`

---

### Success Criteria:

#### Automated Verification:
- [ ] README.md renders correctly in GitHub preview
- [ ] All internal links still work (METHODOLOGY.md, ROADMAP.md)
- [ ] Markdown syntax is valid (no broken formatting)

#### Manual Verification:
- [ ] Opening paragraph emphasizes methodology before data insight
- [ ] Language uses "exploration" tone, not "innovation" claims
- [ ] Technical content is accessible to general audience
- [ ] Data insight (1.1%) is present but positioned as result, not headline
- [ ] Reviewer feedback: "What is this project about?" should elicit methodology-first responses

---

## Phase 2: CLAUDE.md Updates

### Overview
Update CLAUDE.md to frame the project as a portfolio piece with clear methodological emphasis, since this document specifically guides AI assistants working on the codebase.

### Changes Required:

#### 2.1 Project Overview Section (lines 5-12)

**Current**:
```markdown
## Project Overview

Half of America is an experimental data visualization project exploring US population concentration. It produces an interactive map highlighting the areas where 50% of Americans live, with a user-controlled slider to balance area minimization vs. perimeter smoothness.

**Project Goals:**
- Show how geographically concentrated the US population is
- Make the visualization compelling (not just accurate)
- Serve as a portfolio piece for data science work
```

**Updated**:
```markdown
## Project Overview

Half of America is a portfolio project exploring the application of max-flow min-cut optimization to cartographic data visualization. It produces an interactive map where users control a "surface tension" parameter (λ) to balance area minimization vs. perimeter smoothness when selecting census tracts, revealing that 50% of Americans live in just 1.1% of the country's land area.

**Portfolio Value:**
This project showcases:
- Graph optimization applied to spatial problems (operations research)
- Interactive parameter exploration (computational cartography)
- Full-stack implementation from data pipeline to web visualization

**Project Goals:**
- Demonstrate methodological exploration: applying optimization techniques to geographic data
- Create compelling, interactive visualization (not just static analysis)
- Showcase end-to-end data science skills for portfolio purposes
```

**Rationale**:
- Immediately identifies as "portfolio project"
- New "Portfolio Value" section makes the showcase aspect explicit
- Reordered goals to lead with methodology
- Maintains all original information but reframed
- Helps AI assistants understand the project's purpose when making decisions

**File**: `CLAUDE.md:5-12`

---

### Success Criteria:

#### Automated Verification:
- [ ] CLAUDE.md is valid Markdown
- [ ] All internal links work (README.md, METHODOLOGY.md, etc.)
- [ ] File structure matches expected format for Claude Code

#### Manual Verification:
- [ ] Project Overview clearly identifies portfolio purpose
- [ ] Portfolio Value section is prominent and clear
- [ ] Project Goals emphasize methodology over data insight
- [ ] Tone is appropriate for guiding AI assistants (clear, directive)
- [ ] Technical concepts are accurately described

---

## Testing Strategy

### Validation Approach

After implementing both phases, validate the framing shift by asking 3-5 technical reviewers (data scientists, engineers):

**Question**: "Read the README opening and first section. What is this project about in one sentence?"

**Current expected responses**:
- "A map showing population concentration"
- "Shows 50% of Americans live in 1.1% of land"
- "Interactive visualization of population data"

**Target responses after changes**:
- "Exploration of graph optimization for cartography"
- "Applies max-flow min-cut to census tract selection"
- "Interactive surface tension parameter for geographic optimization"

### Success Metrics

- At least 60% of reviewers mention methodology/optimization in their one-sentence description
- Data insight (1.1%) mentioned as supporting detail, not primary feature
- Terms like "graph optimization," "max-flow min-cut," or "surface tension" appear in responses

---

## Performance Considerations

N/A - Documentation changes only, no runtime impact.

---

## Migration Notes

N/A - Documentation updates are non-breaking. Old documentation simply gets replaced.

---

## References

- Original research: `thoughts/shared/research/2025-11-24-project-purpose-alignment.md`
- User constraints:
  - Line 546: Softer language, no strong claims without citations
  - Line 584: ROADMAP.md is internal, skip changes
  - Line 648: Keep tab order as-is
  - Line 679: No social media descriptions exist
- Related research:
  - `thoughts/shared/research/2025-11-24-slider-improvement-research.md` (slider as primary vs. secondary)
  - `thoughts/shared/research/2025-11-23-user-personas-and-stories.md` (audience analysis)
- Current files:
  - `README.md:6-40` (opening and "How It Works")
  - `CLAUDE.md:5-12` (Project Overview)
