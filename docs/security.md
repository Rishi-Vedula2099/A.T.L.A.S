# A.T.L.A.S — Security Posture & Roadmap

Security architecture, credential management, network isolation, and security implementation roadmap for A.T.L.A.S.

---

## Current Security Posture (Phase 1 + Phase 2)

### 1. Authentication & Authorization
- **JWT Tokens:** HS256 signed access tokens (15-minute TTL) paired with refresh tokens (7-day TTL).
- **API Keys:** Secure random 32-byte tokens generated via `secrets.token_urlsafe(32)` for daemon and service integration.
- **RBAC:** Role-based access control guarding API endpoints (`admin`, `operator`, `user`).

### 2. Secret Management
- **Local / Single Node:** File-based Docker Secrets mounted read-only at `/run/secrets/*` in enterprise Compose setups. `.env` permissions set to `0600`.
- **Cloud Managed:** Secrets Manager (AWS RDS) and Azure Key Vault integration templates for IaC deployments.
- **No In-Code Hardcoding:** Secret values are loaded strictly via environment variables or secret files.

### 3. Network Isolation
- **Micro-segmentation:** Strict 3-tier network model (Ingress, Application, Database).
- **Kubernetes Isolation:** Default-deny `NetworkPolicy` enforcing explicit backend-to-database access rules.
- **Edge Security:** Traefik ingress handling TLS 1.3 termination and ACME certificate management.

### 4. Data Protection & Backup Security
- **Encryption at Rest:** Backups encrypted with AES-256-GCM using `ATLAS_BACKUP_KEY`.
- **Storage Protection:** MinIO S3 bucket access protected via restricted access key/secret key pairs.

---

## Phase 3 Roadmap (Future Enhancements)

The following advanced enterprise security controls are deferred to Phase 3:

1. **HashiCorp Vault Server Deployment:** Dynamic database credential generation, automated secret rotation, and PKI engine.
2. **mTLS (Mutual TLS):** Service mesh (Istio / Linkerd) sidecar integration for zero-trust in-transit encryption between microservices.
3. **Supply Chain Security:**
   - **SBOM:** Syft SBOM generation for software component transparency.
   - **Vulnerability Scanning:** Trivy container image scanning in CI/CD pipelines.
   - **Image Signing:** Cosign digital signatures verified by Kubernetes Admission Controllers.
4. **OAuth2 / OIDC Integration:** Native Okta, Azure AD, and Keycloak SSO provider integration.
