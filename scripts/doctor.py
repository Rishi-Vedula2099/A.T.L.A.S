#!/usr/bin/env python3
"""
A.T.L.A.S — diagnostics CLI.

Prints a traffic-light report on why the stack isn't (or might not be) healthy.
Use this whenever `./install` fails or the dashboard can't reach the backend.

Checks, in order of typical failure frequency:
    1. Docker daemon running.
    2. Docker Compose v2 plugin available.
    3. Required ports (80, 443, 3000, 8000) are free on the host.
    4. `.env` exists at the expected locations and contains every required var.
    5. Each secret still has its placeholder value (e.g. "change-me").
    6. Every expected container is present and (if applicable) healthy.
    7. Backend `/healthz` and `/readyz` respond.

Exit code is the number of failed checks (capped at 1 so it's a boolean in
shell). Warnings don't change the exit code.
"""

from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
from pathlib import Path
from typing import Callable, List, Tuple
from urllib.error import URLError
from urllib.request import urlopen

_REPO_ROOT = Path(__file__).resolve().parents[1]
_COMPOSE_FILE = _REPO_ROOT / "infrastructure" / "docker" / "docker-compose.yml"
_REPO_ENV = _REPO_ROOT / ".env"

# Service name -> friendly label.
_EXPECTED_CONTAINERS = {
    "atlas-postgres":   "PostgreSQL",
    "atlas-redis":      "Redis",
    "atlas-neo4j":      "Neo4j",
    "atlas-qdrant":     "Qdrant",
    "atlas-backend":    "Backend",
    "atlas-frontend":   "Frontend",
    "atlas-traefik":    "Traefik",
    "atlas-minio":      "MinIO",
}

_REQUIRED_ENV_VARS = (
    "ATLAS_API_KEY",
    "JWT_SECRET",
    "JWT_REFRESH_SECRET",
    "POSTGRES_PASSWORD",
    "NEO4J_PASSWORD",
    "MINIO_ACCESS_KEY",
    "MINIO_SECRET_KEY",
    "ATLAS_BACKUP_KEY",
)

# Placeholder values from .env.example that MUST be replaced.
_PLACEHOLDERS = {
    "JWT_SECRET": "change-me",
    "JWT_REFRESH_SECRET": "change-me",
    "POSTGRES_PASSWORD": "change-me",
    "NEO4J_PASSWORD": "change-me",
    "MINIO_ACCESS_KEY": "change-me",
    "MINIO_SECRET_KEY": "change-me",
    "ATLAS_API_KEY": "change-me",
    "ATLAS_BACKUP_KEY": "change-me",
}

_CHECK_PORTS = (80, 443, 3000, 8000)


# --------------------------------------------------------------------------- #
# Output helpers
# --------------------------------------------------------------------------- #

class Report:
    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed: List[str] = []

    def ok(self, msg: str) -> None:
        self.passed.append(msg)
        print(f"  [ \033[32mOK \033[0m] {msg}")

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)
        print(f"  [ \033[33mWARN\033[0m] {msg}")

    def fail(self, msg: str) -> None:
        self.errors.append(msg)
        print(f"  [ \033[31mFAIL\033[0m] {msg}")


def _section(title: str) -> None:
    print()
    print(f"\033[1m--- {title} ---\033[0m")


def _no_color(report: Report) -> None:
    """Strip ANSI codes from a Report's outputs (Windows cmd / monochrome terminals)."""
    # The prints above already happened; this is a hook if we want to disable color
    # globally in the future. For now, ANSI works on modern Windows terminals.


# --------------------------------------------------------------------------- #
# Command execution
# --------------------------------------------------------------------------- #

