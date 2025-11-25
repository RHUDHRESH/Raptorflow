"""
Swarm Configuration

Central configuration for the agent swarm system.
"""

from typing import List, Dict, Any
from enum import Enum


# ============================================================================
# AGENT DEFINITIONS
# ============================================================================

class AgentDefinition:
    """Definition of an agent in the swarm"""

    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        capabilities: List[str],
        pod: str,
        max_concurrent: int = 5,
        timeout_seconds: float = 120.0,
        retry_count: int = 3
    ):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.capabilities = capabilities
        self.pod = pod
        self.max_concurrent = max_concurrent
        self.timeout_seconds = timeout_seconds
        self.retry_count = retry_count


AGENT_DEFINITIONS = {
    # Strategy Sector
    "STRAT-01": AgentDefinition(
        agent_id="STRAT-01",
        agent_name="MoveArchitect",
        capabilities=["strategy_design", "campaign_planning", "goal_analysis"],
        pod="strategy",
        max_concurrent=3,
        timeout_seconds=60.0
    ),

    "PSY-01": AgentDefinition(
        agent_id="PSY-01",
        agent_name="PsycheLens",
        capabilities=["audience_analysis", "psychographics", "cohort_profiling"],
        pod="strategy",
        max_concurrent=3,
        timeout_seconds=45.0
    ),

    "EXP-01": AgentDefinition(
        agent_id="EXP-01",
        agent_name="SplitMind",
        capabilities=["ab_testing", "experiment_design", "statistical_analysis"],
        pod="strategy",
        max_concurrent=3,
        timeout_seconds=30.0
    ),

    # Creation Sector
    "IDEA-01": AgentDefinition(
        agent_id="IDEA-01",
        agent_name="MuseForge",
        capabilities=["content_ideation", "hook_generation", "narrative_design"],
        pod="creation",
        max_concurrent=2,
        timeout_seconds=90.0
    ),

    "COPY-01": AgentDefinition(
        agent_id="COPY-01",
        agent_name="LyraQuill",
        capabilities=["copywriting", "email", "linkedin", "twitter", "instagram"],
        pod="creation",
        max_concurrent=5,
        timeout_seconds=60.0
    ),

    "VIS-01": AgentDefinition(
        agent_id="VIS-01",
        agent_name="NoirFrame",
        capabilities=["visual_design", "design_direction", "composition_strategy"],
        pod="creation",
        max_concurrent=4,
        timeout_seconds=45.0
    ),

    "ADAPT-01": AgentDefinition(
        agent_id="ADAPT-01",
        agent_name="PortaMorph",
        capabilities=["content_adaptation", "platform_translation", "repurposing"],
        pod="creation",
        max_concurrent=5,
        timeout_seconds=30.0
    ),

    # Signals Sector
    "METRIC-01": AgentDefinition(
        agent_id="METRIC-01",
        agent_name="OptiMatrix",
        capabilities=["performance_analysis", "optimization", "metric_tracking"],
        pod="signals",
        max_concurrent=3,
        timeout_seconds=30.0
    ),

    "TREND-01": AgentDefinition(
        agent_id="TREND-01",
        agent_name="PulseSeer",
        capabilities=["trend_detection", "trend_prediction", "opportunity_scoring"],
        pod="signals",
        max_concurrent=2,
        timeout_seconds=120.0
    ),

    "COMP-01": AgentDefinition(
        agent_id="COMP-01",
        agent_name="MirrorScout",
        capabilities=["competitor_analysis", "content_scraping", "pattern_extraction"],
        pod="signals",
        max_concurrent=2,
        timeout_seconds=180.0
    ),

    # Risk Sector
    "CRISIS-01": AgentDefinition(
        agent_id="CRISIS-01",
        agent_name="FirewallMaven",
        capabilities=["brand_safety", "compliance", "risk_assessment"],
        pod="risk",
        max_concurrent=3,
        timeout_seconds=30.0
    ),

    "PA": AgentDefinition(
        agent_id="PA",
        agent_name="PolicyArbiter",
        capabilities=["conflict_resolution", "decision_making", "policy_enforcement"],
        pod="executive",
        max_concurrent=5,
        timeout_seconds=120.0
    ),
}


