"""FastAPI auth dependencies.

Usage:

    from services.auth.middleware import current_user, optional_user

    @app.get("/me")
    async def me(user: dict = Depends(current_user)):
        return {"user_id": user["sub"]}

`current_user` raises HTTPException(401) when no valid token is present.
`optional_user` returns None instead — used for endpoints that behave
differently for anonymous vs. authenticated callers (e.g. /ws).
"""

from __future__ import annotations

import os
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from services.auth.jwt import TokenError, decode_access_token

_bearer = HTTPBearer(auto_error=False)


def _extract_token(
    creds: HTTPAuthorizationCredentials | None,
    request: Request,
) -> str | None:
    if creds and creds.credentials:
        return creds.credentials
    # Fallback: ?token=... query string (used by WebSocket clients and curl).
    return request.query_params.get("token")


async def current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    request: Request = None,
) -> dict[str, Any]:
    """Resolve the authenticated user from a bearer access token."""
    token = _extract_token(creds, request)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return decode_access_token(token)
    except TokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def optional_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    request: Request = None,
) -> dict[str, Any] | None:
    """Like `current_user`, but anonymous callers get None."""
    token = _extract_token(creds, request)
    if not token:
        return None
    try:
        return decode_access_token(token)
    except TokenError:
        return None


def has_role(*roles: str):
    """Role-based access control dependency factory.

        @app.delete("/users/{id}", dependencies=[Depends(has_role("admin"))])

    Roles come from the JWT `roles` claim (list[str]).
    """

    async def _check(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
        user_roles = set(user.get("roles", []))
        if not user_roles.intersection(roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"requires one of: {', '.join(roles)}",
            )
        return user

    return _check


# Eager sanity check at import time in dev so misconfig is loud.
if os.getenv("ATLAS_ENV") == "development":  # pragma: no cover
    try:
        from services.auth.jwt import _access_secret  # noqa: F401
    except RuntimeError as e:
        print(f"[Auth] {e}")
