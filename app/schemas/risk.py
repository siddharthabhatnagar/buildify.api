from pydantic import BaseModel, Field


class RiskRequest(BaseModel):
    project_idea: str = Field(..., min_length=15, max_length=2000)


class RiskAssessment(BaseModel):
    technical_feasibility: int = Field(
        ..., ge=1, le=10, description="Technical feasibility score (1=hard, 10=easy)."
    )
    market_risk: int = Field(
        ..., ge=1, le=10, description="Market risk score (1=risky, 10=safe)."
    )
    cost_risk: int = Field(
        ..., ge=1, le=10, description="Cost risk score (1=likely overrun, 10=well-estimated)."
    )
    timeline_risk: int = Field(
        ..., ge=1, le=10, description="Timeline risk score (1=likely delay, 10=on-schedule)."
    )
    overall_score: int = Field(
        ..., ge=1, le=100, description="Overall feasibility score (1=very risky, 100=very safe)."
    )
    red_flags: list[str] = Field(
        ..., description="Specific risks that could derail the project."
    )
    mitigations: list[str] = Field(
        ..., description="Suggested mitigations for identified risks."
    )
    verdict: str = Field(
        ..., description="One-sentence go/no-go recommendation."
    )


class RiskResponse(BaseModel):
    risk_assessment: RiskAssessment
    detailed_analysis: str = Field(
        ..., description="In-depth explanation of the risk assessment."
    )
