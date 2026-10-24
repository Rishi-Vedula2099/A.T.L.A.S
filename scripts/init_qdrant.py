#!/usr/bin/env python3
"""Idempotently create Qdrant collections listed in collections.json.

Qdrant has no equivalent of Postgres' /docker-entrypoint-initdb.d/, so the
backend runs this at startup. Safe to re-run.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parents[1] / "infrastructure" / "init" / "qdrant" / "collections.json"


def main() -> int:
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.http.exceptions import UnexpectedResponse
    except ImportError:
        print("[init_qdrant] qdrant-client not installed; skipping.", file=sys.stderr)
        return 0

    config = json.loads(CONFIG_PATH.read_text())
    host = os.getenv("QDRANT_HOST", "localhost")
    port = int(os.getenv("QDRANT_PORT", "6333"))
    client = QdrantClient(host=host, port=port, timeout=10)

    for name, spec in config.get("collections", {}).items():
        vectors = spec["vectors"]
        try:
            client.recreate_collection(
                collection_name=name,
                vectors_config=vectors,
                hnsw_config=spec.get("hnsw_config"),
                optimizers_config=spec.get("optimizers_config"),
                on_disk_payload=spec.get("on_disk_payload", False),
            )
            print(f"[init_qdrant] ensured collection '{name}' on {host}:{port}")
        except Exception as e:
            print(f"[init_qdrant] failed for '{name}': {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
