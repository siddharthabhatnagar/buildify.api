from typing import Literal

from pydantic import BaseModel, Field


class TeamRequest(BaseModel):
    project_idea: str = Field(..., min_length=15, max_length=2000)
    currency: str = Field(default="USD", min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")


class TeamMember(BaseModel):
    role: str = Field(..., description="Job title (e.g. Flutter Developer, UI/UX Designer).")
    duration_months: int = Field(..., ge=1, description="How many months this role is needed.")
    employment_type: Literal["Full-time", "Part-time", "Freelance", "Contract"] = Field(
        ..., description="Recommended employment arrangement."
    )
    estimated_monthly_rate: float = Field(
        ..., ge=0, description="Estimated monthly rate for this role."
    )
    skills_required: list[str] = Field(
        ..., description="Key skills needed for this role."
    )
    responsibilities: list[str] = Field(
        ..., description="What this person will be responsible for."
    )


class TeamResponse(BaseModel):
    team: list[TeamMember] = Field(..., min_length=1)
    total_monthly_cost: float = Field(..., ge=0)
    total_project_cost: float = Field(..., ge=0)
    currency: str = Field(..., min_length=3, max_length=3)
    hiring_strategy: str = Field(
        ..., description="Recommended approach to hiring (in-house vs outsource)."
    )
