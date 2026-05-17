from pydantic import BaseModel, Field


class CompetitorRequest(BaseModel):
    project_idea: str = Field(..., min_length=15, max_length=2000)


class Competitor(BaseModel):
    name: str = Field(..., description="Competitor app/product name.")
    url: str = Field(default="", description="Play Store or website URL.")
    estimated_downloads: str = Field(
        ..., description="Estimated download range (e.g. '1M-5M')."
    )
    rating: float = Field(..., ge=0, le=5, description="Average user rating.")
    key_features: list[str] = Field(..., description="Core features of this competitor.")
    weaknesses: list[str] = Field(
        ..., description="Gaps or weaknesses the user can exploit."
    )
    pricing_model: str = Field(
        ..., description="How this competitor makes money."
    )


class CompetitorResponse(BaseModel):
    competitors: list[Competitor] = Field(
        ..., description="List of identified competitors."
    )
    market_gap: str = Field(
        ..., description="Identified market gap the user's idea can fill."
    )
    differentiator_suggestion: str = Field(
        ..., description="Specific way to differentiate from competitors."
    )
    market_saturation: str = Field(
        ..., description="Assessment of market saturation level."
    )