# ============================================================================
# WORKFLOW DEFINITIONS
# ============================================================================

class WorkflowDefinition:
    """Definition of a workflow type"""

    def __init__(
        self,
        workflow_type: str,
        description: str,
        stages: List[Dict[str, Any]],
        timeout_minutes: int = 30
    ):
        self.workflow_type = workflow_type
        self.description = description
        self.stages = stages
        self.timeout_minutes = timeout_minutes


WORKFLOW_DEFINITIONS = {
    "move_creation": WorkflowDefinition(
        workflow_type="move_creation",
        description="Create a complete marketing move with full swarm collaboration",
        stages=[
            {
                "name": "research_analysis",
                "description": "Research and analyze goal, cohorts, trends, competitors",
                "parallel": True,
                "required_agents": ["STRAT-01", "PSY-01", "TREND-01", "COMP-01"]
            },
            {
                "name": "conflict_resolution",
                "description": "Resolve any conflicts in recommendations",
                "parallel": False,
                "required_agents": ["PA"]
            },
            {
                "name": "content_creation",
                "description": "Create content with ideas, copy, and visuals",
                "parallel": True,
                "required_agents": ["IDEA-01", "COPY-01", "VIS-01"]
            },
            {
                "name": "adaptation",
                "description": "Adapt content across platforms",
                "parallel": False,
                "required_agents": ["ADAPT-01"]
            },
            {
                "name": "quality_review",
                "description": "Review for brand safety and quality",
                "parallel": True,
                "required_agents": ["CRISIS-01"]
            }
        ],
        timeout_minutes=30
    ),

    "content_generation": WorkflowDefinition(
        workflow_type="content_generation",
        description="Generate content for a specific brief",
        stages=[
            {
                "name": "ideation",
                "description": "Generate content ideas",
                "parallel": False,
                "required_agents": ["IDEA-01"]
            },
            {
                "name": "creation",
                "description": "Write copy and design visuals",
                "parallel": True,
                "required_agents": ["COPY-01", "VIS-01"]
            },
            {
                "name": "review",
                "description": "Review for quality and brand safety",
                "parallel": False,
                "required_agents": ["CRISIS-01"]
            }
        ],
        timeout_minutes=20
    ),

    "performance_analysis": WorkflowDefinition(
        workflow_type="performance_analysis",
        description="Analyze move performance and optimize",
        stages=[
            {
                "name": "metric_collection",
                "description": "Collect and aggregate metrics",
                "parallel": False,
                "required_agents": ["METRIC-01"]
            },
            {
                "name": "insights",
                "description": "Generate insights from metrics",
                "parallel": False,
                "required_agents": ["METRIC-01"]
            }
        ],
        timeout_minutes=15
    ),
}


# ============================================================================
# SECTOR CONFIGURATION
# ============================================================================

class SectorConfig:
    """Configuration for an agent sector"""

    def __init__(
        self,
        sector_id: str,
        sector_name: str,
        agents: List[str],
        description: str
    ):
        self.sector_id = sector_id
        self.sector_name = sector_name
        self.agents = agents
        self.description = description


SECTOR_CONFIG = {
    "strategy": SectorConfig(
        sector_id="strategy",
        sector_name="Strategy Sector",
        agents=["STRAT-01", "PSY-01", "EXP-01"],
        description="Campaign strategy, planning, and testing"
    ),

    "creation": SectorConfig(
        sector_id="creation",
        sector_name="Creation Sector",
        agents=["IDEA-01", "COPY-01", "VIS-01", "ADAPT-01"],
        description="Content creation and adaptation"
    ),

    "signals": SectorConfig(
        sector_id="signals",
        sector_name="Signals Sector",
        agents=["METRIC-01", "TREND-01", "COMP-01"],
        description="Analytics, trends, competitor intelligence"
    ),

    "risk": SectorConfig(
        sector_id="risk",
        sector_name="Risk & Governance Sector",
        agents=["CRISIS-01"],
        description="Brand safety, compliance, risk management"
    ),

    "executive": SectorConfig(
        sector_id="executive",
        sector_name="Executive Sector",
        agents=["PA"],
        description="Orchestration, conflict resolution, policy"
    ),
}


