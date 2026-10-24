# A.T.L.A.S — Enterprise Architecture & System Topology

High-level architecture, network topology, service components, and data flow specifications for the A.T.L.A.S platform.

---

## 1. System Architecture

```mermaid
graph TD
    Client[Web Browser / Tauri App] -->|HTTPS / WSS| Traefik[Traefik Reverse Proxy / WAF]
    
    subgraph App Layer
        Traefik -->|Sticky WSS / REST| BE1[atlas-backend Replica 1]
        Traefik -->|Sticky WSS / REST| BE2[atlas-backend Replica 2]
        Traefik -->|Sticky WSS / REST| BE3[atlas-backend Replica 3]
        Traefik -->|Static Assets| FE[atlas-frontend]
    end
    
    subgraph Data Subnet (Internal Only)
        BE1 & BE2 & BE3 -->|PostgreSQL Protocol| PG[(PostgreSQL 16)]
        BE1 & BE2 & BE3 -->|Bolt Protocol| Neo[(Neo4j Graph DB)]
        BE1 & BE2 & BE3 -->|HTTP gRPC| Qd[(Qdrant Vector DB)]
        BE1 & BE2 & BE3 -->|RESP| Rd[(Redis Cache/PubSub)]
        BE1 & BE2 & BE3 -->|S3 API| MinIO[(MinIO Object Store)]
    end

    subgraph Batch Jobs
        Backup[atlas-backup Cron] -->|Encrypted Dump| MinIO
    end
```

---

## 2. Service Map & Ports

| Service Name | Container Image | Internal Port | Protocol | Purpose |
|--------------|-----------------|---------------|----------|---------|
| **Traefik** | `traefik:v3.0` | 80, 443 | HTTP / HTTPS | Edge TLS Termination & Routing |
| **atlas-backend** | `atlas-backend:latest` | 8000 | HTTP / WS | Core FastAPI Application & Orchestration |
| **atlas-frontend** | `atlas-frontend:latest` | 3000 | HTTP | React / Next.js Web Interface |
| **PostgreSQL** | `postgres:16-alpine` | 5432 | TCP | Relational metadata, user accounts, logs |
| **Redis** | `redis:7-alpine` | 6379 | TCP | Caching, session management, Pub/Sub |
| **Neo4j** | `neo4j:5.18-community` | 7474, 7687 | HTTP / Bolt | Knowledge Graph & Entity Relationships |
| **Qdrant** | `qdrant/qdrant:v1.8.3` | 6333, 6334 | HTTP / gRPC | Vector embeddings index for RAG |
| **MinIO** | `minio/minio:RELEASE...` | 9000, 9001 | HTTP | S3-compatible document & artifact storage |
| **atlas-backup** | `atlas-backup:latest` | None | Batch | Scheduled DB dumps & AES-256 encryption |

---

## 3. Network Topology & Isolation

ATLAS employs a strictly segmented network topology across container and Kubernetes environments:

1. **Edge/Management Subnet (`atlas-management` / `atlas-ingress`):**
   - Publicly exposed ports 80 and 443 via Traefik / Ingress Controller.
   - Handles TLS termination, ACME automated certificate renewal, sticky session load balancing.
2. **Application Subnet (`atlas-backend` / `atlas-frontend`):**
   - Hosts application replicas.
   - Accepts ingress traffic exclusively from Traefik.
3. **Database Subnet (`atlas-database`):**
   - Enforces internal-only traffic (`internal: true` / K8s `NetworkPolicy` default-deny).
   - Only application backends and backup jobs can initiate database connections.
