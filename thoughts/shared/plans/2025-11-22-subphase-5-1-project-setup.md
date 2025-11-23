# Sub-Phase 5.1: Project Setup Implementation Plan

## Overview

Set up the React + Vite frontend project scaffold with deck.gl and Mapbox dependencies, configured for GitHub Pages deployment. This creates the foundation for the interactive visualization without implementing the actual map components (Sub-Phase 5.2) or deployment workflow (Sub-Phase 5.3).

## Current State Analysis

**What exists:**
- Python backend complete in `src/half_america/`
- 11 TopoJSON files in `data/output/topojson/` (~1.2 MB total)
- CI workflow for Python tests (`.github/workflows/ci.yml`)
- Pre-commit hooks for Python linting

**What's missing:**
- `web/` directory (no frontend scaffold)
- `package.json`, `vite.config.ts`, TypeScript config
- Frontend environment configuration
- TopoJSON files in a web-accessible location

### Key Discoveries:
- TopoJSON files range from 29 KB (`lambda_0.9.json`) to 362 KB (`lambda_0.0.json`)
- `/data/` is gitignored, so files must be copied to `web/public/data/`
- Vite's `react-ts` template already enables strict TypeScript (no changes needed)

## Desired End State

After this plan is complete:

1. A `web/` directory exists with a working React + Vite + TypeScript scaffold
2. All required dependencies are installed (react-map-gl, deck.gl, mapbox-gl, topojson-client)
3. Vite is configured with `base: '/half-america/'` for GitHub Pages
4. Environment configuration exists for `VITE_MAPBOX_ACCESS_TOKEN`
5. TopoJSON files are copied to `web/public/data/`
6. Dev server runs successfully (`npm run dev`)
7. Production build succeeds (`npm run build`)

### Verification:
- `cd web && npm run dev` starts without errors
- `cd web && npm run build` produces `dist/` with correct asset paths
- `web/public/data/` contains all 11 TopoJSON files

## What We're NOT Doing

- **Map component implementation** - Deferred to Sub-Phase 5.2
- **Lambda slider control** - Deferred to Sub-Phase 5.2
- **GitHub Actions deployment workflow** - Deferred to Sub-Phase 5.3
- **GitHub UI configuration** (Pages source, repository secrets) - Manual steps, documented only
- **Monorepo tooling** - Decided against per research findings
- **Custom TypeScript strictness** - Using Vite defaults

---

## Phase 1: Create React + Vite Scaffold

### Overview
Initialize the frontend project using Vite's React + TypeScript template and install all required dependencies.

### Changes Required:

#### 1. Create Vite project
**Command**: Run from repository root

```bash
npm create vite@latest web -- --template react-ts
```

**Expected result**: `web/` directory with standard Vite scaffold

#### 2. Install dependencies
**Command**: Run from `web/` directory

```bash
cd web
npm install

# Core mapping
npm install react-map-gl mapbox-gl

# deck.gl for data visualization
npm install @deck.gl/core @deck.gl/react @deck.gl/mapbox @deck.gl/layers

# TopoJSON parsing
npm install topojson-client

# Type definitions
npm install -D @types/mapbox-gl @types/topojson-client
```

### Success Criteria:

#### Automated Verification:
- [ ] `web/` directory exists with expected structure
- [ ] `npm install` completes without errors: `cd web && npm install`
- [ ] Dependencies present in `package.json`: `grep -q "react-map-gl" web/package.json`
- [ ] TypeScript compiles: `cd web && npm run build` (will fail on Vite config, but TS should pass)

#### Manual Verification:
- [ ] Confirm `web/node_modules/` contains deck.gl packages

**Implementation Note**: After completing this phase and all automated verification passes, proceed to Phase 2.

---

## Phase 2: Configure Vite and TypeScript

### Overview
Configure Vite for GitHub Pages deployment and verify TypeScript settings.

### Changes Required:

#### 1. Update Vite configuration
**File**: `web/vite.config.ts`

