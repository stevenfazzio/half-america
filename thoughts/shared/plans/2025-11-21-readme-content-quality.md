# README Content Quality Improvements Implementation Plan

## Overview

Implement README content quality improvements based on the critical evaluation research (`thoughts/shared/research/2025-11-21-readme-critical-evaluation.md`). The changes focus on merging redundant sections, relocating misplaced content, and standardizing API subsection naming to improve the new developer experience.

## Current State Analysis

The README has structural and content issues identified from a new developer perspective:

| Issue | Severity | Location |
|-------|----------|----------|
| "Background" section is redundant with intro | **High** | Lines 10-12 |
| Census API setup buried in wrong location | **High** | Lines 71-78 |
| Inconsistent subsection naming ("Quick Start" ×2, "Available Functions" ×2) | **Medium** | API Reference sections |
| "Documentation" section is redundant | **Low** | Lines 169-172 |

### Key Discoveries:
- `README.md:10-12` - Background is a single paragraph that should merge into The Problem
- `README.md:71-78` - Census API setup is a prerequisite, not an API feature
- `README.md:100,145` - "Available Functions" appears twice with no differentiation
- `README.md:169-172` - Documentation links already exist in other sections

## Desired End State

After implementation:
1. "Background" content flows naturally into "The Problem" section
2. Census API key setup appears in Installation (before Usage)
3. API subsections use consistent naming: "Function Reference" instead of "Available Functions"
4. API Reference has a navigation note helping readers find what they need
5. Redundant "Documentation" section is removed

### Verification:
- README structure follows the proposed outline from research
- No duplicate H4 heading names within API Reference
- New developer can follow Installation → Usage without hitting missing API key error

## What We're NOT Doing

- Not splitting API Reference into a separate file (premature - wait until Phase 4/5)
- Not adding Table of Contents (let GitHub auto-generate)
- Not renaming "The Problem" heading (user is open to it but current name is acceptable)
- Not expanding Quick Start examples with expected output (defer to separate task)
- Not adding "Data Schema" section to Data Pipeline (would require additional research)

## Implementation Approach

Execute changes in order of dependency: structural merges first, then relocations, then renames. Each phase is independently verifiable.

---

## Phase 1: Merge Background into The Problem

### Overview
Combine the single-paragraph Background section into The Problem section, creating a cohesive narrative: "Here's what exists → Here's why it's flawed."

### Changes Required:

#### 1. Merge sections in README.md
**File**: `README.md`
**Changes**: Delete "## Background" heading and merge its content as the opening paragraph of "## The Problem"

**Before** (lines 10-21):
```markdown
## Background

There is a genre of viral maps that frequently circulates on the internet, typically titled "Half of the United States Lives In These Counties" ([example](https://www.businessinsider.com/half-of-the-united-states-lives-in-these-counties-2013-9)). These maps illustrate the extreme geographic concentration of the US population using a simple algorithm: rank counties by population and select the top N until exceeding 50% of the total.

## The Problem

Traditional "half of America lives here" maps have two issues:

1. **The San Bernardino Problem**: County boundaries include vast empty areas (San Bernardino County is larger than nine US states but mostly desert)
2. **The Dust Problem**: Using smaller units creates thousands of disconnected specks that fail as visualization

This project solves both using **Max-Flow Min-Cut optimization** with a user-controlled "surface tension" parameter.
```

**After**:
```markdown
## The Problem

There is a genre of viral maps that frequently circulates on the internet, typically titled "Half of the United States Lives In These Counties" ([example](https://www.businessinsider.com/half-of-the-united-states-lives-in-these-counties-2013-9)). These maps illustrate the extreme geographic concentration of the US population using a simple algorithm: rank counties by population and select the top N until exceeding 50% of the total.

Traditional approaches have two issues:

1. **The San Bernardino Problem**: County boundaries include vast empty areas (San Bernardino County is larger than nine US states but mostly desert)
2. **The Dust Problem**: Using smaller units creates thousands of disconnected specks that fail as visualization

This project solves both using **Max-Flow Min-Cut optimization** with a user-controlled "surface tension" parameter.
```

### Success Criteria:

#### Automated Verification:
- [x] No "## Background" heading exists: `grep -c "^## Background" README.md` returns 0
- [x] "## The Problem" section exists and contains Business Insider link
- [x] Markdown renders correctly: no lint errors

#### Manual Verification:
- [x] Section reads naturally as cohesive narrative
- [x] No content was lost from original Background section

**Implementation Note**: After completing this phase, proceed to Phase 2.

---

## Phase 2: Relocate Census API Setup to Installation

### Overview
Move the Census API key setup from "Data Pipeline > Setup" to the Installation section. This ensures new developers set up credentials before attempting to use the CLI.

### Changes Required:

