# GitHub Configuration for Deployment

These manual steps are required before the deployment workflow (Sub-Phase 5.3) will work.

## Configure GitHub Pages Source

1. Go to repository **Settings** > **Pages**
2. Under "Build and deployment" > "Source", select **GitHub Actions**
3. Save changes

This enables deployment via GitHub Actions instead of branch-based deployment.

## Notes

- **No API keys required**: This project uses MapLibre GL JS with CARTO basemaps, which are free and require no authentication.
- The deployment workflow will be set up in Sub-Phase 5.3.
