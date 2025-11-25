# Methodology-Forward Slider Improvements Implementation Plan

## Overview

This plan implements focused slider improvements to enhance the lambda (λ) slider's usability and educational value through better visual polish and on-demand explanations. The slider is already prominently positioned in the UI; this plan focuses on refinement rather than restructuring.

**Based on**: `thoughts/shared/research/2025-11-24-methodology-forward-slider-improvements.md` (adapted based on user feedback)

## Current State Analysis

### What Exists Now:
- Lambda slider component with basic functionality (`web/src/components/LambdaSlider.tsx`)
- Visual hierarchy that de-emphasizes methodology:
  - Hero stats: 28px (population %, land %)
  - Lambda: 11px, hidden on mobile
- Slider positioned at bottom-left on mobile, top-left on desktop (280px width)
- Semantic endpoint labels ("Fragmented" / "Compact") without directional indicators
- Dynamic microcopy hints based on lambda value
- Fast layer-toggle architecture for real-time updates
- State management local to MapTab component

### Key Constraints Discovered:
- Lambda values are discrete (99 values from 0.0 to 0.98) defined in `LAMBDA_VALUES` constant
- Slider uses index-based control, not continuous values
- All lambda layers pre-loaded via `useTopoJsonLoader` for performance
- TabBar controls visibility - StoryTab and MapTab don't share state currently
- Mobile vs desktop layouts use different positioning strategies

### What's Missing (Industry Standards):
1. ❌ Directional arrows on endpoint labels
2. ❌ Info icon/tooltip for on-demand explanation
3. ❌ Dual control option (slider + numeric input)
4. ❌ Improved label positioning (lambda value symmetry)

## Desired End State

### Post-Implementation Specifications:

**Slider Polish**:
- Directional arrows on endpoint labels (← Fragmented / Compact →)
- Lambda value centered below slider (improved symmetry)
- Slider width: 360px on desktop (28% increase from current 280px for better precision)

**Educational Features**:
- Info icon (ⓘ) with tooltip explaining λ parameter and methodology
- Tooltip links to Story tab (what it does) and Method tab (how it works)
- Optional dual control mode (toggle between slider and numeric input)

**Interaction Patterns**:
- Real-time response maintained (<0.1s via existing layer toggle)
- Accessibility: ARIA labels, keyboard navigation, screen reader support
- Progressive disclosure: tooltip appears on hover/click, doesn't clutter default view

### Verification Criteria:
- [ ] Tooltip renders with correct content and positioning
- [ ] Slider responds within 100ms (validated via browser DevTools performance tab)
- [ ] All ARIA attributes present and correct
- [ ] Build succeeds without warnings: `npm run build`
- [ ] TypeScript compilation passes (if configured)

## What We're NOT Doing

1. **Not changing SummaryPanel visual hierarchy**: Lambda is already displayed in both slider and panel - sufficient for minimal UI
2. **Not adding default value markers**: λ=0.5 default is arbitrary and doesn't need visual indication
3. **Not changing slider functionality**: The underlying index-based LAMBDA_VALUES system remains unchanged
4. **Not modifying data loading**: The useTopoJsonLoader architecture stays as-is
5. **Not implementing advanced features**: Before/after previews, guided prompts, and advanced parameters are future work
6. **Not implementing narrative embedding**: StoryTab integration requires coordination with content rewrite
7. **Not adding analytics/tracking**: Event tracking for engagement metrics is future work
8. **Not changing Map/Story/Method tab structure**: TabBar and routing logic remain unchanged
9. **Not modifying backend**: All changes are frontend-only

## Implementation Approach

**Strategy**: Implement changes in 2 sequential phases, validating each phase before proceeding.

**Phase 1 (Polish)**: Fix visual asymmetry and add directional indicators
**Phase 2 (Educational)**: Add on-demand explanations and precision control

**Key Principles**:
1. **Incremental verification**: Test after each component change
2. **Preserve performance**: Maintain <0.1s response time via existing architecture
3. **Mobile-first responsive**: Ensure all features work on small screens
4. **Accessibility-first**: ARIA attributes, semantic HTML, keyboard navigation

