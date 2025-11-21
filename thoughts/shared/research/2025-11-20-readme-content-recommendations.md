---
date: 2025-11-20T21:50:00-05:00
researcher: Claude
git_commit: 0174349111ed595f145129a7944b75d30a87a1b1
branch: master
repository: half_america
topic: "README.md Content Recommendations"
tags: [research, documentation, readme]
status: complete
last_updated: 2025-11-20
last_updated_by: Claude
---

# Research: README.md Content Recommendations

**Date**: 2025-11-20T21:50:00-05:00
**Researcher**: Claude
**Git Commit**: 0174349111ed595f145129a7944b75d30a87a1b1
**Branch**: master
**Repository**: half_america

## Research Question
What content should be added to the empty README.md file?

## Summary
The README.md is currently empty (0 bytes). Based on analysis of existing documentation (PROJECT_SUMMARY.md, METHODOLOGY.md, ROADMAP.md) and project structure, the README should serve as the primary entry point, providing a compelling project overview, installation instructions, usage examples, and links to detailed documentation.

## Detailed Findings

### Current Project State
- **Phase**: Initial skeleton - documentation complete, no functional code yet
- **Source Code**: Only `src/half_america/__init__.py` with a placeholder `main()` function
- **Documentation**: Comprehensive technical docs exist but README is empty
- **Tooling**: Dev environment set up with pytest, black, mypy, ruff via uv

### Existing Documentation Analysis
| File | Purpose | Key Content |
|------|---------|-------------|
| `PROJECT_SUMMARY.md` | Vision & goals | Problem statement, solution approach, scope |
| `METHODOLOGY.md` | Technical approach | Math formulation, Max-Flow Min-Cut algorithm, implementation stack |
| `ROADMAP.md` | Implementation plan | 5 phases from data pipeline to web frontend |
| `CLAUDE.md` | AI assistant guidance | Commands, architecture overview |

### Recommended README Sections

1. **Title & Badges**
   - Project name with tagline
   - Python version badge
   - License badge (if applicable)

2. **Hero Description**
   - One-paragraph elevator pitch (from PROJECT_SUMMARY.md)
   - Visual preview (placeholder for future screenshot/GIF)

3. **The Problem**
   - Brief explanation of "San Bernardino Problem" and "Dust Problem"
   - Links to the viral maps that inspired this

4. **How It Works**
   - Surface tension concept with lambda slider explanation
   - Link to METHODOLOGY.md for math details

5. **Installation**
   - Prerequisites (Python 3.11+, uv)
   - Clone and install commands

6. **Usage**
   - CLI commands from CLAUDE.md
   - Development commands (test, lint, format)

7. **Project Status**
   - Current phase indicator
   - Link to ROADMAP.md

8. **Documentation Links**
   - PROJECT_SUMMARY.md - Full project vision
   - METHODOLOGY.md - Technical details
   - ROADMAP.md - Implementation plan

9. **License & Contributing**
   - License info
   - Contribution guidelines (or note that it's experimental)

## Code References
- `README.md` - Currently empty (0 bytes)
- `PROJECT_SUMMARY.md` - Contains the "Background & Inspiration" and "The Problem" sections
- `METHODOLOGY.md` - Contains detailed algorithm description
- `ROADMAP.md` - Contains implementation phases and current status
- `pyproject.toml:1-11` - Project metadata including name, version, author
- `CLAUDE.md:9-32` - Command examples for installation and development

## Architecture Insights
The project uses a clean separation:
- User-facing README for quick onboarding
- PROJECT_SUMMARY.md for vision/context
- METHODOLOGY.md for technical depth
- ROADMAP.md for progress tracking
- CLAUDE.md for AI tool guidance

The README should bridge these by providing quick access without duplicating content.

## Recommended README Template

```markdown
# Half of America

A topology optimization experiment visualizing US population distribution with smooth, organic shapes instead of dusty dots or blocky counties.

> Where does half of America *really* live?

## The Problem

Traditional "half of America lives here" maps have two issues:
1. **The San Bernardino Problem**: County boundaries include vast empty areas
2. **The Dust Problem**: Using smaller units creates thousands of disconnected specks

This project solves both using **Max-Flow Min-Cut optimization** with a user-controlled "surface tension" parameter.

## How It Works

A slider controls lambda (λ):
- **λ ≈ 0**: Minimizes area → high-resolution "dusty" city centers
- **λ ≈ 1**: Minimizes perimeter → smooth, compact blobs

See [METHODOLOGY.md](METHODOLOGY.md) for the math.

## Installation

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

git clone <repo-url>
cd half_america
uv sync

## Usage

# Run the CLI
uv run half-america

# Run tests
uv run pytest

# Format & lint
uv run black src/ tests/
uv run ruff check src/ tests/

## Project Status

**Current Phase**: Initial skeleton (Phase 0)

See [ROADMAP.md](ROADMAP.md) for the full implementation plan.

## Documentation

- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Full project vision and scope
- [METHODOLOGY.md](METHODOLOGY.md) - Mathematical formulation and algorithm
- [ROADMAP.md](ROADMAP.md) - Implementation roadmap

## License

[Add license info]

## Disclaimer

This is a personal experimental project exploring topology optimization and cartography. Not intended as a production tool.
```

## Open Questions
1. Should a LICENSE file be added? (MIT, Apache 2.0, etc.)
RESPONSE: MIT
2. Should badges be added (Python version, tests passing, etc.)?
RESPONSE: Yes
3. Should a visual placeholder be included for the future interactive map?
RESPONSE: No, we'll just add a link to the map once we have one.
4. Should contributing guidelines be added or is this solo-developer only?
RESPONSE: No, this is solo developer
