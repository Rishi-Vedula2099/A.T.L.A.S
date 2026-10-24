#!/usr/bin/env python3
"""
A.T.L.A.S — standalone .env generator.

Thin wrapper around ``installer/lib/secrets.py`` for developers who already
have Docker installed and don't want to run the full installer. Generates a
ready-to-use ``.env`` with cryptographically strong random secrets.

Examples:
    python scripts/generate_env.py                  # writes <repo>/.env
    python scripts/generate_env.py --output ~/.atlas/.env
    python scripts/generate_env.py --force          # rotate ALL secrets
    python scripts/generate_env.py --with-llm-keys  # prompt for OpenAI/... keys
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

# Allow running both from the repo root and from scripts/.
_REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_secrets_module():
    """Load installer/lib/secrets.py as a module without shadowing stdlib `secrets`."""
    secrets_path = _REPO_ROOT / "installer" / "lib" / "secrets.py"
    if not secrets_path.exists():
        print(f"[generate_env] missing dependency: {secrets_path}", file=sys.stderr)
        sys.exit(2)
    spec = importlib.util.spec_from_file_location("atlas_secrets", secrets_path)
    mod = importlib.util.module_from_spec(spec)
    # Need to add to sys.modules before exec so the module can resolve its own imports.
    sys.modules["atlas_secrets"] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    p = argparse.ArgumentParser(
        description="Generate a secure A.T.L.A.S .env file (standalone).",
        epilog="Equivalent to the secret-generation step of ./install.",
    )
    p.add_argument("--output", "-o", type=Path,
                   default=_REPO_ROOT / ".env",
                   help="Output path (default: <repo>/.env)")
    p.add_argument("--force", action="store_true",
                   help="Overwrite an existing file (rotates ALL secrets).")
    p.add_argument("--with-llm-keys", action="store_true",
                   help="Interactively prompt for optional LLM/voice API keys.")
    p.add_argument("--env-file", type=Path, default=None,
                   help="Read optional API keys from an existing .env instead of prompting.")
    args = p.parse_args()

    atlas_secrets = _load_secrets_module()
    out = atlas_secrets.generate_env(
        args.output,
        force=args.force,
        with_llm_prompts=args.with_llm_keys,
        llm_env_file=args.env_file,
    )

    print(f"[generate_env] Wrote {out}")
    print(f"[generate_env] Installer-managed env location: {atlas_secrets.default_env_path()}")
    print("[generate_env] Next steps:")
    print("  docker compose -f infrastructure/docker/docker-compose.yml config   # sanity-check")
    print("  docker compose -f infrastructure/docker/docker-compose.yml up -d    # start stack")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
