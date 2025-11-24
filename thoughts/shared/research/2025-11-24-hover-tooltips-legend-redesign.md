---
date: 2025-11-24T10:00:00-08:00
researcher: Claude
git_commit: 3fd464909968cb2a517956f15891a423c3e3693a
branch: master
repository: half-america
topic: "Hover Tooltips and Legend Redesign - Stats Distribution Analysis"
tags: [research, ui, ux, legend, tooltips, statistics, personas]
status: complete
last_updated: 2025-11-24
last_updated_by: Claude
---

# Research: Hover Tooltips and Legend Redesign - Stats Distribution Analysis

**Date**: 2025-11-24T10:00:00-08:00
**Researcher**: Claude
**Git Commit**: 3fd464909968cb2a517956f15891a423c3e3693a
**Branch**: master
**Repository**: half-america

## Research Question

Re-evaluate the conclusions from the original UI style polish research (2025-11-23-ui-style-polish.md) regarding:
1. Add hover tooltips showing population, area, and density for selected regions
2. Redesign legend: prominently display population %, reorder metrics, improve formatting

Specifically: Consider user personas, the purpose each stat serves, and whether the original conclusions about legend vs tooltip placement are correct.

## Summary

The original research had a **critical oversight**: the project only has **aggregate statistics** (for all selected regions combined), not per-region statistics. This fundamentally changes the tooltip vs legend decision:

| Original Recommendation | Revised Recommendation |
|-------------------------|------------------------|
| Tooltips: Population, Area, Density | Tooltips: Visual highlight only (no text) |
| Legend: Current stats reordered | Legend: Add "% of US land area" as hero stat |

**Key Finding**: The legend is missing the second half of the core narrative. The Story tab says "half of Americans live in 1.1% of land" but the legend only shows population % (the "half"), not land area % (the "1.1%").

---

## The Data Constraint Problem

### What Stats Actually Exist?

The TopoJSON export (`src/half_america/postprocess/export.py:31-38`) includes:

| Property | Type | Scope | Description |
|----------|------|-------|-------------|
| `lambda_value` | float | Global | Surface tension parameter |
| `population_selected` | int | Aggregate | Population in ALL selected tracts |
| `total_population` | int | Reference | Total US population |
| `area_sqm` | float | Aggregate | Total area of ALL selected regions |
| `num_parts` | int | Aggregate | Count of disconnected regions |

**Critical Observation**: The geometry is a **single Feature** containing a MultiPolygon. Individual polygons within the MultiPolygon do NOT have separate statistics.

### What This Means for Tooltips

When a user hovers over Region A vs Region B:
- We know WHICH polygon they're hovering on (visual highlight works)
- We do NOT know Region A's population vs Region B's population
- We can only show the SAME aggregate stats regardless of which region is hovered

**This makes text tooltips confusing**: Hovering on NYC Metro would show "165 million people" - but that's not NYC's population, it's ALL selected regions combined.

---

## Stats Analysis by Purpose

### The Core Narrative

From the Story tab (`web/src/components/StoryTab.tsx:21-22`):
> "That's **165 million people** living in just **1.1% of the country's land area**"

This is a **two-part statistic**:
1. **Half the population** (165M / 331M ≈ 50%)
2. **Tiny fraction of land** (42,902 mi² / 3.8M mi² ≈ 1.1%)

### Current Legend vs Narrative

