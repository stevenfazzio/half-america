---
date: 2025-11-22T12:00:00-08:00
researcher: Claude
git_commit: 2399ccfb44118b5bf41732dfb09be6bff7abd52f
branch: master
repository: half-america
topic: "MapLibre vs Mapbox for Half of America web frontend"
tags: [research, codebase, phase-5, web-frontend, maplibre, mapbox, deck-gl]
status: complete
last_updated: 2025-11-22
last_updated_by: Claude
---

# Research: MapLibre vs Mapbox for Half of America Web Frontend

**Date**: 2025-11-22T12:00:00-08:00
**Researcher**: Claude
**Git Commit**: 2399ccfb44118b5bf41732dfb09be6bff7abd52f
**Branch**: master
**Repository**: half-america

## Research Question

Should this project switch from Mapbox GL JS to MapLibre GL JS for the web frontend? What are the pros and cons given the nature of this project (a portfolio data visualization piece)?

## Summary

**Recommendation: Switch to MapLibre GL JS.**

For a portfolio project hosted on GitHub Pages with no commercial requirements, MapLibre is the better choice. It eliminates API key management for the map library, has no billing concerns, and demonstrates awareness of open-source alternatives. The migration is trivial since no Mapbox rendering code has been implemented yet.

| Factor | Mapbox | MapLibre | Winner |
|--------|--------|----------|--------|
| License | Proprietary (v2+) | BSD-2 (open source) | MapLibre |
| Cost | Requires subscription | Free forever | MapLibre |
| API Key for Library | Required | Not required | MapLibre |
| deck.gl Support | Native | Equally supported | Tie |
| react-map-gl Support | `/mapbox` export | `/maplibre` export | Tie |
| Free Tile Sources | Mapbox-hosted only | CARTO, OpenFreeMap, etc. | MapLibre |
| Portfolio Appeal | Standard choice | Shows FOSS awareness | MapLibre |

## Detailed Findings

### Current Mapbox Integration Status

The project is in Sub-Phase 5.1 (Project Setup). Mapbox dependencies are installed but **no rendering code exists yet**:

**Installed packages** (`web/package.json`):
- `mapbox-gl@^3.16.0`
- `@deck.gl/mapbox@^9.2.2`
- `react-map-gl@^8.1.0`
- `@types/mapbox-gl@^3.4.1`

**Current usage** (`web/src/App.tsx:6`):
```typescript
const hasMapboxToken = !!import.meta.env.VITE_MAPBOX_ACCESS_TOKEN;
```

This is only a token presence check for the smoke test UI. No actual map is rendered.

### Licensing Differences

| Aspect | Mapbox GL JS | MapLibre GL JS |
|--------|--------------|----------------|
| License | Proprietary (since v2.0, Dec 2020) | BSD-2-Clause |
| Origin | Original library | Fork of Mapbox GL JS v1.13 |
| Cost | Subscription required | Free |
| API Key | Required to load library | Not required for library |

MapLibre was forked when Mapbox changed from BSD-3 to a proprietary license. The libraries have diverged since, but both remain fully functional for web mapping.

### deck.gl Integration

**Key finding**: The `@deck.gl/mapbox` module works with **both** Mapbox GL JS and MapLibre GL JS.

```typescript
// Works identically with either library
import { MapboxOverlay } from '@deck.gl/mapbox';

const overlay = new MapboxOverlay({
  interleaved: true,
  layers: [new GeoJsonLayer({ ... })]
});

map.addControl(overlay);
```

The `MapboxOverlay` class implements the standard `IControl` interface that both libraries support.

### react-map-gl Support

react-map-gl v8+ has fully separated code paths:

```typescript
// Mapbox
import Map from 'react-map-gl/mapbox';

// MapLibre
import Map from 'react-map-gl/maplibre';
```

There's also a dedicated `@vis.gl/react-maplibre` package for MapLibre-only projects (recommended for new projects).

### Free Tile Sources for MapLibre

Since MapLibre doesn't include hosted tiles, you need a tile source:

| Provider | API Key | Limits | Commercial Use |
|----------|---------|--------|----------------|
| **CARTO Basemaps** | No | None | Non-commercial |
| **OpenFreeMap** | No | None | Yes |
| **MapTiler** | Yes | 5K sessions/mo | Non-commercial (free tier) |

**Recommended for this project**: CARTO basemaps (Positron or Dark Matter styles)

```typescript
mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
```

No API key required. deck.gl's own examples use CARTO basemaps.

### Project Context

