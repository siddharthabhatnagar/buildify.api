import logging

from app.schemas.competitor import CompetitorResponse
from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a market research analyst specializing in the mobile app and software industry. "
    "You identify competitors, analyze their strengths and weaknesses, "
    "and find market gaps that new entrants can exploit. "
    "Always return valid JSON matching the requested schema. "
    "Do not include markdown or text outside the JSON."
)


class CompetitorService:
    async def analyze_competitors(self, project_idea: str) -> CompetitorResponse:
        user_prompt = (
            f"Find and analyze competitors for this app idea:\n\n"
            f'"{project_idea}"\n\n'
            f"Identify 3-5 major competitors, their features, weaknesses, and pricing. "
            f"Find market gaps the user can exploit.\n\n"
            f"Return JSON:\n"
            f'{{\n'
            f'  "competitors": [\n'
            f'    {{\n'
            f'      "name": "App Name",\n'
            f'      "url": "play store or website URL",\n'
            f'      "estimated_downloads": "1M-5M",\n'
            f'      "rating": 4.5,\n'
            f'      "key_features": ["feature1", ...],\n'
            f'      "weaknesses": ["weakness1", ...],\n'
            f'      "pricing_model": "Freemium, Subscription, etc."\n'
            f'    }}\n'
            f'  ],\n'
            f'  "market_gap": "Description of the market gap",\n'
            f'  "differentiator_suggestion": "How to stand out",\n'
            f'  "market_saturation": "Low | Medium | High"\n'
            f'}}'
        )

        return await gemini_service.structured_call(
            system_instruction=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=CompetitorResponse,
            cache_type="competitor",
        )


competitor_service = CompetitorService()