| Legend Stat | Purpose | Supports Core Narrative? |
|-------------|---------|--------------------------|
| Population % | "Half the population" | **Yes** (Hero Stat #1) |
| Area (mi²) | Absolute size | Weak (raw number lacks context) |
| Regions | Visual complexity context | Tangential |
| Area/Region | Average size | Low value (derived) |
| Lambda | Technical control | Technical users only |

**GAP IDENTIFIED**: "% of US Land Area" is the Hero Stat #2, but it's completely absent from the legend!

### Stat Purpose by Persona

| Stat | Explorer | Curious Reader | Technical Evaluator |
|------|----------|----------------|---------------------|
| **Population %** | "Half - that's the point!" | Key validation | Checks correctness |
| **Land Area %** | "Wow, 1.1%!" (shareable) | Reinforces narrative | Verifies claim |
| Area (absolute) | "Is that big?" | Context | Sanity check |
| Regions | "Why so many blobs?" | Understands fragmentation | Algorithm output |
| Area/Region | Confusing | Moderate interest | Algorithm insight |
| Lambda | Ignores | Learned from Story tab | Wants to see it |
| Density | "How crowded?" | Makes sense of the data | Sanity check |

---

## Revised Recommendations

### Legend Redesign

**Principle**: The legend should communicate the core narrative at a glance.

**Hero Section** (visually prominent):
```
┌─────────────────────────────┐
│   50%                       │  ← Large, bold
│   of U.S. Population        │  ← Label
├─────────────────────────────┤
│   1.1%                      │  ← Large, bold (NEW!)
│   of U.S. Land Area         │  ← Label
└─────────────────────────────┘
```

**Supporting Stats**:
```
│  Area: 42,902 mi²           │
│  Regions: 847               │
```

**Technical Stats** (collapsed or subdued):
```
│  λ = 0.50                   │  ← Smaller, dimmer
```

**Removed**:
- Area/Region (low value, derived stat that doesn't serve any persona well)

### Hover Tooltips

**Recommendation**: Keep the current approach of **visual highlight only, no text tooltip**.

**Rationale**:
1. No per-region stats exist to display
2. Showing aggregate stats on hover is misleading (implies region-specific data)
3. The original research (citing NYT Graphics) noted that few users interact with tooltips anyway
4. The deck.gl `autoHighlight: true` with `highlightColor` already works well

**Alternative if text tooltips are desired**: Don't show stats. Instead show:
```
┌───────────────────┐
│ Selected Region   │
│ (1 of 847)        │
└───────────────────┘
```
This acknowledges the hover without implying per-region data.

### Missing Data: What Would Be Needed for Per-Region Tooltips

If we wanted true per-region tooltips, we'd need to:
1. Modify `export.py` to output each region as a separate Feature (not MultiPolygon)
2. Calculate per-region stats during dissolution
3. Store: region population, region area, region density, region tract count
4. This is significant scope creep and not recommended for Phase 6

---

## Stats Inventory: What's Available vs What's Shown

### Currently Exported (5 fields)
| Field | Currently Displayed | Should Display |
|-------|---------------------|----------------|
| `population_selected` | Yes (as %) | Yes (hero stat) |
| `total_population` | Implicitly (for %) | Implicitly |
| `area_sqm` | Yes (as mi²) | Yes + as % |
| `num_parts` | Yes | Yes |
| `lambda_value` | Yes | Yes (de-emphasized) |

### Available but NOT Exported (could add)
| Field | Worth Adding? | Rationale |
|-------|--------------|-----------|
| `total_area` | **Yes** | Required to calculate "% of US land" |
| `num_tracts` | No | Implementation detail |
| `mu` | No | Algorithm internals |
| `flow_value` | No | Algorithm internals |
| `iterations` | No | Algorithm internals |

**Minimum Change Required**: Export `total_area` to calculate `area_sqm / total_area * 100` = "1.1%"

---

## Implementation Implications

### To Add "% of US Land Area" to Legend

**Backend Change** (`src/half_america/postprocess/export.py`):
```python
@dataclass
class ExportMetadata:
    # ... existing fields ...
    total_area_sqm: float  # NEW: total area of all tracts
```

**Frontend Change** (`web/src/components/SummaryPanel.tsx`):
```typescript
const areaPercent = ((props.area_sqm / props.total_area_sqm) * 100).toFixed(1);
// Display: "1.1% of U.S. Land Area"
```

### Legend Visual Redesign

CSS changes to `SummaryPanel.css`:
- Create `.hero-stat` class with larger font (24-32px)
- Create `.supporting-stat` class with current sizing
- Create `.technical-stat` class with smaller, dimmer styling

---

## Comparison with Original Research

### Where Original Research Was Correct

1. **Tooltip content priority** (Population > Area > Density) - Correct ordering IF we had per-region stats
2. **Skip tract count, perimeter** - Correct, these are implementation details
3. **Legend format** ("42,902 mi²" not "Area (mi²): 42,902") - Correct
4. **Population % as visually prominent** - Correct
5. **Fixed Summary Panel + Hover Highlight pattern** - Correct

### Where Original Research Missed the Mark

1. **Assumed per-region tooltip data exists** - It doesn't
2. **Didn't identify "% of land area" as missing hero stat** - Critical oversight
3. **Area/Region retained** - Should be removed (low value)
4. **Didn't deeply consider data structure constraint** - MultiPolygon ≠ per-region stats

---

## Final Recommendations Summary

| Item | Recommendation | Priority |
|------|----------------|----------|
| Add "% of US Land Area" to legend | **High** - Missing hero stat | P0 |
| Make Population % and Land Area % visually prominent | High - Story emphasis | P1 |
| Remove Area/Region stat | Medium - Low value | P2 |
| De-emphasize Lambda in legend | Low - Technical detail | P3 |
| Keep hover as visual-only (no text tooltip) | Keep current approach | - |
| Add per-region stats to export | **Not recommended** - Scope creep | - |

---

## Code References

- `web/src/components/SummaryPanel.tsx:4-10` - HalfAmericaProperties interface
- `web/src/components/SummaryPanel.tsx:33-54` - Current stats display
- `web/src/components/StoryTab.tsx:21-22` - Core narrative stats
- `src/half_america/postprocess/export.py:31-38` - ExportMetadata definition
- `src/half_america/postprocess/dissolve.py:13-21` - DissolveResult (has total_area_sqm)

---

## Related Research

- [2025-11-23-ui-style-polish.md](2025-11-23-ui-style-polish.md) - Original UI research
- [2025-11-23-user-personas-and-stories.md](2025-11-23-user-personas-and-stories.md) - User personas

---

## Open Questions

1. **Density stat**: Is `population / area` worth showing in legend? It reinforces concentration but is derivable.
RESPONSE: I don't think it adds much. We can remove it.
2. **Region numbering on hover**: If we add text tooltips, would "Region 3 of 847" be useful or confusing?
RESPONSE: Confusing and useless
3. **Mobile tooltip behavior**: deck.gl hover is problematic on touch - tap-to-reveal or skip entirely?
