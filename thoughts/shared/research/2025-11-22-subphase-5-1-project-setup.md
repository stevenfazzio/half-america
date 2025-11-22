---
date: 2025-11-22T15:00:00-05:00
researcher: Claude
git_commit: db4ed48d68b42edcc5a678dde31e1d3749b266c1
branch: master
repository: stevenfazzio/half-america
topic: "Sub-Phase 5.1: Project Setup Research"
tags: [research, codebase, phase-5, web-frontend, react, vite, deck.gl, mapbox, project-setup]
status: complete
last_updated: 2025-11-22
last_updated_by: Claude
---

# Research: Sub-Phase 5.1: Project Setup

**Date**: 2025-11-22
**Researcher**: Claude
**Git Commit**: db4ed48d68b42edcc5a678dde31e1d3749b266c1
**Branch**: master
**Repository**: stevenfazzio/half-america

## Research Question

What is the current state of Sub-Phase 5.1: Project Setup, and what specific steps are needed to complete it?

## Summary

**Sub-Phase 5.1 has not been started.** The codebase is currently Python-only with no frontend implementation. All milestones are pending:

| Milestone | Status | Notes |
|-----------|--------|-------|
| Set up React + Vite application in `web/` | Not started | No `web/` directory exists |
| Configure Vite with `base: '/half-america/'` | Not started | No Vite config exists |
| Add environment configuration for `VITE_MAPBOX_ACCESS_TOKEN` | Not started | No `.env.example` for frontend |
| Configure GitHub Pages source to "GitHub Actions" | Not started | Manual step in GitHub settings |
| Create `VITE_MAPBOX_TOKEN` repository secret | Not started | Manual step in GitHub settings |

**Recommendation**: Proceed with implementation. All prerequisites from Phase 4 are complete (TopoJSON files exist in `data/output/topojson/`).

## Detailed Findings

### Current Codebase State

#### What Exists

| Component | Location | Status |
|-----------|----------|--------|
| Python backend | `src/half_america/` | Complete |
| TopoJSON output | `data/output/topojson/` | 11 files ready |
| CI workflow | `.github/workflows/ci.yml` | Python tests only |
| Pre-commit hooks | `.pre-commit-config.yaml` | Python linting only |

#### What Does NOT Exist

- `web/` directory
- `package.json` (Node.js config)
- `vite.config.ts`
- Any React/TypeScript files
- GitHub Pages deployment workflow
- Frontend environment configuration

### Sub-Phase 5.1 Milestones (Detailed)

#### 1. Set up React + Vite application in `web/` directory

**Purpose**: Create the frontend project scaffold.

**Recommended approach**:
```bash
cd /Users/stevenfazzio/repos/half-america
npm create vite@latest web -- --template react-ts
cd web
npm install
```

**Expected result**:
```
web/
├── public/
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   └── ...
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

**Dependencies to add**:
```bash
# Core mapping
npm install react-map-gl mapbox-gl @types/mapbox-gl

# deck.gl for data visualization
npm install @deck.gl/core @deck.gl/react @deck.gl/mapbox @deck.gl/layers

# TopoJSON parsing
npm install topojson-client @types/topojson-client
```

#### 2. Configure Vite with `base: '/half-america/'` for GitHub Pages

**Purpose**: Ensure assets load correctly when deployed to `stevenfazzio.github.io/half-america/`.

**File**: `web/vite.config.ts`

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/half-america/',
})
```

**Why this matters**: Without `base`, asset URLs will be absolute (e.g., `/assets/main.js`), which fails on GitHub Pages subpath hosting.

#### 3. Add environment configuration for `VITE_MAPBOX_ACCESS_TOKEN`

**Purpose**: Securely manage the Mapbox access token for development and production.

**Files to create**:

`web/.env.example`:
```
VITE_MAPBOX_ACCESS_TOKEN=pk.your_mapbox_token_here
```

`web/.gitignore` (append):
```
.env
.env.local
```

**Usage in code**:
```typescript
// src/App.tsx
const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN;
```

