---
date: 2025-11-22T12:00:00-05:00
researcher: Claude
git_commit: c89a0086c0881e9011e9be94f65252b3c86d438e
branch: master
repository: stevenfazzio/half-america
topic: "GitHub Pages Hosting Feasibility for Half of America Webapp"
tags: [research, deployment, github-pages, hosting, frontend, phase-5]
status: complete
last_updated: 2025-11-22
last_updated_by: Claude
---

# Research: GitHub Pages Hosting Feasibility

**Date**: 2025-11-22
**Researcher**: Claude
**Git Commit**: c89a0086c0881e9011e9be94f65252b3c86d438e
**Branch**: master
**Repository**: stevenfazzio/half-america

## Research Question

Is GitHub Pages a feasible approach for hosting the Half of America webapp? What are the pros and cons, and should we adjust the Phase 5 plan accordingly?

## Summary

**GitHub Pages is highly feasible and recommended** for hosting this project. The architecture is a perfect match:

- **Static-only requirement** - Our pre-computed TopoJSON files + React frontend = pure static site
- **File sizes well under limits** - ~350 KB per lambda file, ~3.5 MB total vs. 1 GB limit
- **Bandwidth sufficient** - 100 GB/month is ample for a portfolio project
- **Zero cost** - Free hosting with custom domain and HTTPS
- **Seamless integration** - Already using GitHub, deployment via Actions is straightforward

**Recommendation**: Proceed with GitHub Pages. Consider Cloudflare Pages as a drop-in alternative if traffic exceeds expectations.

## Detailed Findings

### Current Project State

| Aspect | Status |
|--------|--------|
| Phase 5 (Web Frontend) | Not started |
| Existing frontend code | None |
| TopoJSON files | Generated (~350 KB each, 10 files) |
| Combined.json | Optional (~1 MB) |
| Total static data | ~3.5-4.5 MB |

### GitHub Pages Limits vs. Project Requirements

