"""
Expert Skill Harness
The bridge between high-density Markdown logic and LLM inference.
Parses procedural spines and injects them into the agent's context.
"""

import os
import yaml
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class ExpertSkillHarness:
    """
    The 'Neural Harness' for Expert Skills.
    Loads 200-line Markdown logic spines and prepares them for prompt injection.
    """
    
    def __init__(self, skills_dir: str = "backend/agents/skills/expert_skills"):
        # Resolve path regardless of where the script is run
        base_path = Path(__file__).parent.parent.parent.parent
        self.skills_path = base_path / skills_dir
        self.skill_cache: Dict[str, Dict[str, Any]] = {}
        
    def load_expert_skills(self, expert_id: str) -> str:
        """
        Loads all 200-line logic spines for a specific expert and 
        returns a combined 'System Knowledge' string.
        """
        logger.info(f"[Harness] Loading high-density protocols for expert: {expert_id}")
        
        expert_protocols = []
        
        if not self.skills_path.exists():
            logger.error(f"[Harness] Skills directory not found: {self.skills_path}")
            return ""

        for file in os.listdir(self.skills_path):
            if file.endswith(".md"):
                skill_data = self._parse_skill_file(self.skills_path / file)
                
                # Verify if this skill belongs to the requested expert
                # We check the YAML frontmatter 'expert' field or the filename
                if expert_id.lower() in skill_data.get("expert", "").lower():
                    content = skill_data.get("content", "")
                    expert_protocols.append(content)
                    logger.info(f"[Harness] Injected {file} ({len(content.splitlines())} lines)")

        if not expert_protocols:
            logger.warning(f"[Harness] No skills found for expert: {expert_id}")
            return ""

        return "\n\n".join(expert_protocols)

    def _parse_skill_file(self, file_path: Path) -> Dict[str, Any]:
        """Parses Markdown file with YAML frontmatter."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_content = f.read()
            
            if not raw_content.startswith("---"):
                return {"content": raw_content, "expert": "unknown"}

            # Split YAML and Markdown
            parts = raw_content.split("---", 2)
            metadata = yaml.safe_load(parts[1])
            markdown_logic = parts[2].strip()
            
            metadata["content"] = markdown_logic
            return metadata
        except Exception as e:
            logger.error(f"[Harness] Failed to parse {file_path}: {e}")
            return {"content": "", "expert": "error"}

# Singleton instance
_harness_instance: Optional[ExpertSkillHarness] = None

def get_skill_harness() -> ExpertSkillHarness:
    global _harness_instance
    if _harness_instance is None:
        _harness_instance = ExpertSkillHarness()
    return _harness_instance
