# Lambda Unit Scaling Bug - Implementation Plan

## Overview

Fix the lambda parameter having no effect on optimization results due to a unit mismatch in the energy function. The boundary term is normalized by ρ (making it dimensionless, ~1), while the area term remains in square meters (~6 million), creating an 8-order-of-magnitude difference that renders λ weighting meaningless.

## Current State Analysis

### Bug Evidence
From sweep results, λ=0.0 and λ=0.5 produce **identical** partitions (2779 parts, 40134 tracts), and λ=0.9 differs by only 258 tracts.

### Root Cause
In `src/half_america/graph/network.py`:
- **Line 50**: Boundary cost normalized: `capacity = lambda_param * l_ij / rho` → ~1 (dimensionless)
- **Line 42**: Area cost unnormalized: `sink_cap = (1 - lambda_param) * attributes.area[i]` → ~6,250,000 m²

The ratio is ~1.6×10⁻⁷, making boundary cost contribute ~0.00002% of total cost.

### Key Discoveries:
- `src/half_america/graph/network.py:42` - Area cost bug location
- `src/half_america/graph/network.py:102` - Energy function area term (also needs fix)
- `METHODOLOGY.md:29` - States "both terms should be dimensionless" (correct intent, wrong implementation)
- Test fixtures use unrealistic scales (area=1000, rho=100, giving area/rho²=0.1 vs real ~1)

## Desired End State

After this fix:
1. λ=0.0 vs λ=0.5 should produce **visibly different** partitions
2. λ=0.9 should have significantly fewer single-tract islands than λ=0.0
3. Higher λ should produce smoother, more contiguous regions
4. Binary search should still converge to 50% population target

### Verification
Run a comparison script showing partition differences across λ values.

## What We're NOT Doing

