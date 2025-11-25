---
date: 2025-11-25T12:00:00-05:00
researcher: Claude
git_commit: 9fe6122196ee5bd7f7979456cb56e2d274117d15
branch: master
repository: stevenfazzio/half-america
topic: "Geographic Scope Validation and Disclaimer Implementation"
tags: [research, geographic-scope, disclaimers, contiguous-us, ui-text]
status: complete
last_updated: 2025-11-25
last_updated_by: Claude
last_updated_note: "Corrected algorithm analysis - disconnected subgraphs would work fine"
---

# Research: Geographic Scope Validation and Disclaimer Implementation

**Date**: 2025-11-25
**Researcher**: Claude
**Git Commit**: 9fe6122196ee5bd7f7979456cb56e2d274117d15
**Branch**: master
**Repository**: stevenfazzio/half-america

## Research Question

The visualization refers to "America" and the "US Land Area", as well as to "Americans" and the "U.S. Population". Validate whether these terms accurately reflect the implemented geographic scope. Determine if language or implementation needs updating, and design disclaimers for both summary panel (short infobox) and Method tab (full treatment).

## Summary

**Finding: The terminology is technically inaccurate.**

The implementation explicitly limits data to the **contiguous United States only** (48 states + DC), excluding:
- Alaska (FIPS 02)
- Hawaii (FIPS 15)
- Puerto Rico (FIPS 72)
- All other US territories

However, the UI text uses terms like "America," "Americans," "U.S. Population," and "U.S. Land Area" without qualification—implying the full United States is represented.

**Recommendation**: Update language AND add disclaimers. The current terminology is misleading; disclaimers alone would feel like fine-print corrections to incorrect claims.

## Detailed Findings

### 1. Data Pipeline Geographic Scope

The geographic filtering occurs at data ingestion via a whitelist constant:

