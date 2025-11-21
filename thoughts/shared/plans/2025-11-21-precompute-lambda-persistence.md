# Pre-compute Lambda Results: Persistence Implementation Plan

## Overview

Add save/load functions for `SweepResult` to enable persistence of optimization results, plus a CLI command to trigger pre-computation. This completes the Phase 3 milestone "Pre-compute results for discrete λ values" and unblocks Phase 4 (which needs to load results).

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
5. CLI command `uv run half-america precompute` triggers pre-computation and caching
6. ROADMAP.md milestone is marked complete

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
- [x] Type checking passes: `uv run mypy src/half_america/data/cache.py`
- [x] Linting passes: `uv run ruff check src/half_america/data/cache.py`

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
- [x] Type checking passes: `uv run mypy src/half_america/optimization/sweep.py`
- [x] Linting passes: `uv run ruff check src/half_america/optimization/sweep.py`

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
- [x] Import works: `python -c "from half_america.optimization import save_sweep_result, load_sweep_result"`
- [x] Type checking passes: `uv run mypy src/half_america/optimization/__init__.py`

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
- [x] All new tests pass: `uv run pytest tests/test_optimization/test_sweep.py -v`
- [x] Existing tests still pass: `uv run pytest tests/test_optimization/ -v`
- [x] Full test suite passes: `uv run pytest`

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
- [x] File contains `[x] Pre-compute results`

#### Manual Verification:
- [x] ROADMAP.md accurately reflects project state

---

## Phase 6: Add CLI Command

### Overview
Add a `precompute` CLI command using Click to trigger the lambda sweep and cache results.

### Changes Required:

#### 1. Add Click dependency
**File**: `pyproject.toml`
**Changes**: Add click to dependencies

```toml
"click>=8.0",
```

#### 2. Create CLI module
**File**: `src/half_america/cli.py`
**Changes**: Create new file with Click commands

```python
"""Command-line interface for half-america."""

import click

from half_america.data.cache import get_sweep_cache_path
from half_america.graph.pipeline import build_graph_data
from half_america.optimization import (
    DEFAULT_LAMBDA_VALUES,
    save_sweep_result,
    load_sweep_result,
    sweep_lambda,
)


@click.group()
def cli() -> None:
    """Half of America - topology optimization for population distribution."""
    pass


@cli.command()
@click.option(
    "--force",
    is_flag=True,
    help="Rebuild cache even if it exists",
)
@click.option(
    "--lambda-step",
    type=float,
    default=0.1,
    help="Lambda increment (default: 0.1)",
)
def precompute(force: bool, lambda_step: float) -> None:
    """Pre-compute optimization results for all lambda values."""
    cache_path = get_sweep_cache_path(lambda_step)

    if cache_path.exists() and not force:
        click.echo(f"Cache exists: {cache_path}")
        click.echo("Use --force to rebuild")
        return

    click.echo("Building graph data...")
    graph_data = build_graph_data()

    lambda_values = [round(i * lambda_step, 2) for i in range(int(1 / lambda_step) + 1)]
    click.echo(f"Running sweep for {len(lambda_values)} lambda values...")

    result = sweep_lambda(graph_data, lambda_values=lambda_values)

    save_sweep_result(result, cache_path)
    click.echo(f"Saved to: {cache_path}")
```

#### 3. Update package entry point
**File**: `src/half_america/__init__.py`
**Changes**: Replace placeholder main with CLI import

```python
"""Half of America - topology optimization for population distribution."""


def main() -> None:
    """CLI entry point."""
    from half_america.cli import cli

    cli()
```

#### 4. Run uv sync to install Click
**Command**: `uv sync`

### Success Criteria:

#### Automated Verification:
- [x] Type checking passes: `uv run mypy src/half_america/cli.py`
- [x] Linting passes: `uv run ruff check src/half_america/cli.py`
- [x] CLI help works: `uv run half-america --help`
- [x] Precompute help works: `uv run half-america precompute --help`

#### Manual Verification:
- [x] `uv run half-america precompute` runs optimization and saves cache
- [x] `uv run half-america precompute` (second run) reports cache exists
- [x] `uv run half-america precompute --force` rebuilds cache
- [x] Cache file appears in `data/cache/processed/`

---

## Phase 7: Update ROADMAP.md for CLI

### Overview
Move CLI from Phase 5 to Phase 3 in ROADMAP.md since we're implementing it now.

### Changes Required:

#### 1. Update ROADMAP.md
**File**: `ROADMAP.md`
**Changes**: Add CLI milestone to Phase 3, remove from Phase 5

In Phase 3, add after "Pre-compute results":
```markdown
- [ ] Add CLI `precompute` command
```

In Phase 5, change:
```markdown
- [ ] Add CLI framework (Click) with `precompute` and `export` subcommands
```
to:
```markdown
- [ ] Add CLI `export` subcommand for TopoJSON output
```

### Success Criteria:

#### Automated Verification:
- [x] ROADMAP.md contains `Add CLI \`precompute\` command` in Phase 3

#### Manual Verification:
- [x] ROADMAP.md structure is clear and accurate

---

## Testing Strategy

### Unit Tests:
- Round-trip serialization preserves all fields
- Parent directory creation works
- FileNotFoundError on missing file
- Cache path includes correct years and lambda step

### Integration Tests:
- CLI `--help` displays usage information
- CLI `precompute --help` shows command options

### Manual Testing Steps:
1. Run `uv run half-america precompute` on real data
2. Verify cache file appears in `data/cache/processed/`
3. Run again without `--force` - should report cache exists
4. Run with `--force` - should rebuild cache
5. Load saved results programmatically and verify they're valid

## Performance Considerations

- Pickle serialization of ~800KB should be nearly instantaneous (<100ms)
- No performance impact on existing code paths
- File I/O is the bottleneck, not serialization

## References

- Original research: `thoughts/shared/research/2025-11-21-precompute-lambda-values.md`
- Existing cache pattern: `src/half_america/graph/pipeline.py:51-78`
- Sweep implementation: `src/half_america/optimization/sweep.py`
- Click documentation: https://click.palletsprojects.com/
