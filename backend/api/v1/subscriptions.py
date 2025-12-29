from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel

from core.auth import get_current_user, require_workspace_owner
from services.payment_service import payment_service

router = APIRouter(prefix="/v1/subscriptions", tags=["Subscriptions"])


class SubscriptionCancelRequest(BaseModel):
    cancellation_reason: str = None


@router.get("")
async def get_subscription(
    current_user: dict = Depends(get_current_user),
    workspace_id: str = Depends(require_workspace_owner),
):
    """Get current subscription details and usage quotas for the workspace."""
    try:
        result = await payment_service.get_subscription_details(workspace_id)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get subscription details: {str(e)}"
        )


@router.get("/status")
async def get_subscription_status(
    current_user: dict = Depends(get_current_user),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
):
    """Get subscription details for the current workspace (non-owner access)."""
    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Workspace ID required.",
        )

    try:
        result = await payment_service.get_subscription_details(x_tenant_id)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get subscription details: {str(e)}"
        )


@router.put("/cancel")
async def cancel_subscription(
    payload: SubscriptionCancelRequest,
    current_user: dict = Depends(get_current_user),
    workspace_id: str = Depends(require_workspace_owner),
):
    """Cancel or downgrade the subscription."""
    try:
        result = await payment_service.cancel_subscription(
            workspace_id=workspace_id, cancellation_reason=payload.cancellation_reason
        )
        return {"status": "success", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to cancel subscription: {str(e)}"
        )
