# A.T.L.A.S — Phase 3 Enterprise Security & CI/CD Documentation

Comprehensive documentation for Phase 3 enterprise capabilities: GitHub Actions CI/CD workflows, HashiCorp Vault server & agent integration, supply chain security, mTLS service mesh, OIDC native authentication, and GCP multi-cloud IaC.

---

## 1. GitHub Actions CI/CD Workflows

Location: `.github/workflows/`

- **Continuous Integration (`ci.yml`):** Automatically runs on pull requests and pushes to `main`/`develop`. Executes Python compilation checks (`py_compile`), YAML structural parsing, Docker Compose syntax validation, Helm chart linting (`helm lint`), and Terraform formatting (`terraform fmt`).
- **Release & Supply Chain (`release.yml`):** Triggered on git version tags (`v*.*.*`). Performs multi-architecture Docker image builds (`linux/amd64`, `linux/arm64`), generates SPDX JSON SBOM artifacts via **Syft**, scans for container vulnerabilities via **Trivy**, signs container images using **Cosign**, and publishes to GitHub Container Registry (`ghcr.io`).
- **Continuous Deployment (`deploy.yml`):** Interactive workflow dispatch for rolling out releases to staging or production environments.

---

## 2. HashiCorp Vault Integration

Location: `infrastructure/vault/` and `infrastructure/docker/docker-compose.vault.yml`

- **Vault Server (`config/vault.hcl`):** Production-ready Vault server configuration with Raft storage engine and TLS support.
- **Vault Agent Sidecar (`config/agent.hcl`):** Auto-authenticates via AppRole and continuously renders secrets directly into mounted `/run/secrets/` files.
- **Initialization Scripts:** [init_vault.sh](file:///c:/Projects/A.T.L.A.S/infrastructure/vault/scripts/init_vault.sh) and [init_vault.ps1](file:///c:/Projects/A.T.L.A.S/infrastructure/vault/scripts/init_vault.ps1) set up the KV secrets engine, PKI engine, policies, and AppRole credentials.

---

## 3. Supply Chain Security Policies

Location: `infrastructure/security/`

- **Trivy Configuration (`trivy.yaml`):** Filters for `HIGH` and `CRITICAL` vulnerability severities across OS and language packages.
- **Syft SBOM Configuration (`syft.yaml`):** Configures SPDX JSON SBOM generation across all image layers.
- **Cosign Verification Policy (`cosign-policy.yaml`):** Kyverno cluster policy enforcing image signature verification for pods running images from `ghcr.io/atlas/*`.

---

## 4. Service Mesh & mTLS Isolation

Location: `infrastructure/kubernetes/70-mtls-linkerd.yaml` & `infrastructure/helm/atlas/`

- **Linkerd mTLS:** Enforces mutual TLS encryption and strict client identity verification (`Server` and `ServerAuthorization` CRDs) between frontend and backend workloads.
- **Helm Integration:** `mtls.enabled` toggle available in `values.yaml` and enabled in `values-enterprise.yaml`.

---

## 5. Native OIDC Provider Integration

Location: [services/auth_oidc.py](file:///c:/Projects/A.T.L.A.S/services/auth_oidc.py)

- Normalizes user identity payloads, role claims, and OpenID Connect discovery endpoints across **Okta**, **Azure AD (Entra ID)**, **Keycloak**, and **Auth0**.

---

## 6. Multi-Cloud IaC — GCP Modules

Location: [infrastructure/terraform/gcp/](file:///c:/Projects/A.T.L.A.S/infrastructure/terraform/gcp)

- Complete modular GCP deployment covering VPC Networks, Cloud NAT, GKE Regional Cluster, Cloud SQL for PostgreSQL 16, Artifact Registry, and Secret Manager.
