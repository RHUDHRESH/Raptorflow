# COMPLETE API SPECIFICATION

---

## API Overview

Base URL: `https://api.raptorflow.com/api/v1`

Authentication: Bearer token (JWT)

---

## Agent Endpoints

```python
# backend/api/v1/agents.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import asyncio

from core.config import get_settings
from api.deps import get_current_user, get_db_session
from agents.queen_router import queen_router, ExecutionPlan
from agents.swarm_node import SwarmNode, ExecutionResult
from economics.budget_enforcer import budget_enforcer
from economics.cost_predictor import cost_predictor

router = APIRouter()


class ExecuteRequest(BaseModel):
    """Request to execute an agent task."""
    request: str  # Natural language request
    context: Optional[Dict[str, Any]] = None
    skip_approval: bool = False
    stream: bool = False


class ExecuteResponse(BaseModel):
    """Response from agent execution."""
    execution_id: str
    plan: ExecutionPlan
    result: Optional[ExecutionResult] = None
    requires_approval: bool = False


@router.post("/execute", response_model=ExecuteResponse)
async def execute_agent(
    request: ExecuteRequest,
    background_tasks: BackgroundTasks,
    user = Depends(get_current_user)
):
    """
    Execute an agent task.

    Flow:
    1. Queen routes the request
    2. Cost is estimated
    3. If approval needed, return plan
    4. Otherwise, execute and return result
    """
    # Step 1: Route the request
    plan = await queen_router.route(
        user_id=user.id,
        request=request.request,
        context=request.context
    )

    # Step 2: Check budget
    budget_check = await budget_enforcer.check_budget(
        user_id=user.id,
        estimated_cost=plan.total_estimated_cost
    )

    if not budget_check["can_afford"]:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "INSUFFICIENT_BUDGET",
                "message": f"Estimated cost ${plan.total_estimated_cost:.4f} exceeds remaining budget ${budget_check['remaining_budget']:.4f}",
                "remaining_budget": budget_check["remaining_budget"]
            }
        )

    # Step 3: Check if approval needed
    if plan.requires_approval and not request.skip_approval:
        return ExecuteResponse(
            execution_id="",
            plan=plan,
            requires_approval=True
        )

    # Step 4: Execute
    results = []
    for step in plan.steps:
        node = SwarmNode(
            skill_id=step.skill_id,
            user_id=user.id
        )

        result = await node.execute(
            inputs=step.inputs,
            model_client=model_client  # Injected
        )
        results.append(result)

    return ExecuteResponse(
        execution_id=results[0].execution_id if results else "",
        plan=plan,
        result=results[0] if len(results) == 1 else None,
        requires_approval=False
    )


@router.post("/execute/stream")
async def execute_agent_stream(
    request: ExecuteRequest,
    user = Depends(get_current_user)
):
    """
    Execute with streaming response.
    Returns Server-Sent Events (SSE) for real-time updates.
    """
    async def generate():
        # Route
        plan = await queen_router.route(
            user_id=user.id,
            request=request.request,
            context=request.context
        )

        yield f"data: {{'type': 'plan', 'data': {plan.model_dump_json()}}}\n\n"

        # Execute with streaming
        for step in plan.steps:
            node = SwarmNode(skill_id=step.skill_id, user_id=user.id)

            async for chunk in node.execute_streaming(
                inputs=step.inputs,
                model_client=model_client
            ):
                yield f"data: {json.dumps(chunk)}\n\n"

        yield "data: {\"type\": \"done\"}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )


@router.post("/approve/{plan_id}")
async def approve_plan(
    plan_id: str,
    user = Depends(get_current_user)
):
    """Approve a pending execution plan."""
    # Implementation
    pass


@router.get("/executions")
async def list_executions(
    limit: int = 20,
    offset: int = 0,
    status: Optional[str] = None,
    user = Depends(get_current_user)
):
    """List user's past executions."""
    pass


@router.get("/executions/{execution_id}")
async def get_execution(
    execution_id: str,
    user = Depends(get_current_user)
):
    """Get details of a specific execution."""
    pass


import json
```

---

## Skills Endpoints

