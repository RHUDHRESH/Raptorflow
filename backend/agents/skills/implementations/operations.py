"""
Operations and Optimization executable skills.
"""

import logging
import json
from typing import Any, Dict, List

from ..base import Skill, SkillCategory, SkillLevel

logger = logging.getLogger(__name__)

class CopyPolisherSkill(Skill):
    def __init__(self):
        super().__init__(
            name="copy_polisher",
            category=SkillCategory.OPERATIONS,
            level=SkillLevel.INTERMEDIATE,
            description="Refine and polish text for clarity, grammar, and punchiness.",
            capabilities=["Editing", "Proofreading", "Content refinement"]
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        agent = context.get("agent")
        text = context.get("text")
        tone = context.get("tone", "professional")
        
        system_prompt = f"You are a Senior Editor. Rewrite the text to improve flow, clarity, and impact. Maintain a {tone} tone. Fix any grammar or stylistic errors."
        result = await agent._call_llm(f"Text to Polish:\n{text}", system_prompt=system_prompt)
        return {"polished_text": result}

class DataSynthesizerSkill(Skill):
    def __init__(self):
        super().__init__(
            name="data_synthesizer",
            category=SkillCategory.OPERATIONS,
            level=SkillLevel.ADVANCED,
            description="Synthesize multiple data sources or articles into a coherent insight summary.",
            capabilities=["Data synthesis", "Summarization", "Insight extraction"]
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        agent = context.get("agent")
        sources = context.get("data_sources") # List of strings
        
        system_prompt = "You are a specialized Data Analyst. Synthesize the provided information into 3 Key Insights and a cohesive Summary. Do not just list facts; connect the dots."
        prompt = f"Information Sources:\n{json.dumps(sources)[:3000]}" # Truncate for safety
        result = await agent._call_llm(prompt, system_prompt=system_prompt)
        return {"synthesis": result}

class ReportArchitectSkill(Skill):
    def __init__(self):
        super().__init__(
            name="report_architect",
            category=SkillCategory.OPERATIONS,
            level=SkillLevel.INTERMEDIATE,
            description="Structure raw notes and findings into a professional business report.",
            capabilities=["Report writing", "Formatting", "Business communication"]
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        agent = context.get("agent")
        notes = context.get("notes")
        Report_type = context.get("type", "Executive Brief")
        
        system_prompt = f"You are a Business Consultant. Convert the raw notes into a professional {Report_type}. Use clear headings, bullet points, and an executive summary."
        result = await agent._call_llm(f"Raw Notes:\n{notes}", system_prompt=system_prompt)
        return {"business_report": result}

class ForecastOracleSkill(Skill):
    def __init__(self):
        super().__init__(
            name="forecast_oracle",
            category=SkillCategory.OPERATIONS,
            level=SkillLevel.ADVANCED,
            description="Estimate potential outcomes, ROI, or engagement based on industry benchmarks.",
            capabilities=["Forecasting", "ROI estimation", "Benchmarking"]
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        agent = context.get("agent")
        campaign_details = context.get("campaign_details")
        budget = context.get("budget")
        
        system_prompt = "You are a Marketing Forecaster. Based on standard industry benchmarks (CTR 1-2%, Conv 2-5%), estimate the potential Reach, Clicks, and Conversions for this campaign. Be conservative and provide a range."
        prompt = f"Campaign: {campaign_details}\nBudget: {budget}"
        result = await agent._call_llm(prompt, system_prompt=system_prompt)
        return {"forecast": result}

class ConversionAuditSkill(Skill):
    def __init__(self):
        super().__init__(
            name="conversion_audit",
            category=SkillCategory.OPERATIONS,
            level=SkillLevel.ADVANCED,
            description="Audit a landing page or copy for conversion rate optimization opportunities.",
            capabilities=["CRO", "UX Audit", "Persuasion analysis"]
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        agent = context.get("agent")
        content_or_url = context.get("content")
        
        system_prompt = "You are a CRO Expert. Audit the content for conversion blockers. Identify 3 flaws and suggest 3 high-impact improvements to boost conversion rate."
        result = await agent._call_llm(f"Content to Audit:\n{content_or_url}", system_prompt=system_prompt)
        return {"cro_audit": result}
