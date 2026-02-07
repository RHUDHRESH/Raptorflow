from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.creatives import (
    AdAnalysis,
    AdCopy,
    BlogPost,
    CreativeLintResult,
    ImagePrompt,
    LinkedInPost,
    SVGDiagram,
    TwitterThread,
    create_ad_architect,
    create_content_transformer,
    create_diagram_architect,
    create_formatting_filter,
    create_linkedin_architect,
    create_multi_variant_generator,
    create_tone_adjuster,
    create_twitter_architect,
    create_visual_prompter,
)


@pytest.mark.asyncio
async def test_formatting_filter_logic():
    """Verify that the filter removes prohibited elements."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = CreativeLintResult(
        clean_content="Clean.",
        changes_made=["Removed emoji"],
        has_prohibited_emojis=True,
    )

    with patch("backend.agents.creatives.FormattingFilter.__init__", return_value=None):
        filter_node = create_formatting_filter(mock_llm)
        filter_node.chain = mock_chain

        state = {"current_draft": "Clean🚀"}
        result = await filter_node(state)

        assert result["current_draft"] == "Clean."


@pytest.mark.asyncio
async def test_multi_variant_generator_logic():
    """Verify that the generator produces exactly 5 parallel variants."""
    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = MagicMock(content="Variant Content")

    generator = create_multi_variant_generator(mock_llm)
    state = {"current_draft": "SOTA"}
    result = await generator(state)

    assert len(result["variants"]) == 5
    assert mock_llm.ainvoke.call_count == 5


@pytest.mark.asyncio
async def test_diagram_architect_logic():
    """Verify that the architect creates structured SVG data."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = SVGDiagram(
        svg_code="<svg></svg>", explanation="A loop", accessibility_alt="Loop diagram"
    )

    with patch("backend.agents.creatives.DiagramArchitect.__init__", return_value=None):
        architect = create_diagram_architect(mock_llm)
        architect.chain = mock_chain

        state = {"current_draft": "Loop"}
        result = await architect(state)

        assert "<svg>" in result["final_output"]


@pytest.mark.asyncio
async def test_visual_prompter_logic():
    """Verify that the prompter creates structured image prompts."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = ImagePrompt(
        prompt_text="A clean desk", negative_prompt="clutter", aspect_ratio="16:9"
    )

    with patch("backend.agents.creatives.VisualPrompter.__init__", return_value=None):
        prompter = create_visual_prompter(mock_llm)
        prompter.chain = mock_chain

        state = {"current_draft": "SOTA", "research_bundle": {}}
        result = await prompter(state)

        assert result["current_brief"]["image_prompt"]["prompt_text"] == "A clean desk"


@pytest.mark.asyncio
async def test_tone_adjuster_logic():
    """Verify that the adjuster refines the draft tone."""
    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = MagicMock(content="Refined SOTA Copy")

    adjuster = create_tone_adjuster(mock_llm)
    state = {"current_draft": "Hype! Hype! Hype!"}
    result = await adjuster(state)

    assert result["current_draft"] == "Refined SOTA Copy"


@pytest.mark.asyncio
async def test_content_transformer_logic():
    """Verify that the transformer creates structured blog posts."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = BlogPost(
        title="SOTA AI",
        introduction="Intro.",
        key_sections=[{"title": "Section 1", "body": "Details."}],
        conclusion="Fin.",
    )

    with patch(
        "backend.agents.creatives.ContentTransformer.__init__", return_value=None
    ):
        transformer = create_content_transformer(mock_llm)
        transformer.chain = mock_chain

        state = {"research_bundle": {"executive_brief": "data"}}
        result = await transformer(state)

        assert result["variants"][0]["title"] == "SOTA AI"
        assert len(result["variants"][0]["key_sections"]) == 1


@pytest.mark.asyncio
async def test_ad_architect_logic():
    """Verify that the architect creates structured ad variations."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = AdAnalysis(
        ads=[
            AdCopy(
                platform="FB",
                headline="Stop Guessing.",
                body_text="Use Muse.",
                call_to_action="Get Started",
            )
        ]
    )

    with patch("backend.agents.creatives.AdArchitect.__init__", return_value=None):
        architect = create_ad_architect(mock_llm)
        architect.chain = mock_chain

        state = {"context_brief": {"uvps": {}, "icp_demographics": {}}}
        result = await architect(state)

        assert len(result["variants"]) == 1
        assert result["variants"][0]["headline"] == "Stop Guessing."


@pytest.mark.asyncio
async def test_twitter_architect_logic():
    """Verify that the architect creates structured threads."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = TwitterThread(
        hook_tweet="Why most SaaS fail.",
        body_tweets=["1/ Logic.", "2/ Speed."],
        closing_tweet="Follow for more.",
    )

    with patch("backend.agents.creatives.TwitterArchitect.__init__", return_value=None):
        architect = create_twitter_architect(mock_llm)
        architect.chain = mock_chain

        state = {"context_brief": {}, "research_bundle": {}}
        result = await architect(state)

        assert result["variants"][0]["hook_tweet"] == "Why most SaaS fail."
        assert len(result["variants"][0]["body_tweets"]) == 2


@pytest.mark.asyncio
async def test_linkedin_architect_logic():
    """Verify that the architect creates structured social posts."""
    mock_llm = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = LinkedInPost(
        hook="Stop guessing.",
        body="Systems win.",
        cta="Learn more.",
        post_vibe="Surgical",
    )

    with patch(
        "backend.agents.creatives.LinkedInArchitect.__init__", return_value=None
    ):
        architect = create_linkedin_architect(mock_llm)
        architect.chain = mock_chain

        state = {"context_brief": {}, "research_bundle": {}}
        result = await architect(state)

        assert result["variants"][0]["hook"] == "Stop guessing."
        assert "Systems win." in result["current_draft"]
