# Sub-Phase 5.3: Deployment Implementation Plan

## Overview

Deploy the Half of America web application to GitHub Pages using GitHub Actions. This enables automatic deployment on every push to master, making the visualization publicly accessible at `stevenfazzio.github.io/half-america`.

## Current State Analysis

| Component | Status | Location |
|-----------|--------|----------|
| Vite base path | Configured | `web/vite.config.ts:7` |
| TopoJSON files | Generated | `web/public/data/` (11 files) |
| Python CI | Working | `.github/workflows/ci.yml` |
| Deployment workflow | Not created | `.github/workflows/deploy.yml` |
| GitHub Pages source | Not configured | Repository Settings > Pages |

### Key Discoveries:
- Vite already configured with `base: '/half-america/'` for correct asset paths
- Build command `npm run build` produces output in `web/dist/`
- No API keys or secrets required (MapLibre + CARTO basemaps are free)
- Existing CI workflow uses `actions/checkout@v4` pattern we can follow

## Desired End State

After implementation:
1. Every push to `master` automatically builds and deploys the web app
2. Site accessible at `https://stevenfazzio.github.io/half-america`
3. Map loads correctly with all lambda values (0.0-0.9) functional
4. Manual deployments possible via workflow_dispatch trigger

## What We're NOT Doing

- Custom domain configuration (using github.io initially)
- SPA routing/404 handling (single-page map, not needed)
- Environment secrets or API key management
- Cloudflare Pages fallback setup (deferred unless needed)

## Implementation Approach

Create a two-job GitHub Actions workflow: build job compiles the Vite app, deploy job publishes to GitHub Pages. This follows GitHub's recommended "static site as artifact" pattern for reliability and concurrency control.

---

## Phase 1: Create Deployment Workflow

### Overview
Create the GitHub Actions workflow file that builds and deploys the web frontend.

### Changes Required:

#### 1. Create `.github/workflows/deploy.yml`

**File**: `.github/workflows/deploy.yml`
**Action**: Create new file

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

### Configuration Details

| Setting | Value | Reason |
|---------|-------|--------|
| `branches: [master]` | master | Project uses `master` not `main` |
| `node-version: 22` | Node 22 LTS | Current active LTS (until April 2027) |
| `cache-dependency-path` | `web/package-lock.json` | Required for monorepo caching |
| `working-directory` | `./web` | Frontend in subdirectory |
| `path: ./web/dist` | Vite output | Default Vite build output directory |

### Success Criteria:

#### Automated Verification:
- [ ] File exists at `.github/workflows/deploy.yml`
- [ ] YAML syntax is valid: `python -c "import yaml; yaml.safe_load(open('.github/workflows/deploy.yml'))"`
- [ ] Workflow appears in GitHub Actions UI after push

#### Manual Verification:
- [ ] None required for this phase

**Implementation Note**: After creating this file, commit and push to trigger the workflow. The workflow will fail until Phase 2 is complete (GitHub Pages source configuration).

---

## Phase 2: Configure GitHub Pages Source

### Overview
Configure GitHub repository settings to accept deployments from GitHub Actions.

### Changes Required:

#### 1. Manual GitHub Configuration

**Location**: Repository Settings > Pages
**Action**: Configure deployment source

**Steps**:
1. Navigate to `https://github.com/stevenfazzio/half-america/settings/pages`
2. Under "Build and deployment" > "Source", select **GitHub Actions**
3. Click Save

This is a one-time manual configuration that cannot be automated via workflow.

### Success Criteria:

#### Automated Verification:
- [ ] None (repository settings cannot be verified via CLI)

#### Manual Verification:
- [ ] GitHub Pages source shows "GitHub Actions" in repository settings
- [ ] Deployment workflow runs successfully (check Actions tab)
- [ ] Deployment job shows green checkmark

**Implementation Note**: After completing this configuration, the workflow from Phase 1 should deploy successfully. If it failed previously, re-run it via the Actions UI.

---

## Phase 3: Verify Deployment

### Overview
Confirm the deployed site functions correctly.

### Verification Steps:

#### 1. Access the Deployed Site

**URL**: `https://stevenfazzio.github.io/half-america`

#### 2. Functional Checks

| Check | Expected Result |
|-------|-----------------|
| Page loads | Map renders without errors |
| Basemap visible | CARTO basemap tiles load |
| Data layer visible | Census tract polygons displayed |
| Lambda slider | Slider responds, changes visualization |
| All lambda values | Values 0.0-0.9 all work |
| Console errors | No JavaScript errors in browser console |

### Success Criteria:

#### Automated Verification:
- [ ] Site returns 200: `curl -s -o /dev/null -w "%{http_code}" https://stevenfazzio.github.io/half-america`
- [ ] Index.html contains expected content: `curl -s https://stevenfazzio.github.io/half-america | grep -q "half-america"`

#### Manual Verification:
- [ ] Map renders correctly in browser
- [ ] Lambda slider changes the visualization smoothly
- [ ] No console errors (open DevTools > Console)
- [ ] TopoJSON files load (check Network tab for `lambda_*.json` requests)

**Implementation Note**: After verifying deployment, update ROADMAP.md to mark Sub-Phase 5.3 tasks as complete.

---

## Phase 4: Update Documentation

### Overview
Mark Sub-Phase 5.3 as complete in the roadmap.

### Changes Required:

#### 1. Update ROADMAP.md

**File**: `ROADMAP.md`
**Changes**: Mark deployment tasks as complete

```markdown
### Sub-Phase 5.3: Deployment

- [x] Set up GitHub Actions workflow (`working-directory: ./web`)
- [x] Deploy to GitHub Pages (`stevenfazzio.github.io/half-america`)
```

### Success Criteria:

#### Automated Verification:
- [ ] ROADMAP.md contains `[x]` for both Sub-Phase 5.3 tasks

#### Manual Verification:
- [ ] None required

---

## Testing Strategy

### Automated Tests:
- Workflow YAML validation via Python yaml parser
- HTTP response code check via curl
- Content verification via curl + grep

### Manual Testing Steps:
1. Open `https://stevenfazzio.github.io/half-america` in browser
2. Verify map loads with basemap and data layer
3. Move lambda slider from 0.0 to 0.9
4. Confirm visualization changes at each value
5. Open browser DevTools, check Console for errors
6. Check Network tab to verify TopoJSON files load

## Rollback Strategy

If deployment fails or causes issues:
1. Delete or rename `.github/workflows/deploy.yml`
2. In GitHub Settings > Pages, set Source to "Deploy from a branch" > "None"
3. Site will become unavailable but no data is lost

## References

- Research document: `thoughts/shared/research/2025-11-23-subphase-5-3-deployment.md`
- ROADMAP milestones: `ROADMAP.md:131-135`
- Existing CI pattern: `.github/workflows/ci.yml`
- Manual setup docs: `web/GITHUB_SETUP.md`
- Vite deployment guide: https://vite.dev/guide/static-deploy
