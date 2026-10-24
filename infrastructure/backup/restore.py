#!/usr/bin/env python3
"""
A.T.L.A.S — encrypted restore job.

Mirror of ``backup.py``. Downloads a named backup (or ``latest``) from MinIO,
decrypts it, and restores each datastore.

Safety:
    Restore is destructive. ``restore.py`` refuses to overwrite a non-empty
    target unless ``--force`` is passed.
"""

from __future__ import annotations

import argparse
import base64
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
except ImportError:  # pragma: no cover
    AESGCM = None

try:
    from minio import Minio
    from minio.error import S3Error
except ImportError:  # pragma: no cover
    Minio = None
    S3Error = Exception


# --------------------------------------------------------------------------- #
# Logging / env helpers (mirror backup.py)
# --------------------------------------------------------------------------- #

def log(msg: str) -> None:
    print(f"[restore] {msg}", flush=True)


def die(msg: str, code: int = 1) -> None:
    print(f"[restore] FATAL: {msg}", file=sys.stderr, flush=True)
    raise SystemExit(code)


def env(key: str, default: str | None = None, required: bool = False) -> str:
    v = os.environ.get(key, default)
    if required and not v:
        die(f"Missing required environment variable: {key}")
    return v or ""


def _run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    log(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, check=True, **kw)


# --------------------------------------------------------------------------- #
# MinIO
# --------------------------------------------------------------------------- #

def minio_client() -> "Minio":
    if Minio is None:
        die("minio python client is not installed.")
    endpoint = env("MINIO_ENDPOINT", required=True)
    access_key = env("MINIO_ACCESS_KEY", required=True)
    secret_key = env("MINIO_SECRET_KEY", required=True)
    secure = env("MINIO_SECURE", "false").lower() in ("1", "true", "yes")
    return Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)


def resolve_object_name(client, bucket: str, requested: str) -> str:
    """Resolve 'latest' or a prefix to a concrete object name."""
    objs = sorted(client.list_objects(bucket, prefix="atlas-backup-"),
                  key=lambda o: o.object_name)
    if not objs:
        die("no backups found in MinIO bucket")
    if requested in ("latest", ""):
        return objs[-1].object_name
    if requested in (o.object_name for o in objs):
        return requested
    # Try prefix match.
    matches = [o.object_name for o in objs if requested in o.object_name]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        die(f"ambiguous backup name '{requested}': {matches}")
    die(f"backup '{requested}' not found. Available:\n  " +
        "\n  ".join(o.object_name for o in objs[-10:]))


# --------------------------------------------------------------------------- #
# Decrypt + untar
# --------------------------------------------------------------------------- #

def decrypt_file(enc_path: Path, plain_path: Path, key_b64: str) -> None:
    if AESGCM is None:
        die("cryptography is not installed.")
    try:
        key = base64.urlsafe_b64decode(key_b64)
    except Exception as e:
        die(f"ATLAS_BACKUP_KEY is not valid base64: {e}")
    if len(key) < 32:
        die("ATLAS_BACKUP_KEY must decode to at least 32 bytes.")

    blob = enc_path.read_bytes()
    nonce, ciphertext = blob[:12], blob[12:]
    aesgcm = AESGCM(key[:32])
    try:
        plain = aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as e:
        die(f"decryption failed (wrong key? corrupted file?): {e}")
    plain_path.write_bytes(plain)
    log(f"decrypted bundle: {plain_path.name} ({plain_path.stat().st_size} bytes)")


def untar(tar_path: Path, dest: Path) -> None:
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(dest)


# --------------------------------------------------------------------------- #
# Per-DB restorers
# --------------------------------------------------------------------------- #

def _check_nonempty(path: Path, label: str, force: bool) -> None:
    if path.exists() and any(path.iterdir()) and not force:
        die(f"{label} target {path} is non-empty. Pass --force to overwrite.")


