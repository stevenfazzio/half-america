---
date: 2025-11-21T12:00:00-05:00
researcher: Claude
git_commit: 9457ab29e72aa3bf33bbff6326780856b69b714c
branch: fix/lambda-unit-scaling
repository: half-america
topic: "Lambda parameter has no effect due to unit scaling mismatch"
tags: [research, bug, optimization, graph-cuts, normalization]
status: complete
last_updated: 2025-11-21
last_updated_by: Claude
---

# Research: Lambda Parameter Unit Scaling Bug

**Date**: 2025-11-21
**Researcher**: Claude
**Git Commit**: 9457ab29e72aa3bf33bbff6326780856b69b714c
**Branch**: fix/lambda-unit-scaling
**Repository**: half-america
**Issue**: [#1](https://github.com/stevenfazzio/half-america/issues/1)

## Research Question

Why does the lambda (λ) parameter have no effect on optimization results? The issue reports that λ=0.0 and λ=0.5 produce identical partitions, and λ=0.9 differs by only 258 tracts out of ~40,000.

## Summary

The root cause is a **unit mismatch** in the energy function. The boundary term is normalized by ρ (making it dimensionless, ~1-6 per tract), while the area term remains in square meters (~48 million per tract). This 8-order-of-magnitude difference renders the λ weighting meaningless.

**The fix**: Normalize both terms to comparable scales by dividing area by ρ².

## Detailed Findings

### 1. Energy Function Definition

From `METHODOLOGY.md:36` and `src/half_america/graph/network.py:19`:

```
E(X) = λ Σ(l_ij/ρ)|x_i - x_j| + (1-λ) Σ a_i x_i - μ Σ p_i x_i
       ↑ Boundary cost           ↑ Area cost      ↑ Population reward
```

### 2. Current Implementation

**Boundary term** (`network.py:46-51`):
```python
rho = attributes.rho
for i, j in edges:
    l_ij = attributes.edge_lengths[(i, j)]
    capacity = lambda_param * l_ij / rho  # Dimensionless!
```

**Area term** (`network.py:42`):
```python
sink_cap = (1 - lambda_param) * attributes.area[i]  # Square meters!
```

### 3. Characteristic Length Scale (ρ)

From `src/half_america/graph/boundary.py:19-32`:
```python
def compute_rho(gdf: gpd.GeoDataFrame) -> float:
    """ρ = median(√a_i) where a_i is tract area in square meters."""
    sqrt_areas = np.sqrt(gdf["area_sqm"].values)
    return float(np.median(sqrt_areas))
```

**Expected real-world value**: ~2,500 meters (2.5 km) based on `docs/API.md:63`

### 4. Quantified Scale Mismatch

For a typical census tract:
- **Tract area**: ~6.25 km² = 6,250,000 m² (based on ρ ≈ 2500m, so a ≈ ρ² ≈ 6.25×10⁶)
- **Edge length**: ~2,500 m (similar to ρ)
- **ρ**: ~2,500 m

| Term | Formula | Typical Value | Units |
|------|---------|---------------|-------|
| Boundary (per edge) | λ × l_ij / ρ | λ × 2500 / 2500 = **λ × 1** | dimensionless |
| Area (per tract) | (1-λ) × a_i | (1-λ) × 6,250,000 = **(1-λ) × 6.25M** | m² |

**Ratio**: boundary/area ≈ 1 / 6,250,000 ≈ **1.6 × 10⁻⁷**

The boundary term contributes ~0.00002% of the total cost. Changing λ from 0 to 0.9 has negligible effect because:
- At λ=0.0: cost = 0 + 6.25M = 6.25M
- At λ=0.9: cost = 0.9 + 0.625M = 0.625M (still dominated by area term's residual)

### 5. Why Binary Search Still Works

The binary search for μ still converges because μ scales the population term:
- `source_cap = mu * attributes.population[i]`
- Population values are ~1,000-8,000 per tract
- μ auto-scales based on `total_area / total_pop` (`search.py:134`)

The search finds μ that balances area cost vs population reward, but λ doesn't meaningfully participate in this balance.

### 6. Proposed Fix

**Option 1: Normalize area by ρ²** (recommended)
```python
# network.py:42
sink_cap = (1 - lambda_param) * attributes.area[i] / (attributes.rho ** 2)
```

This makes both terms dimensionless:
- Boundary: λ × l_ij / ρ → ~1 (dimensionless)
- Area: (1-λ) × a_i / ρ² → ~1 (dimensionless)

**Option 2: Scale boundary by ρ**
```python
# network.py:50
capacity = lambda_param * l_ij * rho  # Instead of l_ij / rho
```

This makes both terms in area units (m²), but is less intuitive.

### 7. Impact on Other Components

Files requiring changes:
1. `src/half_america/graph/network.py:42` - `build_flow_network()` sink_cap calculation
2. `src/half_america/graph/network.py:102` - `compute_energy()` area_cost calculation

Files requiring review:
3. `METHODOLOGY.md:36,57` - Update formulas to reflect normalization
4. `tests/test_optimization/test_correctness.py` - Energy function tests may need updating
5. `tests/test_graph/test_network.py` - Flow network tests

### 8. Verification Strategy

After fix, verify:
1. λ=0.0 vs λ=0.5 should produce **different** partitions
2. λ=0.9 should have significantly fewer single-tract islands than λ=0.0
3. Higher λ should produce smoother, more contiguous regions
4. Binary search should still converge to 50% population target

## Code References

- `src/half_america/graph/network.py:42` - Area cost calculation (bug location)
- `src/half_america/graph/network.py:50` - Boundary cost calculation (correctly normalized)
- `src/half_america/graph/network.py:102` - Energy function area term
- `src/half_america/graph/boundary.py:19-32` - ρ calculation
- `src/half_america/optimization/search.py:71-107` - Binary search loop

## Architecture Insights

The METHODOLOGY.md describes the intended behavior correctly - both terms should be dimensionless after normalization. The implementation diverged by only normalizing the boundary term.

The docstring in `network.py:19` shows the intended formula:
```
E(X) = λ Σ(l_ij/ρ)|x_i - x_j| + (1-λ) Σ a_i x_i - μ Σ p_i x_i
```

But METHODOLOGY.md Section 2.1 states: "This ensures both terms in the objective function are dimensionless." This implies area should also be normalized, but the formula as written doesn't show it.

## Open Questions

1. Should μ also be re-scaled after the fix? (Likely auto-handled by binary search bounds)
2. Should existing cached sweep results be invalidated?
3. Should the test fixtures be updated to use realistic scale ratios?
