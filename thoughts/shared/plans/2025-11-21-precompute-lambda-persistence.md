# Pre-compute Lambda Results: Persistence Implementation Plan

## Overview

Add save/load functions for `SweepResult` to enable persistence of optimization results. This completes the Phase 3 milestone "Pre-compute results for discrete λ values" and unblocks Phase 4 (which needs to load results) and Phase 5 (which will add CLI to trigger pre-computation).

## Current State Analysis

The `sweep_lambda()` function in `sweep.py:56` already computes optimization results for all λ values. What's missing is the ability to persist these results to disk.

### Key Discoveries:
- Existing pickle caching pattern in `pipeline.py:51-78` provides a template
- Cache paths use `TIGER_YEAR` and `ACS_YEAR` from `config.py:25-26`
- `get_processed_cache_path()` in `cache.py:24-26` returns paths in `data/cache/processed/`
- `SweepResult` is a `NamedTuple` containing `dict[float, LambdaResult]` - pickle handles this well
- Estimated file size: ~800KB for 11 λ values (73,000 boolean partition values each)

## Desired End State

After this implementation:
1. `save_sweep_result(result, path)` serializes a `SweepResult` to disk
2. `load_sweep_result(path)` deserializes a `SweepResult` from disk
3. `get_sweep_cache_path(lambda_step)` returns canonical cache path
4. Unit tests verify round-trip serialization preserves all data
5. ROADMAP.md milestone is marked complete

### Verification:
```python
# This should work after implementation:
from half_america.optimization import sweep_lambda, save_sweep_result, load_sweep_result
from half_america.data.cache import get_sweep_cache_path

result = sweep_lambda(graph_data)
path = get_sweep_cache_path(0.1)
save_sweep_result(result, path)
loaded = load_sweep_result(path)
assert loaded == result  # Round-trip preserves data
```

## What We're NOT Doing

- **CLI commands** - Deferred to Phase 5 (ROADMAP.md updated)
- **Structured export format** - Simple pickle is sufficient; Parquet-per-λ adds complexity without benefit
- **Incremental cache updates** - Regenerating all values is fast (~seconds with parallel execution)
- **Cache invalidation logic** - Users can use `force_rebuild` pattern or delete cache manually
- **Metadata file** - Version info can be added later if needed

## Implementation Approach

Follow the existing caching pattern from `pipeline.py:51-78`:
1. Add `save_sweep_result()` and `load_sweep_result()` to `sweep.py` (keep related code together)
2. Add `get_sweep_cache_path()` to `cache.py` (follows existing `get_*_cache_path()` pattern)
3. Export new functions from `optimization/__init__.py`
4. Write unit tests following `test_sweep.py` patterns

---

## Phase 1: Add Cache Path Helper

### Overview
Add `get_sweep_cache_path()` to `cache.py` following the existing pattern.

### Changes Required:

#### 1. Update cache.py
**File**: `src/half_america/data/cache.py`
**Changes**: Add function to generate sweep cache path

```python
def get_sweep_cache_path(lambda_step: float = 0.1) -> Path:
    """Get cache path for sweep results.

    Args:
        lambda_step: Lambda increment used in sweep (default 0.1)

    Returns:
        Path like data/cache/processed/sweep_2024_2022_0.1.pkl
    """
    from half_america.config import TIGER_YEAR, ACS_YEAR
    return PROCESSED_DIR / f"sweep_{TIGER_YEAR}_{ACS_YEAR}_{lambda_step}.pkl"
```

### Success Criteria:

#### Automated Verification:
- [ ] Type checking passes: `uv run mypy src/half_america/data/cache.py`
- [ ] Linting passes: `uv run ruff check src/half_america/data/cache.py`

---

## Phase 2: Add Persistence Functions

### Overview
Add `save_sweep_result()` and `load_sweep_result()` to `sweep.py`.

### Changes Required:

#### 1. Add imports to sweep.py
**File**: `src/half_america/optimization/sweep.py`
**Changes**: Add pickle and Path imports at top

```python
import pickle
from pathlib import Path
```

#### 2. Add save function
**File**: `src/half_america/optimization/sweep.py`
**Changes**: Add after `sweep_lambda()` function

```python
def save_sweep_result(result: SweepResult, path: Path) -> None:
    """Save sweep result to disk.

    Args:
        result: SweepResult from sweep_lambda()
        path: Output path (should end in .pkl)
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(result, f)
```

#### 3. Add load function
**File**: `src/half_america/optimization/sweep.py`
**Changes**: Add after `save_sweep_result()`

```python
def load_sweep_result(path: Path) -> SweepResult:
    """Load sweep result from disk.

    Args:
        path: Path to saved .pkl file

    Returns:
        SweepResult that was previously saved

    Raises:
        FileNotFoundError: If path does not exist
    """
    with open(path, "rb") as f:
        return pickle.load(f)
```

### Success Criteria:

#### Automated Verification:
- [ ] Type checking passes: `uv run mypy src/half_america/optimization/sweep.py`
- [ ] Linting passes: `uv run ruff check src/half_america/optimization/sweep.py`

---

## Phase 3: Export New Functions

### Overview
Export the new functions from `optimization/__init__.py` so they're accessible via `from half_america.optimization import save_sweep_result`.

### Changes Required:

