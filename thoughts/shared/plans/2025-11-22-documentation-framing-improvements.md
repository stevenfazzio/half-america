# Documentation Framing Improvements Implementation Plan

## Overview

Reframe the project documentation to accurately represent the project's origins, evolution, and purpose. The current documentation presents problems as static issues to solve, rather than showing the iterative discovery journey that led to the current approach.

## Current State Analysis

The documentation has several framing issues:

1. **README.md** presents "San Bernardino Problem" and "Dust Problem" as pre-existing issues, not discoveries
2. **Tagline** focuses on "topology optimization" rather than data visualization
3. **Blockquote** asks "where does half live?" instead of emphasizing population concentration
4. **No evolution narrative** - the iterative problem-solving journey is lost
5. **METHODOLOGY.md** jumps into technical details without explaining motivation

### Key Discoveries:
- Research document: `thoughts/shared/research/2025-11-22-documentation-improvement-recommendations.md`
- User clarified: evolution story should be woven into "Background" section
- User clarified: portfolio mention in CLAUDE.md only, not README.md
- User clarified: METHODOLOGY.md motivation should be technically accurate (matching file's tone)

## Desired End State

After implementation:

1. README.md tells the project's evolution story in a "Background" section
2. Tagline emphasizes data visualization, not topology optimization
3. Blockquote emphasizes population concentration, not "where does half live"
4. CLAUDE.md includes project goals and portfolio context
5. METHODOLOGY.md has a technically-accurate motivation section

### Verification:
- All documentation accurately represents the project as a data visualization exploring population concentration
- The iterative discovery journey (San Bernardino → Dust → Bridge → Perimeter solution) is clear
- No mention of "portfolio" in README.md
- METHODOLOGY.md motivation matches technical tone of rest of file

## What We're NOT Doing

- Changing API.md (appropriately technical/reference-focused)
- Changing ROADMAP.md (appropriately task/milestone-focused)
- Changing any code or functionality
- Adding new documentation files

## Implementation Approach

Make changes in order of public visibility: README.md first (public face), then CLAUDE.md (developer guidance), then METHODOLOGY.md (technical reference).

---

## Phase 1: README.md Reframe

### Overview
Update the public-facing README to tell the project's evolution story and reframe around data visualization.

### Changes Required:

#### 1. Update Tagline and Blockquote (lines 6-8)

**File**: `README.md`

**Current:**
```markdown
A topology optimization experiment that treats the 'Half of America' map as a fluid, replacing dusty dots with smooth, organic population blobs.

> Where does half of America *really* live?
```

**New:**
```markdown
An experimental data visualization exploring US population concentration. Interactive map highlighting where 50% of Americans live, with a slider to balance area minimization vs. perimeter smoothness.

> Half of America lives in a *very* small area. See for yourself.
```

#### 2. Rewrite "The Problem" as "Background" (lines 10-19)

**File**: `README.md`

**Current:**
```markdown
## The Problem

There is a genre of viral maps that frequently circulates on the internet, typically titled "Half of the United States Lives In These Counties" ([example](https://www.businessinsider.com/half-of-the-united-states-lives-in-these-counties-2013-9)). These maps illustrate the extreme geographic concentration of the US population using a simple algorithm: rank counties by population and select the top N until exceeding 50% of the total.

Traditional approaches have two issues:

1. **The San Bernardino Problem**: County boundaries include vast empty areas (San Bernardino County is larger than nine US states but mostly desert)
2. **The Dust Problem**: Using smaller units creates thousands of disconnected specks that fail as visualization

This project solves both using **Max-Flow Min-Cut optimization** with a user-controlled "surface tension" parameter.
```

**New:**
```markdown
## Background

There is a genre of viral maps that frequently circulates on the internet, typically titled "Half of the United States Lives In These Counties" ([example](https://www.businessinsider.com/half-of-the-united-states-lives-in-these-counties-2013-9)). These maps show how concentrated the US population is by selecting the most populous counties until reaching 50% of the total population.

This project evolved through several iterations:

1. **The San Bernardino Problem**: County-level maps include vast empty areas (San Bernardino County is larger than nine US states but mostly desert). Solution: use Census Tracts (~73,000 units) instead of counties (~3,100).

2. **The Dust Problem**: Census tracts created thousands of tiny disconnected regions. While technically accurate, humans struggle to visually reason about thousands of tiny specks. The map was accurate but not *compelling*.

3. **The Bridge Problem**: Minimizing region *count* (to reduce dust) created oddly-shaped regions with narrow "bridges" connecting dense areas.

4. **The Solution**: Minimize *perimeter* instead. This produces smooth, organic shapes that are easier to visually interpret while remaining accurate. Implemented via **Max-Flow Min-Cut optimization** with a user-controlled "surface tension" parameter.
```

#### 3. Reframe "How It Works" (lines 21-32)

**File**: `README.md`

**Current:**
```markdown
## How It Works

A slider controls lambda (0 to <1):

- **lambda ~ 0**: Minimizes area, showing high-resolution "dusty" city centers
- **lambda ~ 0.9**: Minimizes perimeter, creating smooth, compact blobs

Note: lambda=1.0 is mathematically degenerate and excluded from valid values.

**Note**: Due to computational complexity, geometries for various lambda values are pre-calculated. The web app serves as a visualizer for these pre-computed states.

See [METHODOLOGY.md](METHODOLOGY.md) for the mathematical formulation.
```

**New:**
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

### Success Criteria:

#### Automated Verification:
- [x] File exists and is valid markdown: `cat README.md | head -50`
- [x] No broken links: Check that METHODOLOGY.md link resolves
- [x] Tagline no longer contains "topology optimization experiment"
- [x] Blockquote no longer contains "Where does half of America"

#### Manual Verification:
- [x] Evolution story reads naturally and tells the iterative journey
- [x] No mention of "portfolio" in the file
- [x] Tone is approachable for general audience

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the changes look good before proceeding to the next phase.

---

## Phase 2: CLAUDE.md Updates

### Overview
Update developer/AI guidance with accurate project context, goals, and portfolio mention.

### Changes Required:

#### 1. Update Project Overview (line 7)

**File**: `CLAUDE.md`

**Current:**
```markdown
## Project Overview

Half of America is a topology optimization experiment that creates an interactive visualization of US population distribution. Instead of simple county-level "half of America lives here" maps, this project uses Census Tract data (~73,000 tracts) with Max-Flow Min-Cut optimization to generate smooth, organic shapes controlled by a "surface tension" parameter (λ).
```

**New:**
```markdown
## Project Overview

Half of America is an experimental data visualization project exploring US population concentration. It produces an interactive map highlighting the areas where 50% of Americans live, with a user-controlled slider to balance area minimization vs. perimeter smoothness.

**Project Goals:**
- Show how geographically concentrated the US population is
- Make the visualization compelling (not just accurate)
- Serve as a portfolio piece for data science work

The implementation uses Census Tract data (~73,000 tracts) with Max-Flow Min-Cut optimization to generate smooth, organic shapes controlled by a "surface tension" parameter (λ).
```

#### 2. Add Project Evolution Section (after Project Overview, before Naming Convention)

**File**: `CLAUDE.md`

Insert new section after the Project Overview paragraph, before the "**Naming Convention:**" line:

```markdown
**Project Evolution:**
The approach evolved through iteration:
1. County maps had the "San Bernardino Problem" (empty areas included)
2. Census tracts created "dust" (too many tiny regions to reason about)
3. Minimizing region count created "bridges" (narrow connections)
4. Minimizing perimeter produces smooth, compelling shapes

```

### Success Criteria:

#### Automated Verification:
- [x] File exists and is valid markdown: `cat CLAUDE.md | head -30`
- [x] Contains "portfolio piece": `grep -c "portfolio" CLAUDE.md` returns 1
- [x] Contains "Project Goals": `grep -c "Project Goals" CLAUDE.md` returns 1
- [x] Contains "Project Evolution": `grep -c "Project Evolution" CLAUDE.md` returns 1

#### Manual Verification:
- [x] Project Overview accurately describes the project's purpose
- [x] Evolution section provides useful context for developers/AI

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the changes look good before proceeding to the next phase.

---

## Phase 3: METHODOLOGY.md Motivation Section

### Overview
Add a technically-accurate motivation section at the top of METHODOLOGY.md, matching the file's existing technical tone.

### Changes Required:

#### 1. Add Motivation Section (after title, before Section 1)

**File**: `METHODOLOGY.md`

Insert new section after line 1 (`# Technical Methodology`), before line 3 (`## 1. Data Sources & Preprocessing`):

```markdown

## Motivation

Traditional "half of America" visualizations face several technical limitations:

1. **County Resolution**: County boundaries encompass vast unpopulated areas. San Bernardino County, for example, exceeds the land area of nine US states while containing primarily desert terrain.

2. **Dust Artifacts**: Using finer-grained units (e.g., Census Tracts) produces thousands of disconnected micro-regions. While mathematically accurate, this exceeds human perceptual limits for visual reasoning.

3. **Bridge Artifacts**: Minimizing region *count* to consolidate dust produces degenerate geometries with narrow "bridge" connections between dense population centers.

This methodology addresses these issues by minimizing *perimeter* rather than region count, producing smooth, topologically coherent shapes that remain accurate representations of population concentration.

```

### Success Criteria:

#### Automated Verification:
- [x] File exists and is valid markdown: `cat METHODOLOGY.md | head -20`
- [x] Contains "## Motivation": `grep -c "## Motivation" METHODOLOGY.md` returns 1
- [x] Section appears before "## 1. Data Sources": Line number of Motivation < line number of Data Sources

#### Manual Verification:
- [x] Motivation section matches technical tone of rest of file
- [x] Provides useful context for readers approaching the technical content

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that all documentation changes are complete and accurate.

---

## Testing Strategy

### Automated Tests:
- Verify all markdown files parse correctly
- Check for broken internal links
- Verify expected phrases are present/absent

### Manual Testing Steps:
1. Read README.md start to finish—does the evolution story flow naturally?
2. Read CLAUDE.md—does the Project Goals/Evolution provide useful context?
3. Read METHODOLOGY.md—does the Motivation section fit the technical tone?
4. Verify no mention of "portfolio" in README.md

## References

- Research document: `thoughts/shared/research/2025-11-22-documentation-improvement-recommendations.md`
- README.md: Current state at lines 1-135
- CLAUDE.md: Current state at lines 1-99
- METHODOLOGY.md: Current state at lines 1-91