**Note**: Vite requires the `VITE_` prefix for environment variables to be exposed to client code.

#### 4. Configure GitHub Pages source to "GitHub Actions"

**Purpose**: Enable deployment via GitHub Actions instead of branch-based deployment.

**Steps** (manual in GitHub UI):
1. Go to repository Settings > Pages
2. Under "Build and deployment" > "Source", select "GitHub Actions"
3. This enables the `actions/deploy-pages` action

**Why not branch-based**: The `web/` subdirectory structure and build step require a workflow, not direct branch deployment.

#### 5. Create `VITE_MAPBOX_TOKEN` repository secret

**Purpose**: Securely pass the Mapbox token to GitHub Actions during build.

**Steps** (manual in GitHub UI):
1. Go to repository Settings > Secrets and variables > Actions
2. Click "New repository secret"
3. Name: `VITE_MAPBOX_TOKEN`
4. Value: Your Mapbox access token (starts with `pk.`)

**Usage in workflow** (Sub-Phase 5.3):
```yaml
- run: npm run build
  working-directory: web
  env:
    VITE_MAPBOX_ACCESS_TOKEN: ${{ secrets.VITE_MAPBOX_TOKEN }}
```

### Integration Pattern: deck.gl + Mapbox

Per the deck.gl feasibility research, the recommended pattern uses `MapboxOverlay` in interleaved mode:

```tsx
import React from 'react';
import {Map, useControl} from 'react-map-gl/mapbox';
import {MapboxOverlay} from '@deck.gl/mapbox';
import {GeoJsonLayer} from '@deck.gl/layers';
import 'mapbox-gl/dist/mapbox-gl.css';

function DeckGLOverlay(props) {
  const overlay = useControl(() => new MapboxOverlay(props));
  overlay.setProps(props);
  return null;
}

function App() {
  const layers = [
    new GeoJsonLayer({
      id: 'census-tracts',
      data: geojsonData,
      getFillColor: [255, 100, 100, 180],
      beforeId: 'waterway-label'  // Render under Mapbox labels
    })
  ];

  return (
    <Map
      initialViewState={{longitude: -98, latitude: 39, zoom: 4}}
      mapStyle="mapbox://styles/mapbox/light-v11"
      mapboxAccessToken={import.meta.env.VITE_MAPBOX_ACCESS_TOKEN}
    >
      <DeckGLOverlay layers={layers} interleaved />
    </Map>
  );
}
```

### Data Strategy

**Recommendation**: Copy TopoJSON files into `web/public/data/` for deployment.

```
web/public/data/
├── lambda_0.0.json
├── lambda_0.1.json
├── ...
└── lambda_0.9.json
```

**Rationale** (from GitHub Pages research):
- Files are small (~350 KB each, ~3.5 MB total)
- No build-time generation needed
- Simplifies deployment (pure static files)
- No CORS issues (same-origin)

### Project Structure (Target)

```
half-america/
├── src/                        # Python package (existing)
├── web/                        # NEW: Frontend application
│   ├── public/
│   │   └── data/               # Pre-computed TopoJSON files
│   │       ├── lambda_0.0.json
│   │       ├── lambda_0.1.json
│   │       └── ...
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── Map.tsx         # Sub-Phase 5.2
│   │   │   └── LambdaSlider.tsx  # Sub-Phase 5.2
│   │   └── main.tsx
│   ├── .env.example
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── .github/
│   └── workflows/
│       ├── ci.yml              # Existing Python CI
│       └── deploy.yml          # NEW: Sub-Phase 5.3
└── ...
```

## Implementation Checklist