From `CLAUDE.md` and `README.md`:
- **Type**: Personal/portfolio project
- **License**: MIT
- **Goals**: Show population concentration, make it compelling, serve as portfolio piece
- **Hosting**: GitHub Pages (static site)
- **Commercial**: No

This context strongly favors MapLibre:
1. No need for Mapbox's commercial features
2. No budget for map API subscriptions
3. Portfolio benefit from showing FOSS awareness
4. Static hosting works perfectly with either library

### Migration Effort

Since no Mapbox rendering code exists yet, migration is minimal:

**Package changes**:
```diff
- "mapbox-gl": "^3.16.0",
+ "maplibre-gl": "^5.0.0",
- "@types/mapbox-gl": "^3.4.1",
```

**Import changes** (for future code):
```diff
- import Map from 'react-map-gl/mapbox';
+ import Map from 'react-map-gl/maplibre';
```

**Environment variables**:
- Remove `VITE_MAPBOX_ACCESS_TOKEN` requirement
- No token needed for MapLibre itself
- CARTO basemaps need no authentication

## Code References

- `web/package.json:12-21` - Current Mapbox dependencies
- `web/src/App.tsx:6` - Token presence check (only current usage)
- `web/.env.example:1-2` - Mapbox token configuration
- `ROADMAP.md:88-97` - Technology stack definition
- `thoughts/shared/research/2025-11-22-deck-gl-feasibility.md:85-116` - Planned deck.gl integration pattern

## Architecture Insights

The planned architecture uses deck.gl in "interleaved mode" with the base map library:

```
┌─────────────────────────────────────┐
│           React App                  │
├─────────────────────────────────────┤
│  react-map-gl/maplibre (or mapbox)  │
├─────────────────────────────────────┤
│      MapboxOverlay (deck.gl)        │
│  ┌─────────────────────────────────┐│
│  │   GeoJsonLayer (census tracts)  ││
│  └─────────────────────────────────┘│
├─────────────────────────────────────┤
│   MapLibre GL JS (or Mapbox GL JS)  │
│   + CARTO/Mapbox basemap tiles      │
└─────────────────────────────────────┘
```

This architecture works identically with either library. The `@deck.gl/mapbox` package name is historical; it supports MapLibre equally.

## Recommendation

**Switch to MapLibre GL JS** with the following stack:

```json
{
  "dependencies": {
    "maplibre-gl": "^5.0.0",
    "react-map-gl": "^8.1.0",
    "@deck.gl/core": "^9.2.2",
    "@deck.gl/react": "^9.2.2",
    "@deck.gl/mapbox": "^9.2.2",
    "@deck.gl/layers": "^9.2.2",
    "topojson-client": "^3.1.0"
  }
}
```

**Basemap**: CARTO Positron (`https://basemaps.cartocdn.com/gl/positron-gl-style/style.json`)

**Benefits**:
1. No API key management for the map library
2. No billing concerns
3. CARTO basemaps are free and high-quality
4. Shows FOSS awareness (good for portfolio)
5. No vendor lock-in
6. deck.gl works identically

**Tradeoffs**:
1. Lose access to Mapbox-specific styles (but CARTO styles are excellent)
2. Slightly less documentation (but react-map-gl docs cover both)

## Migration Steps

If approved, these changes are needed:

1. **Update `web/package.json`**:
   - Remove `mapbox-gl`, `@types/mapbox-gl`
   - Add `maplibre-gl`

2. **Update `web/src/App.tsx`**:
   - Remove Mapbox token check (or change to optional)

3. **Update environment files**:
   - Remove Mapbox token from `.env.example`
   - Update `GITHUB_SETUP.md` to remove Mapbox secret requirement

4. **Update documentation**:
   - `CLAUDE.md`, `ROADMAP.md`, `METHODOLOGY.md`
   - Plan files and research docs

5. **Update Sub-Phase 5.1 plan**:
   - Change dependencies list
   - Remove Mapbox token configuration steps

## Related Research

- `thoughts/shared/research/2025-11-22-deck-gl-feasibility.md` - deck.gl integration patterns
- `thoughts/shared/research/2025-11-22-github-pages-hosting.md` - Hosting requirements
- `thoughts/shared/plans/2025-11-22-subphase-5-1-project-setup.md` - Current implementation plan

## Open Questions

1. **Style preference**: Should we use CARTO Positron (light) or Dark Matter (dark) as the default basemap?
2. **Style customization**: Do we need custom basemap styling, or are CARTO defaults sufficient?
3. **Fallback**: Should we provide a fallback if CARTO tiles are unavailable?
