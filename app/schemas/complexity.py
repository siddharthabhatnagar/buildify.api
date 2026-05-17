from pydantic import BaseModel, Field


class ComplexityRequest(BaseModel):
    project_idea: str = Field(
        ..., min_length=15, max_length=2000,
        description="The project idea to visualize complexity for.",
    )


class ComplexityFactor(BaseModel):
    factor: str = Field(..., description="Name of the complexity factor.")
    score: int = Field(..., ge=1, le=10, description="Complexity score 1-10 (10=most complex).")
    reason: str = Field(..., description="Why this factor contributes to complexity.")
    reduction_tip: str = Field(..., description="Tip to reduce this complexity.")


class ComplexityBreakdown(BaseModel):
    frontend: int = Field(..., ge=1, le=10, description="Frontend complexity score.")
    backend: int = Field(..., ge=1, le=10, description="Backend complexity score.")
    database: int = Field(..., ge=1, le=10, description="Database complexity score.")
    integrations: int = Field(..., ge=1, le=10, description="Third-party integrations complexity.")
    devops: int = Field(..., ge=1, le=10, description="DevOps / infrastructure complexity.")
    security: int = Field(..., ge=1, le=10, description="Security & compliance complexity.")


class ComplexityResponse(BaseModel):
    overall_complexity: int = Field(..., ge=1, le=100, description="Overall complexity score (1=simple, 100=extremely complex).")
    complexity_level: str = Field(..., description="Label: Low, Medium, High, Very High.")
    breakdown: ComplexityBreakdown = Field(..., description="Per-area complexity scores.")
    top_factors: list[ComplexityFactor] = Field(..., description="Top 5 complexity drivers.")
    simplified_version: str = Field(..., description="How to simplify the project to reduce complexity.")
    estimated_dev_time_multiplier: float = Field(
        ..., ge=0.5,
        description="Multiplier on baseline dev time (1.0=normal, 2.0=double).",
    )