---

## Phase 1: Visual Polish & Precision

### Overview
Improve slider visual symmetry, add directional indicators, and increase slider width for better precision control.

### Changes Required:

#### 1. Fix Label Positioning Asymmetry & Add Directional Arrows

**File**: `web/src/components/LambdaSlider.tsx`
**Changes**: Separate lambda value display from slider container and add directional arrows

**Current structure** (lines 24-44):
```tsx
<div className="slider-container">
  <input type="range" ... />
  <span className="lambda-value">{value.toFixed(2)}</span>
</div>
<div className="slider-endpoints">
  <span>Fragmented</span>
  <span>Compact</span>
</div>
```

**Problem**: Lambda value appears inline with slider, breaking visual symmetry with endpoint labels.

**New structure**:
```tsx
<div className="slider-container">
  <input type="range" ... />
</div>
<div className="slider-endpoints">
  <span>← Fragmented</span>
  <span>Compact →</span>
</div>
<div className="slider-value-display">
  <span className="lambda-value">{value.toFixed(2)}</span>
</div>
```

**Note**: Added directional arrows (← →) to endpoint labels as part of same edit.

---

**File**: `web/src/components/LambdaSlider.css`
**Changes**: Update styles for new value display placement and increase slider width

**Update** `.slider-container`:
```css
.slider-container {
  margin-bottom: 4px;
}
```

**Update** `.lambda-value`:
```css
.lambda-value {
  font-size: 16px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
  font-variant-numeric: tabular-nums;
}
```

**Add new** `.slider-value-display`:
```css
.slider-value-display {
  display: flex;
  justify-content: center;
  margin-top: 6px;
}
```

**Update desktop width** (line 20):
```css
@media (min-width: 768px) {
  .lambda-slider {
    /* ... existing properties ... */
    width: 360px; /* Increased from 280px for better precision */
  }
}
```

---

### Success Criteria:

#### Automated Verification:
- [ ] Build succeeds: `npm run build`
- [ ] No layout shifts or CSS warnings in console
- [ ] Slider still functional after restructuring

#### Manual Verification:
- [ ] Endpoint labels show arrows: "← Fragmented" / "Compact →"
- [ ] Lambda value appears centered below slider (not inline)
- [ ] Slider symmetry verified: left and right labels align visually
- [ ] Slider width is 360px on desktop — measure in browser DevTools
- [ ] No visual glitches when resizing browser window
- [ ] Increased slider width improves precision when selecting specific λ values

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful before proceeding to Phase 2.

---

## Phase 2: Educational Enhancements

### Overview
Add on-demand depth for Technical Evaluators (critical for portfolio) and Curious Readers. These features demonstrate thoroughness without cluttering the interface.

### Changes Required:

#### 1. Add Info Icon with Tooltip

**File**: `web/src/components/LambdaSlider.tsx`
**Changes**: Add info icon and tooltip state management

**Import additions** (top of file):
```tsx
import { useState } from 'react'; // Add if not already imported
```

