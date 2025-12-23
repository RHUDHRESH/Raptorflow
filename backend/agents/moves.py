import logging
from typing import List, TypedDict, Optional
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
    priority: str = Field(default="P1", description="P0 (Critical), P1 (Standard), P2 (Optional)")
    estimated_effort: str = Field(default="Medium", description="Low, Medium, High")
    required_skills: List[str] = Field(default_factory=list, description="Skills needed: Search, Copy, ImageGen, etc.")
    deadline: Optional[str] = Field(None, description="ISO format deadline for completion.")

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
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", MovePrompts.GENERATOR_SYSTEM),
            ("user", MovePrompts.MOVE_GENERATION)
        ])
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
            sequence = await self.chain.ainvoke({
                "arc": str(campaign_arc),
                "month_number": month_num,
                "theme": theme,
                "objective": obj
            })
            all_moves.extend([m.model_dump() for m in sequence.moves])
        
        logger.info(f"Move generation complete. Generated {len(all_moves)} moves across the arc.")
        
        return {"current_moves": all_moves, "messages": [f"Generated {len(all_moves)} weekly moves for the 90-day arc."]}

class MoveRefiner:
    """
    SOTA Move Refinement Node.
    Ensures moves are actionable and production-ready.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", MovePrompts.REFINER_SYSTEM),
            ("user", "Please refine this move: {move_data}")
        ])
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
            
        return {"current_moves": refined_moves, "messages": ["Refined weekly moves for production readiness."]}