def _run(cmd: List[str], timeout: float = 10.0) -> Tuple[int, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, (r.stdout + r.stderr)
    except FileNotFoundError:
        return 127, f"command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, "timed out"
    except Exception as e:  # noqa: BLE001
        return 1, str(e)


# --------------------------------------------------------------------------- #
# Individual checks
# --------------------------------------------------------------------------- #

def check_docker(r: Report) -> None:
    rc, out = _run(["docker", "info"])
    if rc == 0:
        r.ok("Docker daemon is running")
    elif rc == 127:
        r.fail("Docker is not installed or not on PATH. Install Docker Desktop / Engine.")
    else:
        r.fail("Docker daemon is not responding. Start Docker Desktop / `systemctl start docker`.")
        r.warn(f"docker info output: {out.strip().splitlines()[:3]}")


def check_compose(r: Report) -> None:
    rc, _ = _run(["docker", "compose", "version"])
    if rc == 0:
        r.ok("Docker Compose v2 plugin available")
    else:
        r.fail("Docker Compose v2 plugin is missing. Install `docker-compose-plugin` or restart Docker Desktop.")


def check_ports(r: Report) -> None:
    for port in _CHECK_PORTS:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        try:
            in_use = sock.connect_ex(("127.0.0.1", port)) == 0
        finally:
            sock.close()
        if in_use and port in (80, 443):
            # Traefik should be holding 80/443 when stack is up — that's fine.
            r.ok(f"port {port} is listening (Traefik?)")
        elif in_use and port in (3000, 8000):
            # Could be the stack or a conflicting dev server on the host.
            r.warn(f"port {port} is in use — check it's the ATLAS service, not another app")
        else:
            r.ok(f"port {port} is free")


def _parse_env(path: Path) -> dict:
    out = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip()
    return out


def check_env(r: Report) -> None:
    # Look at both possible locations; prefer repo .env since that's what compose reads.
    candidates = [_REPO_ENV]
    home_env = Path(os.path.expanduser("~")) / ".atlas" / ".env"
    if home_env.exists():
        candidates.append(home_env)

    if not _REPO_ENV.exists():
        r.fail(f".env missing at {_REPO_ENV}. Run `./install` or `python scripts/generate_env.py`.")
        return

    env = _parse_env(_REPO_ENV)
    missing = [k for k in _REQUIRED_ENV_VARS if k not in env or not env[k]]
    if missing:
        r.fail(f".env is missing required keys: {', '.join(missing)}")
    else:
        r.ok(".env has all required keys")

    placeholders = [k for k, v in env.items()
                    if k in _PLACEHOLDERS and v.strip() == _PLACEHOLDERS[k]]
    if placeholders:
        r.fail(f".env still has placeholder values for: {', '.join(placeholders)}")
        r.warn("  regenerate with: python scripts/generate_env.py --force")
    else:
        r.ok(".env secrets are not placeholders")


def check_containers(r: Report) -> None:
    rc, out = _run(["docker", "ps", "--format", "{{.Names}}|{{.Status}}"])
    if rc != 0:
        r.warn("could not list containers (is Docker running?)")
        return

    running = {}
    for line in out.splitlines():
        if "|" in line:
            name, _, status = line.partition("|")
            running[name.strip()] = status.strip()

    if not running:
        r.fail("no ATLAS containers running. Start the stack: `docker compose up -d` "
               f"(from {_COMPOSE_FILE.parent})")
        return

    for name, label in _EXPECTED_CONTAINERS.items():
        if name not in running:
            r.fail(f"container {name} ({label}) is not running")
        elif "healthy" in running[name].lower():
            r.ok(f"{label} ({name}) healthy")
        elif "unhealthy" in running[name].lower():
            r.fail(f"{label} ({name}) UNHEALTHY — see `docker logs {name}`")
        else:
            r.ok(f"{label} ({name}) running (status: {running[name]})")


def check_backend_http(r: Report) -> None:
    for path in ("/healthz", "/readyz"):
        url = f"http://localhost{path}"
        try:
            with urlopen(url, timeout=3) as resp:
                body = resp.read(120).decode("utf-8", "replace")
                if 200 <= resp.status < 300:
                    r.ok(f"{url} -> HTTP {resp.status}")
                else:
                    r.fail(f"{url} -> HTTP {resp.status}: {body!r}")
        except URLError:
            r.warn(f"{url} not reachable — stack may not be up yet")
        except Exception as e:  # noqa: BLE001
            r.warn(f"{url} error: {e}")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def run_all() -> int:
    print("=" * 60)
    print(" A.T.L.A.S — doctor")
    print("=" * 60)

    r = Report()

    _section("Docker")
    check_docker(r)
    check_compose(r)

    _section("Ports")
    check_ports(r)

    _section("Environment")
    check_env(r)

    _section("Containers")
    check_containers(r)

    _section("HTTP health")
    check_backend_http(r)

    print()
    print("=" * 60)
    print(f" {len(r.passed)} OK   {len(r.warnings)} WARN   {len(r.errors)} FAIL")
    print("=" * 60)
    if r.errors:
        print("\nMost likely fixes:")
        for e in r.errors[:3]:
            print(f"  - {e}")
        print("\nRe-run after fixing: python scripts/doctor.py")
    return 1 if r.errors else 0


def main() -> int:
    argparse.ArgumentParser(
        description="Diagnose why the A.T.L.A.S stack is not healthy."
    ).parse_args()  # no flags yet; argparse gives us --help and consistent exit codes
    return run_all()


if __name__ == "__main__":
    raise SystemExit(main())
