# README Organization Implementation Plan

## Overview

Address documentation redundancy and improve README scanability by condensing duplicated commands in CLAUDE.md and adding an "API Reference" grouping header in README.md.

## Current State Analysis

- **CLAUDE.md** (54 lines): Commands section duplicates README.md verbatim with slight formatting differences
- **README.md** (177 lines): API documentation (93 lines, 53%) lacks visual grouping header
- Both files are well-structured but have maintenance burden from duplication

### Key Discoveries:
- `CLAUDE.md:11-32` - Verbose multi-line commands format (22 lines)
- `README.md:46-60` - Usage/commands section (source of truth)
- `README.md:63-157` - Data Pipeline and Graph Construction sections need grouping header

## Desired End State

1. CLAUDE.md has condensed commands section (~10 lines vs current 22) with reference to README
2. README.md has "API Reference" header grouping Data Pipeline and Graph Construction sections
3. CLAUDE.md Documentation section links to specific README section

### Verification:
- Both files render correctly in markdown preview
- CLAUDE.md is shorter but retains all essential quick-reference value
- README.md has improved visual hierarchy and scanability

## What We're NOT Doing

- Not deleting any content from README.md
- Not moving API documentation to separate files (deferred per research)
- Not adding sphinx/mkdocs (deferred per research)
- Not changing METHODOLOGY.md or ROADMAP.md

## Implementation Approach

Two simple edits to markdown files, executed sequentially to allow verification.

---

## Phase 1: Condense CLAUDE.md Commands Section

### Overview
Replace verbose multi-line commands format with compact single-line format, adding reference to README as source of truth.

### Changes Required:

#### 1. CLAUDE.md Commands Section
**File**: `CLAUDE.md`
**Lines**: 9-32
**Changes**: Replace verbose format with condensed format

**Before** (lines 9-32):
```markdown
## Commands

```bash
# Install dependencies (uses uv)
uv sync

# Run tests
uv run pytest

# Run single test
uv run pytest tests/test_sanity.py::test_sanity -v

# Format code
uv run black src/ tests/

# Lint
uv run ruff check src/ tests/

# Type check
uv run mypy src/

# Run the CLI
uv run half-america
```
```

**After**:
```markdown
## Commands

Common commands (see [README.md#usage](README.md#usage) for full list):

```bash
uv sync                              # Install dependencies
uv run pytest                        # Run tests
uv run pytest path/to/test.py -v     # Run single test
uv run black src/ tests/             # Format code
uv run ruff check src/ tests/        # Lint
uv run mypy src/                     # Type check
uv run half-america                  # Run CLI
```
```

### Success Criteria:

#### Automated Verification:
- [ ] File renders correctly: preview CLAUDE.md in markdown viewer
- [ ] All commands are present and syntactically correct
- [ ] Link `README.md#usage` resolves correctly in GitHub

#### Manual Verification:
- [ ] Commands section is visually scannable
- [ ] Reference to README is clear

**Implementation Note**: After completing this phase, proceed to Phase 2.

---

## Phase 2: Add API Reference Header to README.md

### Overview
Add "API Reference" section header before Data Pipeline to improve visual hierarchy and scanability.

### Changes Required:

#### 1. README.md API Reference Header
**File**: `README.md`
**Line**: 63 (before "## Data Pipeline")
**Changes**: Insert new section header with brief intro

**Before** (lines 61-65):
```markdown
```

## Data Pipeline

The data pipeline downloads Census Tract geometries and population data for the contiguous United States.
```

**After**:
```markdown
```

## API Reference

The following sections document the Python API for programmatic use.

### Data Pipeline

The data pipeline downloads Census Tract geometries and population data for the contiguous United States.
```

#### 2. Update Graph Construction to Subsection
**File**: `README.md`
**Line**: 108
**Changes**: Change `## Graph Construction` to `### Graph Construction`

**Before**:
```markdown
## Graph Construction
```

**After**:
```markdown
### Graph Construction
```

### Success Criteria:

#### Automated Verification:
- [ ] File renders correctly: preview README.md in markdown viewer
- [ ] Table of contents (if auto-generated) shows correct hierarchy
- [ ] All internal links still work

#### Manual Verification:
- [ ] API sections are visually grouped under single header
- [ ] README is easier to scan

**Implementation Note**: After completing this phase, all changes are complete.

---

## Testing Strategy

### Manual Testing Steps:
1. Preview CLAUDE.md in markdown viewer - verify formatting
2. Preview README.md in markdown viewer - verify hierarchy
3. Click `README.md#usage` link from CLAUDE.md - verify it navigates correctly
4. Verify GitHub renders both files correctly (if pushing)

## References

- Research: `thoughts/shared/research/2025-11-21-readme-organization-audit.md`
- Current CLAUDE.md: 54 lines
- Current README.md: 177 lines
