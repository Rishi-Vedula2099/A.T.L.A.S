# syntax=docker/dockerfile:1.7
# ==============================================================================
# A.T.L.A.S — Next.js frontend image
# Multi-stage build producing a standalone Next.js runtime.
# ==============================================================================

ARG NODE_VERSION=20-bookworm-slim

# --- Stage 1: install deps ---------------------------------------------------
FROM node:${NODE_VERSION} AS deps
WORKDIR /app

# Copy lockfile + manifest for deterministic install.
COPY package.json package-lock.json* ./
RUN if [ -f package-lock.json ]; then \
      npm ci; \
    else \
      npm install; \
    fi

# --- Stage 2: build ----------------------------------------------------------
FROM node:${NODE_VERSION} AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production

RUN npm run build

# --- Stage 3: dev (used by docker-compose.dev.yml via target: dev) -----------
FROM node:${NODE_VERSION} AS dev
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
EXPOSE 3000
CMD ["npm", "run", "dev"]

# --- Stage 4: runtime (standalone) -------------------------------------------
FROM node:${NODE_VERSION} AS runtime
WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

# Non-root user.
RUN groupadd --system --gid 1001 nodejs \
    && useradd --system --uid 1001 --gid nodejs nextjs

# Copy standalone server + static assets from the build output.
# `output: standalone` in next.config.ts produces .next/standalone.
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

USER nextjs
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD wget -qO- http://127.0.0.1:3000/api/health || exit 1

CMD ["node", "server.js"]
