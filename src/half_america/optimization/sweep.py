"""Lambda parameter sweep for pre-computing optimization results."""

import pickle
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import NamedTuple

from half_america.graph.pipeline import GraphData
from half_america.optimization.search import SearchResult, find_optimal_mu


class LambdaResult(NamedTuple):
    """Result for a single λ value."""

    lambda_param: float  # The λ value
    search_result: SearchResult  # Result from find_optimal_mu
    elapsed_seconds: float  # Time taken for this λ


class SweepResult(NamedTuple):
    """Result from lambda parameter sweep."""

    results: dict[float, LambdaResult]  # λ → LambdaResult mapping
    lambda_values: list[float]  # λ values in order
    total_iterations: int  # Total binary search iterations across all λ
    total_elapsed_seconds: float  # Total wall-clock time
    all_converged: bool  # True if all λ values converged


# Default λ values: 0.0, 0.1, 0.2, ..., 0.9 (excludes 1.0 which causes convergence failure)
DEFAULT_LAMBDA_VALUES = [round(i * 0.1, 1) for i in range(10)]


def _run_single_lambda(
    graph_data: GraphData,
    lambda_param: float,
    target_fraction: float,
    tolerance: float,
) -> LambdaResult:
    """Run optimization for a single λ value with timing."""
    start = time.perf_counter()
    search_result = find_optimal_mu(
        graph_data,
        lambda_param=lambda_param,
        target_fraction=target_fraction,
        tolerance=tolerance,
        verbose=False,
    )
    elapsed = time.perf_counter() - start
    return LambdaResult(
        lambda_param=lambda_param,
        search_result=search_result,
        elapsed_seconds=elapsed,
    )


def sweep_lambda(
    graph_data: GraphData,
    lambda_values: list[float] | None = None,
    target_fraction: float = 0.5,
    tolerance: float = 0.01,
    max_workers: int | None = None,
    verbose: bool = True,
    raise_on_failure: bool = True,
) -> SweepResult:
    """
    Run optimization across a range of λ (surface tension) values.

    Uses parallel execution since each λ optimization is independent.

    Args:
        graph_data: Input graph with edges and attributes
        lambda_values: λ values to sweep (default: 0.0 to 1.0 by 0.1)
        target_fraction: Target population fraction (default: 0.5)
        tolerance: Population tolerance (default: 0.01 = 1%)
        max_workers: Maximum parallel workers (default: None = CPU count)
        verbose: Print progress information
        raise_on_failure: If True (default), raise RuntimeError on non-convergence.
            If False, continue and include non-converged results.

    Returns:
        SweepResult with optimization results for each λ value

    Raises:
        RuntimeError: If any λ value fails to converge and raise_on_failure=True
    """
    if lambda_values is None:
        lambda_values = DEFAULT_LAMBDA_VALUES.copy()

    if verbose:
        print(f"Starting λ sweep: {len(lambda_values)} values")
        print(f"  λ range: {lambda_values[0]} → {lambda_values[-1]}")
        print(f"  Target: {target_fraction*100:.0f}% population ± {tolerance*100:.0f}%")
        print(f"  Parallel workers: {max_workers or 'auto'}")

    results: dict[float, LambdaResult] = {}
    total_start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_lambda = {
            executor.submit(
                _run_single_lambda,
                graph_data,
                lam,
                target_fraction,
                tolerance,
            ): lam
            for lam in lambda_values
        }

        # Collect results as they complete
        for future in as_completed(future_to_lambda):
            lam = future_to_lambda[future]
            try:
                result = future.result()
                results[lam] = result

                if verbose:
                    opt = result.search_result.result
                    print(
                        f"  λ={lam:.1f}: {opt.population_fraction*100:.2f}% pop, "
                        f"μ={opt.mu:.6f}, {result.search_result.iterations} iters, "
                        f"{result.elapsed_seconds:.2f}s"
                    )

                # Early termination check
                if not result.search_result.converged:
                    if raise_on_failure:
                        # Cancel remaining futures
                        for f in future_to_lambda:
                            f.cancel()
                        raise RuntimeError(
                            f"λ={lam} failed to converge after "
                            f"{result.search_result.iterations} iterations"
                        )
                    elif verbose:
                        print(f"  WARNING: λ={lam} did not converge")

            except Exception:
                # Cancel remaining futures on any error
                for f in future_to_lambda:
                    f.cancel()
                raise

    total_elapsed = time.perf_counter() - total_start
    total_iterations = sum(r.search_result.iterations for r in results.values())
    all_converged = all(r.search_result.converged for r in results.values())

    if verbose:
        print(f"\n{'='*50}")
        print(f"Sweep complete: {total_iterations} total iterations")
        print(f"Total time: {total_elapsed:.2f}s")
        print(f"All converged: {all_converged}")

    return SweepResult(
        results=results,
        lambda_values=lambda_values,
        total_iterations=total_iterations,
        total_elapsed_seconds=total_elapsed,
        all_converged=all_converged,
    )


def save_sweep_result(result: SweepResult, path: Path) -> None:
    """Save sweep result to disk.

    Args:
        result: SweepResult from sweep_lambda()
        path: Output path (should end in .pkl)
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(result, f)


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
