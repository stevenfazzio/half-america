---
date: 2025-01-20T00:00:00-08:00
researcher: Claude
git_commit: b7617a3
branch: master
repository: half_america
topic: "Archive PROJECT_SUMMARY.md - Gap Analysis and Migration Plan"
tags: [research, documentation, archive, migration]
status: complete
last_updated: 2025-01-20
last_updated_by: Claude
---

# Research: Archive PROJECT_SUMMARY.md - Gap Analysis and Migration Plan

**Date**: 2025-01-20
**Researcher**: Claude
**Git Commit**: b7617a3
**Branch**: master
**Repository**: half_america

## Research Question

Analyze PROJECT_SUMMARY.md content to determine what information needs to be migrated to other documentation files (README.md, CLAUDE.md, ROADMAP.md, METHODOLOGY.md) before archiving.

## Summary

PROJECT_SUMMARY.md contains valuable project context that is **partially but not fully** represented in other documentation. Before archiving, **two key sections** need to be migrated to README.md:

1. **Background & Inspiration** - The "viral maps" genre context and Business Insider reference
2. **Technical constraints note** - Pre-computed geometries explanation

After migration, README.md's Documentation section should be updated to remove the PROJECT_SUMMARY.md reference.

## Detailed Findings

### Content Coverage Analysis

| PROJECT_SUMMARY.md Content | Coverage Status | Location |
|---------------------------|-----------------|----------|
| Background & Inspiration (viral maps, Business Insider) | **NOT COVERED** | - |
| San Bernardino Problem | ✅ Covered | README.md:13-14 |
| Dust Problem | ✅ Covered | README.md:15-16 |
| Project Goal (topology optimization) | ✅ Covered | README.md:6,17; CLAUDE.md:7 |
| Slider/λ parameter explanation | ✅ Covered | README.md:21-24; CLAUDE.md:46-47 |
| UX description (megaregions merging) | **PARTIAL** | README has basics, missing vivid description |
| Scope: Geography (contiguous US) | ✅ Implied | README/METHODOLOGY |
| Scope: Data Source (Census Tract) | ✅ Covered | METHODOLOGY.md:7-8 |
| Scope: Pre-computed geometries | **NOT COVERED** | - |
| Disclaimer | ✅ Covered | README.md:73-75 |

### Gap 1: Background & Inspiration (PROJECT_SUMMARY.md lines 3-9)

**Missing content:**
```markdown
There is a genre of viral maps that frequently circulates on the internet,
typically titled "Half of the United States Lives In These Counties." An example
of this can be seen in this [Business Insider article](https://www.businessinsider.com/half-of-the-united-states-lives-in-these-counties-2013-9).

These maps serve a simple purpose: they illustrate the extreme geographic
concentration of the US population. The methodology is usually a simple sorting algorithm:
1. Rank all counties by population.
2. Select the top N counties until the cumulative sum exceeds 50% of the total US population.
```

**Recommendation**: Add this section to README.md as "Background" before "The Problem" section. This provides important context for why the project exists.

### Gap 2: Pre-computed Geometries Technical Constraint (PROJECT_SUMMARY.md line 32)

**Missing content:**
```markdown
Due to the computational complexity of the optimization, the map states for
various λ values will be pre-calculated. The web app will serve as a visualizer
for these pre-computed geometries.
```

**Recommendation**: Add this to README.md's "How It Works" section or create a brief "Technical Note" subsection.

### Gap 3: Enhanced UX Description (PROJECT_SUMMARY.md lines 26-27)

**Missing content:**
```markdown
By sliding between these values, the user can visualize the "surface tension"
of American geography, observing how distinct urban centers merge into megaregions
and eventually into continental blocks.
```

**Recommendation**: This is optional but would enhance README.md's "How It Works" section with more evocative language.

## Recommended Implementation Plan

### Step 1: Update README.md

Add new "Background" section after the blockquote and before "The Problem":

```markdown
## Background

There is a genre of viral maps that frequently circulates on the internet, typically titled "Half of the United States Lives In These Counties" ([example](https://www.businessinsider.com/half-of-the-united-states-lives-in-these-counties-2013-9)). These maps illustrate the extreme geographic concentration of the US population using a simple algorithm: rank counties by population and select the top N until exceeding 50% of the total.
```

### Step 2: Update README.md "How It Works" section

Add technical note about pre-computation:

```markdown
**Note**: Due to computational complexity, geometries for various lambda values are pre-calculated. The web app serves as a visualizer for these pre-computed states.
```

### Step 3: Update README.md Documentation section

Change from:
```markdown
## Documentation

- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Full project vision and scope
- [METHODOLOGY.md](METHODOLOGY.md) - Mathematical formulation and algorithm
- [ROADMAP.md](ROADMAP.md) - Implementation roadmap
```

To:
```markdown
## Documentation

- [METHODOLOGY.md](METHODOLOGY.md) - Mathematical formulation and algorithm
- [ROADMAP.md](ROADMAP.md) - Implementation roadmap
```

### Step 4: Update ROADMAP.md

Change line 7 from:
```markdown
Documentation (METHODOLOGY.md, PROJECT_SUMMARY.md) is complete
```

To:
```markdown
Documentation (METHODOLOGY.md, README.md) is complete
```

### Step 5: Create archive directory

```bash
mkdir -p docs/archive
```

### Step 6: Add archive notice to PROJECT_SUMMARY.md

Prepend to the file:
```markdown
> **ARCHIVED**: This document has been archived as of [DATE]. It is a static historical
> record and should not be updated. Current project documentation can be found in:
> - [README.md](../../README.md) - Project overview and quick start
> - [METHODOLOGY.md](../../METHODOLOGY.md) - Technical methodology
> - [ROADMAP.md](../../ROADMAP.md) - Implementation roadmap

---

```

### Step 7: Move file

```bash
git mv PROJECT_SUMMARY.md docs/archive/PROJECT_SUMMARY.md
```

## Code References

- `PROJECT_SUMMARY.md:3-9` - Background & Inspiration section (to migrate)
- `PROJECT_SUMMARY.md:29-32` - Scope section with pre-computation note
- `README.md:63-67` - Documentation section (to update)
- `ROADMAP.md:7` - Reference to PROJECT_SUMMARY.md (to update)

## Architecture Insights

The documentation structure follows a clear separation:
- **README.md**: Public-facing intro, quick start, high-level overview
- **METHODOLOGY.md**: Deep technical/mathematical details
- **ROADMAP.md**: Implementation tracking
- **CLAUDE.md**: AI assistant guidance

PROJECT_SUMMARY.md served as an early "vision document" that predates the more structured documentation. Its content has largely been distributed but the narrative origin story is worth preserving in README.md.

## Open Questions

1. Should the Business Insider link be kept as-is, or should we note it may be paywalled/unavailable?
2. Should we create a `docs/` README explaining the archive structure?
