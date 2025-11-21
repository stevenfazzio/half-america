"""s-t flow network construction for graph cut optimization."""

import numpy as np
import maxflow

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
    E(X) = λ Σ(l_ij/ρ)|x_i - x_j| + (1-λ) Σ a_i x_i - μ Σ p_i x_i

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
        sink_cap = (1 - lambda_param) * attributes.area[i]
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
