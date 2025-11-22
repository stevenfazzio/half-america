"""Binary search for Lagrange multiplier (μ)."""

from typing import NamedTuple

from half_america.graph.pipeline import GraphData
from half_america.optimization.solver import (
    TARGET_TOLERANCE,
    OptimizationResult,
    solve_partition,
)


class SearchResult(NamedTuple):
    """Result from binary search for optimal μ."""

    result: OptimizationResult  # Final optimization result
    iterations: int  # Number of binary search iterations
    mu_history: list[float]  # μ values tried during search
    converged: bool  # True if converged within max_iterations


# Default parameters
DEFAULT_MAX_ITERATIONS = 50
DEFAULT_MU_MIN = 0.0


def find_optimal_mu(
    graph_data: GraphData,
    lambda_param: float,
    target_fraction: float = 0.5,
    tolerance: float = TARGET_TOLERANCE,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
    mu_min: float = DEFAULT_MU_MIN,
    mu_max: float | None = None,
    verbose: bool = True,
) -> SearchResult:
    """
    Binary search for μ that achieves target population fraction.

    Exploits monotonicity: higher μ → more tracts selected.

    Args:
        graph_data: GraphData from load_graph_data()
        lambda_param: Surface tension parameter [0, 1]
        target_fraction: Target population fraction (default 0.5)
        tolerance: Acceptable deviation from target (default 0.01 = 1%)
        max_iterations: Maximum search iterations (default 50)
        mu_min: Lower bound for μ (default 0.0)
        mu_max: Upper bound for μ (auto-scaled if None)
        verbose: Print diagnostic output

    Returns:
        SearchResult with final OptimizationResult and search metadata
    """
    total_pop = graph_data.attributes.population.sum()
    target_pop = target_fraction * total_pop
    pop_tolerance = tolerance * total_pop

    # Auto-scale mu_max if not provided
    if mu_max is None:
        mu_max = _estimate_mu_max(graph_data)

    if verbose:
        print(f"Binary search for μ: target={target_fraction:.1%} ± {tolerance:.1%}")
        print(f"  Population target: {target_pop:,.0f} ± {pop_tolerance:,.0f}")
        print(f"  μ bounds: [{mu_min:.6f}, {mu_max:.6f}]")

    mu_history: list[float] = []
    result: OptimizationResult | None = None

    for iteration in range(max_iterations):
        mu = (mu_min + mu_max) / 2
        mu_history.append(mu)

        result = solve_partition(
            graph_data,
            lambda_param,
            mu,
            verbose=False,
        )

        error = result.selected_population - target_pop

        if verbose:
            print(
                f"  [{iteration + 1:2d}] μ={mu:.6f}, "
                f"pop={result.selected_population:,} "
                f"({100 * result.population_fraction:.2f}%), "
                f"error={error:+,.0f}"
            )

        # Check convergence
        if abs(error) <= pop_tolerance:
            if verbose:
                print(f"  Converged in {iteration + 1} iterations")
            return SearchResult(
                result=result,
                iterations=iteration + 1,
                mu_history=mu_history,
                converged=True,
            )

        # Binary search step
        if result.selected_population < target_pop:
            mu_min = mu  # Need more selection → increase reward
        else:
            mu_max = mu  # Need less selection → decrease reward

    # Did not converge
    if verbose:
        print(f"  Did not converge in {max_iterations} iterations")

    assert result is not None  # Always at least one iteration
    return SearchResult(
        result=result,
        iterations=max_iterations,
        mu_history=mu_history,
        converged=False,
    )


def _estimate_mu_max(graph_data: GraphData) -> float:
    """
    Estimate upper bound for μ based on data characteristics.

    μ should be on scale of (area cost) / (population benefit).
    We want μ × p_i to be comparable to (1-λ) × a_i / ρ².
    """
    attrs = graph_data.attributes
    total_area = attrs.area.sum()
    total_pop = attrs.population.sum()
    rho_sq = attrs.rho**2

    # Scale factor: normalized area per person, with headroom
    # Area cost is now a_i / ρ², so scale accordingly
    mu_scale = (total_area / rho_sq) / total_pop
    return mu_scale * 10  # Allow 10x headroom
