#!/usr/bin/env python3
"""
A.T.L.A.S — encrypted backup job.

Dumps every stateful datastore, tar+encrypts the bundle with AES-256-GCM, and
uploads it to MinIO. Old backups are pruned to ``ATLAS_BACKUP_RETENTION``.

Dumps performed:
    - PostgreSQL:  ``pg_dump`` (custom format)
    - Redis:       ``redis-cli --rdb`` (raw RDB snapshot)
    - Neo4j:       ``neo4j-admin database dump`` (full database dump)
    - Qdrant:      snapshot API (one snapshot per collection, downloaded)

Each dump is produced under a fresh staging directory, then the directory is
tarred, encrypted, and pushed. The encrypted object name encodes the timestamp
so listings sort lexically by recency.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:  # pragma: no cover - import guard for doctor/dev runs
    AESGCM = None

try:
    from minio import Minio
    from minio.error import S3Error
except ImportError:  # pragma: no cover
    Minio = None
    S3Error = Exception


# --------------------------------------------------------------------------- #
# Logging
# --------------------------------------------------------------------------- #

def log(msg: str) -> None:
    print(f"[backup] {msg}", flush=True)


def die(msg: str, code: int = 1) -> None:
    print(f"[backup] FATAL: {msg}", file=sys.stderr, flush=True)
    raise SystemExit(code)


# --------------------------------------------------------------------------- #
# Environment
# --------------------------------------------------------------------------- #

def env(key: str, default: str | None = None, required: bool = False) -> str:
    v = os.environ.get(key, default)
    if required and not v:
        die(f"Missing required environment variable: {key}")
    return v or ""


def env_int(key: str, default: int) -> int:
    try:
        return int(os.environ.get(key, str(default)))
    except ValueError:
        return default


# --------------------------------------------------------------------------- #
# Per-DB dumpers
# --------------------------------------------------------------------------- #

def _run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    """Run a command, stream output to the log, raise on non-zero exit."""
    log(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, check=True, **kw)


def dump_postgres(staging: Path) -> None:
    host = env("POSTGRES_HOST", "postgres")
    port = env("POSTGRES_PORT", "5432")
    user = env("POSTGRES_USER", "atlas_admin")
    db = env("POSTGRES_DB", "atlas_db")
    password = env("POSTGRES_PASSWORD", required=True)

    env_ = {**os.environ, "PGPASSWORD": password}
    out = staging / "postgres.dump"
    cmd = [
        "pg_dump",
        f"--host={host}", f"--port={port}",
        f"--username={user}",
        "--format=custom", "--no-owner", "--no-privileges",
        f"--file={out}",
        db,
    ]
    try:
        _run(cmd, env=env_)
        log(f"postgres dumped -> {out.name}")
    except FileNotFoundError:
        die("pg_dump not found on PATH. Install postgresql-client in the image.")
    except subprocess.CalledProcessError as e:
        die(f"pg_dump failed with exit code {e.returncode}")


def dump_redis(staging: Path) -> None:
    host = env("REDIS_HOST", "redis")
    port = env("REDIS_PORT", "6379")
    password = env("REDIS_PASSWORD", "")
    out = staging / "redis.rdb"

    cmd = ["redis-cli", "-h", host, "-p", port]
    if password:
        cmd += ["-a", password, "--no-auth-warning"]
    cmd += ["--rdb", str(out)]

    try:
        _run(cmd)
        if not out.exists() or out.stat().st_size == 0:
            log("redis RDB is empty (server may have no keys) - keeping file anyway")
        log(f"redis dumped -> {out.name}")
    except FileNotFoundError:
        die("redis-cli not found on PATH. Install redis-tools in the image.")
    except subprocess.CalledProcessError as e:
        die(f"redis-cli --rdb failed with exit code {e.returncode}")


def dump_neo4j(staging: Path) -> None:
    host = env("NEO4J_HOST", "neo4j")
    port = env("NEO4J_BOLT_PORT", "7687")
    user = env("NEO4J_USER", "neo4j")
    password = env("NEO4J_PASSWORD", required=True)
    database = env("NEO4J_DATABASE", "neo4j")

    out = staging / "neo4j.dump"
    # neo4j-admin database dump requires an output path argument with --to=
    uri = f"bolt://{host}:{port}"
    cmd = [
        "neo4j-admin", "database", "dump",
        f"--database={database}",
        f"--to-path={staging}",
        f"--overwrite=true",
        # neo4j-admin talks to the DB via the bolt URI when given --from-burl
        "--verbose",
    ]

    env_ = {**os.environ, "NEO4J_URI": uri, "NEO4J_USERNAME": user, "NEO4J_PASSWORD": password}
    try:
        _run(cmd, env=env_)
        produced = staging / f"{database}.dump"
        if produced.exists():
            produced.rename(out)
            log(f"neo4j dumped -> {out.name}")
        else:
            log(f"neo4j dump produced no file at {produced} (server may be empty)")
    except FileNotFoundError:
        die("neo4j-admin not found on PATH. Install neo4j admin tools in the image.")
    except subprocess.CalledProcessError as e:
        die(f"neo4j-admin dump failed with exit code {e.returncode}")


def dump_qdrant(staging: Path) -> None:
    """Take a snapshot of each Qdrant collection and download it."""
    if not shutil.which("curl"):
        log("curl not found - skipping Qdrant backup")
        return

    host = env("QDRANT_HOST", "qdrant")
    port = env("QDRANT_PORT", "6333")
    base = f"http://{host}:{port}"

    # List collections.
    try:
        r = _run(["curl", "-fsS", f"{base}/collections"])
        import json
        payload = json.loads(r.stdout.decode() if isinstance(r.stdout, bytes) else r.stdout)
        collections = payload.get("result", {}).get("collections", [])
        names = [c.get("name") for c in collections if c.get("name")]
    except (subprocess.CalledProcessError, ValueError):
        log("could not list Qdrant collections - skipping Qdrant backup")
        return

    if not names:
        log("qdrant has no collections - skipping Qdrant backup")
        return

    qstaging = staging / "qdrant"
    qstaging.mkdir(parents=True, exist_ok=True)
    for name in names:
        snapshot_name = f"atlas-{int(time.time())}-{name}"
        try:
            _run([
                "curl", "-fsS", "-X", "POST",
                f"{base}/collections/{name}/snapshots?wait=true",
                "-H", "Content-Type: application/json",
            ])
            # List and download the most recent snapshot for this collection.
            listing = _run(["curl", "-fsS", f"{base}/collections/{name}/snapshots"])
            import json
            data = json.loads(listing.stdout.decode() if isinstance(listing.stdout, bytes) else listing.stdout)
            snaps = data.get("result", [])
            if not snaps:
                continue
            link = snaps[-1].get("link") or f"{base}/collections/{name}/snapshots/{snaps[-1]['name']}"
            out = qstaging / f"{name}.snapshot"
            _run(["curl", "-fsS", "-o", str(out), link])
            log(f"qdrant[{name}] snapshot -> {out.name}")
        except (subprocess.CalledProcessError, ValueError, KeyError) as e:
            log(f"qdrant[{name}] snapshot failed: {e} - continuing")


# --------------------------------------------------------------------------- #
# Tar + encrypt
# --------------------------------------------------------------------------- #

def tar_staging(staging: Path, dest_tar: Path) -> None:
    with tarfile.open(dest_tar, mode="w:gz") as tar:
        for child in staging.iterdir():
            tar.add(child, arcname=child.name)


def encrypt_file(plain: Path, enc: Path, key_b64: str) -> None:
    """AES-256-GCM encrypt ``plain`` into ``enc`` using a base64-encoded 32-byte key."""
    if AESGCM is None:
        die("cryptography is not installed. Add it to backup/requirements.txt.")
    import base64

    try:
        key = base64.urlsafe_b64decode(key_b64)
    except Exception as e:
        die(f"ATLAS_BACKUP_KEY is not valid base64: {e}")
    if len(key) < 32:
        die("ATLAS_BACKUP_KEY must decode to at least 32 bytes (AES-256).")

    nonce = os.urandom(12)
    aesgcm = AESGCM(key[:32])
    data = plain.read_bytes()
    ciphertext = aesgcm.encrypt(nonce, data, None)
    # Output: 12-byte nonce || ciphertext || 16-byte GCM tag (tag is appended by cryptography lib).
    enc.write_bytes(nonce + ciphertext)
    log(f"encrypted bundle: {enc.name} ({enc.stat().st_size} bytes)")


# --------------------------------------------------------------------------- #
# MinIO upload + retention
# --------------------------------------------------------------------------- #

def minio_client() -> "Minio":
    if Minio is None:
        die("minio python client is not installed. Add it to backup/requirements.txt.")
    endpoint = env("MINIO_ENDPOINT", required=True)
    access_key = env("MINIO_ACCESS_KEY", required=True)
    secret_key = env("MINIO_SECRET_KEY", required=True)
    secure = env("MINIO_SECURE", "false").lower() in ("1", "true", "yes")
    return Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)


def ensure_bucket(client, bucket: str) -> None:
    try:
        if not client.bucket_exists(bucket):
            client.make_bucket(bucket)
            log(f"created MinIO bucket: {bucket}")
    except S3Error as e:
        die(f"MinIO bucket check failed: {e}")


def object_name_for(ts: datetime) -> str:
    return f"atlas-backup-{ts.strftime('%Y%m%dT%H%M%SZ')}.tar.gz.enc"


def upload(client, bucket: str, object_name: str, path: Path) -> None:
    client.fput_object(bucket, object_name, str(path))
    log(f"uploaded -> s3://{bucket}/{object_name}")


def prune(client, bucket: str, retention: int) -> int:
    """Delete everything older than the most recent ``retention`` backups."""
    if retention <= 0:
        return 0
    objs = sorted(client.list_objects(bucket, prefix="atlas-backup-"),
                  key=lambda o: o.object_name)
    excess = len(objs) - retention
    if excess <= 0:
        return 0
    for o in objs[:excess]:
        client.remove_object(bucket, o.object_name)
        log(f"pruned old backup: {o.object_name}")
    return excess


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def run_backup() -> Path:
    log("=" * 60)
    log("starting A.T.L.A.S backup")
    log("=" * 60)

    ts = datetime.now(timezone.utc)
    staging = Path(tempfile.mkdtemp(prefix=f"atlas-backup-{ts.strftime('%Y%m%dT%H%M%SZ')}-"))
    log(f"staging dir: {staging}")

    # Per-DB dumps (each is best-effort at the run level; errors call die()).
    dump_postgres(staging)
    dump_redis(staging)
    dump_neo4j(staging)
    dump_qdrant(staging)

    # Tar + encrypt.
    plain_tar = staging / "bundle.tar.gz"
    tar_staging(staging, plain_tar)

    enc_path = staging / object_name_for(ts).replace(".tar.gz.enc", ".tar.gz.enc")
    enc_path = staging / enc_path.name
    key = env("ATLAS_BACKUP_KEY", required=True)
    encrypt_file(plain_tar, enc_path, key)

    # Upload + prune.
    bucket = env("MINIO_BUCKET", "atlas-backups")
    retention = env_int("ATLAS_BACKUP_RETENTION", 14)
    client = minio_client()
    ensure_bucket(client, bucket)
    name = object_name_for(ts)
    upload(client, bucket, name, enc_path)
    pruned = prune(client, bucket, retention)
    log(f"retention policy: keep last {retention} (pruned {pruned})")

    # Clean up staging.
    shutil.rmtree(staging, ignore_errors=True)
    log("backup complete.")
    return enc_path


def main() -> int:
    p = argparse.ArgumentParser(description="Run an A.T.L.A.S encrypted backup now.")
    p.add_argument("--dry-run", action="store_true",
                   help="Run dump + tar + encrypt but skip the MinIO upload.")
    args = p.parse_args()

    if args.dry_run:
        # Wrap upload so we stop before pushing.
        global upload
        upload = lambda *a, **kw: log(f"[dry-run] would upload {a[2]}")  # noqa: E731
    run_backup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
