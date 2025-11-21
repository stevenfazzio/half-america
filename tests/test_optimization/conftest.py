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
