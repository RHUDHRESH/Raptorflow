from graphs.council import get_expert_council_graph


def test_expert_council_graph_assembly():
    """Verify that the Expert Council graph is correctly assembled."""
    graph = get_expert_council_graph()
    assert graph is not None
    # Verify it can be compiled
    compiled = graph.compile()
    assert compiled is not None
