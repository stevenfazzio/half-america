# Slider Endpoint Labels Implementation Plan

## Overview

Add "Fragmented" and "Compact" labels below the slider track to encourage user exploration, as specified in ROADMAP.md Phase 6.

## Current State Analysis

The LambdaSlider component (`web/src/components/LambdaSlider.tsx`) currently has:
- A label ("Surface Tension (λ)")
- A slider container with range input + numeric value display
- A dynamic hint that changes based on lambda value

**Missing**: Static endpoint labels indicating what the slider extremes represent.

## Desired End State

After this plan is complete:
- "Fragmented" appears at the left end of the slider (λ=0)
- "Compact" appears at the right end of the slider (λ→1)
- Labels are subtle (11px, 50% opacity) to avoid competing with the numeric value
- Layout works on both desktop and mobile

**Visual representation:**
```
Surface Tension (λ)

─────────────●───────────── 0.50
Fragmented                 Compact

         Balanced optimization
```

## What We're NOT Doing

- Changing the dynamic hint text
- Adding tooltips or additional interactivity
- Modifying the slider behavior
- Adding animations

## Implementation Approach

Simple CSS/JSX changes following existing patterns in the codebase.

## Phase 1: Add Endpoint Labels

### Overview
Add a new flex container with two labels positioned at slider extremes.

### Changes Required:

#### 1. LambdaSlider Component
**File**: `web/src/components/LambdaSlider.tsx`
**Changes**: Add `.slider-endpoints` div between slider container and hint

Insert after line 40 (closing `</div>` of slider-container):

```tsx
      <div className="slider-endpoints">
        <span>Fragmented</span>
        <span>Compact</span>
      </div>
```

#### 2. LambdaSlider Styles
**File**: `web/src/components/LambdaSlider.css`
**Changes**: Add `.slider-endpoints` styling

Add after `.lambda-value` block (after line 86):

```css
.slider-endpoints {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 4px;
  padding: 0 2px;
}
```

### Success Criteria:

#### Automated Verification:
- [x] Build succeeds: `npm run build`
- [x] Lint passes: `npm run lint`
- [x] No TypeScript errors

#### Manual Verification:
- [x] "Fragmented" label visible at left end of slider
- [x] "Compact" label visible at right end of slider
- [x] Labels are visually subtle (don't compete with slider value)
- [x] Works on desktop layout (slider in top-left corner)
- [x] Works on mobile layout (slider at bottom of screen)

---

## Testing Strategy

### Manual Testing Steps:
1. Run `npm run dev` in `web/` directory
2. Open http://localhost:5173
3. Verify labels appear below slider track
4. Resize browser to mobile width (<768px)
5. Verify labels still display correctly
6. Move slider to verify labels don't interfere with interaction

## Performance Considerations

None - this is static content with no runtime impact.

## References

- Research: `thoughts/shared/research/2025-11-24-slider-endpoint-labels.md`
- Component: `web/src/components/LambdaSlider.tsx:19-47`
- Styles: `web/src/components/LambdaSlider.css:88-93`
