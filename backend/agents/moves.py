import logging
from typing import List, Optional, TypedDict

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from backend.core.prompts import MovePrompts

logger = logging.getLogger("raptorflow.agents.moves")


class ExecutionMove(BaseModel):
    """SOTA structured representation of a weekly execution packet."""

    week_number: int
    title: str
    action_items: List[str] = Field(description="Exactly 3-5 surgical action items.")
    desired_outcome: str
    priority: str = Field(
        default="P1", description="P0 (Critical), P1 (Standard), P2 (Optional)"
    )
    estimated_effort: str = Field(default="Medium", description="Low, Medium, High")
    required_skills: List[str] = Field(
        default_factory=list, description="Skills needed: Search, Copy, ImageGen, etc."
    )
    deadline: Optional[str] = Field(
        None, description="ISO format deadline for completion."
    )


ExecutionMove.model_rebuild()


class MoveSequence(BaseModel):
    """The granular weekly breakdown of a month in a campaign."""

    moves: List[ExecutionMove]


class MoveGenerator:
    """
    SOTA Weekly Execution Node.
    Breaks 90-day arcs into granular, weekly 'Moves' using Gemini Ultra Reasoning.
    """

    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", MovePrompts.GENERATOR_SYSTEM),
                ("user", MovePrompts.MOVE_GENERATION),
            ]
        )
        self.chain = self.prompt | llm.with_structured_output(MoveSequence)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        campaign_arc = state.get("context_brief", {}).get("campaign_arc", {})
        # For simplicity, we generate moves for all 3 months if not specified,
        # but the prompt asks for one month. Let's adapt.

        all_moves = []
        monthly_plans = campaign_arc.get("monthly_plans", [])

        logger.info(f"Generating weekly moves for {len(monthly_plans)} months...")

        for month in monthly_plans:
            month_num = month.get("month_number")
            theme = month.get("theme")
            obj = month.get("key_objective")

            logger.info(f"Sequencing month {month_num}: {theme}")
            sequence = await self.chain.ainvoke(
                {
                    "arc": str(campaign_arc),
                    "month_number": month_num,
                    "theme": theme,
                    "objective": obj,
                }
            )
            all_moves.extend([m.model_dump() for m in sequence.moves])

        logger.info(
            f"Move generation complete. Generated {len(all_moves)} moves across the arc."
        )

        return {
            "current_moves": all_moves,
            "messages": [
                f"Generated {len(all_moves)} weekly moves for the 90-day arc."
            ],
        }


class MoveRefiner:
    """
    SOTA Move Refinement Node.
    Ensures moves are actionable and production-ready.
    """

    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", MovePrompts.REFINER_SYSTEM),
                ("user", "Please refine this move: {move_data}"),
            ]
        )
        self.chain = self.prompt | llm.with_structured_output(ExecutionMove)

    async def __call__(self, state: TypedDict):
        """Node execution logic for refinement."""
        moves = state.get("current_moves", [])
        if not moves:
            return {"messages": ["WARNING: No moves found to refine."]}

        # Refine the latest/current set of moves or just a subset
        # For now, let's refine all generated moves to ensure quality
        refined_moves = []
        for move in moves:
            refined = await self.chain.ainvoke({"move_data": str(move)})
            refined_moves.append(refined.model_dump())

        return {
            "current_moves": refined_moves,
            "messages": ["Refined weekly moves for production readiness."],
        }


class ResourceManager:
    """
    SOTA Resource Management Node.
    Checks if the required tools/skills for a move are available in the current environment.
    """

    AVAILABLE_TOOLS = ["Search", "Copy", "ImageGen", "SocialAPI", "Analytics"]

    async def __call__(self, state: TypedDict):
        """Verify tool availability for the generated moves."""
        moves = state.get("current_moves", [])
        if not moves:
            return {"messages": ["WARNING: No moves for resource check."]}

        validated_moves = []
        messages = []

        for move in moves:
            required = move.get("required_skills", [])
            missing = [tool for tool in required if tool not in self.AVAILABLE_TOOLS]

            if missing:
                messages.append(
                    f"WARNING: Move '{move.get('title')}' requires unavailable tools: {missing}"
                )
                # Mark for adjustment or lower priority
                move["priority"] = "P2"
            else:
                messages.append(f"✓ Resources verified for: {move.get('title')}")

            validated_moves.append(move)

        return {"current_moves": validated_moves, "messages": messages}