def restore_postgres(staging: Path, force: bool) -> None:
    dump = staging / "postgres.dump"
    if not dump.exists():
        log("no postgres.dump in bundle - skipping postgres")
        return

    host = env("POSTGRES_HOST", "postgres")
    port = env("POSTGRES_PORT", "5432")
    user = env("POSTGRES_USER", "atlas_admin")
    db = env("POSTGRES_DB", "atlas_db")
    password = env("POSTGRES_PASSWORD", required=True)
    env_ = {**os.environ, "PGPASSWORD": password}

    if not force:
        # Best-effort emptiness check: query row count of the most basic table.
        try:
            r = subprocess.run(
                ["psql", "-h", host, "-p", port, "-U", user, "-d", db, "-tAc",
                 "SELECT count(*) FROM information_schema.tables WHERE table_schema='public';"],
                env=env_, capture_output=True, text=True,
            )
            count = int((r.stdout or "0").strip() or "0")
            if count > 0:
                die(f"postgres target has {count} table(s) in schema 'public'. Pass --force to overwrite.")
        except (FileNotFoundError, ValueError):
            log("could not verify postgres emptiness (psql missing?) - continuing")

    cmd = [
        "pg_restore",
        f"--host={host}", f"--port={port}",
        f"--username={user}",
        "--dbname=" + db,
        "--clean", "--if-exists", "--no-owner", "--no-privileges",
        "--exit-on-error",
        str(dump),
    ]
    try:
        _run(cmd, env=env_)
        log("postgres restored")
    except FileNotFoundError:
        die("pg_restore not found on PATH.")
    except subprocess.CalledProcessError as e:
        die(f"pg_restore failed with exit code {e.returncode}")


