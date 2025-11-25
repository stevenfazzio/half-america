# Lambda Slider Tooltip Content Update

## Overview

Update the Lambda Slider tooltip to better emphasize the physical analogy of surface tension and provide clearer practical guidance on what the parameter does. Replace the current two-section tooltip (technical + practical) with a unified educational approach that leads with the physical intuition.

## Current State Analysis

The tooltip is currently implemented in `web/src/components/LambdaSlider.tsx:40-61` with two sections:
1. "What it does:" - Explains compact boundaries vs precise area, suggests Story tab
2. "How it works:" - Technical graph optimization details, suggests Method tab

**Current Issues:**
- Leads with abstract concepts ("compact boundaries", "precise area selection")
- Technical section may be too detailed for initial exploration
- Doesn't emphasize the physical analogy that makes λ intuitive

## Desired End State

A single-section tooltip that:
1. Leads with the physical analogy (liquid surface tension)
2. Connects the analogy to the visual effect on the map
3. Provides practical guidance on low vs high λ values
4. Directs users to Story and Method tabs for deeper exploration

### Success Criteria:

#### Automated Verification:
- [ ] TypeScript compiles without errors: `npm run build`
- [ ] No linting errors: `npm run lint`
- [ ] Dev server runs successfully: `npm run dev`

#### Manual Verification:
- [ ] Tooltip displays correctly on hover/click of info icon
- [ ] Tooltip content is readable and well-formatted
- [ ] Links to Story and Method tabs are clear and actionable
- [ ] Tooltip positioning works on both mobile and desktop
- [ ] No visual regressions in tooltip styling

## What We're NOT Doing

- Not changing the tooltip trigger mechanism (hover/click/focus behavior)
- Not modifying CSS styling or layout
- Not changing the info icon appearance
- Not altering the slider functionality itself

## Implementation Approach

This is a simple content replacement in the JSX. The structure remains a single tooltip div with sections, but the content will be rewritten to match the new educational approach.

## Phase 1: Update Tooltip Content

### Overview
Replace the current two-section tooltip content with the new unified educational content that emphasizes the surface tension analogy.

### Changes Required:

#### 1. LambdaSlider Component
**File**: `web/src/components/LambdaSlider.tsx`
**Changes**: Replace lines 40-61 (tooltip JSX content)

**Current Structure:**
```tsx
{showTooltip && (
  <div className="lambda-tooltip" role="tooltip">
    <div className="tooltip-section">
      <strong>What it does:</strong>
      <p>...</p>
      <p className="tooltip-suggestion">Visit the Story tab to learn more.</p>
    </div>
    <div className="tooltip-section">
      <strong>How it works:</strong>
      <p>...</p>
      <p className="tooltip-suggestion">See the Method tab for full methodology.</p>
    </div>
  </div>
)}
```

**New Structure:**
```tsx
{showTooltip && (
  <div className="lambda-tooltip" role="tooltip">
    <div className="tooltip-section">
      <strong>What "Surface Tension" means here:</strong>
      <p>
        In liquids, surface tension causes water to bead into smooth, rounded shapes.
        Here, increasing λ has a similar effect—pulling the selected regions into
        smoother, more cohesive boundaries.
      </p>
    </div>
    <div className="tooltip-section">
      <strong>Practically:</strong>
      <p>
        Low λ preserves fine detail but creates many tiny fragments.
        High λ smooths edges and merges nearby areas into clearer shapes.
      </p>
    </div>
    <div className="tooltip-section">
      <strong>Learn more:</strong>
      <p className="tooltip-suggestion">
        See the Story tab for examples and motivation.
      </p>
      <p className="tooltip-suggestion">
        See the Method tab for the full formulation.
      </p>
    </div>
  </div>
)}
```

**Key Changes:**
- Three sections instead of two: "What 'Surface Tension' means here", "Practically", "Learn more"
- Lead with physical analogy (surface tension → water beading)
- Connect analogy to visual effect (smoother, cohesive boundaries)
- Practical guidance uses clearer language (fine detail/fragments vs smoothing/merging)
- Consolidate both tab references into a "Learn more" section
- Use consistent capitalization ("Story tab", "Method tab")

### Success Criteria:

#### Automated Verification:
- [ ] TypeScript compiles without errors: `npm run build`
- [ ] No linting errors: `npm run lint`
- [ ] Dev server runs without errors: `npm run dev`

#### Manual Verification:
- [ ] Tooltip displays on hover/click/focus of info icon
- [ ] All three sections render correctly with proper formatting
- [ ] Text wrapping and line breaks are natural and readable
- [ ] "Learn more" section clearly directs to both tabs
- [ ] Tooltip remains positioned correctly (not cut off on mobile)
- [ ] No visual regressions compared to previous tooltip

## Testing Strategy

### Manual Testing Steps:
1. **Desktop Testing:**
   - Hover over info icon → tooltip should appear
   - Click info icon → tooltip should toggle
   - Tab to info icon → tooltip should appear on focus
   - Verify all three sections are visible and readable
   - Check text wrapping at various browser widths (360px, 768px, 1024px)

2. **Mobile Testing:**
   - Open dev server on mobile device or use responsive mode
   - Tap info icon → tooltip should appear
   - Verify tooltip doesn't overflow screen edges
   - Check that text is readable at mobile font sizes

3. **Content Verification:**
   - Verify "Surface Tension" is properly quoted
   - Verify λ symbol renders correctly
   - Verify "Story tab" and "Method tab" capitalization is consistent
   - Verify punctuation is correct (periods at end of sentences)

## References

- Component: `web/src/components/LambdaSlider.tsx:40-61`
- Styling: `web/src/components/LambdaSlider.css:64-123`
- Recent improvements: See git log for slider-related commits (tooltip added in recent work)