**Update component**:
```tsx
export function LambdaSlider({ value, onChange, disabled }: LambdaSliderProps) {
  const stepIndex = LAMBDA_VALUES.indexOf(value);
  const [showTooltip, setShowTooltip] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const index = parseInt(e.target.value, 10);
    onChange(LAMBDA_VALUES[index]);
  };

  return (
    <div className="lambda-slider">
      <label htmlFor="lambda-slider" className="lambda-label">
        Surface Tension (λ)
        <button
          type="button"
          className="info-icon"
          aria-label="What is surface tension? Click for details"
          onMouseEnter={() => setShowTooltip(true)}
          onMouseLeave={() => setShowTooltip(false)}
          onClick={() => setShowTooltip(!showTooltip)}
          onFocus={() => setShowTooltip(true)}
          onBlur={() => setShowTooltip(false)}
        >
          <span className="icon" aria-hidden="true">ⓘ</span>
        </button>
      </label>

      {showTooltip && (
        <div className="lambda-tooltip" role="tooltip">
          <div className="tooltip-section">
            <strong>What it does:</strong>
            <p>
              Surface Tension (λ) controls the tradeoff between compact boundaries
              and precise area selection. Lower values create scattered regions
              that minimize land area. Higher values create smooth, organic shapes.
            </p>
            <a href="#story" className="tooltip-link">Learn more in the Story tab →</a>
          </div>
          <div className="tooltip-section">
            <strong>How it works:</strong>
            <p>
              Uses max-flow min-cut graph optimization with a perimeter
              minimization term. λ weights the boundary smoothness penalty
              in the energy function.
            </p>
            <a href="#method" className="tooltip-link">See full methodology in Method tab →</a>
          </div>
        </div>
      )}

      <div className="slider-container">
        <input
          id="lambda-slider"
          type="range"
          min={0}
          max={LAMBDA_VALUES.length - 1}
          step={1}
          value={stepIndex}
          onChange={handleChange}
          disabled={disabled}
          aria-valuemin={0}
          aria-valuemax={0.98}
          aria-valuenow={value}
          aria-valuetext={`Lambda ${value.toFixed(2)}`}
          aria-describedby={showTooltip ? 'lambda-tooltip' : undefined}
        />
      </div>
      <div className="slider-endpoints">
        <span>← Fragmented</span>
        <span>Compact →</span>
      </div>
      <div className="slider-value-display">
        <span className="lambda-value">{value.toFixed(2)}</span>
      </div>
      <p className="lambda-hint">
        {value < 0.3 ? 'Minimizes area (more fragmented)' :
         value > 0.7 ? 'Minimizes perimeter (smoother shapes)' :
         'Balanced optimization'}
      </p>
    </div>
  );
}
```

---

**File**: `web/src/components/LambdaSlider.css`
**Changes**: Add tooltip styles

```css
/* Info icon button */
.lambda-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
}

.info-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  padding: 0;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.info-icon:hover,
.info-icon:focus {
  background: rgba(0, 114, 178, 0.2);
  border-color: rgba(0, 114, 178, 0.6);
  color: #0072B2;
  outline: none;
}

.info-icon:focus-visible {
  outline: 2px solid #0072B2;
  outline-offset: 2px;
}

/* Tooltip container */
.lambda-tooltip {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 8px;
  padding: 14px;
  background: rgba(0, 0, 0, 0.95);
  border: 1px solid rgba(0, 114, 178, 0.4);
  border-radius: 6px;
  font-size: 13px;
  line-height: 1.5;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
}

.tooltip-section {
  margin-bottom: 12px;
}

.tooltip-section:last-child {
  margin-bottom: 0;
}

.tooltip-section strong {
  display: block;
  margin-bottom: 4px;
  color: #56B4E9;
  font-size: 12px;
}

.tooltip-section p {
  margin: 0 0 6px 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
}

.tooltip-link {
  display: inline-block;
  margin-top: 4px;
  color: #0072B2;
  text-decoration: none;
  font-weight: 600;
  font-size: 11px;
  transition: color 0.2s ease;
}

.tooltip-link:hover,
.tooltip-link:focus {
  color: #56B4E9;
  text-decoration: underline;
}

/* Mobile: Adjust tooltip positioning and size */
@media (max-width: 767px) {
  .lambda-tooltip {
    font-size: 12px;
    padding: 12px;
  }

  .tooltip-section p {
    font-size: 11px;
  }

  .tooltip-link {
    font-size: 10px;
  }
}
```

---

#### 2. Add Dual Control (Optional Text Input Mode)

**File**: `web/src/components/LambdaSlider.tsx`
**Changes**: Add toggle between slider and numeric input

**Add state** (after existing state):
```tsx
const [inputMode, setInputMode] = useState<'slider' | 'input'>('slider');
const [inputValue, setInputValue] = useState(value.toFixed(2));
```

