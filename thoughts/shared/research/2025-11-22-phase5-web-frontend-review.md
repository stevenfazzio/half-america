---
date: 2025-11-22T14:00:00-05:00
researcher: Claude
git_commit: c2f6f9a6f5039a1be218a71d2d61486c969a2b73
branch: master
repository: stevenfazzio/half-america
topic: "Phase 5 Web Frontend Milestone Review"
tags: [research, codebase, phase-5, web-frontend, roadmap, milestones]
status: complete
last_updated: 2025-11-22
last_updated_by: Claude
---

# Research: Phase 5 Web Frontend Milestone Review

**Date**: 2025-11-22
**Researcher**: Claude
**Git Commit**: c2f6f9a6f5039a1be218a71d2d61486c969a2b73
**Branch**: master
**Repository**: stevenfazzio/half-america

## Research Question

Should we make adjustments to Phase 5: Web Frontend in ROADMAP.md? Specifically:
1. Are we missing important milestones?
2. Should any milestones be excluded or changed?
3. Could the milestones be grouped into sub-phases?

## Summary

**The current Phase 5 milestones are solid for core functionality** but could benefit from:

1. **Two missing critical milestones**: Environment configuration (Mapbox token) and loading states
2. **One milestone to modify**: GitHub Actions workflow needs more specificity
3. **Recommended sub-phase structure**: Group into 3 sub-phases for clearer execution

**Recommendation**: Keep all existing milestones, add 2 critical ones, modify 1, and organize into sub-phases.

## Current Milestones Analysis

| Current Milestone | Status | Notes |
|-------------------|--------|-------|
| Set up React + Vite application in `web/` directory | ✅ Keep | Essential starting point |
| Configure Vite with `base: '/half-america/'` | ✅ Keep | Required for GitHub Pages |
| Integrate Mapbox GL JS basemap via react-map-gl | ✅ Keep | Core requirement |
| Add deck.gl with MapboxOverlay in interleaved mode | ✅ Keep | Per deck.gl research |
| Implement TopoJSON → GeoJSON conversion | ✅ Keep | Essential for data loading |
| Create GeoJsonLayer for census tract polygons | ✅ Keep | Core visualization |
| Implement λ slider control | ✅ Keep | Core UX feature |
| Pre-load layers for each λ value with visibility toggling | ✅ Keep | Critical for instant slider response |
| Set up GitHub Actions workflow for deployment | ⚠️ Modify | Needs more specificity |
| Deploy to GitHub Pages | ✅ Keep | End goal |

## Recommended Changes

### Missing Milestones (Add)

#### 1. Environment Configuration for Mapbox Token

**Priority**: High (blocking)
**Rationale**: Mapbox GL JS requires an access token. This must be:
- Stored as `VITE_MAPBOX_TOKEN` in `.env.local` for development
- Added as a GitHub repository secret for CI/CD
- Referenced in the build step of the workflow

Without this, the map won't render.

#### 2. Loading State During Initial Data Fetch

**Priority**: Medium (UX)
**Rationale**: Loading ~3.5 MB of TopoJSON files takes noticeable time. Users need feedback:
- Loading spinner or skeleton while data fetches
- Error state if data fails to load