Replace contents with:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/half-america/',
})
```

#### 2. Verify TypeScript configuration
**File**: `web/tsconfig.json`

Vite's template already includes `strict: true`. Verify these settings exist (no changes needed):

```json
{
  "compilerOptions": {
    "strict": true,
    "skipLibCheck": true
  }
}
```

**Note**: `skipLibCheck: true` is required for deck.gl compatibility and is already in Vite's default.

### Success Criteria:

#### Automated Verification:
- [ ] Vite config has correct base path: `grep -q "base: '/half-america/'" web/vite.config.ts`
- [ ] TypeScript strict mode enabled: `grep -q '"strict": true' web/tsconfig.json`
- [ ] Build succeeds: `cd web && npm run build`
- [ ] Built assets use correct base path: `grep -q "/half-america/assets" web/dist/index.html`

#### Manual Verification:
- [ ] None required for this phase

**Implementation Note**: After completing this phase and all automated verification passes, proceed to Phase 3.

---

## Phase 3: Set Up Environment and Data

### Overview
Create environment configuration for Mapbox token, update gitignore, and copy TopoJSON files for local development.

### Changes Required:

#### 1. Create environment example file
**File**: `web/.env.example`

```
# Mapbox access token (get from https://account.mapbox.com/access-tokens/)
VITE_MAPBOX_ACCESS_TOKEN=pk.your_mapbox_token_here
```

#### 2. Create local .env file (not committed)
**File**: `web/.env.local`

```
VITE_MAPBOX_ACCESS_TOKEN=pk.actual_token_here
```

**Note**: User must replace with their actual Mapbox token.

#### 3. Update root .gitignore
**File**: `.gitignore`

Append to existing file:

```
# Node.js (web frontend)
web/node_modules/
web/dist/
web/.env
web/.env.local
```

#### 4. Create web-specific .gitignore
**File**: `web/.gitignore`

```
# Dependencies
node_modules/

# Build output
dist/

# Environment (keep .env.example)
.env
.env.local
.env.*.local

# Editor
.vscode/
*.swp
*.swo

# OS
.DS_Store
```

#### 5. Create data directory and copy TopoJSON files
**Commands**:

```bash
mkdir -p web/public/data
cp data/output/topojson/lambda_*.json web/public/data/
cp data/output/topojson/combined.json web/public/data/
```

#### 6. Create TypeScript types for lambda values
**File**: `web/src/types/lambda.ts`

```typescript
/**
 * Lambda parameter values for surface tension control.
 * λ≈0 minimizes area (dusty map), λ≈0.9 minimizes perimeter (smooth blobs).
 */
export const LAMBDA_VALUES = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9] as const;

export type LambdaValue = (typeof LAMBDA_VALUES)[number];

/**
 * Get the path to a TopoJSON file for a given lambda value.
 * Files are served from /half-america/data/ in production.
 */
export const getTopoJsonPath = (lambda: LambdaValue): string =>
  `${import.meta.env.BASE_URL}data/lambda_${lambda.toFixed(1)}.json`;

/**
 * Get the path to the combined TopoJSON file (all lambda values).
 */
export const getCombinedTopoJsonPath = (): string =>
  `${import.meta.env.BASE_URL}data/combined.json`;
```

### Success Criteria:

#### Automated Verification:
- [ ] `.env.example` exists: `test -f web/.env.example`
- [ ] Root `.gitignore` updated: `grep -q "web/node_modules" .gitignore`
- [ ] Web `.gitignore` exists: `test -f web/.gitignore`
- [ ] TopoJSON files copied: `ls web/public/data/lambda_*.json | wc -l` returns 10
- [ ] Combined file copied: `test -f web/public/data/combined.json`
- [ ] Types file exists: `test -f web/src/types/lambda.ts`
- [ ] Types compile: `cd web && npx tsc --noEmit`

#### Manual Verification:
- [ ] User has created `web/.env.local` with their Mapbox token

**Implementation Note**: After completing this phase and all automated verification passes, proceed to Phase 4.

---

## Phase 4: Create Minimal Smoke Test

### Overview
Replace the default Vite template with a minimal app that verifies the setup works, without implementing the actual map (deferred to Sub-Phase 5.2).

### Changes Required:

#### 1. Replace App component
**File**: `web/src/App.tsx`

```typescript
import { LAMBDA_VALUES, getTopoJsonPath } from './types/lambda';
import './App.css';

