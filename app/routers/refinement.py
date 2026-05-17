import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import optional_api_key
from app.schemas.refinement import RefinementRequest, RefinementResponse
from app.services.refinement_service import refinement_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/refine-idea", response_model=RefinementResponse)
async def refine_idea(
    payload: RefinementRequest,
    _api_key: str = Depends(optional_api_key),
) -> RefinementResponse:
    """
    Refine a vague app idea by asking clarifying questions and
    inferring core features, platforms, and category.
    """
    try:
        logger.info("Refinement request: %s", payload.project_idea[:80])
        result = await refinement_service.refine_idea(payload.project_idea)
        logger.info("Refinement completed for: %s", payload.project_idea[:50])
        return result
    except ValueError as exc:
        logger.error("Validation error in refinement: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The AI returned invalid data. Please try again.",
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error in refinement: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again.",
        ) from exc