**[`src/half_america/data/constants.py:5-55`](https://github.com/stevenfazzio/half-america/blob/9fe6122196ee5bd7f7979456cb56e2d274117d15/src/half_america/data/constants.py#L5-L55)**
```python
# Contiguous US FIPS codes (48 states + DC = 49)
# Excludes: Alaska (02), Hawaii (15), territories
CONTIGUOUS_US_FIPS: list[str] = [
    "01",  # Alabama
    # ... 49 total FIPS codes
    "56",  # Wyoming
]
```

This constant is used in all data fetching:
- **TIGER downloads**: [`tiger.py:69`](https://github.com/stevenfazzio/half-america/blob/9fe6122196ee5bd7f7979456cb56e2d274117d15/src/half_america/data/tiger.py#L69)
- **Census population**: [`census.py:105`](https://github.com/stevenfazzio/half-america/blob/9fe6122196ee5bd7f7979456cb56e2d274117d15/src/half_america/data/census.py#L105)
- **Data pipeline**: [`pipeline.py:75`](https://github.com/stevenfazzio/half-america/blob/9fe6122196ee5bd7f7979456cb56e2d274117d15/src/half_america/data/pipeline.py#L75)

**Projection choice confirms intent**: The `TARGET_CRS = "EPSG:5070"` (Albers Equal Area) projection is specifically designed for the contiguous US and would distort Alaska/Hawaii.

### 2. UI Text Audit

| Location | Current Text | Issue |
|----------|--------------|-------|
| `StoryTab.tsx:12` | "Half of America" | Ambiguous |
| `StoryTab.tsx:13` | "Where do half of all Americans actually live?" | Implies all Americans |
| `StoryTab.tsx:21` | "Half of the United States population" | Inaccurate (excludes ~4.8M people) |
| `SummaryPanel.tsx:41` | "of U.S. Population" | Inaccurate |
| `SummaryPanel.tsx:45` | "of U.S. Land Area" | Inaccurate (excludes ~680K mi²) |
| `MapTitle.tsx:7` | "Where 50% of Americans live" | Implies all Americans |

**No existing disclaimers** were found anywhere in the codebase.

### 3. Scale of the Discrepancy

| Metric | Contiguous US | Excluded Areas | % Excluded |
|--------|---------------|----------------|------------|
| Population | ~328M | ~4.8M (AK+HI+PR+territories) | ~1.5% |
| Land Area | ~3.12M mi² | ~680K mi² (AK alone: ~665K) | ~18% |

The population discrepancy is small (~1.5%), but the land area discrepancy is substantial (~18%) due to Alaska's size. This affects the "% of land area" statistic meaningfully.

### 4. Existing Info Icon Pattern

The `LambdaSlider` component demonstrates a working tooltip pattern:

**[`LambdaSlider.tsx:27-71`](https://github.com/stevenfazzio/half-america/blob/9fe6122196ee5bd7f7979456cb56e2d274117d15/web/src/components/LambdaSlider.tsx#L27-L71)**
```tsx
<button
  type="button"
  className="info-icon"
  aria-label="What is surface tension? Click for details"
  onMouseEnter={() => setShowTooltip(true)}
  onMouseLeave={() => setShowTooltip(false)}
  onClick={() => setShowTooltip(!showTooltip)}
  // ...
>
  <span className="icon" aria-hidden="true">ⓘ</span>
</button>

{showTooltip && (
  <div className="lambda-tooltip" role="tooltip">
    {/* Multi-section content */}
  </div>
)}
```

This pattern can be replicated for the summary panel disclaimer.

### 5. Method Tab Structure

The Method tab (`MethodTab.tsx`) has these sections:
1. Header + hook paragraph
2. Objective function (equation hero box)
3. Variable definitions
4. Algorithm details
5. Data sources
6. Post-processing
7. Implementation stack
8. Navigation links

**Gap**: No "Scope & Limitations" or "Data Coverage" section exists.

## Proposed Changes

### A. Update UI Language

Replace ambiguous terms with accurate ones:

| Current | Proposed |
|---------|----------|
| "of U.S. Population" | "of Contiguous U.S. Population" |
| "of U.S. Land Area" | "of Contiguous U.S. Land Area" |
| "Half of the United States population" | "Half of the contiguous United States population" |
| "Where 50% of Americans live" | "Where 50% of the contiguous U.S. lives" |

**Keep "Half of America"** as the project title—it's catchy and the scope disclaimer handles accuracy.

### B. Summary Panel Info Icon (Short Disclaimer)

Add an info icon next to the summary title with tooltip:

**Proposed content:**
> **Geographic Scope**
>
> This visualization covers the contiguous United States only (48 states + DC).
>
> Alaska, Hawaii, Puerto Rico, and other US territories are excluded due to map projection
> and visualization constraints.
>
> *See the Method tab for details.*

### C. Method Tab Section (Full Treatment)

Add a new "Data Scope & Limitations" section after "Data Sources":

**Proposed content:**

```markdown
## Data Scope & Limitations

### Geographic Coverage
This analysis covers the **contiguous United States only**—the 48 states physically connected
on the North American mainland, plus the District of Columbia. This totals 49 jurisdictions
containing approximately:

- **328 million people** (~98.5% of US population)
- **3.12 million square miles** (~82% of US land area)

### Excluded Areas
The following are excluded:

- **Alaska** (FIPS 02) — ~733,000 people, ~665,000 mi²
- **Hawaii** (FIPS 15) — ~1.4 million people, ~10,900 mi²
- **Puerto Rico** (FIPS 72) — ~3.2 million people, ~3,500 mi²
- **Other territories** — Guam, USVI, American Samoa, CNMI, etc.

### Why Contiguous US Only?

1. **Projection**: The Albers Equal Area Conic projection (EPSG:5070) used for area calculations
   is optimized for the contiguous US. Including Alaska would introduce significant area distortion,
   and Hawaii would require a separate projection entirely.

2. **Visual Coherence**: The map visualization assumes a continuous landmass. Non-contiguous
   territories would require inset maps, adding complexity beyond the scope of this demonstration.

3. **Methodological Simplicity**: While the max-flow min-cut algorithm *would* work with
   non-contiguous regions (all nodes connect to source/sink terminals regardless of spatial
   adjacency), working with a connected landmass simplifies both implementation and interpretation.

### Terminology Note
When this visualization refers to "America," "Americans," or "U.S.," these terms specifically
mean the contiguous United States unless otherwise noted.
```

## Implementation Approach

### Phase 1: Language Updates
1. Update `SummaryPanel.tsx` labels
2. Update `StoryTab.tsx` text
3. Update `MapTitle.tsx` subtitle

### Phase 2: Summary Panel Info Icon
1. Add state management for tooltip visibility to `SummaryPanel.tsx`
2. Add info icon button next to title (reuse `.info-icon` pattern from `LambdaSlider`)
3. Add tooltip component with disclaimer content
4. Add CSS styles (can largely reuse from `LambdaSlider.css`)

### Phase 3: Method Tab Section
1. Add new "Data Scope & Limitations" section to `MethodTab.tsx`
2. Position after "Data Sources" section
3. Use existing `.section-card` styling for consistency

## Code References

- FIPS constant: `src/half_america/data/constants.py:5-55`
- TIGER download: `src/half_america/data/tiger.py:69`
- Census fetch: `src/half_america/data/census.py:105`
- Pipeline: `src/half_america/data/pipeline.py:75`
- SummaryPanel: `web/src/components/SummaryPanel.tsx:35-45`
- StoryTab: `web/src/components/StoryTab.tsx:12-26`
- MapTitle: `web/src/components/MapTitle.tsx:6-7`
- MethodTab: `web/src/components/MethodTab.tsx`
- LambdaSlider (tooltip pattern): `web/src/components/LambdaSlider.tsx:27-71`
- LambdaSlider CSS: `web/src/components/LambdaSlider.css:56-127`

## Architecture Insights

The geographic scope is enforced at the **data ingestion layer** via a whitelist pattern (`CONTIGUOUS_US_FIPS`). This is architecturally clean—expanding to include other territories would require:
1. Adding FIPS codes to the constant
2. Handling projection differently for non-contiguous regions (Alaska/Hawaii need different CRS)
3. Updating the visualization layer to handle inset maps or discontinuous display

**Note on algorithm compatibility**: The max-flow min-cut algorithm would work correctly with disconnected subgraphs. Each node connects to source (S) and sink (T) via terminal edges (t-links) regardless of spatial adjacency. Disconnected regions like Alaska would simply be decided independently based on their population reward vs. area cost tradeoff, without any boundary cost influence from the mainland. The λ (surface tension) parameter would still affect smoothing *within* Alaska among adjacent Alaskan tracts.

The UI layer has no geographic filtering logic; it displays whatever data is loaded.

## Open Questions

1. **Title change?** Should "Half of America" become "Half of the Contiguous US" or similar? Current recommendation is to keep the catchy title and use disclaimers.

2. **Population percentage accuracy**: The "50%" target is for the contiguous US population. Should the visualization state "50% of the contiguous U.S. population lives here" or is "50% of the population" acceptable given the disclaimer?

3. **Data year disclosure**: The Method tab should probably mention TIGER 2024 and ACS 2022 explicitly, not just "TIGER/Line Shapefiles and ACS 5-Year Estimates."

---

## Follow-up Research: Algorithm Analysis Correction

**Date**: 2025-11-25
**Prompted by**: User question about disconnected subgraph handling

### Original Claim (Incorrect)
The initial research stated that "spatial connectivity" was a reason for excluding Alaska/Hawaii because "the max-flow min-cut algorithm operates on spatially adjacent regions" and disconnected regions would create problems.

### Investigation
Reviewed the actual implementation in `src/half_america/graph/network.py`:

```python
# Terminal edges (t-links) - EVERY node connects to source and sink
for i in range(num_nodes):
    source_cap = mu * attributes.population[i]           # Population reward
    sink_cap = (1 - lambda_param) * attributes.area[i]   # Area cost
    g.add_tedge(i, source_cap, sink_cap)

# Neighborhood edges (n-links) - only adjacent nodes
for i, j in edges:
    capacity = lambda_param * l_ij / rho                 # Boundary cost
    g.add_edge(i, j, capacity, capacity)
```

### Corrected Understanding
The algorithm **would work correctly** with disconnected subgraphs because:

1. **Graph connectivity via terminals**: All nodes connect to source (S) and sink (T) via t-links, maintaining overall graph connectivity regardless of spatial adjacency.

2. **Independent decisions for isolated regions**: Alaska/Hawaii tracts would be included or excluded based purely on their `population_reward - area_cost` balance, with no boundary cost influence from the mainland.

3. **Internal smoothing still applies**: The λ parameter would still affect boundary costs *within* Alaska (among adjacent Alaskan tracts).

### Practical Implications
If Alaska were included:
- Its tracts would likely be entirely excluded at most λ values (huge area cost, relatively small population reward)
- The surface tension parameter wouldn't create any preference to "connect" Alaska to the mainland
- It would essentially be an independent optimization subproblem sharing the same μ

### Updated Rationale
The valid reasons for contiguous-US-only are:
1. **Projection** (EPSG:5070 distorts Alaska significantly)
2. **Visualization** (inset maps add complexity)
3. **Methodological simplicity** (simpler to interpret a connected landmass)

The algorithm limitation claim was **incorrect** and has been removed from the proposed disclaimer content.