```markdown
### Sub-Phase 5.1: Project Setup

- [ ] Create `web/` directory with React + Vite scaffold
  - [ ] Run `npm create vite@latest web -- --template react-ts`
  - [ ] Install dependencies: react-map-gl, mapbox-gl, @deck.gl/*, topojson-client

- [ ] Configure Vite
  - [ ] Set `base: '/half-america/'` in vite.config.ts

- [ ] Set up environment configuration
  - [ ] Create `web/.env.example` with VITE_MAPBOX_ACCESS_TOKEN placeholder
  - [ ] Add .env to .gitignore
  - [ ] Document token setup in README or CLAUDE.md

- [ ] Configure GitHub (manual steps)
  - [ ] Settings > Pages > Source: "GitHub Actions"
  - [ ] Settings > Secrets > New: VITE_MAPBOX_TOKEN

- [ ] Copy TopoJSON data
  - [ ] Create `web/public/data/` directory
  - [ ] Copy lambda_*.json files from data/output/topojson/
```

## Dependencies Summary

| Package | Version | Purpose |
|---------|---------|---------|
| react | ^18 | UI framework |
| react-dom | ^18 | React DOM renderer |
| vite | ^5 | Build tool |
| @vitejs/plugin-react | ^4 | Vite React plugin |
| typescript | ^5 | Type checking |
| react-map-gl | ^7 | Mapbox React wrapper |
| mapbox-gl | ^3 | Mapbox GL JS |
| @deck.gl/core | ^9 | deck.gl core |
| @deck.gl/react | ^9 | deck.gl React bindings |
| @deck.gl/mapbox | ^9 | deck.gl Mapbox integration |
| @deck.gl/layers | ^9 | deck.gl layer types |
| topojson-client | ^3 | TopoJSON → GeoJSON conversion |

## Code References

- [`ROADMAP.md:114-121`](https://github.com/stevenfazzio/half-america/blob/db4ed48d68b42edcc5a678dde31e1d3749b266c1/ROADMAP.md#L114-L121) - Sub-Phase 5.1 milestones
- [`data/output/topojson/`](https://github.com/stevenfazzio/half-america/tree/db4ed48d68b42edcc5a678dde31e1d3749b266c1/data/output/topojson) - Pre-computed TopoJSON files
- [`.github/workflows/ci.yml`](https://github.com/stevenfazzio/half-america/blob/db4ed48d68b42edcc5a678dde31e1d3749b266c1/.github/workflows/ci.yml) - Existing CI workflow

## Historical Context (from thoughts/)

- [`thoughts/shared/research/2025-11-22-deck-gl-feasibility.md`](thoughts/shared/research/2025-11-22-deck-gl-feasibility.md) - Confirms deck.gl + Mapbox integration pattern
- [`thoughts/shared/research/2025-11-22-github-pages-hosting.md`](thoughts/shared/research/2025-11-22-github-pages-hosting.md) - Confirms GitHub Pages feasibility, provides deployment workflow template
- [`thoughts/shared/research/2025-11-22-phase5-web-frontend-review.md`](thoughts/shared/research/2025-11-22-phase5-web-frontend-review.md) - Recommends sub-phase structure (already implemented in ROADMAP.md)

## Related Research

- [thoughts/shared/research/2025-11-22-deck-gl-feasibility.md](thoughts/shared/research/2025-11-22-deck-gl-feasibility.md)
- [thoughts/shared/research/2025-11-22-github-pages-hosting.md](thoughts/shared/research/2025-11-22-github-pages-hosting.md)
- [thoughts/shared/research/2025-11-22-phase5-web-frontend-review.md](thoughts/shared/research/2025-11-22-phase5-web-frontend-review.md)

## Open Questions

1. **Mapbox style**: Which style (light-v11, dark-v10, streets-v12) best showcases the population regions? Needs visual testing.
2. **TypeScript strictness**: Should we use strict mode from the start, or relax for faster iteration?
3. **Monorepo tooling**: Should we add workspace configuration for shared types between Python and TypeScript?

## Sources

- [Vite Static Deploy Guide](https://vite.dev/guide/static-deploy)
- [deck.gl Using with Mapbox](https://deck.gl/docs/developer-guide/base-maps/using-with-mapbox)
- [react-map-gl Documentation](https://visgl.github.io/react-map-gl/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Mapbox GL JS Documentation](https://docs.mapbox.com/mapbox-gl-js/)
