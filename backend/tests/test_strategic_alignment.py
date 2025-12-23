import pytest
from unittest.mock import MagicMock
from backend.agents.strategists import BrandVoiceAligner

@pytest.mark.asyncio
async def test_strategic_alignment_check():
    """Verify that BrandVoiceAligner identifies misaligned UVPs."""
    mock_llm = MagicMock()
    aligner = BrandVoiceAligner(mock_llm)
    
    class MockAnalysis:
        def model_dump(self):
            return {
                "alignments": [
                    {
                        "uvp_title": "Cheap Marketing",
                        "is_aligned": False,
                        "score": 0.2,
                        "feedback": "Too playful."
                    }
                ]
            }
        @property
        def alignments(self):
            # The agent calls len(analysis.alignments)
            return [MagicMock()]

    async def mock_ainvoke(*args, **kwargs):
        return MockAnalysis()

    # Mock the chain directly
    aligner.chain = MagicMock()
    aligner.chain.ainvoke = mock_ainvoke
    
    state = {
        "context_brief": {
            "brand_kit": "Calm, Expensive",
            "uvps": {"winning_positions": [{"title": "Cheap"}]}
        }
    }
    
    # Execute the node
    result = await aligner(state)
    
    # Verify the results
    assert "context_brief" in result
    assert "brand_alignment" in result["context_brief"]
    alignment_data = result["context_brief"]["brand_alignment"]
    assert alignment_data["alignments"][0]["is_aligned"] is False