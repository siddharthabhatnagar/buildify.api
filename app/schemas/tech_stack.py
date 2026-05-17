from pydantic import BaseModel, Field


class TechStackRequest(BaseModel):
    project_idea: str = Field(..., min_length=15, max_length=2000)
    currency: str = Field(default="USD", min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")


class TechOption(BaseModel):
    category: str = Field(
        ..., description="Category (Frontend, Backend, Database, Hosting, Payments, etc.)."
    )


class TechDetail(BaseModel):
    name: str = Field(..., description="Technology name.")
    pros: list[str] = Field(..., description="Advantages of this technology.")
    cons: list[str] = Field(..., description="Disadvantages of this technology.")
    cost_per_month: float = Field(..., ge=0, description="Estimated monthly cost.")
    setup_difficulty: str = Field(
        ..., description="How hard to set up: Easy, Medium, or Hard."
    )
    scalability: str = Field(
        ..., description="Scalability rating: Low, Medium, High."
    )


class TechCategoryComparison(BaseModel):
    category: str
    open_source: TechDetail
    paid: TechDetail


class TechStackResponse(BaseModel):
    comparisons: list[TechCategoryComparison] = Field(
        ..., description="Comparison per technology category."
    )
    recommended_combo: str = Field(
        ..., description="The recommended combination of technologies."
    )
    estimated_savings_vs_paid: float = Field(
        ..., ge=0, description="Monthly savings using open-source vs paid."
    )
    currency: str = Field(..., min_length=3, max_length=3)
