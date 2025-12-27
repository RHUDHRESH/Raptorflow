from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.librarian import LibrarianAgent


@pytest.mark.asyncio
@patch("inference.InferenceProvider.get_model")
async def test_librarian_extraction(m_get_model):
    # Mock LLM setup to avoid loading heavy dependencies that crash on win32/py3.14
    m_get_model.return_value = AsyncMock()
    agent = LibrarianAgent()

    mock_json = {
        "never_rules": ["Never use red in logo"],
        "always_rules": ["Always be calm"],
        "exploits": [{"title": "Win A", "description": "Desc A", "predicted_roi": 5.0}],
        "target_agents": ["brand_philosopher"],
    }

    import json

    mock_response = MagicMock()
    mock_response.content = json.dumps(mock_json)

    with patch.object(agent.llm, "ainvoke", AsyncMock(return_value=mock_response)):
        result = await agent.extract_heuristics("Sample document text")

        assert len(result["never_rules"]) == 1
        assert result["never_rules"][0] == "Never use red in logo"
        assert len(result["exploits"]) == 1
        assert result["exploits"][0]["title"] == "Win A"


@pytest.mark.asyncio
@patch("db.get_db_connection")
async def test_save_heuristics(m_get_db):
    from db import save_heuristics

    mock_cur = AsyncMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__aenter__.return_value = mock_cur

    m_get_db.return_value.__aenter__.return_value = mock_conn

    heuristics = {"never_rules": ["Rule 1"], "always_rules": ["Rule 2"]}

    await save_heuristics("ws_123", heuristics)

    assert mock_cur.execute.call_count == 2
