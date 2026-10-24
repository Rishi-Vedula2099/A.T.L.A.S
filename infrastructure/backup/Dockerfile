# syntax=docker/dockerfile:1.7
# ==============================================================================
# A.T.L.A.S — backup/restore job image
# ==============================================================================
# Slim image with the client CLIs needed to dump each datastore, plus a small
# Python layer for tar+encrypt+upload. Runs as a non-root user.
#
# Entrypoint modes (ATLAS_MODE):
#   schedule (default)  long-lived cron loop calling backup.py
#   backup              run one backup now and exit
#   restore             run restore.py once and exit
# ==============================================================================

ARG PYTHON_VERSION=3.12-slim

FROM python:${PYTHON_VERSION} AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt


FROM python:${PYTHON_VERSION} AS runtime

ARG APP_USER=atlas
ARG APP_UID=1000
ARG APP_GID=1000

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    TZ=UTC

# Runtime system deps:
#   - postgresql-client   pg_dump / pg_restore
#   - redis-tools         redis-cli
#   - neo4j               neo4j-admin + cypher-shell (downloaded below)
#   - curl                Qdrant snapshot API + healthcheck
#   - tini                PID 1
RUN apt-get update && apt-get install -y --no-install-recommends \
        postgresql-client \
        redis-tools \
        curl \
        ca-certificates \
        tini \
        gnupg \
    \
    # Neo4j admin tools (5.x) — required for database dump/load.
    && curl -fsSL https://debian.neo4j.com/neotechnology.gpg.key \
        | gpg --dearmor -o /usr/share/keyrings/neo4j.gpg \
    && echo 'deb [signed-by=/usr/share/keyrings/neo4j.gpg] https://debian.neo4j.com stable latest' \
        > /etc/apt/sources.list.d/neo4j.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends neo4j \
    && rm -rf /var/lib/apt/lists/*

# Python deps from builder.
COPY --from=builder /install /usr/local

# Non-root user.
RUN groupadd --system --gid ${APP_GID} ${APP_USER} \
    && useradd --system --uid ${APP_UID} --gid ${APP_GID} \
       --create-home --shell /bin/bash ${APP_USER}

WORKDIR /app

COPY --chown=${APP_UID}:${APP_GID} backup.py restore.py entrypoint.sh requirements.txt ./
COPY --chown=${APP_UID}:${APP_GID} README.md ./

RUN chmod +x entrypoint.sh && \
    mkdir -p /work && chown -R ${APP_UID}:${APP_GID} /app /work

USER ${APP_USER}

ENV ATLAS_MODE=schedule \
    ATLAS_BACKUP_SCHEDULE="0 2 * * *" \
    ATLAS_BACKUP_RETENTION=14

VOLUME ["/work"]

# No port published — this is a batch job.
ENTRYPOINT ["/usr/bin/tini", "--", "/app/entrypoint.sh"]
