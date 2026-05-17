from pydantic import BaseModel, Field


class RefinementQuestion(BaseModel):
    question: str = Field(..., description="A clarifying question about the project.")
    purpose: str = Field(..., description="Why this question matters for the estimate.")


class RefinementRequest(BaseModel):
    project_idea: str = Field(
        ...,
        min_length=15,
        max_length=2000,
        description="The user's raw project idea to be refined.",
    )


class RefinementResponse(BaseModel):
    clarified_idea: str = Field(
        ..., description="The project idea after refinement through Q&A."
    )
    questions_asked: list[RefinementQuestion] = Field(
        ..., description="The clarifying questions that were generated."
    )
    suggested_features: list[str] = Field(
        ..., description="Core features inferred from the idea."
    )
    platform_suggestions: list[str] = Field(
        ..., description="Recommended platforms (iOS, Android, Web, etc.)."
    )
    idea_category: str = Field(
        ..., description="Category of the app (e.g., E-commerce, Social, SaaS)."
    )
