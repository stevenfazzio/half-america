"""Graph cut solver wrapper for optimization."""

from typing import NamedTuple

import numpy as np

from half_america.graph.network import build_flow_network, get_partition
from half_america.graph.pipeline import GraphData


class OptimizationResult(NamedTuple):
    """Result from graph cut optimization."""

    partition: np.ndarray  # Boolean array: True = selected (source partition)
    selected_population: int  # Sum of p_i for selected tracts
    selected_area: float  # Sum of a_i for selected tracts in sq meters
    total_population: int  # Total population across all tracts
    total_area: float  # Total area in sq meters
    population_fraction: float  # selected_population / total_population
    satisfied_target: bool  # True if population_fraction within 1% of 50%
    lambda_param: float  # Surface tension parameter used
    mu: float  # Lagrange multiplier used
    flow_value: float  # Minimum cut value from maxflow


# Target tolerance: population fraction must be within this of 0.5
TARGET_TOLERANCE = 0.01


def solve_partition(
    graph_data: GraphData,
    lambda_param: float,
    mu: float,
    verbose: bool = True,
) -> OptimizationResult:
    """
    Solve graph cut optimization for given parameters.

    Args:
        graph_data: GraphData from load_graph_data()
        lambda_param: Surface tension parameter [0, 1]
        mu: Lagrange multiplier for population constraint (non-negative)
        verbose: Print diagnostic output

    Returns:
        OptimizationResult with partition and statistics

    Raises:
        ValueError: If lambda_param not in [0, 1] or mu < 0
    """
    # Validate parameters
    if not 0 <= lambda_param <= 1:
        raise ValueError(f"lambda_param must be in [0, 1], got {lambda_param}")
    if mu < 0:
        raise ValueError(f"mu must be non-negative, got {mu}")

    if verbose:
        print(f"Solving partition for λ={lambda_param:.2f}, μ={mu:.6f}...")

    # Build and solve flow network
    g = build_flow_network(
        graph_data.attributes,
        graph_data.edges,
        lambda_param,
        mu,
    )
    flow_value = g.maxflow()
    partition = get_partition(g, graph_data.num_nodes)

    # Compute statistics
    attrs = graph_data.attributes
    selected_population = int(attrs.population[partition].sum())
    selected_area = float(attrs.area[partition].sum())
    total_population = int(attrs.population.sum())
    total_area = float(attrs.area.sum())
    population_fraction = selected_population / total_population
    satisfied_target = abs(population_fraction - 0.5) <= TARGET_TOLERANCE

    if verbose:
        print(f"  Selected: {partition.sum():,} / {graph_data.num_nodes:,} tracts")
        print(
            f"  Population: {selected_population:,} / {total_population:,} "
            f"({100 * population_fraction:.2f}%)"
        )
        print(f"  Area: {selected_area / 1e6:.0f} / {total_area / 1e6:.0f} km²")
        print(f"  Flow value: {flow_value:.2f}")
        if satisfied_target:
            print("  Target satisfied: Yes")
        else:
            print(f"  Target satisfied: No (need 49-51%, got {100 * population_fraction:.2f}%)")

    return OptimizationResult(
        partition=partition,
        selected_population=selected_population,
        selected_area=selected_area,
        total_population=total_population,
        total_area=total_area,
        population_fraction=population_fraction,
        satisfied_target=satisfied_target,
        lambda_param=lambda_param,
        mu=mu,
        flow_value=flow_value,
    )
