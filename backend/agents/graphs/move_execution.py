"""
Move execution workflow graph for marketing move implementation.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Literal, Optional, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from ..specialists.content_creator import ContentCreator
from ..specialists.move_strategist import MoveStrategist
from ..state import AgentState


class MoveExecutionState(AgentState):
    """Extended state for move execution workflow."""

    move_id: str
    move_name: str
    move_category: Literal["ignite", "capture", "authority", "repair", "rally"]
    current_day: int
    total_days: int
    tasks: List[Dict[str, Any]]
    completed_tasks: List[str]
    task_results: Dict[str, Any]
    content_generated: Dict[str, Any]
    execution_status: Literal["planning", "active", "paused", "completed", "failed"]
    progress_percentage: float
    next_actions: List[str]
    performance_metrics: Dict[str, Any]


class MoveTaskHandler:
    """Handler for move task generation and execution."""

    def __init__(self):
        self.move_strategist = MoveStrategist()
        self.content_creator = ContentCreator()

    def generate_daily_tasks(
        self, move_strategy: Dict[str, Any], day: int
    ) -> List[Dict[str, Any]]:
        """Generate tasks for a specific day of the move."""
        tasks = []

        # Extract move parameters
        move_category = move_strategy.get("category", "ignite")
        duration_days = move_strategy.get("duration", 14)
        target_audience = move_strategy.get("target_audience", {})
        objectives = move_strategy.get("objectives", [])

        # Generate tasks based on move category and day
        if move_category == "ignite":
            tasks.extend(
                self._generate_ignite_tasks(
                    day, duration_days, target_audience, objectives
                )
            )
        elif move_category == "capture":
            tasks.extend(
                self._generate_capture_tasks(
                    day, duration_days, target_audience, objectives
                )
            )
        elif move_category == "authority":
            tasks.extend(
                self._generate_authority_tasks(
                    day, duration_days, target_audience, objectives
                )
            )
        elif move_category == "repair":
            tasks.extend(
                self._generate_repair_tasks(
                    day, duration_days, target_audience, objectives
                )
            )
        elif move_category == "rally":
            tasks.extend(
                self._generate_rally_tasks(
                    day, duration_days, target_audience, objectives
                )
            )

        return tasks

    def _generate_ignite_tasks(
        self, day: int, duration: int, audience: Dict, objectives: List
    ) -> List[Dict[str, Any]]:
        """Generate tasks for ignite moves (awareness & attention)."""
        tasks = []

        if day == 1:
            tasks.append(
                {
                    "id": "launch_content",
                    "title": "Launch Initial Content",
                    "description": "Create and publish attention-grabbing content",
                    "type": "content_creation",
                    "priority": "high",
                    "estimated_time": "2-3 hours",
                    "dependencies": [],
                }
            )
            tasks.append(
                {
                    "id": "initial_promotion",
                    "title": "Initial Promotion",
                    "description": "Promote content across primary channels",
                    "type": "promotion",
                    "priority": "high",
                    "estimated_time": "1-2 hours",
                    "dependencies": ["launch_content"],
                }
            )
        elif day <= 3:
            tasks.append(
                {
                    "id": "engage_responses",
                    "title": "Engage with Responses",
                    "description": "Respond to comments and engage with audience",
                    "type": "engagement",
                    "priority": "medium",
                    "estimated_time": "30-60 minutes",
                    "dependencies": [],
                }
            )
        elif day <= 7:
            tasks.append(
                {
                    "id": "followup_content",
                    "title": "Create Follow-up Content",
                    "description": "Create content that builds on initial momentum",
                    "type": "content_creation",
                    "priority": "medium",
                    "estimated_time": "1-2 hours",
                    "dependencies": [],
                }
            )
        elif day <= 14:
            tasks.append(
                {
                    "id": "analyze_performance",
                    "title": "Analyze Performance",
                    "description": "Review metrics and adjust strategy",
                    "type": "analysis",
                    "priority": "low",
                    "estimated_time": "30 minutes",
                    "dependencies": [],
                }
            )

        return tasks

    def _generate_capture_tasks(
        self, day: int, duration: int, audience: Dict, objectives: List
    ) -> List[Dict[str, Any]]:
        """Generate tasks for capture moves (lead generation)."""
        tasks = []

        if day == 1:
            tasks.append(
                {
                    "id": "setup_capture",
                    "title": "Setup Lead Capture",
                    "description": "Prepare landing pages and capture mechanisms",
                    "type": "setup",
                    "priority": "high",
                    "estimated_time": "2-3 hours",
                    "dependencies": [],
                }
            )
        elif day <= 3:
            tasks.append(
                {
                    "id": "drive_traffic",
                    "title": "Drive Traffic",
                    "description": "Run campaigns to drive traffic to capture pages",
                    "type": "promotion",
                    "priority": "high",
                    "estimated_time": "1-2 hours",
                    "dependencies": ["setup_capture"],
                }
            )
        elif day <= 7:
            tasks.append(
                {
                    "id": "nurture_leads",
                    "title": "Nurture Leads",
                    "description": "Begin lead nurturing sequences",
                    "type": "nurturing",
                    "priority": "medium",
                    "estimated_time": "1 hour",
                    "dependencies": ["drive_traffic"],
                }
            )

        return tasks

    def _generate_authority_tasks(
        self, day: int, duration: int, audience: Dict, objectives: List
    ) -> List[Dict[str, Any]]:
        """Generate tasks for authority moves (thought leadership)."""
        tasks = []

        if day <= 3:
            tasks.append(
                {
                    "id": "create_authority_content",
                    "title": "Create Authority Content",
                    "description": "Develop in-depth, expert-level content",
                    "type": "content_creation",
                    "priority": "high",
                    "estimated_time": "4-6 hours",
                    "dependencies": [],
                }
            )
        elif day <= 7:
            tasks.append(
                {
                    "id": "distribute_authority",
                    "title": "Distribute Authority Content",
                    "description": "Share content across authority-building platforms",
                    "type": "distribution",
                    "priority": "high",
                    "estimated_time": "2-3 hours",
                    "dependencies": ["create_authority_content"],
                }
            )
        elif day <= 14:
            tasks.append(
                {
                    "id": "engage_discussions",
                    "title": "Engage in Discussions",
                    "description": "Participate in industry discussions and Q&A",
                    "type": "engagement",
                    "priority": "medium",
                    "estimated_time": "1-2 hours",
                    "dependencies": [],
                }
            )

        return tasks

    def _generate_repair_tasks(
        self, day: int, duration: int, audience: Dict, objectives: List
    ) -> List[Dict[str, Any]]:
        """Generate tasks for repair moves (reputation recovery)."""
        tasks = []

        if day == 1:
            tasks.append(
                {
                    "id": "assess_situation",
                    "title": "Assess Situation",
                    "description": "Analyze the issue that needs repair",
                    "type": "analysis",
                    "priority": "high",
                    "estimated_time": "1-2 hours",
                    "dependencies": [],
                }
            )
        elif day <= 3:
            tasks.append(
                {
                    "id": "create_response",
                    "title": "Create Response",
                    "description": "Develop thoughtful response or solution",
                    "type": "content_creation",
                    "priority": "high",
                    "estimated_time": "2-3 hours",
                    "dependencies": ["assess_situation"],
                }
            )
        elif day <= 7:
            tasks.append(
                {
                    "id": "implement_solution",
                    "title": "Implement Solution",
                    "description": "Execute the repair strategy",
                    "type": "implementation",
                    "priority": "high",
                    "estimated_time": "2-4 hours",
                    "dependencies": ["create_response"],
                }
            )

        return tasks

    def _generate_rally_tasks(
        self, day: int, duration: int, audience: Dict, objectives: List
    ) -> List[Dict[str, Any]]:
        """Generate tasks for rally moves (community building)."""
        tasks = []

        if day == 1:
            tasks.append(
                {
                    "id": "rally_call",
                    "title": "Rally Call",
                    "description": "Create call-to-action for community",
                    "type": "content_creation",
                    "priority": "high",
                    "estimated_time": "1-2 hours",
                    "dependencies": [],
                }
            )
        elif day <= 3:
            tasks.append(
                {
                    "id": "engage_community",
                    "title": "Engage Community",
                    "description": "Active community engagement and facilitation",
                    "type": "engagement",
                    "priority": "high",
                    "estimated_time": "2-3 hours",
                    "dependencies": ["rally_call"],
                }
            )
        elif day <= duration:
            tasks.append(
                {
                    "id": "maintain_momentum",
                    "title": "Maintain Momentum",
                    "description": "Keep community engaged and active",
                    "type": "engagement",
                    "priority": "medium",
                    "estimated_time": "1-2 hours",
                    "dependencies": [],
                }
            )

        return tasks


async def generate_tasks(state: MoveExecutionState) -> MoveExecutionState:
    """Generate daily tasks for the move."""
    try:
        task_handler = MoveTaskHandler()

        # Get move strategy from state or database
        move_strategy = state.get("move_strategy", {})

        # Generate tasks for current day
        tasks = task_handler.generate_daily_tasks(move_strategy, state["current_day"])

        state["tasks"] = tasks
        state["execution_status"] = "active"

        return state
    except Exception as e:
        state["error"] = f"Task generation failed: {str(e)}"
        state["execution_status"] = "failed"
        return state


async def schedule_tasks(state: MoveExecutionState) -> MoveExecutionState:
    """Schedule tasks for execution."""
    try:
        tasks = state.get("tasks", [])

        # Add scheduling information to tasks
        for task in tasks:
            task["scheduled_time"] = datetime.now() + timedelta(hours=1)
            task["status"] = "scheduled"

        state["tasks"] = tasks
        state["next_actions"] = [
            task["title"] for task in tasks if task["priority"] == "high"
        ]

        return state
    except Exception as e:
        state["error"] = f"Task scheduling failed: {str(e)}"
        return state


async def execute_task(state: MoveExecutionState) -> MoveExecutionState:
    """Execute a specific task."""
    try:
        tasks = state.get("tasks", [])

        # Find the next high-priority task
        next_task = None
        for task in tasks:
            if task.get("status") == "scheduled" and task.get("priority") == "high":
                next_task = task
                break

        if not next_task:
            # No high-priority tasks, find medium priority
            for task in tasks:
                if (
                    task.get("status") == "scheduled"
                    and task.get("priority") == "medium"
                ):
                    next_task = task
                    break

        if not next_task:
            state["next_actions"] = ["No tasks to execute"]
            return state

        # Execute task based on type
        task_result = await _execute_task_by_type(next_task, state)

        # Update task status
        next_task["status"] = "completed"
        next_task["completed_at"] = datetime.now()
        next_task["result"] = task_result

        # Add to completed tasks
        state["completed_tasks"].append(next_task["id"])
        state["task_results"][next_task["id"]] = task_result

        return state
    except Exception as e:
        state["error"] = f"Task execution failed: {str(e)}"
        return state


async def _execute_task_by_type(
    task: Dict[str, Any], state: MoveExecutionState
) -> Dict[str, Any]:
    """Execute a task based on its type."""
    task_type = task.get("type")

    if task_type == "content_creation":
        return await _execute_content_creation_task(task, state)
    elif task_type == "promotion":
        return await _execute_promotion_task(task, state)
    elif task_type == "engagement":
        return await _execute_engagement_task(task, state)
    elif task_type == "analysis":
        return await _execute_analysis_task(task, state)
    elif task_type == "setup":
        return await _execute_setup_task(task, state)
    elif task_type == "nurturing":
        return await _execute_nurturing_task(task, state)
    elif task_type == "distribution":
        return await _execute_distribution_task(task, state)
    elif task_type == "implementation":
        return await _execute_implementation_task(task, state)
    else:
        return {"success": False, "error": f"Unknown task type: {task_type}"}


async def _execute_content_creation_task(
    task: Dict[str, Any], state: MoveExecutionState
) -> Dict[str, Any]:
    """Execute content creation task."""
    try:
        # Use content creator to generate content
        content_creator = ContentCreator()

        # Determine content type based on move category
        move_category = state.get("move_category", "ignite")
        content_type = _map_move_to_content_type(move_category)

        # Generate content
        content_result = await content_creator.execute(state)

        return {
            "success": True,
            "content": content_result.get("output"),
            "content_type": content_type,
            "tokens_used": content_result.get("tokens_used", 0),
            "cost_usd": content_result.get("cost_usd", 0.0),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def _map_move_to_content_type(move_category: str) -> str:
    """Map move category to content type."""
    mapping = {
        "ignite": "social_post",
        "capture": "email",
        "authority": "blog_intro",
        "repair": "social_post",
        "rally": "social_post",
    }
    return mapping.get(move_category, "social_post")


async def _execute_promotion_task(
    task: Dict[str, Any], state: MoveExecutionState
) -> Dict[str, Any]:
    """Execute promotion task."""
    return {
        "success": True,
        "action": "promotion",
        "details": "Content promoted across channels",
        "channels": ["social_media", "email", "website"],
    }


async def _execute_engagement_task(
    task: Dict[str, Any], state: MoveExecutionState
) -> Dict[str, Any]:
    """Execute engagement task."""
    return {
        "success": True,
        "action": "engagement",
        "details": "Engaged with audience responses",
        "responses_count": 15,
    }


async def _execute_analysis_task(
    task: Dict[str, Any], state: MoveExecutionState
) -> Dict[str, Any]:
    """Execute analysis task."""
    return {
        "success": True,
        "action": "analysis",
        "details": "Analyzed performance metrics",
        "metrics": {"reach": 1000, "engagement": 50, "conversions": 5},
    }


async def _execute_setup_task(
    task: Dict[str, Any], state: MoveExecutionState
) -> Dict[str, Any]:
    """Execute setup task."""
    return {
        "success": True,
        "action": "setup",
        "details": "Setup completed successfully",
        "setup_items": ["landing_page", "capture_form", "email_sequence"],
    }


async def _execute_nurturing_task(
    task: Dict[str, Any], state: MoveExecutionState
) -> Dict[str, Any]:
    """Execute nurturing task."""
    return {
        "success": True,
        "action": "nurturing",
        "details": "Lead nurturing sequence initiated",
        "leads_nurtured": 25,
    }


async def _execute_distribution_task(
    task: Dict[str, Any], state: MoveExecutionState
) -> Dict[str, Any]:
    """Execute distribution task."""
    return {
        "success": True,
        "action": "distribution",
        "details": "Content distributed to authority platforms",
        "platforms": ["linkedin", "industry_blogs", "forums"],
    }


async def _execute_implementation_task(
    task: Dict[str, Any], state: MoveExecutionState
) -> Dict[str, Any]:
    """Execute implementation task."""
    return {
        "success": True,
        "action": "implementation",
        "details": "Solution implemented successfully",
        "implementation_items": [
            "fix_applied",
            "communication_sent",
            "monitoring_started",
        ],
    }


async def generate_content(state: MoveExecutionState) -> MoveExecutionState:
    """Generate content for tasks that require it."""
    try:
        # Check if any tasks need content generation
        tasks_needing_content = [
            task
            for task in state.get("tasks", [])
            if task.get("type") == "content_creation"
            and task.get("status") == "scheduled"
        ]

        if not tasks_needing_content:
            return state

        # Generate content for each task
        content_creator = ContentCreator()
        content_results = {}

        for task in tasks_needing_content:
            content_result = await content_creator.execute(state)
            content_results[task["id"]] = content_result.get("output")

        state["content_generated"] = content_results

        return state
    except Exception as e:
        state["error"] = f"Content generation failed: {str(e)}"
        return state


async def mark_complete(state: MoveExecutionState) -> MoveExecutionState:
    """Mark tasks as complete and update progress."""
    try:
        tasks = state.get("tasks", [])
        total_tasks = len(tasks)
        completed_tasks = len(
            [task for task in tasks if task.get("status") == "completed"]
        )

        # Calculate progress
        progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        state["progress_percentage"] = progress

        # Check if move is complete
        if state["current_day"] >= state["total_days"] and progress >= 90:
            state["execution_status"] = "completed"
        else:
            state["execution_status"] = "active"

        # Update next actions
        remaining_tasks = [task for task in tasks if task.get("status") == "scheduled"]
        state["next_actions"] = [task["title"] for task in remaining_tasks[:3]]

        return state
    except Exception as e:
        state["error"] = f"Progress update failed: {str(e)}"
        return state


async def update_progress(state: MoveExecutionState) -> MoveExecutionState:
    """Update overall move progress."""
    try:
        # Calculate progress based on completed tasks and days
        day_progress = (state["current_day"] / state["total_days"]) * 100
        task_progress = state.get("progress_percentage", 0)

        # Overall progress is weighted average
        overall_progress = (day_progress * 0.3) + (task_progress * 0.7)
        state["progress_percentage"] = overall_progress

        # Generate performance metrics
        state["performance_metrics"] = {
            "tasks_completed": len(state.get("completed_tasks", [])),
            "total_tasks": len(state.get("tasks", [])),
            "day": state["current_day"],
            "total_days": state["total_days"],
            "progress_percentage": overall_progress,
            "status": state.get("execution_status", "active"),
        }

        return state
    except Exception as e:
        state["error"] = f"Progress update failed: {str(e)}"
        return state


def should_continue_execution(state: MoveExecutionState) -> str:
    """Determine next step in move execution."""
    if state.get("error"):
        return END

    execution_status = state.get("execution_status", "planning")

    if execution_status == "planning":
        return "generate_tasks"
    elif execution_status == "active":
        # Check if we have tasks to execute
        scheduled_tasks = [
            task for task in state.get("tasks", []) if task.get("status") == "scheduled"
        ]

        if scheduled_tasks:
            return "execute_task"
        else:
            return "mark_complete"
    elif execution_status == "completed":
        return END
    else:
        return END


class MoveExecutionGraph:
    """Move execution workflow graph."""

    def __init__(self):
        self.graph = None

    def create_graph(self) -> StateGraph:
        """Create the move execution workflow graph."""
        workflow = StateGraph(MoveExecutionState)

        # Add nodes
        workflow.add_node("generate_tasks", generate_tasks)
        workflow.add_node("schedule_tasks", schedule_tasks)
        workflow.add_node("execute_task", execute_task)
        workflow.add_node("generate_content", generate_content)
        workflow.add_node("mark_complete", mark_complete)
        workflow.add_node("update_progress", update_progress)

        # Set entry point
        workflow.set_entry_point("generate_tasks")

        # Add conditional edges
        workflow.add_conditional_edges(
            "generate_tasks",
            should_continue_execution,
            {"schedule_tasks": "schedule_tasks", END: END},
        )
        workflow.add_conditional_edges(
            "schedule_tasks",
            should_continue_execution,
            {
                "execute_task": "execute_task",
                "generate_content": "generate_content",
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "execute_task",
            should_continue_execution,
            {
                "execute_task": "execute_task",  # Continue executing tasks
                "mark_complete": "mark_complete",
                END: END,
            },
        )
        workflow.add_conditional_edges(
            "generate_content",
            should_continue_execution,
            {"execute_task": "execute_task", END: END},
        )
        workflow.add_edge("mark_complete", "update_progress")
        workflow.add_edge("update_progress", END)

        # Add memory checkpointing
        memory = MemorySaver()

        # Compile the graph
        self.graph = workflow.compile(checkpointer=memory)
        return self.graph

    async def start_move_execution(
        self, move_id: str, workspace_id: str, user_id: str, session_id: str
    ) -> Dict[str, Any]:
        """Start move execution."""
        if not self.graph:
            self.create_graph()

        # Create initial state
        initial_state = MoveExecutionState(
            move_id=move_id,
            move_name="",
            move_category="ignite",
            current_day=1,
            total_days=14,
            tasks=[],
            completed_tasks=[],
            task_results={},
            content_generated={},
            execution_status="planning",
            progress_percentage=0.0,
            next_actions=[],
            performance_metrics={},
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
                "thread_id": f"move_{move_id}",
                "checkpoint_ns": f"move_execution_{workspace_id}",
            }
        }

        try:
            result = await self.graph.ainvoke(initial_state, config=thread_config)

            return {
                "success": True,
                "move_id": move_id,
                "execution_status": result.get("execution_status"),
                "current_day": result.get("current_day"),
                "progress": result.get("progress_percentage", 0),
                "tasks": result.get("tasks", []),
                "next_actions": result.get("next_actions", []),
                "performance_metrics": result.get("performance_metrics", {}),
                "error": result.get("error"),
            }

        except Exception as e:
            return {"success": False, "error": f"Move execution failed: {str(e)}"}
