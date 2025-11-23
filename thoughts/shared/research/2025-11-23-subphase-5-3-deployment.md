---
date: 2025-11-23T10:00:00-05:00
researcher: Claude
git_commit: 43cef6be4d89dabe606a3e43dccf541d0d126b9a
branch: master
repository: half-america
topic: "Sub-Phase 5.3: Deployment Research"
tags: [research, deployment, github-pages, github-actions, phase-5, ci-cd]
status: complete
last_updated: 2025-11-23
last_updated_by: Claude
---

# Research: Sub-Phase 5.3 Deployment

**Date**: 2025-11-23
**Researcher**: Claude
**Git Commit**: 43cef6be4d89dabe606a3e43dccf541d0d126b9a
**Branch**: master
**Repository**: half-america

## Research Question

What is required to complete Sub-Phase 5.3: Deployment? What are the specific tasks, configuration requirements, and best practices for deploying the Half of America web app to GitHub Pages?

## Summary

Sub-Phase 5.3 has **two tasks** per ROADMAP.md:

1. **Set up GitHub Actions workflow** (`working-directory: ./web`)
2. **Deploy to GitHub Pages** (`stevenfazzio.github.io/half-america`)

The project is **well-positioned for deployment**:
- Vite already configured with `base: '/half-america/'`
- TopoJSON data files already in `web/public/data/`
- Existing CI workflow (`ci.yml`) provides a template pattern
- Manual setup steps documented in `web/GITHUB_SETUP.md`

**Implementation requires**: Creating a new `deploy.yml` workflow and configuring GitHub Pages source to "GitHub Actions" in repository settings.

## Detailed Findings

### Current Project State

| Component | Status | Location |
|-----------|--------|----------|
| Vite base path | ✅ Configured | `web/vite.config.ts:7` |
| TopoJSON files | ✅ Generated | `web/public/data/` (11 files, ~3.5 MB) |
| Python CI | ✅ Working | `.github/workflows/ci.yml` |
| Deployment workflow | ❌ Not created | `.github/workflows/deploy.yml` |
| GitHub Pages source | ❌ Not configured | Repository Settings > Pages |

### Task 1: GitHub Actions Workflow

#### Recommended Workflow: `.github/workflows/deploy.yml`

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [master]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
          cache-dependency-path: web/package-lock.json

      - name: Install dependencies
        run: npm ci
        working-directory: ./web

      - name: Build
        run: npm run build
        working-directory: ./web

      - name: Setup Pages
        uses: actions/configure-pages@v5

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: ./web/dist

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

#### Key Configuration Details

| Setting | Value | Reason |
|---------|-------|--------|
| `branches: [master]` | master | Project uses `master` not `main` |
| `node-version: 22` | Node 22 LTS | Current active LTS (until April 2027) |
| `cache-dependency-path` | `web/package-lock.json` | Required for monorepo caching |
| `working-directory` | `./web` | Frontend in subdirectory |
| `path: ./web/dist` | Vite output | Default Vite build output directory |

#### Action Versions (Current as of Nov 2025)

| Action | Version | Notes |
|--------|---------|-------|
| `actions/checkout` | v4 | Standard |
| `actions/setup-node` | v4 | Use v4, not v6 (runner compatibility) |
| `actions/configure-pages` | v5 | Latest stable |
| `actions/upload-pages-artifact` | v3 | Latest stable |
| `actions/deploy-pages` | v4 | Latest stable |

### Task 2: GitHub Pages Configuration

**Manual step** (documented in `web/GITHUB_SETUP.md`):

1. Go to repository **Settings** > **Pages**
2. Under "Build and deployment" > "Source", select **GitHub Actions**
3. Save changes

This one-time configuration enables deployment via GitHub Actions instead of the legacy branch-based approach.

### Existing Configuration (Already Complete)