**Add input handler**:
```tsx
const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  const val = e.target.value;
  setInputValue(val);

  const numVal = parseFloat(val);
  if (!isNaN(numVal) && numVal >= 0 && numVal <= 0.98) {
    // Find closest lambda value
    const closest = LAMBDA_VALUES.reduce((prev, curr) =>
      Math.abs(curr - numVal) < Math.abs(prev - numVal) ? curr : prev
    );
    onChange(closest);
  }
};

// Update inputValue when value prop changes
useEffect(() => {
  setInputValue(value.toFixed(2));
}, [value]);
```

**Add imports**:
```tsx
import { useState, useEffect } from 'react'; // Update import
```

**Update JSX** (replace slider-container section):
```tsx
<div className="slider-mode-controls">
  <button
    type="button"
    onClick={() => setInputMode('slider')}
    className={`mode-toggle ${inputMode === 'slider' ? 'active' : ''}`}
    aria-label="Slider mode"
    aria-pressed={inputMode === 'slider'}
  >
    🎚️
  </button>
  <button
    type="button"
    onClick={() => setInputMode('input')}
    className={`mode-toggle ${inputMode === 'input' ? 'active' : ''}`}
    aria-label="Numeric input mode"
    aria-pressed={inputMode === 'input'}
  >
    🔢
  </button>
</div>

{inputMode === 'slider' ? (
  <div className="slider-container">
    <input
      id="lambda-slider"
      type="range"
      min={0}
      max={LAMBDA_VALUES.length - 1}
      step={1}
      value={stepIndex}
      onChange={handleChange}
      disabled={disabled}
      aria-valuemin={0}
      aria-valuemax={0.98}
      aria-valuenow={value}
      aria-valuetext={`Lambda ${value.toFixed(2)}`}
    />
  </div>
) : (
  <div className="input-container">
    <input
      id="lambda-input"
      type="number"
      min={0}
      max={0.98}
      step={0.01}
      value={inputValue}
      onChange={handleInputChange}
      disabled={disabled}
      className="lambda-numeric-input"
      aria-label="Lambda value"
      aria-valuemin={0}
      aria-valuemax={0.98}
    />
  </div>
)}
```

---

**File**: `web/src/components/LambdaSlider.css`
**Changes**: Add styles for dual control mode

```css
/* Mode toggle buttons */
.slider-mode-controls {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
  justify-content: flex-end;
}

.mode-toggle {
  width: 32px;
  height: 28px;
  padding: 0;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mode-toggle:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
}

.mode-toggle.active {
  background: rgba(0, 114, 178, 0.3);
  border-color: #0072B2;
  color: #fff;
}

.mode-toggle:focus-visible {
  outline: 2px solid #0072B2;
  outline-offset: 2px;
}

/* Numeric input styling */
.input-container {
  position: relative;
  margin-bottom: 4px;
}

.lambda-numeric-input {
  width: 100%;
  height: 40px;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  text-align: center;
  transition: all 0.2s ease;
}

.lambda-numeric-input:hover {
  border-color: rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.15);
}

.lambda-numeric-input:focus {
  outline: none;
  border-color: #0072B2;
  background: rgba(0, 114, 178, 0.1);
}

.lambda-numeric-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Remove number input spinners for cleaner look */
.lambda-numeric-input::-webkit-inner-spin-button,
.lambda-numeric-input::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.lambda-numeric-input[type='number'] {
  -moz-appearance: textfield;
}
```

---

### Success Criteria:

#### Automated Verification:
- [ ] Build succeeds: `npm run build`
- [ ] No console errors when toggling input modes
- [ ] TypeScript compilation passes (no type errors)
- [ ] Tooltip renders without layout shifts

