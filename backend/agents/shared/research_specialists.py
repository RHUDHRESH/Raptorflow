import json
from typing import List

from langchain_core.messages import HumanMessage, SystemMessage

from inference import InferenceProvider
from models.research_schemas import FactClaim, WebDocument


class LibrarianAgent:
    """A00: Specialized in query expansion and source discovery."""

    def __init__(self):
        self.llm = InferenceProvider.get_model(model_tier="smart")

    async def plan_search(self, objective: str, prior_logs: List[str]) -> List[str]:
        system = SystemMessage(
            content="""
            You are the Master Librarian.
            Given a research objective, generate 5 surgical search queries.
            Vary the perspective:
            1. Direct (The answer)
            2. Contextual (The background)
            3. Contrarian (Opposing views)
            4. Technical (The 'how')
            5. Case Study (Real examples)
        """
        )
        user = HumanMessage(content=f"Objective: {objective}\nLogs: {prior_logs}")
        res = await self.llm.ainvoke([system, user])
        # In prod, use structured output parser. For now, assume newline separated.
        return res.content.split("\n")


class FactCheckerAgent:
    """A05: Specialized in finding contradictions and validating claims."""

    def __init__(self):
        self.llm = InferenceProvider.get_model(model_tier="ultra")

    async def verify_claim(self, claim: FactClaim, all_docs: List[WebDocument]) -> str:
        system = SystemMessage(
            content="""
            You are the Surgical Fact-Checker.
            Verify the following claim against the provided corpus.
            Mark as 'verified', 'debunked', or 'conflicting'.
            Provide a one-sentence rationale.
        """
        )
        context = "\n\n".join([f"SOURCE {d.url}: {d.summary}" for d in all_docs])
        user = HumanMessage(content=f"CLAIM: {claim.claim}\n\nCORPUS:\n{context}")
        res = await self.llm.ainvoke([system, user])
        return res.content


class SynthesisAgent:
    """A11: Specialized in MasterClass-grade reports with citations."""

    def __init__(self):
        self.llm = InferenceProvider.get_model(model_tier="ultra")

    async def generate_report(
        self, objective: str, verified_claims: List[FactClaim]
    ) -> str:
        system = SystemMessage(
            content="""
            You are the Lead Research Strategist.
            Synthesize the verified evidence into a surgical executive report.
            Style: MasterClass polish + Editorial restraint.
            Use Footnotes [1], [2] linked to sources.
            Structure: Executive Summary -> The Hard Truths -> Evidence Chains -> Recommendations.
        """
        )
        claims_json = json.dumps([c.dict() for c in verified_claims])
        user = HumanMessage(
            content=f"OBJECTIVE: {objective}\n\nVERIFIED EVIDENCE:\n{claims_json}"
        )
        res = await self.llm.ainvoke([system, user])
        return res.content
