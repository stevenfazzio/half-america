# Lambda=1.0 Exclusion Implementation Plan

## Overview

Change the valid lambda range from [0, 1] to [0, 1) across the codebase to fix the convergence failure at lambda=1.0. The Lagrangian relaxation formulation breaks down at lambda=1.0 because the sink capacity (area cost) becomes zero, making 100% selection always optimal regardless of mu.

## Current State Analysis

The research document `thoughts/shared/research/2025-11-21-lambda-one-convergence-failure.md` conclusively demonstrates:

1. At lambda=1.0, sink capacity is zero: `(1-lambda) * area = 0`
2. With no area cost, selecting 100% of tracts is always optimal
3. Binary search cannot find 50% because the cost function is flat at 100%
4. The mathematical problem "minimize perimeter at 50% population" IS well-defined, but our max-flow formulation cannot solve it

### Key Discoveries:
- `src/half_america/optimization/solver.py:52-53` - Current validation accepts [0, 1] inclusive
- `src/half_america/optimization/sweep.py:32` - `DEFAULT_LAMBDA_VALUES` includes 1.0
- `src/half_america/cli.py:52` - CLI generates lambda values up to and including 1.0
- `tests/test_optimization/test_solver.py:139-147` - Test expects lambda=1.0 to be valid
- `METHODOLOGY.md:39` - Documents lambda in [0, 1]

## Desired End State

