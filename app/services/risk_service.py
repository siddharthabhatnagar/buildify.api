import logging

from app.schemas.risk import RiskResponse
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a risk assessment specialist for software projects. "
    "You evaluate technical feasibility, market risk, cost risk, and timeline risk "
    "for app ideas and provide an overall feasibility score. "
    "Always return valid JSON matching the requested schema. "
    "Do not include markdown or text outside the JSON."
)


class RiskService:
    async def assess_risk(self, project_idea: str) -> RiskResponse:
        user_prompt = (
            f"Assess the risk and feasibility of this app idea:\n\n"
            f'"{project_idea}"\n\n'
            f"Score each dimension 1-10, give an overall score 1-100, "
            f"identify red flags and suggest mitigations.\n\n"
            f"Return JSON:\n"
            f'{{\n'
            f'  "risk_assessment": {{\n'
            f'    "technical_feasibility": 7,\n'
            f'    "market_risk": 5,\n'
            f'    "cost_risk": 6,\n'
            f'    "timeline_risk": 4,\n'
            f'    "overall_score": 65,\n'
            f'    "red_flags": ["flag1", ...],\n'
            f'    "mitigations": ["mitigation1", ...],\n'
            f'    "verdict": "Proceed with caution: ..."\n'
            f'  }},\n'
            f'  "detailed_analysis": "In-depth explanation of the risk assessment"\n'
            f'}}'
        )

        return await gemini_service.structured_call(
            system_instruction=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=RiskResponse,
            cache_type="risk",
        )


risk_service = RiskService()
