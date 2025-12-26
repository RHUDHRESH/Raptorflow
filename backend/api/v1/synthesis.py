from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core.auth import get_current_user, get_tenant_id
from inference import InferenceProvider
from models.foundation import (
    JTBD,
    AwarenessMatrix,
    MessageHierarchy,
    PrecisionSoundbite,
)

router = APIRouter(prefix="/v1/synthesis", tags=["synthesis"])


class SynthesisRequest(BaseModel):
    jtbd: JTBD
    hierarchy: MessageHierarchy
    awareness: AwarenessMatrix
    proof_points: Optional[List[str]] = []


class SoundbiteResponse(BaseModel):
    soundbites: List[PrecisionSoundbite]


@router.post("/soundbites", response_model=SoundbiteResponse)
async def generate_soundbites(
    request: SynthesisRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    _current_user: dict = Depends(get_current_user),
):
    """
    Generates 7 Precision Soundbites based on the JTBD, Hierarchy, and Awareness Matrix.
    Uses Gemini-2.5-Flash (or higher) via InferenceProvider.
    """

    model = InferenceProvider.get_model("reasoning", temperature=0.7)

    prompt = f"""
    You are a world-class copywriter and marketing strategist.
    Your goal is to generate exactly 7 Precision Soundbites using the 'Precision Soundbite Framework 3.0'.

    CONTEXT:
    - Jobs to Be Done (JTBD):
        - Functional: {request.jtbd.functional_job}
        - Emotional: {request.jtbd.emotional_job}
        - Social: {request.jtbd.social_job}

    - Message Hierarchy:
        - Essence: {request.hierarchy.essence}
        - Core Message: {request.hierarchy.core_message}
        - Pillars: {", ".join(request.hierarchy.pillars)}

    - Awareness Matrix:
        - Unaware: {request.awareness.unaware_strategy}
        - Problem: {request.awareness.problem_aware_strategy}
        - Solution: {request.awareness.solution_aware_strategy}
        - Product: {request.awareness.product_aware_strategy}
        - Most: {request.awareness.most_aware_strategy}

    - Available Proof Points:
        {", ".join(request.proof_points)}

    TASK:
    Generate 7 soundbites, one for each category:
    1. problem_revelation: Hook the unaware/problem-aware with specific pain.
    2. agitation: Amplify the pain and emotional consequence.
    3. mechanism: Explain the unique differentiated solution.
    4. objection_handling: Address a core skepticism with proof/logic.
    5. transformation: Paint the 'after' state with a timeframe.
    6. positioning: Status-based positioning (who uses you/elite group).
    7. urgency: Irresistible offer with real scarcity.

    REQUIREMENTS:
    - Return JSON array of objects with "type" and "content".
    - "content" should be high-impact, editorial-grade copy.
    - Follow 'Quiet Luxury' style: Calm, Surgical, Confident.
    """

    try:
        # Use structured output if available, or parse JSON
        response = await model.ainvoke(prompt)
        # Simple extraction for now, can be hardened with pydantic output parser
        import json
        import re

        content = response.content
        match = re.search(r"\[.*\]", content, re.DOTALL)
        if not match:
            raise ValueError("No JSON array found in response")

        soundbites_raw = json.loads(match.group(0))

        results = []
        for sb in soundbites_raw:
            results.append(
                PrecisionSoundbite(
                    workspace_id=tenant_id,
                    type=sb["type"],
                    content=sb["content"],
                    status="draft",
                )
            )

        return SoundbiteResponse(soundbites=results)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")
