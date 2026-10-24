"""Auth HTTP routes: /auth/signup, /auth/login, /auth/refresh, /auth/verify.

Passwords are hashed with passlib bcrypt. User rows live in the `users` table
(see infrastructure/init/postgres/001_init.sql). Refresh tokens are tracked in
`refresh_tokens` for rotation + revocation.
"""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field

from databases.postgres.connection import PostgresConnection
from services.auth.jwt import (
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from services.auth.middleware import current_user

router = APIRouter()

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


# --- Request / response schemas ---------------------------------------------

class SignupIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class RefreshIn(BaseModel):
    refresh_token: str


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserOut(BaseModel):
    id: str
    email: EmailStr
    display_name: str | None
    role: str


# --- Helpers ----------------------------------------------------------------

def _pg() -> PostgresConnection:
    return PostgresConnection()


def _hash(password: str) -> str:
    return _pwd.hash(password)


def _verify(password: str, hashed: str) -> bool:
    try:
        return _pwd.verify(password, hashed)
    except Exception:
        return False


def _row_to_user(row: dict) -> dict:
    return {
        "id": str(row["id"]),
        "email": row["email"],
        "display_name": row.get("display_name"),
        "role": row.get("role", "user"),
    }


def _store_refresh_token(user_id: str, jti: str) -> None:
    """Track an issued refresh token so it can be revoked."""
    expires_at = datetime.now(timezone.utc) + _refresh_ttl()
    conn = _pg()
    conn.execute_query(
        """
        INSERT INTO refresh_tokens (id, user_id, jti, expires_at, revoked)
        VALUES (%s, %s, %s, %s, FALSE)
        """,
        (str(uuid.uuid4()), user_id, jti, expires_at),
    )


def _refresh_ttl():
    from datetime import timedelta

    return timedelta(days=int(os.getenv("JWT_REFRESH_TTL_DAYS", "7")))


# --- Routes -----------------------------------------------------------------

@router.post("/signup", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def signup(body: SignupIn) -> TokenOut:
    conn = _pg()
    existing = conn.execute_query(
        "SELECT id FROM users WHERE email = %s", (body.email,)
    )
    if existing:
        raise HTTPException(status_code=409, detail="email already registered")

    user_id = str(uuid.uuid4())
    conn.execute_query(
        """
        INSERT INTO users (id, email, password_hash, display_name, role)
        VALUES (%s, %s, %s, %s, 'user')
        """,
        (user_id, body.email, _hash(body.password), body.display_name),
    )

    return _issue_tokens(user_id, roles=["user"])


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn) -> TokenOut:
    conn = _pg()
    rows = conn.execute_query(
        "SELECT id, email, password_hash, role FROM users WHERE email = %s",
        (body.email,),
    )
    if not rows or not _verify(body.password, rows[0]["password_hash"]):
        raise HTTPException(status_code=401, detail="invalid credentials")

    user = rows[0]
    return _issue_tokens(str(user["id"]), roles=[user.get("role", "user")])


@router.post("/refresh", response_model=TokenOut)
def refresh(body: RefreshIn) -> TokenOut:
    try:
        claims = decode_refresh_token(body.refresh_token)
    except TokenError as e:
        raise HTTPException(status_code=401, detail=str(e))

    # Check revocation list.
    conn = _pg()
    rows = conn.execute_query(
        "SELECT revoked FROM refresh_tokens WHERE jti = %s", (claims["jti"],)
    )
    if not rows or rows[0]["revoked"]:
        raise HTTPException(status_code=401, detail="refresh token revoked")

    # Rotate: revoke the old, issue a new pair.
    conn.execute_query(
        "UPDATE refresh_tokens SET revoked = TRUE WHERE jti = %s", (claims["jti"],)
    )
    user_rows = conn.execute_query(
        "SELECT role FROM users WHERE id = %s", (claims["sub"],)
    )
    roles = [user_rows[0]["role"]] if user_rows else ["user"]
    return _issue_tokens(claims["sub"], roles=roles)


@router.get("/verify", response_model=UserOut)
def verify(user: dict = Depends(current_user)) -> UserOut:
    """Traefik forward-auth target: returns 200 + user if token is valid."""
    conn = _pg()
    rows = conn.execute_query(
        "SELECT id, email, display_name, role FROM users WHERE id = %s",
        (user["sub"],),
    )
    if not rows:
        raise HTTPException(status_code=404, detail="user not found")
    return UserOut(**_row_to_user(rows[0]))


@router.get("/me", response_model=UserOut)
def me(user: dict = Depends(current_user)) -> UserOut:
    return verify(user)


# --- Internal ---------------------------------------------------------------

def _issue_tokens(user_id: str, roles: list[str]) -> TokenOut:
    access = create_access_token(user_id, claims={"roles": roles})
    refresh_tok = create_refresh_token(user_id)
    # Decode jti for tracking (no verify needed, we just minted it).
    from jose import jwt as _jwt

    claims = _jwt.get_unverified_claims(refresh_tok)
    _store_refresh_token(user_id, claims["jti"])

    return TokenOut(
        access_token=access,
        refresh_token=refresh_tok,
        expires_in=int(os.getenv("JWT_ACCESS_TTL_MINUTES", "15")) * 60,
    )