# ============================================================================
# ORCHESTRATOR SETTINGS
# ============================================================================

class OrchestratorSettings:
    """Global orchestrator settings"""

    # Message queue
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 0
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

    # Execution settings
    DEFAULT_WORKFLOW_TIMEOUT = 30 * 60  # 30 minutes
    DEFAULT_STAGE_TIMEOUT = 5 * 60  # 5 minutes
    DEFAULT_AGENT_TIMEOUT = 2 * 60  # 2 minutes

    # Polling settings
    CONTEXT_POLL_INTERVAL = 0.5  # seconds
    MAX_RETRIES = 3
    RETRY_BACKOFF = 2  # exponential backoff multiplier

    # Buffer settings
    MESSAGE_BUFFER_SIZE = 10000
    CONTEXT_BUFFER_SIZE = 5000

    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "[%(name)s] %(message)s"

    # Monitoring
    ENABLE_MONITORING = True
    METRICS_INTERVAL = 60  # seconds
    HEALTH_CHECK_INTERVAL = 300  # seconds


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_agent_definition(agent_id: str) -> AgentDefinition:
    """Get agent definition by ID"""

    if agent_id not in AGENT_DEFINITIONS:
        raise ValueError(f"Unknown agent: {agent_id}")

    return AGENT_DEFINITIONS[agent_id]


def get_workflow_definition(workflow_type: str) -> WorkflowDefinition:
    """Get workflow definition by type"""

    if workflow_type not in WORKFLOW_DEFINITIONS:
        raise ValueError(f"Unknown workflow: {workflow_type}")

    return WORKFLOW_DEFINITIONS[workflow_type]


def get_agents_by_sector(sector_id: str) -> List[AgentDefinition]:
    """Get all agents in a sector"""

    if sector_id not in SECTOR_CONFIG:
        raise ValueError(f"Unknown sector: {sector_id}")

    agent_ids = SECTOR_CONFIG[sector_id].agents
    return [AGENT_DEFINITIONS[agent_id] for agent_id in agent_ids]


def get_all_agents() -> List[AgentDefinition]:
    """Get all agent definitions"""

    return list(AGENT_DEFINITIONS.values())


# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Validate swarm configuration"""

    print("[Config] Validating swarm configuration...")

    # Check all agents in workflows exist
    for workflow_type, workflow in WORKFLOW_DEFINITIONS.items():
        for stage in workflow.stages:
            for agent_id in stage.get("required_agents", []):
                if agent_id not in AGENT_DEFINITIONS:
                    raise ValueError(
                        f"Workflow {workflow_type} requires unknown agent {agent_id}"
                    )

    # Check all agents in sectors exist
    for sector_id, sector in SECTOR_CONFIG.items():
        for agent_id in sector.agents:
            if agent_id not in AGENT_DEFINITIONS:
                raise ValueError(
                    f"Sector {sector_id} references unknown agent {agent_id}"
                )

    print(f"[Config] ✓ Valid: {len(AGENT_DEFINITIONS)} agents, {len(WORKFLOW_DEFINITIONS)} workflows")


if __name__ == "__main__":
    validate_config()

    print("\nAgent Summary:")
    for agent in get_all_agents():
        print(f"  {agent.agent_id}: {agent.agent_name} ({agent.pod})")
        print(f"    Capabilities: {', '.join(agent.capabilities)}")
        print(f"    Max concurrent: {agent.max_concurrent}")
        print()