function App() {
  // Verify environment variable is accessible
  const hasMapboxToken = !!import.meta.env.VITE_MAPBOX_ACCESS_TOKEN;

  return (
    <div className="app">
      <h1>Half of America</h1>
      <p>Project setup complete. Map implementation coming in Sub-Phase 5.2.</p>

      <section>
        <h2>Environment Check</h2>
        <p>
          Mapbox token:{' '}
          <span className={hasMapboxToken ? 'status-ok' : 'status-missing'}>
            {hasMapboxToken ? 'Configured' : 'Missing - create web/.env.local'}
          </span>
        </p>
      </section>

      <section>
        <h2>Data Files</h2>
        <p>TopoJSON files available for lambda values:</p>
        <ul>
          {LAMBDA_VALUES.map((lambda) => (
            <li key={lambda}>
              <code>{getTopoJsonPath(lambda)}</code>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

export default App;
```

#### 2. Replace App styles
**File**: `web/src/App.css`

```css
.app {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  font-family: system-ui, -apple-system, sans-serif;
}

h1 {
  margin-bottom: 0.5rem;
}

h2 {
  margin-top: 2rem;
  font-size: 1.25rem;
}

section {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #f5f5f5;
  border-radius: 8px;
}

ul {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

li {
  margin: 0.25rem 0;
}

code {
  background: #e0e0e0;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  font-size: 0.875rem;
}

.status-ok {
  color: #2e7d32;
  font-weight: bold;
}

.status-missing {
  color: #c62828;
  font-weight: bold;
}
```

#### 3. Update index.html title
**File**: `web/index.html`

Change the `<title>` tag:

```html
<title>Half of America</title>
```

#### 4. Clean up unused template files
**Commands**:

```bash
rm -f web/src/assets/react.svg
rm -f web/public/vite.svg
```

Update `web/src/main.tsx` to remove default index.css import if present, or keep it minimal.

### Success Criteria:

#### Automated Verification:
- [ ] TypeScript compiles: `cd web && npx tsc --noEmit`
- [ ] Build succeeds: `cd web && npm run build`
- [ ] No unused imports: `cd web && npx tsc --noEmit 2>&1 | grep -c "error"` returns 0
- [ ] index.html has correct title: `grep -q "Half of America" web/index.html`

#### Manual Verification:
- [ ] Dev server starts: `cd web && npm run dev`
- [ ] Page loads at http://localhost:5173/half-america/
- [ ] "Mapbox token: Configured" shows (after creating .env.local)
- [ ] TopoJSON file paths are displayed correctly

**Implementation Note**: After completing this phase and all automated verification passes, proceed to Phase 5.

---

## Phase 5: Document Manual Steps

### Overview
Update documentation with instructions for manual GitHub configuration steps that cannot be automated.

### Changes Required:

#### 1. Update CLAUDE.md
**File**: `CLAUDE.md`

Add to the Commands section:

```markdown
## Frontend Development

```bash
cd web
npm install                          # Install dependencies
npm run dev                          # Start dev server (localhost:5173)
npm run build                        # Production build
npm run preview                      # Preview production build
```

**Environment setup**: Copy `web/.env.example` to `web/.env.local` and add your Mapbox token.
```

#### 2. Create GitHub setup instructions
**File**: `web/GITHUB_SETUP.md`

```markdown
# GitHub Configuration for Deployment

These manual steps are required before the deployment workflow (Sub-Phase 5.3) will work.

## 1. Configure GitHub Pages Source

1. Go to repository **Settings** > **Pages**
2. Under "Build and deployment" > "Source", select **GitHub Actions**
3. Save changes

This enables deployment via GitHub Actions instead of branch-based deployment.

## 2. Create Repository Secret for Mapbox Token

1. Go to repository **Settings** > **Secrets and variables** > **Actions**
2. Click **New repository secret**
3. Name: `VITE_MAPBOX_TOKEN`
4. Value: Your Mapbox access token (starts with `pk.`)
5. Click **Add secret**

The deployment workflow will use this secret during the build step.

## Getting a Mapbox Token

1. Create a free account at [mapbox.com](https://account.mapbox.com/)
2. Go to [Access Tokens](https://account.mapbox.com/access-tokens/)
3. Copy your default public token or create a new one
4. The token should start with `pk.` (public token)
```

### Success Criteria:

#### Automated Verification:
- [ ] CLAUDE.md updated: `grep -q "npm run dev" CLAUDE.md`
- [ ] GitHub setup doc exists: `test -f web/GITHUB_SETUP.md`

#### Manual Verification:
- [ ] Instructions are clear and complete
- [ ] User can follow steps to configure GitHub (deferred until Sub-Phase 5.3)

**Implementation Note**: This completes Sub-Phase 5.1. The deployment workflow and GitHub configuration will be done in Sub-Phase 5.3.

---

## Testing Strategy

### Automated Tests:
- TypeScript compilation: `cd web && npx tsc --noEmit`
- Production build: `cd web && npm run build`
- Lint (if configured): `cd web && npm run lint`

### Manual Testing Steps:
1. Start dev server: `cd web && npm run dev`
2. Open http://localhost:5173/half-america/
3. Verify page loads without console errors
4. Verify Mapbox token status shows correctly
5. Verify TopoJSON paths are displayed
6. Test production build: `cd web && npm run build && npm run preview`

---

## Performance Considerations

- TopoJSON files total ~1.2 MB - acceptable for initial load
- Files will be cached by browser after first load
- Pre-loading strategy for smooth slider (Sub-Phase 5.2) will handle perceived performance

---

## References

- Research document: `thoughts/shared/research/2025-11-22-subphase-5-1-project-setup.md`
- deck.gl feasibility: `thoughts/shared/research/2025-11-22-deck-gl-feasibility.md`
- GitHub Pages research: `thoughts/shared/research/2025-11-22-github-pages-hosting.md`
- ROADMAP milestones: `ROADMAP.md:114-121`
