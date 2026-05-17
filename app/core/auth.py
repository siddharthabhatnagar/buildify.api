from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify the API key provided in the X-API-Key header.
    If settings.api_auth_token is empty, authentication is disabled (dev mode).
    Returns the API key string on success.
    """
    # If no auth token configured, skip authentication (development mode)
    if not settings.api_auth_token:
        return api_key or "dev-mode"

    if api_key != settings.api_auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key. Provide X-API-Key header.",
        )

    return api_key


# Optional dependency — raises only if token is configured
async def optional_api_key(api_key: str = Security(api_key_header)) -> str:
    """Non-blocking auth: only enforces if a token is configured."""
    if not settings.api_auth_token:
        return "dev-mode"
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Provide X-API-Key header.",
        )
    if api_key != settings.api_auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )
    return api_key
