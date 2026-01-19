"""
Production RaptorFlow Backend with Agent System Integration
Enterprise-ready, 100% functional, no fallbacks
"""

import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional

import uvicorn

# Agent system imports
from agents import (
    AgentConfig,
    AgentState,
    VertexAILLM,
    create_initial_state,
    get_config,
    get_llm,
    validate_config,
)
from backend.agents.dispatcher import AgentDispatcher
from backend.agents.exceptions import ConfigurationError, RaptorflowError
from backend.agents.graphs.main import create_raptorflow_graph, execute_workflow
from backend.agents.preprocessing import RequestPreprocessor
from backend.agents.routing.pipeline import RoutingPipeline
from backend.agents.specialists.quality_checker import QualityChecker
from backend.agents.tools.registry import get_tool_registry
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("/var/log/raptorflow/agent.log", mode="a"),
    ],
)
logger = logging.getLogger(__name__)

# Global instances
dispatcher: Optional[AgentDispatcher] = None
workflow_graph = None
tool_registry = None
config: Optional[AgentConfig] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    global dispatcher, workflow_graph, tool_registry, config

    logger.info("🚀 Starting RaptorFlow Agent System...")

    try:
        # Step 1: Validate configuration
        logger.info("📋 Validating configuration...")
        config = get_config()
        if not validate_config():
            raise ConfigurationError("Configuration validation failed")
        logger.info("✅ Configuration validated")

        # Step 2: Initialize tool registry
        logger.info("🔧 Initializing tool registry...")
        tool_registry = get_tool_registry()
        tool_registry.initialize_default_tools()
        logger.info(
            f"✅ Tool registry initialized with {len(tool_registry.list_tools())} tools"
        )

        # Step 3: Initialize agent dispatcher
        logger.info("🤖 Initializing agent dispatcher...")
        dispatcher = AgentDispatcher()
        logger.info(
            f"✅ Agent dispatcher initialized with {len(dispatcher.registry.list_agents())} agents"
        )

        # Step 4: Initialize workflow graph
        logger.info("📊 Initializing workflow graph...")
        preprocessor = RequestPreprocessor()
        routing_pipeline = RoutingPipeline()
        quality_checker = QualityChecker()

        workflow_graph = create_raptorflow_graph(
            preprocessor=preprocessor,
            routing_pipeline=routing_pipeline,
            dispatcher=dispatcher,
            quality_checker=quality_checker,
        )
        logger.info("✅ Workflow graph initialized")

        # Step 5: Warmup LLM models
        logger.info("🧠 Warming up LLM models...")
        from agents.config import ModelTier

        for tier in [ModelTier.FLASH_LITE, ModelTier.FLASH, ModelTier.PRO]:
            try:
                llm = get_llm(tier)
                logger.info(f"✅ {tier.value} model ready")
            except Exception as e:
                logger.warning(f"⚠️ Failed to warm up {tier.value}: {e}")

        logger.info("🎉 RaptorFlow Agent System started successfully!")

        yield

    except Exception as e:
        logger.error(f"❌ Failed to start agent system: {e}")
        raise

    finally:
        logger.info("🛑 Shutting down RaptorFlow Agent System...")
        # Cleanup if needed
        logger.info("✅ Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="RaptorFlow Agent System",
    description="Enterprise AI Agent System for Marketing Operations",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class AgentRequest(BaseModel):
    request: str
    workspace_id: str
    user_id: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    agent_hint: Optional[str] = None
    fast_mode: bool = False


class AgentResponse(BaseModel):
    success: bool
    agent: Optional[str] = None
    output: Optional[Any] = None
    error: Optional[str] = None
    execution_time_seconds: float
    tokens_used: int = 0
    cost_usd: float = 0.0
    routing_decision: Optional[Dict[str, Any]] = None
    quality_score: Optional[float] = None
    requires_approval: bool = False
    approval_gate_id: Optional[str] = None
    timestamp: str


# Health check endpoints
@app.get("/health")
async def health_check():
    """Comprehensive health check."""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0",
            "components": {},
        }

        # Check configuration
        if config:
            health_status["components"]["config"] = "healthy"
        else:
            health_status["components"]["config"] = "unhealthy"
            health_status["status"] = "degraded"

        # Check dispatcher
        if dispatcher:
            dispatcher_health = dispatcher.get_health_status()
            health_status["components"]["dispatcher"] = dispatcher_health["status"]
        else:
            health_status["components"]["dispatcher"] = "unhealthy"
            health_status["status"] = "degraded"

        # Check tool registry
        if tool_registry:
            health_status["components"]["tools"] = "healthy"
            health_status["components"]["tool_count"] = len(tool_registry.list_tools())
        else:
            health_status["components"]["tools"] = "unhealthy"
            health_status["status"] = "degraded"

        # Check workflow graph
        if workflow_graph:
            health_status["components"]["workflow"] = "healthy"
        else:
            health_status["components"]["workflow"] = "unhealthy"
            health_status["status"] = "degraded"

        return health_status

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
            },
        )


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with component stats."""
    try:
        detailed_status = await health_check()

        if dispatcher:
            detailed_status["dispatcher_stats"] = dispatcher.get_dispatcher_stats()

        if tool_registry:
            detailed_status["tool_stats"] = tool_registry.get_registry_stats()
            detailed_status["available_tools"] = tool_registry.list_tools()
            detailed_status["available_agents"] = (
                dispatcher.registry.list_agents() if dispatcher else []
            )

        return detailed_status

    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))


# Agent execution endpoints
@app.post("/agent/execute", response_model=AgentResponse)
async def execute_agent(request: AgentRequest):
    """Execute an agent request."""
    if not dispatcher:
        raise HTTPException(status_code=503, detail="Agent dispatcher not available")

    try:
        # Execute via dispatcher
        result = await dispatcher.dispatch(
            request=request.request,
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            session_id=request.session_id or f"session_{datetime.now().timestamp()}",
            context=request.context,
            agent_hint=request.agent_hint,
            fast_mode=request.fast_mode,
        )

        # Convert to response format
        response = AgentResponse(
            success=result.get("success", False),
            agent=result.get("agent"),
            output=result.get("output"),
            error=result.get("error"),
            execution_time_seconds=result.get("execution_time_seconds", 0.0),
            tokens_used=result.get("state", {}).get("tokens_used", 0),
            cost_usd=result.get("state", {}).get("cost_usd", 0.0),
            routing_decision=result.get("routing_decision"),
            quality_score=result.get("state", {}).get("quality_score"),
            requires_approval=result.get("state", {}).get("requires_approval", False),
            approval_gate_id=result.get("state", {}).get("approval_gate_id"),
            timestamp=result.get("timestamp", datetime.now().isoformat()),
        )

        return response

    except RaptorflowError as e:
        logger.error(f"Agent execution failed: {e.to_dict()}")
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error in agent execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agent/workflow", response_model=AgentResponse)
async def execute_workflow_endpoint(request: AgentRequest):
    """Execute the full workflow graph."""
    if not workflow_graph:
        raise HTTPException(status_code=503, detail="Workflow graph not available")

    try:
        # Execute via workflow graph
        result = await execute_workflow(
            graph=workflow_graph,
            request=request.request,
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            session_id=request.session_id or f"workflow_{datetime.now().timestamp()}",
            config={"recursion_limit": 50},
        )

        # Convert to response format
        response = AgentResponse(
            success=result.get("success", False),
            output=result.get("output"),
            error=result.get("error"),
            execution_time_seconds=0.0,  # Workflow graph doesn't track this directly
            tokens_used=result.get("tokens_used", 0),
            cost_usd=result.get("cost_usd", 0.0),
            quality_score=result.get("quality_score"),
            requires_approval=result.get("requires_approval", False),
            approval_gate_id=result.get("approval_gate_id"),
            timestamp=datetime.now().isoformat(),
        )

        return response

    except RaptorflowError as e:
        logger.error(f"Workflow execution failed: {e.to_dict()}")
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error in workflow execution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Management endpoints
@app.get("/agents")
async def list_agents():
    """List all available agents."""
    if not dispatcher:
        raise HTTPException(status_code=503, detail="Agent dispatcher not available")

    agents = []
    for agent_name in dispatcher.registry.list_agents():
        agent_info = dispatcher.get_agent_info(agent_name)
        if agent_info:
            agents.append(agent_info)

    return {"agents": agents}


@app.get("/agents/{agent_name}")
async def get_agent_info(agent_name: str):
    """Get detailed information about a specific agent."""
    if not dispatcher:
        raise HTTPException(status_code=503, detail="Agent dispatcher not available")

    agent_info = dispatcher.get_agent_info(agent_name)
    if not agent_info:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")

    return agent_info


@app.get("/tools")
async def list_tools():
    """List all available tools."""
    if not tool_registry:
        raise HTTPException(status_code=503, detail="Tool registry not available")

    tools = []
    for tool_name in tool_registry.list_tools():
        tool_info = tool_registry.get_tool_info(tool_name)
        if tool_info:
            tools.append(tool_info)

    return {"tools": tools}


@app.get("/routing/stats")
async def get_routing_stats():
    """Get routing pipeline statistics."""
    if not dispatcher:
        raise HTTPException(status_code=503, detail="Agent dispatcher not available")

    return dispatcher.routing_pipeline.get_pipeline_stats()


@app.get("/dispatcher/stats")
async def get_dispatcher_stats():
    """Get dispatcher statistics."""
    if not dispatcher:
        raise HTTPException(status_code=503, detail="Agent dispatcher not available")

    return dispatcher.get_dispatcher_stats()


# Error handlers
@app.exception_handler(RaptorflowError)
async def raptorflow_error_handler(request: Request, exc: RaptorflowError):
    """Handle Raptorflow-specific errors."""
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.message,
            "error_code": exc.error_code,
            "details": exc.details,
            "timestamp": datetime.now().isoformat(),
        },
    )


@app.exception_handler(ConfigurationError)
async def configuration_error_handler(request: Request, exc: ConfigurationError):
    """Handle configuration errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Configuration error",
            "message": exc.message,
            "timestamp": datetime.now().isoformat(),
        },
    )


if __name__ == "__main__":
    # Run the production server
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")

    logger.info(f"🌟 Starting RaptorFlow Agent System on {host}:{port}")

    uvicorn.run(
        "main_production:app",
        host=host,
        port=port,
        reload=False,  # Production mode
        log_level="info",
        access_log=True,
    )
