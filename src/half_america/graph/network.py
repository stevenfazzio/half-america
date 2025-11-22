"""s-t flow network construction for graph cut optimization."""

import maxflow
import numpy as np

from half_america.graph.boundary import GraphAttributes


def build_flow_network(
    attributes: GraphAttributes,
    edges: list[tuple[int, int]],
    lambda_param: float,
    mu: float,
) -> maxflow.Graph:
    """
    Construct s-t flow network for graph cut optimization.

    The network encodes the energy function:
    E(X) = λ Σ(l_ij/ρ)|x_i - x_j| + (1-λ) Σ (a_i/ρ²) x_i - μ Σ p_i x_i

    Args:
        attributes: GraphAttributes with population, area, rho, edge_lengths
        edges: List of (i, j) neighbor pairs (only i < j pairs)
        lambda_param: Surface tension parameter [0, 1]
        mu: Lagrange multiplier for population constraint

    Returns:
        PyMaxFlow Graph ready for maxflow() computation
    """
    num_nodes = len(attributes.population)
    num_edges = len(edges)

    # Create graph with float capacities
    g: maxflow.Graph = maxflow.Graph[float](num_nodes, num_edges)
    g.add_nodes(num_nodes)

    # Add terminal edges (t-links)
    # Source capacity: μ × p_i (population reward for inclusion)
    # Sink capacity: (1-λ) × a_i (area cost for inclusion)
    for i in range(num_nodes):
        source_cap = mu * attributes.population[i]
        sink_cap = (1 - lambda_param) * attributes.area[i] / (attributes.rho**2)
        g.add_tedge(i, source_cap, sink_cap)

    # Add neighborhood edges (n-links)
    # Capacity: λ × l_ij / ρ (boundary cost, normalized)
    rho = attributes.rho
    for i, j in edges:
        l_ij = attributes.edge_lengths[(i, j)]
        capacity = lambda_param * l_ij / rho
        g.add_edge(i, j, capacity, capacity)  # Symmetric

    return g


def get_partition(g: maxflow.Graph, num_nodes: int) -> np.ndarray:
    """
    Extract partition assignment after maxflow computation.

    Args:
        g: PyMaxFlow Graph after maxflow() has been called
        num_nodes: Number of nodes in the graph

    Returns:
        Boolean array where True = node in source partition (selected)
    """
    return np.array([g.get_segment(i) == 0 for i in range(num_nodes)])


def compute_energy(
    attributes: GraphAttributes,
    edges: list[tuple[int, int]],
    partition: np.ndarray,
    lambda_param: float,
    mu: float,
) -> float:
    """
    Compute energy function value for a given partition.

    E(X) = λ Σ(l_ij/ρ)|x_i - x_j| + (1-λ) Σ (a_i/ρ²) x_i - μ Σ p_i x_i

    Args:
        attributes: GraphAttributes with population, area, rho, edge_lengths
        edges: List of (i, j) neighbor pairs
        partition: Boolean array where True = selected
        lambda_param: Surface tension parameter [0, 1)
        mu: Lagrange multiplier

    Returns:
        Total energy value (lower is better for the optimizer)
    """
    # Boundary cost: λ Σ(l_ij/ρ)|x_i - x_j|
    # Only count edges crossing the cut (where x_i != x_j)
    boundary_cost = 0.0
    rho = attributes.rho
    for i, j in edges:
        if partition[i] != partition[j]:
            l_ij = attributes.edge_lengths[(i, j)]
            boundary_cost += lambda_param * l_ij / rho

    # Area cost: (1-λ) Σ (a_i/ρ²) x_i (for selected nodes only)
    rho_sq = attributes.rho**2
    area_cost = (1 - lambda_param) * attributes.area[partition].sum() / rho_sq

    # Population reward: μ Σ p_i x_i (for selected nodes only)
    population_reward = mu * attributes.population[partition].sum()

    return boundary_cost + area_cost - population_reward
