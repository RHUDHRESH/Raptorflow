import inspect
import logging
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field

from backend.agents.router import IntentRouterAgent
from backend.inference import InferenceProvider
from backend.models.cognitive import (
    AgentMessage,
    ResourceBudget,
    RoutingMetadata,
    SharedMemoryHandles,
)

logger = logging.getLogger("raptorflow.swarm.orchestrator")


class SwarmIntent(BaseModel):
    asset_type: str = Field(
        description="The family of asset (email, social, meme, strategy)"
    )
    confidence: float = Field(description="Confidence score 0.0 - 1.0")
    extracted_goal: str = Field(description="What the user wants to achieve")
    entities: List[str] = Field(
        description="Extracted @mentions like cohorts or campaigns"
    )
    ambiguity_reasons: Optional[List[str]] = Field(
        description="Reasons for low confidence",
        default=None,
    )

    @property
    def asset_family(self) -> str:
        return self.asset_type

    @property
    def goal(self) -> str:
        return self.extracted_goal

    def to_intent_payload(self) -> Dict[str, Any]:
        return {
            "asset_family": self.asset_type,
            "goal": self.extracted_goal,
            "entities": self.entities,
            "confidence": self.confidence,
            "ambiguity_reasons": self.ambiguity_reasons,
        }


class SwarmRoutingDecision(BaseModel):
    """Structured output for the Swarm Controller router."""

    next_node: str = Field(
        description="The next swarm to call, or 'FINISH' to terminate."
    )
    instructions: str = Field(description="Instructions for the delegated swarm.")
    rationale: Optional[str] = Field(default=None, description="Routing rationale.")


class SwarmRouteDecision(BaseModel):
    """Structured output for the Swarm controller router."""

    next_node: str = Field(
        description="The next specialist crew to call, or 'FINISH' to deliver to user."
    )
    instructions: str = Field(
        description="Specific sub-task instructions for the specialist."
    )