class ProgressTracker:
    """
    SOTA Progress Tracking Node.
    Calculates overall campaign progress based on move completion status.
    """

    async def __call__(self, state: TypedDict):
        """Update campaign progress based on current move statuses."""
        moves = state.get("current_moves", [])
        if not moves:
            return {"messages": ["No moves found to calculate progress."]}

        # In a real scenario, we'd fetch ALL moves for the campaign from DB.
        # For the graph node, we estimate based on the current context.
        total_moves = len(moves)
        completed_moves = len([m for m in moves if m.get("status") == "executed"])

        progress = completed_moves / total_moves if total_moves > 0 else 0.0

        return {
            "quality_score": progress,  # Using quality_score as a proxy for progress in state
            "messages": [f"Campaign progress updated: {progress*100:.1f}%"],
        }


from backend.db import save_move, log_agent_decision
from backend.core.toolbelt import ToolbeltV2


class SkillExecutor:
    """
    SOTA Skill Execution Node.
    Orchestrates tool calls for a move based on its required skills.
    """

    def __init__(self):
        self.belt = ToolbeltV2()

    async def __call__(self, state: TypedDict):
        """Execute tools for the current moves."""
        moves = state.get("current_moves", [])
        if not moves:
            return {"messages": ["No moves found for skill execution."]}

        results = []
        messages = []

        for move in moves:
            # Map required_skills to tool_names in ToolbeltV2.
            skill_map = {
                "Search": "tavily_search",
                "Copy": "asset_gen",
                "ImageGen": "asset_gen", # Muse handles both for now
                "Research": "perplexity_search"
            }

            for skill in move.get("required_skills", []):
                tool_name = skill_map.get(skill)
                if tool_name:
                    logger.info(f"Executing skill '{skill}' via tool '{tool_name}'...")
                    
                    # Prepare tool inputs based on skill type
                    tool_kwargs = {"query": move.get("title")} # Default
                    if skill in ["Copy", "ImageGen"]:
                        tool_kwargs = {
                            "topic": move.get("title"),
                            "format": "LinkedIn Post" if skill == "Copy" else "Image Prompt",
                            "context": move.get("description")
                        }

                    res = await self.belt.run_tool(tool_name, **tool_kwargs)
                    
                    if res["success"]:
                        results.append({
                            "move_id": move.get("db_id"),
                            "skill": skill,
                            "tool": tool_name,
                            "output": res["data"]
                        })
                        messages.append(f"✓ Skill '{skill}' executed for move '{move.get('title')}'")
                    else:
                        messages.append(f"✗ Skill '{skill}' failed: {res['error']}")

        return {"pending_moves": results, "messages": messages}


class SafetyValidator:
    """
    SOTA Safety Validation Node.
    Ensures tool outputs and agent decisions meet safety and brand guidelines.
    """

    BLOCKED_KEYWORDS = ["competitor_leak", "offensive_term", "internal_secret"]

    async def __call__(self, state: TypedDict):
        """Validate tool outputs in the state."""
        pending_results = state.get("pending_moves", [])
        messages = []
        is_safe = True

        for item in pending_results:
            content = str(item.get("output", ""))
            for word in self.BLOCKED_KEYWORDS:
                if word in content.lower():
                    messages.append(f"⚠ Safety violation in tool output: {word}")
                    is_safe = False

        if is_safe:
            messages.append("✓ Safety validation passed for all tool outputs.")

        return {"status": "complete" if is_safe else "error", "messages": messages}

    async def __call__(self, state: TypedDict):
        """Persist generated moves to the database."""
        tenant_id = state.get("tenant_id")
        campaign_id = state.get("campaign_id")
        moves = state.get("current_moves", [])

        if not tenant_id or not campaign_id:
            return {"messages": ["WARNING: Missing tenant_id or campaign_id for persistence."]}

        if not moves:
            return {"messages": ["No moves found to persist."]}

        messages = []
        for move in moves:
            # Map ExecutionMove fields to DB schema
            db_move = {
                "title": move.get("title"),
                "description": f"{move.get('desired_outcome')} - Actions: {', '.join(move.get('action_items', []))}",
                "status": "pending",
                "priority": int(move.get("priority", "P1").replace("P", "")),
                "move_type": "automated",  # Default for now
                "tool_requirements": move.get("required_skills", []),
            }
            move_uuid = await save_move(campaign_id, db_move)
            move["db_id"] = move_uuid
            messages.append(f"✓ Move '{move.get('title')}' persisted to DB.")

        # Log the generation decision
        await log_agent_decision(
            tenant_id=tenant_id,
            decision_data={
                "agent_id": "MoveGenerator",
                "decision_type": "move_gen",
                "input_state": {"campaign_id": campaign_id},
                "output_decision": {"move_count": len(moves)},
                "rationale": f"Generated {len(moves)} weekly moves for campaign {campaign_id}",
            },
        )

        return {"current_moves": moves, "messages": messages}
