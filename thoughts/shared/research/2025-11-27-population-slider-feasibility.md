---
date: 2025-11-27T12:00:00-08:00
researcher: Claude
git_commit: 98d45991a12114f1a5117f04630cc5c6334d536e
branch: master
repository: stevenfazzio/half-america
topic: "Computational feasibility of variable population percentage slider"
tags: [research, optimization, population-slider, parametric-maxflow, computational-complexity]
status: complete
last_updated: 2025-11-27
last_updated_by: Claude
---

# Research: Computational Feasibility of Population Percentage Slider

**Date**: 2025-11-27T12:00:00-08:00
**Researcher**: Claude
**Git Commit**: 98d45991a12114f1a5117f04630cc5c6334d536e
**Branch**: master
**Repository**: stevenfazzio/half-america

## Research Question

Suppose I wanted to add a slider so that the user could adjust the 50% of the population parameter. How computationally feasible is this? Would it increase generation time by ~100x (since it would have to run for each population percentage 0% to 100%)? Or is there an opportunity to be more clever about it?

## Summary

**Short Answer**: Yes, naive implementation would increase computation by ~100×, but there are clever approaches that could reduce this significantly.

**Key Finding**: The current architecture performs binary search over the Lagrange multiplier μ to achieve 50% population for each λ value. The relationship between μ and population is monotonic—higher μ always yields more population. This monotonicity opens several optimization opportunities:

1. **Parametric max-flow** (most promising): Solve for ALL μ breakpoints in one pass per λ, yielding the complete curve of population vs. μ
2. **Coarse grid with interpolation**: Precompute 10-20 population targets instead of 100
3. **On-demand computation**: Only compute when user releases slider (requires server-side computation)

**Computational Impact**:
| Approach | Max-flow Solves | Relative Cost |
|----------|-----------------|---------------|
| Current (50% only) | ~150 | 1× |
| Naive (1% granularity) | ~15,000 | 100× |
| Coarse grid (10% steps) | ~1,500 | 10× |
| Parametric max-flow | ~10 (one per λ) | 0.07× |

## Detailed Findings

### Current Architecture: How 50% is Enforced

The optimization uses a **two-level nested strategy** (src/half_america/optimization/sweep.py:59-166):

**Outer Loop**: Sweep over λ (surface tension) values [0.0, 0.1, ..., 0.9]

**Inner Loop**: Binary search for μ (Lagrange multiplier) to hit 50% population

```
E(X) = λ Σ(l_ij/ρ)|x_i - x_j| + (1-λ) Σ(a_i/ρ²)x_i - μ Σ p_i x_i
       [Boundary Cost]        [Area Cost]           [Population Reward]
```

The μ term acts as a "reward per person"—higher μ incentivizes selecting more tracts, thus more population.

**Binary Search** (src/half_america/optimization/search.py:27-119):
- Starts with bounds [μ_min, μ_max]
- Tests midpoint: solve max-flow, check population
- If under target → increase μ_min; if over → decrease μ_max
- Converges in ~10-20 iterations per λ value

**Current Cost**:
- 10 λ values × ~15 iterations = ~150 max-flow solves
- Each solve: ~73,000 nodes × ~200,000 edges
- Total precomputation: parallelized across CPU cores, takes several minutes

### Why Variable Population Targets are Non-Trivial

**The Challenge**: Each (λ, population_target) pair requires finding a different μ value. The partition changes discretely as μ varies—you can't interpolate between partitions.

**Naive Approach** (1% population granularity):
```
10 λ values × 100 population targets × ~15 binary search iterations = ~15,000 max-flow solves
```
This is indeed ~100× more computation.

**File Size Impact**:
- Current: 100 TopoJSON files (one per 0.01 λ step) ≈ 100MB total
- Naive: 100 λ × 100 population = 10,000 files ≈ 10GB
- This would require rethinking delivery architecture

### Clever Approaches to Reduce Computation

#### Approach 1: Parametric Max-Flow (Most Promising)

**Insight**: For a fixed λ, as μ varies from 0 to ∞, the min-cut partition changes at discrete "breakpoints". Between breakpoints, the partition is constant.

**Parametric Max-Flow Algorithm**:
- Solve for all breakpoints in μ simultaneously
- Returns the complete piecewise-constant function: μ → partition
- Complexity: O(1 max-flow) + O(|breakpoints| × node count)

**Result**: For each λ, you get ALL possible partitions (and their population fractions) in roughly the time of one max-flow solve.

**Implementation**: Would require replacing PyMaxFlow with a parametric max-flow implementation. Libraries exist (e.g., IBFS with parametric extension, Boykov-Kolmogorov parametric variant).

**Estimated Improvement**: ~10 solves total (one parametric solve per λ) instead of 15,000 → **150× speedup** over naive.

**Reference**: Gallo, Grigoriadis, and Tarjan (1989) "A Fast Parametric Maximum Flow Algorithm and Applications"

#### Approach 2: Coarse Population Grid

**Insight**: Users may not need 1% granularity. Precompute at 10% increments (or 5%) and let the slider snap to nearest.

**Population Targets**: [10%, 20%, 30%, 40%, 50%, 60%, 70%, 80%, 90%]

