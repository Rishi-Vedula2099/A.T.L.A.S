# Operations Manual

Day-2 operations for A.T.L.A.S once the stack is up: backups, restores, logs,
scaling, GPU enablement, and updates. For initial install see
[deployment.md](deployment.md).

---

## 1. Backups

The backup container (in `infrastructure/backup/`) dumps all four stateful
datastores, tars them, encrypts the bundle with AES-256-GCM, and uploads to
MinIO. Old backups are pruned to `ATLAS_BACKUP_RETENTION`.

### Enable scheduled backups

```bash
docker compose -f infrastructure/docker/docker-compose.yml \
               --profile backup up -d atlas-backup
```

By default this runs nightly at 02:00 UTC (`ATLAS_BACKUP_SCHEDULE=0 2 * * *`).
Override the schedule in `~/.atlas/.env`:

```ini
ATLAS_BACKUP_SCHEDULE=0 */6 * * *    # every 6 hours
ATLAS_BACKUP_RETENTION=30            # keep last 30
```

Then restart the container to pick up the new schedule:

```bash
docker compose -f infrastructure/docker/docker-compose.yml --profile backup up -d atlas-backup
```

### Run a one-shot backup now

```bash
docker compose -f infrastructure/docker/docker-compose.yml \
               --profile backup run --rm \
               -e ATLAS_MODE=backup atlas-backup
```

### List / inspect backups

Backups are stored as objects named `atlas-backup-<UTC timestamp>.tar.gz.enc`
in the MinIO bucket `atlas-backups`. Browse them via the MinIO console at
`http://minio.atlas.localhost`, or with the `mc` CLI:

```bash
mc alias set atlas http://localhost:9000 <MINIO_ACCESS_KEY> <MINIO_SECRET_KEY>
mc ls atlas/atlas-backups
```

### Restore

```bash
# Restore the latest backup (interactive — refuses non-empty targets)
docker compose -f infrastructure/docker/docker-compose.yml \
               --profile backup run --rm \
               -e ATLAS_MODE=restore -e ATLAS_RESTORE_ARGS="latest" atlas-backup

# Force restore over an existing database (DESTRUCTIVE)
docker compose -f infrastructure/docker/docker-compose.yml \
               --profile backup run --rm \
               -e ATLAS_MODE=restore -e ATLAS_RESTORE_ARGS="latest --force" atlas-backup

# Restore only Postgres and Redis from a named backup
docker compose -f infrastructure/docker/docker-compose.yml \
               --profile backup run --rm \
               -e ATLAS_RESTORE_ARGS="atlas-backup-20260101T020000Z --only postgres redis" \
               -e ATLAS_MODE=restore atlas-backup
```

See [infrastructure/backup/README.md](../infrastructure/backup/README.md) for
the full reference and key-rotation procedure.

---

## 2. Logs & observability

### Per-container logs

```bash
docker compose -f infrastructure/docker/docker-compose.yml logs -f atlas-backend
docker compose -f infrastructure/docker/docker-compose.yml logs --tail=500 atlas-frontend
```

All containers use the `json-file` driver with 10 MB × 3 file rotation.

### Centralized logging (opt-in)

Bring up the observability profile:

```bash
docker compose -f infrastructure/docker/docker-compose.yml \
               --profile observability up -d
```

- **Loki + Promtail** collect container logs.
- **Prometheus** scrapes metrics from `atlas-backend:8000/metrics`, cAdvisor,
  and node-exporter.
- **Grafana** at `http://grafana.atlas.localhost` (default login
  `admin` / value of `GRAFANA_ADMIN_PASSWORD` or `admin`) ships with
  Prometheus + Loki datasources auto-provisioned.

### Application metrics

The backend exposes a Prometheus exposition endpoint at `/metrics` with:

- `atlas_agent_runs_total{agent,status}` — counter
- `atlas_agent_run_latency_seconds{agent}` — histogram
- `http_requests_total`, `http_request_duration_seconds` — HTTP middleware

OpenTelemetry traces are exported to the OTel Collector (when the profile is
enabled), which fans out to debug / Prometheus / Loki per
`infrastructure/observability/otel-collector.yml`.

