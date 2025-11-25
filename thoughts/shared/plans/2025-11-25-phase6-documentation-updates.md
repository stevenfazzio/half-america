# Phase 6 Documentation Updates Implementation Plan

## Overview

Update project documentation to reflect that Phase 6 (Map Final Touches) is complete. This involves updating status indicators, correcting outdated examples, adding new feature descriptions, and archiving planning documents.

## Current State Analysis

Phase 6 is fully implemented with all milestones checked off in ROADMAP.md (lines 144-162), but documentation still references Phase 5 as current and contains outdated examples.

### Key Discoveries:
- ROADMAP.md:7 - Status says "in progress" but all milestones are `[x]`
- README.md:36 - References λ≈0.9 but actual max is 0.98 (per `web/src/types/lambda.ts:15`)
- README.md:73 - CLI example uses `--lambda-step 0.05` but production uses 0.01
- README.md:151 - Says "Phase 5" but Phase 6 is complete
- CLAUDE.md:109 - Still says "Phase 5" for web frontend
- METHODOLOGY.md:19 - Missing year specifics (TIGER 2024, ACS 2022)
- docs/tab_strategy.md - Implementation complete, should be archived

## Desired End State

All documentation accurately reflects the current state:
- Phase 6 marked as complete
- Lambda examples match actual implementation (0.98 max, 0.01 step)
- Phase 6 features (tabs, navigation, KaTeX) documented
- Geographic scope documented in METHODOLOGY.md
- tab_strategy.md archived with notice

### Verification:
- No references to Phase 5 as "current"
- Lambda values match `web/src/types/lambda.ts`
- New features (tabs, hash routing, KeepMounted) documented
- `docs/archive/tab_strategy.md` exists with archive notice

## What We're NOT Doing

- Adding new features to the web app
- Changing code (documentation only)
- Creating new documentation files (except archiving existing)
- Updating docs/API.md (already current)

## Implementation Approach

Sequential updates to each documentation file, prioritized by impact. Each phase is a single file for atomic commits.

---

## Phase 1: ROADMAP.md Status Update

### Overview
Update the status line from "in progress" to "complete".

### Changes Required:

#### 1. Status Line
**File**: `ROADMAP.md`
**Line**: 7
**Changes**: Update status text

**Current**:
```markdown
**Phase 6: Map Final Touches** is in progress. The site is live at https://stevenfazzio.github.io/half-america
```

**New**:
```markdown
**Phase 6: Map Final Touches** is complete. The site is live at https://stevenfazzio.github.io/half-america
```

### Success Criteria:

#### Automated Verification:
- [ ] File contains "Phase 6: Map Final Touches** is complete"
- [ ] No linting errors

#### Manual Verification:
- [ ] ROADMAP.md reads correctly with Phase 6 complete

---

## Phase 2: README.md Updates

### Overview
Update project status, fix lambda examples, and add Phase 6 features.

### Changes Required:

#### 1. Lambda Upper Bound Example
**File**: `README.md`
**Line**: 36
**Changes**: Update λ≈0.9 to λ≈0.98

**Current**:
```markdown
- **λ ≈ 0.9**: Prioritizes perimeter minimization. Creates smooth, compact regions that are easier to reason about while remaining accurate.
```

**New**:
```markdown
- **λ ≈ 0.98**: Prioritizes perimeter minimization. Creates smooth, compact regions that are easier to reason about while remaining accurate.
```

#### 2. CLI Lambda Step Example
**File**: `README.md`
**Line**: 73
**Changes**: Update example to match production (0.01)

**Current**:
```bash
uv run half-america precompute --lambda-step 0.05  # Finer granularity
```

**New**:
```bash
uv run half-america precompute --lambda-step 0.01  # Match production (99 values)
```

#### 3. Project Status Section
**File**: `README.md`
**Lines**: 149-153
**Changes**: Update phase and add features

