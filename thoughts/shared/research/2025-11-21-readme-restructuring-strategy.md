---
date: 2025-11-21T12:00:00-05:00
researcher: Claude
git_commit: ded94a34ce8f675002157a4c563bde68afd93b0b
branch: master
repository: half_america
topic: "README.md Restructuring Strategy - Documentation Organization"
tags: [research, documentation, readme, restructuring, best-practices]
status: complete
last_updated: 2025-11-21
last_updated_by: Claude
last_updated_note: "Resolved open questions with user decisions"
---

# Research: README.md Restructuring Strategy

**Date**: 2025-11-21T12:00:00-05:00
**Researcher**: Claude
**Git Commit**: ded94a34ce8f675002157a4c563bde68afd93b0b
**Branch**: master
**Repository**: half_america

## Research Question

README.md is getting long (238 lines). Should we create additional documentation files? If so, what should they be called and what should their purposes be? How can we improve README.md to fit the sort of project/repo this is?

## Summary

**TL;DR**: README is at 238 lines—acceptable but approaching the threshold where splitting becomes beneficial. The project should adopt a **"README as landing page, docs/ for depth"** strategy, creating an `API.md` file and consolidating metadata into a footer pattern. No action is urgent, but Phase 4 is the ideal time to restructure.

| Finding | Recommendation | Priority |
|---------|----------------|----------|
| API Reference is 55% of README | Create `docs/API.md` | Medium (do in Phase 4) |
| Four tiny footer sections | Consolidate into 1-2 sections | Low |
| No contributing guidelines | Create `CONTRIBUTING.md` | Low (when ready for contributors) |
| Missing architecture docs | Consider `ARCHITECTURE.md` after Phase 5 | Future |

---

## Current Documentation State

### File Inventory

| File | Lines | Content | % of Total |
|------|-------|---------|------------|
| README.md | 238 | Project overview, installation, API reference | 49% |
| ROADMAP.md | 111 | Implementation phases and progress | 23% |
| METHODOLOGY.md | 89 | Mathematical formulation | 18% |
| CLAUDE.md | 48 | AI assistant guidance | 10% |
| **Total** | **486** | | |

### README.md Section Breakdown

| Section | Lines | % of README | Content Type |
|---------|-------|-------------|--------------|
| Title + Badges | 5 | 2% | Metadata |
| Intro + Quote | 3 | 1% | Hook |
| The Problem | 10 | 4% | Context |
| How It Works | 11 | 5% | Solution overview |
| Installation | 17 | 7% | Setup |
| Usage | 16 | 7% | CLI commands |
| **API Reference** | **131** | **55%** | API documentation |
| Project Status | 5 | 2% | Status |
| License + Disclaimer | 6 | 3% | Legal/meta |

**Key observation**: API Reference (131 lines, 55%) dominates the README. This is the primary candidate for extraction.

---

## Best Practices Research

### Industry Standards for README Length

- **No hard limit**, but consensus: README should be scannable in 2-3 minutes
- **Pandas README**: ~190 lines (11.6 KB) - good benchmark for mature scientific project
- **Matplotlib README**: Deliberately concise - 4-5 sections pointing to external docs
- **Rule of thumb**: If >300 lines, strongly consider splitting

### README Role: "Landing Page, Not Encyclopedia"

Best practices from pyOpenSci, Real Python, and major Python projects:

| Keep in README | Move Elsewhere |
|----------------|----------------|
| One-sentence description | Full tutorials |
| Badges (version, CI, license) | Complete API reference |
| Quick-start example (5-15 lines) | Platform-specific installation |
| Installation basics | Detailed architecture |
| Links to full documentation | Historical changelog |
| License statement | Contributing guidelines |

### When to Create Separate Files

| File | Create When | Purpose |
|------|-------------|---------|
| `docs/API.md` | API section >100 lines | Detailed function/class reference |
| `CONTRIBUTING.md` | Ready for external contributors | Development setup, PR guidelines |
| `ARCHITECTURE.md` | Codebase >10k LOC | Code organization, design decisions |
| `CHANGELOG.md` | After first release | Version history |
| `docs/` with Sphinx | Production/Phase 5 | Auto-generated API docs |

---

## Analysis: What's Working, What's Not

### What's Working

1. **Clear problem statement** - "The Problem" section explains motivation well
2. **Good layered documentation** - README (overview) → METHODOLOGY (math) → code (implementation)
3. **Appropriate CLAUDE.md** - Quick reference without excessive duplication
4. **API Quick Start examples** - Useful for developers getting started

### What's Not Working

1. **API Reference dominates** (55% of README) - Makes scanning difficult
2. **Footer fragmentation** - Four tiny sections (Project Status, Documentation, License, Disclaimer)
3. **No contributing guidelines** - No `CONTRIBUTING.md` when contributors arrive
4. **Documentation section is redundant** - Links already exist in other sections

---

## Recommendations

### Recommendation 1: Create `docs/API.md`

**Rationale**: API Reference is 131 lines (55% of README). Moving it creates a focused README and dedicated API documentation.

**Structure for `docs/API.md`**:
```markdown
# API Reference

## Data Pipeline
[Current content from README]

## Graph Construction
[Current content from README]

## Optimization
[Current content from README]
```

**README changes**:
- Replace detailed API sections with "Quick Start" example only
- Add: "See [API Reference](docs/API.md) for detailed documentation"

