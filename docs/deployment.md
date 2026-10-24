# Deployment Guide

This guide covers installing, running, and troubleshooting A.T.L.A.S on a
single host (developer workstation or a single server) using Docker Compose.
For enterprise / Kubernetes / Terraform deployment see
[enterprise-deployment.md](enterprise-deployment.md).

---

## 1. One-shot install (recommended)

The installer automates everything: OS/arch/GPU detection, Docker install,
secret generation, image build, service startup, and healthchecks.

**macOS / Linux**
```bash
./install
```

**Windows** (cmd, PowerShell, or double-click in Explorer)
```bat
install.bat
```

What it does, in order:

1. Detect OS, architecture, RAM, GPU, disk space.
2. Install Docker if missing (Linux: `get.docker.com` + usermod; macOS: `brew
   --cask docker`; Windows: `winget Docker.DockerDesktop`).
3. Generate cryptographically strong secrets to `~/.atlas/.env`.
4. Mirror secrets into `<repo>/.env` (gitignored).
5. `docker compose build` + `docker compose up -d`.
6. Poll `http://localhost/readyz` until healthy.
7. Open the dashboard at `http://localhost`.

The installer is **idempotent** — re-running it preserves existing secrets and
only rebuilds changed images.

See [installer/README.md](../installer/README.md) for flags
(`--force-secrets`, `--profile`, `--no-pull`, `--skip-open`).

---

## 2. Manual setup (if you already have Docker)

```bash
# 1. Generate secrets
python scripts/generate_env.py                 # writes <repo>/.env

# 2. Validate the compose file
docker compose -f infrastructure/docker/docker-compose.yml config > /dev/null

# 3. Build + start the lean core
docker compose -f infrastructure/docker/docker-compose.yml up -d

# 4. Wait for readiness
python installer/lib/healthcheck.py
```

Endpoints after start:

| URL                              | What                          |
|----------------------------------|-------------------------------|
| `http://localhost`               | Frontend (Next.js dashboard)  |
| `http://localhost/readyz`        | Backend readiness check       |
| `http://localhost/healthz`       | Backend liveness check        |
| `http://localhost/docs`          | Backend OpenAPI UI            |
| `http://api.atlas.localhost/*`   | Backend behind Traefik host   |
| `http://minio.atlas.localhost`   | MinIO console (backups)      |

> **Note on `*.localhost` hosts:** Traefik routes by Host header. Modern
> browsers resolve `*.localhost` to `127.0.0.1` automatically, so no DNS
> changes are needed. If yours doesn't, use `localhost` directly (the frontend
> is reachable on both).

---

## 3. Compose profiles

The base `docker-compose.yml` brings up only the **lean core** (databases +
backend + frontend + Traefik + MinIO). Everything else is opt-in:

```bash
# Observability stack
docker compose -f infrastructure/docker/docker-compose.yml \
    --profile observability up -d

# Kafka + Zookeeper
docker compose -f infrastructure/docker/docker-compose.yml \
    --profile messaging up -d

# GPU reservation on backend (needs NVIDIA Container Toolkit on host)
ATLAS_ENABLE_GPU=true docker compose -f infrastructure/docker/docker-compose.yml \
    --profile gpu up -d

# Scheduled encrypted backups
docker compose -f infrastructure/docker/docker-compose.yml \
    --profile backup up -d
```

Multiple profiles compose: `--profile observability --profile backup`.

---

## 4. Compose variants

Three compose files layer on top of the base:

| Variant                | When to use                          |
|------------------------|--------------------------------------|
| `docker-compose.yml`         | Default — local dev/prod lean core |
| `+ docker-compose.dev.yml`   | Hot-reload, verbose logs, no resource limits |
| `+ docker-compose.prod.yml`  | Replicas, restart=always, ACME TLS, tighter limits |
| `+ docker-compose.enterprise.yml` | Phase 2 — Docker Secrets, stricter limits, Watchtower (see [enterprise-deployment.md](enterprise-deployment.md)) |

```bash
# Dev with hot reload
docker compose -f infrastructure/docker/docker-compose.yml \
               -f infrastructure/docker/docker-compose.dev.yml up

# Production
docker compose -f infrastructure/docker/docker-compose.yml \
               -f infrastructure/docker/docker-compose.prod.yml up -d
```

---

## 5. Stopping & cleaning up

```bash
# Stop containers (volumes preserved)
docker compose -f infrastructure/docker/docker-compose.yml down

# Stop AND delete data volumes (DESTRUCTIVE — drops all databases)
docker compose -f infrastructure/docker/docker-compose.yml down -v
```

Secrets in `~/.atlas/.env` survive `down` and `down -v`.

---

## 6. Troubleshooting

If the installer fails or the dashboard can't reach the backend, start here:

```bash
python scripts/doctor.py
```

`doctor.py` prints a traffic-light report covering Docker daemon state, port
conflicts, `.env` integrity, container health, and backend HTTP responses.

### Common failures

| Symptom                                            | Likely cause                                     | Fix                                                              |
|----------------------------------------------------|--------------------------------------------------|------------------------------------------------------------------|
| `[docker] winget is not available on PATH`         | Windows without App Installer / Store            | Install Docker Desktop manually from docker.com                  |
| `docker-compose.yml: POSTGRES_PASSWORD is not set` | `.env` missing or incomplete                     | `./install` or `python scripts/generate_env.py --force`          |
| Backend `/readyz` 500s                             | A DB hasn't finished initializing                | Wait 30–60s, then retry. Check `docker compose logs postgres`    |
| `bind: address already in use` on port 80          | Another web server is running                    | Stop it, or remap Traefik's port in the compose override         |
| `docker: Cannot connect to the Docker daemon`      | Docker Desktop not started (Win/Mac)             | Launch Docker Desktop, wait for the whale icon, re-run install   |
| Frontend loads but WebSocket won't connect         | Browser blocked `ws://` or wrong host            | Use `http://localhost` (not the LAN IP) for local dev            |
| `[atlas] GPU detected` but no GPU in containers    | Profile not enabled                              | Re-run with `--profile gpu` and `ATLAS_ENABLE_GPU=true` in `.env`|

### Inspecting logs

```bash
# All services, last 200 lines
docker compose -f infrastructure/docker/docker-compose.yml logs --tail=200

# A specific service, follow mode
docker compose -f infrastructure/docker/docker-compose.yml logs -f atlas-backend

# With the observability profile, view logs in Grafana -> Explore -> Loki
```

### Resetting to a clean state

```bash
docker compose -f infrastructure/docker/docker-compose.yml down -v
rm -f .env ~/.atlas/.env
./install
```
