---
date: 2025-11-22T12:00:00-08:00
researcher: Claude
git_commit: e649996525bbf18a4d582bbbe00505ea73ed2c0e
branch: master
repository: half_america
topic: "Documentation Improvement Based on User Feedback"
tags: [research, documentation, readme, methodology, framing]
status: complete
last_updated: 2025-11-22
last_updated_by: Claude
---

# Research: Documentation Improvement Based on User Feedback

**Date**: 2025-11-22T12:00:00-08:00
**Researcher**: Claude
**Git Commit**: e649996525bbf18a4d582bbbe00505ea73ed2c0e
**Branch**: master
**Repository**: half_america

## Research Question

How should we improve the documentation files to better represent the project based on the user's feedback about its purpose, evolution, and goals?

## Summary

The current documentation has several framing issues that don't accurately represent the project's origins, evolution, or purpose. Key problems:

1. **Framing as "solving two problems"** - The docs present San Bernardino Problem and Dust Problem as pre-existing issues to solve, rather than as an iterative discovery journey
2. **Wrong emphasis on "where does half live"** - The real purpose is showing how concentrated the population is
3. **Missing project evolution narrative** - The iterative problem-solving journey is lost
4. **Missing portfolio piece mention** - This is also a professional data science portfolio piece
5. **Dust problem misframed** - Should emphasize human cognitive limits, not just "failing as visualization"

## User Feedback Analysis

### Key Corrections from User

| Current Framing | Corrected Framing |
|-----------------|-------------------|
| "Topology optimization experiment" | "Data visualization project exploring population density" |
| "Solves two problems" (San Bernardino + Dust) | "Evolved through iterative problem-solving" |
| "Where does half of America really live?" | "Shows how concentrated the population is" |
| Dust "fails as visualization" | Dust is hard to reason about due to human cognitive limits |
| No mention of portfolio | This is also a portfolio piece for data science career |

### The Evolution Story (Missing from Docs)

The project evolved through these stages:

1. **Started**: Attempt to improve viral "Half of America" county maps
2. **Noticed**: San Bernardino Problem (counties include empty areas)
3. **Solution 1**: Use census tracts instead (~73,000 vs ~3,100 counties)
4. **Problem**: Dust Problem - thousands of tiny regions, not visually compelling
5. **Solution 2**: Try minimizing region *count* in addition to area
6. **Problem**: Oddly-shaped regions with narrow "bridges" between dense areas
7. **Solution 3**: Minimize *perimeter* instead of region count - produces smooth shapes

This journey is not captured anywhere in the current documentation.

## Detailed Recommendations

### README.md Changes

#### 1. Change Tagline/Description

**Current:**
```markdown
A topology optimization experiment that treats the 'Half of America' map as a fluid, replacing dusty dots with smooth, organic population blobs.

> Where does half of America *really* live?
```

**Recommended:**
```markdown
An experimental data visualization exploring US population concentration. Interactive map highlighting where 50% of Americans live, with a slider to balance area minimization vs. perimeter smoothness.

> Half of America lives in a *very* small area. See for yourself.
```

#### 2. Reframe "The Problem" Section

**Current:** Presents two problems as static issues to solve

**Recommended:** Present the evolution story

```markdown
## Background

There is a genre of viral maps that frequently circulates on the internet, typically titled "Half of the United States Lives In These Counties" ([example](https://www.businessinsider.com/half-of-the-united-states-lives-in-these-counties-2013-9)). These maps show how concentrated the US population is by selecting the most populous counties until reaching 50% of the total population.

## The Evolution

This project evolved through several iterations:

1. **The San Bernardino Problem**: County-level maps include vast empty areas (San Bernardino County is larger than nine US states but mostly desert). Solution: use Census Tracts (~73,000 units) instead of counties (~3,100).

2. **The Dust Problem**: Census tracts created thousands of tiny disconnected regions. While technically accurate, humans struggle to visually reason about thousands of tiny specks. The map was accurate but not *compelling*.

3. **The Bridge Problem**: Minimizing region *count* (to reduce dust) created oddly-shaped regions with narrow "bridges" connecting dense areas.

4. **The Solution**: Minimize *perimeter* instead. This produces smooth, organic shapes that are easier to visually interpret while remaining accurate representations of population concentration.
```

#### 3. Reframe "How It Works"

**Current:** Focuses on lambda slider mechanics

**Recommended:** Emphasize the visualization goal

