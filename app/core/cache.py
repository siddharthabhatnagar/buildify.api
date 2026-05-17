import hashlib
import json
import logging
from typing import Any

from cachetools import TTLCache

from app.core.config import settings

logger = logging.getLogger(__name__)

# In-memory LRU cache with TTL
_cache: TTLCache = TTLCache(maxsize=512, ttl=settings.cache_ttl_seconds)


def _make_key(project_idea: str, currency: str, analysis_type: str) -> str:
    """Create a deterministic cache key from inputs."""
    raw = f"{analysis_type}:{currency}:{project_idea.strip().lower()}"
    return hashlib.sha256(raw.encode()).hexdigest()


def get_cached(key: str) -> dict[str, Any] | None:
    """Retrieve a cached result, or None if not found / expired."""
    result = _cache.get(key)
    if result is not None:
        logger.info("Cache HIT for key=%s", key[:12])
    return result


def set_cached(key: str, value: dict[str, Any]) -> None:
    """Store a result in cache."""
    _cache[key] = value
    logger.info("Cache SET for key=%s", key[:12])


def make_cache_key(project_idea: str, currency: str, analysis_type: str) -> str:
    """Public helper to create cache key."""
    return _make_key(project_idea, currency, analysis_type)