**Current**:
```markdown
## Project Status

**Current Phase**: Web Frontend Complete (Phase 5)

The interactive visualization is live at https://stevenfazzio.github.io/half-america
```

**New**:
```markdown
## Project Status

**Current Phase**: Map Final Touches Complete (Phase 6)

The interactive visualization is live at https://stevenfazzio.github.io/half-america

**Features:**
- Interactive map with smooth lambda slider (99 increments from 0.00 to 0.98)
- Real-time statistics: population percentage and land area percentage
- Story tab with project narrative and evolution explanation
- Method tab with technical details and mathematical formulation (KaTeX)
- Hash-based routing for shareable URLs (`#map`, `#story`, `#method`)
- Responsive design (desktop and mobile optimized)
```

#### 4. Frontend Description
**File**: `README.md`
**Line**: 119
**Changes**: Add tab structure mention

**Current**:
```markdown
The frontend is built with React + Vite + MapLibre GL JS + deck.gl. No API keys required.
```

**New**:
```markdown
The frontend is built with React + Vite + MapLibre GL JS + deck.gl + KaTeX. The app features three tabs (Map, Story, Method) with hash-based routing. No API keys required.
```

### Success Criteria:

#### Automated Verification:
- [ ] README.md contains "λ ≈ 0.98"
- [ ] README.md contains "--lambda-step 0.01"
- [ ] README.md contains "Phase 6"
- [ ] README.md contains "KaTeX"

#### Manual Verification:
- [ ] README renders correctly on GitHub
- [ ] Examples are accurate and clear

---

## Phase 3: CLAUDE.md Updates

### Overview
Update architecture section and add navigation pattern documentation.

### Changes Required:

#### 1. Frontend Stack
**File**: `CLAUDE.md`
**Line**: 62
**Changes**: Add KaTeX to stack

**Current**:
```markdown
**Stack**: React + Vite + MapLibre GL JS + deck.gl. No API keys required.
```

**New**:
```markdown
**Stack**: React + Vite + MapLibre GL JS + deck.gl + KaTeX. No API keys required.
```

#### 2. Add Navigation Pattern
**File**: `CLAUDE.md`
**After line**: 64
**Changes**: Add navigation documentation

**Insert**:
```markdown

**Navigation**: The app uses hash-based routing (`#map`, `#story`, `#method`) with three tabs. The Map tab uses a KeepMounted pattern to preserve WebGL state when switching tabs.
```

#### 3. Architecture Status
**File**: `CLAUDE.md`
**Line**: 109
**Changes**: Update from "Phase 5" to "implemented"

**Current**:
```markdown
- **Web Frontend:** React, MapLibre GL JS (basemap), deck.gl (data visualization) - *Phase 5*
```

**New**:
```markdown
- **Web Frontend:** React, MapLibre GL JS (basemap), deck.gl (data visualization) - *implemented*
```

#### 4. Documentation Section
**File**: `CLAUDE.md`
**Line**: 132 (end of Documentation section)
**Changes**: Add reference to tab_strategy.md (will point to archive)

**Current**:
```markdown
- [ROADMAP.md](ROADMAP.md) - Implementation phases and roadmap
```

**New**:
```markdown
- [ROADMAP.md](ROADMAP.md) - Implementation phases and roadmap
- [docs/archive/tab_strategy.md](docs/archive/tab_strategy.md) - Tab structure design rationale (archived)
```

### Success Criteria:

#### Automated Verification:
- [ ] CLAUDE.md contains "KaTeX"
- [ ] CLAUDE.md contains "KeepMounted"
- [ ] CLAUDE.md contains "implemented" (not "Phase 5") for web frontend
- [ ] CLAUDE.md references docs/archive/tab_strategy.md

#### Manual Verification:
- [ ] CLAUDE.md provides accurate developer guidance

---

## Phase 4: METHODOLOGY.md Updates

### Overview
Add geographic scope section and update data source details.

### Changes Required:

#### 1. Data Source Years
**File**: `METHODOLOGY.md`
**Line**: 19
**Changes**: Add specific years

**Current**:
```markdown
* **Source:** US Census Bureau TIGER/Line Shapefiles and ACS 5-Year Estimates.
```

**New**:
```markdown
* **Source:** US Census Bureau TIGER/Line Shapefiles (2024) and ACS 5-Year Estimates (2022).
```

#### 2. Future Tense Fix
**File**: `METHODOLOGY.md`
**Line**: 24
**Changes**: Change "will be" to "are"

**Current**:
```markdown
* **Quantization:** Coordinates will be snapped to a high-precision integer grid (via TopoJSON) to eliminate micro-gaps between tracts.
```

**New**:
```markdown
* **Quantization:** Coordinates are snapped to a high-precision integer grid (via TopoJSON) to eliminate micro-gaps between tracts.
```

#### 3. Geographic Scope Section
**File**: `METHODOLOGY.md`
**After line**: 26 (after section 1.2)
**Changes**: Add new section 1.3

**Insert**:
```markdown

