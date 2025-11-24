# Lambda Decimal Precision Bug Fix

## Overview

Fix inconsistency where the lambda value displays 1 decimal place in the legend but 2 decimal places in the slider.

## Current State Analysis

- **Slider** (`LambdaSlider.tsx:37,39`): Uses `value.toFixed(2)` → displays "0.50"
- **Legend** (`SummaryPanel.tsx:52`): Uses `lambda.toFixed(1)` → displays "0.5"

## Desired End State

Both the slider and legend display lambda with 2 decimal places (e.g., "0.50").

## What We're NOT Doing

- Changing the slider's precision
- Modifying any other metrics in the legend
- Adding any new features

## Implementation Approach

Single line change in SummaryPanel.tsx.

## Phase 1: Fix Precision

### Overview
Change `toFixed(1)` to `toFixed(2)` in the legend.

### Changes Required:

**File**: `web/src/components/SummaryPanel.tsx`
**Line**: 52

```tsx
// Before
<dd>{lambda.toFixed(1)}</dd>

// After
<dd>{lambda.toFixed(2)}</dd>
```

### Success Criteria:

#### Automated Verification:
- [x] TypeScript compiles: `npm run build`
- [x] Linting passes: `npm run lint`

#### Manual Verification:
- [ ] Lambda value in legend shows 2 decimal places (e.g., "0.50" not "0.5")
- [ ] Value matches slider display exactly

## References

- Research: `thoughts/shared/research/2025-11-23-ui-style-polish.md` (Section 8)
