"""Tests for flow network construction."""

import pytest
import numpy as np
from half_america.graph.boundary import GraphAttributes
from half_america.graph.network import build_flow_network, get_partition


@pytest.fixture
def simple_attributes():
    """Create simple graph attributes for testing."""
    return GraphAttributes(
        population=np.array([100, 200, 300]),
        area=np.array([1000.0, 1000.0, 1000.0]),
        rho=100.0,
        edge_lengths={(0, 1): 50.0, (1, 0): 50.0, (1, 2): 50.0, (2, 1): 50.0},
    )


class TestBuildFlowNetwork:
    def test_creates_graph(self, simple_attributes):
        """Test that a graph is created."""
        edges = [(0, 1), (1, 2)]
        g = build_flow_network(simple_attributes, edges, lambda_param=0.5, mu=0.01)

        # Should be able to call maxflow without error
        flow = g.maxflow()
        assert flow >= 0

    def test_high_mu_selects_all(self, simple_attributes):
        """Test that high mu (population reward) selects all nodes."""
        edges = [(0, 1), (1, 2)]
        g = build_flow_network(simple_attributes, edges, lambda_param=0.5, mu=1000.0)
        g.maxflow()

        partition = get_partition(g, 3)
        # With very high mu, all nodes should be selected (source partition)
        assert partition.all()

    def test_zero_mu_selects_none(self, simple_attributes):
        """Test that zero mu (no population reward) selects no nodes."""
        edges = [(0, 1), (1, 2)]
        g = build_flow_network(simple_attributes, edges, lambda_param=0.5, mu=0.0)
        g.maxflow()

        partition = get_partition(g, 3)
        # With zero mu, area cost dominates -> no nodes selected
        assert not partition.any()


class TestGetPartition:
    def test_returns_boolean_array(self, simple_attributes):
        """Test partition extraction returns correct format."""
        edges = [(0, 1), (1, 2)]
        g = build_flow_network(simple_attributes, edges, lambda_param=0.5, mu=0.01)
        g.maxflow()

        partition = get_partition(g, 3)

        assert partition.dtype == bool
        assert len(partition) == 3
