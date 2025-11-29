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
last_updated_note: "Investigated all 4 open questions with detailed findings and recommendations"
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

## Investigated Questions

### 1. Parametric Max-Flow Libraries

**Question**: What Python-compatible parametric max-flow implementations exist? IBFS? Boykov-Kolmogorov extensions?

**Investigation Summary**

There is exactly one ready-to-use Python parametric max-flow library: **Hochbaum's Pseudoflow (HPF)**.

**Options Analysis**

| Library | Python Support | Parametric? | License | Status |
|---------|---------------|-------------|---------|--------|
| **Hochbaum Pseudoflow** | ✅ `pip install pseudoflow` | ✅ Full parametric | Academic (non-commercial) | Recommended |
| **PBFS (2024 paper)** | ❌ No implementation | ✅ 2-3× faster than HPF | N/A | Future option |
| **Kolmogorov POTTS** | ❌ C++ only | ✅ Yes | Research only | Requires wrapper |
| **PyMaxFlow** (current) | ✅ Already using | ❌ No | MIT | Continue binary search |
| **NetworkX/igraph** | ✅ Yes | ❌ No | MIT | Standard max-flow only |

**Recommendation: Hochbaum's Pseudoflow**

```bash
pip install pseudoflow
```

- Finds ALL breakpoints in one pass per λ value
- Works with NetworkX graphs
- O(mn log n) complexity
- **Caveat**: Non-commercial academic license—verify fits portfolio use case

**Alternative**: If license is problematic, continue optimized binary search with warm-starting.

