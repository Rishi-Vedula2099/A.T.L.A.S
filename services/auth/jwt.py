"""JWT token utilities for A.T.L.A.S.

Issues and verifies HS256 access + refresh tokens. Secrets and TTLs are read
from environment; see `.env.example` for the full list.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

_ALG = os.getenv("JWT_ALGORITHM", "HS256")
_ACCESS_TTL = timedelta(minutes=int(os.getenv("JWT_ACCESS_TTL_MINUTES", "15")))
_REFRESH_TTL = timedelta(days=int(os.getenv("JWT_REFRESH_TTL_DAYS", "7")))


def _access_secret() -> str:
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise RuntimeError(
            "JWT_SECRET is not set. Run the installer or scripts/generate_env.py."
        )
    return secret


def _refresh_secret() -> str:
    secret = os.getenv("JWT_REFRESH_SECRET")
    if not secret:
        raise RuntimeError(
            "JWT_REFRESH_SECRET is not set. Run the installer or scripts/generate_env.py."
        )
    return secret


def create_access_token(sub: str, claims: dict[str, Any] | None = None) -> str:
    """Short-lived access token. `sub` is the user id."""
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": sub,
        "iat": now,
        "exp": now + _ACCESS_TTL,
        "type": "access",
        "jti": uuid.uuid4().hex,
    }
    if claims:
        payload.update(claims)
    return jwt.encode(payload, _access_secret(), algorithm=_ALG)


def create_refresh_token(sub: str) -> str:
    """Long-lived refresh token. Only identifies the user."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "iat": now,
        "exp": now + _REFRESH_TTL,
        "type": "refresh",
        "jti": uuid.uuid4().hex,
    }
    return jwt.encode(payload, _refresh_secret(), algorithm=_ALG)


class TokenError(Exception):
    """Raised when a token is missing, malformed, expired, or wrong type."""


def decode_access_token(token: str) -> dict[str, Any]:
    """Verify an access token and return its claims."""
    try:
        claims = jwt.decode(token, _access_secret(), algorithms=[_ALG])
    except JWTError as e:
        raise TokenError(f"invalid access token: {e}") from e
    if claims.get("type") != "access":
        raise TokenError("expected access token")
    return claims


def decode_refresh_token(token: str) -> dict[str, Any]:
    """Verify a refresh token and return its claims."""
    try:
        claims = jwt.decode(token, _refresh_secret(), algorithms=[_ALG])
    except JWTError as e:
        raise TokenError(f"invalid refresh token: {e}") from e
    if claims.get("type") != "refresh":
        raise TokenError("expected refresh token")
    return claims