#### Vite Configuration (`web/vite.config.ts`)

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: '/half-america/',
})
```

The `base: '/half-america/'` setting is **already correct** for GitHub Pages project deployment.

#### Build Scripts (`web/package.json`)

```json
"scripts": {
  "dev": "vite",
  "build": "tsc -b && vite build",
  "lint": "eslint .",
  "preview": "vite preview"
}
```

The `npm run build` command runs TypeScript compilation then Vite build, producing output in `web/dist/`.

### Common Pitfalls to Avoid

1. **Branch name**: Use `master` not `main` (this repo uses master)
2. **Cache path**: Must specify `cache-dependency-path: web/package-lock.json` for subdirectory
3. **working-directory**: Only works with `run` commands, not `uses` actions
4. **SPA routing**: Not needed for this project (single-page map with no client-side routing)
5. **Action versions**: Use stable v4/v5 versions, avoid v6 for setup-node

### Dependencies

The deployment has **no external dependencies**:
- No API keys required (MapLibre + CARTO basemaps are free)
- No environment secrets needed
- No external services to configure

## Code References

- `ROADMAP.md:131-135` - Sub-Phase 5.3 milestones
- `.github/workflows/ci.yml` - Existing Python CI workflow (pattern reference)
- `web/vite.config.ts:7` - Base path configuration (`base: '/half-america/'`)
- `web/package.json:7-10` - Build scripts
- `web/GITHUB_SETUP.md` - Manual setup instructions
- `web/public/data/` - TopoJSON files (11 files)

## Historical Context (from thoughts/)

### Prior Research Documents

| Document | Key Insight |
|----------|-------------|
| `thoughts/shared/research/2025-11-22-github-pages-hosting.md` | GitHub Pages feasibility analysis - recommended for this project |
| `thoughts/shared/research/2025-11-22-phase5-web-frontend-review.md` | Phase 5 milestone review including deployment |
| `thoughts/shared/research/2025-11-22-subphase-5-1-project-setup.md` | Project setup decisions including Vite configuration |

### Key Decisions (Already Made)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Hosting platform | GitHub Pages | Free, simple, perfect for static sites |
| Data strategy | Commit TopoJSON to repo | Small files (~3.5 MB total) |
| SPA routing | Not needed | Single-page map view |
| Custom domain | Use github.io initially | Simplicity |
| Fallback host | Cloudflare Pages | If traffic exceeds GitHub limits |

## Implementation Checklist

### Workflow Creation
- [ ] Create `.github/workflows/deploy.yml` with content above
- [ ] Verify workflow triggers on push to master
- [ ] Confirm build succeeds in Actions

### Repository Settings
- [ ] Navigate to Settings > Pages
- [ ] Set Source to "GitHub Actions"
- [ ] Verify deployment succeeds

### Verification
- [ ] Access `stevenfazzio.github.io/half-america`
- [ ] Confirm map loads correctly
- [ ] Test lambda slider functionality
- [ ] Verify all TopoJSON files accessible

## Architecture Insights

The deployment architecture follows the "static site as artifact" pattern:

```
Push to master
    │
    ▼
┌─────────────────┐
│  Build Job      │
│  - npm ci       │
│  - npm run build│
│  - Upload dist/ │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Deploy Job     │
│  - Deploy Pages │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GitHub Pages   │
│  CDN serving    │
│  static files   │
└─────────────────┘
```

This is the recommended approach for Vite applications as it:
- Separates build from deployment
- Supports concurrency controls
- Uses GitHub's Pages artifact system for reliability

## Related Research

- [thoughts/shared/research/2025-11-22-github-pages-hosting.md](thoughts/shared/research/2025-11-22-github-pages-hosting.md) - Hosting feasibility
- [thoughts/shared/research/2025-11-22-deck-gl-feasibility.md](thoughts/shared/research/2025-11-22-deck-gl-feasibility.md) - Visualization technology

## Open Questions

None - Sub-Phase 5.3 is well-defined and ready for implementation.

## Sources

- [Deploying a Static Site | Vite](https://vite.dev/guide/static-deploy) - Official Vite deployment guide
- [Using custom workflows with GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages) - GitHub documentation
- [actions/deploy-pages](https://github.com/actions/deploy-pages) - Official GitHub Pages action
