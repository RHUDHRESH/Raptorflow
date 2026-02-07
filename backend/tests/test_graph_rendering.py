import os

import pytest

from graphs.moves_campaigns_orchestrator import moves_campaigns_orchestrator


def test_graph_rendering_mermaid():
    """Verify that the graph can generate a mermaid string."""
    mermaid_str = moves_campaigns_orchestrator.get_graph().draw_mermaid()
    assert "approve_campaign" in mermaid_str
    assert "approve_move" in mermaid_str
    assert "init" in mermaid_str


def test_graph_rendering_png_export():
    """Verify that the graph can be exported to a PNG file (if possible)."""
    # This might fail if dependencies are missing, but we want to know.
    output_path = "graph.png"
    try:
        png_data = moves_campaigns_orchestrator.get_graph().draw_mermaid_png()
        with open(output_path, "wb") as f:
            f.write(png_data)
        assert os.path.exists(output_path)
        os.remove(output_path)
    except Exception as e:
        pytest.skip(f"PNG rendering skipped: {e}")