**Computation**: 10 λ × 9 targets × ~15 iterations = ~1,350 solves (9× increase, not 100×)

**User Experience**: Less smooth, but much more feasible. Could display discrete population bands on the map.

#### Approach 3: μ-Population Lookup Table

**Insight**: The population fraction is a monotonic step function of μ. For each λ, precompute this curve by sampling μ values.

**Process**:
1. For each λ, sample μ at many values (e.g., 1000 logarithmically spaced points)
2. Record (μ, partition, population_fraction) tuples
3. Due to monotonicity, many μ values map to the same partition
4. Store unique partitions with their population ranges

**Tradeoff**: More precomputation than current (~10,000 solves), but captures the full population curve. Partitions can be deduplicated.

#### Approach 4: Server-Side On-Demand Computation

**Insight**: Don't precompute everything. Compute on user request.

**Architecture**:
- Frontend sends (λ, population_target) request
- Server runs binary search (~15 max-flow solves)
- Returns TopoJSON in real-time

**Latency**: Each max-flow on 73k nodes takes ~0.1-0.5 seconds. Binary search = ~2-8 seconds total latency.

**Pros**: No precomputation explosion, always accurate
**Cons**: Requires server infrastructure, latency on slider interaction, can't work offline

**Hybrid**: Precompute coarse grid (10% steps), compute on-demand for fine adjustments.

### Code Locations for Key Components

| Component | File | Lines |
|-----------|------|-------|
| Binary search for μ | src/half_america/optimization/search.py | 27-119 |
| Target tolerance (1%) | src/half_america/optimization/solver.py | 28 |
| Lambda sweep | src/half_america/optimization/sweep.py | 59-166 |
| Flow network construction | src/half_america/graph/network.py | 9-53 |
| Energy function | src/half_america/graph/network.py | 70-108 |
| CLI precompute command | src/half_america/cli.py | 53-83 |
| TopoJSON export | src/half_america/postprocess/export.py | 108-167 |

### Mathematical Structure Enabling Optimization

**Key Property**: Population is monotonically increasing with μ.

```python
# From tests/test_optimization/test_search.py:102-106
def test_higher_mu_more_selection(self, complex_graph_data):
    """Test that higher μ → more selection."""
    low = solve_partition(complex_graph_data, 0.5, mu=0.001, verbose=False)
    high = solve_partition(complex_graph_data, 0.5, mu=1.0, verbose=False)
    assert high.selected_population >= low.selected_population
```

This monotonicity is what makes binary search work, and also enables parametric approaches.

**Graph Structure is Reusable**: The adjacency graph (which tracts touch which) is constant. Only edge weights change with λ and μ. The graph data is cached at `data/cache/processed/graph_{TIGER_YEAR}_{ACS_YEAR}.pkl`.

## Recommendations

### For Portfolio/Demo Purposes

**Recommended**: Coarse grid approach (Approach 2)
- Precompute 10 λ × 10 population targets = 100 (λ, pop) combinations
- ~10× computation increase (manageable)
- ~10× file size increase (still reasonable at ~1GB)
- Clear UI with labeled population bands

### For Production/Research Quality

**Recommended**: Parametric max-flow (Approach 1)
- Requires library change from PyMaxFlow
- One-time implementation effort
- Results in ~150× speedup over naive
- Enables true continuous population slider
- Most elegant solution mathematically

### For Interactive Exploration

**Recommended**: Hybrid server-side (Approach 4)
- Precompute coarse grid for instant feedback
- Compute on-demand for precise values
- Best user experience
- Requires backend infrastructure

## Open Questions

1. **Parametric max-flow libraries**: What Python-compatible parametric max-flow implementations exist? IBFS? Boykov-Kolmogorov extensions?

2. **Breakpoint density**: For the half-america graph, how many μ breakpoints exist per λ value? If relatively few (hundreds vs. thousands), the lookup table approach becomes attractive.

3. **Perceptual thresholds**: At what population granularity do users notice differences? Maybe 5% steps are "good enough" perceptually.

4. **WebAssembly feasibility**: Could max-flow be compiled to WASM for client-side computation? Would eliminate server infrastructure needs.

## Architecture Insights

The current architecture cleanly separates concerns:
- **Graph construction**: One-time, cached
- **Optimization**: Parameterized by (λ, μ)
- **Post-processing**: Dissolve → Simplify → Export
- **Frontend**: Load TopoJSON, render with deck.gl

Adding variable population targets affects the optimization and export layers but leaves graph construction and frontend rendering unchanged.

The `target_fraction` parameter already exists in `find_optimal_mu()` (search.py:30) and `sweep_lambda()` (sweep.py:63)—it's just hardcoded to 0.5 at the CLI level (cli.py:75-79).

## Related Research

- Gallo, G., Grigoriadis, M. D., & Tarjan, R. E. (1989). "A fast parametric maximum flow algorithm and applications"
- Hochbaum, D. S. (2008). "The pseudoflow algorithm: A new algorithm for the maximum-flow problem"
- Boykov, Y., & Kolmogorov, V. (2004). "An experimental comparison of min-cut/max-flow algorithms for energy minimization in vision"
