from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    project_idea: str = Field(
        ..., min_length=5, max_length=5000,
        description="User's message or project context.",
    )
    session_id: str = Field(
        default="", description="Session ID for conversation continuity."
    )
    mode: Literal["product_manager", "architect", "investor", "general"] = Field(
        default="general",
        description="Expert mode: product_manager, architect, investor, or general.",
    )


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"] = Field(..., description="Who sent the message.")
    content: str = Field(..., description="Message text.")


class ChatResponse(BaseModel):
    reply: str = Field(..., description="Expert's response to the user.")
    session_id: str = Field(..., description="Session ID for continuity.")
    mode: str = Field(..., description="Which expert mode responded.")
    next_steps: list[str] = Field(
        default_factory=list,
        description="Suggested next steps based on the conversation.",
    )


class ChatSummaryRequest(BaseModel):
    session_id: str = Field(..., description="Session ID to summarize.")


class ChatSummaryResponse(BaseModel):
    session_id: str
    summary: str = Field(..., description="Summary of the conversation.")
    key_points: list[str] = Field(..., description="Key discussion points.")
    action_items: list[str] = Field(..., description="Actionable next steps from the chat.")
