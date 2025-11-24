---
date: 2025-11-23T14:00:00-08:00
researcher: Claude
git_commit: b2cb7201be47d6720cc3fb2180b3dcb281ea684f
branch: master
repository: half-america
topic: "Population Fraction Data Analysis: Why 82% of Values Are Below 50%"
tags: [research, optimization, population, bug, frontend, backend, data-mismatch]
status: complete
last_updated: 2025-11-23
last_updated_by: Claude
---

# Research: Population Fraction Data Analysis

**Date**: 2025-11-23T14:00:00-08:00
**Researcher**: Claude
**Git Commit**: b2cb7201be47d6720cc3fb2180b3dcb281ea684f
**Branch**: master
**Repository**: half-america

## Research Question

Why does the population fraction data show 81/99 lambda values (82%) below 50%, with a range of 48.59% to 50.45%? Is this a bug in the algorithm, or expected behavior?

## Summary

**ROOT CAUSE: Frontend/Backend Population Mismatch**

The displayed population percentages are systematically low because:

| Source | Total Population | Notes |
|--------|-----------------|-------|
| Frontend constant | 331,893,745 | Hardcoded in `SummaryPanel.tsx:17` |
| Backend tract data | 328,912,183 | Actual sum from Census tracts |
| **Difference** | **-2,981,562** | **-0.90%** |

This ~3 million person discrepancy causes ALL displayed percentages to be shifted down by approximately **0.45 percentage points**. When the backend correctly targets 50%, the frontend displays ~49.55%.

**Secondary Factor: Discretization Gap**

Even with corrected totals, the discrete nature of the graph cut algorithm means exact 50% solutions often don't exist. The algorithm converges to the nearest stable solution within the 1% tolerance band (49-51%).

## Detailed Findings

### 1. The Population Mismatch

**Frontend** (`web/src/components/SummaryPanel.tsx:16-17`):
```typescript
const US_TOTAL_POPULATION = 331_893_745;
```

This value likely comes from the official Census Bureau population estimate, which includes:
- All 50 states + DC
- Puerto Rico and territories (in some estimates)
- Group quarters populations

**Backend** (actual tract data):
```python
gdf["population"].sum()  # Returns 328,912,183
```

The tract-level data excludes:
- Non-geographic populations
- Tracts with zero population
- Potential data quality issues in ACS estimates
- Alaska/Hawaii tracts may have different coverage

**Impact Calculation**:
```
Backend targets: 50% of 328,912,183 = 164,456,092
Frontend displays: 164,456,092 / 331,893,745 = 49.55%
Systematic offset: -0.45%
```

### 2. Empirical Verification

Analysis of all 99 TopoJSON files confirms the pattern:

| Metric | Value |
|--------|-------|
| Values below 50% | 81 (82%) |
| Values at/above 50% | 18 (18%) |
| Minimum | 48.59% (λ=0.75) |
| Maximum | 50.45% (λ=0.91) |
| λ=0.50 | 49.87% |

If we correct for the 0.45% offset, the corrected distribution would be:
- Corrected minimum: ~49.04%
- Corrected maximum: ~50.90%
- Most values centered around 50%

### 3. The Binary Search Algorithm Is Correct

The algorithm in `src/half_america/optimization/search.py` is symmetric:

```python
# Binary search step (lines 103-107)
if result.selected_population < target_pop:
    mu_min = mu  # Need more selection
else:
    mu_max = mu  # Need less selection
```

- No explicit directional bias
- Uses midpoint: `mu = (mu_min + mu_max) / 2`
- Converges when `abs(error) <= pop_tolerance` (symmetric)
- Tolerance is 1% (±3.3M people)

### 4. Discretization Gap (Secondary Factor)

The max-flow min-cut algorithm produces **discrete** solutions. The population function P(μ) is a step function:

```
P(μ) = Σ p_i × x_i(μ)

where x_i(μ) ∈ {0, 1} (tract either selected or not)
```

This means:
1. Exact 50% may not exist as a valid partition
2. Adjacent stable solutions might be at 49.3% and 50.7%
3. The algorithm returns whichever first enters the tolerance band

