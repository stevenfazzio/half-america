---
date: 2025-11-24T01:30:00-05:00
researcher: Claude
git_commit: c3ce794b9fcaa2031fac428f179d2329c0d01ef4
branch: master
repository: half-america
topic: "Slider Endpoint Labels Implementation Research"
tags: [research, ui, ux, slider, labels, lambda, terminology]
status: complete
last_updated: 2025-11-24
last_updated_by: Claude
last_updated_note: "Added follow-up research on alternative label terminology"
---

# Research: Slider Endpoint Labels

**Date**: 2025-11-24T01:30:00-05:00
**Researcher**: Claude
**Git Commit**: 45cd68c549aed0c58c0124b43680a8f9fafae3f5
**Branch**: master
**Repository**: half-america

## Research Question

How to implement slider endpoint labels ("Fragmented" and "Smooth") to encourage user exploration, as specified in ROADMAP.md Phase 6 and item 2 of `thoughts/shared/research/2025-11-23-ui-style-polish.md`.

## Summary

The implementation is straightforward. The LambdaSlider component needs:
1. A new `.slider-endpoints` div with two span labels below the slider track
2. CSS using `justify-content: space-between` to position labels at extremes
3. Styling consistent with existing `.lambda-hint` (12px, 70% opacity white)

**Estimated effort**: 15-20 minutes

## Detailed Findings

### Current LambdaSlider Structure

**File**: `web/src/components/LambdaSlider.tsx`

```tsx
<div className="lambda-slider">
  <label htmlFor="lambda-slider" className="lambda-label">
    Surface Tension (λ)
  </label>
  <div className="slider-container">
    <input type="range" ... />
    <span className="lambda-value">{value.toFixed(2)}</span>
  </div>
  <p className="lambda-hint">
    {value < 0.3 ? 'Minimizes area (more fragmented)' :
     value > 0.7 ? 'Minimizes perimeter (smoother shapes)' :
     'Balanced optimization'}
  </p>
</div>
```

### Recommended Implementation

#### 1. Add Endpoint Labels Row (LambdaSlider.tsx)

Insert between `.slider-container` and `.lambda-hint`:

```tsx
<div className="slider-container">
  <input type="range" ... />
  <span className="lambda-value">{value.toFixed(2)}</span>
</div>
<div className="slider-endpoints">
  <span>Fragmented</span>
  <span>Smooth</span>
</div>
<p className="lambda-hint">
  ...
</p>
```

#### 2. Add CSS Styling (LambdaSlider.css)

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

**Design rationale**:
- `justify-content: space-between` pushes labels to left/right edges (existing pattern from `SummaryPanel.css:40`)
- `font-size: 11px` - slightly smaller than hint text (12px) to create hierarchy
- `color: rgba(255, 255, 255, 0.5)` - more subtle than hint (0.7) since labels are static context, not dynamic information
- `margin-top: 4px` - tight coupling to slider track
- `padding: 0 2px` - slight inset to align with track edges

### Alternative: Labels Inline with Slider

Could also place labels inline with the slider itself:

```tsx
<div className="slider-container">
  <span className="slider-endpoint-left">Fragmented</span>
  <input type="range" ... />
  <span className="slider-endpoint-right">Smooth</span>
  <span className="lambda-value">{value.toFixed(2)}</span>
</div>
```

**Rejected** because:
- Makes the slider row too wide/crowded
- Labels would compete with the numeric value display
- Mobile layout would be problematic

### Existing Patterns Used

| Pattern | Source | Application |
|---------|--------|-------------|
| `justify-content: space-between` | `SummaryPanel.css:40` | Left/right positioning |
| `color: rgba(255, 255, 255, 0.7)` | Multiple components | Secondary text color |
| `font-size: 12px` | `LambdaSlider.css:89` | Small label size |
| Below-slider hints | `LambdaSlider.tsx:41-45` | Placement pattern |

### Mobile Considerations

The slider has mobile-specific styling at `@media (max-width: 767px)`:
- Positioned at bottom of screen
- Full-width layout

The endpoint labels should work without modification because:
- `justify-content: space-between` scales with container width
- No fixed widths that would break
- Text is short enough not to wrap

**Verify**: May want to slightly reduce font-size to 10px on mobile if space is tight.

## Code References

- `web/src/components/LambdaSlider.tsx:19-47` - Current component structure
- `web/src/components/LambdaSlider.tsx:41-45` - Existing dynamic hint logic
- `web/src/components/LambdaSlider.css:31-35` - Slider container flex layout
- `web/src/components/LambdaSlider.css:88-93` - Hint text styling
- `web/src/components/SummaryPanel.css:38-43` - Space-between pattern example

## Implementation Plan

### Phase 1: Add Endpoint Labels

1. **Edit `LambdaSlider.tsx`**: Add `.slider-endpoints` div with "Fragmented" and "Smooth" spans
2. **Edit `LambdaSlider.css`**: Add `.slider-endpoints` styling
3. **Verify**: Build succeeds, lint passes
4. **Manual test**: Labels visible at correct positions on desktop and mobile

### Success Criteria