```markdown
## How It Works

The project shows how concentrated the US population is - 50% of Americans live in a surprisingly small area. The challenge is presenting this in a visually compelling way.

A slider controls lambda (0 to <1):

- **lambda ~ 0**: Minimizes total area. Shows high-resolution "dusty" city centers - accurate but hard to visually process.
- **lambda ~ 0.9**: Minimizes perimeter. Creates smooth, compact blobs that are easier to reason about while still being accurate.

The slider lets you explore the tradeoff between precision and visual clarity.
```

#### 4. Add Portfolio Context

Add to existing disclaimer or project status:

```markdown
*This is a personal experimental project exploring topology optimization and cartography, and serves as a portfolio piece demonstrating data science and visualization skills.*
```

### CLAUDE.md Changes

#### 1. Update Project Overview

**Current:**
```markdown
Half of America is a topology optimization experiment that creates an interactive visualization of US population distribution.
```

**Recommended:**
```markdown
Half of America is an experimental data visualization project exploring US population concentration. It produces an interactive map highlighting the areas where 50% of Americans live, with a user-controlled slider to balance area minimization vs. perimeter smoothness.

**Project Goals:**
- Show how geographically concentrated the US population is
- Make the visualization compelling (not just accurate)
- Serve as a portfolio piece for data science work
```

#### 2. Add "Project Evolution" Section

Add a brief section explaining the iterative development:

```markdown
## Project Evolution

The approach evolved through iteration:
1. County maps had the "San Bernardino Problem" (empty areas included)
2. Census tracts created "dust" (too many tiny regions to reason about)
3. Minimizing region count created "bridges" (narrow connections)
4. Minimizing perimeter produces smooth, compelling shapes
```

### METHODOLOGY.md Changes

This file is appropriately technical and doesn't need major changes. However, a brief "Motivation" section at the top could help:

```markdown
## Motivation

Traditional "half of America" maps have limitations:
- County boundaries include empty areas (San Bernardino Problem)
- Using smaller units creates visual "dust" that's hard to process
- Minimizing region count creates unnatural "bridges"

This methodology uses perimeter minimization to create smooth, organic shapes that are both accurate and visually compelling.
```

### docs/API.md Changes

No changes needed - this is appropriately technical/reference-focused.

### ROADMAP.md Changes

No changes needed - this is appropriately task/milestone-focused.

## Implementation Priority

| File | Priority | Scope |
|------|----------|-------|
| README.md | High | Major reframe - tagline, problem section, how it works, portfolio mention |
| CLAUDE.md | Medium | Update project overview, add evolution context |
| METHODOLOGY.md | Low | Optional motivation section |
| API.md | None | No changes |
| ROADMAP.md | None | No changes |

## Code References

- `README.md:1-134` - Full README requiring updates
- `CLAUDE.md:1-99` - Project overview section needs update
- `METHODOLOGY.md:1-91` - Optional motivation addition
- `docs/archive/PROJECT_SUMMARY.md` - Historical context (already archived)

## Architecture Insights

The documentation hierarchy is:
- **README.md**: Public-facing, should tell the story and hook interest
- **CLAUDE.md**: Developer/AI guidance, should provide accurate context
- **METHODOLOGY.md**: Technical deep-dive, appropriately dense
- **ROADMAP.md**: Progress tracking, doesn't need narrative
- **docs/API.md**: Reference, doesn't need narrative

The README is the most important to fix as it's the public face of the project.

## Open Questions

1. Should the README include a "Project Evolution" section, or should this context be woven into "The Problem" section?
RESPONSE: I think it should be woven into the section. That being said, I'm not sure I love titling that section "The Problem", or "Project Evolution". Maybe something like "Background"? I'm not married to that, so I'm very open if you have a better idea.
2. How prominent should the portfolio piece mention be?
RESPONSE: I don't want to mention it in the README.md, but I think it could go in CLAUDE.md.
3. Should METHODOLOGY.md have a narrative motivation section, or stay purely technical?
RESPONSE: I think that would make sense. Maybe we have a friendly version in README.md, and a more technically specific/accurate version in METHODOLOGY.md (matching the rest of that file)?

## Summary of Changes

### README.md
- Change tagline from "topology optimization experiment" to "data visualization project"
- Change blockquote from "where does half live?" to "half lives in a very small area"
- Rewrite "The Problem" as "Background" + "The Evolution" to tell the iterative story
- Reframe "How It Works" to emphasize visualization goal, not just mechanics
- Add portfolio piece mention to disclaimer

### CLAUDE.md
- Update Project Overview to emphasize visualization and portfolio goals
- Add "Project Evolution" section with brief history

### METHODOLOGY.md (optional)
- Add brief "Motivation" section at top