---

## 3. Scaling

### Horizontal (within Compose)

Production compose (`docker-compose.prod.yml`) defines `replicas: 2` for both
backend and frontend. To scale further on a single host:

```bash
docker compose -f infrastructure/docker/docker-compose.yml \
               -f infrastructure/docker/docker-compose.prod.yml \
               up -d --scale atlas-backend=3
```

> Traefik load-balances across replicas automatically. The backend is
> stateless, so any replica can serve any request. WebSocket sessions are
> pinned to a single replica per connection.

### Vertical (resource limits)

Each service has `deploy.resources.limits.memory` set in the base compose.
Raise them in a custom override file (`docker-compose.override.yml` is picked
up automatically):

```yaml
services:
  atlas-backend:
    deploy:
      resources:
        limits:
          memory: 4g
          cpus: "2.0"
```

### Beyond a single host

For multi-node deployments use Kubernetes — see
[enterprise-deployment.md](enterprise-deployment.md) and the manifests in
`infrastructure/kubernetes/`.

---

## 4. GPU enablement

If a CUDA-capable GPU is present:

1. Install the [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/)
   on the host.
2. In `~/.atlas/.env`:
   ```ini
   ATLAS_ENABLE_GPU=true
   ```
3. Start with the `gpu` profile:
   ```bash
   ./install --profile gpu
   # or manually:
   docker compose -f infrastructure/docker/docker-compose.yml --profile gpu up -d
   ```

`doctor.py` reports whether a GPU was detected and whether the profile is
active.

---

## 5. Updates

### Pulling a new release

The installer is idempotent, so the update path is simply:

```bash
git pull
./install
```

This rebuilds any image whose source has changed, pulls fresh base images, and
restarts affected services while preserving volumes and secrets.

### Updating only the images (no source change)

```bash
docker compose -f infrastructure/docker/docker-compose.yml pull
docker compose -f infrastructure/docker/docker-compose.yml up -d
```

### Rolling back

If a new image is broken:

```bash
# Pin a previous image tag in <repo>/.env, e.g.:
#   ATLAS_IMAGE_TAG=v0.0.5
docker compose -f infrastructure/docker/docker-compose.yml up -d
```

Then restore data from the most recent good backup (see [§1](#1-backups)).

### Desktop auto-updater

The Tauri desktop shell includes an auto-updater pointing at GitHub Releases
(configured in `apps/desktop/src-tauri/tauri.conf.json`). Once releases are
published with a signing key (Phase 3 work), desktop clients will self-update.

---

## 6. Health & readiness

| Endpoint           | Purpose                          | Returns healthy when                |
|--------------------|----------------------------------|-------------------------------------|
| `/healthz`         | Liveness — backend process up    | HTTP 200, no DB checks              |
| `/readyz`          | Readiness — all DBs reachable    | HTTP 200 only if all 4 DBs respond  |
| `/metrics`         | Prometheus exposition             | Always 200                          |

Kubernetes readiness/liveness probes and the installer's healthcheck both use
these endpoints. If `/readyz` fails, `doctor.py` will tell you which DB is the
holdout.

---

## 7. Common day-2 tasks

| Task                        | Command                                                                                |
|-----------------------------|----------------------------------------------------------------------------------------|
| Open a DB shell             | `docker exec -it atlas-postgres psql -U atlas_admin atlas_db`                          |
| Flush Redis                 | `docker exec -it atlas-redis redis-cli FLUSHALL`                                       |
| Run a Cypher query          | `docker exec -it atlas-neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD"`               |
| Tail all logs               | `docker compose -f infrastructure/docker/docker-compose.yml logs -f --tail=100`        |
| Restart a service           | `docker compose -f infrastructure/docker/docker-compose.yml restart atlas-backend`     |
| Re-seed the admin user      | `docker exec -it atlas-backend python scripts/seed_admin.py`                           |
| Disk usage of volumes       | `docker system df -v`                                                                  |
| Diagnose the stack          | `python scripts/doctor.py`                                                             |