#### 1. Update optimization/__init__.py
**File**: `src/half_america/optimization/__init__.py`
**Changes**: Add new exports to import and `__all__`

Update the sweep import block:
```python
from half_america.optimization.sweep import (
    DEFAULT_LAMBDA_VALUES,
    LambdaResult,
    SweepResult,
    sweep_lambda,
    save_sweep_result,
    load_sweep_result,
)
```

Update `__all__` sweep section:
```python
    # Sweep
    "DEFAULT_LAMBDA_VALUES",
    "LambdaResult",
    "SweepResult",
    "sweep_lambda",
    "save_sweep_result",
    "load_sweep_result",
```

### Success Criteria:

#### Automated Verification:
- [ ] Import works: `python -c "from half_america.optimization import save_sweep_result, load_sweep_result"`
- [ ] Type checking passes: `uv run mypy src/half_america/optimization/__init__.py`

---

## Phase 4: Write Unit Tests

### Overview
Add tests for serialization round-trip and cache path generation.

### Changes Required:

#### 1. Add serialization tests to test_sweep.py
**File**: `tests/test_optimization/test_sweep.py`
**Changes**: Add new test class

```python
class TestSweepPersistence:
    """Tests for sweep result persistence."""

    def test_save_and_load_roundtrip(self, complex_graph_data, tmp_path):
        """Saved result can be loaded back identically."""
        from half_america.optimization import save_sweep_result, load_sweep_result

        result = sweep_lambda(
            complex_graph_data,
            lambda_values=[0.0, 0.5],
            tolerance=0.15,
            verbose=False,
        )

        path = tmp_path / "test_sweep.pkl"
        save_sweep_result(result, path)
        loaded = load_sweep_result(path)

        assert loaded.lambda_values == result.lambda_values
        assert loaded.total_iterations == result.total_iterations
        assert loaded.all_converged == result.all_converged
        assert set(loaded.results.keys()) == set(result.results.keys())

    def test_save_creates_parent_dirs(self, complex_graph_data, tmp_path):
        """Save creates parent directories if needed."""
        from half_america.optimization import save_sweep_result

        result = sweep_lambda(
            complex_graph_data,
            lambda_values=[0.5],
            tolerance=0.15,
            verbose=False,
        )

        path = tmp_path / "nested" / "dirs" / "test.pkl"
        save_sweep_result(result, path)
        assert path.exists()

    def test_load_nonexistent_raises(self, tmp_path):
        """Load raises FileNotFoundError for missing file."""
        from half_america.optimization import load_sweep_result
        import pytest

        with pytest.raises(FileNotFoundError):
            load_sweep_result(tmp_path / "nonexistent.pkl")
```

#### 2. Add cache path test
**File**: `tests/test_optimization/test_sweep.py`
**Changes**: Add test for cache path helper

```python
class TestSweepCachePath:
    """Tests for sweep cache path generation."""

    def test_cache_path_includes_years(self):
        """Cache path includes TIGER and ACS years."""
        from half_america.data.cache import get_sweep_cache_path
        from half_america.config import TIGER_YEAR, ACS_YEAR

        path = get_sweep_cache_path(0.1)
        assert str(TIGER_YEAR) in path.name
        assert str(ACS_YEAR) in path.name

    def test_cache_path_includes_lambda_step(self):
        """Cache path includes lambda step."""
        from half_america.data.cache import get_sweep_cache_path

        path = get_sweep_cache_path(0.05)
        assert "0.05" in path.name

    def test_cache_path_is_pkl(self):
        """Cache path has .pkl extension."""
        from half_america.data.cache import get_sweep_cache_path

        path = get_sweep_cache_path()
        assert path.suffix == ".pkl"
```

### Success Criteria:

#### Automated Verification:
- [ ] All new tests pass: `uv run pytest tests/test_optimization/test_sweep.py -v`
- [ ] Existing tests still pass: `uv run pytest tests/test_optimization/ -v`
- [ ] Full test suite passes: `uv run pytest`

---

## Phase 5: Update ROADMAP.md

### Overview
Mark the "Pre-compute results" milestone as complete.

### Changes Required:

#### 1. Update ROADMAP.md
**File**: `ROADMAP.md`
**Changes**: Change checkbox from `[ ]` to `[x]`

```markdown
- [x] Pre-compute results for discrete λ values (e.g., 0.0, 0.1, 0.2, ..., 1.0)
```

### Success Criteria:

#### Automated Verification:
- [ ] File contains `[x] Pre-compute results`

#### Manual Verification:
- [ ] ROADMAP.md accurately reflects project state

---

## Testing Strategy

### Unit Tests:
- Round-trip serialization preserves all fields
- Parent directory creation works
- FileNotFoundError on missing file
- Cache path includes correct years and lambda step

### Integration Tests:
- None required - this is purely about persistence

### Manual Testing Steps:
1. Run optimization on real data and save results
2. Load saved results and verify they match
3. Verify cache file appears in expected location

## Performance Considerations

- Pickle serialization of ~800KB should be nearly instantaneous (<100ms)
- No performance impact on existing code paths
- File I/O is the bottleneck, not serialization

## References

- Original research: `thoughts/shared/research/2025-11-21-precompute-lambda-values.md`
- Existing cache pattern: `src/half_america/graph/pipeline.py:51-78`
- Sweep implementation: `src/half_america/optimization/sweep.py`
