from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class SkillMetadata(BaseModel):
    name: str = Field(..., description="Unique name of the skill")
    description: str = Field(..., description="What the skill does")
    required_tools: List[str] = Field(default_factory=list, description="List of tool names required by this skill")
    output_format: str = Field(default="JSON", description="Expected output format (JSON, Markdown, Text)")
    version: str = Field(default="1.0.0", description="Version of the skill definition")
    category: Optional[str] = Field(None, description="Category of the onboarding step")

class SkillDefinition(BaseModel):
    metadata: SkillMetadata
    prompt: str = Field(..., description="The main prompt template for the LLM")
    system_prompt: Optional[str] = Field(None, description="Override the default system prompt")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tunable parameters for the skill/LLM")
