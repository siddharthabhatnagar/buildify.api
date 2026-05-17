import json
import logging
from typing import Any, Type, TypeVar

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pydantic import BaseModel, ValidationError

from app.core.config import settings
from app.core.cache import get_cached, set_cached, make_cache_key

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# Retry: up to 3 attempts, exponential backoff (1s, 2s, 4s)
_retry_decorator = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.HTTPStatusError)),
    before_sleep=lambda state: logger.warning(
        "Retrying Gemini call (attempt %d): %s",
        state.attempt_number,
        state.outcome.exception() if state.outcome else "unknown",
    ),
)


class GeminiService:
    """Async Gemini API client with retry, caching, and Pydantic enforcement."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    # ── Core call with retry ──

    @_retry_decorator
    async def _call_gemini(
        self,
        system_instruction: str,
        user_prompt: str,
    ) -> dict[str, Any]:
        """Make an async call to the Gemini API with retry logic."""
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not set.")

        client = await self._get_client()
        api_url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{settings.gemini_model}:generateContent"
        )

        payload = {
            "systemInstruction": {"parts": [{"text": system_instruction}]},
            "contents": [{"parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.3,
            },
        }
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": settings.gemini_api_key,
        }

        logger.info("Calling Gemini API for: %s", user_prompt[:80])
        response = await client.post(api_url, json=payload, headers=headers)
        response.raise_for_status()

        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return self._safe_parse_json(text)

    # ── Structured call with caching + Pydantic validation ──

    async def structured_call(
        self,
        system_instruction: str,
        user_prompt: str,
        response_model: Type[T],
        cache_type: str = "generic",
    ) -> T:
        """
        Call Gemini, cache the result, and validate with Pydantic model.
        Returns an instance of response_model.
        """
        # Check cache
        cache_key = make_cache_key(user_prompt, "", cache_type)
        cached = get_cached(cache_key)
        if cached is not None:
            try:
                return response_model(**cached)
            except (ValidationError, Exception):
                logger.warning("Cached data failed validation, re-fetching.")

        # Call Gemini
        raw = await self._call_gemini(system_instruction, user_prompt)

        # Validate with Pydantic
        try:
            result = response_model(**raw)
        except ValidationError as e:
            logger.error("Gemini returned invalid data for %s: %s", cache_type, e)
            raise ValueError(
                f"Gemini returned data that does not match expected schema for {cache_type}. "
                f"Please try again."
            ) from e

        # Cache the validated dict
        set_cached(cache_key, result.model_dump())

        return result

    # ── JSON parsing ──

    @staticmethod
    def _safe_parse_json(text: str) -> dict[str, Any]:
        """Parse JSON from Gemini response, with brace-extraction fallback."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start == -1 or end == -1:
                raise ValueError("Gemini response did not contain valid JSON.")
            return json.loads(text[start : end + 1])


# ── Singleton ──
gemini_service = GeminiService()