- [ ] "Fragmented" label visible at left end of slider
- [ ] "Smooth" label visible at right end of slider
- [ ] Labels are subtle (don't compete with slider value)
- [ ] Works on both desktop and mobile layouts
- [ ] Build and lint pass

## Visual Mockup

```
Surface Tension (λ)

─────────────●───────────── 0.50
Fragmented                 Smooth

         Balanced optimization
```

## Related Research

- `thoughts/shared/research/2025-11-23-ui-style-polish.md` - Original design spec (item 2)
- Research sources cited: Material Design, Apple HIG, Carbon Design, Smashing Magazine

## Open Questions

None - implementation is straightforward.

---

## Follow-up Research: Label Terminology Alternatives (2025-11-24)

### Question

Are "Fragmented" and "Smooth" the best word choices? The concern is that "Smooth" describes boundary quality rather than region characteristics, creating a category mismatch with "Fragmented."

### Terminology Currently Used in Codebase

| Context | λ=0 (area min) | λ→1 (perimeter min) |
|---------|----------------|---------------------|
| **CLAUDE.md** | "dusty map" | "smooth blobs" |
| **README.md** | "dusty", "tiny disconnected" | "smooth, compact blobs" |
| **LambdaSlider hint** | "more fragmented" | "smoother shapes" |
| **StoryTab** | "scattered dots" | "coherent shapes", "maximum smoothness" |
| **MethodTab** | — | "smooth boundaries" |
| **ROADMAP animation** | "dusty (λ=0)" | "smooth (λ=1)" |

**Key insight**: The codebase consistently uses "smooth" but pairs it differently:
- "smooth blobs" (regions)
- "smooth boundaries" (perimeter)
- "smoother shapes" (visual result)

### UX Best Practices for Slider Labels

Per Microsoft, Smashing Magazine, and Nielsen Norman Group:

1. **Single word preferred** - "Use only one word, if possible, for each label"
2. **True opposites** - Labels should be parallel and conceptually opposite
3. **Descriptive parallelism** - Both labels should describe the same category (regions, boundaries, or visual effect)

### The Parallelism Problem

"Fragmented" describes **regions** (broken into pieces), while "Smooth" describes **boundaries** (not jagged). This violates parallelism:

| Label | Describes |
|-------|-----------|
| Fragmented | Region distribution |
| Smooth | Boundary quality |

A user might ask: "Fragmented *what*? Smooth *what*?"

### Alternative Label Pairs

#### Option 1: Scattered / Consolidated (Recommended)

| Criterion | Score | Notes |
|-----------|-------|-------|
| Parallelism | ✓ | Both describe spatial distribution |
| Intuitive | ✓ | Immediately conveys meaning |
| Single word | ✓/✗ | "Consolidated" is 4 syllables |
| Geographic | ✓ | Common in urban planning |

**Visual**: `Scattered ──────●────── Consolidated`

#### Option 2: Fragmented / Compact

| Criterion | Score | Notes |
|-----------|-------|-------|
| Parallelism | ✓ | Both describe region character |
| Intuitive | ✓ | Clear opposition |
| Single word | ✓ | Both short |
| Geographic | ✓ | Established pair in political geography |

**Visual**: `Fragmented ──────●────── Compact`

**Note**: "Compact" already appears in README.md: "smooth, compact blobs"

#### Option 3: Scattered / Connected

| Criterion | Score | Notes |
|-----------|-------|-------|
| Parallelism | ✓ | Both describe connectivity |
| Intuitive | ✓ | Clear visual meaning |
| Single word | ✓ | Both short |
| Geographic | ✓ | Common terms |

**Visual**: `Scattered ──────●────── Connected`

#### Option 4: Many / Few (Simplest)

| Criterion | Score | Notes |
|-----------|-------|-------|
| Parallelism | ✓ | Both describe quantity |
| Intuitive | ✓ | Dead simple |
| Single word | ✓ | Minimal |
| Geographic | ✗ | Too generic |

**Visual**: `Many ──────●────── Few`

#### Option 5: Fine / Coarse (Resolution metaphor)

| Criterion | Score | Notes |
|-----------|-------|-------|
| Parallelism | ✓ | Both describe granularity |
| Intuitive | ✓ | Common in map generalization |
| Single word | ✓ | Both short |
| Geographic | ✓ | Used in cartography |

**Visual**: `Fine ──────●────── Coarse`

### Keeping "Smooth" - Reframing Options

If "Smooth" is preferred for consistency with existing terminology, the left label could be adjusted:

| Left | Right | Parallel Category |
|------|-------|-------------------|
| Jagged | Smooth | Boundary quality |
| Rough | Smooth | Visual texture |
| Sharp | Smooth | Shape character |

However, "Jagged/Rough/Sharp" don't accurately describe λ=0 behavior (many small regions).

### Recommendation

**Primary**: `Scattered` ↔ `Compact`
- Best balance of parallelism, intuitiveness, and brevity
- "Compact" already used in codebase ("smooth, compact blobs")
- Both describe the regions themselves

**Alternative**: `Fragmented` ↔ `Compact`
- Keeps "Fragmented" from original spec
- Fixes the parallelism issue
- Established geographic terminology pair

**Why not keep "Smooth"?**
- Violates parallelism principle
- Describes algorithm effect (perimeter) rather than visual result (regions)
- May confuse users expecting boundary quality to change

### Decision Matrix

| Pair | Parallelism | Intuitive | Brevity | Codebase Fit | Total |
|------|-------------|-----------|---------|--------------|-------|
| Scattered / Compact | ✓ | ✓ | ✓ | ✓ | 4/4 |
| Fragmented / Compact | ✓ | ✓ | ✓ | ✓ | 4/4 |
| Scattered / Connected | ✓ | ✓ | ✓ | ○ | 3.5/4 |
| Fragmented / Smooth | ✗ | ✓ | ✓ | ✓ | 3/4 |
| Fine / Coarse | ✓ | ○ | ✓ | ✗ | 2.5/4 |

### Sources

- Microsoft Slider Design Guidelines
- Smashing Magazine: Designing The Perfect Slider UX
- Nielsen Norman Group: Rating Scales in UX Research
- Semantic Differential research (bipolar adjective pairs)
- AP Human Geography: Compact vs Fragmented state morphology
