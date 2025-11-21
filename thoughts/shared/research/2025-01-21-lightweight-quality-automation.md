---
date: 2025-01-21T00:00:00-05:00
researcher: Claude
git_commit: c036c6ec0e73359b9301753a022053cf03f4f7a9
branch: master
repository: half-america
topic: "Lightweight automated quality checks for Python projects"
tags: [research, automation, pre-commit, ci, ruff, github-actions]
status: complete
last_updated: 2025-01-21
last_updated_by: Claude
---

# Research: Lightweight Automated Quality Checks

**Date**: 2025-01-21
**Researcher**: Claude
**Git Commit**: c036c6ec0e73359b9301753a022053cf03f4f7a9
**Branch**: master
**Repository**: half-america

## Research Question

What are the "no-brainer" automated quality checks for a lightweight Python project that already has tooling (uv, pytest, black, ruff, mypy) but no automation infrastructure (pre-commit, CI, Makefile)?

## Summary

For this small-to-medium project (~1,735 LOC source, ~2,051 LOC tests), three additions would provide significant value with minimal complexity:

1. **Replace black with ruff format** - Ruff now handles both linting AND formatting (30x faster than black, 99.9% compatible)
2. **Add pre-commit hooks** - Minimal 5-hook config using ruff (runs in milliseconds)
3. **Add GitHub Actions CI** - Single-job workflow running lint, format check, mypy, and pytest

Skip task runners (Makefile/justfile) - `uv run` is sufficient for this project size.

## Current State

### Codebase Metrics
- **Source files**: 19 Python files in `src/half_america/`
- **Test files**: 22 Python files in `tests/`
- **Source LOC**: ~1,735 lines
- **Test LOC**: ~2,051 lines (1.18:1 test-to-source ratio)
- **Structure**: 4 logical packages (data, graph, optimization, cli)

### Existing Tooling (in dev dependencies)
- `black>=25.11.0` - formatting
- `ruff>=0.14.5` - linting
- `mypy>=1.18.2` - type checking
- `pytest>=9.0.1` - testing (with pytest-cov, pytest-benchmark)

### Missing Automation
- No `.pre-commit-config.yaml`
- No `.github/workflows/`
- No `Makefile` or `justfile`
- No `tox.ini`

## Recommendations

### 1. Replace black with ruff format (NO-BRAINER)

Ruff now handles both linting AND formatting. It's:
- **30x faster** than black
- **99.9% black-compatible** (tested on Django, Zulip)
- One less dependency to maintain

**Changes to `pyproject.toml`**:

```toml
[dependency-groups]
dev = [
    # Remove: "black>=25.11.0",
    "mypy>=1.18.2",
    "pandas-stubs>=2.0",
    "pytest>=9.0.1",
    "pytest-benchmark>=4.0",
    "pytest-cov>=4.0",
    "ruff>=0.14.5",
]

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

**New commands**:
```bash
uv run ruff check src/ tests/       # Lint
uv run ruff check --fix src/ tests/ # Lint + auto-fix
uv run ruff format src/ tests/      # Format (replaces black)
```

### 2. Add pre-commit hooks (NO-BRAINER)

Pre-commit is still the standard for Python projects. With ruff, hooks run in milliseconds.

**Create `.pre-commit-config.yaml`**:

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

**Setup**:
```bash
uv add --dev pre-commit
uv run pre-commit install
```

**Note**: Mypy is deliberately excluded from pre-commit (too slow). Run it in CI instead.

### 3. Add GitHub Actions CI (NO-BRAINER)

A minimal single-job workflow provides safety net without complexity.

**Create `.github/workflows/ci.yml`**:

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

**Key features**:
- Single job (simpler, often faster for small projects)
- `--output-format=github` gives inline PR annotations
- `enable-cache: true` caches uv dependencies
- `--locked` ensures exact versions from `uv.lock`

### 4. Skip task runners (RECOMMENDATION)

For a project this size, Makefile or justfile adds complexity without benefit:
- uv is already 10-100x faster than pip
- Commands are simple enough (`uv run pytest`, `uv run ruff check`)
- A README checklist is sufficient

If you want shortcuts, use shell aliases or just document in README.

## Decision Matrix

| Option | Value | Complexity | Verdict |
|--------|-------|------------|---------|
| Ruff format (replace black) | High | Very Low | DO IT |
| Pre-commit (ruff hooks) | High | Low | DO IT |
| GitHub Actions CI | High | Low | DO IT |
| Makefile/justfile | Low | Medium | SKIP |
| Pre-push hooks | Medium | Medium | OPTIONAL |
| Multi-Python CI matrix | Low | Medium | SKIP (only need 3.11+) |
| Coverage thresholds | Low | Low | OPTIONAL |

## Implementation Plan

1. **Remove black, add ruff config** to `pyproject.toml`
2. **Add `pre-commit`** to dev dependencies
3. **Create `.pre-commit-config.yaml`** with ruff hooks
4. **Create `.github/workflows/ci.yml`**
5. **Update `CLAUDE.md`** commands section
6. **Run `uv sync` and `uv run pre-commit install`**

Total estimated files to create/modify: 4-5

## Open Questions

1. **Coverage thresholds**: Add `--cov-fail-under=80` to CI? Currently no enforcement.
RESPONSE: Skip for now
2. **Branch protection**: Enable "Require status checks to pass" on master?
RESPONSE: Skip for now
3. **Dependabot**: Add for dependency updates? (probably overkill for this project)
RESPONSE: Skip for now

## References

- [Astral Ruff Formatter](https://astral.sh/blog/the-ruff-formatter)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [pre-commit](https://pre-commit.com/)
- [ruff-pre-commit](https://github.com/astral-sh/ruff-pre-commit)
- [uv GitHub Integration](https://docs.astral.sh/uv/guides/integration/github/)
- [astral-sh/setup-uv](https://github.com/astral-sh/setup-uv)
