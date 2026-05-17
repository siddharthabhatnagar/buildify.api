import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.auth import optional_api_key
from app.schemas.estimation import EstimateRequest, EstimateResponse
from app.services.estimation_service import estimation_service

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/estimate-cost", response_model=EstimateResponse)
@limiter.limit("10/minute")
async def estimate_cost(
    request: Request,
    payload: EstimateRequest,
    _api_key: str = Depends(optional_api_key),
) -> EstimateResponse:
    """
    Generate a detailed cost estimate for a software project idea.
    Uses Gemini AI with Pydantic-enforced structured output.
    Rate limited to 10 requests per minute per IP.
    """
    try:
        logger.info("Estimate request: %s (currency: %s)", payload.project_idea[:80], payload.currency)
        result = await estimation_service.estimate_cost(payload)
        logger.info("Estimate completed successfully for: %s", payload.project_idea[:50])
        return result
    except ValueError as exc:
        logger.error("Validation error in estimation: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The AI returned data that could not be validated. Please try again.",
        ) from exc
    except ConnectionError as exc:
        logger.error("Gemini API connection error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The estimation service is temporarily unavailable. Please try again later.",
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error in estimation: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again.",
        ) from exc
