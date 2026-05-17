import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import optional_api_key
from app.schemas.chat import ChatRequest, ChatResponse, ChatSummaryRequest, ChatSummaryResponse
from app.services.chat_service import chat_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_expert(
    payload: ChatRequest,
    _api_key: str = Depends(optional_api_key),
) -> ChatResponse:
    """
    Chat with an AI expert. Supports modes: product_manager, architect, investor, general.
    Sessions are maintained for conversation continuity.
    """
    try:
        logger.info("Chat request (mode=%s): %s", payload.mode, payload.project_idea[:80])
        result = await chat_service.chat(payload)
        logger.info("Chat response sent for session %s", result.session_id)
        return result
    except Exception as exc:
        logger.error("Chat error: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during chat. Please try again.",
        ) from exc


@router.post("/chat/summary", response_model=ChatSummaryResponse)
async def summarize_chat(
    payload: ChatSummaryRequest,
    _api_key: str = Depends(optional_api_key),
) -> ChatSummaryResponse:
    """
    Summarize a chat session and extract key points and action items.
    """
    try:
        logger.info("Summary request for session: %s", payload.session_id)
        result = await chat_service.summarize_session(payload.session_id)
        return result
    except Exception as exc:
        logger.error("Summary error: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred. Please try again.",
        ) from exc
