import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.models.project import ChatSession, ChatMessage
from app.schemas.chat import ChatRequest, ChatResponse, ChatSummaryResponse
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

MODE_SYSTEM_PROMPTS = {
    "product_manager": (
        "You are an expert Product Manager consultant. Help the user refine their "
        "app idea, define user stories, prioritize features, and create a product roadmap. "
        "Be specific, actionable, and practical. Always return valid JSON."
    ),
    "architect": (
        "You are an expert Software Architect consultant. Help the user design "
        "their system architecture, choose databases, design APIs, and plan infrastructure. "
        "Be technical, detailed, and practical. Always return valid JSON."
    ),
    "investor": (
        "You are an experienced startup investor and pitch coach. Help the user "
        "refine their pitch, understand financials, practice presenting, and identify "
        "what investors would ask. Be direct, realistic, and constructive. Always return valid JSON."
    ),
    "general": (
        "You are a knowledgeable startup consultant who can discuss app development "
        "from both business and technical perspectives. Help the user think through "
        "their idea, ask clarifying questions, and provide balanced advice. "
        "Always return valid JSON.",
    ),
}


class ChatService:
    async def chat(self, request: ChatRequest) -> ChatResponse:
        async with async_session() as session:
            # Get or create session
            session_id = request.session_id
            if not session_id:
                session_id = f"session_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

            # Fetch existing session or create new one
            result = await session.execute(
                select(ChatSession).where(ChatSession.session_id == session_id)
            )
            chat_session = result.scalar_one_or_none()

            if not chat_session:
                chat_session = ChatSession(
                    session_id=session_id,
                    mode=request.mode,
                    project_idea=request.project_idea,
                )
                session.add(chat_session)
                await session.commit()
                await session.refresh(chat_session)

            # Fetch recent history from DB
            msg_result = await session.execute(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.asc())
                .limit(10)
            )
            recent_messages = msg_result.scalars().all()

            # Build conversation context
            mode = request.mode
            system_prompt = MODE_SYSTEM_PROMPTS.get(mode, MODE_SYSTEM_PROMPTS["general"])

            history_context = ""
            if recent_messages:
                history_context = "\n\nPrevious conversation:\n"
                for msg in recent_messages:
                    role = "User" if msg.role == "user" else "Expert"
                    history_context += f"{role}: {msg.content}\n"

            user_prompt = (
                f"{history_context}\n"
                f"User's current message: {request.project_idea}\n\n"
                f"Return JSON:\n"
                f'{{\n'
                f'  "reply": "Your detailed response to the user",\n'
                f'  "session_id": "{session_id}",\n'
                f'  "mode": "{mode}",\n'
                f'  "next_steps": ["suggested action 1", "suggested action 2"]\n'
                f'}}'
            )

            from pydantic import BaseModel

            class _ChatResult(BaseModel):
                reply: str
                session_id: str
                mode: str
                next_steps: list[str]

            result = await gemini_service.structured_call(
                system_instruction=system_prompt,
                user_prompt=user_prompt,
                response_model=_ChatResult,
                cache_type=f"chat_{session_id}",
            )

            # Save user message and assistant response to DB
            user_msg = ChatMessage(session_id=session_id, role="user", content=request.project_idea)
            assistant_msg = ChatMessage(session_id=session_id, role="assistant", content=result.reply)
            session.add(user_msg)
            session.add(assistant_msg)
            await session.commit()

            return ChatResponse(
                reply=result.reply,
                session_id=session_id,
                mode=mode,
                next_steps=result.next_steps,
            )

    async def summarize_session(self, session_id: str) -> ChatSummaryResponse:
        async with async_session() as session:
            # Fetch all messages for the session
            result = await session.execute(
                select(ChatMessage)
                .where(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.asc())
            )
            messages = result.scalars().all()

            if not messages:
                return ChatSummaryResponse(
                    session_id=session_id,
                    summary="No conversation found for this session.",
                    key_points=[],
                    action_items=[],
                )

            conversation = "\n".join(
                f"{'User' if m.role == 'user' else 'Expert'}: {m.content}"
                for m in messages
            )

            system_prompt = (
                "You are a meeting summarizer. Summarize the conversation, "
                "extract key points, and identify action items. "
                "Always return valid JSON."
            )
            user_prompt = (
                f"Summarize this conversation:\n\n{conversation}\n\n"
                f"Return JSON:\n"
                f'{{\n'
                f'  "summary": "Brief summary",\n'
                f'  "key_points": ["point1", "point2"],\n'
                f'  "action_items": ["action1", "action2"]\n'
                f'}}'
            )

            from pydantic import BaseModel

            class _SummaryResult(BaseModel):
                summary: str
                key_points: list[str]
                action_items: list[str]

            result = await gemini_service.structured_call(
                system_instruction=system_prompt,
                user_prompt=user_prompt,
                response_model=_SummaryResult,
                cache_type=f"summary_{session_id}",
            )

            return ChatSummaryResponse(
                session_id=session_id,
                summary=result.summary,
                key_points=result.key_points,
                action_items=result.action_items,
            )


chat_service = ChatService()
