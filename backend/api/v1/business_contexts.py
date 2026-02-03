import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from schemas.business_context_input import BusinessContextInput
from validators.business_context_validator import (
    BusinessContextValidationError,
    business_context_validator,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/business-contexts", tags=["business-contexts"])


class BusinessContextResponse(BaseModel):
    success: bool
    business_context: Optional[Dict[str, Any]] = None
    validation: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


@router.post("", response_model=BusinessContextResponse, status_code=status.HTTP_201_CREATED)
async def create_business_context(
    request: BusinessContextInput, workspace_id: str = Query(..., description="Workspace ID")
):
    try:
        context = request.to_business_context(
            workspace_id=auth_context.workspace_id, user_id=auth_context.user.id
        )
        validated_context, validation_results = (
            business_context_validator.validate_from_dict(context.model_dump())
        )
    except BusinessContextValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": exc.message,
                "errors": exc.errors,
                "warnings": exc.warnings,
            },
        ) from exc
    except Exception as exc:
        logger.error(f"Business context validation failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Business context validation failed",
        ) from exc

    supabase = get_supabase_admin()
    metadata = dict(validated_context.metadata)
    metadata["validation"] = validation_results

    payload = {
        "workspace_id": auth_context.workspace_id,
        "user_id": auth_context.user.id,
        "ucid": validated_context.ucid,
        "identity": validated_context.identity.model_dump(),
        "audience": validated_context.audience.model_dump(),
        "positioning": validated_context.positioning.model_dump(),
        "evidence_ids": validated_context.evidence_ids,
        "noteworthy_insights": validated_context.noteworthy_insights,
        "metadata": metadata,
        "created_at": validated_context.created_at.isoformat(),
        "updated_at": validated_context.updated_at.isoformat(),
    }

    try:
        result = supabase.table("business_contexts").upsert(payload).execute()
    except Exception as exc:
        logger.error(f"Failed to persist business context: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist business context",
        ) from exc

    return BusinessContextResponse(
        success=True,
        business_context=validated_context.model_dump(),
        validation=validation_results,
        message="Business context saved successfully",
    )