### 5. High Lambda Anomaly (λ=0.98)

The data shows λ=0.98 has unusually low population (48.71%):

| Lambda | Population % | Notes |
|--------|-------------|-------|
| λ=0.95 | 49.07% | |
| λ=0.96 | 50.01% | |
| λ=0.97 | 50.26% | |
| λ=0.98 | **48.71%** | Anomalous drop |

This is near the λ=1.0 convergence failure threshold documented in `2025-11-21-lambda-one-convergence-failure.md`. At high λ, the area cost term `(1-λ)` becomes very small, making the optimization less stable.

## Code References

- `web/src/components/SummaryPanel.tsx:16-17` - Hardcoded US population constant
- `src/half_america/optimization/search.py:55-57` - Backend total population calculation
- `src/half_america/optimization/search.py:93` - Convergence check (symmetric)
- `src/half_america/optimization/solver.py:28` - TARGET_TOLERANCE = 0.01
- `src/half_america/data/census.py:70-73` - Population data ingestion

## Resolution Options

### Option 1: Fix Frontend Constant (Recommended)

Update `SummaryPanel.tsx` to use the actual tract population:

```typescript
// Option A: Hardcode the correct value
const US_TOTAL_POPULATION = 328_912_183;

// Option B: Include total in TopoJSON and read dynamically
const populationPercent = (props.population_selected / props.total_population) * 100;
```

**Pros**: Simple fix, accurate display
**Cons**: Hardcoded value could drift if tract data changes

### Option 2: Include Total in TopoJSON

Modify `export.py` to include `total_population` in the exported properties:

```python
gdf = gpd.GeoDataFrame({
    ...
    "total_population": [metadata.total_population],  # Add this
})
```

Then update frontend to use the dynamic value.

**Pros**: Self-consistent, no hardcoding
**Cons**: Requires re-export of all TopoJSON files

### Option 3: Bias Algorithm to 50.5%

Change the target fraction in the optimization:

```python
target_fraction: float = 0.505  # Instead of 0.5
```

**Pros**: Compensates for both mismatch and discretization
**Cons**: Masks the real issue, makes backend less accurate

### Option 4: Document as Expected Behavior

Add a note that displayed percentages may vary slightly from 50% due to:
- Data coverage differences
- Discrete optimization solutions

**Pros**: No code changes
**Cons**: Users may be confused by "Half of America" showing 49.x%

## Recommended Resolution

**Implement Option 2 (include total in TopoJSON)** for accuracy, with **Option 1 as a quick fix**.

1. **Immediate**: Update `SummaryPanel.tsx` to use `328_912_183`
2. **Follow-up**: Modify export to include `total_population` property
3. **Optional**: Cap slider at λ=0.97 to avoid the λ=0.98 anomaly

## Architecture Insights

The mismatch reveals a coupling issue:
- Backend uses **dynamic** total from tract data
- Frontend uses **static** constant from a different source
- These should be synchronized via the data pipeline

The TopoJSON export already includes `population_selected` (derived from backend). Including `total_population` would make the data self-consistent.

## Historical Context (from thoughts/)

- `thoughts/shared/research/2025-11-21-lambda-one-convergence-failure.md` - Documents why λ=1.0 fails
- `thoughts/shared/research/2025-11-21-binary-search-lagrange-multiplier.md` - Binary search algorithm design
- `thoughts/shared/research/2025-11-23-ui-style-polish.md` - Original issue documentation

## Related Research

- [Lambda One Convergence Failure](2025-11-21-lambda-one-convergence-failure.md)
- [Binary Search Lagrange Multiplier](2025-11-21-binary-search-lagrange-multiplier.md)
- [UI Style and Polish](2025-11-23-ui-style-polish.md)

## Open Questions

1. **Why is tract total lower?** Is it ACS methodology, excluded territories, or data quality?
2. **Should we re-target to 50.25%?** To center the display around 50% after correction?
3. **Is λ=0.98 salvageable?** Or should we cap at λ=0.97?