```python
# backend/api/v1/skills.py
from fastapi import APIRouter, Depends
from typing import List, Optional

from skills.registry import skill_registry
from api.deps import get_current_user

router = APIRouter()


@router.get("/")
async def list_skills(
    category: Optional[str] = None,
    tag: Optional[str] = None,
    user = Depends(get_current_user)
):
    """List all available skills."""
    if category:
        skills = skill_registry.get_skills_by_category(category)
    elif tag:
        skills = skill_registry.get_skills_by_tag(tag)
    else:
        skills = list(skill_registry.skills.values())

    return {
        "skills": [
            {
                "skill_id": s.config.skill_id,
                "name": s.config.name,
                "description": s.config.description,
                "category": s.config.category,
                "tags": s.config.tags,
                "version": s.config.version,
                "estimated_cost": s.config.max_cost
            }
            for s in skills
        ]
    }


@router.get("/{skill_id}")
async def get_skill(
    skill_id: str,
    user = Depends(get_current_user)
):
    """Get details of a specific skill."""
    skill = skill_registry.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    return {
        "skill_id": skill.config.skill_id,
        "name": skill.config.name,
        "description": skill.config.description,
        "category": skill.config.category,
        "tags": skill.config.tags,
        "version": skill.config.version,
        "input_schema": skill.config.input_schema,
        "output_schema": skill.config.output_schema,
        "tools": skill.config.required_tools + skill.config.optional_tools,
        "limits": {
            "max_cost": skill.config.max_cost,
            "timeout_seconds": skill.config.timeout_seconds
        }
    }


@router.post("/{skill_id}/estimate")
async def estimate_skill_cost(
    skill_id: str,
    inputs: dict,
    user = Depends(get_current_user)
):
    """Estimate cost for executing a skill."""
    from economics.cost_predictor import cost_predictor

    estimate = await cost_predictor.predict(skill_id, inputs)

    return {
        "skill_id": skill_id,
        **estimate
    }


from fastapi import HTTPException
```

---

## Campaign Endpoints

```python
# backend/api/v1/campaigns.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

from api.deps import get_current_user, get_db_session
from products.campaigns.campaign_planner import campaign_planner

router = APIRouter()


class CreateCampaignRequest(BaseModel):
    name: str
    type: str  # product_launch, diwali, eofy, leadgen, awareness
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    target_icp_ids: List[str] = []
    focus_areas: List[str] = []
    risk_level: int = 5


class GenerateStrategyRequest(BaseModel):
    campaign_id: str
    additional_context: Optional[str] = None


@router.post("/")
async def create_campaign(
    request: CreateCampaignRequest,
    user = Depends(get_current_user),
    db = Depends(get_db_session)
):
    """Create a new campaign."""
    campaign = await campaign_planner.create(
        user_id=user.id,
        **request.model_dump()
    )
    return campaign


@router.get("/")
async def list_campaigns(
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    user = Depends(get_current_user)
):
    """List user's campaigns."""
    pass


@router.get("/{campaign_id}")
async def get_campaign(
    campaign_id: str,
    user = Depends(get_current_user)
):
    """Get campaign details."""
    pass


@router.post("/{campaign_id}/generate-strategy")
async def generate_campaign_strategy(
    campaign_id: str,
    request: GenerateStrategyRequest,
    user = Depends(get_current_user)
):
    """Generate AI strategy for a campaign."""
    strategy = await campaign_planner.generate_strategy(
        campaign_id=campaign_id,
        user_id=user.id,
        additional_context=request.additional_context
    )
    return {"strategy": strategy}


@router.post("/{campaign_id}/generate-moves")
async def generate_campaign_moves(
    campaign_id: str,
    user = Depends(get_current_user)
):
    """Generate executable moves for a campaign."""
    moves = await campaign_planner.generate_moves(
        campaign_id=campaign_id,
        user_id=user.id
    )
    return {"moves": moves}


@router.get("/recommendations")
async def get_campaign_recommendations(
    days_ahead: int = 90,
    user = Depends(get_current_user)
):
    """Get campaign recommendations based on festivals/events."""
    from indian_market.festival_calendar import festival_calendar
    from memory.foundation_store import foundation_store

    foundation = await foundation_store.get_foundation(user.id)
    industry = foundation.get("industry", "").lower()

    recommendations = festival_calendar.get_campaign_recommendations(
        industry=industry,
        days_ahead=days_ahead
    )

    return {"recommendations": recommendations}
```

---

