"""
Agents Domain - Models
AI agent execution models
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    """Agent execution status"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentType(str, Enum):
    """Agent types"""

    ICP_ARCHITECT = "icp_architect"
    STRATEGIST = "strategist"
    RESEARCHER = "researcher"
    COPYWRITER = "copywriter"
    ANALYST = "analyst"


class AgentTask(BaseModel):
    """Agent task/execution"""

    id: str = Field(default_factory=lambda: str(uuid4()))
    workspace_id: str
    agent_type: AgentType
    status: AgentStatus = AgentStatus.PENDING
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class AgentResult(BaseModel):
    """Agent execution result"""

    task_id: str
    status: AgentStatus
    output: Dict[str, Any]
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None
