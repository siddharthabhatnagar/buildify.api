import logging

from app.schemas.tech_stack import TechStackResponse
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a technology advisor and DevOps consultant. "
    "You compare open-source vs paid technology options across categories "
    "(Frontend, Backend, Database, Hosting, Payments) and recommend the best combo. "
    "Always return valid JSON matching the requested schema. "
    "Do not include markdown or text outside the JSON."
)


class TechStackService:
    async def compare_tech(self, project_idea: str, currency: str) -> TechStackResponse:
        user_prompt = (
            f"Compare technology options for building this app:\n\n"
            f'"{project_idea}"\n\n'
            f"Currency: {currency}\n\n"
            f"For each category, compare an open-source option vs a paid option.\n\n"
            f"Return JSON:\n"
            f'{{\n'
            f'  "comparisons": [\n'
            f'    {{\n'
            f'      "category": "Frontend",\n'
            f'      "open_source": {{\n'
            f'        "name": "React",\n'
            f'        "pros": ["pro1"],\n'
            f'        "cons": ["con1"],\n'
            f'        "cost_per_month": 0,\n'
            f'        "setup_difficulty": "Medium",\n'
            f'        "scalability": "High"\n'
            f'      }},\n'
            f'      "paid": {{\n'
            f'        "name": "Flutter",\n'
            f'        "pros": ["pro1"],\n'
            f'        "cons": ["con1"],\n'
            f'        "cost_per_month": 0,\n'
            f'        "setup_difficulty": "Medium",\n'
            f'        "scalability": "High"\n'
            f'      }}\n'
            f'    }}\n'
            f'  ],\n'
            f'  "recommended_combo": "React + Node.js + PostgreSQL + AWS",\n'
            f'  "estimated_savings_vs_paid": 500,\n'
            f'  "currency": "{currency}"\n'
            f'}}'
        )

        return await gemini_service.structured_call(
            system_instruction=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=TechStackResponse,
            cache_type="tech_stack",
        )


tech_stack_service = TechStackService()
