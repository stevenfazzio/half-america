---
date: 2025-11-21T21:00:00-08:00
researcher: Claude
git_commit: 10bda85d34b1262c51892eeb54e5e2f9bf69f612
branch: master
repository: half_america
topic: "Why λ=1.0 Fails to Converge: Lagrangian Relaxation Breakdown"
tags: [research, codebase, optimization, lambda, edge-cases, max-flow, convergence, bug-analysis]
status: complete
last_updated: 2025-11-21
last_updated_by: Claude
---

# Research: Why λ=1.0 Fails to Converge

**Date**: 2025-11-21T21:00:00-08:00
**Researcher**: Claude
**Git Commit**: 10bda85d34b1262c51892eeb54e5e2f9bf69f612
**Branch**: master
**Repository**: half_america

## Research Question

The previous research document `2025-11-21-lambda-edge-cases.md` concluded that "no special handling is required" for λ=1.0, and that "binary search prevents degenerate solutions." However, running `uv run half-america precompute` shows:

```
λ=1.0: 100.00% pop, μ=0.000000, 50 iters
WARNING: λ=1.0 did not converge
```

Why does λ=1.0 select 100% of the population regardless of μ, and why can't the binary search find 50%?

## Summary

**The previous research was incorrect.** The Lagrangian relaxation formulation fundamentally breaks down at λ=1.0 because:

1. At λ=1, the sink capacity (area cost) is zero: `(1-λ) × area = 0`
2. With no area cost, there's no penalty for selecting tracts
3. Selecting ALL tracts has zero boundary cost (no internal cuts)
4. Therefore, selecting 100% is always optimal for ANY μ ≥ 0
5. Binary search cannot find 50% because the cost function is flat

**The question "minimize perimeter subject to 50% population" IS well-defined mathematically, but our max-flow formulation cannot solve it at λ=1.**

## Detailed Findings

### 1. Edge Capacity Analysis at λ=1

From `src/half_america/graph/network.py:40-51`:

| Edge Type | Formula | Value at λ=1 |
|-----------|---------|--------------|
| Source → Node | `μ × population[i]` | `μ × p_i` |
| Node → Sink | `(1-λ) × area[i]` | **0** |
| Node ↔ Node | `λ × l_ij / ρ` | `l_ij / ρ` |

**Critical observation:** The sink capacity is **always zero** at λ=1, regardless of μ.

### 2. Why 100% Selection is Always Optimal

Consider the cost of different partitions at λ=1:

**Select everything (100%):**
- Boundary cuts = 0 (no n-links cut when all nodes selected)
- Sink cuts = 0 (sink capacity is 0)
- Source cuts = 0 (all nodes connected to source)
- **Total cost = 0**

**Select 50%:**
- Boundary cuts > 0 (must cut some n-links to separate selected/unselected)
- Sink cuts = 0 (sink capacity is 0)
- Source cuts = some value (unselected nodes cut from source)
- **Total cost > 0**

Since selecting 100% has strictly lower cost than any proper subset, the min-cut algorithm always selects everything at λ=1.

### 3. Why Binary Search Cannot Help

The binary search algorithm (`src/half_america/optimization/search.py:71-107`) works by:
1. If population too high → decrease μ
2. If population too low → increase μ

At λ=1:
- For ANY μ > 0: 100% population selected (optimal to select all)
- Binary search keeps decreasing μ toward 0
- Even at μ ≈ 0: Still 100% selected (no incentive to exclude)

The search exhausts 50 iterations without finding 50% because the function is flat at 100% for all μ values.

### 4. Mathematical Analysis

The energy function from `METHODOLOGY.md:31-41`:

```
E(X) = λ Σ(l_ij/ρ)|x_i - x_j| + (1-λ) Σ a_i x_i - μ Σ p_i x_i
```

At λ=1:
```
E(X) = Σ(l_ij/ρ)|x_i - x_j| - μ Σ p_i x_i
     = perimeter - μ × population
```

For the "select all" solution:
- perimeter = 0 (no internal boundaries)
- population = total_pop
- **E(X_all) = -μ × total_pop**

For any 50% solution:
- perimeter > 0 (some boundary required)
- population = 0.5 × total_pop
- **E(X_50%) = perimeter - 0.5 × μ × total_pop**