**Timing**: Phase 4 (Post-Processing) is ideal - adding another API section would push README past 300 lines.

### Recommendation 2: Consolidate Footer Sections

**Current** (4 sections, 16 lines):
```markdown
## Project Status
## Documentation
## License
## Disclaimer
```

**Proposed** (2 sections, ~12 lines):
```markdown
## Project Status
**Current Phase**: Optimization Engine Complete (Phase 3)

For more information:
- [ROADMAP.md](ROADMAP.md) - Implementation plan
- [METHODOLOGY.md](METHODOLOGY.md) - Mathematical details

## License

MIT License. See [LICENSE](LICENSE).

*This is a personal experimental project exploring topology optimization and cartography. Not intended as a production tool.*
```

**Benefit**: Reduces visual clutter while retaining all information.

### Recommendation 3: Create `CONTRIBUTING.md` (Future)

**When**: When ready for external contributors (likely after Phase 5/public release)

**Contents**:
- Development setup (uv, Census API key)
- Code style (black, ruff, mypy)
- Testing approach
- PR guidelines

### Recommendation 4: Consider `ARCHITECTURE.md` (Future)

**When**: After Phase 5 when codebase is stable and >10k LOC

**Contents**:
- Module relationships
- Data flow diagram
- Key design decisions

---

## Proposed Documentation Structure

### Current
```
half-america/
├── README.md           (238 lines - all-in-one)
├── METHODOLOGY.md      (89 lines)
├── ROADMAP.md          (111 lines)
├── CLAUDE.md           (48 lines)
└── docs/
    └── archive/
        └── PROJECT_SUMMARY.md
```

### After Phase 4 (Recommended)
```
half-america/
├── README.md           (~120 lines - landing page)
├── METHODOLOGY.md      (89 lines)
├── ROADMAP.md          (111 lines)
├── CLAUDE.md           (48 lines)
└── docs/
    ├── API.md          (~150 lines - extracted)
    └── archive/
        └── PROJECT_SUMMARY.md
```

### After Phase 5 / Public Release (Future)
```
half-america/
├── README.md           (~100 lines)
├── CONTRIBUTING.md     (new)
├── METHODOLOGY.md
├── ROADMAP.md
├── CLAUDE.md
└── docs/
    ├── API.md
    ├── ARCHITECTURE.md (optional)
    └── archive/
```

---

## Decision Matrix

| Action | Effort | Impact | Timing |
|--------|--------|--------|--------|
| Create `docs/API.md` | Medium | High | Phase 4 |
| Consolidate footer sections | Low | Low | Now or Phase 4 |
| Create `CONTRIBUTING.md` | Low | Medium | Phase 5/public release |
| Add Sphinx/auto-docs | High | Medium | Phase 5 |
| Create `ARCHITECTURE.md` | Medium | Low | Post-Phase 5 |

---

## Answers to Specific Questions

### "Is README.md too long?"

**Answer**: At 238 lines, it's at the upper limit of acceptable but not critical. The API Reference (55%) is the issue, not overall length. Moving API docs would reduce README to ~120 lines (ideal).

### "Should we create another documentation file?"

**Answer**: Yes, create `docs/API.md` during Phase 4. This is the natural inflection point—adding Phase 4 API docs would push README past 300 lines.

### "What should it be called and what should its purpose be?"

| File | Purpose |
|------|---------|
| `docs/API.md` | Complete API reference (functions, types, examples) |
| `CONTRIBUTING.md` | Development setup and contribution guidelines (future) |

### "Are there other things we can do to improve README.md?"

1. **Consolidate footer sections** - Merge Documentation into Project Status
2. **Add navigation aids** - Brief intro sentence before API Reference
3. **Keep Quick Start examples** - Even after API extraction, keep 1 example per module in README

---

## Implementation Plan

### Phase 4 (Recommended)

1. Create `docs/API.md` with current API Reference content
2. Replace README API sections with Quick Start examples + link to docs/API.md
3. Consolidate footer sections
4. Update CLAUDE.md to reference docs/API.md

### If Acting Now (Optional)

If you want to act before Phase 4:
1. Consolidate footer sections only (low-risk, immediate improvement)
2. Defer API extraction until Phase 4 adds more content

---

## Related Research

- `thoughts/shared/research/2025-11-21-readme-critical-evaluation.md` - Content quality issues
- `thoughts/shared/research/2025-11-21-readme-organization-audit.md` - Previous redundancy analysis
- `thoughts/shared/plans/2025-11-21-readme-organization.md` - Prior restructuring plan

---

## Open Questions (Resolved)

1. **Should `docs/API.md` be split further (one file per module) or kept as single file?**

   **Decision**: Keep as single file. Can always split later if it becomes unwieldy.

2. **Should Quick Start examples in README show expected output?**

   **Decision**: Keep current comment-style approach (e.g., `# Output: {...}`).

   *Rationale*: The current approach is a good middle ground—lightweight, signals expected behavior without being verbose, and avoids maintenance burden of keeping output in sync with implementation changes.

3. **Should we add a Table of Contents to README after restructuring?**

   **Decision**: No. Skip the manual TOC.

   *Rationale*: At ~120 lines post-restructuring, the README will be short enough that a TOC adds more clutter than value. GitHub's built-in TOC (hamburger icon next to file name) handles navigation for those who need it. Revisit if README grows past ~200 lines again.
