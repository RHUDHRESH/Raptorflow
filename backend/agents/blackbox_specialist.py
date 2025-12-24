import inspect
from abc import ABC, abstractmethod
from typing import Any, Dict

from backend.inference import InferenceProvider


class BlackboxSpecialist(ABC):
    """
    Base class for all Blackbox specialist agents.
    Provides shared access to inference and common utilities.
    """

    def __init__(self, agent_id: str, model_tier: str = "driver"):
        self.agent_id = agent_id
        self.llm = InferenceProvider.get_model(model_tier=model_tier)
        # Legacy alias for sync agents/tests that still reference .model
        self.model = self.llm

    @abstractmethod
    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the specialist's core logic.
        """
        pass

    async def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Allows the specialist to be used as a LangGraph node.
        """
        result = self.run(state)
        if inspect.isawaitable(result):
            return await result
        return result


class ROIAnalystAgent(BlackboxSpecialist):
    """
    Specialist focused on business outcome attribution and ROI calculation.
    """

    def __init__(self, model_tier: str = "reasoning"):
        super().__init__(agent_id="roi_analyst", model_tier=model_tier)

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        outcomes = state.get("outcomes", [])
        move_id = state.get("move_id", "unknown")

        prompt = (
            "You are the RaptorFlow ROI Analyst. Analyze these outcomes for move {move_id}:\n"
            "{outcomes}\n\n"
            "Provide a concise attribution report including ROI estimate."
        ).format(move_id=move_id, outcomes=outcomes)

        response = await self.llm.ainvoke(prompt)
        return {
            "attribution_report": response.content,
            "status": ["attributed"],
        }


class StrategicDriftAgent(BlackboxSpecialist):
    """
    Specialist focused on detecting deviation from brand foundation and strategy.
    """

    def __init__(self, model_tier: str = "reasoning"):
        super().__init__(agent_id="strategic_drift", model_tier=model_tier)

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        findings = state.get("findings", [])
        move_id = state.get("move_id", "unknown")

        prompt = (
            "You are the RaptorFlow Strategic Drift Agent. Analyze these findings for move {move_id}:\n"
            "{findings}\n\n"
            "Compare them against typical 'Brand Foundation' constraints. "
            "Identify any 'Strategic Drift' or misalignment."
        ).format(move_id=move_id, findings=findings)

        response = await self.llm.ainvoke(prompt)
        return {
            "drift_analysis": response.content,
            "status": ["analyzed"],
        }


class CompetitorIntelligenceAgent(BlackboxSpecialist):
    """
    Specialist focused on extracting insights from competitor scrape telemetry.
    """

    def __init__(self, model_tier: str = "reasoning"):
        super().__init__(agent_id="competitor_intelligence", model_tier=model_tier)

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        telemetry = state.get("telemetry_data", [])
        move_id = state.get("move_id", "unknown")

        # Filter for scrape actions
        scrapes = [t for t in telemetry if "scrape" in str(t).lower()]

        prompt = (
            "You are the RaptorFlow Competitor Intelligence Agent. Analyze these scrapes for move {move_id}:\n"
            "{scrapes}\n\n"
            "Identify key competitor moves, price changes, or creative hooks discovered."
        ).format(move_id=move_id, scrapes=scrapes)

        response = await self.llm.ainvoke(prompt)
        return {
            "competitor_insights": response.content,
            "status": ["analyzed"],
        }


class BlackboxCritiqueAgent(BlackboxSpecialist):
    """
    Quality Gate specialist that critiques analysis results and findings.
    """

    def __init__(self, model_tier: str = "ultra"):
        super().__init__(agent_id="blackbox_critique", model_tier=model_tier)

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        findings = state.get("findings", [])
        attribution = state.get("attribution_report", "No attribution yet.")
        drift = state.get("drift_analysis", "No drift analysis yet.")

        prompt = (
            "You are the RaptorFlow Quality Gate. Critique the following Blackbox Analysis:\n\n"
            "FINDINGS: {findings}\n"
            "ATTRIBUTION: {attribution}\n"
            "DRIFT: {drift}\n\n"
            "Identify logic gaps, unsupported claims, or missing context. "
            "Return a score (0.0 - 1.0) and a list of specific improvements needed."
        ).format(findings=findings, attribution=attribution, drift=drift)

        response = await self.llm.ainvoke(prompt)
        # Robust score extraction using regex
        import re

        score = 0.8
        match = re.search(r"score[:\s]*(\d+\.?\d*)", response.content.lower())
        if match:
            try:
                score = float(match.group(1))
            except (ValueError, IndexError):
                pass

        return {
            "critique": response.content,
            "confidence_score": score,
            "status": ["critiqued"],
        }


class LearningAgent(BlackboxSpecialist):
    """
    Specialist that aggregates multiple findings into strategic pivots and learnings.
    """

    def __init__(self, model_tier: str = "ultra"):
        super().__init__(agent_id="learning_agent", model_tier=model_tier)

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        findings = state.get("findings", [])
        reflection = state.get("reflection", "")

        prompt = (
            "You are the RaptorFlow Chief Learning Officer. Synthesize these findings and "
            "reflections into a set of 'Strategic Pivots' or 'Confirmed Constraints'.\n\n"
            "FINDINGS:\n{findings}\n\n"
            "REFLECTION:\n{reflection}\n\n"
            "Identify the single most important lesson and 2-3 supporting pivots."
        ).format(findings=findings, reflection=reflection)

        response = await self.llm.ainvoke(prompt)
        return {
            "pivots": response.content,
            "status": ["learned"],
        }