- Not changing ρ calculation (it's correct)
- Not modifying binary search bounds (auto-handles via `total_area / total_pop`)
- Not updating test fixture values to realistic scales (they work fine with either normalization)
- Not migrating existing cached sweep results (will regenerate)

## Implementation Approach

Normalize the area term by ρ² to make it dimensionless, matching the boundary term. This is the minimal change that fixes the bug while maintaining mathematical consistency with METHODOLOGY.md.

---

## Phase 1: Fix Network Construction

### Overview
Normalize area costs in both flow network construction and energy calculation.

### Changes Required:

#### 1. Flow Network Construction
**File**: `src/half_america/graph/network.py`
**Changes**: Normalize sink_cap by ρ²

```python
# Line 42: Change from:
sink_cap = (1 - lambda_param) * attributes.area[i]

# To:
sink_cap = (1 - lambda_param) * attributes.area[i] / (attributes.rho ** 2)
```

#### 2. Energy Function Calculation
**File**: `src/half_america/graph/network.py`
**Changes**: Normalize area_cost by ρ² to match

```python
# Line 102: Change from:
area_cost = (1 - lambda_param) * attributes.area[partition].sum()

# To:
area_cost = (1 - lambda_param) * attributes.area[partition].sum() / (attributes.rho ** 2)
```

#### 3. Update Docstrings
**File**: `src/half_america/graph/network.py`
**Changes**: Update the energy function formula in docstrings (lines 18-19 and 80-81)

From:
```
E(X) = λ Σ(l_ij/ρ)|x_i - x_j| + (1-λ) Σ a_i x_i - μ Σ p_i x_i
```

To:
```
E(X) = λ Σ(l_ij/ρ)|x_i - x_j| + (1-λ) Σ (a_i/ρ²) x_i - μ Σ p_i x_i
```

### Success Criteria:

#### Automated Verification:
- [x] Unit tests pass: `uv run pytest tests/test_graph/test_network.py -v`
- [x] Type checking passes: `uv run mypy src/`
- [x] Linting passes: `uv run ruff check src/`

#### Manual Verification:
- [x] N/A for this phase

---

## Phase 2: Update Test Energy Expectations

### Overview
Update test cases that hardcode expected energy values to account for the new normalization.

### Changes Required:

#### 1. Update Energy Test Expectations
**File**: `tests/test_optimization/test_correctness.py`
**Changes**: Update `test_energy_for_full_partition` and `test_energy_boundary_term_only`

The test fixture uses: area=1000, rho=100, so area/ρ² = 1000/10000 = 0.1

In `test_energy_for_full_partition` (line 122-126):
```python
# OLD calculation:
# - area_cost = (1-0.5) * (1000+1000+1000) = 0.5 * 3000 = 1500
# - energy = 0 + 1500 - 600000 = -598500

# NEW calculation:
# - area_cost = (1-0.5) * 3000 / (100**2) = 0.5 * 3000 / 10000 = 0.15
# - energy = 0 + 0.15 - 600000 = -599999.85
expected_energy = 0.0 + 0.5 * 3000.0 / (100.0 ** 2) - 1000.0 * 600.0
```

In `test_energy_boundary_term_only` (line 141-145):
```python
# OLD calculation:
# - area_cost = 1.0 * 3000 = 3000
# - energy = 0 + 3000 - 600000 = -597000

# NEW calculation:
# - area_cost = 1.0 * 3000 / 10000 = 0.3
# - energy = 0 + 0.3 - 600000 = -599999.7
expected_energy = 0.0 + 1.0 * 3000.0 / (100.0 ** 2) - 1000.0 * 600.0
```

In `test_energy_manual_calculation_partial_selection` (line 180):
```python
# Update manual area_cost calculation
area_cost = (1 - 0.5) * attrs.area[partition].sum() / (attrs.rho ** 2)
```

### Success Criteria:

#### Automated Verification:
- [x] All correctness tests pass: `uv run pytest tests/test_optimization/test_correctness.py -v`
- [x] Full test suite passes: `uv run pytest`

#### Manual Verification:
- [x] N/A for this phase

---

## Phase 3: Update Documentation

### Overview
Update METHODOLOGY.md to reflect the correct formula with area normalization.

### Changes Required:

#### 1. Update Energy Function Formula
**File**: `METHODOLOGY.md`
**Changes**: Update line 36 to show normalized area term

From:
```
$$E(X) = \underbrace{\lambda \sum_{(i,j) \in N} \frac{l_{ij}}{\rho} \cdot |x_i - x_j|}_{\text{Boundary Cost}} + \underbrace{(1-\lambda) \sum_{i} a_i x_i}_{\text{Area Cost}} - \underbrace{\mu \sum_{i} p_i x_i}_{\text{Population Reward}}$$
```

To:
```
$$E(X) = \underbrace{\lambda \sum_{(i,j) \in N} \frac{l_{ij}}{\rho} \cdot |x_i - x_j|}_{\text{Boundary Cost}} + \underbrace{(1-\lambda) \sum_{i} \frac{a_i}{\rho^2} x_i}_{\text{Area Cost}} - \underbrace{\mu \sum_{i} p_i x_i}_{\text{Population Reward}}$$
```

#### 2. Update Terminal Edge Formula
**File**: `METHODOLOGY.md`
**Changes**: Update line 57 sink edge capacity formula

From:
```
* Capacity: $(1-\lambda) \cdot a_i$
```

To:
```
* Capacity: $(1-\lambda) \cdot \frac{a_i}{\rho^2}$
```

### Success Criteria:

#### Automated Verification:
- [x] N/A

#### Manual Verification:
- [x] Documentation formulas match implementation

---

## Phase 4: Verify Lambda Effect

### Overview
Verify that λ now has the intended effect on optimization results.

### Changes Required:

None (verification only)

### Success Criteria:

#### Automated Verification:
- [x] Full test suite passes: `uv run pytest`

#### Manual Verification:
- [x] Run verification script to compare λ=0.0 vs λ=0.5 vs λ=0.9
- [x] λ=0.0 and λ=0.5 produce **different** partitions
- [x] Higher λ produces smoother regions (fewer single-tract islands)
- [x] Binary search still converges for all λ values

**Verification Script:**
```bash
uv run python << 'EOF'
from half_america.data.pipeline import load_all_tracts
from half_america.graph.pipeline import build_graph
from half_america.optimization.search import binary_search

gdf = load_all_tracts()
graph_data = build_graph(gdf)

for lam in [0.0, 0.5, 0.9]:
    result = binary_search(graph_data, lambda_param=lam, verbose=False)
    print(f"λ={lam}: selected={result.result.partition.sum()} tracts, pop={result.result.selected_population:,}")
EOF
```

---

## Testing Strategy

### Unit Tests:
- Existing tests in `test_correctness.py` cover energy function correctness
- Existing tests verify partition invariants hold
- Brute-force optimality tests will validate the fix

### Integration Tests:
- Binary search convergence still works
- Sweep produces varied results across λ values

### Manual Testing Steps:
1. Run sweep with multiple λ values
2. Visually inspect that λ=0.9 produces smoother boundaries than λ=0.0
3. Count single-tract islands at different λ values

## Performance Considerations

None - the fix adds only two division operations (one in network construction, one in energy calculation). Both are O(n) where n is number of tracts.

## Migration Notes

- **Cached sweep results will be invalidated** - new sweeps must be regenerated
- No database migration required
- No API changes

## References

- Research document: `thoughts/shared/research/2025-11-21-lambda-unit-scaling-bug.md`
- GitHub Issue: [#1](https://github.com/stevenfazzio/half-america/issues/1)
- Bug location: `src/half_america/graph/network.py:42`
