from typing import Any, Dict, List, Optional, TypedDict, Literal
from datetime import datetime
import logging
import json

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from ..state import AgentState
from backend.core.supabase_mgr import get_supabase_client
from backend.services.search.searxng import SearXNGClient

logger = logging.getLogger(__name__)

class DailyWinState(AgentState):
    """Extended state for the LangGraph Daily Wins Engine."""
    
    # Phase 1: Context Gathering
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

# Schema for the 7 skills' inputs and outputs (Nodes)

async def context_miner_node(state: DailyWinState) -> DailyWinState:
    """Node: Extracts internal BCM context (wins, moves, campaigns)."""
    try:
        workspace_id = state.get("workspace_id")
        supabase = get_supabase_client()
        
        # 1. Fetch recent moves
        moves_res = supabase.table("moves").select("*").eq("workspace_id", workspace_id).order("created_at", desc=True).limit(5).execute()
        state["recent_moves"] = moves_res.data if moves_res.data else []
        
        # 2. Fetch active campaigns
        campaigns_res = supabase.table("campaigns").select("*").eq("workspace_id", workspace_id).eq("status", "active").execute()
        state["active_campaigns"] = campaigns_res.data if campaigns_res.data else []
        
        # 3. Fetch past daily wins for context
        wins_res = supabase.table("daily_wins").select("*").eq("workspace_id", workspace_id).order("created_at", desc=True).limit(3).execute()
        state["internal_wins"] = wins_res.data if wins_res.data else []
        
        logger.info(f"Context Miner: Extracted {len(state['recent_moves'])} moves and {len(state['active_campaigns'])} campaigns.")
        return state
    except Exception as e:
        logger.error(f"Context Miner Node Error: {e}")
        state["error"] = str(e)
        return state

async def trend_mapper_node(state: DailyWinState) -> DailyWinState:
    """Node: Fetches external trends via search tools (SearXNG, Reddit)."""
    try:
        # Determine search queries based on foundation/industry
        foundation = state.get("foundation_summary", "marketing trends")
        query = f"latest {foundation} trends LinkedIn Reddit"
        
        searxng = SearXNGClient()
        trends = await searxng.query(query, limit=5)
        await searxng.close()
        
        state["external_trends"] = trends
        logger.info(f"Trend Mapper: Found {len(trends)} external trends.")
        return state
    except Exception as e:
        logger.error(f"Trend Mapper Node Error: {e}")
        state["external_trends"] = [] # Fallback to empty
        return state


async def synthesizer_node(state: DailyWinState) -> DailyWinState:


    """Node: Bridges internal activity with external trends."""


    try:


        from ..specialists.daily_wins import DailyWinsGenerator


        agent = DailyWinsGenerator()


        


        # 1. Prepare data for synthesis


        moves_str = json.dumps(state.get("recent_moves", [])[:3])


        trends_str = json.dumps(state.get("external_trends", [])[:3])


        


        prompt = f"""


        Merge these internal business 'moves' with these external market 'trends' to find a unique, contrarian angle for a LinkedIn post.


        


        INTERNAL MOVES: {moves_str}


        EXTERNAL TRENDS: {trends_str}


        


        Focus on 'Editorial Restraint' and 'Surprise'. What is the one non-obvious synthesis?


        """


        


        # Use existing agent's LLM capability


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


        from ..specialists.daily_wins import DailyWinsGenerator


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


        logger.info(f"Voice Architect: Content draft refined for {state['target_platform']}.")


        return state


    except Exception as e:


        logger.error(f"Voice Architect Node Error: {e}")


        state["error"] = str(e)


        return state





async def hook_specialist_node(state: DailyWinState) -> DailyWinState:
    """Node: Generates viral hooks/headlines for the post."""
    try:
        from ..specialists.daily_wins import DailyWinsGenerator
        agent = DailyWinsGenerator()
        
        content = state.get("content_draft")
        if not content:
            state["error"] = "No content to generate hooks from."
            return state
            
        prompt = """
        Generate 3 attention-grabbing hooks/headlines for this post.
        Focus on 'Surprise' and 'Decisiveness'.
        
        POST CONTENT: {content}
        
        Output only a JSON list of strings.
        """
        
        res = await agent._call_llm(prompt)
        # Attempt to parse JSON list
        try:
            # Basic cleanup if LLM includes markdown
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
        from ..specialists.daily_wins import DailyWinsGenerator
        agent = DailyWinsGenerator()
        
        content = state.get("content_draft")
        prompt = """
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
        from ..specialists.daily_wins import DailyWinsGenerator
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
        
        Output only a JSON object: {{\"score\": float (0.0-1.0), \"feedback\": \"string\"}}
        """
        
        res = await agent._call_llm(prompt)
        # Increment iteration count
        state["iteration_count"] = state.get("iteration_count", 0) + 1
        
        try:
            clean_res = res.strip().replace("```json", "").replace("```", "")
            eval_data = json.loads(clean_res)
            state["surprise_score"] = float(eval_data.get("score", 0.0))
            state["reflection_feedback"] = eval_data.get("feedback", "No feedback.")
        except:
            state["surprise_score"] = 0.5
            state["reflection_feedback"] = "Failed to parse score."
            
        # Final win logic
        if state["surprise_score"] >= 0.8:
            state["final_win"] = {
                "content": content,
                "hooks": hooks,
                "visual_prompt": state.get("visual_prompt"),
                "score": state["surprise_score"],
                "generated_at": datetime.now().isoformat()
            }
            logger.info(f"Skeptic: Draft APPROVED with score {state['surprise_score']}.")
        else:
            logger.info(f"Skeptic: Draft REJECTED with score {state['surprise_score']}. Feedback: {state['reflection_feedback']}")
            
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
            "skeptic",
            should_continue,
            {
                "synthesizer": "synthesizer",
                END: END
            }
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
            "messages": []
        }
        
        config = {"configurable": {"thread_id": f"dw_{workspace_id}_{datetime.now().strftime('%Y%m%d')}"}}
        
        final_state = await self.app.ainvoke(initial_state, config=config)
        return final_state
