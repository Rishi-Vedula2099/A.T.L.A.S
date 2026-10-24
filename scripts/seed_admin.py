#!/usr/bin/env python3
"""Seed (or reset) the bootstrap admin user from env vars.

Uses:
    ATLAS_BOOTSTRAP_ADMIN_EMAIL
    ATLAS_BOOTSTRAP_ADMIN_PASSWORD

Safe to re-run. Idempotent: existing users get their password updated.

Usage:
    python scripts/seed_admin.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from passlib.context import CryptContext  # noqa: E402

from databases.postgres.connection import PostgresConnection  # noqa: E402

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def main() -> int:
    email = os.getenv("ATLAS_BOOTSTRAP_ADMIN_EMAIL")
    password = os.getenv("ATLAS_BOOTSTRAP_ADMIN_PASSWORD")
    if not email or not password:
        print("[seed_admin] ATLAS_BOOTSTRAP_ADMIN_EMAIL / _PASSWORD not set", file=sys.stderr)
        return 1

    hashed = _pwd.hash(password)
    conn = PostgresConnection()
    conn.execute_query(
        """
        INSERT INTO users (email, password_hash, role, display_name)
        VALUES (%s, %s, 'admin', 'ATLAS Admin')
        ON CONFLICT (email) DO UPDATE
            SET password_hash = EXCLUDED.password_hash,
                role          = EXCLUDED.role
        """,
        (email, hashed),
    )
    print(f"[seed_admin] admin ensured: {email}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
