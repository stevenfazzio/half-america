"""Fixtures for optimization tests."""

import pytest
import numpy as np
from half_america.graph.boundary import GraphAttributes
from half_america.graph.pipeline import GraphData


@pytest.fixture
def simple_graph_data():
    """Create minimal 3-node GraphData for testing."""
    attributes = GraphAttributes(
        population=np.array([100, 200, 300]),
        area=np.array([1000.0, 1000.0, 1000.0]),
        rho=100.0,
        edge_lengths={(0, 1): 50.0, (1, 0): 50.0, (1, 2): 50.0, (2, 1): 50.0},
    )
    return GraphData(
        edges=[(0, 1), (1, 2)],
        attributes=attributes,
        num_nodes=3,
        num_edges=2,
    )


@pytest.fixture
def complex_graph_data():
    """Create 5-node GraphData where 50% requires multiple nodes.

    Populations: [80, 120, 150, 200, 250] = 800 total
    50% target = 400, achievable via nodes 3+4 (200+250=450) or 2+3 (150+200=350)
    but not by any single node.

    Graph topology: 0 -- 1 -- 2 -- 3 -- 4 (linear chain)
    """
    attributes = GraphAttributes(
        population=np.array([80, 120, 150, 200, 250]),
        area=np.array([1000.0, 1000.0, 1000.0, 1000.0, 1000.0]),
        rho=100.0,
        edge_lengths={
            (0, 1): 50.0, (1, 0): 50.0,
            (1, 2): 50.0, (2, 1): 50.0,
            (2, 3): 50.0, (3, 2): 50.0,
            (3, 4): 50.0, (4, 3): 50.0,
        },
    )
    return GraphData(
        edges=[(0, 1), (1, 2), (2, 3), (3, 4)],
        attributes=attributes,
        num_nodes=5,
        num_edges=4,
    )


@pytest.fixture
def tiny_graph_factory():
    """Factory to create tiny graphs for brute-force testing."""

    def _create(n: int) -> GraphData:
        """Create n-node linear chain graph."""
        # Generate populations that sum to nice numbers
        populations = np.array([100 * (i + 1) for i in range(n)])
        areas = np.array([1000.0] * n)

        # Linear chain edges
        edges = [(i, i + 1) for i in range(n - 1)]

        # Edge lengths all equal
        edge_lengths = {}
        for i, j in edges:
            edge_lengths[(i, j)] = 50.0
            edge_lengths[(j, i)] = 50.0

        attributes = GraphAttributes(
            population=populations,
            area=areas,
            rho=100.0,
            edge_lengths=edge_lengths,
        )
        return GraphData(
            edges=edges,
            attributes=attributes,
            num_nodes=n,
            num_edges=len(edges),
        )

    return _create
