"""
Simplified agent configuration management system.
Provides centralized configuration for agents, skills, and tools.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
import json
import yaml

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for a single agent."""
    
    name: str
    description: str
    model_tier: str = "flash_lite"
    tools: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    enabled: bool = True
    timeout_seconds: int = 120
    max_tokens: int = 8192
    temperature: float = 0.7
    priority: int = 5
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillConfig:
    """Configuration for a skill."""
    
    name: str
    category: str
    description: str
    level: str = "intermediate"
    enabled: bool = True
    capabilities: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ToolConfig:
    """Configuration for a tool."""
    
    name: str
    description: str
    enabled: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 30
    retry_count: int = 3
    dependencies: List[str] = field(default_factory=list)


@dataclass
class SystemConfig:
    """System-wide configuration."""
    
    agents: Dict[str, AgentConfig] = field(default_factory=dict)
    skills: Dict[str, SkillConfig] = field(default_factory=dict)
    tools: Dict[str, ToolConfig] = field(default_factory=dict)
    global_settings: Dict[str, Any] = field(default_factory=dict)
    
    # Performance settings
    default_timeout: int = 120
    default_max_tokens: int = 8192
    default_temperature: float = 0.7
    cache_ttl: int = 3600
    
    # Security settings
    enable_security_validation: bool = True
    enable_rate_limiting: bool = True
    max_requests_per_minute: int = 60
    max_concurrent_agents: int = 10
    
    # Monitoring settings
    enable_health_monitoring: bool = True
    enable_performance_monitoring: bool = True
    health_check_interval: int = 60
    
    # Optimization settings
    optimization_level: str = "balanced"
    enable_caching: bool = True
    enable_connection_pooling: bool = True