| Resource | GitHub Pages Limit | Project Requirement | Verdict |
|----------|-------------------|---------------------|---------|
| Site size | 1 GB | ~10-50 MB (app + data) | **OK** |
| File size | 100 MB | ~350 KB max | **OK** |
| Bandwidth | 100 GB/month | Portfolio traffic | **OK** |
| Server-side code | None allowed | None needed | **OK** |
| HTTPS | Free (Let's Encrypt) | Required | **OK** |
| Custom domain | Supported | Desired | **OK** |

### Pros of GitHub Pages

1. **Perfect architecture match** - Static files only, which is exactly what we have
2. **Zero hosting cost** - Free tier is sufficient
3. **Seamless CI/CD** - GitHub Actions deploys on push
4. **Version control integration** - Site lives in same repo as source
5. **Free HTTPS** - Automatic Let's Encrypt certificates
6. **Custom domain support** - Can use `halfofamerica.com` or similar
7. **Reliable infrastructure** - GitHub's CDN is production-grade
8. **Simple rollback** - Revert deployment by reverting commit

### Cons of GitHub Pages

1. **100 GB/month bandwidth** - Soft limit, but could be an issue if project goes viral
2. **No server-side code** - Not a con for us (we don't need it)
3. **Single repo deployment** - Site must come from same repo
4. **Build time limits** - 10 builds/hour (bypassed with Actions)
5. **No edge functions** - Can't add serverless endpoints later

### Specific Technical Considerations

#### React + Vite Configuration

Required `vite.config.js` setting:
```javascript
export default defineConfig({
  base: '/half-america/',  // Must match repo name for GitHub Pages
  plugins: [react()]
})
```

#### React Router Issue

GitHub Pages returns 404 for client-side routes. Solutions:
1. **Use HashRouter** (recommended for simplicity) - URLs like `/#/about`
2. **404.html workaround** - Copy index.html to 404.html during build

For this project, HashRouter is fine since we likely only need one route (the map).

#### MapLibre GL JS

- Works on GitHub Pages with no special configuration
- No API token required (using CARTO basemaps)
- Consider CDN loading to reduce bundle size

#### TopoJSON Serving

- JSON files served correctly as `application/json`
- No CORS issues since data is on same domain
- Pre-computed approach eliminates need for dynamic API

### Alternatives Comparison

| Feature | GitHub Pages | Cloudflare Pages | Netlify | Vercel |
|---------|-------------|------------------|---------|--------|
| Bandwidth | 100 GB/mo | **Unlimited** | 100 GB/mo | 100 GB/mo |
| Site size | 1 GB | Unlimited | 10 GB | - |
| Cost | Free | Free | Free | Free |
| Build minutes | Unlimited (Actions) | 500/mo | 300/mo | 6,000/mo |
| Edge functions | No | Yes | Yes | Yes |
| Complexity | Low | Low | Medium | Medium |

**Cloudflare Pages is the best fallback** if GitHub Pages limits become an issue. Migration would be straightforward since both serve static files.

## Recommendations

### Proceed with GitHub Pages

1. **No plan changes needed** - Current Phase 5 approach is compatible
2. **Add deployment workflow** - GitHub Actions for CI/CD
3. **Configure Vite correctly** - Set `base` path for repo name
4. **Use HashRouter** - Simplest solution for SPA routing

### Deployment Workflow

Add `.github/workflows/deploy.yml`:
```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: ['main']
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v6
        with:
          node-version: lts/*
          cache: 'npm'
          cache-dependency-path: 'web/package-lock.json'
      - run: npm ci
        working-directory: web
      - run: npm run build
        working-directory: web
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v4
        with:
          path: 'web/dist'
      - uses: actions/deploy-pages@v4
        id: deployment
```

### Data Strategy Options

**Option A: Include TopoJSON in repo (recommended)**
- Commit TopoJSON files to `web/public/data/`
- Simple, no build-time generation
- Small size (~3.5 MB) acceptable in repo

**Option B: Generate during build**
- Run Python export as part of GitHub Actions
- Requires Python environment in workflow
- More complex, but keeps data out of repo

**Option C: External data hosting**
- Host TopoJSON on separate CDN (S3, R2, etc.)
- Adds complexity and potential CORS issues
- Only needed if data is very large

For this project, **Option A is best** due to small file sizes and simplicity.

### Suggested Project Structure

```
half-america/
├── src/                    # Python package (existing)
├── web/                    # NEW: Frontend application
│   ├── public/
│   │   └── data/           # Pre-computed TopoJSON files
│   │       ├── lambda_0.0.json
│   │       ├── lambda_0.1.json
│   │       └── ...
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── Map.tsx
│   │   │   └── LambdaSlider.tsx
│   │   └── main.tsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
├── .github/
│   └── workflows/
│       └── deploy.yml      # GitHub Pages deployment
└── ...
```

## Architecture Insights

The project's pre-computation approach is ideally suited for static hosting:

1. **Expensive computation happens offline** - PyMaxFlow optimization runs once
2. **Web app is pure visualization** - No server-side processing needed
3. **Data is cacheable** - TopoJSON files never change after generation
4. **Lambda interpolation is client-side** - Slider just swaps files

This architecture means **any static host will work**. GitHub Pages is simply the most convenient choice given the existing GitHub workflow.

## Decisions (Resolved)

| Question | Decision |
|----------|----------|
| Custom domain? | Use `github.io` subdomain (`stevenfazzio.github.io/half-america`) |
| Lambda granularity? | Start with 0.1 step; move to 0.01 later (per Future Enhancements) |
| Smooth transitions? | Pre-loading makes sense; needs more research |
| Analytics? | None planned |

## Code References

- `src/half_america/cli.py:77-161` - Export CLI command
- `src/half_america/postprocess/export.py:40` - `export_to_topojson()` function
- `src/half_america/config.py:21-22` - Output directory configuration
- `ROADMAP.md:84-97` - Phase 5 milestones

## Sources

- [GitHub Pages Limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)
- [About GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages)
- [Deploying Vite to GitHub Pages](https://vite.dev/guide/static-deploy)
- [Mapbox GL JS Large GeoJSON Data](https://docs.mapbox.com/help/troubleshooting/working-with-large-geojson-data/)
- [Cloudflare Pages Limits](https://developers.cloudflare.com/pages/platform/limits/)
