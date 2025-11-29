# backend/agents/council_of_lords/eris.py
# RaptorFlow Codex - Eris Lord Agent (Project Chaos)
# "Order is easy. Chaos is the true test."

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import uuid
import json
from enum import Enum

from agents.base_agent import BaseAgent, AgentType, AgentStatus, Capability
from backend.models.chaos import ChaosEvent, ChaosType, ChaosSeverity, StrategyResilienceScore, WargameScenario
from backend.services.vertex_ai_client import vertex_ai_client
from backend.bus.raptor_bus import get_bus

logger = logging.getLogger(__name__)

class ErisLord(BaseAgent):
    """
    Eris Lord - The Agent of Chaos & Resilience.
    
    Role: Adversary / Red Teamer
    Responsibility: Stress-test strategies by injecting controlled entropy and simulating 
    Black Swan events. Ensures the organization is antifragile.
    """

    def __init__(self):
        super().__init__(
            name="Eris",
            # agent_type=AgentType.LORD, # Assuming AgentType.LORD exists, otherwise fallback
        )
        # Manually setting attributes if AgentType.LORD is not available in BaseAgent init
        self.role = "eris" 
        self.council_position = 8 # The 8th Lord (Unofficial)
        
        self.active_scenarios: Dict[str, WargameScenario] = {}
        self.chaos_history: List[ChaosEvent] = []

        # Register Capabilities
        self.capabilities = [
            Capability(
                name="generate_chaos_event",
                handler=self._generate_chaos_event,
                description="Generate a random or targeted chaos event"
            ),
            Capability(
                name="run_wargame_simulation",
                handler=self._run_wargame_simulation,
                description="Simulate a full wargame against a strategy"
            ),
            Capability(
                name="inject_entropy",
                handler=self._inject_entropy,
                description="Inject noise into a specific context or metric"
            )
        ]

    async def initialize(self) -> None:
        """Initialize Eris Lord"""
        logger.info("🍎 Initializing Eris Lord (Chaos Engine)...")
        # Any specific initialization logic here
        logger.info(f"✅ Eris Lord initialized with {len(self.capabilities)} capabilities")

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute capability"""
        capability_name = payload.get("capability")
        if not capability_name:
            # Default behavior if no capability specified?
            # Maybe just generate a random event
            return await self._generate_chaos_event(**payload)
            
        for cap in self.capabilities:
            if cap.name == capability_name:
                kwargs = payload.copy()
                if "capability" in kwargs:
                    del kwargs["capability"]
                return await cap.handler(**kwargs)
        
        raise ValueError(f"Unknown capability: {capability_name}")

    # ========================================================================
    # CHAOS GENERATION
    # ========================================================================

    async def _generate_chaos_event(self, **kwargs) -> Dict[str, Any]:
        """
        Generate a Chaos Event using Vertex AI.
        
        Args:
            target_domain: The domain to disrupt (e.g., "pricing", "pr", "tech").
            severity: Desired severity (low, medium, high, critical).
            context: Current strategy context to tailor the disruption.
        """
        target_domain = kwargs.get("target_domain", "market")
        severity = kwargs.get("severity", "medium")
        context = kwargs.get("context", {})
        
        logger.info(f"🎲 Eris generating chaos event for {target_domain} ({severity})")

        prompt = f"""
        You are Eris, the Agent of Chaos and Resilience. Your job is to generate a realistic but disruptive "Chaos Event" to stress-test a marketing strategy.
        
        Target Domain: {target_domain}
        Severity: {severity}
        Current Context: {json.dumps(context)}
        
        Generate a JSON response with the following structure:
        {{
            "type": "market_crash" | "reputation_scandal" | "competitor_move" | "regulatory_change" | "technical_failure" | "black_swan",
            "name": "Headline of the event",
            "description": "Detailed scenario description",
            "parameters": {{ "key": "value" }},
            "expected_impact": {{ "metric_name": impact_float_0_to_1 }}
        }}
        
        Make it creative, plausible, and difficult to solve.
        """

        try:
            response = await vertex_ai_client.generate_json(
                prompt=prompt,
                system_prompt="You are Eris, a creative adversarial agent.",
                model_type="creative" # Using creative model for better scenarios
            )
            
            event = ChaosEvent(
                type=response.get("type", ChaosType.BLACK_SWAN),
                name=response.get("name", "Unknown Event"),
                description=response.get("description", "No description"),
                severity=ChaosSeverity(severity),
                parameters=response.get("parameters", {}),
                expected_impact=response.get("expected_impact", {})
            )
            
            self.chaos_history.append(event)
            
            # Publish to bus so other agents (Seer/Strategos) can react
            bus = await get_bus()
            await bus.publish("chaos_event_generated", event.dict())

            return event.dict()

        except Exception as e:
            logger.error(f"Failed to generate chaos event: {e}")
            # Fallback
            return ChaosEvent(
                type=ChaosType.TECHNICAL_FAILURE,
                name="Vertex AI Outage",
                description="The AI generation service failed, simulating a technical outage.",
                severity=ChaosSeverity.LOW
            ).dict()

    # ========================================================================
    # WARGAME SIMULATION
    # ========================================================================

    async def _run_wargame_simulation(self, **kwargs) -> Dict[str, Any]:
        """
        Run a full wargame simulation against a strategy.
        """
        strategy_id = kwargs.get("strategy_id")
        strategy_details = kwargs.get("strategy_details", {})
        num_events = kwargs.get("num_events", 3)
        
        logger.info(f"⚔️ Running Wargame for Strategy: {strategy_id}")
        
        # 1. Generate Sequence of Events
        events = []
        for i in range(num_events):
            # Escalate severity over time
            severity = "low" if i == 0 else ("medium" if i < num_events - 1 else "high")
            event_dict = await self._generate_chaos_event(
                target_domain="random", 
                severity=severity,
                context=strategy_details
            )
            events.append(ChaosEvent(**event_dict))
            
        scenario = WargameScenario(
            name=f"Wargame {datetime.utcnow().strftime('%Y-%m-%d')}",
            description="Automated stress test",
            events=events
        )
        
        self.active_scenarios[scenario.id] = scenario
        
        # 2. Assess Resilience (Simulated for now, could ask Strategos to react)
        # We assume the strategy has a 'robustness' score or we calculate it
        
        # Simple heuristic resilience calculation based on event severity vs strategy keywords
        survival_prob = 1.0
        weaknesses = []
        
        for event in events:
            impact = 0.1 # Base impact
            if event.severity == ChaosSeverity.HIGH:
                impact = 0.3
            elif event.severity == ChaosSeverity.CRITICAL:
                impact = 0.5
            
            # If strategy mentions the domain, reduce impact (preparedness)
            if any(word in strategy_details.get("description", "").lower() for word in event.type.split("_")):
                impact *= 0.5 # Mitigated
            else:
                weaknesses.append(f"Unprepared for {event.type}")
                
            survival_prob *= (1.0 - impact)
            
        score = StrategyResilienceScore(
            strategy_id=strategy_id or "unknown",
            scenario_id=scenario.id,
            overall_score=survival_prob * 100,
            survival_probability=survival_prob,
            weaknesses_exposed=weaknesses,
            recommendations=["Add contingency plans for " + w for w in weaknesses]
        )

        return {
            "scenario": scenario.dict(),
            "resilience_score": score.dict()
        }

    # ========================================================================
    # ENTROPY INJECTION
    # ========================================================================

    async def _inject_entropy(self, **kwargs) -> Dict[str, Any]:
        """
        Slightly modify a value or context to simulate noise/uncertainty.
        """
        data = kwargs.get("data", {})
        noise_level = kwargs.get("noise_level", 0.1)
        
        logger.info("Injecting entropy...")
        
        # This is a simple fuzzing logic
        fuzzed_data = data.copy()
        for key, value in fuzzed_data.items():
            if isinstance(value, (int, float)):
                import random
                variance = value * noise_level
                fuzzed_data[key] = value + random.uniform(-variance, variance)
        
        return {"original": data, "fuzzed": fuzzed_data}
