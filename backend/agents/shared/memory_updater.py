from typing import List, Optional
from pydantic import BaseModel, Field
from inference import InferenceProvider
from langchain_core.messages import SystemMessage, HumanMessage

class StyleRule(BaseModel):
    key: str = Field(description="The preference key (e.g. 'emoji_usage', 'paragraph_style')")
    value: str = Field(description="The learned rule (e.g. 'Never use emojis', 'Max 2 sentences per paragraph')")
    confidence: float = Field(description="Confidence 0-1. Only return if > 0.8")
    evidence: str = Field(description="One sentence explaining what changed to trigger this rule")

class MemoryUpdaterAgent:
    def __init__(self):
        self.llm = InferenceProvider.get_model(model_tier="smart").with_structured_output(StyleRule)

    async def extract_preference(self, draft: str, final: str) -> Optional[StyleRule]:
        """
        Analyzes the delta between AI output and User final version.
        Extracts high-fidelity stylistic preferences.
        """
        if draft.strip() == final.strip():
            return None

        system_msg = SystemMessage(content="""
            You are the RaptorFlow Cognitive Memory Engine.
            Compare the AI Draft and the User's Final version.
            Identify ONE surgical stylistic preference the user demonstrated.
            
            EXAMPLES:
            - AI used emojis, user removed them -> Rule: "no_emojis" | "User hates emojis."
            - AI wrote 5 paragraphs, user merged into 2 -> Rule: "paragraph_length" | "Prefers short, consolidated blocks."
            - AI used 'Unlock', user changed to 'Build' -> Rule: "taboo_words" | "Avoid 'Unlock'; use 'Build'."
            
            Return null if no clear pattern is found.
        """)
        
        comparison = f"AI DRAFT:\n{draft}\n\nUSER FINAL:\n{final}"
        
        try:
            return await self.llm.ainvoke([system_msg, HumanMessage(content=comparison)])
        except Exception:
            return None