#### Manual Verification:
- [ ] Info icon (ⓘ) appears next to "Surface Tension (λ)" label
- [ ] Tooltip appears on hover and click, contains all specified content
- [ ] Tooltip link navigates to #method tab
- [ ] Tooltip closes when clicking outside or pressing Escape
- [ ] Mode toggle buttons switch between slider and numeric input
- [ ] Numeric input accepts values 0.00-0.98, rounds to nearest available λ
- [ ] Invalid numeric input doesn't break map rendering
- [ ] Tooltip readable on mobile (text not truncated)
- [ ] All interactive elements keyboard accessible (Tab navigation works)
- [ ] Screen reader announces tooltip content correctly

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation from the human that the manual testing was successful. This completes the core slider improvements.

---

## Testing Strategy

### Unit Tests (Future Enhancement)
While not implemented in this plan, the following could be tested:

**LambdaSlider Component**:
- Renders with correct initial lambda value
- Calls onChange when slider moved
- Tooltip toggles correctly on click/hover
- Numeric input mode rounds to nearest LAMBDA_VALUE
- ARIA attributes present and correct

**SummaryPanel Component**:
- Lambda hero section renders above supporting stats
- Mobile layout hides nothing critical
- CSS classes applied correctly

### Integration Tests (Future Enhancement)
- Slider updates map layer visibility in real-time
- Mode toggle preserves lambda value when switching
- Tooltip doesn't interfere with slider interaction

### Manual Testing Steps

#### Slider Polish Verification (Phase 1):
1. Verify endpoint arrows visible: "← Fragmented" / "Compact →"
2. Lambda value appears centered below slider (not inline)
3. Slider width is 360px on desktop — measure in browser DevTools
4. Drag slider from λ=0.0 to λ=0.98, verify smooth movement
5. Verify map updates within 100ms (no perceptible lag)
6. Check layout at viewport widths: 375px, 768px, 1024px, 1920px

#### Tooltip Functionality (Phase 2):
1. Hover over info icon (ⓘ) → tooltip appears
2. Move mouse away → tooltip disappears
3. Click icon → tooltip toggles on/off
4. Verify tooltip has two sections: "What it does" and "How it works"
5. Click "Learn more in the Story tab →" → navigates to #story
6. Click "See full methodology in Method tab →" → navigates to #method
7. Test keyboard: Tab to icon, Enter to open, Escape to close
8. Verify mobile layout: tooltip not cut off at screen edges

#### Dual Control Mode (Phase 2):
1. Click 🔢 button → numeric input appears
2. Type "0.75" → map updates to λ=0.75
3. Type "0.735" → rounds to closest value (0.73 or 0.74)
4. Click 🎚️ button → slider reappears with correct position
5. Verify mode toggle preserves lambda value

#### Accessibility:
1. Navigate entire slider using only keyboard (Tab, arrow keys)
2. Use screen reader (VoiceOver/NVDA) to verify ARIA labels
3. Verify color contrast meets WCAG AA standards (0072B2 on dark background)
4. Check focus indicators visible on all interactive elements

#### Cross-Browser:
- Chrome/Edge (Chromium)
- Firefox
- Safari (desktop and iOS)

---

## Performance Considerations

### Real-Time Response Requirement
**Target**: <0.1s response time for exploration to feel fluid

**Current Architecture** (validated):
- All lambda layers pre-loaded via `useTopoJsonLoader`
- Layer visibility toggled via `visible` property in GeoJsonLayer (lines 50-67 of MapTab.tsx)
- No re-rendering or data fetching during slider movement
- **Expected performance**: ✅ Meets <0.1s requirement

**Validation**:
Add performance monitoring during development (optional):

```tsx
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  const start = performance.now();
  const index = parseInt(e.target.value, 10);
  onChange(LAMBDA_VALUES[index]);

  requestAnimationFrame(() => {
    const duration = performance.now() - start;
    if (duration > 100) {
      console.warn(`⚠️ Slider response slow: ${duration.toFixed(1)}ms`);
    }
  });
};
```

**Note**: Remove performance monitoring before production build.

---

### Bundle Size Impact
**New additions**:
- Tooltip component: ~1KB (inline, no dependencies)
- Numeric input: ~0.5KB
- CSS additions: ~2KB uncompressed

**Total impact**: <5KB uncompressed, <2KB gzipped
**Assessment**: Negligible impact on bundle size

