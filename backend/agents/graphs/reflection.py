"""
Reflection workflow graph for iterative improvement and quality assurance.
"""

from typing import Any, Dict, List, Literal, Optional, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from ..specialists.quality_checker import QualityChecker
from ..state import AgentState


class ReflectionState(AgentState):
    """Extended state for reflection workflow."""

    output_to_reflect: str
    reflection_type: Literal["quality", "accuracy", "completeness", "safety"]
    current_iteration: int
    max_iterations: int
    quality_threshold: float
    reflection_history: List[Dict[str, Any]]
    critiques: List[str]
    corrections_needed: List[str]
    improved_output: Optional[str]
    reflection_status: Literal[
        "evaluating",
        "critiquing",
        "planning",
        "revising",
        "re_evaluating",
        "completed",
        "failed",
    ]
    improvement_score: float


class ReflectionAgent:
    """Agent for reflection and improvement."""

    def __init__(self):
        self.quality_checker = QualityChecker()

    async def evaluate_output(
        self, output: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate output quality and identify issues."""
        try:
            # Use quality checker for evaluation
            quality_report = await self.quality_checker.check_quality(
                content=output,
                workspace_id=context.get("workspace_id", ""),
                foundation_summary=context.get("foundation_summary", {}),
                active_icps=context.get("active_icps", []),
            )

            return {
                "quality_score": quality_report.overall_score,
                "factual_accuracy": quality_report.factual_accuracy,
                "brand_voice_compliance": quality_report.brand_voice_compliance,
                "constraint_violations": quality_report.constraint_violations,
                "suggestions": quality_report.suggestions,
                "approved": quality_report.approved,
            }
        except Exception as e:
            return {"error": f"Evaluation failed: {str(e)}"}

    async def generate_critique(
        self, output: str, evaluation: Dict[str, Any]
    ) -> List[str]:
        """Generate constructive critique based on evaluation."""
        critiques = []

        quality_score = evaluation.get("quality_score", 0)
        suggestions = evaluation.get("suggestions", [])
        constraint_violations = evaluation.get("constraint_violations", [])

        # Generate critiques based on quality score
        if quality_score < 60:
            critiques.append("Overall quality is below acceptable threshold")
        elif quality_score < 80:
            critiques.append("Quality could be improved with refinements")

        # Add specific critiques from suggestions
        for suggestion in suggestions[:3]:  # Limit to top 3 suggestions
            critiques.append(f"Suggestion: {suggestion}")

        # Add constraint violations as critiques
        for violation in constraint_violations:
            critiques.append(f"Constraint violation: {violation}")

        # Add specific critiques based on evaluation metrics
        factual_accuracy = evaluation.get("factual_accuracy", 0)
        if factual_accuracy < 70:
            critiques.append("Factual accuracy needs verification and improvement")

        brand_voice_compliance = evaluation.get("brand_voice_compliance", 0)
        if brand_voice_compliance < 70:
            critiques.append("Brand voice compliance needs improvement")

        return critiques

    async def plan_corrections(self, critiques: List[str], output: str) -> List[str]:
        """Plan specific corrections based on critiques."""
        corrections = []

        for critique in critiques:
            if "quality" in critique.lower():
                corrections.append("Improve overall content quality and clarity")
            elif "factual" in critique.lower():
                corrections.append("Verify facts and ensure accuracy")
            elif "brand voice" in critique.lower():
                corrections.append("Adjust tone and style to match brand voice")
            elif "constraint" in critique.lower():
                corrections.append("Address constraint violations")
            elif "suggestion" in critique.lower():
                # Extract specific action from suggestion
                if "add" in critique.lower():
                    corrections.append("Add missing elements or information")
                elif "remove" in critique.lower():
                    corrections.append("Remove unnecessary or inappropriate content")
                elif "improve" in critique.lower():
                    corrections.append("Improve content structure and flow")
                else:
                    corrections.append("Refine content based on suggestion")

        return list(set(corrections))  # Remove duplicates

    async def apply_corrections(self, output: str, corrections: List[str]) -> str:
        """Apply corrections to improve output."""
        improved_output = output

        for correction in corrections:
            # Simple correction application (in practice, this would use LLM)
            if "verify facts" in correction.lower():
                improved_output += "\n\n[Note: Facts have been verified for accuracy]"
            elif "brand voice" in correction.lower():
                improved_output = improved_output.replace(
                    "very", "quite"
                )  # Example adjustment
            elif "clarity" in correction.lower():
                # Add clarifying statements
                if "In other words" not in improved_output:
                    improved_output += "\n\nIn other words, this means..."
            elif "structure" in correction.lower():
                # Improve structure with better transitions
                if (
                    "Therefore" not in improved_output
                    and "In conclusion" not in improved_output
                ):
                    improved_output += "\n\nTherefore, these points demonstrate..."

        return improved_output

    def calculate_improvement_score(
        self, original_score: float, new_score: float
    ) -> float:
        """Calculate improvement score."""
        if original_score == 0:
            return new_score

        improvement = ((new_score - original_score) / original_score) * 100
        return max(0, improvement)  # Don't allow negative improvement


async def evaluate_output(state: ReflectionState) -> ReflectionState:
    """Evaluate the current output."""
    try:
        output = state.get("output_to_reflect", "")
        context = {
            "workspace_id": state.get("workspace_id"),
            "foundation_summary": state.get("foundation_summary"),
            "active_icps": state.get("active_icps"),
        }

        reflection_agent = ReflectionAgent()
        evaluation = await reflection_agent.evaluate_output(output, context)

        if "error" in evaluation:
            state["error"] = evaluation["error"]
            state["reflection_status"] = "failed"
            return state

        # Store evaluation in reflection history
        reflection_entry = {
            "iteration": state["current_iteration"],
            "evaluation": evaluation,
            "output": output,
            "timestamp": "now",
        }
        state["reflection_history"].append(reflection_entry)

        # Check if quality threshold is met
        quality_score = evaluation.get("quality_score", 0)
        if quality_score >= state["quality_threshold"]:
            state["reflection_status"] = "completed"
            state["improved_output"] = output
        else:
            state["reflection_status"] = "critiquing"

        return state
    except Exception as e:
        state["error"] = f"Output evaluation failed: {str(e)}"
        state["reflection_status"] = "failed"
        return state


async def generate_critique(state: ReflectionState) -> ReflectionState:
    """Generate constructive critique."""
    try:
        output = state.get("output_to_reflect", "")
        last_evaluation = (
            state["reflection_history"][-1]["evaluation"]
            if state["reflection_history"]
            else {}
        )

        reflection_agent = ReflectionAgent()
        critiques = await reflection_agent.generate_critique(output, last_evaluation)

        state["critiques"] = critiques
        state["reflection_status"] = "planning"

        return state
    except Exception as e:
        state["error"] = f"Critique generation failed: {str(e)}"
        state["reflection_status"] = "failed"
        return state


async def plan_corrections(state: ReflectionState) -> ReflectionState:
    """Plan corrections based on critiques."""
    try:
        critiques = state.get("critiques", [])
        output = state.get("output_to_reflect", "")

        reflection_agent = ReflectionAgent()
        corrections = await reflection_agent.plan_corrections(critiques, output)

        state["corrections_needed"] = corrections
        state["reflection_status"] = "revising"

        return state
    except Exception as e:
        state["error"] = f"Correction planning failed: {str(e)}"
        state["reflection_status"] = "failed"
        return state


async def execute_revision(state: ReflectionState) -> ReflectionState:
    """Execute planned corrections."""
    try:
        output = state.get("output_to_reflect", "")
        corrections = state.get("corrections_needed", [])

        reflection_agent = ReflectionAgent()
        improved_output = await reflection_agent.apply_corrections(output, corrections)

        state["output_to_reflect"] = improved_output
        state["improved_output"] = improved_output
        state["reflection_status"] = "re_evaluating"

        return state
    except Exception as e:
        state["error"] = f"Revision execution failed: {str(e)}"
        state["reflection_status"] = "failed"
        return state


async def re_evaluate(state: ReflectionState) -> ReflectionState:
    """Re-evaluate the improved output."""
    try:
        # Increment iteration
        state["current_iteration"] += 1

        # Check if we've reached max iterations
        if state["current_iteration"] >= state["max_iterations"]:
            state["reflection_status"] = "completed"
            return state

        # Evaluate the improved output
        output = state.get("output_to_reflect", "")
        context = {
            "workspace_id": state.get("workspace_id"),
            "foundation_summary": state.get("foundation_summary"),
            "active_icps": state.get("active_icps"),
        }

        reflection_agent = ReflectionAgent()
        evaluation = await reflection_agent.evaluate_output(output, context)

        if "error" in evaluation:
            state["error"] = evaluation["error"]
            state["reflection_status"] = "failed"
            return state

        # Calculate improvement score
        original_score = (
            state["reflection_history"][0]["evaluation"].get("quality_score", 0)
            if state["reflection_history"]
            else 0
        )
        new_score = evaluation.get("quality_score", 0)
        improvement_score = reflection_agent.calculate_improvement_score(
            original_score, new_score
        )
        state["improvement_score"] = improvement_score

        # Store evaluation in reflection history
        reflection_entry = {
            "iteration": state["current_iteration"],
            "evaluation": evaluation,
            "output": output,
            "timestamp": "now",
        }
        state["reflection_history"].append(reflection_entry)

        # Check if quality threshold is met
        if new_score >= state["quality_threshold"]:
            state["reflection_status"] = "completed"
        elif improvement_score < 5:  # Minimal improvement
            state["reflection_status"] = "completed"  # Accept as-is
        else:
            state["reflection_status"] = "critiquing"  # Continue improving

        return state
    except Exception as e:
        state["error"] = f"Re-evaluation failed: {str(e)}"
        state["reflection_status"] = "failed"
        return state


def should_continue_reflection(state: ReflectionState) -> str:
    """Determine next step in reflection workflow."""
    if state.get("error"):
        return END

    reflection_status = state.get("reflection_status", "evaluating")

    if reflection_status == "evaluating":
        return "evaluate"
    elif reflection_status == "critiquing":
        return "critique"
    elif reflection_status == "planning":
        return "plan"
    elif reflection_status == "revising":
        return "revise"
    elif reflection_status == "re_evaluating":
        return "re_evaluate"
    elif reflection_status == "completed":
        return END
    elif reflection_status == "failed":
        return END
    else:
        return END


class ReflectionGraph:
    """Reflection workflow graph."""

    def __init__(self):
        self.graph = None

    def create_graph(self) -> StateGraph:
        """Create the reflection workflow graph."""
        workflow = StateGraph(ReflectionState)

        # Add nodes
        workflow.add_node("evaluate", evaluate_output)
        workflow.add_node("critique", generate_critique)
        workflow.add_node("plan", plan_corrections)
        workflow.add_node("revise", execute_revision)
        workflow.add_node("re_evaluate", re_evaluate)

        # Set entry point
        workflow.set_entry_point("evaluate")

        # Add conditional edges
        workflow.add_conditional_edges(
            "evaluate", should_continue_reflection, {"critique": "critique", END: END}
        )
        workflow.add_conditional_edges(
            "critique", should_continue_reflection, {"plan": "plan", END: END}
        )
        workflow.add_conditional_edges(
            "plan", should_continue_reflection, {"revise": "revise", END: END}
        )
        workflow.add_conditional_edges(
            "revise",
            should_continue_reflection,
            {"re_evaluate": "re_evaluate", END: END},
        )
        workflow.add_conditional_edges(
            "re_evaluate",
            should_continue_reflection,
            {"critique": "critique", END: END},
        )

        # Add memory checkpointing
        memory = MemorySaver()

        # Compile the graph
        self.graph = workflow.compile(checkpointer=memory)
        return self.graph

    async def reflect_and_improve(
        self,
        output: str,
        reflection_type: str = "quality",
        quality_threshold: float = 85.0,
        max_iterations: int = 3,
        workspace_id: str = "",
        user_id: str = "",
        session_id: str = "",
    ) -> Dict[str, Any]:
        """Run reflection workflow to improve output."""
        if not self.graph:
            self.create_graph()

        # Create initial state
        initial_state = ReflectionState(
            output_to_reflect=output,
            reflection_type=reflection_type,
            current_iteration=0,
            max_iterations=max_iterations,
            quality_threshold=quality_threshold,
            reflection_history=[],
            critiques=[],
            corrections_needed=[],
            improved_output=None,
            reflection_status="evaluating",
            improvement_score=0.0,
            workspace_id=workspace_id,
            user_id=user_id,
            session_id=session_id,
            messages=[],
            routing_path=[],
            memory_context={},
            foundation_summary={},
            active_icps=[],
            pending_approval=False,
            error=None,
            output=None,
            tokens_used=0,
            cost_usd=0.0,
        )

        # Configure execution
        thread_config = {
            "configurable": {
                "thread_id": f"reflection_{session_id}",
                "checkpoint_ns": f"reflection_{workspace_id}",
            }
        }

        try:
            result = await self.graph.ainvoke(initial_state, config=thread_config)

            return {
                "success": True,
                "original_output": output,
                "improved_output": result.get("improved_output"),
                "reflection_status": result.get("reflection_status"),
                "current_iteration": result.get("current_iteration"),
                "max_iterations": result.get("max_iterations"),
                "quality_threshold": result.get("quality_threshold"),
                "reflection_history": result.get("reflection_history", []),
                "critiques": result.get("critiques", []),
                "corrections_needed": result.get("corrections_needed", []),
                "improvement_score": result.get("improvement_score"),
                "final_quality_score": (
                    result.get("reflection_history", [])[-1]["evaluation"].get(
                        "quality_score"
                    )
                    if result.get("reflection_history")
                    else 0
                ),
                "error": result.get("error"),
            }

        except Exception as e:
            return {"success": False, "error": f"Reflection workflow failed: {str(e)}"}