class ConfigurationManager:
    """Manages agent, skill, and tool configurations."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "config/agent_config.yaml"
        self.config = SystemConfig()
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file."""
        config_path = Path(self.config_file)
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = yaml.safe_load(f)
                    self._update_from_dict(data)
                logger.info(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                logger.error(f"Failed to load config from {self.config_file}: {e}")
                self._create_default_config()
        else:
            logger.info(f"Config file {self.config_file} not found, creating default")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration."""
        # Default agent configurations
        self.config.agents = {
            "icp_architect": AgentConfig(
                name="ICPArchitect",
                description="Creates and manages Ideal Customer Profiles using cognitive psychology models",
                model_tier="flash",
                tools=["web_search", "database", "content_gen"],
                skills=["persona_builder", "content_generation"],
                enabled=True,
                priority=10
            ),
            "content_creator": AgentConfig(
                name="ContentCreator",
                description="Generates various types of content based on requirements",
                model_tier="flash",
                tools=["web_search", "database", "content_gen"],
                skills=["content_generation", "copy_polisher", "viral_hook"],
                enabled=True,
                priority=8
            ),
            "marketing_strategist": AgentConfig(
                name="MarketingStrategist",
                description="Develops marketing strategies and campaigns",
                model_tier="pro",
                tools=["web_search", "database", "content_gen"],
                skills=["content_generation", "copy_polisher", "viral_hook", "seo_analysis"],
                enabled=True,
                priority=9
            ),
            "data_analyst": AgentConfig(
                name="DataAnalyst",
                description="Analyzes data and provides insights",
                model_tier="pro",
                tools=["web_search", "database"],
                skills=["content_generation", "analysis"],
                enabled=True,
                priority=7
            ),
        }
        
        # Default skill configurations
        self.config.skills = {
            "content_generation": SkillConfig(
                name="content_generation",
                category="content",
                level="intermediate",
                description="Generate various types of content",
                capabilities=["Writing", "Creation", "Generation"],
                parameters={"max_length": 10000, "style": "professional"}
            ),
            "copy_polisher": SkillConfig(
                name="copy_polisher",
                category="operations",
                level="intermediate",
                description="Refine and polish text for clarity and impact",
                capabilities=["Editing", "Proofreading", "Content refinement"],
                parameters={"tone": "professional"}
            ),
            "viral_hook": SkillConfig(
                name="viral_hook",
                category="creative",
                level="advanced",
                description="Generate high-conversion hooks for content",
                capabilities=["Copywriting", "Hook generation", "Attention engineering"],
                parameters={"max_hooks": 10}
            ),
            "seo_analysis": SkillConfig(
                name="seo_analysis",
                category="analysis",
                level="intermediate",
                description="Analyze content for SEO optimization",
                capabilities=["SEO", "Analysis", "Optimization"],
                parameters={"depth": "comprehensive"}
            ),
            "persona_builder": SkillConfig(
                name="persona_builder",
                category="strategy",
                level="intermediate",
                description="Create detailed buyer personas",
                capabilities=["Persona creation", "Customer profiling", "Empathy mapping"],
                parameters={"detail_level": "comprehensive"}
            ),
        }
        
        # Default tool configurations
        self.config.tools = {
            "web_search": ToolConfig(
                name="web_search",
                description="Search the web for information",
                enabled=True,
                timeout_seconds=30,
                retry_count=3
            ),
            "database": ToolConfig(
                name="database",
                description="Access and manipulate database",
                enabled=True,
                timeout_seconds=30,
                retry_count=3
            ),
            "content_gen": ToolConfig(
                name="content_gen",
                description="Generate content using LLM",
                enabled=True,
                timeout_seconds=60,
                retry_count=3
            ),
        }
        
        # Default global settings
        self.config.global_settings = {
            "system_version": "1.3.0",
            "api_version": "v1",
            "default_language": "en",
            "timezone": "UTC",
            "log_level": "INFO",
        }
        
        self._save_config()
    
    def _update_from_dict(self, data: Dict[str, Any]):
        """Update configuration from dictionary."""
        # Update agents
        if "agents" in data:
            for name, agent_data in data["agents"].items():
                self.config.agents[name] = AgentConfig(**agent_data)
        
        # Update skills
        if "skills" in data:
            for name, skill_data in data["skills"].items():
                self.config.skills[name] = SkillConfig(**skill_data)
        
        # Update tools
        if "tools" in data:
            for name, tool_data in data["tools"].items():
                self.config.tools[name] = ToolConfig(**tool_data)
        
        # Update global settings
        if "global_settings" in data:
            self.config.global_settings.update(data["global_settings"])
    
    def _save_config(self):
        """Save configuration to file."""
        config_path = Path(self.config_file)
        
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dictionary
        config_dict = {
            "agents": {name: asdict(agent) for name, agent in self.config.agents.items()},
            "skills": {name: asdict(skill) for name, skill in self.config.skills.items()},
            "tools": {name: asdict(tool) for name, tool in self.config.tools.items()},
            "global_settings": self.config.global_settings,
        }
        
        try:
            with open(config_path, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            logger.info(f"Saved configuration to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save config to {self.config_file}: {e}")
    
    def get_agent_config(self, agent_name: str) -> Optional[AgentConfig]:
        """Get configuration for a specific agent."""
        return self.config.agents.get(agent_name)
    
    def get_skill_config(self, skill_name: str) -> Optional[SkillConfig]:
        """Get configuration for a specific skill."""
        return self.config.skills.get(skill_name)
    
    def get_tool_config(self, tool_name: str) -> Optional[ToolConfig]:
        """Get configuration for a specific tool."""
        return self.config.tools.get(tool_name)
    
    def list_agents(self) -> List[str]:
        """List all configured agents."""
        return list(self.config.agents.keys())
    
    def list_skills(self) -> List[str]:
        """List all configured skills."""
        return list(self.config.skills.keys())
    
    def list_tools(self) -> List[str]:
        """List all configured tools."""
        return list(self.config.tools.keys())
    
    def add_agent(self, agent_config: AgentConfig) -> None:
        """Add or update an agent configuration."""
        self.config.agents[agent_config.name] = agent_config
        self._save_config()
        logger.info(f"Added/updated agent: {agent_config.name}")
    
    def add_skill(self, skill_config: SkillConfig) -> None:
        """Add or update a skill configuration."""
        self.config.skills[skill_config.name] = skill_config
        self._save_config()
        logger.info(f"Added/updated skill: {skill_config.name}")
    
    def add_tool(self, tool_config: ToolConfig) -> None:
        """Add or update a tool configuration."""
        self.config.tools[tool_config.name] = tool_config
        self._save_config()
        logger.info(f"Added/updated tool: {tool_config.name}")
    
    def remove_agent(self, agent_name: str) -> bool:
        """Remove an agent configuration."""
        if agent_name in self.config.agents:
            del self.config.agents[agent_name]
            self._save_config()
            logger.info(f"Removed agent: {agent_name}")
            return True
        return False
    
    def remove_skill(self, skill_name: str) -> bool:
        """Remove a skill configuration."""
        if skill_name in self.config.skills:
            del self.config.skills[skill_name]
            self._save_config()
            logger.info(f"Removed skill: {skill_name}")
            return True
        return False
    
    def remove_tool(self, tool_name: str) -> bool:
        """Remove a tool configuration."""
        if tool_name in self.config.tools:
            del self.config.tools[tool_name]
            self._save_config()
            logger.info(f"Removed tool: {tool_name}")
            return True
        return False
    
    def enable_agent(self, agent_name: str) -> bool:
        """Enable an agent."""
        if agent_name in self.config.agents:
            self.config.agents[agent_name].enabled = True
            self._save_config()
            logger.info(f"Enabled agent: {agent_name}")
            return True
        return False
    
    def disable_agent(self, agent_name: str) -> bool:
        """Disable an agent."""
        if agent_name in self.config.agents:
            self.config.agents[agent_name].enabled = False
            self._save_config()
            logger.info(f"Disabled agent: {agent_name}")
            return True
        return False
    
    def enable_skill(self, skill_name: str) -> bool:
        """Enable a skill."""
        if skill_name in self.config.skills:
            self.config.skills[skill_name].enabled = True
            self._save_config()
            logger.info(f"Enabled skill: {skill_name}")
            return True
        return False
    
    def disable_skill(self, skill_name: str) -> bool:
        """Disable a skill."""
        if skill_name in self.config.skills:
            self.config.skills[skill_name].enabled = False
            self._save_config()
            logger.info(f"Disabled skill: {skill_name}")
            return True
        return False
    
    def enable_tool(self, tool_name: str) -> bool:
        """Enable a tool."""
        if tool_name in self.config.tools:
            self.config.tools[tool_name].enabled = True
            self._save_config()
            logger.info(f"Enabled tool: {tool_name}")
            return True
        return False
    
    def disable_tool(self, tool_name: str) -> bool:
        """Disable a tool."""
        if tool_name in self.config.tools:
            self.config.tools[tool_name].enabled = False
            self._save_config()
            logger.info(f"Disabled tool: {tool_name}")
            return True
        return False
    
    def update_agent_config(self, agent_name: str, **kwargs) -> bool:
        """Update agent configuration."""
        if agent_name not in self.config.agents:
            return False
        
        agent_config = self.config.agents[agent_name]
        for key, value in kwargs.items():
            if hasattr(agent_config, key):
                setattr(agent_config, key, value)
        
        self._save_config()
        logger.info(f"Updated agent configuration: {agent_name}")
        return True
    
    def get_enabled_agents(self) -> List[str]:
        """Get list of enabled agents."""
        return [name for name, config in self.config.agents.items() if config.enabled]
    
    def get_enabled_skills(self) -> List[str]:
        """Get list of enabled skills."""
        return [name for name, config in self.config.skills.items() if config.enabled]
    
    def get_enabled_tools(self) -> List[str]:
        """Get list of enabled tools."""
        return [name for name, config in self.config.tools.items() if config.enabled]
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate the configuration."""
        errors = []
        warnings = []
        
        # Check for required fields
        required_agent_fields = ["name", "description"]
        for agent_name, agent_config in self.config.agents.items():
            for field in required_agent_fields:
                if not getattr(agent_config, field, None):
                    errors.append(f"Agent {agent_name} missing required field: {field}")
        
        # Check for circular dependencies
        for agent_name, agent_config in self.config.agents.items():
            # Check tool dependencies
            for tool_name in agent_config.tools:
                tool_config = self.config.tools.get(tool_name)
                if tool_name not in self.config.tools:
                    errors.append(f"Agent {agent_name} references unknown tool: {tool_name}")
            
            # Check skill dependencies
            for skill_name in agent_config.skills:
                skill_config = self.config.skills.get(skill_name)
                if skill_name not in self.config.skills:
                    errors.append(f"Agent {agent_name} references unknown skill: {skill_name}")
        
        # Check for circular skill dependencies
        for skill_name, skill_config in self.config.skills.items():
            for dependency in skill_config.dependencies:
                if dependency not in self.config.skills:
                    errors.append(f"Skill {skill_name} references unknown skill: {dependency}")
        
        # Check for circular tool dependencies
        for tool_name, tool_config in self.config.tools.items():
            for dependency in tool_config.dependencies:
                if dependency not in self.config.tools:
                    errors.append(f"Tool {tool_name} references unknown tool: {dependency}")
        
        result = {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "stats": {
                "total_agents": len(self.config.agents),
                "enabled_agents": len(self.get_enabled_agents()),
                "total_skills": len(self.config.skills),
                "enabled_skills": len(self.get_enabled_skills()),
                "total_tools": len(self.config.tools),
                "enabled_tools": len(self.get_enabled_tools()),
            }
        }
        
        if errors:
            logger.error(f"Configuration validation failed: {errors}")
        else:
            logger.info("Configuration validation passed")
        
        return result
    
    def export_config(self, format: str = "yaml") -> str:
        """Export configuration to string."""
        if format.lower() == "json":
            return json.dumps({
                "agents": {name: asdict(agent) for name, agent in self.config.agents.items()},
                "skills": {name: asdict(skill) for name, skill in self.config.skills.items()},
                "tools": {name: asdict(tool) for name, tool in self.config.tools.items()},
                "global_settings": self.config.global_settings,
            }, indent=2)
        elif format.lower() == "yaml":
            return yaml.dump({
                "agents": {name: asdict(agent) for name, agent in self.config.agents.items()},
                "skills": {name: asdict(skill) for name, skill in self.config.skills.items()},
                "tools": {name: asdict(tool) for name, tool in self.config.tools.items()},
                "global_settings": self.config.global_settings,
            }, default_flow_style=False, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def import_config(self, config_string: str, format: str = "yaml") -> None:
        """Import configuration from string."""
        if format.lower() == "json":
            data = json.loads(config_string)
        elif format.lower() == "yaml":
            data = yaml.safe_load(config_string)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        self._update_from_dict(data)
        logger.info(f"Imported configuration from string")
    
    def reload_config(self) -> None:
        """Reload configuration from file."""
        self._load_config()
        logger.info("Configuration reloaded")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the configuration."""
        return {
            "agents": {
                "total": len(self.config.agents),
                "enabled": len(self.get_enabled_agents()),
                "disabled": len(self.config.agents) - len(self.get_enabled_agents())
            },
            "skills": {
                "total": len(self.config.skills),
                "enabled": len(self.get_enabled_skills()),
                "disabled": len(self.config.skills) - len(self.get_enabled_skills())
            },
            "tools": {
                "total": len(self.config.tools),
                "enabled": len(self.get_enabled_tools()),
                "disabled": len(self.config.tools) - len(self.get_enabled_tools())
            },
            "global_settings": self.config.global_settings
        }


# Global configuration manager instance
_config_manager: Optional[ConfigurationManager] = None


def get_config_manager() -> ConfigurationManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager


def get_agent_config(agent_name: str) -> Optional[AgentConfig]:
    """Get agent configuration (convenience function)."""
    manager = get_config_manager()
    return manager.get_agent_config(agent_name)


def get_skill_config(skill_name: str) -> Optional[SkillConfig]:
    """Get skill configuration (convenience function)."""
    manager = get_config_manager()
    return manager.get_skill_config(skill_name)


def get_tool_config(tool_name: str) -> Optional[ToolConfig]:
    """Get tool configuration (convenience function)."""
    manager = get_config_manager()
    return manager.get_tool_config(tool_name)


def list_enabled_agents() -> List[str]:
    """List enabled agents (convenience function)."""
    manager = get_config_manager()
    return manager.get_enabled_agents()


def list_enabled_skills() -> List[str]:
    """List enabled skills (convenience function)."""
    manager = get_config_manager()
    return manager.get_enabled_skills()


def list_enabled_tools() -> List[str]:
    """List enabled tools (convenience function)."""
    manager = get_config_manager()
    return manager.get_enabled_tools()


# Configuration decorators
def require_agent(agent_name: str):
    """Decorator to ensure agent is configured and enabled."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            manager = get_config_manager()
            agent_config = manager.get_agent_config(agent_name)
            
            if not agent_config:
                raise ValueError(f"Agent '{agent_name}' not found in configuration")
            
            if not agent_config.enabled:
                raise ValueError(f"Agent '{agent_name}' is disabled")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_skill(skill_name: str):
    """Decorator to ensure skill is configured and enabled."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            manager = get_config_manager()
            skill_config = manager.get_skill_config(skill_name)
            
            if not skill_config:
                raise ValueError(f"Skill '{skill_name}' not found in configuration")
            
            if not skill_config.enabled:
                raise ValueError(f"Skill '{skill_name}' is disabled")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_tool(tool_name: str):
    """Decorator to ensure tool is configured and enabled."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            manager = get_config_manager()
            tool_config = manager.get_tool_config(tool_name)
            
            if not tool_config:
                raise ValueError(f"Tool '{tool_name}' not found in configuration")
            
            if not tool_config.enabled:
                raise ValueError(f"Tool '{tool_name}' is disabled")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Environment-based configuration loading
def load_config_from_env() -> ConfigurationManager:
    """Load configuration from environment variables."""
    manager = ConfigurationManager()
    
    # Override with environment variables if present
    import os
    
    # Database configuration
    if os.getenv("DATABASE_URL"):
        manager.config.global_settings["database_url"] = os.getenv("DATABASE_URL")
    
    # Redis configuration
    if os.getenv("REDIS_URL"):
        manager.config.global_settings["redis_url"] = os.getenv("REDIS_URL")
    
    # LLM configuration
    if os.getenv("GOOGLE_API_KEY"):
        manager.config.global_settings["google_api_key"] = os.getenv("GOOGLE_API_KEY")
    if os.getenv("GOOGLE_PROJECT_ID"):
        manager.config.global_settings["google_project_id"] = os.getenv("GOOGLE_PROJECT_ID")
    if os.getenv("GOOGLE_REGION"):
        manager.config.global_settings["google_region"] = os.getenv("GOOGLE_REGION", "us-central1")
    
    # Security configuration
    if os.getenv("SECRET_KEY"):
        manager.config.global_settings["secret_key"] = os.getenv("SECRET_KEY")
    
    # Performance configuration
    if os.getenv("MAX_CONCURRENT_AGENTS"):
        manager.config.max_concurrent_agents = int(os.getenv("MAX_CONCURRENT_AGENTS", "10"))
    
    # Save updated configuration
    manager._save_config()
    
    return manager


# Auto-reload configuration on file changes
def enable_auto_reload(interval: int = 60):
    """Enable automatic configuration reloading."""
    import asyncio
    
    async def reload_loop():
        while True:
            try:
                await asyncio.sleep(interval)
                manager = get_config_manager()
                manager.reload_config()
                logger.info("Configuration auto-reloaded")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Auto-reload error: {e}")
    
    asyncio.create_task(reload_loop())


# Validation functions
def validate_agent_config(agent_name: str) -> bool:
    """Validate a specific agent configuration."""
    manager = get_config_manager()
    agent_config = manager.get_agent_config(agent_name)
    return agent_config is not None and agent_config.enabled


def validate_skill_config(skill_name: str) -> bool:
    """Validate a specific skill configuration."""
    manager = get_config_manager()
    skill_config = manager.get_skill_config(skill_name)
    return skill_config is not None and skill_config.enabled


def validate_tool_config(tool_name: str) -> bool:
    """Validate a specific tool configuration."""
    manager = get_config_manager()
    tool_config = manager.get_tool_config(tool_name)
    return tool_config is not None and tool_config.enabled


# Configuration validation for deployment
def validate_deployment_config() -> Dict[str, Any]:
    """Validate configuration for deployment."""
    manager = get_config_manager()
    validation_result = manager.validate_config()
    
    if not validation_result["valid"]:
        raise ValueError(f"Configuration validation failed: {validation_result['errors']}")
    
    # Additional deployment-specific validations
    warnings = validation_result["warnings"]
    
    # Check for required environment variables
    required_env_vars = ["GOOGLE_API_KEY", "GOOGLE_PROJECT_ID", "SECRET_KEY"]
    missing_vars = []
    
    import os
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        warnings.append(f"Missing environment variables: {missing_vars}")
    
    # Check for optional but recommended environment variables
    recommended_env_vars = ["REDIS_URL", "DATABASE_URL"]
    missing_recommended = []
    
    for var in recommended_env_vars:
        if not os.getenv(var):
            missing_recommended.append(f"Recommended: {var}")
    
    if missing_recommended:
        warnings.extend([f"Missing recommended environment variables: {missing_recommended}"])
    
    validation_result["warnings"] = warnings
    
    return validation_result