---

## Migration Notes

**No data migration required** — all changes are UI/styling only.

**Breaking changes**: None
**Backwards compatibility**: Maintains existing component APIs

**Deployment considerations**:
- Static site — no server changes needed
- Can deploy incrementally (phases 0, 1, 2 as separate deploys if desired)
- No cache invalidation required beyond normal asset versioning

---

## References

### Research Documents:
- Original research: `thoughts/shared/research/2025-11-24-methodology-forward-slider-improvements.md`
- Slider UX research: `thoughts/shared/research/2025-11-24-slider-improvement-research.md`
- Project purpose alignment: `thoughts/shared/research/2025-11-24-project-purpose-alignment.md`
- User personas: `thoughts/shared/research/2025-11-23-user-personas-and-stories.md`

### Current Implementation:
- Slider component: `web/src/components/LambdaSlider.tsx:1-52`
- Slider styles: `web/src/components/LambdaSlider.css:1-103`
- Summary panel: `web/src/components/SummaryPanel.tsx:1-67`
- Summary styles: `web/src/components/SummaryPanel.css:1-131`
- Map integration: `web/src/components/MapTab.tsx:1-100`
- Lambda constants: `web/src/types/lambda.ts:1-32`

### Industry Best Practices:
- Distill.pub methodology showcases: https://distill.pub/
- Nielsen Norman Group slider guidelines: https://www.nngroup.com/articles/gui-slider-controls/
- TensorFlow Playground: http://playground.tensorflow.org/
- Bret Victor explorable explanations: https://worrydream.com/ExplorableExplanations/

---

## Key Takeaways

### Focused Improvements Over Restructuring

**Approach**: Rather than restructuring the entire visual hierarchy, this plan focuses on targeted improvements to the slider component itself. Lambda is already displayed prominently in the slider and additionally in the summary panel — sufficient for a minimal UI.

### Implementation Principles Applied

1. **Surgical Changes**: Improve what needs improvement, leave what works alone
2. **Incremental Validation**: Test each phase before proceeding
3. **Industry Alignment**: Dual controls and educational tooltips match leading methodology-focused tools
4. **Accessibility First**: ARIA, keyboard, screen reader support throughout
5. **Performance Preserved**: Zero impact on <0.1s response requirement

### Portfolio Value Delivered

**For Technical Evaluators**:
- Tooltip explains mathematical methodology (max-flow min-cut, energy function)
- Dual control mode demonstrates attention to precision
- Links to Method tab for deeper dive

**For Curious Readers**:
- "What it does" section explains parameter effect in plain language
- Links to Story tab for context
- Progressive disclosure: depth available on demand

**For Explorers**:
- Improved visual symmetry (centered lambda value)
- Directional arrows aid understanding
- Wider slider (360px) improves precision

---

## Total Implementation Effort

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| **Phase 1** | Visual polish & precision | 1-1.5 hours |
| **Phase 2** | Educational enhancements | 3-4 hours |
| **Total** | Core improvements | **4-5.5 hours** |

This is significantly scoped down from the original research (which proposed 17-27 hours including visual hierarchy restructuring).

---

## Future Enhancements (Out of Scope)

### Advanced Educational Features
- Before/after preview thumbnails (requires pre-rendering map images)
- Guided exploration prompts (first-visit tooltip suggesting λ values to try)
- Advanced parameters section (show Lagrange multiplier μ)
- **Effort**: 4-8 hours

### Narrative Integration
- Lift `currentLambda` state to `App.tsx`
- Share state between MapTab and StoryTab
- Embed interactive slider in StoryTab narrative (Distill.pub pattern)
- **Effort**: 3-4 hours

### Analytics & Optimization
- Event tracking for slider engagement
- Heatmap analysis of lambda value distribution
- Conversion tracking: slider interaction → Method tab views
- **Effort**: 2-3 hours

**Recommendation**: Complete Phases 1-2 first, validate portfolio value, then prioritize future enhancements based on user feedback.
