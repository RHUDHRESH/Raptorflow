import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from core.supabase_mgr import get_supabase_client

from ..state import AgentState

logger = logging.getLogger(__name__)


class DailyWinState(AgentState):
    """Extended state for the LangGraph Daily Wins Engine."""

    # Phase 1: Context Gathering
    bcm_manifest: Optional[Dict[str, Any]]
    internal_wins: List[Dict[str, Any]]
    recent_moves: List[Dict[str, Any]]
    active_campaigns: List[Dict[str, Any]]
    external_trends: List[Dict[str, Any]]

    # Phase 2: Synthesis & Architecture
    synthesized_narrative: Optional[str]
    target_platform: Literal["LinkedIn", "X (Twitter)", "Instagram", "Email"]

    # Phase 3: Content Generation
    content_draft: Optional[str]
    hooks: List[str]
    visual_prompt: Optional[str]

    # Phase 4: Reflection & Refinement
    surprise_score: float
    reflection_feedback: Optional[str]
    iteration_count: int
    max_iterations: int

    # Final Result
    final_win: Optional[Dict[str, Any]]


async def context_miner_node(state: DailyWinState) -> DailyWinState:
    """Node: Extracts internal BCM context using the Unified Context Builder."""
    try:
        workspace_id = state.get("workspace_id")
        supabase = get_supabase_client()

        from integration.context_builder import build_business_context_manifest
        from memory.controller import MemoryController

        # Build full BCM manifest
        memory_controller = MemoryController()
        manifest_data = await build_business_context_manifest(
            workspace_id=workspace_id,
            db_client=supabase,
            memory_controller=memory_controller,
        )

        state["bcm_manifest"] = manifest_data.get("content", {})

        # Map specific parts for easier access in subsequent nodes
        state["recent_moves"] = state["bcm_manifest"].get("current_moves", [])
        state["active_campaigns"] = state["bcm_manifest"].get("active_campaigns", [])

        # Still fetch past wins for continuity
        wins_res = (
            supabase.table("daily_wins")
            .select("*")
            .eq("workspace_id", workspace_id)
            .order("created_at", desc=True)
            .limit(3)
            .execute()
        )
        state["internal_wins"] = wins_res.data if wins_res.data else []

        logger.info(
            f"Context Miner (BCM): Extracted manifest for workspace {workspace_id}."
        )
        return state
    except Exception as e:
        logger.error(f"Context Miner Node Error: {e}")
        state["error"] = str(e)
        return state


async def trend_mapper_node(state: DailyWinState) -> DailyWinState:
    """Node: Fetches external trends via the Titan Intelligence Engine."""
    try:
        from services.titan.tool import TitanIntelligenceTool

        # Determine search queries based on BCM foundation/industry
        bcm = state.get("bcm_manifest") or {}
        foundation = bcm.get("foundation") or {}
        industry = foundation.get("industry", "marketing")
        business_name = foundation.get("business_name", "our startup")

        query = f"latest {industry} trends and news relevant to {business_name} LinkedIn Reddit"

        titan = TitanIntelligenceTool()
        result = await titan._arun(query=query, mode="LITE")

        if result.success:
            state["external_trends"] = result.data
        else:
            state["external_trends"] = []

        logger.info(
            f"Trend Mapper (Titan): Found trends via Titan Intelligence Engine."
        )
        return state
    except Exception as e:
        logger.error(f"Trend Mapper Node Error: {e}")
        state["external_trends"] = []
        return state


async def synthesizer_node(state: DailyWinState) -> DailyWinState:
    """Node: Bridges internal activity with external trends."""
    try:
        from specialists.daily_wins import DailyWinsGenerator

        agent = DailyWinsGenerator()

        moves_str = json.dumps(state.get("recent_moves", [])[:3])
        trends_str = json.dumps(state.get("external_trends", [])[:3])
        feedback = state.get("reflection_feedback", "None")

        prompt = f"""
        Merge these internal business 'moves' with these external market 'trends' to find a unique, contrarian angle for a {state.get('target_platform', 'LinkedIn')} post.

        INTERNAL MOVES: {moves_str}
        EXTERNAL TRENDS: {trends_str}

        PREVIOUS FEEDBACK (if any): {feedback}

        Focus on 'Editorial Restraint' and 'Surprise'. What is the one non-obvious synthesis?
        If feedback was provided, pivot your angle to address it while maintaining surprise.
        """

        narrative = await agent._call_llm(prompt)
        state["synthesized_narrative"] = narrative
        logger.info(f"Synthesizer: Narrative generated.")
        return state
    except Exception as e:
        logger.error(f"Synthesizer Node Error: {e}")
        state["error"] = str(e)
        return state


