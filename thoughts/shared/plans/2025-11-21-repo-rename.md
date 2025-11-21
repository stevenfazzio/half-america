# Repository Rename Implementation Plan

## Overview

Rename the local repository directory from `half_america` to `half-america` before creating the GitHub remote. This follows Python/GitHub conventions where distribution names use hyphens while Python module names use underscores.

## Current State Analysis

- **Local directory**: `half_america`
- **pyproject.toml**: Already correctly configured with `name = "half-america"` (distribution) and module `half_america`
- **Git remotes**: None configured (not yet on GitHub)
- **Virtual environment**: `.venv` exists with absolute paths that will break on rename

### Key Discoveries:
- No code changes needed - all Python imports use `half_america` module name
- pyproject.toml:2 already has `name = "half-america"`
- pyproject.toml:41 has CLI entry point `half-america = "half_america:main"`
- No GitHub URLs exist in codebase
- No CI/CD configuration exists

## Desired End State

- Repository directory named `half-america`
- GitHub repository created as `half-america`
- Git remote configured pointing to GitHub
- Working virtual environment
- Documentation updated to clarify naming convention

### Verification:
- `pwd` shows `/Users/stevenfazzio/repos/half-america`
- `git remote -v` shows GitHub remote
- `uv run half-america --help` works
- `uv run pytest` passes

## What We're NOT Doing

- Renaming the Python module (stays `half_america`)
- Updating historical research document frontmatter
- Changing pyproject.toml (already correct)
- Modifying any Python imports

## Implementation Approach

Since there's no GitHub remote yet, this is a simple local rename followed by GitHub repo creation. The virtual environment must be recreated after the rename because it contains absolute paths.

---

## Phase 1: Rename Local Directory

### Overview
Deactivate and remove the virtual environment, then rename the directory.

### Steps:

```bash
# 1. Deactivate venv (if active)
deactivate

# 2. Remove old venv (paths will be invalid after rename)
rm -rf /Users/stevenfazzio/repos/half_america/.venv

# 3. Rename directory
cd /Users/stevenfazzio/repos
mv half_america half-america
cd half-america

# 4. Recreate venv
uv sync
```

### Success Criteria:

#### Automated Verification:
- [x] Directory exists: `ls -la /Users/stevenfazzio/repos/half-america`
- [x] Venv recreated: `ls -la /Users/stevenfazzio/repos/half-america/.venv`
- [x] Dependencies installed: `uv run python -c "import half_america; print('OK')"`
- [x] CLI works: `uv run half-america --help`
- [x] Tests pass: `uv run pytest`

#### Manual Verification:
- [x] Confirm you're in the renamed directory

**Implementation Note**: Complete this phase before proceeding. The remaining phases assume you're working from `/Users/stevenfazzio/repos/half-america`.

---

## Phase 2: Create GitHub Repository

### Overview
Create the GitHub repository and configure it as the remote origin.

### Steps:

```bash
# Option A: Create via gh CLI (recommended)
cd /Users/stevenfazzio/repos/half-america
gh repo create half-america --public --source=. --remote=origin

# Option B: Create via GitHub web UI, then add remote
# 1. Go to github.com/new
# 2. Create repo named "half-america"
# 3. Add remote locally:
git remote add origin git@github.com:stevenfazzio/half-america.git
```

### Success Criteria:

#### Automated Verification:
- [x] Remote configured: `git remote -v` shows origin
- [x] Can push: `git push -u origin master`

#### Manual Verification:
- [x] Repository visible at `https://github.com/stevenfazzio/half-america`

---

## Phase 3: Update Documentation

### Overview
Update CLAUDE.md to clarify the naming convention for future reference.

### Changes Required:

**File**: `CLAUDE.md`
**Changes**: Add clarification about repository vs module naming

Add after the "## Project Overview" heading:

```markdown
**Naming Convention:**
- Repository/PyPI: `half-america` (hyphenated)
- Python module: `half_america` (underscored)
- CLI command: `half-america`
```

### Success Criteria:

#### Automated Verification:
- [x] CLAUDE.md contains naming clarification: `grep -q "half-america.*hyphenated" CLAUDE.md`

#### Manual Verification:
- [x] Documentation reads clearly

---

## Testing Strategy

### Automated Tests:
After Phase 1, run the full test suite to ensure nothing broke:
```bash
uv run pytest
uv run mypy src/
uv run ruff check src/ tests/
```

### Manual Testing:
- Verify CLI works: `uv run half-america --help`
- Verify imports work in Python REPL

## References

- Research document: `thoughts/shared/research/2025-11-21-repo-rename-analysis.md`
- pyproject.toml:2 - Package name definition
- pyproject.toml:41 - CLI entry point
