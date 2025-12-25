import inspect
import logging
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field

from backend.inference import InferenceProvider

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


class SwarmController:
    """Unified controller for intent routing and multi-agent supervision."""

    def __init__(
        self,
        supervisor_llm: Optional[Any] = None,
        team_members: Optional[List[str]] = None,
        system_prompt: Optional[str] = None,
        intent_llm: Optional[Any] = None,
    ) -> None:
        self.supervisor_llm = supervisor_llm
        self.team_members = team_members or []
        self.system_prompt = system_prompt
        self.intent_chain = (
            intent_llm
            or InferenceProvider.get_model(model_tier="fast", temperature=0.0)
        ).with_structured_output(SwarmIntent)
        self._supervisor_chain = None

    @property
    def supervisor_chain(self):
        if self._supervisor_chain is None:
            if not self.supervisor_llm or not self.system_prompt:
                raise ValueError("Supervisor LLM and system prompt must be provided.")

            options = self.team_members + ["FINISH"]
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", self.system_prompt),
                    MessagesPlaceholder(variable_name="messages"),
                    (
                        "system",
                        "Given the conversation above, who should act next?"
                        " Or should we FINISH? Select one of: {options}",
                    ),
                ]
            ).partial(options=str(options))

            self._supervisor_chain = (
                prompt | self.supervisor_llm.with_structured_output(SwarmRouteDecision)
            )
        return self._supervisor_chain

    async def __call__(self, state: Dict[str, Any]) -> Dict[str, str]:
        return await self.decide_next(state)

    async def route_intent(self, prompt: str) -> SwarmIntent:
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
            [system_msg, HumanMessage(content=prompt)]
        )

    async def decide_next(
        self,
        state: Dict[str, Any],
        *,
        chain: Optional[Any] = None,
    ) -> Dict[str, str]:
        logger.info("Swarm controller evaluating state...")
        router = chain or self.supervisor_chain
        response = await router.ainvoke(state)

        if hasattr(response, "next_node"):
            next_node = response.next_node
            instructions = response.instructions
        else:
            next_node = response.get("next_node")
            instructions = response.get("instructions")

        logger.info("Swarm controller delegated to: %s", next_node)
        return {"next": str(next_node), "instructions": str(instructions)}

    async def delegate_to_specialist(
        self,
        specialist_name: str,
        state: Dict[str, Any],
        specialist_node: Any,
    ) -> Dict[str, Any]:
        logger.info("Delegating task to specialist: %s", specialist_name)

        adapter = (
            specialist_node
            if isinstance(specialist_node, SwarmAgentAdapter)
            else SwarmAgentAdapter.from_callable(specialist_name, specialist_node)
        )
        return await adapter(state)

    async def execute_loop(
        self,
        initial_state: Dict[str, Any],
        nodes: Dict[str, Any],
        *,
        max_loops: int = 10,
        chain: Optional[Any] = None,
    ) -> Dict[str, Any]:
        current_state = initial_state.copy()
        if "messages" not in current_state:
            current_state["messages"] = []

        loop_count = 0

        while loop_count < max_loops:
            decision = await self.decide_next(current_state, chain=chain)
            next_node = decision["next"]
            instructions = decision["instructions"]

            if next_node == "FINISH":
                break

            if next_node in nodes:
                specialist_node = nodes[next_node]
                current_state["instructions"] = instructions
                result = await self.delegate_to_specialist(
                    next_node, current_state, specialist_node
                )

                summary = result.get("analysis_summary", "Task completed.")
                current_state["messages"].append(
                    AIMessage(content=f"[{next_node}]: {summary}")
                )
            else:
                logger.error("Specialist %s not found in nodes.", next_node)
                break

            loop_count += 1

        current_state["next"] = "FINISH"
        return current_state

    def aggregate_findings(self, findings: List[Dict[str, Any]]) -> str:
        logger.info("Aggregating %s specialist findings...", len(findings))

        summary_parts = ["### MATRIX BOARDROOM SUMMARY ###"]
        for i, finding in enumerate(findings):
            source = finding.get("source", f"Specialist {i+1}")
            text = finding.get("analysis_summary", "No summary provided.")
            summary_parts.append(f"- [{source}]: {text}")

        return "\n".join(summary_parts)
