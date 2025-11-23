---
date: 2025-11-22T12:00:00-05:00
researcher: Claude
git_commit: 5fd7340269a1c9838a82eaf4ddbb41d7726e986c
branch: master
repository: half-america
topic: "Audit of mapbox references in codebase"
tags: [research, codebase, mapbox, maplibre, audit, cleanup]
status: complete
last_updated: 2025-11-22
last_updated_by: Claude
---

# Research: Audit of Mapbox References in Codebase

**Date**: 2025-11-22T12:00:00-05:00
**Researcher**: Claude
**Git Commit**: 5fd7340269a1c9838a82eaf4ddbb41d7726e986c
**Branch**: master
**Repository**: half-america

## Research Question

Where is "mapbox" (case insensitive) used in the repository? Which references should be updated, and which should be preserved?

## Summary

The MapLibre migration is **complete** in all production code. The remaining "mapbox" references fall into three categories:

1. **Should Preserve** - Correct technical references (`@deck.gl/mapbox`, `MapboxOverlay`)
2. **Should Preserve** - Transitive dependencies from MapLibre (`@mapbox/*` packages)
3. **Should Preserve** - Historical documentation in `thoughts/` directory

**No updates needed.** All mapbox references are either technically correct or intentional historical documentation.

## Detailed Findings

### Category 1: Production Code & Config (PRESERVE)

These references are **correct and should NOT be changed**:

| File | Reference | Reason to Preserve |
|------|-----------|-------------------|
| `web/package.json:15` | `@deck.gl/mapbox` | Official deck.gl package - works with BOTH Mapbox AND MapLibre |
| `ROADMAP.md:92` | `@deck.gl/mapbox` | Correct package name in tech stack |
| `ROADMAP.md:124` | `MapboxOverlay` | Correct class name from `@deck.gl/mapbox` |

**Key insight**: The `@deck.gl/mapbox` package name is historical - it supports MapLibre equally well. The `MapboxOverlay` class implements the standard `IControl` interface that both libraries support.

### Category 2: Transitive Dependencies (PRESERVE)

The `web/package-lock.json` contains multiple `@mapbox/*` packages. These are **transitive dependencies** of MapLibre GL JS (which forked from Mapbox GL JS and shares some utility packages):

- `@mapbox/geojson-rewind` - GeoJSON winding order utilities
- `@mapbox/jsonlint-lines-primitives` - JSON linting
- `@mapbox/point-geometry` - Point geometry primitives
- `@mapbox/tiny-sdf` - Signed distance field generation
- `@mapbox/unitbezier` - Bezier curve utilities
- `@mapbox/vector-tile` - Vector tile parsing
- `@mapbox/whoots-js` - WMS/TMS utilities

These are internal dependencies managed by npm - **do not manually remove**.

### Category 3: Historical Documentation (PRESERVE)

The `thoughts/` directory contains research and planning documents that reference the Mapbox → MapLibre migration. These should be preserved as historical context:

| File | Purpose |
|------|---------|
| `thoughts/shared/research/2025-11-22-maplibre-vs-mapbox.md` | Research comparing both libraries |
| `thoughts/shared/research/2025-11-22-deck-gl-feasibility.md` | deck.gl integration research |
| `thoughts/shared/plans/2025-11-22-subphase-5-1-project-setup.md` | Original plan (documents migration) |
| Various other research docs | Historical context |

### Verification: Source Code is Clean

The `web/src/` directory has **zero** mapbox references:

```bash
grep -ri mapbox web/src/
# (no output)
```

The production source code correctly uses MapLibre only.

## Code References

- `web/package.json:15-17` - Dependencies showing MapLibre + deck.gl/mapbox
- `ROADMAP.md:91-92` - Tech stack listing
- `ROADMAP.md:124` - MapboxOverlay milestone

## Architecture Insights

The project correctly implements the recommended architecture:

```
react-map-gl/maplibre (wrapper)
       ↓
MapboxOverlay (@deck.gl/mapbox)
       ↓
MapLibre GL JS (basemap rendering)
```

This architecture uses:
- **MapLibre GL JS** for basemap rendering (no API key needed)
- **@deck.gl/mapbox** for data visualization layer (package name is historical, works with MapLibre)
- **react-map-gl/maplibre** as the React wrapper

## Recommendations

| Action | Target | Verdict |
|--------|--------|---------|
| Update | `@deck.gl/mapbox` references | **NO** - Correct package name |
| Update | `MapboxOverlay` references | **NO** - Correct class name |
| Remove | `@mapbox/*` from package-lock.json | **NO** - Required transitive deps |
| Update | thoughts/ documentation | **NO** - Preserve as history |

**Conclusion**: No changes needed. The codebase correctly distinguishes between:
1. The map library (MapLibre - no API key)
2. The deck.gl integration package (named "mapbox" but works with MapLibre)
3. Historical documentation of the migration decision

## Open Questions

None - the audit is complete and no ambiguities were found.