Similar projects (The Pudding's Human Terrain, deck.gl showcase projects) all include loading states.

### Milestones to Modify

#### GitHub Actions Workflow (More Specific)

Current: "Set up GitHub Actions workflow for deployment"

**Issue**: Too vague. The deployment workflow has several specific requirements for a monorepo with environment secrets.

**Suggested breakdown**:
- Configure GitHub Pages source to "GitHub Actions" in repository settings
- Create `VITE_MAPBOX_TOKEN` repository secret
- Create `.github/workflows/deploy.yml` with `working-directory: ./web`
- Pass Mapbox token secret to build step via `env:`

### Milestones to Exclude/Defer

None recommended for exclusion. All current milestones are essential for a functional MVP.

## Recommended Sub-Phase Structure

### Sub-Phase 5.1: Project Setup

Foundation and configuration work.

```markdown
- [ ] Set up React + Vite application in `web/` directory
- [ ] Configure Vite with `base: '/half-america/'` for GitHub Pages
- [ ] Add environment configuration for VITE_MAPBOX_ACCESS_TOKEN
- [ ] Configure GitHub Pages source to "GitHub Actions" in repository settings
- [ ] Create `VITE_MAPBOX_TOKEN` repository secret
```

### Sub-Phase 5.2: Core Visualization

The map and interactive controls.

```markdown
- [ ] Integrate Mapbox GL JS basemap via react-map-gl
- [ ] Add deck.gl with MapboxOverlay in interleaved mode
- [ ] Implement TopoJSON → GeoJSON conversion via topojson-client
- [ ] Create GeoJsonLayer for census tract polygons
- [ ] Add loading state/skeleton during initial data fetch
- [ ] Implement λ slider control for surface tension parameter
- [ ] Pre-load layers for each λ value with visibility toggling (instant slider response)
```

### Sub-Phase 5.3: Deployment

CI/CD and production deployment.

```markdown
- [ ] Set up GitHub Actions workflow for deployment (web/ subdirectory, environment secrets)
- [ ] Deploy to GitHub Pages (`stevenfazzio.github.io/half-america`)
```

## Additional Considerations (Not Required for Phase 5)

These features appeared frequently in similar projects but are appropriate for Phase 6 or Future Enhancements:

| Feature | Priority | Notes |
|---------|----------|-------|
| Statistics panel (area %, population %, tract count) | Medium | Already have `population_selected` in metadata |
| Hover tooltips on regions | Low | Nice-to-have for exploration |
| URL state persistence (?lambda=0.5) | Low | Shareable links |
| Mobile-responsive layout | Medium | Should test but may work by default |
| Accessibility (ARIA labels, keyboard nav) | Medium | Important for production but not MVP |
| Error boundary for WebGL failures | Low | Graceful degradation |

## Comparison with Similar Projects

### The Pudding's "Human Terrain"

- Has splash page with "Start" button (Phase 6: Tabs for description)
- Guided tour with navigation (Future Enhancement)
- Toggle switches for time periods (similar to lambda slider)
- Uses Mapbox with vector tiles (we use pre-computed files - simpler)

### deck.gl Showcase Projects

- All have loading states (**we should add**)
- Heavy use of tooltips/hover states (Future Enhancement)
- Many have parameter controls (lambda slider covers this)

## Architecture Insights

The pre-computation approach in Half of America is ideal for static hosting:
- All expensive computation happens offline (PyMaxFlow)
- Web app is pure visualization (no server needed)
- Data is cacheable (TopoJSON files are immutable per λ)
- GitHub Pages is a perfect fit

The sub-phase structure reflects the natural dependency chain:
1. Setup → 2. Build visualization → 3. Deploy

## Code References

- [`ROADMAP.md:84-126`](https://github.com/stevenfazzio/half-america/blob/c2f6f9a6f5039a1be218a71d2d61486c969a2b73/ROADMAP.md#L84-L126) - Current Phase 5 specification
- [`thoughts/shared/research/2025-11-22-deck-gl-feasibility.md`](thoughts/shared/research/2025-11-22-deck-gl-feasibility.md) - deck.gl research (confirms MapboxOverlay approach)
- [`thoughts/shared/research/2025-11-22-github-pages-hosting.md`](thoughts/shared/research/2025-11-22-github-pages-hosting.md) - GitHub Pages research (confirms feasibility)

## Related Research

- [thoughts/shared/research/2025-11-22-deck-gl-feasibility.md](thoughts/shared/research/2025-11-22-deck-gl-feasibility.md)
- [thoughts/shared/research/2025-11-22-github-pages-hosting.md](thoughts/shared/research/2025-11-22-github-pages-hosting.md)

## Open Questions

1. **Mapbox style choice**: Which Mapbox style (light-v11, dark-v10, etc.) best showcases the population regions?
2. **Lambda granularity**: Start with 0.1 increments (11 files) or go directly to 0.01 (101 files)?
3. **Preloading strategy**: For 101 lambda values, should we lazy-load instead of preload all?

## Sources

### Primary Research
- [deck.gl Using with React](https://deck.gl/docs/get-started/using-with-react)
- [deck.gl Performance Optimization](https://deck.gl/docs/developer-guide/performance)
- [Vite Static Deploy Guide](https://vite.dev/guide/static-deploy)
- [GitHub Pages Limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)

### Similar Projects
- [Human Terrain - The Pudding](https://pudding.cool/2018/10/city_3d/)
- [deck.gl Showcase](https://deck.gl/showcase)
- [Map UI Patterns](https://mapuipatterns.com/patterns/)

### UX Best Practices
- [Designing The Perfect Slider - Smashing Magazine](https://www.smashingmagazine.com/2017/07/designing-perfect-slider/)
- [Minnesota IT Accessibility Guide for Interactive Web Maps](https://mn.gov/mnit/assets/Accessibility%20Guide%20for%20Interactive%20Web%20Maps_tcm38-403564.pdf)

### Deployment
- [GitHub Actions - Deploy Pages](https://github.com/actions/deploy-pages)
- [rossjrw/pr-preview-action](https://github.com/rossjrw/pr-preview-action) (optional for PR previews)