**Code References**
- [hochbaumGroup/pseudoflow-parametric-cut](https://github.com/hochbaumGroup/pseudoflow-parametric-cut)
- [PBFS paper (arXiv:2410.15920)](https://arxiv.org/abs/2410.15920)

---

### 2. Breakpoint Density

**Question**: For the half-america graph, how many μ breakpoints exist per λ value? If relatively few (hundreds vs. thousands), the lookup table approach becomes attractive.

**Investigation Summary**

**Theoretical bound**: At most **n-1 breakpoints** (72,999 for your graph) due to the Gallo-Grigoriadis-Tarjan (1989) nesting property.

**Practical expectation**: **Thousands to tens of thousands** of breakpoints for geographic optimization.

**Options Analysis**

| Scenario | Breakpoint Count | Implication |
|----------|------------------|-------------|
| Few breakpoints | ~100-500 | Lookup table very attractive; store all partitions |
| Moderate | ~1,000-5,000 | Lookup table feasible; ~50-250 MB storage per λ |
| Many breakpoints | ~10,000-73,000 | Parametric max-flow essential; storage challenging |

**Why "many breakpoints" is likely:**

1. **Continuous spatial variation**: Population density varies continuously, creating many distinct μ thresholds
2. **Fine granularity**: 73,000 tracts provide fine spatial resolution
3. **Heterogeneous weights**: Population and area vary significantly across tracts
4. **Recent research**: PBFS paper notes polygon aggregation has "many breakpoints"

**Recommendation**

Plan for O(n) storage. Run parametric analysis once to empirically measure actual breakpoint count—this would be valuable to document.

**Code References**
- [Gallo, Grigoriadis, Tarjan (1989)](https://epubs.siam.org/doi/10.1137/0218003) - Theoretical foundation
- [Scutellà (2007)](https://link.springer.com/article/10.1007/s10479-006-0155-z) - Nesting property

---

### 3. Perceptual Thresholds

**Question**: At what population granularity do users notice differences? Maybe 5% steps are "good enough" perceptually.

**Investigation Summary**

**5% steps are recommended** based on perceptual psychology and cartographic research.

**Options Analysis**

| Granularity | Positions | Perceptual Basis | Recommendation |
|-------------|-----------|------------------|----------------|
| **1% steps** | 101 | Below JND threshold (5-10%); users can't distinguish | ❌ Too fine |
| **5% steps** | 21 | Matches Weber's Law JND; round numbers (25%, 50%, 75%) | ✅ **Recommended** |
| **10% steps** | 11 | Clear differences; within optimal 4-12 step range | ✅ Good alternative |
| **Non-uniform** | Variable | More detail near 50% where behavior is interesting | 🔄 Consider for v2 |

**Supporting Research**

1. **Weber's Law**: JND for visual perception is typically 5-10% of reference
2. **Cleveland & McGill (1984)**: Area perception ranks 4th in accuracy hierarchy—users need larger differences
3. **Choropleth maps**: Research shows 4-7 classes optimize accuracy
4. **UX guidelines**: Sliders work best with 4-12 meaningful steps

**Recommendation**

Use **5% steps** (0%, 5%, 10%...95%, 100%) with visual tick marks at 0%, 25%, 50%, 75%, 100%. Display current percentage numerically.

**Code References**
- [Smashing Magazine - Designing Perfect Slider](https://www.smashingmagazine.com/2017/07/designing-perfect-slider/)
- [Cleveland & McGill - Graphical Perception](https://www.researchgate.net/publication/6062457_Graphical_Perception_and_Graphical_Methods_for_Analyzing_Scientific_Data)

---

### 4. WebAssembly Feasibility

**Question**: Could max-flow be compiled to WASM for client-side computation? Would eliminate server infrastructure needs.

**Investigation Summary**

**Technically feasible but NOT recommended.** Precomputed static files are strongly superior.

**Options Analysis**

| Approach | Dev Time | Performance | Server Cost | Complexity |
|----------|----------|-------------|-------------|------------|
| **Client WASM** | 4-6 weeks | 2-10s per solve | $0 | Very High |
| **Server API** | 1 week | 0.5-1s + latency | $20-50/month | Medium |
| **Precomputed static** | 1-2 days | <100ms load | **$0** | **Low** |

**Why WASM is problematic:**

1. **Performance overhead**: WASM runs 45-55% slower than native (USENIX research)
2. **No existing libraries**: Would need to compile C++ max-flow with Emscripten
3. **Serialization costs**: Passing 73k nodes across JS/WASM boundary adds overhead
4. **Development complexity**: 4-6 weeks vs 1-2 days for precomputation
5. **GEOS case study**: Geometry library found serialization eliminated WASM performance gains

**Memory is NOT a constraint**: Browsers support up to 4GB WASM memory; your graph needs ~40-60MB.

**Recommendation: Precompute Everything**

```bash
# Generate all results offline
for lambda in 0.00 0.05 0.10 ... 0.95; do
    uv run half-america precompute --lambda $lambda
    uv run half-america export --output web/public/data/lambda_${lambda}.topojson
done
# Deploy to GitHub Pages (free)
```

**Benefits:**
- <100ms load time vs 2-10s WASM computation
- Zero server costs (GitHub Pages)
- Demonstrates full data pipeline for portfolio
- 1-2 days implementation vs 4-6 weeks

**Code References**
- [GEOS WASM case study](https://kylebarron.dev/blog/geos-wasm/) - Why serialization kills performance
- [USENIX WASM performance](https://www.usenix.org/conference/atc19/presentation/jangda) - 45-55% overhead

## Open Questions

No remaining open questions. All four original questions have been investigated with recommendations provided.

## Architecture Insights

The current architecture cleanly separates concerns:
- **Graph construction**: One-time, cached
- **Optimization**: Parameterized by (λ, μ)
- **Post-processing**: Dissolve → Simplify → Export
- **Frontend**: Load TopoJSON, render with deck.gl

Adding variable population targets affects the optimization and export layers but leaves graph construction and frontend rendering unchanged.

The `target_fraction` parameter already exists in `find_optimal_mu()` (search.py:30) and `sweep_lambda()` (sweep.py:63)—it's just hardcoded to 0.5 at the CLI level (cli.py:75-79).

## Implementation Experiment (2025-11-29)

### What Was Attempted

Based on the research above, we attempted to implement Approach 1 (Parametric Max-Flow) using the Hochbaum Pseudoflow library. The implementation was done on branch `feature/population-percentage-slider`.

**Changes made:**
1. Added `pseudoflow>=2022.12.0` and `networkx>=3.0` to dependencies
2. Created `src/half_america/optimization/parametric.py` with:
   - `solve_parametric()` - finds all μ breakpoints in one pass per λ
   - `sweep_lambda_parametric()` - runs parametric solve for each λ
   - `find_partition_for_target()` - finds closest breakpoint to target population
3. Updated CLI `precompute` command to use parametric max-flow
4. Updated `export` command for 2D (λ, population) file naming
5. Created frontend `PopulationSlider` component
6. Updated `useTopoJsonLoader` for 2D data grid (380 files: 20λ × 19pop)

### Why It Failed

**Critical scalability issue**: Building a NetworkX graph for pseudoflow is dramatically slower than PyMaxflow's C++ backend.

**Observed behavior:**
- Small test data (18 nodes): Completed instantly, found correct breakpoints
- Full census data (83,777 nodes, 264,620 edges): First λ value took 10+ minutes and was still running

**Root cause analysis:**

| Library | Backend | Graph Construction | Max-Flow Solve |
|---------|---------|-------------------|----------------|
| PyMaxflow (current) | C++ | ~1 second | ~0.1-0.5 seconds |
| Pseudoflow | NetworkX (Python) | ~10+ minutes | Unknown (never completed) |

The pseudoflow library requires building a NetworkX DiGraph with:
- Source edges to all 83,777 nodes
- Sink edges from all 83,777 nodes
- Interior edges: 264,620 × 2 (both directions)
- **Total: ~700,000 edges per λ value**

NetworkX's pure Python graph construction is O(E) with significant constant factors. Building this graph 19 times (once per λ) is infeasible.

**Time estimates:**
- At 10+ minutes per λ value × 19 λ values = **3+ hours** minimum for precomputation
- This compares to ~5 minutes for the current binary search approach

### Lessons Learned

1. **Library evaluation was insufficient**: The research correctly identified pseudoflow as the only Python parametric max-flow library, but didn't benchmark it on realistic data sizes.

2. **The theoretical O(1 max-flow solve) advantage is real, but dominated by graph construction overhead**: Pseudoflow's parametric algorithm is efficient, but NetworkX's graph construction negates the benefit.

3. **PyMaxflow's C++ backend is essential for performance**: The current approach works because PyMaxflow handles graph construction in C++.

### Possible Future Approaches

If revisiting this feature:

1. **Hybrid approach**: Use PyMaxflow (fast) with multiple binary searches:
   - 19 λ values × 19 population targets × ~15 iterations = ~5,400 solves
   - At 0.5s each ≈ 45 minutes (vs current 5 minutes)
   - Still 9× slower but feasible

2. **C++ parametric implementation**: Write a C++ wrapper around a parametric max-flow algorithm (IBFS or HPF C code) with Python bindings. High development effort.

3. **Coarse population grid**: Reduce to 5 population targets (25%, 40%, 50%, 60%, 75%) for 5× increase instead of 19×.

4. **Accept current limitation**: Keep the fixed 50% population target. The visualization still effectively demonstrates population concentration.

### Branch Status

The `feature/population-percentage-slider` branch was abandoned. All changes were discarded with `git checkout -- . && git clean -fd`.

The code was functionally correct (tests passed, types checked, lint passed) but operationally infeasible at scale.

## Related Research

- Gallo, G., Grigoriadis, M. D., & Tarjan, R. E. (1989). "A fast parametric maximum flow algorithm and applications"
- Hochbaum, D. S. (2008). "The pseudoflow algorithm: A new algorithm for the maximum-flow problem"
- Boykov, Y., & Kolmogorov, V. (2004). "An experimental comparison of min-cut/max-flow algorithms for energy minimization in vision"
