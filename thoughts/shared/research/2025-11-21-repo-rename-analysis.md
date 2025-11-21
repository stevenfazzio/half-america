---
date: 2025-11-21T12:00:00-08:00
researcher: Claude
git_commit: 84af3490b8c50c4abb79e4a57230e3de0962fb93
branch: master
repository: half_america
topic: "Repository Rename Analysis: half_america → half-america"
tags: [research, codebase, naming-conventions, repository-management]
status: complete
last_updated: 2025-11-21
last_updated_by: Claude
---

# Research: Repository Rename Analysis

**Date**: 2025-11-21T12:00:00-08:00
**Researcher**: Claude
**Git Commit**: 84af3490b8c50c4abb79e4a57230e3de0962fb93
**Branch**: master
**Repository**: half_america

## Research Question

Should the repository be renamed from `half_america` to `half-america`, while keeping the Python package as `half_america`? What would need to be updated?

## Summary

**Recommendation: Yes, renaming is advisable** and follows Python/GitHub conventions.

The rename would be low-impact because:
1. **pyproject.toml already uses `half-america`** as the distribution/PyPI name
2. **Python imports use `half_america`** (module name) - unchanged
3. **CLI command is `half-america`** - already hyphenated
4. **No GitHub URLs exist in the codebase** - no links to update
5. **No CI/CD configuration exists** - no workflows to modify

This follows the Python convention where:
- **Distribution name** (PyPI, repo): uses hyphens (`half-america`)
- **Importable module**: uses underscores (`half_america`)

## Detailed Findings

### Current Naming State

| Context | Current Value | After Rename |
|---------|---------------|--------------|
| Repository directory | `half_america` | `half-america` |
| GitHub repo name | `half_america` | `half-america` |
| PyPI package name | `half-america` | `half-america` (unchanged) |
| Python module | `half_america` | `half_america` (unchanged) |
| CLI command | `half-america` | `half-america` (unchanged) |

### Files Requiring Updates

#### 1. No Code Changes Needed

All Python imports use the module name `half_america`:
```python
from half_america.data.pipeline import load_all_tracts
from half_america.optimization import find_optimal_mu
```

These are **unaffected** by a repository rename. Found in:
- 25 source files under `src/half_america/`
- 14 test files under `tests/`

#### 2. pyproject.toml - No Changes Needed

Already configured correctly:
```toml
[project]
name = "half-america"  # PyPI name (hyphenated) ✓

[project.scripts]
half-america = "half_america:main"  # CLI uses hyphen, module uses underscore ✓
```

#### 3. CLAUDE.md - Minor Update Recommended

Update the project overview section:
```markdown
# Current
...when working with code in this repository.

# After (optional clarification)
Repository: `half-america`
Package: `half_america`
```

#### 4. Documentation References (Optional)

The following have `repository: half_america` in YAML frontmatter (17 files):
- `thoughts/shared/research/*.md` - All research documents

These are **historical references** and don't need updating, but you may choose to update new documents going forward.

#### 5. No CI/CD Files to Update

No GitHub Actions, Travis CI, or other CI/CD configuration exists.

#### 6. No External URLs to Update

No `github.com` URLs exist in the codebase.

### Git Operations Required

```bash
# 1. Rename local directory
cd /Users/stevenfazzio/repos
mv half_america half-america
cd half-america

# 2. Rename on GitHub (via web UI or gh CLI)
gh repo rename half-america

# 3. Update local git remote (if URL changes)
git remote set-url origin git@github.com:YOUR_USERNAME/half-america.git
```

### Potential Impacts

| Area | Impact | Notes |
|------|--------|-------|
| Local imports | None | Module name `half_america` unchanged |
| Installed package | None | `pip install half-america` unchanged |
| CLI usage | None | `half-america` command unchanged |
| Git history | Preserved | Rename doesn't affect history |
| Existing clones | URL update | Others need to update remote URL |
| PyPI | None | Package name already hyphenated |

## Code References

- `pyproject.toml:2` - Package name definition (`half-america`)
- `pyproject.toml:41` - CLI entry point (`half-america = "half_america:main"`)
- `src/half_america/__init__.py:6` - Example import usage
- `CLAUDE.md:20` - CLI command documentation

## Architecture Insights

This repository follows Python best practices for naming:

1. **PEP 8 / PEP 503**: Package names should use lowercase with underscores for modules, but hyphens are preferred for distribution names on PyPI.

2. **GitHub convention**: Hyphenated names are standard for repository URLs (easier to type, more URL-friendly).

3. **The split naming is intentional**: Many popular Python packages do this (e.g., `scikit-learn` package → `sklearn` module).

## Checklist for Rename

- [ ] Rename GitHub repository (via Settings or `gh repo rename`)
- [ ] Rename local directory
- [ ] Update git remote URL
- [ ] (Optional) Update CLAUDE.md to clarify naming
- [ ] Notify any collaborators to update their remote URLs

## Open Questions

None - the rename is straightforward with minimal impact.
