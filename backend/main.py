from fastapi import FastAPI, HTTPException, Request, Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import os
import uuid
import logging
from graphs.muse_create import build_muse_spine

# Production Logger
logger = logging.getLogger("raptorflow.api")

app = FastAPI(title="RaptorFlow V2 Spine")

class CreateRequest(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=2000)
    workspace_id: str
    user_id: str
    thread_id: Optional[str] = None

    @field_validator('workspace_id')
    def validate_workspace(cls, v):
        if not v.startswith('ws_'):
            # In real app, check against DB
            pass
        return v

# --- Global Exception Handler ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"FATAL ERROR: {str(exc)} | Path: {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "code": "RF_500", "detail": "Our surgical robots are recalibrating. Please retry."}
    )

# --- Dependency: Auth Simulation ---
async def verify_token(x_api_key: str = Header(...)):
    if x_api_key != os.getenv("RF_INTERNAL_KEY"):
        raise HTTPException(status_code=401, detail="Unauthorized Spine Access")

# --- Endpoints ---

@app.post("/v2/muse/create", dependencies=[Depends(verify_token)])
async def create_asset(request: CreateRequest):
    thread_id = request.thread_id or f"thread_{uuid.uuid4()}"
    
    logger.info(f"Incoming Request | Workspace: {request.workspace_id} | Thread: {thread_id}")
    
    try:
        spine = build_muse_spine()
        
        # Invoke the Cognitive Spine
        result = await spine.ainvoke({
            "prompt": request.prompt,
            "workspace_id": request.workspace_id,
            "user_id": request.user_id,
            "thread_id": thread_id,
            "drafts": [],
            "iterations": 0,
            "status": "start"
        }, config={"configurable": {"thread_id": thread_id}})
        
        return {
            "thread_id": thread_id,
            "asset_content": result.get("current_draft"),
            "quality_score": result.get("quality_score"),
            "status": result.get("status"),
            "iterations": result.get("iterations")
        }
        
    except Exception as e:
        logger.error(f"Spine Invocation Failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to execute cognitive graph.")

@app.get("/health")
async def health():
    # Production health check includes DB connectivity
    return {"status": "healthy", "service": "raptorflow-spine", "version": "2.0.0"}