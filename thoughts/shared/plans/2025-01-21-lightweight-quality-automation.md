# Lightweight Quality Automation Implementation Plan

## Overview

Add automated quality checks to the project: replace black with ruff format, add pre-commit hooks, and set up GitHub Actions CI. This follows the recommendations from the research document with no additional scope.

## Current State Analysis

### Codebase Metrics
- Source: 19 Python files (~1,735 LOC) in `src/half_america/`
- Tests: 22 Python files (~2,051 LOC) in `tests/`

### Existing Tooling
- `black>=25.11.0` - formatting (to be removed)
- `ruff>=0.14.5` - linting only (to add formatting)
- `mypy>=1.18.2` - type checking
- `pytest>=9.0.1` - testing

### Key Discoveries
- No `[tool.ruff]` config exists in `pyproject.toml:58-65`
- No `.pre-commit-config.yaml` exists
- No `.github/workflows/` directory exists
- `black` referenced in: `CLAUDE.md:22`, `README.md:65`, `pyproject.toml:49`

## Desired End State

After implementation:
1. `ruff format` handles all formatting (black removed)
2. Pre-commit hooks run ruff lint+format on every commit
3. GitHub Actions CI runs lint, format check, mypy, and pytest on push/PR to master
4. Documentation updated to reflect new commands

### Verification
- `uv run ruff format --check src/ tests/` passes
- `uv run ruff check src/ tests/` passes
- `uv run pre-commit run --all-files` passes
- GitHub Actions workflow runs successfully

## What We're NOT Doing

- No Makefile or justfile (uv is sufficient)
- No coverage thresholds
- No branch protection rules
- No Dependabot
- No multi-Python CI matrix
- No pre-push hooks

## Implementation Approach

Sequential phases to ensure each change is validated before proceeding. Changes are minimal and focused.

---

## Phase 1: Replace black with ruff format

### Overview
Remove black from dependencies, add ruff configuration for both linting and formatting.

### Changes Required:

#### 1. pyproject.toml
**File**: `pyproject.toml`
**Changes**: Remove black, add ruff config

Remove from dev dependencies:
```toml
# Remove this line:
    "black>=25.11.0",
```

Add at end of file (after `[tool.pytest.ini_options]`):
```toml
[tool.ruff]
line-length = 88

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # Pyflakes
    "I",   # isort (import sorting)
    "UP",  # pyupgrade
    "W",   # pycodestyle warnings
]
```

### Success Criteria:

#### Automated Verification:
- [x] `uv sync` completes without errors
- [x] `uv run ruff check src/ tests/` passes
- [x] `uv run ruff format --check src/ tests/` passes (or run `ruff format` first to fix)
- [x] `uv run mypy src/` passes
- [x] `uv run pytest` passes

#### Manual Verification:
- [x] Confirm black is no longer in `uv.lock`

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation before proceeding to Phase 2.

---

## Phase 2: Add pre-commit hooks

### Overview
Install pre-commit and configure hooks for ruff lint/format and basic file hygiene.

### Changes Required:

#### 1. Add pre-commit to dev dependencies
**File**: `pyproject.toml`
**Changes**: Add pre-commit to dev group

```toml
[dependency-groups]
dev = [
    "mypy>=1.18.2",
    "pandas-stubs>=2.0",
    "pre-commit>=4.2.0",  # Add this line
    "pytest>=9.0.1",
    "pytest-benchmark>=4.0",
    "pytest-cov>=4.0",
    "ruff>=0.14.5",
]
```

#### 2. Create .pre-commit-config.yaml
**File**: `.pre-commit-config.yaml` (new file)
**Changes**: Create with ruff and basic hooks

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.14.6
    hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
```

### Success Criteria:

#### Automated Verification:
- [x] `uv sync` completes without errors
- [x] `uv run pre-commit install` succeeds
- [x] `uv run pre-commit run --all-files` passes

#### Manual Verification:
- [ ] Create a test commit to verify hooks run

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation before proceeding to Phase 3.

---

## Phase 3: Add GitHub Actions CI

### Overview
Create a single-job CI workflow that runs lint, format check, mypy, and tests.

### Changes Required:

#### 1. Create workflow directory and file
**File**: `.github/workflows/ci.yml` (new file, create directory)
**Changes**: Create CI workflow

```yaml
name: CI

on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v6
        with:
          enable-cache: true
          cache-dependency-glob: "uv.lock"

      - name: Set up Python
        run: uv python install 3.11

      - name: Install dependencies
        run: uv sync --locked --dev

      - name: Lint with ruff
        run: uv run ruff check --output-format=github src/ tests/

      - name: Check formatting
        run: uv run ruff format --check src/ tests/

      - name: Type check with mypy
        run: uv run mypy src/

      - name: Run tests
        run: uv run pytest tests/ -v
```

### Success Criteria:

#### Automated Verification:
- [ ] File created at `.github/workflows/ci.yml`
- [ ] YAML syntax is valid: `uv run pre-commit run check-yaml --files .github/workflows/ci.yml`

#### Manual Verification:
- [ ] Push to a branch and verify workflow runs in GitHub Actions
- [ ] All CI steps pass

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation before proceeding to Phase 4.

---

## Phase 4: Update documentation

### Overview
Update CLAUDE.md and README.md to reflect the new ruff-based workflow.

### Changes Required:

#### 1. Update CLAUDE.md
**File**: `CLAUDE.md`
**Changes**: Replace black command with ruff format

```bash
# Old:
uv run black src/ tests/             # Format code

# New:
uv run ruff format src/ tests/       # Format code
```

#### 2. Update README.md
**File**: `README.md`
**Changes**: Replace black command with ruff format

```bash
# Old:
uv run black src/ tests/

# New:
uv run ruff format src/ tests/
```

### Success Criteria:

#### Automated Verification:
- [ ] `grep -r "black" CLAUDE.md README.md` returns no results
- [ ] `grep "ruff format" CLAUDE.md README.md` shows both files updated

#### Manual Verification:
- [ ] Review CLAUDE.md commands section looks correct
- [ ] Review README.md usage section looks correct

---

## Testing Strategy

### Unit Tests
- No new unit tests needed (tooling only)

### Integration Tests
- Pre-commit hooks run on all files
- CI workflow executes all checks

### Manual Testing Steps
1. After Phase 1: Run `uv run ruff format src/ tests/` and verify formatting
2. After Phase 2: Make a small change and commit to verify hooks run
3. After Phase 3: Push to GitHub and verify workflow runs
4. After Phase 4: Review documentation for accuracy

## Migration Notes

- `uv.lock` will be regenerated without black
- No data migration needed
- Rollback: Revert commits, run `uv sync`

## References

- Original research: `thoughts/shared/research/2025-01-21-lightweight-quality-automation.md`
- [Astral Ruff Formatter](https://astral.sh/blog/the-ruff-formatter)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [pre-commit](https://pre-commit.com/)
- [astral-sh/setup-uv](https://github.com/astral-sh/setup-uv)