## Foundation Endpoints

```python
# backend/api/v1/foundation.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from api.deps import get_current_user
from memory.foundation_store import foundation_store

router = APIRouter()


class UpdateFoundationRequest(BaseModel):
    company_name: Optional[str] = None
    business_description: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    positioning: Optional[str] = None
    unique_value_proposition: Optional[str] = None
    brand_voice: Optional[str] = None
    competitors: Optional[List[Dict[str, str]]] = None


@router.get("/")
async def get_foundation(user = Depends(get_current_user)):
    """Get user's Foundation data."""
    foundation = await foundation_store.get_foundation(user.id)
    return foundation


@router.put("/")
async def update_foundation(
    request: UpdateFoundationRequest,
    user = Depends(get_current_user)
):
    """Update Foundation data."""
    updates = {k: v for k, v in request.model_dump().items() if v is not None}
    await foundation_store.update_foundation(user.id, updates)
    return {"success": True}


@router.get("/summary")
async def get_foundation_summary(user = Depends(get_current_user)):
    """Get compressed Foundation summary."""
    summary = await foundation_store.get_foundation_summary(user.id)
    return {"summary": summary}


@router.get("/icps")
async def get_icps(user = Depends(get_current_user)):
    """Get all ICPs."""
    icps = await foundation_store.get_icps(user.id)
    return {"icps": [icp.model_dump() for icp in icps]}


@router.post("/icps")
async def create_icp(
    icp_data: Dict[str, Any],
    user = Depends(get_current_user)
):
    """Create a new ICP."""
    # Check ICP limit based on subscription
    existing_icps = await foundation_store.get_icps(user.id)

    icp_limits = {
        "free": 1,
        "starter": 3,
        "growth": 5,
        "agency": 10,
        "enterprise": 999
    }

    max_icps = icp_limits.get(user.subscription_tier, 3)

    if len(existing_icps) >= max_icps:
        raise HTTPException(
            status_code=403,
            detail=f"ICP limit reached ({max_icps}). Upgrade to add more."
        )

    # Create ICP
    # Implementation...
    pass
```

---

## Billing Endpoints

```python
# backend/api/v1/billing.py
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

from api.deps import get_current_user
from indian_market.phonepe_gateway import phonepe_gateway, PaymentRequest
from indian_market.gst_service import gst_service
from economics.budget_enforcer import budget_enforcer

router = APIRouter()


class InitiatePaymentRequest(BaseModel):
    plan_id: str  # starter, growth, agency
    billing_cycle: str = "monthly"  # monthly, yearly


class SubscriptionPlan(BaseModel):
    id: str
    name: str
    price_monthly: float
    price_yearly: float
    features: list


PLANS = {
    "starter": SubscriptionPlan(
        id="starter",
        name="Starter",
        price_monthly=2999,
        price_yearly=29990,
        features=["3 ICPs", "100 Moves/month", "Email support"]
    ),
    "growth": SubscriptionPlan(
        id="growth",
        name="Growth",
        price_monthly=9999,
        price_yearly=99990,
        features=["5 ICPs", "500 Moves/month", "Priority support", "Campaign templates"]
    ),
    "agency": SubscriptionPlan(
        id="agency",
        name="Agency",
        price_monthly=24999,
        price_yearly=249990,
        features=["10 ICPs", "Unlimited Moves", "White-label reports", "API access"]
    )
}


@router.get("/plans")
async def get_plans():
    """Get available subscription plans."""
    return {"plans": [p.model_dump() for p in PLANS.values()]}


@router.post("/initiate-payment")
async def initiate_payment(
    request: InitiatePaymentRequest,
    user = Depends(get_current_user)
):
    """Initiate a payment for subscription."""
    plan = PLANS.get(request.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    amount = plan.price_monthly if request.billing_cycle == "monthly" else plan.price_yearly

    # Calculate GST
    gst = gst_service.calculate_gst(
        amount=amount,
        seller_state="Karnataka",
        buyer_state=user.state or "Maharashtra"
    )

    # Initiate PhonePe payment
    payment_result = await phonepe_gateway.initiate_payment(
        PaymentRequest(
            user_id=user.id,
            amount=gst["total_amount"],
            plan_id=request.plan_id,
            redirect_url=f"https://app.raptorflow.com/billing/success",
            callback_url=f"https://api.raptorflow.com/webhooks/phonepe/callback"
        )
    )

    return {
        "payment_url": payment_result["redirect_url"],
        "transaction_id": payment_result["transaction_id"],
        "amount": amount,
        "gst": gst["total_gst"],
        "total": gst["total_amount"]
    }


@router.get("/usage")
async def get_usage(user = Depends(get_current_user)):
    """Get current usage and billing info."""
    usage = await budget_enforcer.get_usage_report(user.id)
    return usage


@router.get("/invoices")
async def list_invoices(
    limit: int = 10,
    user = Depends(get_current_user)
):
    """List user's invoices."""
    # Implementation
    pass


@router.get("/invoices/{invoice_id}")
async def get_invoice(
    invoice_id: str,
    user = Depends(get_current_user)
):
    """Get specific invoice."""
    pass


@router.get("/invoices/{invoice_id}/pdf")
async def download_invoice_pdf(
    invoice_id: str,
    user = Depends(get_current_user)
):
    """Download invoice as PDF."""
    pass
```