#### 1. Add Census API subsection to Installation
**File**: `README.md`
**Changes**: Add "### Census API Key" subsection after the `uv sync` code block

**Current Installation section** (lines 34-42):
```markdown
## Installation

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone <repo-url>
cd half_america
uv sync
```
```

**New Installation section**:
```markdown
## Installation

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone <repo-url>
cd half_america
uv sync
```

### Census API Key

The data pipeline requires a Census API key:

1. Get a free key from https://api.census.gov/data/key_signup.html
2. Create your environment file:
   ```bash
   cp .env.example .env
   # Add your CENSUS_API_KEY to .env
   ```
```

#### 2. Remove Setup subsection from Data Pipeline
**File**: `README.md`
**Changes**: Delete the "#### Setup" subsection (lines 71-78) from Data Pipeline

**Delete this block**:
```markdown
#### Setup

1. Get a Census API key from https://api.census.gov/data/key_signup.html
2. Copy `.env.example` to `.env` and add your key:
   ```bash
   cp .env.example .env
   # Edit .env and add your CENSUS_API_KEY
   ```
```

### Success Criteria:

#### Automated Verification:
- [x] "### Census API Key" exists under Installation: `grep -A1 "^## Installation" README.md` followed by subsection check
- [x] No "#### Setup" under Data Pipeline: `grep -c "^#### Setup" README.md` returns 0
- [x] Census API URL appears only once in document

#### Manual Verification:
- [x] Installation section flows logically: requirements → clone → sync → API key
- [x] Data Pipeline section starts with description, then Quick Start

**Implementation Note**: After completing this phase, proceed to Phase 3.

---

## Phase 3: Standardize API Subsection Names

### Overview
Rename duplicate subsection names and add a navigation note to API Reference. Changes:
- "Available Functions" → "Function Reference" (both sections)
- Add brief intro/navigation note to API Reference

### Changes Required:

#### 1. Add navigation note to API Reference intro
**File**: `README.md`
**Changes**: Expand the API Reference intro paragraph

**Current** (lines 63-65):
```markdown
## API Reference

The following sections document the Python API for programmatic use.
```

**New**:
```markdown
## API Reference

The following sections document the Python API for programmatic use. Each module includes a Quick Start example and full function reference.
```

#### 2. Rename "Available Functions" to "Function Reference" in Data Pipeline
**File**: `README.md`
**Changes**: Rename heading at line 100

**Before**: `#### Available Functions`
**After**: `#### Function Reference`

#### 3. Rename "Available Functions" to "Function Reference" in Graph Construction
**File**: `README.md`
**Changes**: Rename heading at line 145

**Before**: `#### Available Functions`
**After**: `#### Function Reference`

### Success Criteria:

#### Automated Verification:
- [x] No "Available Functions" headings: `grep -c "Available Functions" README.md` returns 0
- [x] Two "Function Reference" headings: `grep -c "Function Reference" README.md` returns 2
- [x] API Reference intro mentions "Quick Start" and "function reference"

#### Manual Verification:
- [x] Subsection names are now unique when searching document
- [x] Navigation note helps reader understand API Reference structure

**Implementation Note**: After completing this phase, proceed to Phase 4.

---

## Phase 4: Remove Redundant Documentation Section

### Overview
Remove the "## Documentation" section since both links already appear elsewhere:
- METHODOLOGY.md is linked in "How It Works" (line 32)
- ROADMAP.md is linked in "Project Status" (line 167)

### Changes Required:

#### 1. Delete Documentation section
**File**: `README.md`
**Changes**: Delete lines 169-172

**Delete this block**:
```markdown
## Documentation

- [METHODOLOGY.md](METHODOLOGY.md) - Mathematical formulation and algorithm
- [ROADMAP.md](ROADMAP.md) - Implementation roadmap
```

### Success Criteria:

#### Automated Verification:
- [x] No "## Documentation" heading: `grep -c "^## Documentation" README.md` returns 0
- [x] METHODOLOGY.md still linked in How It Works section
- [x] ROADMAP.md still linked in Project Status section

#### Manual Verification:
- [x] Footer sections flow naturally: Project Status → License → Disclaimer
- [x] No information was lost (links exist elsewhere)

**Implementation Note**: After completing this phase, all changes are complete.

---

## Testing Strategy

### Automated Tests:
- Markdown linting passes
- All internal links resolve correctly
- No duplicate H2/H3/H4 headings within same parent section

### Manual Testing Steps:
1. Read README top-to-bottom as a new developer
2. Follow Installation instructions - should include API key setup
3. Verify The Problem section reads as cohesive narrative
4. Search for "Quick Start" - should find two results with clear parent context
5. Search for "Function Reference" - should find two results (replacing "Available Functions")

## References

- Research document: `thoughts/shared/research/2025-11-21-readme-critical-evaluation.md`
- Current README: `README.md`
