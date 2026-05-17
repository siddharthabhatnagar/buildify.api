import logging

from app.schemas.refinement import RefinementResponse
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a senior product manager and business analyst. "
    "Your job is to take a vague app idea and ask clarifying questions "
    "to refine it into a well-defined product specification. "
    "Always return valid JSON matching the requested schema. "
    "Do not include markdown or text outside the JSON."
)


class RefinementService:
    async def refine_idea(self, project_idea: str) -> RefinementResponse:
        user_prompt = (
            f"A user has this app idea:\n\n"
            f'"{project_idea}"\n\n'
            f"Generate a refined version of this idea by:\n"
            f"1. Asking 3-5 clarifying questions that would help estimate the cost\n"
            f"2. Inferring the core features based on the idea\n"
            f"3. Suggesting which platforms make sense\n"
            f"4. Categorizing the app\n\n"
            f"Return JSON:\n"
            f'{{\n'
            f'  "clarified_idea": "A refined, detailed description of the project",\n'
            f'  "questions_asked": [\n'
            f'    {{"question": "...", "purpose": "why this matters"}}\n'
            f'  ],\n'
            f'  "suggested_features": ["feature1", "feature2", ...],\n'
            f'  "platform_suggestions": ["iOS", "Android", "Web", ...],\n'
            f'  "idea_category": "E-commerce | Social | SaaS | etc."\n'
            f'}}'
        )

        return await gemini_service.structured_call(
            system_instruction=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=RefinementResponse,
            cache_type="refinement",
        )


refinement_service = RefinementService()