After this plan is complete:
1. Lambda validation rejects values >= 1.0 with a clear error message
2. Default lambda values end at 0.9 instead of 1.0
3. CLI generates lambda values excluding 1.0
4. Tests verify lambda=1.0 is rejected
5. Documentation explains why lambda=1.0 is invalid
6. Existing cache files with lambda=1.0 results remain compatible (they just won't be regenerated)

### Verification:
- `uv run pytest` passes with updated tests
- `uv run mypy src/` passes
- `uv run ruff check src/ tests/` passes
- `uv run half-america precompute --lambda-step 0.1` completes without lambda=1.0 warning

## What We're NOT Doing

- NOT implementing epsilon sink capacity (Option 3 from research)
- NOT implementing alternative constrained optimization formulations
- NOT modifying the graph/network.py edge capacity calculations
- NOT changing the binary search algorithm
- NOT invalidating existing cache files (they remain readable)

## Implementation Approach

Make minimal, surgical changes to exclude lambda=1.0 while preserving all other behavior. Update validation first, then defaults, then tests, then documentation.

---

## Phase 1: Update Validation and Constants

### Overview
Change the core validation logic and default values to exclude lambda=1.0.

### Changes Required:

#### 1. Solver Validation
**File**: `src/half_america/optimization/solver.py`
**Lines**: 52-53

Change validation from inclusive to exclusive upper bound:

```python
# Before (line 52-53):
if not 0 <= lambda_param <= 1:
    raise ValueError(f"lambda_param must be in [0, 1], got {lambda_param}")

# After:
if not 0 <= lambda_param < 1:
    raise ValueError(
        f"lambda_param must be in [0, 1), got {lambda_param}. "
        "lambda=1.0 causes convergence failure (zero area cost)."
    )
```

Also update the docstring at line 41:

```python
# Before:
lambda_param: Surface tension parameter [0, 1]

# After:
lambda_param: Surface tension parameter [0, 1)
```

#### 2. Default Lambda Values
**File**: `src/half_america/optimization/sweep.py`
**Lines**: 31-32

Change default values to exclude 1.0:

```python
# Before (line 31-32):
# Default lambda values: 0.0, 0.1, 0.2, ..., 1.0
DEFAULT_LAMBDA_VALUES = [round(i * 0.1, 1) for i in range(11)]

# After:
# Default lambda values: 0.0, 0.1, 0.2, ..., 0.9 (excludes 1.0 which causes convergence failure)
DEFAULT_LAMBDA_VALUES = [round(i * 0.1, 1) for i in range(10)]
```

#### 3. CLI Lambda Generation
**File**: `src/half_america/cli.py`
**Line**: 52

Change CLI to exclude 1.0 from generated values:

```python
# Before (line 52):
lambda_values = [round(i * lambda_step, 2) for i in range(int(1 / lambda_step) + 1)]

# After:
# Generate lambda values from 0.0 up to but not including 1.0
num_steps = int(1 / lambda_step)
lambda_values = [round(i * lambda_step, 2) for i in range(num_steps)]
```

Note: With `lambda_step=0.1`, this generates [0.0, 0.1, ..., 0.9] (10 values instead of 11).

### Success Criteria:

#### Automated Verification:
- [ ] Type checking passes: `uv run mypy src/`
- [ ] Linting passes: `uv run ruff check src/`
- [ ] Existing tests still pass (except lambda=1.0 tests): `uv run pytest -v`

#### Manual Verification:
- [ ] Confirm `solve_partition(..., lambda_param=1.0, ...)` raises ValueError
- [ ] Confirm `DEFAULT_LAMBDA_VALUES` has 10 elements ending at 0.9

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation before proceeding to Phase 2.

---

## Phase 2: Update Tests

### Overview
Update test expectations to match new validation behavior.

### Changes Required:

#### 1. Solver Validation Tests
**File**: `tests/test_optimization/test_solver.py`
**Lines**: 139-147

Change `test_lambda_one_valid` to expect rejection:

```python
# Before (lines 139-147):
def test_lambda_one_valid(self, simple_graph_data):
    """Test that lambda=1 is valid (boundary)."""
    result = solve_partition(
        simple_graph_data,
        lambda_param=1.0,
        mu=0.01,
        verbose=False,
    )
    assert result.lambda_param == 1.0

# After:
def test_lambda_one_raises(self, simple_graph_data):
    """Test that lambda=1.0 raises ValueError (convergence failure)."""
    with pytest.raises(ValueError, match="lambda_param must be in"):
        solve_partition(
            simple_graph_data,
            lambda_param=1.0,
            mu=0.01,
            verbose=False,
        )
```

#### 2. Sweep Default Values Test
**File**: `tests/test_optimization/test_sweep.py`
**Lines**: 55-58

Update expected default values:

```python
# Before (lines 55-58):
def test_default_lambda_values(self):
    """Default values cover 0.0 to 1.0 by 0.1."""
    expected = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    assert DEFAULT_LAMBDA_VALUES == expected

# After:
def test_default_lambda_values(self):
    """Default values cover 0.0 to 0.9 by 0.1 (excludes 1.0)."""
    expected = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    assert DEFAULT_LAMBDA_VALUES == expected
```

#### 3. Sweep Defaults Exported Test
**File**: `tests/test_optimization/test_sweep.py`
**Lines**: 165-169

Update expected count:

```python
# Before (lines 165-169):
def test_default_lambda_values_exported(self):
    """Test DEFAULT_LAMBDA_VALUES is exported."""
    assert len(DEFAULT_LAMBDA_VALUES) == 11
    assert DEFAULT_LAMBDA_VALUES[0] == 0.0
    assert DEFAULT_LAMBDA_VALUES[-1] == 1.0

# After:
def test_default_lambda_values_exported(self):
    """Test DEFAULT_LAMBDA_VALUES is exported."""
    assert len(DEFAULT_LAMBDA_VALUES) == 10
    assert DEFAULT_LAMBDA_VALUES[0] == 0.0
    assert DEFAULT_LAMBDA_VALUES[-1] == 0.9
```

#### 4. Search Edge Case Test
**File**: `tests/test_optimization/test_search.py`
**Lines**: 139-156

Update or remove `test_lambda_one`:

```python
# Before (lines 139-156):
def test_lambda_one(self, complex_graph_data):
    """Test with lambda=1 (max boundary cost).
    ...
    """
    result = find_optimal_mu(
        complex_graph_data,
        lambda_param=1.0,
        tolerance=0.1,
        verbose=False,
    )
    assert isinstance(result, SearchResult)
    assert result.iterations > 0

# After:
def test_lambda_one_rejected(self, complex_graph_data):
    """Test that lambda=1.0 is rejected before reaching search.

    lambda=1.0 causes convergence failure because sink capacity
    becomes zero, making 100% selection always optimal.
    """
    with pytest.raises(ValueError, match="lambda_param must be in"):
        find_optimal_mu(
            complex_graph_data,
            lambda_param=1.0,
            tolerance=0.1,
            verbose=False,
        )
```

#### 5. Add Test for Maximum Valid Lambda
**File**: `tests/test_optimization/test_solver.py`

Add new test after `test_lambda_zero_valid`:

```python
def test_lambda_near_one_valid(self, simple_graph_data):
    """Test that lambda=0.99 is valid (near upper bound)."""
    result = solve_partition(
        simple_graph_data,
        lambda_param=0.99,
        mu=0.01,
        verbose=False,
    )
    assert result.lambda_param == 0.99
```

### Success Criteria:

#### Automated Verification:
- [ ] All tests pass: `uv run pytest -v`
- [ ] Test count is correct (no missing tests)

#### Manual Verification:
- [ ] Review test output to confirm lambda=1.0 rejection tests pass
- [ ] Confirm no tests are accidentally skipped

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation before proceeding to Phase 3.

---

## Phase 3: Update Documentation

### Overview
Update documentation to reflect the new valid lambda range and explain why.

### Changes Required:

#### 1. Methodology Documentation
**File**: `METHODOLOGY.md`
**Line**: 39

Update lambda range and add explanation:

```markdown
# Before (line 39):
* $\lambda \in [0, 1]$: User-controlled "Surface Tension" parameter.

# After:
* $\lambda \in [0, 1)$: User-controlled "Surface Tension" parameter. Note: $\lambda = 1$ is excluded because it causes the area cost term $(1-\lambda)$ to vanish, making the Lagrangian relaxation degenerate.
```

#### 2. README Description
**File**: `README.md`
**Lines**: 23-27

Update slider description:

```markdown
# Before (lines 23-27):
A slider controls lambda:

- **lambda ~ 0**: Minimizes area, showing high-resolution "dusty" city centers
- **lambda ~ 1**: Minimizes perimeter, creating smooth, compact blobs

# After:
A slider controls lambda (0 to <1):

- **lambda ~ 0**: Minimizes area, showing high-resolution "dusty" city centers
- **lambda ~ 0.9**: Minimizes perimeter, creating smooth, compact blobs

Note: lambda=1.0 is mathematically degenerate and excluded from valid values.
```

#### 3. CLAUDE.md Key Parameters
**File**: `CLAUDE.md`
**Lines**: 21-22

Update lambda description:

```markdown
# Before (lines 21-22):
- lambda (lambda): User-controlled surface tension [0,1]. lambda~0 minimizes area (dusty map), lambda~1 minimizes perimeter (smooth blobs)

# After:
- lambda (lambda): User-controlled surface tension [0,1). lambda~0 minimizes area (dusty map), lambda~0.9 minimizes perimeter (smooth blobs). lambda=1.0 is excluded (causes convergence failure).
```

### Success Criteria:

#### Automated Verification:
- [ ] No broken markdown links
- [ ] Documentation builds without errors (if applicable)

#### Manual Verification:
- [ ] Review METHODOLOGY.md renders correctly with LaTeX
- [ ] README.md is clear and accurate
- [ ] CLAUDE.md accurately reflects implementation

**Implementation Note**: After completing this phase and all automated verification passes, pause here for manual confirmation before proceeding to Phase 4.

---

## Phase 4: Deprecate Incorrect Research

### Overview
Add notice to the superseded research document.

### Changes Required:

#### 1. Add Superseded Notice
**File**: `thoughts/shared/research/2025-11-21-lambda-edge-cases.md`

Add deprecation notice at the top of the file (after frontmatter):

```markdown
> **SUPERSEDED**: This research was partially incorrect regarding lambda=1.0.
> See [2025-11-21-lambda-one-convergence-failure.md](2025-11-21-lambda-one-convergence-failure.md)
> for the corrected analysis showing that lambda=1.0 causes convergence failure
> due to zero sink capacity.
```

### Success Criteria:

#### Automated Verification:
- [ ] File is valid markdown

#### Manual Verification:
- [ ] Notice is prominently visible
- [ ] Link to corrected research is correct

---

## Testing Strategy

### Unit Tests:
- Validation rejects lambda >= 1.0 with clear message
- Validation accepts lambda = 0.99 (near upper bound)
- Default lambda values exclude 1.0
- Sweep and search functions reject lambda = 1.0

### Integration Tests:
- Full precompute sweep completes without lambda=1.0 warning
- No convergence failures with default lambda values

### Manual Testing Steps:
1. Run `uv run half-america precompute --lambda-step 0.1` and verify no warnings
2. Verify output shows 10 lambda values (0.0 to 0.9) instead of 11
3. Try `solve_partition(..., lambda_param=1.0, ...)` in Python REPL and verify error message

## Performance Considerations

- No performance impact (removing one lambda value slightly reduces precompute time)
- Existing cache files with lambda=1.0 results remain valid but won't be regenerated

## Migration Notes

- Existing cache files (`sweep_*.pkl`) may contain lambda=1.0 results
- These remain loadable but the lambda=1.0 entry will show non-converged results
- Users should regenerate cache with `--force` for clean results

## References

- Research: `thoughts/shared/research/2025-11-21-lambda-one-convergence-failure.md`
- Superseded research: `thoughts/shared/research/2025-11-21-lambda-edge-cases.md`
- Solver validation: `src/half_america/optimization/solver.py:52-53`
- Default values: `src/half_america/optimization/sweep.py:32`