The condition for 50% to be better than 100%:
```
perimeter - 0.5μP < -μP
perimeter < -0.5μP
```

This is **impossible** since perimeter ≥ 0 and μ ≥ 0.

**Conclusion:** Selecting 100% is ALWAYS optimal at λ=1 for any non-negative μ.

### 5. Why the Previous Research Was Wrong

The research document `2025-11-21-lambda-edge-cases.md` claimed:

> "The nested optimization strategy (binary search on μ for each λ) prevents trivial solutions"

This is true for λ < 1, where the area term `(1-λ) × area` provides a penalty for selection. But at λ=1:
- Area penalty = 0
- No force pushing nodes toward the sink
- Binary search cannot balance anything

The research also claimed:

> "selected population is monotonic with respect to μ"

This is technically true, but misleading. At λ=1, population is:
- 100% for all μ > 0
- Either 0% or 100% at μ = 0 (degenerate)

The "monotonicity" is trivially satisfied but useless for finding 50%.

### 6. Is "Minimize Perimeter at 50% Pop" Solvable?

Yes, but not with our current formulation. The problem:

> "Find the set of tracts containing 50% population that minimizes total boundary perimeter"

is a valid combinatorial optimization problem (related to minimum perimeter polygons). However:

1. **Lagrangian relaxation requires a tradeoff.** Our formulation uses:
   - Area term: incentive to NOT select
   - Population term: incentive to select
   - Perimeter term: incentive for compactness

   At λ=1, the area incentive is zero, breaking the tradeoff.

2. **Hard constraints vs soft constraints.** Our approach relaxes the 50% constraint into the objective via μ. A different approach would enforce it as a hard constraint.

3. **Alternative formulations exist** but would require significant algorithm changes (e.g., constrained min-cut, submodular optimization with cardinality constraints).

## Code References

- `src/half_america/graph/network.py:40-43` - Terminal edge capacity calculations
- `src/half_america/graph/network.py:47-51` - N-link edge capacity calculations
- `src/half_america/optimization/search.py:103-107` - Binary search step logic
- `src/half_america/optimization/search.py:122-135` - μ_max estimation
- `METHODOLOGY.md:31-41` - Energy function definition

## Recommendations

### Option 1: Document λ=1 as Invalid (Simplest)

Add documentation and validation that λ=1.0 is not a meaningful input:
- The question "minimize perimeter with no area penalty" leads to trivial solutions
- Valid λ range should be [0, 1) not [0, 1]

### Option 2: Cap λ at 0.99 (Pragmatic)

Use `lambda_param = min(lambda_param, 0.99)` to ensure a small area penalty always exists. The visual difference between λ=0.99 and λ=1.0 is negligible.

### Option 3: Add Epsilon to Sink Capacity (Mathematically Cleaner)

```python
sink_cap = max((1 - lambda_param) * area[i], epsilon * area[i])
```

This ensures some area penalty exists even at λ=1, allowing binary search to function.

### Option 4: Alternative Formulation (Future Work)

Implement a constrained optimization approach that enforces 50% population as a hard constraint rather than Lagrangian relaxation. This is a significant undertaking.

## Historical Context

- `thoughts/shared/research/2025-11-21-lambda-edge-cases.md` - Previous (incorrect) analysis claiming no special handling needed
- The test in `tests/test_optimization/test_search.py:100-110` already noted: "May or may not converge - at λ=1, behavior is edge-dominated"

## Open Questions

1. Should we update the valid λ range from [0, 1] to [0, 1)?
RESPONSE: Yes, this sounds like the right approach, at least for now.
2. Is there value in implementing Option 3 (epsilon sink capacity) for completeness?
RESPONSE: It seems like we don't need this if we set the valid λ to [0, 1). I could be convinced otherwise, though, if there's a good arguement for implementing it regardless.
3. Should we update the METHODOLOGY.md to explain this limitation?
RESPONSE: Yet.

## Related Research

- [Lambda Edge Cases](2025-11-21-lambda-edge-cases.md) - Previous research (partially superseded)
- [Phase 3 Optimization Engine](2025-11-21-phase3-optimization-engine.md) - Overall optimization implementation
