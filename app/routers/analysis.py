import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.auth import optional_api_key
from app.schemas.full_analysis import FullAnalysisRequest, FullAnalysisResponse
from app.schemas.estimation import EstimateRequest, EstimateResponse
from app.schemas.roadmap import RoadmapResponse
from app.schemas.revenue import RevenueResponse
from app.schemas.competitor import CompetitorResponse
from app.schemas.risk import RiskResponse
from app.schemas.team import TeamResponse
from app.schemas.tech_stack import TechStackResponse
from app.schemas.complexity import ComplexityResponse
from app.schemas.pitch_deck import PitchDeckResponse
from app.services.estimation_service import estimation_service
from app.services.roadmap_service import roadmap_service
from app.services.revenue_service import revenue_service
from app.services.competitor_service import competitor_service
from app.services.risk_service import risk_service
from app.services.team_service import team_service
from app.services.tech_stack_service import tech_stack_service
from app.services.complexity_service import complexity_service
from app.services.pitch_deck_service import pitch_deck_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/full-analysis", response_model=FullAnalysisResponse)
async def full_analysis(
    payload: FullAnalysisRequest,
    request: Request,
    _api_key: str = Depends(optional_api_key),
) -> FullAnalysisResponse:
    """
    Run ALL analyses in parallel: cost estimate, roadmap, revenue,
    competitors, risk, team, and tech stack comparison.
    This is the premium endpoint.
    """
    try:
        logger.info("Full analysis request: %s", payload.project_idea[:80])

        # Run all analyses in parallel using asyncio.gather
        estimate_result, roadmap_result, revenue_result, competitor_result, risk_result, team_result, tech_result = await asyncio.gather(
            estimation_service.estimate_cost(
                EstimateRequest(project_idea=payload.project_idea, currency=payload.currency)
            ),
            roadmap_service.generate_roadmap(payload.project_idea, payload.currency),
            revenue_service.estimate_revenue(payload.project_idea, payload.currency),
            competitor_service.analyze_competitors(payload.project_idea),
            risk_service.assess_risk(payload.project_idea),
            team_service.generate_team(payload.project_idea, payload.currency),
            tech_stack_service.compare_tech(payload.project_idea, payload.currency),
        )

        logger.info("Full analysis completed for: %s", payload.project_idea[:50])

        return FullAnalysisResponse(
            estimate=estimate_result,
            roadmap=roadmap_result,
            revenue=revenue_result,
            competitors=competitor_result,
            risk=risk_result,
            team=team_result,
            tech_stack=tech_result,
        )
    except ValueError as exc:
        logger.error("Validation error in full analysis: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The AI returned data that could not be validated. Please try again.",
        ) from exc
    except Exception as exc:
        logger.error("Unexpected error in full analysis: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during analysis. Please try again.",
        ) from exc


# ── Individual analysis endpoints ──

@router.post("/roadmap", response_model=RoadmapResponse)
async def get_roadmap(
    payload: FullAnalysisRequest,
    _api_key: str = Depends(optional_api_key),
) -> RoadmapResponse:
    try:
        return await roadmap_service.generate_roadmap(payload.project_idea, payload.currency)
    except Exception as exc:
        logger.error("Roadmap error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred. Please try again.") from exc


@router.post("/revenue", response_model=RevenueResponse)
async def get_revenue(
    payload: FullAnalysisRequest,
    _api_key: str = Depends(optional_api_key),
) -> RevenueResponse:
    try:
        return await revenue_service.estimate_revenue(payload.project_idea, payload.currency)
    except Exception as exc:
        logger.error("Revenue error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred. Please try again.") from exc


@router.post("/competitors", response_model=CompetitorResponse)
async def get_competitors(
    payload: FullAnalysisRequest,
    _api_key: str = Depends(optional_api_key),
) -> CompetitorResponse:
    try:
        return await competitor_service.analyze_competitors(payload.project_idea)
    except Exception as exc:
        logger.error("Competitor error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred. Please try again.") from exc


@router.post("/risk", response_model=RiskResponse)
async def get_risk(
    payload: FullAnalysisRequest,
    _api_key: str = Depends(optional_api_key),
) -> RiskResponse:
    try:
        return await risk_service.assess_risk(payload.project_idea)
    except Exception as exc:
        logger.error("Risk error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred. Please try again.") from exc


@router.post("/team", response_model=TeamResponse)
async def get_team(
    payload: FullAnalysisRequest,
    _api_key: str = Depends(optional_api_key),
) -> TeamResponse:
    try:
        return await team_service.generate_team(payload.project_idea, payload.currency)
    except Exception as exc:
        logger.error("Team error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred. Please try again.") from exc


@router.post("/tech-stack", response_model=TechStackResponse)
async def get_tech_stack(
    payload: FullAnalysisRequest,
    _api_key: str = Depends(optional_api_key),
) -> TechStackResponse:
    try:
        return await tech_stack_service.compare_tech(payload.project_idea, payload.currency)
    except Exception as exc:
        logger.error("Tech stack error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred. Please try again.") from exc


@router.post("/complexity", response_model=ComplexityResponse)
async def get_complexity(
    payload: FullAnalysisRequest,
    _api_key: str = Depends(optional_api_key),
) -> ComplexityResponse:
    """
    Visualize and score the development complexity of a project idea.
    Returns per-area scores, top complexity drivers, and reduction tips.
    """
    try:
        return await complexity_service.analyze_complexity(payload.project_idea)
    except Exception as exc:
        logger.error("Complexity error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred. Please try again.") from exc


@router.post("/pitch-deck", response_model=PitchDeckResponse)
async def get_pitch_deck(
    payload: FullAnalysisRequest,
    _api_key: str = Depends(optional_api_key),
) -> PitchDeckResponse:
    """
    Generate an investor pitch deck with slides, speaker notes,
    elevator pitch, key metrics, and funding ask.
    """
    try:
        return await pitch_deck_service.generate_pitch_deck(payload.project_idea, payload.currency)
    except Exception as exc:
        logger.error("Pitch deck error: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred. Please try again.") from exc
