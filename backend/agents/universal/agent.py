import os
import yaml
import logging
from typing import Any, Dict, List, Optional
from backend.llm import llm_manager, LLMRequest, LLMMessage, LLMRole
from .schemas import SkillDefinition, SkillMetadata

logger = logging.getLogger(__name__)

class SkillRegistry:
    """Registry for managing and loading Universal Agent skills."""
    
    def __init__(self, skills_dir: Optional[str] = None):
        if skills_dir is None:
            skills_dir = os.path.join(os.path.dirname(__file__), "skills")
        self.skills_dir = skills_dir
        self._skills_cache: Dict[str, SkillDefinition] = {}

    def get_skill(self, skill_name: str) -> SkillDefinition:
        """Get a skill definition, loading it from disk if necessary."""
        if skill_name in self._skills_cache:
            return self._skills_cache[skill_name]
            
        skill_path = os.path.join(self.skills_dir, f"{skill_name}.yaml")
        if not os.path.exists(skill_path):
            raise FileNotFoundError(f"Skill '{skill_name}' not found at {skill_path}")
            
        with open(skill_path, "r", encoding="utf-8") as f:
            try:
                raw_data = yaml.safe_load(f)
                skill_def = SkillDefinition(**raw_data)
                self._skills_cache[skill_name] = skill_def
                return skill_def
            except (yaml.YAMLError, ValueError) as e:
                logger.error(f"Error parsing skill YAML for '{skill_name}': {e}")
                raise

    def list_skills(self) -> List[str]:
        """List all available skill names in the registry."""
        skills = []
        for filename in os.listdir(self.skills_dir):
            if filename.endswith(".yaml"):
                skills.append(filename[:-5])
        return skills

from .tools import tool_registry, BaseTool

class UniversalAgent:
    """
    Single agent architecture for processing all onboarding steps using dynamic skills.
    Uses native LLMManager for unified interface and better integration.
    """
    
    def __init__(self, model_tier: str = "PRO", skills_dir: Optional[str] = None):
        self.model_tier = model_tier
        self.registry = SkillRegistry(skills_dir)
        self.tool_registry = tool_registry
        
    def register_tool(self, name: str, tool: BaseTool):
        """Register a tool that can be used by the agent."""
        self.tool_registry.register_tool(name, tool)
        
    async def run_step(self, skill_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific onboarding step using the corresponding skill.
        """
        logger.info(f"Running onboarding step with skill: {skill_name}")
        
        try:
            skill_def = self.registry.get_skill(skill_name)
            prompt_template = skill_def.prompt
            system_prompt = skill_def.system_prompt or "You are the RaptorFlow Universal Onboarding Agent."
            
            # Format prompt with input data
            try:
                formatted_prompt = prompt_template.format(**input_data)
            except KeyError as e:
                logger.error(f"Missing input variable for skill '{skill_name}': {e}")
                raise ValueError(f"Missing input variable: {e}")
            
            # Create LLM request
            request = LLMRequest(
                messages=[
                    LLMMessage(role=LLMRole.SYSTEM, content=system_prompt),
                    LLMMessage(role=LLMRole.USER, content=formatted_prompt)
                ],
                model="", # LLMManager will use tier mapping
                temperature=skill_def.parameters.get("temperature", 0.1),
                max_tokens=skill_def.parameters.get("max_tokens", 2048)
            )
            
            # Execute via LLMManager
            response = await llm_manager.generate(request, tier=self.model_tier)
            
            return {
                "success": True,
                "skill": skill_name,
                "metadata": skill_def.metadata.model_dump(),
                "output": response.content
            }
            
        except Exception as e:
            logger.error(f"Error executing skill '{skill_name}': {e}")
            return {
                "success": False,
                "skill": skill_name,
                "error": str(e)
            }
