# backend/routers/lords/eris.py
# RaptorFlow Codex - Eris Lord API Endpoints
# "Order is easy. Chaos is the true test."

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import logging
from datetime import datetime

from backend.agents.council_of_lords.eris import ErisLord
from backend.api.deps import get_current_user, get_current_workspace

logger = logging.getLogger(__name__)

# Get Eris instance (singleton)
eris: Optional[ErisLord] = None

async def get_eris() -> ErisLord:
    """Get or initialize Eris Lord"""
    global eris
    if eris is None:
        eris = ErisLord()
        await eris.initialize()
    return eris

router = APIRouter(prefix="/lords/eris", tags=["Eris Lord"])

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class GenerateChaosRequest(BaseModel):
    """Generate chaos event request"""
    target_domain: str = "market"
    severity: str = "medium" # low, medium, high, critical
    context: Dict[str, Any] = {}

class WargameRequest(BaseModel):
    """Run wargame request"""
    strategy_id: str
    strategy_details: Dict[str, Any]
    num_events: int = 3

class EntropyRequest(BaseModel):
    """Inject entropy request"""
    data: Dict[str, Any]
    noise_level: float = 0.1

# ============================================================================
# CHAOS ENDPOINTS
# ============================================================================

@router.post("/chaos/generate", response_model=Dict[str, Any])
async def generate_chaos(
    request: GenerateChaosRequest,
    current_user: str = Depends(get_current_user),
    # current_workspace: str = Depends(get_current_workspace),
    eris_lord: ErisLord = Depends(get_eris)
):
    """
    Generate a Chaos Event.
    
    Eris uses generative AI to create a plausible but disruptive event
    based on the target domain and severity.
    """
    logger.info(f"🎲 Generating chaos for: {request.target_domain}")
    
    try:
        result = await eris_lord.execute({
            "capability": "generate_chaos_event",
            "target_domain": request.target_domain,
            "severity": request.severity,
            "context": request.context
        })
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Chaos generation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/wargame/run", response_model=Dict[str, Any])
async def run_wargame(
    request: WargameRequest,
    current_user: str = Depends(get_current_user),
    # current_workspace: str = Depends(get_current_workspace),
    eris_lord: ErisLord = Depends(get_eris)
):
    """
    Run a Wargame Simulation.
    
    Simulates a sequence of chaos events against a specific strategy
    and calculates a resilience score.
    """
    logger.info(f"⚔️ Running wargame for strategy: {request.strategy_id}")
    
    try:
        result = await eris_lord.execute({
            "capability": "run_wargame_simulation",
            "strategy_id": request.strategy_id,
            "strategy_details": request.strategy_details,
            "num_events": request.num_events
        })
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Wargame simulation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/entropy/inject", response_model=Dict[str, Any])
async def inject_entropy(
    request: EntropyRequest,
    current_user: str = Depends(get_current_user),
    eris_lord: ErisLord = Depends(get_eris)
):
    """
    Inject Entropy (Noise).
    
    Fuzzes the input data to simulate uncertainty or data corruption.
    """
    logger.info("Injecting entropy")
    
    try:
        result = await eris_lord.execute({
            "capability": "inject_entropy",
            "data": request.data,
            "noise_level": request.noise_level
        })
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Entropy injection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/history", response_model=List[Dict[str, Any]])
async def get_chaos_history(
    current_user: str = Depends(get_current_user),
    eris_lord: ErisLord = Depends(get_eris)
):
    """Get history of generated chaos events."""
    return [event.dict() for event in eris_lord.chaos_history]