### 1.3 Geographic Scope

This analysis covers the **conterminous United States only**—the 48 states physically connected on the North American mainland, plus the District of Columbia.

**Excluded Areas:**
- Alaska, Hawaii, Puerto Rico, and other territories

**Rationale:**
- **Projection**: Albers Equal Area Conic (EPSG:5070) is optimized for conterminous U.S.
- **Visualization**: Assumes continuous landmass without inset maps
- **Interpretation**: Connected landmass simplifies visual story

**Terminology**: "America" in this document refers specifically to the conterminous United States.
```

### Success Criteria:

#### Automated Verification:
- [ ] METHODOLOGY.md contains "TIGER/Line Shapefiles (2024)"
- [ ] METHODOLOGY.md contains "ACS 5-Year Estimates (2022)"
- [ ] METHODOLOGY.md contains "Coordinates are snapped" (not "will be")
- [ ] METHODOLOGY.md contains "### 1.3 Geographic Scope"
- [ ] METHODOLOGY.md contains "conterminous United States"

#### Manual Verification:
- [ ] Section numbering flows correctly (1.1, 1.2, 1.3)
- [ ] Geographic scope section is clear and accurate

---

## Phase 5: Archive tab_strategy.md

### Overview
Move tab_strategy.md to docs/archive/ with archive notice.

### Changes Required:

#### 1. Create Archive Directory
**Command**: `mkdir -p docs/archive`

#### 2. Move and Update File
**From**: `docs/tab_strategy.md`
**To**: `docs/archive/tab_strategy.md`
**Changes**: Add archive notice at top

**Add to top of file**:
```markdown
> **Archive Notice** (2025-11-25): This document was used to plan the tab structure implemented in Phase 6. For current implementation details, see [ROADMAP.md](../../ROADMAP.md#phase-6-map-final-touches).

---

```

### Success Criteria:

#### Automated Verification:
- [ ] `docs/archive/tab_strategy.md` exists
- [ ] `docs/tab_strategy.md` does not exist
- [ ] Archive file contains "Archive Notice"

#### Manual Verification:
- [ ] Archive notice link works correctly

---

## Testing Strategy

### Automated Tests:
No code changes, so no unit tests needed.

### Manual Testing Steps:
1. View each documentation file on GitHub to ensure markdown renders correctly
2. Verify all internal links work (especially after tab_strategy.md move)
3. Confirm live site URL is accessible
4. Check METHODOLOGY.md section numbering

## References

- Original research: `thoughts/shared/research/2025-11-25-phase6-documentation-updates.md`
- Lambda configuration: `web/src/types/lambda.ts:15`
- Geographic scope source: `web/src/components/MethodTab.tsx:121-174`
- Previous documentation updates: `thoughts/shared/plans/2025-11-2*-documentation*.md`
