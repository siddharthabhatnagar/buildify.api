import logging

from app.schemas.complexity import ComplexityResponse
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a senior software architect who specializes in complexity analysis. "
    "You break down software projects into their complexity components and score "
    "each dimension objectively. You also provide practical tips to reduce complexity. "
    "Always return valid JSON matching the requested schema. "
    "Do not include markdown or text outside the JSON."
)


class ComplexityService:
    async def analyze_complexity(self, project_idea: str) -> ComplexityResponse:
        user_prompt = (
            f"Analyze the development complexity of this app idea:\n\n"
            f'"{project_idea}"\n\n'
            f"Score each dimension (frontend, backend, database, integrations, devops, security) "
            f"from 1-10. Give an overall complexity score 1-100. "
            f"Identify the top 5 complexity drivers with reduction tips. "
            f"Suggest a simplified version and estimate the dev time multiplier.\n\n"
            f"Return JSON:\n"
            f'{{\n'
            f'  "overall_complexity": 55,\n'
            f'  "complexity_level": "Medium",\n'
            f'  "breakdown": {{\n'
            f'    "frontend": 6,\n'
            f'    "backend": 7,\n'
            f'    "database": 5,\n'
            f'    "integrations": 4,\n'
            f'    "devops": 3,\n'
            f'    "security": 6\n'
            f'  }},\n'
            f'  "top_factors": [\n'
            f'    {{\n'
            f'      "factor": "Real-time sync",\n'
            f'      "score": 8,\n'
            f'      "reason": "Requires WebSocket infrastructure",\n'
            f'      "reduction_tip": "Start with polling instead"\n'
            f'    }}\n'
            f'  ],\n'
            f'  "simplified_version": "Description of a simpler MVP",\n'
            f'  "estimated_dev_time_multiplier": 1.5\n'
            f'}}'
        )

        return await gemini_service.structured_call(
            system_instruction=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=ComplexityResponse,
            cache_type="complexity",
        )


complexity_service = ComplexityService()