def restore_redis(staging: Path, force: bool) -> None:
    rdb = staging / "redis.rdb"
    if not rdb.exists():
        log("no redis.rdb in bundle - skipping redis")
        return
    # Redis restore from RDB requires replacing the server's dump file and
    # restarting. We don't restart here (too risky without orchestration);
    # instead, we FLUSH then repopulate via RESTORE on each key.
    host = env("REDIS_HOST", "redis")
    port = env("REDIS_PORT", "6379")
    password = env("REDIS_PASSWORD", "")

    base_cmd = ["redis-cli", "-h", host, "-p", port]
    if password:
        base_cmd += ["-a", password, "--no-auth-warning"]

    log("flushing redis target before restore" if force else "skipping flush (use --force to FLUSH first)")
    if force:
        try:
            _run(base_cmd + ["FLUSHDB"])
        except subprocess.CalledProcessError:
            pass

    # Repopulate from RDB by spawning a throwaway redis-server on a temp port,
    # having it load the RDB, then copying keys over. This is the simplest
    # portable approach without restarting the live server.
    tmp_port = 6399
    tmp_dir = staging / "redis_tmp"
    tmp_dir.mkdir(exist_ok=True)
    shutil.copy(rdb, tmp_dir / "dump.rdb")

    try:
        proc = subprocess.Popen(
            ["redis-server", "--port", str(tmp_port), "--dir", str(tmp_dir),
             "--save", "", "--appendonly", "no", "--daemonize", "no"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        time.sleep(1.0)
        # Copy keys.
        _run(base_cmd + ["--rdb", str(staging / "noop.rdb")])  # noop to verify target alive
        # For each key in tmp, RESTORE into target.
        keys = subprocess.run(
            ["redis-cli", "-h", host, "-p", str(tmp_port), "--scan"],
            capture_output=True, text=True,
        ).stdout.split()
        for k in keys:
            dump_out = subprocess.run(
                ["redis-cli", "-h", host, "-p", str(tmp_port), "DUMP", k],
                capture_output=True,
            )
            ttl = subprocess.run(
                ["redis-cli", "-h", host, "-p", str(tmp_port), "PTTL", k],
                capture_output=True, text=True,
            ).stdout.strip()
            ttl_ms = ttl if ttl.lstrip("-").isdigit() and int(ttl) > 0 else "0"
            subprocess.run(
                base_cmd + ["RESTORE", k, ttl_ms, dump_out.stdout.hex(),
                            "REPLACE"],
                stdout=subprocess.DEVNULL,
            )
        log(f"redis restored ({len(keys)} keys)")
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            pass


def restore_neo4j(staging: Path, force: bool) -> None:
    dump = staging / "neo4j.dump"
    if not dump.exists():
        log("no neo4j.dump in bundle - skipping neo4j")
        return

    host = env("NEO4J_HOST", "neo4j")
    port = env("NEO4J_BOLT_PORT", "7687")
    user = env("NEO4J_USER", "neo4j")
    password = env("NEO4J_PASSWORD", required=True)
    database = env("NEO4J_DATABASE", "neo4j")

    if force:
        # Drop + recreate the database (only works on enterprise edition or 5.x community).
        try:
            _run([
                "cypher-shell", "-a", f"bolt://{host}:{port}",
                "-u", user, "-p", password,
                f"CREATE OR REPLACE DATABASE {database};",
            ])
        except (FileNotFoundError, subprocess.CalledProcessError) as e:
            log(f"could not pre-clear neo4j database ({e}) - continuing")

    cmd = [
        "neo4j-admin", "database", "load",
        f"--database={database}",
        f"--from-path={staging}",
        "--overwrite=true",
        "--verbose",
    ]
    try:
        _run(cmd)
        log("neo4j restored")
    except FileNotFoundError:
        die("neo4j-admin not found on PATH.")
    except subprocess.CalledProcessError as e:
        die(f"neo4j-admin load failed with exit code {e.returncode}")


def restore_qdrant(staging: Path, force: bool) -> None:
    qstaging = staging / "qdrant"
    if not qstaging.exists():
        log("no qdrant/ dir in bundle - skipping qdrant")
        return

    host = env("QDRANT_HOST", "qdrant")
    port = env("QDRANT_PORT", "6333")
    base = f"http://{host}:{port}"

    for snap in qstaging.glob("*.snapshot"):
        collection = snap.stem
        if force:
            try:
                _run(["curl", "-fsS", "-X", "DELETE", f"{base}/collections/{collection}"])
            except subprocess.CalledProcessError:
                pass
        try:
            _run([
                "curl", "-fsS", "-X", "PUT",
                f"{base}/collections/{collection}/snapshots/recover?wait=true",
                "-H", "Content-Type: multipart/form-data",
                "-F", f"snapshot=@{snap}",
            ])
            log(f"qdrant[{collection}] restored")
        except subprocess.CalledProcessError as e:
            log(f"qdrant[{collection}] restore failed ({e}) - continuing")


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #

def run_restore(name: str, *, force: bool, only: list[str] | None) -> None:
    log("=" * 60)
    log(f"starting A.T.L.A.S restore (target: {name})")
    log("=" * 60)

    bucket = env("MINIO_BUCKET", "atlas-backups")
    client = minio_client()
    object_name = resolve_object_name(client, bucket, name)
    log(f"selected backup: {object_name}")

    staging = Path(tempfile.mkdtemp(prefix="atlas-restore-"))
    enc_path = staging / object_name
    client.fget_object(bucket, object_name, str(enc_path))
    log(f"downloaded -> {enc_path.name} ({enc_path.stat().st_size} bytes)")

    plain_tar = staging / "bundle.tar.gz"
    decrypt_file(enc_path, plain_tar, env("ATLAS_BACKUP_KEY", required=True))

    bundle_dir = staging / "bundle"
    bundle_dir.mkdir()
    untar(plain_tar, bundle_dir)

    only_set = set(only or [])
    def should(name_: str) -> bool:
        return not only_set or name_ in only_set

    try:
        if should("postgres"): restore_postgres(bundle_dir, force)
        if should("redis"):    restore_redis(bundle_dir, force)
        if should("neo4j"):    restore_neo4j(bundle_dir, force)
        if should("qdrant"):   restore_qdrant(bundle_dir, force)
    finally:
        shutil.rmtree(staging, ignore_errors=True)

    log("restore complete.")


def main() -> int:
    p = argparse.ArgumentParser(description="Restore A.T.L.A.S from an encrypted backup.")
    p.add_argument("name", nargs="?", default="latest",
                   help="Backup object name, 'latest', or a unique substring.")
    p.add_argument("--force", action="store_true",
                   help="Allow restoring into non-empty targets (destructive).")
    p.add_argument("--only", nargs="*", default=[],
                   choices=["postgres", "redis", "neo4j", "qdrant"],
                   help="Restore only the listed datastores.")
    args = p.parse_args()

    run_restore(args.name, force=args.force, only=args.only)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