---

## Webhook Endpoints

```python
# backend/api/webhooks/phonepe.py
from fastapi import APIRouter, Request, HTTPException
import logging

from indian_market.phonepe_gateway import phonepe_gateway
from core.database import async_session_maker

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/callback")
async def phonepe_callback(request: Request):
    """
    PhonePe payment callback webhook.
    Called when payment status changes.
    """
    # Get raw body and headers
    body = await request.body()
    x_verify = request.headers.get("X-VERIFY", "")

    # Validate webhook signature
    if not phonepe_gateway.validate_webhook(body.decode(), x_verify):
        logger.warning("Invalid PhonePe webhook signature")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse payload
    import json
    import base64

    data = json.loads(body)
    response_data = json.loads(base64.b64decode(data["response"]))

    merchant_transaction_id = response_data.get("merchantTransactionId")
    status = response_data.get("code")

    logger.info(f"PhonePe callback: {merchant_transaction_id} - {status}")

    # Update payment status in database
    async with async_session_maker() as session:
        if status == "PAYMENT_SUCCESS":
            # Update payment status
            await session.execute(
                """
                UPDATE payments SET status = 'success', completed_at = NOW()
                WHERE merchant_transaction_id = :tx_id
                """,
                {"tx_id": merchant_transaction_id}
            )

            # Activate subscription
            user_id = merchant_transaction_id.split("_")[1]  # RF_{user_id}_{timestamp}
            await session.execute(
                """
                UPDATE users SET
                    subscription_status = 'active',
                    subscription_started_at = NOW()
                WHERE id = :user_id
                """,
                {"user_id": user_id}
            )

            # Generate GST invoice
            from indian_market.gst_service import gst_service
            # Generate invoice...

        elif status == "PAYMENT_ERROR" or status == "PAYMENT_DECLINED":
            await session.execute(
                """
                UPDATE payments SET status = 'failed'
                WHERE merchant_transaction_id = :tx_id
                """,
                {"tx_id": merchant_transaction_id}
            )

        await session.commit()

    return {"status": "ok"}


@router.post("/refund")
async def phonepe_refund_callback(request: Request):
    """PhonePe refund callback."""
    # Similar implementation
    pass
```

---

## Health & Metrics Endpoints

```python
# backend/observability/health.py
from fastapi import APIRouter
from datetime import datetime

from core.database import engine
from core.redis_client import redis_client

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with dependencies."""
    checks = {}

    # Database
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        checks["database"] = {"status": "healthy"}
    except Exception as e:
        checks["database"] = {"status": "unhealthy", "error": str(e)}

    # Redis
    try:
        client = await redis_client.get_client()
        await client.ping()
        checks["redis"] = {"status": "healthy"}
    except Exception as e:
        checks["redis"] = {"status": "unhealthy", "error": str(e)}

    # Skills registry
    from skills.registry import skill_registry
    checks["skills"] = {
        "status": "healthy",
        "count": len(skill_registry.skills)
    }

    overall_healthy = all(c.get("status") == "healthy" for c in checks.values())

    return {
        "status": "healthy" if overall_healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": checks
    }


@router.get("/metrics")
async def get_metrics():
    """Prometheus-compatible metrics endpoint."""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from fastapi.responses import Response

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```