async def voice_architect_node(state: DailyWinState) -> DailyWinState:
    """Node: Enforces tone and editorial restraint."""
    try:
        from specialists.daily_wins import DailyWinsGenerator

        agent = DailyWinsGenerator()

        narrative = state.get("synthesized_narrative")
        if not narrative:
            state["error"] = "No narrative to architect."
            return state

        prompt = f"""
        Refine this narrative into a high-end, surgical post for {state['target_platform']}.
        Ensure it mirrors 'MasterClass polish + ChatGPT simplicity'.

        NARRATIVE: {narrative}

        Output only the final post content. No hashtags yet.
        """

        content = await agent._call_llm(prompt)
        state["content_draft"] = content
        logger.info(
            f"Voice Architect: Content draft refined for {state['target_platform']}."
        )
        return state
    except Exception as e:
        logger.error(f"Voice Architect Node Error: {e}")
        state["error"] = str(e)
        return state


async def hook_specialist_node(state: DailyWinState) -> DailyWinState:
    """Node: Generates viral hooks/headlines for the post."""
    try:
        from specialists.daily_wins import DailyWinsGenerator

        agent = DailyWinsGenerator()

        content = state.get("content_draft")
        if not content:
            state["error"] = "No content to generate hooks from."
            return state

        prompt = f"""
        Generate 3 attention-grabbing hooks/headlines for this post.
        Focus on 'Surprise' and 'Decisiveness'.

        POST CONTENT: {content}

        Output only a JSON list of strings.
        """

        res = await agent._call_llm(prompt)
        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            hooks = json.loads(clean_res)
            state["hooks"] = hooks if isinstance(hooks, list) else [res]
        except:
            state["hooks"] = [res]

        logger.info(f"Hook Specialist: {len(state['hooks'])} hooks generated.")
        return state
    except Exception as e:
        logger.error(f"Hook Specialist Node Error: {e}")
        state["hooks"] = []
        return state


async def visualist_node(state: DailyWinState) -> DailyWinState:
    """Node: Generates an editorial image prompt."""
    try:
        from specialists.daily_wins import DailyWinsGenerator

        agent = DailyWinsGenerator()

        content = state.get("content_draft")
        prompt = f"""
        Describe a high-end, cinematic, 'Quiet Luxury' style image that matches this post content.
        The image should feel like a custom editorial shot, not a generic stock photo.

        POST CONTENT: {content}

        Output only the image prompt.
        """

        image_prompt = await agent._call_llm(prompt)
        state["visual_prompt"] = image_prompt
        logger.info(f"Visualist: Image prompt generated.")
        return state
    except Exception as e:
        logger.error(f"Visualist Node Error: {e}")
        state["visual_prompt"] = None
        return state


