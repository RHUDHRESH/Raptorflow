import logging
from typing import Dict, Any, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from backend.inference import InferenceProvider

logger = logging.getLogger("raptorflow.core.validation")

class ValidationResult(BaseModel):
    """SOTA structured research evaluation."""
    is_high_quality: bool = Field(description="Whether the content meets industrial standards.")
    score: float = Field(description="0 to 1 score of factual density.")
    issues: List[str] = Field(description="List of quality issues (e.g., fluff, bias).")
    improvement_suggestions: List[str] = Field(description="How to make this data strategic.")

class ResearchValidator:
    """
    Industrial Data Validation Layer.
    Audits incoming research for factual density, quality, and strategic readiness.
    """
    def __init__(self, llm: Optional[Any] = None):
        self.llm = llm or InferenceProvider.get_model(model_tier="driver")
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
                You are a Ruthless Editorial Research Lead. 
                Your job is to audit incoming research data for RaptorFlow.
                
                CRITERIA:
                1. Factual Density: Does it contain specific numbers, dates, or names?
                2. Strategic Value: Can a founder make a decision based on this?
                3. Non-Redundancy: Is it unique information?
                
                REJECT if the content is generic marketing fluff or AI-generated 'vibes'.
            """),
            ("user", "Audit this content: {content}")
        ])
        # Allow passing a pre-built chain for easier testing
        self.chain = self.prompt | self.llm.with_structured_output(ValidationResult)

    async def validate_content(self, content: str) -> Dict[str, Any]:
        """Executes the audit chain."""
        logger.info("Auditing research artifact quality...")
        try:
            result = await self.chain.ainvoke({"content": content})
            return result.model_dump()
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return {
                "is_high_quality": False,
                "score": 0.0,
                "issues": [f"Validator Error: {str(e)}"],
                "improvement_suggestions": []
            }