class SwarmAgentAdapter:
    """Adapter to normalize different agent call signatures."""

    def __init__(
        self,
        name: str,
        handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]],
    ) -> None:
        self.name = name
        self._handler = handler

    async def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        result = self._handler(state)
        if inspect.isawaitable(result):
            return await result
        return result

    @staticmethod
    def _wrap_result(result: Any) -> Awaitable[Dict[str, Any]]:
        async def _wrapper() -> Dict[str, Any]:
            if inspect.isawaitable(result):
                return await result
            return result

        return _wrapper()

    @classmethod
    def from_callable(cls, name: str, agent: Callable[[Dict[str, Any]], Any]):
        async def handler(state: Dict[str, Any]) -> Dict[str, Any]:
            return await cls._wrap_result(agent(state))

        return cls(name, handler)

    @classmethod
    def from_run_method(
        cls,
        name: str,
        agent: Any,
        *,
        identifier_key: str = "move_id",
        payload_builder: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        def build_payload(state: Dict[str, Any]) -> Dict[str, Any]:
            return payload_builder(state) if payload_builder else state

        async def handler(state: Dict[str, Any]) -> Dict[str, Any]:
            identifier = state.get(identifier_key)
            return await cls._wrap_result(agent.run(identifier, build_payload(state)))

        return cls(name, handler)

    @classmethod
    def from_execute_method(
        cls,
        name: str,
        agent: Any,
        *,
        prompt_key: str = "prompt",
    ):
        async def handler(state: Dict[str, Any]) -> Dict[str, Any]:
            return await cls._wrap_result(agent.execute(state[prompt_key]))

        return cls(name, handler)


class SwarmOrchestrator:
    """
    Unified Swarm Controller coordinating specialized sub-swarms.
    Combines intent routing, multi-agent supervision, and delegation logic.
    """

    def __init__(
        self,
        llm: Any = None,
        team_members: Optional[List[str]] = None,
        system_prompt: str = "",
        sub_swarms: Optional[Dict[str, Any]] = None,
        router_agent: Optional[IntentRouterAgent] = None,
        output_model: type[BaseModel] = SwarmRoutingDecision,
    ):
        self.llm = llm or InferenceProvider.get_model(
            model_tier="fast", temperature=0.0
        )
        self.team_members = team_members or [
            "strategists",
            "researchers",
            "creatives",
            "quality",
        ]
        options = self.team_members + ["FINISH"]

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt or "You are the Swarm Controller."),
                MessagesPlaceholder(variable_name="messages"),
                (
                    "system",
                    "Given the conversation above, who should act next?"
                    " Or should we FINISH? Select one of: {options}",
                ),
            ]
        ).partial(options=str(options))

        self.output_model = output_model
        self._chain = None
        self.router_agent = router_agent or IntentRouterAgent()
        self.sub_swarms = sub_swarms or {}
        self.swarm_tree = self._build_swarm_tree()

        # Intent routing chain
        self.intent_chain = self.llm.with_structured_output(SwarmIntent)

    @property
    def chain(self):
        if self._chain is None:
            self._chain = self.prompt | self.llm.with_structured_output(
                self.output_model
            )
        return self._chain

    def _build_swarm_tree(self) -> Dict[str, Tuple[str, ...]]:
        return {
            "controller": tuple(self.team_members),
            "strategists": ("researchers", "creatives", "quality"),
            "researchers": ("strategists", "quality"),
            "creatives": ("quality",),
            "quality": ("strategists", "creatives"),
        }

    def _ensure_metadata(self, state: Dict[str, Any]) -> Dict[str, Any]:
        state = state.copy()
        state.setdefault("routing_metadata", RoutingMetadata())
        state.setdefault("shared_memory_handles", SharedMemoryHandles())
        state.setdefault("resource_budget", ResourceBudget())
        state.setdefault("delegation_history", [])
        state.setdefault("shared_knowledge", {})
        state.setdefault("swarm_tasks", [])
        return state

    async def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Swarm Controller evaluating state...")
        state = self._ensure_metadata(state)

        state_for_chain = state.copy()
        state_for_chain["messages"] = self._format_messages(
            state_for_chain.get("messages", [])
        )
        response = await self.chain.ainvoke(state_for_chain)
        next_node = getattr(response, "next_node", None) or response.get("next_node")
        instructions = getattr(response, "instructions", None) or response.get(
            "instructions"
        )
        rationale = getattr(response, "rationale", None) or response.get("rationale")

        routing_metadata = state["routing_metadata"]
        routing_metadata.update(
            {
                "current_node": "controller",
                "next_node": str(next_node),
                "instructions": str(instructions),
                "rationale": rationale,
            }
        )
        routing_metadata.setdefault("route_history", []).append(
            {"from": "controller", "to": str(next_node), "reason": rationale}
        )

        logger.info("Swarm Controller delegated to: %s", next_node)
        return {
            "next": str(next_node),
            "instructions": str(instructions),
            "routing_metadata": routing_metadata,
        }

    async def route_intent(self, query: str) -> SwarmIntent:
        """Route user intent using structured output."""
        system_msg = SystemMessage(
            content=(
                "You are the Intent Router for RaptorFlow.\n"
                "Classify user prompts into asset families: email, social, meme, or strategy.\n"
                "Extract @mentions which represent campaigns, cohorts, or competitors.\n"
                "Assign confidence based on how much detail is provided.\n"
                "If the prompt is vague (e.g. 'write an email'), confidence must be < 0.7."
            )
        )

        return await self.intent_chain.ainvoke(
            [system_msg, HumanMessage(content=query)]
        )

    async def execute_loop(
        self, initial_state: Dict[str, Any], nodes: Dict[str, Any]
    ) -> Dict[str, Any]:
        current_state = self._ensure_metadata(initial_state)
        current_state.setdefault("messages", [])

        await self._maybe_capture_intent(current_state)

        max_loops = self._resolve_budget(current_state).get("max_rounds", 10)
        loop_count = 0

        while loop_count < max_loops:
            decision = await self.__call__(current_state)
            next_node = decision["next"]
            instructions = decision["instructions"]

            if next_node == "FINISH":
                break

            if next_node in nodes:
                current_state["instructions"] = instructions
                specialist_node = nodes[next_node]
                result = await self.delegate_to_specialist(
                    next_node, current_state, specialist_node
                )

                summary = result.get("analysis_summary", "Task completed.")
                current_state["messages"].append(
                    AgentMessage(
                        role=next_node,
                        content=f"[{next_node}]: {summary}",
                        metadata={
                            "source": next_node,
                            "instructions": instructions,
                        },
                    )
                )
                current_state["delegation_history"].append(
                    {
                        "node": next_node,
                        "summary": summary,
                        "instructions": instructions,
                    }
                )
            else:
                logger.error("Specialist %s not found in nodes.", next_node)
                break

            loop_count += 1

        current_state["next"] = "FINISH"
        return current_state

    def _format_messages(self, state_messages: List[Any]) -> List[BaseMessage]:
        lc_messages: List[BaseMessage] = []
        for message in state_messages:
            if isinstance(message, BaseMessage):
                lc_messages.append(message)
                continue

            if isinstance(message, AgentMessage):
                role = message.role
                content = message.content
            elif isinstance(message, dict):
                role = message.get("role", "human")
                content = message.get("content", "")
            else:
                role = "human"
                content = str(message)

            if role in {"human", "user"}:
                lc_messages.append(HumanMessage(content=content))
            elif role == "system":
                lc_messages.append(SystemMessage(content=content))
            else:
                prefix = f"[{role}]: "
                formatted = (
                    content if content.startswith(prefix) else f"{prefix}{content}"
                )
                lc_messages.append(AIMessage(content=formatted))

        return lc_messages

    async def delegate_to_specialist(
        self, specialist_name: str, state: Dict[str, Any], specialist_node: Any
    ) -> Dict[str, Any]:
        logger.info("Delegating task to specialist: %s", specialist_name)
        adapter = self._adapt_node(specialist_node)
        result = await adapter(state)
        if isinstance(result, dict):
            return result
        return {"analysis_summary": str(result)}

    async def _maybe_capture_intent(self, state: Dict[str, Any]) -> None:
        if not self.router_agent:
            return
        routing_metadata = state.get("routing_metadata", {})
        if routing_metadata.get("intent"):
            return
        prompt = state.get("raw_prompt") or state.get("prompt")
        if not prompt:
            return
        try:
            intent = await self.router_agent.route(prompt)
        except Exception as exc:
            logger.warning("Intent routing failed: %s", exc)
            return
        routing_metadata["intent"] = intent.model_dump()

    def _resolve_budget(self, state: Dict[str, Any]) -> Dict[str, Any]:
        budget = state.get("resource_budget") or {}
        return {
            "max_rounds": budget.get("max_rounds", 10),
            "max_tokens": budget.get("max_tokens"),
            "max_cost": budget.get("max_cost"),
        }

    def _adapt_node(self, node: Any) -> Callable[[Dict[str, Any]], Any]:
        async def _invoke(state: Dict[str, Any]) -> Any:
            callable_target = node
            if hasattr(node, "__call__"):
                callable_target = node

            try:
                signature = inspect.signature(callable_target)
            except (TypeError, ValueError):
                signature = None

            if signature is None:
                result = callable_target()
                return await result if inspect.isawaitable(result) else result

            params = list(signature.parameters.values())
            if not params:
                result = callable_target()
                return await result if inspect.isawaitable(result) else result

            param_names = {param.name for param in params}
            if any(param.kind == param.VAR_KEYWORD for param in params):
                result = callable_target(**state)
                return await result if inspect.isawaitable(result) else result

            if "state" in param_names:
                arg = state
            elif "prompt" in param_names:
                arg = state.get("raw_prompt") or state.get("prompt")
            elif "query" in param_names:
                arg = state.get("raw_prompt") or state.get("prompt")
            elif "brief" in param_names:
                arg = state.get("brief")
            else:
                arg = state

            result = callable_target(arg)
            return await result if inspect.isawaitable(result) else result

        return _invoke

    def aggregate_findings(self, findings: List[Dict[str, Any]]) -> str:
        logger.info("Aggregating %s specialist findings...", len(findings))

        summary_parts = ["### MATRIX BOARDROOM SUMMARY ###"]
        for i, finding in enumerate(findings):
            source = finding.get("source", f"Specialist {i+1}")
            text = finding.get("analysis_summary", "No summary provided.")
            summary_parts.append(f"- [{source}]: {text}")

        return "\n".join(summary_parts)