async def skeptic_node(state: DailyWinState) -> DailyWinState:
    """Node: Evaluates the draft for 'Surprise' and 'Editorial Restraint'."""
    try:
        from specialists.daily_wins import DailyWinsGenerator

        agent = DailyWinsGenerator()

        content = state.get("content_draft")
        hooks = state.get("hooks", [])

        prompt = f"""
        You are the 'Skeptic/Editor'. Evaluate this LinkedIn post draft for:
        1. Surprise: Does it provide a non-obvious insight?
        2. Editorial Restraint: Is it brief and surgical?
        3. Decisiveness: Does it sound like a founder?

        DRAFT: {content}
        HOOKS: {hooks}

        Output only a JSON object: {{"score": float (0.0-1.0), "feedback": "string"}}
        """

        res = await agent._call_llm(prompt)
        state["iteration_count"] = state.get("iteration_count", 0) + 1

        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            eval_data = json.loads(clean_res)
            state["surprise_score"] = float(eval_data.get("score", 0.0))
            state["reflection_feedback"] = eval_data.get("feedback", "No feedback.")
        except:
            state["surprise_score"] = 0.5
            state["reflection_feedback"] = "Failed to parse score."

        if state["surprise_score"] >= 0.8:
            # Calculate additional metrics using agent logic
            # Use simple class or dict for mocks to satisfy attribute access
            class MockObj:
                def __init__(self, **kwargs):
                    self.__dict__.update(kwargs)

            mock_req = MockObj(content_type="social", urgency="normal")
            mock_angle = MockObj(
                engagement_potential=state["surprise_score"],
                hook_type="controversy",
                emotional_trigger="surprise",
            )

            engagement = agent._calculate_engagement_prediction(
                mock_req, mock_angle, content or ""
            )
            viral = agent._calculate_viral_potential(
                mock_req, mock_angle, content or ""
            )

            state["final_win"] = {
                "id": f"WIN-{uuid.uuid4().hex[:8]}",
                "topic": state.get("target_platform", "LinkedIn") + " Insight",
                "angle": "Surprise Synthesis",
                "hook": content,
                "outline": hooks,
                "content": content,
                "hooks": hooks,
                "visual_prompt": state.get("visual_prompt"),
                "score": state["surprise_score"],
                "engagement_prediction": engagement,
                "viral_potential": viral,
                "follow_up_ideas": [
                    "Deep dive into the synthesis methodology",
                    "Community Q&A on this contrarian take",
                ],
                "platform": state.get("target_platform", "LinkedIn"),
                "timeToPost": "~10 min",
                "generated_at": datetime.now().isoformat(),
            }
            logger.info(
                f"Skeptic: Draft APPROVED with score {state['surprise_score']}."
            )
        else:
            logger.info(
                f"Skeptic: Draft REJECTED with score {state['surprise_score']}. Feedback: {state['reflection_feedback']}"
            )

        return state
    except Exception as e:
        logger.error(f"Skeptic Node Error: {e}")
        state["surprise_score"] = 0.0
        return state


def should_continue(state: DailyWinState) -> Literal["synthesizer", END]:
    """Conditional edge to decide if we should retry synthesis."""
    if state.get("final_win"):
        return END

    if state.get("iteration_count", 0) >= state.get("max_iterations", 3):
        logger.warning("Max iterations reached. Ending with best effort.")
        return END

    return "synthesizer"


class DailyWinsGraph:
    """The LangGraph Orchestrator for Daily Wins."""

    def __init__(self):
        workflow = StateGraph(DailyWinState)

        # Define Nodes
        workflow.add_node("context_miner", context_miner_node)
        workflow.add_node("trend_mapper", trend_mapper_node)
        workflow.add_node("synthesizer", synthesizer_node)
        workflow.add_node("voice_architect", voice_architect_node)
        workflow.add_node("hook_specialist", hook_specialist_node)
        workflow.add_node("visualist", visualist_node)
        workflow.add_node("skeptic", skeptic_node)

        # Build Graph
        workflow.set_entry_point("context_miner")

        workflow.add_edge("context_miner", "trend_mapper")
        workflow.add_edge("trend_mapper", "synthesizer")
        workflow.add_edge("synthesizer", "voice_architect")
        workflow.add_edge("voice_architect", "hook_specialist")
        workflow.add_edge("hook_specialist", "visualist")
        workflow.add_edge("visualist", "skeptic")

        # Conditional Edge (Retry loop)
        workflow.add_conditional_edges(
            "skeptic", should_continue, {"synthesizer": "synthesizer", END: END}
        )

        self.memory = MemorySaver()
        self.app = workflow.compile(checkpointer=self.memory)

    async def run(self, workspace_id: str, user_id: str, platform: str = "LinkedIn"):
        """Executes the graph."""
        initial_state = {
            "workspace_id": workspace_id,
            "user_id": user_id,
            "target_platform": platform,
            "iteration_count": 0,
            "max_iterations": 3,
            "messages": [],
        }

        config = {
            "configurable": {
                "thread_id": f"dw_{workspace_id}_{datetime.now().strftime('%Y%m%d')}"
            }
        }

        final_state = await self.app.ainvoke(initial_state, config=config)
        return final_state
